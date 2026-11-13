#!/bin/bash
# run from a tree root: both blocks (arbiter block; feedback seam block with its emitted 4-statement prelude)
set -o pipefail
python3 tools/audit/seat/features_block.py "R.section(\"pump-duty arbiter — mode and set-points per plan step" "_pa_subs = _PaCoord(" 2>&1 | tail -2 || exit 1
python3 tools/audit/seat/features_block.py --prelude 'exec(open("/tmp/tmp.SsbmTdlI06/fbprelude.py").read())' "# --- R10-WATER-SETPOINT-FEEDBACK (outside report #3380" "_fb_floor = _fb_sim(clamp=(26.4" 2>&1 | tail -2 || exit 1
