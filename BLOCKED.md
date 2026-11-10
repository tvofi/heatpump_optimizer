BLOCKED: r10-process-slim-p2 at 6671786843048c52ea7c11373c1e074e4aa8f187 (body_push: REFUSED REVIEW-PACKET, hot-file #3366)

Question: #3366 holds an unboarded merge verdict and shares the hot file dev/audit/harnesses/r10_seat_selftests_mutants.py with this diff, so `review_packet.py handoff` refuses the body push. Board or merge #3366 first and re-run `bash tools/audit/seat/body_push.sh r10-process-slim-p2 BODY.md` from the body at handoff-wip/r10-process-slim-p2-body 4dcdbd21a66b10c2e403c8e587e7e293af0a4284, or rule otherwise?

Done in this seat:
- Code pushed: handoff/r10-process-slim-p2 0c12e36e..66717868, a merge of origin/main b8f67a775137a8032d5c71b34ea64165c1d4613a with the claimnotes and ledgermerge drivers installed; auto-merged, no hand edit.
- carry: the Forward-carry item now names R10-TRAIN-RESIDUE (not-started at handoff/audit-r10-roster 12dd95af; its brief owns the record-autofix beat deletion and its carries already hold this item). R10-CLOSEOUT-CLEANUP checked and does not own it. carry_audit check: 6 routed, 0 unrouted, 0 bad destination(s).
- ci predict at 66717868: "no closures, fast, governance or instrument red predicted against b8f67a775137".
- PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh with the body: rc=0 at 66717868.

body_push output (tail):
review_packet: REFUSE hot-file: #3366 holds an unboarded merge verdict and shares dev/audit/harnesses/r10_seat_selftests_mutants.py
review-packet handoff: R10-PROCESS-SLIM at 667178684304, 2 carries, 1 refused
body_push: the review packet refuses this head at the handoff (above); answer each, push the code, then the body
body_push: REFUSED REVIEW-PACKET
body_push: refused body kept at handoff-wip/r10-process-slim-p2-body 4dcdbd21a66b10c2e403c8e587e7e293af0a4284
