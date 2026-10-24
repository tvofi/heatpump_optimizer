#!/bin/bash
# Every 300 s: report HANDOFF-MOVED when a handoff-body ref tip leaves its baseline. Writes to coord-loop.log.
D=/Users/timmalmstrom/hpo-orch/r10s4
R=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt
LOG=$D/coord-loop.log
DONE=$D/handoff-watch.done
touch "$DONE"
cd "$R" || exit 1
WATCH="handoff:r10-advisor cd1c837cabe9536b27a7d36d193d5f4e24d23deb
r10-row-only-update f89539226af3659054ebf49a39c9131a78881c49
r10-prepr-closures a7c5383beada6eda41ea444f9b8c39738fae9185
body:r10-verdict-item-barrier b2a1f10d13c58d39cdb690108296a7daa1696cf3
handoff:r10-verdict-item-barrier 821507dca0f1e238cb832d265946b4590504d6f2
body:r10-ci-ratchet-window none
handoff:r10-ci-ratchet-window none
body:r10-pusher-reap 26d5453353bb2b9cd5e7b56573a89b8265ef47cf
handoff:r10-pusher-reap 6ff10e62b3f7b8d38fd3ecab5e23aa71a9f3553d
body:r10-flow-dispatch none
handoff:r10-flow-dispatch none
body:r10-flow-body-patch none
handoff:r10-flow-body-patch 18e7a7c61f2b07691d4d00f49d6a8658eb16d7d6
body:r10-ci-layout-p1 ef5c94f38a08b998659b4b7217b6f961e5693765
handoff:r10-ci-layout-p1 1b4fae9df4762f0d70949c7e5d9f2db78ff92c28
body:r10-flow-yield-probe 14f9d6ab47f9913af9c506d74b55ef66d2fd354b
handoff:r10-flow-yield-probe 7864970031c4c9a24b077a6ccd01fdf02ba192a0
body:r10-flow-relay-hold dd295d08f0f027151de6c7415032b7a274b4c302
handoff:r10-flow-relay-hold cfa89d24f597fbc2d93de1f77f5b57d8e4a8144d
handoff:r10-flow-main-gate 14ce015949c34a34586eae8b570b4d5cebbf6da6
body:r10-flow-main-gate 034148a83a1c4f746f4e0068405bef44c1952fe6
body:r10-flow-andon 1ef4dbd0
body:r10-row-only-update e5e81f0bd3e4edd6ecda5a0f6c17dbce4aaac113
body:r10-night-folds cc6c2db945a43d580fe9e1c2174a595b8c14fc2f
body:r10-pusher-reap c65695a36c2475de8bd620d140cb249a401ead39
body:audit-r10-roster 170a325bd3af47a19863b313bea4425d00e75953
handoff:audit-r10-roster 23ef06dc6cc719917e593174b3a12977cd054071
body:mrbatch none
handoff:r10-flow-design-policy none
body:r10-flow-design-policy none"
while [ ! -f "$D/coord-loop.stop" ]; do
  echo "$WATCH" | while read br base; do
    [ -z "$br" ] && continue
    ref=$br; case "$br" in ref:*) ref="${br#ref:}";; body:*) ref="handoff-body/${br#body:}";; handoff:*) ref="handoff/${br#handoff:}";; *) ref="handoff-body/$br";; esac
    tip=$(git ls-remote origin "refs/heads/$ref" 2>/dev/null | cut -f1)
    [ -z "$tip" ] && tip=none
    if [ "$tip" != "$base" ]; then
      grep -q "^moved $br $tip" "$DONE" || { echo "$(date -u +%H:%M:%SZ) HANDOFF-MOVED $ref from ${base:0:8} to ${tip:0:8}" >> "$LOG"; echo "moved $br $tip" >> "$DONE"; }
    fi
  done
  sleep 300
done
