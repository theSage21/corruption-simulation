#! /bin/bash
for i in `seq 1 20`; do
    python3 society.py > run$1/sim$i
    lines_generated=`wc -l run$1/sim$i`
    echo $lines_generated
done
