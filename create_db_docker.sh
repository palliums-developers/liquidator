
sudo docker run --name=liquidator-postgres -v ./create_table.sql:/create_table.sql -e POSTGRES_PASSWORD="liquidator-postgres" -d -p 5006:5432 postgres
