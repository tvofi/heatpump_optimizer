import json, sys
out = sys.argv[1]
MC = 'MECHANICAL_CLASSES=" ci-red ci-wait ci-pending ci-cancelled red-unanswered body contract conflict head-moved carry-missing carry ungated "'
cls = MC.split('"')[1].split()
B = 'tools/audit/seat/bus.sh'; R = 'tools/audit/seat/cloud_relay.sh'
bus = []
for c in cls:
    bus.append(dict(name='B-drop-'+c, file=B, old=MC, new=MC.replace(' '+c+' ', ' ', 1)))
for c in ['root-cause-unanswered', 'preflight-mismatch', 'harness']:
    bus.append(dict(name='B-add-'+c, file=B, old=MC, new=MC[:-1] + c + ' "'))
L = '$1 == t && $3 ~ /^[0-9]+$/ { p = $3 }'
bus += [
 dict(name='B-exempt-off', file=B, old='mechanical_block "$1" && return 0  # mut:mechclass', new='false && return 0  # mut:mechclass'),
 dict(name='B-rekeyed-lookup-off', file=B, old='[ -n "$pr" ] || pr=$(awk', new='[ -n "$pr" ] || pr=$(true || awk'),
 dict(name='B-rekeyed-numeric-guard', file=B, old=L, new='$1 == t { p = $3 }'),
 dict(name='B-rekeyed-first-not-last', file=B, old=L, new='$1 == t && $3 ~ /^[0-9]+$/ && p == "" { p = $3 }'),
 dict(name='B-rekey-call-off', file=B, old='[ -z "$pr" ] || rekey "$t" "$pr" >&2\n', new='[ -z "$pr" ] || true >&2\n'),
 dict(name='B-pr-numeric-off', file=B, old='--pr) numeric "${2:-}" || die', new='--pr) true "${2:-}" || die'),
 dict(name='B-pr-ignored', file=B, old='--pr) numeric "${2:-}" || die "dispatch-handoff: --pr takes a pull-request number"; pr=$2;', new='--pr) numeric "${2:-}" || die "dispatch-handoff: --pr takes a pull-request number";'),
]
relay = [
 dict(name='R-foldfailed-off', file=R, old='($4 == "fold-failed" || $4 == "push-failed")', new='($4 == "push-failed")'),
 dict(name='R-pushfailed-off', file=R, old='($4 == "fold-failed" || $4 == "push-failed")', new='($4 == "fold-failed")'),
 dict(name='R-first-epoch', file=R, old='"$bsha" "$fo" "$fe" "$fb" "$fh" "$fl"', new='"$bsha" "$fo" "$now" "$fb" "$fh" "$fl"'),
 dict(name='R-tip-unrecorded-foldfailed', file=R, old='fold-failed "$now" "$blob" "${htip:--}"', new='fold-failed "$now" "$blob" -'),
 dict(name='R-ttl-off', file=R, old='fold_memo_stands "$fo" "$fe" "$now" \\\n', new='true \\\n'),
 dict(name='R-blob-cmp-off', file=R, old='[ "$blob" = "$fb" ]; then  # mut:foldblob', new='true; then  # mut:foldblob'),
]
half = (len(bus)+1)//2
json.dump(bus[:half], open(out+'/bus1.json','w'), indent=1)
json.dump(bus[half:], open(out+'/bus2.json','w'), indent=1)
json.dump(relay, open(out+'/relay.json','w'), indent=1)
print(len(bus), len(relay))
