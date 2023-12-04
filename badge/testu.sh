#!/bin/bash

if ! which mpremote > /dev/null; then
    echo "mpremote not found. make sure you have the micropython env activated"
    exit 1
fi

# mpremote cp boot.py :
# mpremote cp config.py :
# mpremote cp main.py :
# mpremote cp library/display.py :library/
mpremote cp library/ir.py :library/
mpremote cp library/monkeybadge.py :library/
# mpremote cp library/radio.py :library/
# mpremote cp library/ticker.py :library/
# mpremote fs touch :badgedb
# mpremote fs touch :badgedb
# mpremote rm :badgedb
# redis-cli flushall

