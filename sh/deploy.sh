#!/bin/sh
docker context use default
docker-compose run cms python3 manage.py collectstatic --noinput
docker build -t specr.azurecr.io/specr:deployment .
docker push specr.azurecr.io/specr:deployment
az container restart --resource-group specr --name specr
