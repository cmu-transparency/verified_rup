#!/bin/bash

# run from inside the manylinux2014 container,
# updated with the appropriate versions of opam, dune, ctypes, and why3:
# docker run -i -t -v `pwd`:/io manylinux2014_opam /bin/bash

ENVS=('38' '39' '310')

eval "$(opam config env)"
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