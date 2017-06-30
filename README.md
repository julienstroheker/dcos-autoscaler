# dcos-autoscaler
[![Build Status](https://travis-ci.org/julienstroheker/dcos-autoscaler.svg?branch=master)](https://travis-ci.org/julienstroheker/dcos-autoscaler)


![](./docs/dcos-autoscaler-logo.png)

## !! In development !!

Experimental project

Autoscaling a DCOS cluster hosted in a cloud provider, either Private or Public, by specifying options.

![](./docs/Overview.png)

!! In development using Microsoft Azure, but more that welcome to have contribution for AWS, GCE and others providers...

You can either use switch (ex: --timer) or environement variables (ex: export AS_TIMER=60)

| Option | Variable | Description | Default |
|---|---|---|---|
| --provider-name | AS_PROVIDER_NAME | provider who host the cluster. ex: Azure, GCE, AWS... |   |
| --timer | AS_TIMER | time in seconds between successive checks | 60 |
| --scale-up-cap | AS_SCALE_UP_MAX | Threshold to kick the scale Up in percentage | 80 |
| --scale-down-cap | AS_SCALE_DOWN_MAX | Threshold to kick the scale Down in percentage | 20 |
| --scale-max | AS_SCALE_MAX | Maximum nodes limitation to scale | 20 |
| --scale-min | AS_SCALE_MIN | Minimum nodes limitation to scale | 3 |
| --azure-subscription-id | AZURE_SUBSCRIPTION_ID | Azure Subscription ID |   |
| --azure-tenant-id | AZURE_TENANT_ID | Azure Tenant ID |   |
| --azure-client-id | AZURE_CLIENT_ID | Azure Client ID |   |
| --azure-client-secret | AZURE_SECRET_ID | Azure Client Secret |   |
| --azure-location | AZURE_LOCATION | Azure DC Location |   |
| --azure-resource-group | AZURE_RG | Azure Resource Group |   |
| --azure-vmss-name | AZURE_VMSS | Azure VMSS Name to scale |   |
| --v --vv --vvv | AS_VERBOSE | The debug noise level | -vv |

High level orverview of the very simple code architecture :

![](./docs/OverviewArchi.png)

### Output in debug mode :

```

2017-06-23 20:20:41,287 - dcos-autoscaler - DEBUG - Debug mode activated
2017-06-23 20:20:41,287 - dcos-autoscaler - DEBUG - Provider Name : Azure
2017-06-23 20:20:41,287 - dcos-autoscaler - DEBUG - Timer : 5
2017-06-23 20:20:41,287 - dcos-autoscaler - DEBUG - Scale Up Cap : 80
2017-06-23 20:20:41,288 - dcos-autoscaler - DEBUG - Scale Down Cap : 20
2017-06-23 20:20:41,288 - dcos-autoscaler - DEBUG - Maximum Nodes : 20
2017-06-23 20:20:41,288 - dcos-autoscaler - DEBUG - Minimum Nodes : 3
2017-06-23 20:20:41,288 - dcos-autoscaler - DEBUG - Azure Subscription ID : 8f26a68d-8613-4a0c-a2a6-2d2d0e261910
2017-06-23 20:20:41,288 - dcos-autoscaler - DEBUG - Azure Tenant ID : 333c7f36-ba66-49f1-9d8a-a450816e8516
2017-06-23 20:20:41,288 - dcos-autoscaler - DEBUG - Azure Client ID : 5308694f-bed6-494a-9c19-335b3c40b8b3
2017-06-23 20:20:41,288 - dcos-autoscaler - DEBUG - Azure Client Secret : myP@ssw0rd1
2017-06-23 20:20:41,288 - dcos-autoscaler - DEBUG - Azure Resource Group : myResourceGroup
2017-06-23 20:20:41,289 - dcos-autoscaler - DEBUG - Azure Location : eastus
2017-06-23 20:20:41,289 - dcos-autoscaler - DEBUG - Azure VMSS Targeted : dcos-agentprivsl-1453224-vmss
2017-06-23 20:20:41,289 - dcos-autoscaler - INFO - DC/OS Autoscaler Started
2017-06-23 20:20:41,289 - dcos-autoscaler - DEBUG - Provider Azure used
2017-06-23 20:20:41,518 - dcos-autoscaler - DEBUG - Get Health Cluster
2017-06-23 20:20:41,529 - dcos-autoscaler - DEBUG - Health from : http://leader.mesos:5050/slaves
2017-06-23 20:20:41,530 - dcos-autoscaler - DEBUG - Filter the health object to get only the stateless nodes
2017-06-23 20:20:41,530 - dcos-autoscaler - DEBUG - 10.1.0.5 - Added to the stateless pool
2017-06-23 20:20:41,530 - dcos-autoscaler - DEBUG - 10.1.0.7 - Added to the stateless pool
2017-06-23 20:20:41,530 - dcos-autoscaler - DEBUG - 10.1.0.4 - Added to the stateless pool
2017-06-23 20:20:41,530 - dcos-autoscaler - DEBUG - 10.1.0.6 - Added to the stateless pool
2017-06-23 20:20:41,530 - dcos-autoscaler - DEBUG - 10.1.0.8 - Added to the stateless pool
2017-06-23 20:20:41,530 - dcos-autoscaler - INFO - Total Cluster CPU = 10.0 - Total Cluster CPU = 29715.0
2017-06-23 20:20:41,530 - dcos-autoscaler - INFO - Total Used CPU = 7.0 - Total Cluster MEM = 3584.0
2017-06-23 20:20:41,531 - dcos-autoscaler - INFO - Ratio CPU = 70.0% - Ratio MEM = 12.061248527679624%
```

### Running the autoscaler in your cluster

Marathon.json 

### Example for Microsoft Azure :

Documentation in progress...

In this example, you:
* [Create a SPN](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal) in your Azure Subscription.
* Deployed a DC/OS cluster, Manually, or using ACS it doesn't matter, you just have to use VMSS
* [Added a custom mesos attribute on the nodes](https://dcos.io/docs/1.8/administration/faq/#q-how-to-add-mesos-attributes-to-nodes-to-use-marathon-constraints-) that you want to scale


From inside the cluster, run this command :
```
docker run -it -d --name=autoscaler
    -e AZURE_CLIENT_ID='5308694f-bed6-494a-9c19-335b3c40b8b3'
    -e AZURE_CLIENT_SECRET='myP@ssw0rd1!' 
    -e AZURE_TENANT_ID='333c7f36-ba66-49f1-9d8a-a450816e8516'
    -e AZURE_SUBSCRIPTION_ID='8f26a68d-8613-4a0c-a2a6-2d2d0e261910' 
    julienstroheker/dcos-autoscaler python main.py -vv 
    --provider-name Azure 
    --azure-location eastus
    --azure-resource-group myResourceGroup
    --azure-vmss-name dcos-agentprivsl-1453224-vmss
```
### TO DO :
- [ ] Tests
- [ ] Documentation
- [ ] CI
