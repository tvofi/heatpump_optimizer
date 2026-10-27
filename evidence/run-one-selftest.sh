#!/bin/bash
set -u
name=$1; dir=$2; out=$3
( cd "$dir" && PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --self-test ) > "$out" 2>&1
echo "RC=$?" >> "$out"
