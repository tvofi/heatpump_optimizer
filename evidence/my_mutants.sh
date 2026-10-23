#!/bin/bash
# Reviewer's own plants on the #2671 merge-resolution lines (not the fixer's tool).
cd ~/hpo-seats/r10s5/rev-2671-mut || exit 2
R=tools/audit/seat/cloud_relay.sh; L=tools/audit/seat/ledger.py
plant() { # name file python-replace-old python-replace-new cmd
  local name=$1 f=$2 old=$3 new=$4; shift 4
  python3 - "$f" "$old" "$new" <<'EOF' || { echo "RESULT mutant=$name PLANT-MISSED"; return; }
import sys; p,o,n=sys.argv[1:4]; s=open(p).read()
assert s.count(o)==1, s.count(o); open(p,'w').write(s.replace(o,n))
EOF
  out=$("$@" 2>&1); rc=$?
  git checkout -q -- "$f"
  echo "RESULT mutant=$name rc=$rc fails=$(grep -c '^ *FAIL' <<< "$out") $(grep -E 'checks, [0-9]+ failed' <<< "$out" | tail -1)"
  grep -E '^ *FAIL' <<< "$out" | head -4 | sed 's/^/    /'
}
plant M1-verdict-unposted-dropped $R '  ledger_open verdict-unposted "$pr" "$head" "$first"
' '' bash $R --self-test
plant M2-unposted-silent $R 'unposted() { echo "cloud_relay: UNPOSTED #$1: $3 (the verdict stays owed in the ledger)" >&2; }' 'unposted() { :; }' bash $R --self-test
plant M3-review-arm-dropped $L '        ("refs/heads/review/", "confirm-owed"))' '        )' bash $R --self-test
plant M4-kinds-dropped $L '    "probe-refused": "derived", "confirm-owed": "derived",' '' python3 -I $L --self-test
plant M5-confirm-why-dropped $R '"confirm failed: $(last_line "$out")"' '"confirm failed"' bash $R --self-test
echo "null:"; out=$(bash $R --self-test 2>&1); echo "RESULT null rc=$? $(grep -E 'checks, [0-9]+ failed' <<< "$out" | tail -1)"
git status --short
