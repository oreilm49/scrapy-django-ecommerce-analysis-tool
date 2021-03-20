#!/bin/sh
bash ./sh/build.sh
az container restart --resource-group specr --name specr
