import logging
import sys
import os

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import VirtualMachineScaleSet

LOGGER = logging.getLogger('dcos-autoscaler')


class Azure(object):
    def __init__(self, azure_subscription_id, azure_tenant_id, azure_client_id, azure_client_secret,
                 azure_location, azure_resource_group, azure_vmss_name):
        LOGGER.debug("Provider Azure used")

        if (azure_subscription_id == "" or
                azure_tenant_id == "" or
                azure_client_id == "" or
                azure_client_secret == ""):
            LOGGER.error("Missing Azure credentials. Please provide --azure-subscription-id "
                         "--azure-tenant-id --azure-client-id --azure-client-secret")
            sys.exit(1)
        if azure_location == "" or azure_resource_group == "" or azure_vmss_name == "":
            LOGGER.error("Missing Azure Informations. Please verify --azure-location "
                         "--azure-resource-group --azure-vmss-name")
            sys.exit(1)
        subscription_id = azure_subscription_id
        LOGGER.debug("Azure - Service Principal Credentials Init")
        credentials = ServicePrincipalCredentials(
            client_id=azure_client_id,
            secret=azure_client_secret,
            tenant=azure_tenant_id
        )
        LOGGER.debug("Azure - Compute Client Init")
        self.compute_client = ComputeManagementClient(credentials, subscription_id)
        self.azure_location = azure_location
        self.azure_resource_group = azure_resource_group
        self.azure_vmss_name = azure_vmss_name

    def get_vmss_info(self):
        LOGGER.debug("Getting the VMSS informations")
        return self.compute_client.virtual_machine_scale_sets.get(self.azure_resource_group,
                                                                  self.azure_vmss_name)

    def scale(self, new_capacity):
        vmss = self.get_vmss_info()
        vmss_new = VirtualMachineScaleSet(vmss.location, sku=vmss.sku)
        vmss_new.sku.capacity = vmss.sku.capacity + new_capacity
        scaling_action = self.compute_client.virtual_machine_scale_sets.create_or_update(
            self.azure_resource_group, self.azure_vmss_name, vmss_new)
        res = scaling_action.result()
        return res

    def scale_up(self):
        LOGGER.debug("Azure - Scaling UP the VMSS")
        self.scale(2)

    def scale_down(self):
        LOGGER.debug("Azure - Scaling Down the VMSS")
        self.scale(-1)
