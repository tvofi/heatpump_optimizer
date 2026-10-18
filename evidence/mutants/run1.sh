#!/bin/bash
m=$1; cd /tmp/seat/rev2391/mut; rm -rf $m; cp -r clean $m
python3 mk.py $m $m > $m.txt 2>&1 || { echo APPLYFAIL >> $m.txt; exit; }
cd $m; PYTHONPATH=tests/hastub python3 tests/features.py >> ../$m.txt 2>&1; echo rc=$? >> ../$m.txt
