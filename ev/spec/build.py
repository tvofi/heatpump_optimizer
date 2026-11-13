import json, sys, os
root = sys.argv[1]; out = sys.argv[2]
bus = "tools/audit/seat/bus.sh"; rel = "tools/audit/seat/cloud_relay.sh"
ML = 'MECHANICAL_CLASSES=" ci-red ci-wait ci-pending ci-cancelled red-unanswered root-cause-unanswered body contract preflight-mismatch conflict head-moved carry-missing carry ungated "'
classes = ML.split('"')[1].split()
B = []
for c in classes:
    rest = [x for x in classes if x != c]
    B.append(dict(name=f"B-drop-{c}", file=bus, old=ML, new='MECHANICAL_CLASSES=" ' + " ".join(rest) + ' "'))
B.append(dict(name="B-add-harness", file=bus, old=ML, new=ML[:-1] + 'harness "'))
B += [
 dict(name="B-exempt-off", file=bus, old='mechanical_block "$1" && return 0  # mut:mechclass', new='false && return 0  # mut:mechclass'),
 dict(name="B-rekeyed-lookup-off", file=bus, old='[ -n "$pr" ] || pr=$(awk', new='[ -n "$pr" ] || pr=$(true || awk'),
 dict(name="B-rekeyed-numeric-guard", file=bus, old="$1 == t && $3 ~ /^[0-9]+$/ { p = $3 }", new="$1 == t { p = $3 }"),
 dict(name="B-rekeyed-first-not-last", file=bus, old="$1 == t && $3 ~ /^[0-9]+$/ { p = $3 }", new='$1 == t && $3 ~ /^[0-9]+$/ && p == "" { p = $3 }'),
 dict(name="B-rekey-call-off", file=bus, old='[ -z "$pr" ] || rekey "$t" "$pr" >&2 ||', new='[ -z "$pr" ] || true >&2 ||'),
 dict(name="B-rekey-fail-ignored", file=bus, old='rekey "$t" "$pr" >&2 || die "dispatch-handoff: recorded, but could not re-key', new='rekey "$t" "$pr" >&2 || true "dispatch-handoff: recorded, but could not re-key'),
 dict(name="B-pr-numeric-off", file=bus, old='--pr) numeric "${2:-}" || die', new='--pr) true "${2:-}" || die'),
 dict(name="B-pr-ignored", file=bus, old='--pr) numeric "${2:-}" || die "dispatch-handoff: --pr takes a pull-request number"; pr=$2;', new='--pr) numeric "${2:-}" || die "dispatch-handoff: --pr takes a pull-request number";'),
]
R = [
 dict(name="R-oldformat-guard-off", file=rel, old='[ "${#mb}" = 40 ] || [ "$mb" = - ] || mo=', new='true || mo='),
 dict(name="R-oldformat-dash-off", file=rel, old='[ "${#mb}" = 40 ] || [ "$mb" = - ] || mo=', new='[ "${#mb}" = 40 ] || mo='),
 dict(name="R-tip-cmp-off", file=rel, old='$7 == h { print; exit }', new='1 { print; exit }'),
 dict(name="R-blob-cmp-off", file=rel, old='[ "$blob" = "$fb" ]; then  # mut:foldblob', new='true; then  # mut:foldblob'),
 dict(name="R-ttl-off", file=rel, old='fold_memo_stands "$fo" "$fe" "$now" && [ "${#fb}" = 40 ]', new='[ "${#fb}" = 40 ]'),
 dict(name="R-fb-len-off", file=rel, old='&& [ "${#fb}" = 40 ] \\', new='\\'),
 dict(name="R-foldfailed-off", file=rel, old='($4 == "fold-failed" || $4 == "push-failed")', new='($4 == "push-failed")'),
 dict(name="R-pushfailed-off", file=rel, old='($4 == "fold-failed" || $4 == "push-failed")', new='($4 == "fold-failed")'),
 dict(name="R-first-epoch", file=rel, old='"$bsha" "$fo" "$fe" "$fb" "$fh" "$fl"', new='"$bsha" "$fo" "$now" "$fb" "$fh" "$fl"'),
 dict(name="R-blob-unrecorded", file=rel, old='blob=$(git rev-parse "$bsha:BODY.md" 2>/dev/null || echo -)', new='blob=-'),
 dict(name="R-tip-unrecorded-foldfailed", file=rel, old='fold-failed "$now" "$blob" "${htip:--}"', new='fold-failed "$now" "$blob" -'),
 dict(name="R-tip-unrecorded-pushfailed", file=rel, old='push-failed "$now" "$blob" "${htip:--}"', new='push-failed "$now" "$blob" -'),
 dict(name="R-owed-line-dropped", file=rel, old='"$sha" "$bsha" "$fo" "$fe" "$fb" "$fh" "$fl"; continue', new='"$sha" "$bsha" "$fo" "$fe" "$fb" "$fh"; continue'),
]
bad = 0
for m in B + R:
    n = open(os.path.join(root, m["file"])).read().count(m["old"])
    if n != 1: print("NOT-UNIQUE", m["name"], n); bad += 1
json.dump(B, open(out + "/bus.json", "w"), indent=1); json.dump(R, open(out + "/relay.json", "w"), indent=1)
print(len(B), "bus", len(R), "relay", "bad", bad)
