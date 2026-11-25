#!/usr/bin/env bash
# Run the two blocks on the tree as it is; label in $1.
set -u
cd /Users/timmalmstrom/hpo-seats/r10s6/rev-3866-delta
S=/Users/timmalmstrom/hpo-seats/r10s6/rev-3866-delta-scratch
L=$1
FB=tools/audit/seat/features_block.py
A_START="# R11-OWNER-FLOWCAP (tvofi, 2026-11-22"
A_END="_pa_bl_fb, _ = _pa_boost_level(\"ss\", 1.0, \"channel\", power_meter=True)"
B_START="# The loop's own arithmetic at each boundary it draws"
B_END="# R1's bracket is closed at both ends"
if [ ! -f "$S/preA.py" ]; then
  python3 $FB --emit-prelude "$S/preA.py" "$A_START" "$A_END" > "$S/emitA.log" 2>&1; echo "emitA rc=$?"
  python3 $FB --emit-prelude "$S/preB.py" "$B_START" "$B_END" > "$S/emitB.log" 2>&1; echo "emitB rc=$?"
fi
python3 $FB --prelude "exec(open('$S/preA.py').read())" "$A_START" "$A_END" > "$S/$L.A.log" 2>&1; echo "$L A rc=$?"
python3 $FB --prelude "exec(open('$S/preB.py').read())" "$B_START" "$B_END" > "$S/$L.B.log" 2>&1; echo "$L B rc=$?"
grep -a "FAIL" "$S/$L.A.log" "$S/$L.B.log" | cut -c1-220 | head -12
