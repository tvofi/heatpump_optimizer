cd /home/user/rev
t=$(date -u -d 2026-11-01T00:00Z +%s); end=$(date -u -d 2026-11-06T09:00Z +%s)
while [ $t -le $end ]; do T=$(date -u -d @$t +%Y-%m-%dT%H:%MZ)
python3 -I tools/audit/seat/review_strength.py --window X=2026-09-07T00:00Z..$T --guardrail 2>/dev/null | grep -- '-> would-trip' | sed "s/^/$T /"
t=$((t+3600)); done
