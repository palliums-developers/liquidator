#!/bin/bash

docker stop liquidator-postgres
docker rm liquidator-postgres
sudo docker run --name=liquidator-postgres -e POSTGRES_PASSWORD="liquidator-postgres" -d -p 5006:5432 postgres
./restart.sh