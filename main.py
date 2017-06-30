import logging
import sys
import time
import os

import click

from autoscaler.cluster import Cluster

LOGGER = logging.getLogger('dcos-autoscaler')

DEBUG_LOGGING_MAP = {
    0: logging.CRITICAL,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}

@click.command()
@click.option('--provider-name',
              help='provider who host the cluster. ex: Azure, GCE, AWS',
              envvar='AS_PROVIDER_NAME',
              type=click.Choice(['Azure']))
@click.option('--timer',
              default=60,
              help='time in seconds between successive checks',
              envvar='AS_TIMER')
@click.option('--scale-up-cap',
              default=80,
              help='Threshold to kick the scale Up in percentage, default is 80',
              envvar='AS_SCALE_UP_MAX')
@click.option('--scale-down-cap',
              default=20,
              help='Threshold to kick the scale Down in percentage, default is 20',
              envvar='AS_SCALE_DOWN_MAX')
@click.option('--scale-max',
              default=20,
              help='Maximum nodes limitation to scale, default is 20',
              envvar='AS_SCALE_MAX')
@click.option('--scale-min',
              default=3,
              help='Minimum nodes limitation to scale, default is 3',
              envvar='AS_SCALE_MIN')
@click.option('--endpoint-path',
              default="http://leader.mesos:5050/slaves",
              help='Endpoint to fetch metrics, default is http://leader.mesos:5050/slaves',
              envvar='AS_ENDPOINT')
@click.option('--azure-subscription-id',
              default="",
              help='Azure Subscription ID',
              envvar='AZURE_SUBSCRIPTION_ID')
@click.option('--azure-tenant-id',
              default="",
              help='Azure Tenant ID',
              envvar='AZURE_TENANT_ID')
@click.option('--azure-client-id',
              default="",
              help='Azure Client ID',
              envvar='AZURE_CLIENT_ID')
@click.option('--azure-client-secret',
              default="",
              help='Azure Client Secret',
              envvar='AZURE_CLIENT_SECRET')
@click.option('--azure-location',
              default="eastus",
              help='Azure DC Location',
              envvar='AZURE_LOCATION')
@click.option('--azure-resource-group',
              default="",
              help='Azure Resource Group',
              envvar='AZURE_RG')
@click.option('--azure-vmss-name',
              default="",
              help='Azure VMSS Name to scale',
              envvar='AZURE_VMSS')
@click.option('--verbose', '-v',
              help="Sets the debug noise level, specify multiple times "
                   "for more verbosity.",
              type=click.IntRange(0, 3, clamp=True),
              envvar='AS_VERBOSE',
              count=True, default=2)

def main(provider_name, timer, scale_up_cap, scale_down_cap, scale_max, scale_min, endpoint_path,
         azure_subscription_id, azure_tenant_id, azure_client_id, azure_client_secret,
         azure_location, azure_resource_group, azure_vmss_name,
         verbose):
    #Logger settings
    logger_handler = logging.StreamHandler(sys.stderr)
    loginformater = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger_handler.setFormatter(logging.Formatter(loginformater))
    LOGGER.addHandler(logger_handler)
    LOGGER.setLevel(DEBUG_LOGGING_MAP.get(verbose, logging.CRITICAL))

    LOGGER.debug("Debug mode activated")

    #os.environ.get('DATABASE_NAME', '')

    if not os.environ.get('AS_PROVIDER_NAME', provider_name):
        LOGGER.error("Provider not specified, ex : --provider-name Azure")
        sys.exit(1)

    LOGGER.debug("Provider Name : " + str(os.environ.get('AS_PROVIDER_NAME', provider_name)))
    LOGGER.debug("Timer : " + str(os.environ.get('AS_TIMER', timer)))
    LOGGER.debug("Scale Up Cap : " + str(os.environ.get('AS_SCALE_UP_MAX', scale_up_cap)))
    LOGGER.debug("Scale Down Cap : " + str(os.environ.get('AS_SCALE_DOWN_MAX', scale_down_cap)))
    LOGGER.debug("Maximum Nodes : " + str(os.environ.get('AS_SCALE_MAX', scale_max)))
    LOGGER.debug("Minimum Nodes : " + str(os.environ.get('AS_SCALE_MIN', scale_min)))
    LOGGER.debug("EndPoint Path : " + str(os.environ.get('AS_ENDPOINT', endpoint_path)))
    LOGGER.debug("Azure Subscription ID : " +
                 str(os.environ.get('AZURE_SUBSCRIPTION_ID', azure_subscription_id)))
    LOGGER.debug("Azure Tenant ID : " + str(os.environ.get('AZURE_TENANT_ID', azure_tenant_id)))
    LOGGER.debug("Azure Client ID : " + str(os.environ.get('AZURE_CLIENT_ID', azure_client_id)))
    LOGGER.debug("Azure Client Secret : " +
                 str(os.environ.get('AZURE_CLIENT_SECRET', azure_client_secret)))
    LOGGER.debug("Azure Resource Group : " + str(os.environ.get('AZURE_RG', azure_resource_group)))
    LOGGER.debug("Azure Location : " + str(os.environ.get('AZURE_LOCATION', azure_location)))
    LOGGER.debug("Azure VMSS Targeted : " + str(os.environ.get('AZURE_VMSS', azure_vmss_name)))

    LOGGER.info("DC/OS Autoscaler Started")

    cluster = Cluster(provider_name=os.environ.get('AS_PROVIDER_NAME', provider_name),
                      scale_up_cap=os.environ.get('AS_SCALE_UP_MAX', scale_up_cap),
                      scale_down_cap=os.environ.get('AS_SCALE_DOWN_MAX', scale_down_cap),
                      scale_max=os.environ.get('AS_SCALE_MAX', scale_max),
                      scale_min=os.environ.get('AS_SCALE_MIN', scale_min),
                      endpoint_path=os.environ.get('AS_ENDPOINT', endpoint_path),
                      azure_subscription_id=os.environ.get('AZURE_SUBSCRIPTION_ID',
                                                           azure_subscription_id),
                      azure_tenant_id=os.environ.get('AZURE_TENANT_ID', azure_tenant_id),
                      azure_client_id=os.environ.get('AZURE_CLIENT_ID', azure_client_id),
                      azure_client_secret=os.environ.get('AZURE_CLIENT_SECRET',
                                                         azure_client_secret),
                      azure_location=os.environ.get('AZURE_LOCATION', azure_location),
                      azure_resource_group=os.environ.get('AZURE_RG', azure_resource_group),
                      azure_vmss_name=os.environ.get('AZURE_VMSS', azure_vmss_name))
    while True:
        metrics = {"totalCPU": 0, "totalMEM": 0, "usedCPU": 0,
                   "usedMEM": 0, "ratioCPU": 0, "ratioMEM": 0,
                   "nbNodes": 0}
        cluster.check_health(metrics)
        LOGGER.info("Total Cluster CPU = " + str(metrics["totalCPU"]) +
                    " - Total Cluster CPU = " + str(metrics["totalMEM"]))
        LOGGER.info("Total Used CPU = " + str(metrics["usedCPU"]) +
                    " - Total Cluster MEM = " + str(metrics["usedMEM"]))
        LOGGER.info("Ratio CPU = " + str(metrics["ratioCPU"]) +
                    "% - Ratio MEM = " + str(metrics["ratioMEM"])+ "%")
        if cluster.decide_to_scale(metrics) == 1:
            LOGGER.info("Scale Up Kicked ... In Progress")
            cluster.scale_cluster_up(metrics)
        if cluster.decide_to_scale(metrics) == -1:
            LOGGER.info("Scale Down Kicked... In Progress")
            cluster.scale_cluster_down(metrics)
        time.sleep(timer)

    LOGGER.info("DC/OS Autoscaler Stopped")


if __name__ == "__main__":
    main()
    