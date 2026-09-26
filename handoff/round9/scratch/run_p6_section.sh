#!/bin/bash
# Run entities.py up to and including the P6 section only (the section needs the D8-01 helpers above it).
T=$1; cd $T
e=$(grep -n '^# --- path by path, so a revert' tests/entities.py | cut -d: -f1)
head -n $((e-1)) tests/entities.py > tests/_p6_section.py
echo 'print("P6_SECTION_DONE")' >> tests/_p6_section.py
PYTHONPATH=tests/hastub timeout 1200 /home/claude/venv314/bin/python tests/_p6_section.py 2>&1 | sed -n '/-- P6: every read/,$p'
rm -f tests/_p6_section.py
