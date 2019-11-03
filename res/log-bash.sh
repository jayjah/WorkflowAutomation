#!/bin/bash

for (( ; ; ))
do
   echo "Pres CTRL+C to stop..."
   tail -10 /home/markus/PycharmProjects/WorkflowAutomation/res/log.txt
   sleep 5
done