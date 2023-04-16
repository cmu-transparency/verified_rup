#!/bin/bash

ENVS=('38' '39' '310')

eval "$(conda shell.bash hook)"

for zone in "${ENVS[@]}"
do
    conda activate py${zone}
    python -m build 
    conda deactivate
    WHEEL=$(ls -Art1 dist | tail -n 1)
    echo $WHEEL
    auditwheel addtag dist/$WHEEL -w dist/
    rm dist/$WHEEL
    WHEEL=$(ls -Art1 dist | tail -n 1)
    wheel tags --platform-tag=-linux_x86_64 dist/$WHEEL
    rm dist/$WHEEL
done