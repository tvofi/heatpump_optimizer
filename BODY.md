Part 2 of R10-RELAY-SWEEP (part of #201). Re-measured every carry against origin/main 5bc009bc8: eight of nine are already landed with self-test rows (part 1, #3252, and earlier); the one open item is a guide gap, closed here. No production code changed.

## Head

f5e680bf3b7ae76e711a9f8a68d3914739b176ec (code head; doc-only diff over origin/main 5bc009bc8, measured 2026-11-08T05:38:33Z).

## Mutation proof

n/a: the diff is one paragraph in tools/audit/seat/instruments/tick_loop.sh.md; no production line was added. The dispositioned carries are pinned by existing rows: carry 4's M2/M5 by the two-REFUSE-line stub and the stderr-replay row in cloud_relay.sh --self-test; carry 5 by the tick_loop.sh --self-test row "a TERM to the loop's process group leaves the in-flight relay to write its rc" (RELAY_HOLDER calls os.setpgid(0, 0)).

## Null control

The unmodified tree (origin/main) already passes each pinned row; this diff touches no script. Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed MODE: SCOPED -- 0 script(s) run.

## Figures

none

Dispositions (each verified in the tree at 5bc009bc8):
- Carry 0 (the packet's Carry 1): exit 75 / body-sha keying (handoff_arm key and urc=75 branch), level before the serial loop (handoff_level), body-only level (body_only_owed) all present. bus.sh orphans uses `${arms[@]+"${arms[@]}"}`, so the bash 3.2 empty-array crash is closed, and bare_array.py runs in CI. Process-group sharing: see carry 5. Auto-open dropped per the carry.
- Carry 1: the body-only path is still the function handoff_arm calls; the handoff-body ref's disposition is the ledger.py level fold (handoff-no-pr) plus the registered kinds handoff-body-unapplied and handoff-body-stale. Nothing further owed.
- Carry 2: probe_arm and handoff_arm publish levels before the serial loops; self-test rows with a blocked update stub; orchestrator_tick.py relay_owed prints the GAP line when no .level exists, with positive and null rows.
- Carry 3: body_only_owed prints once per pass; rows including the older-body null control; kind registered in ledger.py.
- Carry 4: M2 and M5 rows exist (two REFUSE lines expecting the second; update output replayed to stderr). Guides: cloud_relay.sh.md documents handoff-update with why, cloud-handoff-failed.why, Code:, handoff-body-stale; body_push.sh.md documents the Code: trailer.
- Carry 5: RELAY_HOLDER is setpgid(0, 0) with the TERM-to-group self-test row. Open piece closed here: tick_loop.sh.md did not say so; it now does.
- Carry 6: delivered guard, per-pass state-dir line, pipefail-safe rows and the R10-RELAY-REPLAY note (dev/audit/rca/) exist. dev/audit/config/bugclasses.json has no class this note fits, so no rca entry is cited (the carry says "if the class exists").
- Carry 7: HELD-BODY with planted and null rows exists; handoff-hold-stale reports hold lines whose PR is no longer open (merged or closed).
- Carry 8 (the packet's Carry 9, 1-based): ev_case_collision in relay(), case_collision in bus.sh push_verdict and its read side, rows with null controls, and fix-review.md's "Evidence names differ beyond case" all exist.

## Red checks

none

## Forward-carry

none

## Friction

none

## Unpinned sites

none: no added code line.
