import logging
import sys
import time

import click

from autoscaler.cluster import Cluster

logger = logging.getLogger('dcos-autoscaler')

DEBUG_LOGGING_MAP = {
    0: logging.CRITICAL,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}

@click.command()
@click.option('--provider-name', help='provider who host the cluster. ex: Azure, GCE, AWS', type=click.Choice(['Azure']))
@click.option("--timer", default=60, help='time in seconds between successive checks')
@click.option('--scale-up-cap', default=80, help='Threshold to kick the scale Up in percentage, default is 80')
@click.option('--scale-down-cap', default=20, help='Threshold to kick the scale Down in percentage, default is 20')
@click.option('--scale-max', default=20, help='Maximum nodes limitation to scale, default is 20')
@click.option('--scale-min', default=3, help='Minimum nodes limitation to scale, default is 3')
@click.option('--azure-subscription-id', default="", help='Azure Subscription ID', envvar='AZURE_SUBSCRIPTION_ID')
@click.option('--azure-tenant-id', default="", help='Azure Tenant ID', envvar='AZURE_TENANT_ID')
@click.option('--azure-client-id', default="", help='Azure Client ID', envvar='AZURE_CLIENT_ID')
@click.option('--azure-client-secret', default="", help='Azure Client Secret', envvar='AZURE_CLIENT_SECRET')
@click.option('--azure-location', default="eastus", help='Azure DC Location', envvar='AZURE_LOCATION')
@click.option('--azure-resource-group', default="", help='Azure Resource Group', envvar='AZURE_RG')
@click.option('--azure-vmss-name', default="", help='Azure VMSS Name to scale', envvar='AZURE_VMSS')
@click.option('--verbose', '-v',
              help="Sets the debug noise level, specify multiple times "
                   "for more verbosity.",
              type=click.IntRange(0, 3, clamp=True),
              count=True, default=2)

def main(provider_name, timer, scale_up_cap, scale_down_cap, scale_max, scale_min,
         azure_subscription_id, azure_tenant_id, azure_client_id, azure_client_secret,
         azure_location, azure_resource_group, azure_vmss_name,
         verbose):
    #Logger settings
    logger_handler = logging.StreamHandler(sys.stderr)
    logger_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(logger_handler)
    logger.setLevel(DEBUG_LOGGING_MAP.get(verbose, logging.CRITICAL))

    logger.debug("Debug mode activated")

    if not provider_name:
        logger.error("Provider not specified, ex : --provider Azure")
        sys.exit(1)

    logger.debug("Provider Name : " + provider_name)
    logger.debug("Timer : " + str(timer))
    logger.debug("Scale Up Cap : " + str(scale_up_cap))
    logger.debug("Scale Down Cap : " + str(scale_down_cap))
    logger.debug("Maximum Nodes : " + str(scale_max))
    logger.debug("Minimum Nodes : " + str(scale_min))
    logger.debug("Azure Subscription ID : " + azure_subscription_id)
    logger.debug("Azure Tenant ID : " + azure_tenant_id)
    logger.debug("Azure Client ID : " + azure_client_id)
    logger.debug("Azure Client Secret : " + azure_client_secret)
    logger.debug("Azure Resource Group : " + azure_resource_group)
    logger.debug("Azure Location : " + azure_location)
    logger.debug("Azure VMSS Targeted : " + azure_vmss_name)

    logger.info("DC/OS Autoscaler Started")

    cluster = Cluster(provider_name=provider_name,
                      scale_up_cap=scale_up_cap,
                      scale_down_cap=scale_down_cap,
                      scale_max=scale_max,
                      scale_min=scale_min,
                      azure_subscription_id=azure_subscription_id,
                      azure_tenant_id=azure_tenant_id,
                      azure_client_id=azure_client_id,
                      azure_client_secret=azure_client_secret,
                      azure_location=azure_location,
                      azure_resource_group=azure_resource_group,
                      azure_vmss_name=azure_vmss_name)
    while True:
        cluster.check_health()
        cluster.decide_to_scale()
        time.sleep(timer)

    logger.info("DC/OS Autoscaler Stopped")


if __name__ == "__main__":
    main()