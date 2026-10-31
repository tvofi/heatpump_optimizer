Fix review: merge 12d32a204c923e768f6146a510445374c23f548c

bus-nonce: bba4c053f8e2fb8147cd7814c4796a78

Round 1. A record PR: it adds dev/programme/triage/s6-batch84.md and delivery/3030.md, and no production code, so the mutation, harness, claim-file and version steps have nothing to run.

## Findings

- The ruling's "unbuilt / dispatch next" is already overtaken. origin/handoff/r10-flow-body-only (cde451a79) carries d1cd320db "body_push: name the code head in a Code: trailer; the relay updates only with the body for its handoff" (2026-10-31 05:35Z). That is the P233 form, in body_push.sh and cloud_relay.sh. The live roster shows R10-FLOW-BODY-ONLY as stage in-progress, not "not-started". The record's facts are dated at 861f949ae, so they were true when read; its roster op (priority plus the fixture row and null) should be appended to that in-flight fix's brief, not issued as a dispatch-next. Carry: R10-FLOW-BODY-ONLY

## Evidence

- CI is GREEN at this head (merge_train.py classify, ev/classify.txt); the packet's gate digest is green. carry_audit prints 0 finding items.
- Merge with origin/main: git merge-tree --write-tree exits 0 (ev/merge-tree.txt), no conflicts.
- The body's figure: no "Code:" line in body_push.sh or cloud_relay.sh at 861f949ae reproduces (ev/grep-base.txt, no match). #2890, #2891 and #2894 appear under P233 in s6-batch46.md, added 2026-10-28. update_pr.sh's header says exit 75 is BUSY and the relay retries it on its next pass, which backs the deferred BUSY part.
- The timestamp variant is rejected for a sound reason (a re-bodied unchanged head is newer and correct; runner and host clocks differ); the Code: trailer identity needs no clock.
- The held op b84-P321.txt is not in the tree or on the roster branch, so I could not compare it. The ruling's text is internally consistent, and the roster op is the orchestrator's.
- Head 12d32a204c923e768f6146a510445374c23f548c is the head measured.
