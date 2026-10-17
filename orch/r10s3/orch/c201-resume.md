Orchestrator resumed (session 3, 2026-10-17 ~20:45Z) at origin/main `633f37487`; nothing was running (no train, tick, beat or sync loop).

Done this turn:
- Merged #2355 (record autofix rows; `record_row.py --automerge-check` OK at its head).
- Opened #2356 (roster): eighteen merged groups' `resume.stage` set to the canonical `done`. `roster_lib.DONE_STAGES` is (`done`, `rca-done`); the stage strings `done: merged #N` kept every after-edge to a merged group reading blocked, so the tick's PLAN printed 56 of 56 open.
- Main checkout had a stale local commit (its roster carry already on main) and a reversed index; backed up to local branch `backup/main-stray-ae958c48a`, reset to origin/main.
- Restarted: `state_docs.py beat --push` (detached), `wt_sync.sh` loop (detached), tick watcher seat.

Seats dispatched: R10-VENT-DETECTOR fixer (unblocked by #2347), R10-I5-DOCS fixer, R10-ARCHSCORE-COVERAGE p4/p5 fixer, R10-REF-PRIVACY remainder (tracked-file scrub + bus evidence-path arm; leaves #2310 open until both land), #2345 R10-DEEPLINK-CENSUS resume fixer, #2351 N-log-flood resume fixer, a reconciliation survey (issue closures owed, the five `[policy] recurring friction` issues, stranded refs, stamp readiness), a critical-path replan seat (edge classification semantic vs file-overlap), and a judge seat for the held R10-PUMP-MODEL D2-s2-01 ruling (comment 6228455340); the ruling follows its recommendation under mandate 6175172275.
- R10-PUMP-MODEL primary PR (D7-arch3-04 + slot-floor, `handoff/r10-pump-model` `c4304bb1f`) opening now via `open_pr.sh`; D2-s2-01 stays held on `handoff/r10-pump-model-d2`.

Stamp: none since v7.0.0 with eight `custom_components/` groups merged; owed once main is green and the notes section exists (survey reports what stamp.py needs).

Leaves #201 open.
