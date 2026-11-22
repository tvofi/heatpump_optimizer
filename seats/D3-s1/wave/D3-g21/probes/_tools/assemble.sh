#!/bin/bash
# assemble.sh <key>: probe-src/<key>.py (with a '#@PRE' line) -> probe-tree probes/probe_<key>.py
k=$1; D=$HOME/probe-tree/dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes
python3 - "$HOME/probe-src/$k.py" "$HOME/probe-src/PRE.py" "$D/probe_$k.py" <<'PY'
import sys
src, pre, out = sys.argv[1:]
t = open(src).read().replace("#@PRE\n", open(pre).read(), 1).replace("#@HOLD\n", open(pre.replace("PRE.py","HOLD_REACH.py")).read(), 1).replace("#@DHWCAP\n", open(pre.replace("PRE.py","DHWCAP.py")).read(), 1)
open(out, "w").write(t.rstrip() + "\nfooter()\n")
PY
cd $HOME/probe-tree && PYTHONPATH=tests/hastub timeout 600 python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_$k.py
