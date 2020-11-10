#!/bin/bash

python3 destory_table.py
python3 create_table.py

sudo docker stop liquidator
sudo docker rm liquidator
sudo docker image rm liquidator
sudo docker image build -t liquidator .
sudo docker run --name=liquidator --rm --network=host -itd liquidator rm ./conf/config.json
sudo docker stop liquidator
sudo docker run --name=liquidator --network=host -d liquidator