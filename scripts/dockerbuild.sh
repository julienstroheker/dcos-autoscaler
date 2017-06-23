#!/bin/bash

docker stop dcos-autoscaler
docker rm dcos-autoscaler
docker build -t dcos-autoscaler .