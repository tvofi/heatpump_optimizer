Fix review: merge 818dd661837adc81a1a077c4c455b9d833159386

bus-nonce: ad08287f456b671ca98cbfea2d09afeb

## Findings

none

## Evidence

- RESULT: head measured 818dd661837adc81a1a077c4c455b9d833159386; diff is two files, dev/programme/triage/s6-batch73.md (71 lines) and dev/programme/delivery/3003.md (its own row). No production code, no claim file, no VERSION/manifest/notes touch, no roster op.
- RESULT: `roster_edit.ruling_verdict` reads P307 as DEFER at this head (the body's mutation proof reproduced). Only one ruling heading (P307) in the file.
- RESULT: merge-tree against origin/main is clean (ev/merge-tree.txt, rc 0).
- RESULT: review_packet: carry_audit 0 finding items; figure_lint 2 resolved, 0 refused; no refusals or advisories.
- Source citations re-derived at origin/main cf4f6b7a6: merge_train.py is 6703 lines; the docstring at 101-105 gives the nightly record-beat reason and names #2291/#2295/#2299/#2302; `hold_refresh` line 2125, the `TRAIN HOLD ... the record beat waits` log line 2169, `hold_idx` line 4393, the `TRAIN HOLD released` assertion line 4414; the P191 "merged under the batch" path at line 2031 and the "critical path: the record sweep waits" log at line 1809 exist. P289 is in s6-batch61.md, P305 and the six set-stage flips are in s6-batch71.md, R10-TRAIN-OVERLAP-GRADE has carry 20 in the roster and R10-FLY-TRAIN-DEFAULTS exists (s6-batch57.md).
- Figures I could not re-derive: the 601 TRAIN HOLD refs, 62 released, 110 BATCH, 8 BOT MERGED, 15 pending skips and the 0 counts come from the orchestrator's out-of-tree merge_train/train.log (3732 lines); no train.log is in the tree or on this host. The ruling and body both state that origin and the date range, and the ruling rests its DEFER on the missing benefit evidence and the code's hold design, not on those counts alone. The 2.25 h mean and the absent 7.06 h figure rest on the out-of-tree regain-24h scratch likewise. These are stated sourced, unverified by me.
- CI at read time (16:5x UTC): the check-runs API lists 7 runs on this head, prelude/refresh/cancel-superseded queued, arm skipped, none red; no gate conclusion existed yet. Body states no red checks, so no root-cause answer is owed. The train gates on CI at the head.
- Contract: body carries Head, Mutation proof, Null control, Figures, Red checks, Forward-carry (none), Friction sections; head SHA in the body matches (818dd66 adds only the delivery row to authored head b05e4b7).
