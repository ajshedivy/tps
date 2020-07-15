#!/bin/bash

echo "starting script"
./scripts/run \
   --network $1 \
   --timeseries $2 \
   --firstscores $3 \
   --prevscores $4\
   --partialmodel $5 \
   --peptidemap $6 \
   --source $7 \
   --threshold 0.01

   echo "finished script"
