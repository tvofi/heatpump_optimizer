Part 1 (carries 0-4) of r10-gate-defer-barrier is built, prepr.sh clean at ba47446a8722acf4055b62883cf32e8e5d7d1c59 (code pushed to handoff/r10-gate-defer-barrier). body_push.sh refuses the one remaining item, which this seat cannot clear:

review_packet: REFUSE hot-file: #3471 holds an unboarded merge verdict and shares tools/audit/seat/orchestrator_tick.py

Question: it clears only when #3471's merge verdict boards the train, goes stale, or the PR closes (review_packet.py hot_file_refusals); the cloud seat has no HPO_BUS_TRAIN_STATE, so every verdict reads unboarded. Re-run `bash tools/audit/seat/body_push.sh r10-gate-defer-barrier <body>` once #3471 has boarded or merged; the body is kept at handoff-wip/r10-gate-defer-barrier-body (a brief-carries answer for carries 2 and 5-8 is already in it, no other refusal remains). Carry 0's RCA 5.2 destination R10-HOTFIX-GATE-REDISPATCH-LOOP is carries-open and not receivable, so it is recorded as dismissed with the reason.
