#!/bin/bash

if ! which mpremote > /dev/null; then
    echo "mpremote not found. make sure you have the micropython env activated"
    exit 1
fi

# mpremote cp boot.py :
# mpremote $1 mip install github:peterhinch/micropython-async/v3/threadsafe
mpremote $1 cp ../badge/config.py :
mpremote $1 cp ../badge/main.py :main.py
mpremote $1 cp -r ../badge/library/ :
mpremote $1 fs touch :badgedb
mpremote $1 rm :badgedb
redis-cli flushall
