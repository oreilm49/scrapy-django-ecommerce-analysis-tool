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
