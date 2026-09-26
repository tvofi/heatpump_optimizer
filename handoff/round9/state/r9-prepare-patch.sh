#!/bin/sh
# Round-9 local, UNPUSHED patch to .claude/workflows/audit-find.js at 1936d5ca (prepare step 5 could never pass).
f="${1:-.claude/workflows/audit-find.js}"
python3 - "$f" <<'PY'
import sys
p=sys.argv[1]; s=open(p).read()
old="its per-dimension step lists are exactly these: ${JSON.stringify(Object.fromEntries(DIMS.map((d) => [d, rotation[d]?.steps ?? null])))}, and its rounds maps equal the ones passed to this run;"
new="its per-dimension {steps, rounds} are exactly these (compare parsed JSON): ${JSON.stringify(Object.fromEntries(DIMS.map((d) => [d, { steps: rotation[d]?.steps ?? null, rounds: rotation[d]?.rounds ?? null }])))};"
assert s.count(old)==1, 'patch anchor not found (already patched?)'
s=s.replace(old,new); s=s.replace("and the Chromium path under ~/.cache/pw-browsers","and the Chromium path (under $PLAYWRIGHT_BROWSERS_PATH if set, else ~/.cache/pw-browsers)")
open(p,'w').write(s); print('patched', p)
PY
