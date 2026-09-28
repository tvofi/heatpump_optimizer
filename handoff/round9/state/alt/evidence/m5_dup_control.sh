#!/usr/bin/env bash
# M5 two-arm control: is duplication_blocks blind to a copy placed in a DIFFERENT module?
# Run inside a throwaway detached worktree at origin/main (31394964).
set -u
F=custom_components/heatpump_optimizer
sed -n '45,76p' $F/tariff.py | sed 's/def _window_slot(/def _window_slot_probe_copy(/' > /tmp/m5copy.py   # tariff._window_slot, 32 lines
{ echo; echo; cat /tmp/m5copy.py; } >> $F/sysid.py
python3 tests/structure.py 2>&1 | grep -E "^\s+(ok|FAIL|IMPROVED)?\s*duplication_blocks|FAIL duplication" | sed 's/^/ARM A (copy into sysid.py): /'
git checkout -q -- $F
{ echo; echo; cat /tmp/m5copy.py; } >> $F/tariff.py
python3 tests/structure.py 2>&1 | grep -E "duplication_blocks" | grep -E "ok|FAIL" | sed 's/^/ARM B (control, copy into tariff.py): /'
git checkout -q -- $F
