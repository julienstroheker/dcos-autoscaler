import logging
import requests
import json

from autoscaler.providerAzure import Azure

logger = logging.getLogger('dcos-autoscaler')

class Provider(object):
    def __init__(self, provider_name, azure_subscription_id, azure_tenant_id, azure_client_id, azure_client_secret,
                 azure_location, azure_resource_group, azure_vmss_name):
        self.provider_name = provider_name
        if provider_name == 'Azure':
            self.provider = Azure(azure_subscription_id=azure_subscription_id,
                                  azure_tenant_id=azure_tenant_id,
                                  azure_client_id=azure_client_id,
                                  azure_client_secret=azure_client_secret,
                                  azure_location=azure_location,
                                  azure_resource_group=azure_resource_group,
                                  azure_vmss_name=azure_vmss_name)

    def scale_up(self):
        logger.debug("Calling the Provider to Scale Up")
        self.provider.scale_up()

    def scale_down(self):
        logger.debug("Calling the Provider to Scale Down")
        self.provider.scale_down()
