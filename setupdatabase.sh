#!/bin/bash
set -e

# Don't create database if for example using a docker image that has created an empty database

./manage.py migrate --run-syncdb
./manage.py createsuperuser --username=admin --email=markoreilly1992@gmail.com --noinput
./manage.py set_fake_passwords
./manage.py runscript --traceback load_accounts
./manage.py runscript --traceback load_cms
exit 0
