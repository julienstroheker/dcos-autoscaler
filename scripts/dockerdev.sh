#!/bin/bash

RUNNING=$(docker inspect -f {{.State.Running}} dcos-autoscaler 2> /dev/null) 

if [ "$?" -ne "0" ]
then
  docker run -it -v ~/.ssh:/root/.ssh -v ~/.acs:/root/.acs -v $(pwd):/app --name dcos-autoscaler dcos-autoscaler
  exit 0
fi

if [ -z $RUNNING ] || [ "$RUNNING" == "true" ]
then
  echo "Connecting to running 'dcos-autoscaler' container"
  docker exec -it dcos-autoscaler bash
else
  echo "Re-starting and connecting to an 'dcos-autoscaler' container"
  docker start dcos-autoscaler
  docker exec -it dcos-autoscaler bash
fi