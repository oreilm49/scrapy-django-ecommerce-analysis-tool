#!/bin/sh
bash ./sh/build.sh
az container create --resource-group specr --name specr
