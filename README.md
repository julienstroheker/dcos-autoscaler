## dcos-autoscaler

## In development

Experimental project

Autoscaling a DCOS cluster hosted in a provider by specifying options.

### TO DO :
- [ ] Tests
- [ ] Documentation
- [ ] CI


### Example for Microsoft Azure :

```python main.py -vv
        --provider-name Azure
        --azure-subscription-id 8f26a68d-8613-4a0c-a2a6-2d2d0e261910
        --azure-tenant-id 333c7f36-ba66-49f1-9d8a-a450816e8516
        --azure-client-id 5308694f-bed6-494a-9c19-335b3c40b8b3
        --azure-client-secret myP@ssw0rd1!
        --azure-resource-group myResourceGroup
        --azure-vmss-name dcos-agentprivsl-1453224-vmss
        --timer 5
```