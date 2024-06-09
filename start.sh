#!/bin/bash

docker rmi -f gsh-ldap-api
docker-compose down
docker-compose build --no-cache
docker-compose up -d
#docker-compose up -d --build