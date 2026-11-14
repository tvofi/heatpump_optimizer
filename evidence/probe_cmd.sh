#!/bin/bash
# reviewer probes: the supply-switch block with the probe block inserted before the ceiling probe
cd "${REPO:-/home/user/rev}"
W=/home/user/w
python3 - <<'PY'
import re
s = open("tests/features.py").read(); p = open("/home/user/w/probe_block.py").read()
i = s.index("# --- R10-CEILING-PROBE")
open("tests/_rev_probe_features.py", "w").write(s[:i] + p + "\n" + s[i:])
PY
python3 -c "
import sys; sys.path.insert(0,'tools/audit/seat'); import features_block as f
sys.exit(f.run('tests/_rev_probe_features.py', 'R.section(\"supply switch at step boundaries (#2492', '# --- R10-CEILING-PROBE', prelude=(\"exec(open('$W/pre_sa.py').read())\",)))" 2>&1 | python3 -c "import sys; [print(l, end='') for l in sys.stdin if 'probe' in l or 'FEATURES' in l or 'Error' in l or 'Trace' in l]"
rc=${PIPESTATUS[0]}; rm -f tests/_rev_probe_features.py; exit $rc
