import logging
import requests
import sys
import time
import json

from autoscaler.provider import Provider

logger = logging.getLogger('dcos-autoscaler')

class Cluster(object):
    def __init__(self, provider_name, scale_up_cap, scale_down_cap, scale_max, scale_min,
                 azure_subscription_id, azure_tenant_id, azure_client_id, azure_client_secret,
                 azure_location, azure_resource_group, azure_vmss_name):
        self.scale_up_cap = scale_up_cap
        self.scale_down_cap = scale_down_cap
        self.scale_max = scale_max
        self.scale_min = scale_min
        self.metricsEndpoint = "http://leader.mesos"
        self.metricsPort = "5050"
        self.metricsPath = "/slaves"
        self.metricsFullEndpoint = self.metricsEndpoint + ":" + self.metricsPort + self.metricsPath
        self.health = {}
        self.healthStateless = {}
        self.metrics = {}
        self.provider = Provider(provider_name=provider_name,
                                 azure_subscription_id=azure_subscription_id,
                                 azure_tenant_id=azure_tenant_id,
                                 azure_client_id=azure_client_id,
                                 azure_client_secret=azure_client_secret,
                                 azure_location=azure_location,
                                 azure_resource_group=azure_resource_group,
                                 azure_vmss_name=azure_vmss_name)


    def get_health(self):
        logger.debug("Get Health Cluster")
        try:
            r = requests.get(self.metricsFullEndpoint)
            self.health = r.json()
            #with open('tests/mockupDown2.json') as json_data:
                #self.health = json.load(json_data)
        except:
            logger.error(sys.exc_info()[0])
            exit(1)
        logger.debug("Health from : " + self.metricsFullEndpoint)
        #logger.debug(self.health)



    def filter_stateless(self):
        logger.debug("Filter the health object to get only the stateless nodes")
        self.metrics = {"totalCPU": 0, "totalMEM": 0, "usedCPU": 0, "usedMEM": 0, "ratioCPU": 0, "ratioMEM": 0,
                        "nbNodes": 0}
        for node in self.health['slaves']:
            if 'attributes' in node and node['active']:
                if 'workload' in node['attributes']:
                    if node['attributes']['workload'] == "stateless":
                        self.metrics["totalCPU"] += node['resources']['cpus']
                        self.metrics["totalMEM"] += node['resources']['mem']
                        self.metrics["usedCPU"] += node['used_resources']['cpus']
                        self.metrics["usedMEM"] += node['used_resources']['mem']
                        self.metrics["nbNodes"] = self.metrics["nbNodes"] + 1
                        logger.debug(node['hostname'] + " - Added to the stateless pool")


    def check_health(self):
        self.get_health()
        self.filter_stateless()

        self.metrics["ratioCPU"] = ((self.metrics["usedCPU"]*100)/self.metrics["totalCPU"])
        self.metrics["ratioMEM"] = ((self.metrics["usedMEM"]*100)/self.metrics["totalMEM"])
        logger.info("Total Cluster CPU = " + str(self.metrics["totalCPU"]) + " - Total Cluster CPU = " + str(self.metrics["totalMEM"]))
        logger.info("Total Used CPU = " + str(self.metrics["usedCPU"]) + " - Total Cluster MEM = " + str(self.metrics["usedMEM"]))
        logger.info("Ratio CPU = " + str(self.metrics["ratioCPU"]) + "% - Ratio MEM = " + str(self.metrics["ratioMEM"])+ "%")

    def decide_to_scale(self):
        if self.metrics["ratioCPU"] >= self.scale_up_cap and self.metrics["nbNodes"] <= self.scale_max:
            logger.info("Scale Up Kicked")
            self.provider.scale_up()
            self.waiting_scale()
        if self.metrics["ratioCPU"] <= self.scale_down_cap and self.metrics["nbNodes"] >= self.scale_min:
            logger.info("Scale Down Kicked")
            self.provider.scale_down()
            self.waiting_scale()

    def waiting_scale(self):
        current_state=self.metrics
        while self.metrics == current_state:
            logger.info("Waiting for new status of the cluster...")
            self.get_health()
            self.filter_stateless()
            time.sleep(30)