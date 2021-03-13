## Build docker image
```
$ docker context use default
$ docker build -t specr.azurecr.io/specr:deployment .
```

## Push image to ACR
```
$ docker login specr.azurecr.io
$ docker tag specr:deployment specr.azurecr.io/specr:deployment
$ docker push specr.azurecr.io/specr:deployment
```

## Deploy to ACI
```
$ az container create --resource-group specr --file azure-deployment.yaml
```

## Storage - Notes
- No data protection enabled yet (cost saving)
