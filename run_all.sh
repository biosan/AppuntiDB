#!/bin/sh

python3 run.py &> /dev/null &disown;
python3 run_amqp.py #&> /dev/null &disown;
