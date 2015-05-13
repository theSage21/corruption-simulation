#! /bin/bash
python3 society.py > run$1/sim$2
wc -l run$1/sim$2
