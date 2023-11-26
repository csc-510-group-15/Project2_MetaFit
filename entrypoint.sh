#!/bin/bash

mongod --fork --logpath /var/log/mongodb.log

sleep 5

python insert_food_data.py &

python application.py
