#!/bin/bash

if ! which mpremote > /dev/null; then
    echo "mpremote not found. make sure you have the micropython env activated"
    exit 1
fi

# mpremote cp boot.py :
mpremote $1 mip install github:peterhinch/micropython-async/v3/threadsafe
mpremote $1 cp config.py :
mpremote $1 cp main.py :
mpremote $1 cp -r library/ :
mpremote $1 fs touch :badgedb
mpremote rm :badgedb
redis-cli flushall
