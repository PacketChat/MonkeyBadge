#!/bin/bash

if ! which mpremote > /dev/null; then
    echo "mpremote not found. make sure you have the micropython env activated"
    exit 1
fi

# mpremote cp boot.py :
mpremote cp config.py :
mpremote cp main.py :
mpremote cp -r library/ :
mpremote rm :badgedb
