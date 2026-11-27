#!/bin/bash
cd "$1"
while read -r a; do
  out=$(PYTHONPATH=tests/hastub python3 tests/mutation_table.py --anchor "$a" --scripts tests/guard_pins.py 2>&1 | tail -4 | tr '\n' ' ')
  echo "$a => $out"
done < "$2"
