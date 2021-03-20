#!/bin/sh
if docker-compose run cms python manage.py test ; then
    bash ./sh/build.sh
    az container restart --resource-group specr --name specr
else
    echo "Deployment cancelled - tests didn't pass successfully."
fi
