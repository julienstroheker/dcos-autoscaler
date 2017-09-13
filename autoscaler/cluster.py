import logging
import sys
import time
import requests
import json

from autoscaler.provider import Provider

LOGGER = logging.getLogger('dcos-autoscaler')

class Cluster(object):
    def __init__(self, provider_name, scale_up_cap, scale_down_cap, scale_max, scale_min,
                 endpoint_path, azure_subscription_id, azure_tenant_id, azure_client_id,
                 azure_client_secret, azure_location, azure_resource_group, azure_vmss_name):
        self.scale_up_cap = scale_up_cap
        self.scale_down_cap = scale_down_cap
        self.scale_max = scale_max
        self.scale_min = scale_min
        self.endpoint_path = endpoint_path
        self.provider = Provider(provider_name=provider_name,
                                 azure_subscription_id=azure_subscription_id,
                                 azure_tenant_id=azure_tenant_id,
                                 azure_client_id=azure_client_id,
                                 azure_client_secret=azure_client_secret,
                                 azure_location=azure_location,
                                 azure_resource_group=azure_resource_group,
                                 azure_vmss_name=azure_vmss_name)


    def get_health(self):
        LOGGER.debug("Get Health Cluster")
        try:
            payload = requests.get(self.endpoint_path)
            return payload.json()
            #with open('test/mockupMid.json') as json_data:
                #return json.load(json_data)
        except:
            LOGGER.error("Connection to " + str(self.endpoint_path) + " Failed")
            LOGGER.error(e = sys.exc_info()[0])
            exit(1)



    def filter_stateless(self, metrics, raw_health):
        LOGGER.debug("Filter the health object to get only the stateless nodes")
        for node in raw_health['slaves']:
            if 'attributes' in node and node['active']:
                if 'workload' in node['attributes']:
                    if node['attributes']['workload'] == "stateless":
                        metrics["totalCPU"] += node['resources']['cpus']
                        metrics["totalMEM"] += node['resources']['mem']
                        metrics["usedCPU"] += node['used_resources']['cpus']
                        metrics["usedMEM"] += node['used_resources']['mem']
                        metrics["nbNodes"] = metrics["nbNodes"] + 1
                        LOGGER.debug(node['hostname'] + " - Added to the stateless pool")
        return metrics


    def check_health(self, metrics):
        health = self.get_health()
        metrics = self.filter_stateless(metrics, health)
        metrics["ratioCPU"] = ((metrics["usedCPU"]*100)/metrics["totalCPU"])
        metrics["ratioMEM"] = ((metrics["usedMEM"]*100)/metrics["totalMEM"])

    def decide_to_scale(self, metrics):
        if metrics["ratioCPU"] >= self.scale_up_cap and metrics["nbNodes"] <= self.scale_max:
            return 1
        if metrics["ratioCPU"] <= self.scale_down_cap and metrics["nbNodes"] >= self.scale_min:
            return -1

    def waiting_scale(self, metrics):
        current_state = metrics
        while metrics == current_state:
            #current_state = []
            current_state = self.filter_stateless(current_state, self.get_health())
            LOGGER.info(
                "Waiting for new status of the cluster...Current State = "
                + str(current_state["totalCPU"]))
            time.sleep(15)
        return True

    def scale_cluster_up(self, metrics):
        self.provider.scale_up()
        self.waiting_scale(metrics)
        return True

    def scale_cluster_down(self, metrics):
        self.provider.scale_down()
        self.waiting_scale(metrics)
        return True
