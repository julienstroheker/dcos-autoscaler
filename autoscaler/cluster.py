import logging
import sys
import time
import json
import requests

from autoscaler.provider import Provider

LOGGER = logging.getLogger('dcos-autoscaler')

class Cluster(object):
    def __init__(self, provider_name, scale_up_cap, scale_down_cap, scale_max, scale_min,
                 endpoint_path,
                 azure_subscription_id, azure_tenant_id, azure_client_id,
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
            #r = requests.get(self.endpoint_path)
            #return r.json()
            with open('test/mockupGPU.json') as json_data:
                return json.load(json_data)
        except:
            LOGGER.error(sys.exc_info()[0])
            exit(1)



    def filter_stateless(self, metrics, raw_health, attribute_key, attribute_value):
        LOGGER.debug("Filter the health object to get only the stateless nodes")
        for node in raw_health['slaves']:
            if 'attributes' in node and node['active']:
                if attribute_key in node['attributes']:
                    if node['attributes'][attribute_key] == attribute_value:
                        metrics["totalCPU"] += node['resources']['cpus']
                        metrics["totalMEM"] += node['resources']['mem']
                        metrics["totalDISK"] += node['resources']['disk']
                        metrics["totalGPU"] += node['resources']['gpus']
                        metrics["usedCPU"] += node['used_resources']['cpus']
                        metrics["usedMEM"] += node['used_resources']['mem']
                        metrics["usedDISK"] += node['used_resources']['disk']
                        metrics["usedGPU"] += node['used_resources']['gpus']
                        metrics["nbNodes"] = metrics["nbNodes"] + 1
                        LOGGER.debug(node['hostname'] +
                                     " - Added to the " + str(attribute_value) + " pool")
        return metrics


    def check_health(self, metrics, resource_tracker, attribute_key, attribute_value):
        health = self.get_health()
        metrics = self.filter_stateless(metrics, health, attribute_key, attribute_value)
        if metrics["totalCPU"] != 0:
            metrics["ratioCPU"] = ((metrics["usedCPU"]*100)/metrics["totalCPU"])
        if metrics["totalMEM"] != 0:
            metrics["ratioMEM"] = ((metrics["usedMEM"]*100)/metrics["totalMEM"])
        if metrics["totalDISK"] != 0:
            metrics["ratioDISK"] = ((metrics["usedDISK"]*100)/metrics["totalDISK"])
        if metrics["totalGPU"] != 0:
            metrics["ratioGPU"] = ((metrics["usedGPU"]*100)/metrics["totalGPU"])

    def decide_to_scale(self, metrics, resource_tracker):
        if (resource_tracker == "cpus" and
                metrics["ratioCPU"] >= self.scale_up_cap and
                metrics["nbNodes"] <= self.scale_max):
            return 1
        if (resource_tracker == "cpus" and
                metrics["ratioCPU"] <= self.scale_down_cap and
                metrics["nbNodes"] >= self.scale_min):
            return -1
        if (resource_tracker == "mem" and
                metrics["ratioMEM"] >= self.scale_up_cap and
                metrics["nbNodes"] <= self.scale_max):
            return 1
        if (resource_tracker == "mem" and
                metrics["ratioMEM"] <= self.scale_down_cap and
                metrics["nbNodes"] >= self.scale_min):
            return -1
        if (resource_tracker == "disk" and
                metrics["ratioDISK"] >= self.scale_up_cap and
                metrics["nbNodes"] <= self.scale_max):
            return 1
        if (resource_tracker == "disk" and
                metrics["ratioDISK"] <= self.scale_down_cap and
                metrics["nbNodes"] >= self.scale_min):
            return -1
        if (resource_tracker == "gpus" and
                metrics["ratioGPU"] >= self.scale_up_cap and
                metrics["nbNodes"] <= self.scale_max):
            return 1
        if (resource_tracker == "gpus" and
                metrics["ratioGPU"] <= self.scale_down_cap and
                metrics["nbNodes"] >= self.scale_min):
            return -1

    def waiting_scale(self, metrics, attribute_key, attribute_value):
        current_state = metrics
        while metrics == current_state:
            LOGGER.debug(
                "Waiting for new status of the cluster...Current State = "
                + current_state["totalCPU"])
            current_state = self.filter_stateless(current_state, self.get_health(),
                                                  attribute_key, attribute_value)
            time.sleep(30)
        return True

    def scale_cluster_up(self, metrics, attribute_key, attribute_value):
        self.provider.scale_up()
        self.waiting_scale(metrics, attribute_key, attribute_value)
        return True

    def scale_cluster_down(self, metrics, attribute_key, attribute_value):
        self.provider.scale_down()
        self.waiting_scale(metrics, attribute_key, attribute_value)
        return True
