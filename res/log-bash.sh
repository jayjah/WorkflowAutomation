#!/bin/bash

for (( ; ; ))
do
   echo "Pres CTRL+C to stop..."
   tail -10 ./log.txt
   sleep 5
done