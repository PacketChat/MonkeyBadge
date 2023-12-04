#!/bin/bash

here=$(dirname $(readlink -f $0))
badge="$(dirname $here)/badge"

if ! which mpremote > /dev/null; then
    echo "mpremote not found. make sure you have the micropython env activated"
    exit 1
fi

if [[ "$1" -lt 1 ]] ||  [[ "$1" -gt 5 ]]; then
    echo "Bad object number"
    exit 1
fi


# mpremote cp boot.py :
# mpremote $1 mip install github:peterhinch/micropython-async/v3/threadsafe
mpremote run "$here/tools/clean_flags.py"
mpremote cp config.py :monkeyconfig.py
cd $badge
mpremote cp -r library/ir_tx :
cd $here
mpremote cp config.py :
mpremote cp main.py :main.py
mpremote cp -r library/ :
mpremote touch "ho$1"
