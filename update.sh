#!/bin/bash

sudo docker stop liquidator
sudo docker rm liquidator
sudo docker image rm liquidator
sudo docker image build -t liquidator .
sudo docker run --name=liquidator --network=host -d liquidator