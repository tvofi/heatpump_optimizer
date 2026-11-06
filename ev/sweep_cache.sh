# cache the full review_strength --guardrail output at every hourly cut, 60-day window as the row uses; no --fetch (bus fetched once before)
cd /home/user/heatpump_optimizer; C=$1
t=$(date -u -d 2026-11-01T00:00Z +%s); end=$(date -u -d 2026-11-06T09:00Z +%s)
while [ $t -le $end ]; do T=$(date -u -d @$t +%Y-%m-%dT%H:%MZ); S=$(date -u -d @$((t-5184000)) +%Y-%m-%dT%H:%MZ)
python3 -I tools/audit/seat/review_strength.py --window X=$S..$T --guardrail > $C/$t.out 2>/dev/null; echo $? > $C/$t.rc
t=$((t+3600)); done
