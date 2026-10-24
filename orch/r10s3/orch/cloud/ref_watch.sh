#!/bin/bash
# ref_watch.sh: every 2 min, list probe/* (non-rev) and handoff*/r10-* refs; log each new or moved ref once to owed.log as "REF-MOVED <ref> <sha>". State: refs.seen
cd "$(dirname "$0")"
R=/Users/timmalmstrom/heatpump_optimizer
snap(){ git -C $R ls-remote origin 'refs/heads/probe/*' 'refs/heads/handoff/r10-*' 'refs/heads/handoff-body/r10-*' | grep -v 'refs/heads/probe/rev-' | awk '{print $2" "$1}' | sort; }
[ -f refs.seen ] || snap > refs.seen
while true; do
  cur=$(snap) || { sleep 120; continue; }
  [ -n "$cur" ] && comm -13 refs.seen <(echo "$cur") | while read r s; do echo "$(date -u +%FT%TZ) REF-MOVED $r $s" >> owed.log; done
  [ -n "$cur" ] && echo "$cur" > refs.seen
  date -u +%FT%TZ > ref_watch.alive; sleep 120
done
