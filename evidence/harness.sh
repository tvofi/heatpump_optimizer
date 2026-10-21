# finder harness (jq over the roster JSON, as the body names); run from repo root
# usage: harness.sh <base-sha> <head-sha>
F=dev/programme/rosters/wave-r10-groups.json
for r in "$1" "$2"; do git show $r:$F > /tmp/g.$r.json
 echo "RESULT $r groups=$(jq '.groups|length' /tmp/g.$r.json) done=$(jq '[.groups[]|select(.resume.stage=="done")]|length' /tmp/g.$r.json) carries=$(jq '[.groups[].carry|length]|add' /tmp/g.$r.json)"; done
