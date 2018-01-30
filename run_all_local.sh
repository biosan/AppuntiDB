#!/bin/bash

./env/bin/python3 run.py &> /dev/null &disown;
./env/bin/python3 run_amqp.py &> /dev/null &disown;
