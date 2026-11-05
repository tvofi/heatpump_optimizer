#!/bin/bash
m=$1; cd /tmp/tmp.7evDx9Kuim/mut/$m
PYTHONPATH=tests/hastub OPENBLAS_CORETYPE=Haswell python3 tests/features.py > ../$m.features.log 2>&1; echo "rc=$?" >> ../$m.features.log
echo "$m done: $(tail -n 2 ../$m.features.log | tr '\n' ' ')"
