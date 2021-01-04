#!/bin/bash

sudo docker stop liquidator
sudo docker rm liquidator
sudo docker image rm liquidator
sudo docker image build --no-cache -t liquidator .
sudo docker run --name=liquidator --network=host -itd liquidator