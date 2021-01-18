#!/bin/bash

sudo docker stop liquidator-postgres
sudo docker rm liquidator-postgres
sudo docker run --name=liquidator-postgres -v ${PWD}/create_table.sql:/create_table.sql -e POSTGRES_PASSWORD="liquidator-postgres" -d -p 5006:5432 postgres
sudo docker exec -itd liquidator-postgres psql -U postgres -f /create_table.sql
./restart.sh