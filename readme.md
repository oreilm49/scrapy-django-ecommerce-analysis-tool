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
$ docker login azure
$ docker context use specr
$ docker compose up
```

## Storage - Notes
- No data protection enabled yet (cost saving)

## TODO
- remove minio from project - replace with default django filestorage implementation
- ensure that ACI specr can use the specr-vnet vpn. This is required to access the storage account.

