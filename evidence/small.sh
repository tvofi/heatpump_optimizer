#!/bin/bash
# reviewer-built: stamp_paths over a 13-line notes diff (heading first), N calls
set -uo pipefail
. "$1"; N=$2
NOTES=$(printf '+## v9.9.9\n'; for i in $(seq 1 12); do printf '+- line %s of the notes\n' $i; done)
m=0
for i in $(seq 1 $N); do
  case "$(stamp_paths "" "" "$NOTES")" in *'RELEASE_NOTES.md(heading)'*) ;; *) m=$((m+1));; esac
done
echo "RESULT small impl=$(basename $1) lines=$(printf '%s\n' "$NOTES"|wc -l|tr -d ' ') calls=$N missed=$m load=$(sysctl -n vm.loadavg)"
