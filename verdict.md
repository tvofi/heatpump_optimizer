Fix review: merge 4da469164e865be71478ac1221fbd8aabf0f65db

bus-nonce: 10cda583714b1c6cbcce9a8cf0a62f13

## Round

This is re-review round 3. Round 1 blocked 6e12aeb5 on `harness: class-open`, and round 2 blocked 2124bc75 on `carry-stale`. I measured head 4da469164e865be71478ac1221fbd8aabf0f65db, which was the PR head when I wrote this verdict. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so I followed the contract as it stands on main. The merge base is origin/main 46e368127. I worked from a detached worktree at the head. My harness was the round-2 reviewer's `evidence/replay.py`, taken from origin/review/2545, not the fixer's.

## Block

None. The round-2 `carry-stale` block is cleared at this head:
- §1 now dates the cause to `1ebc737e7` ("As main stood at `1ebc737e7` ... keyed each row on `f[2]`"). It also records that `b38c6431a` (#2547, merged by 295c874e8, an ancestor of the merge base) keys every log event on its PR and makes the levels a rewritten `<log>.level`.
- §5.1 keeps only the level's live-world closers.
- §7 says "nothing is carried for" the three one-shot kinds.
- The register entry `_rca.N-orphaned-handoff` now has `landed` "b38c6431 (#2547): event keying and the level file". Its `countermeasure` is "barrier, in part landed: b38c6431a keys every relay OWED event on its PR, the one-shots included ...". `parts_missing` names only the level closers, the content-covered close, and the ledger parts.
- The body's old third forward-carry ("Key each event on its PR") is gone. Nothing in the record, the register or the body still calls `handoff-update`, `approve-held-runs` or `dispatch` owed. Its only forward-carry on the relay grammar now asks the ledger to keep the landed grammar, and gives a control that moves.

The round-2 harness finding is cleared too. The harness now stops at `self_test()`, so the line-376 fixture is no longer read as a writer. It also classifies each row by what the tick under test does with it.

## Findings

- The finding's original instrument, the round-2 reviewer's `replay.py`, lives only on `origin/review/2545`, out of tree. I reused it as the finder's harness and built nothing of my own. The PR's committed harness `dev/audit/harnesses/r10_relay_owed_class_reach.py` agrees with it at 1ebc737e7, at the merge base, at the head and under P1, so the class has a committed instrument. Carry: dismissed: disclosure only; the committed round harness agrees with the out-of-tree replay at every end and under perturbation

## Evidence

- Finder's harness (`replay.py`, ev/finder_replay.txt, ev/harness_runs.txt):
  - `RESULT tick=tick_1ebc737e7.py uncleared_after_POSTED=8`, over kinds approve-held-runs, dispatch, handoff-no-pr, handoff-update and probe-ref.
  - `RESULT tick=tick_46e368127.py uncleared_after_POSTED=0` (merge base).
  - `RESULT tick=tick_4da469164e865be71478ac1221fbd8aabf0f65db.py uncleared_after_POSTED=0` (head).
  - Under P1, the head's tick with `pr = f[2] if len(f) > 2 else None`: `uncleared_after_POSTED=8`. This matches the body ("8 at 1ebc737e7, 0 at this head and 8 under P1").
  - The tick and the relay are byte-identical between the merge base and the head (`cmp`), so the PR changes no production line.
- The PR's harness, re-derived by me at both ends (ev/harness_runs.txt):
  - 1ebc737e7: `RESULT writers=10 events=8 events_cleared=4 events_uncleared=4 events_unreported=0 level_writers=2 level_lines=4 level_items=2`. This matches the body.
  - Head: `RESULT writers=10 events=8 events_cleared=8 events_uncleared=0 events_unreported=0 level_writers=2 level_lines=2 level_items=2`. This matches the body.
- Null controls and perturbations, re-derived (ev/harness_runs.txt):
  - Same run at 1ebc737e7: the 4 PR-keyed writers are cleared beside the 4 uncleared ones.
  - P1 (event keying reverted): `events_uncleared=4`, against 0 unmodified.
  - P2 (`level_set`'s `awk -v k="$1" '$3 != k' "$lv"` replaced with `cat "$lv"`): `level_lines=4 level_items=2`, against 2/2.
  - P3 (the head's tick over 1ebc737e7's relay): `events_cleared=8 events_uncleared=0`.
  - P4 (1ebc737e7's tick over the head's relay): `events_uncleared=4`.
  - All of these match the body. The harness moves under each of its own perturbations.
  - Two of my figures are not in the body, which quotes neither: both mixed runs print `level_lines=0`, because the tick and the relay disagree on where the level lives.
- Old harness (from 2124bc75b) at 1ebc737e7, the merge base and the head (ev/old_harness.txt): `writers=10 kinds_on_kind_token=5 uncleared_lines=8`, then `writers=9 kinds_on_kind_token=4 uncleared_lines=0` at both later commits. This matches the body.
- Class rule: outside `dev/audit/harnesses/`, only `cloud_relay.sh` and `orchestrator_tick.py` read the relay log, both at the head and at 1ebc737e7 (ev/relay_log_readers.txt, ev/landed_and_readers.txt). The harness lists all 10 writers at the head, and each one is dispositioned in the body's `## Figures`. Nothing is left open.
- The record against `defect-root-cause.md` and `root-cause.md`:
  - The named cause is §1, three causes, dated.
  - The process state is §3, (c), with the residuals (a) and (d) stated separately.
  - The cost test is §4: 1.65–2.4 h per round against 5.13 h × 1.0. The 5.13 h is labelled "quoted, not verified". The arithmetic re-derives: 5 s × 12/h × 144 h = 2.4 h, and 5 s × 8.25/h × 144 h = 1.65 h.
  - The countermeasure is §5, with the still-owed parts routed in §7.
- Not re-derived (step 8), because they come from the orchestrator's host logs, which are not in the tree:
  - The live-host figures in §2 and §2a: 31,303 lines, 236 refs, 143 passes, ages of 41.9–96.6 h, and 198 passes in 24 h.
  - The 4,073,591-byte board.
  - fold_demo's 22/15/11.
- Register: `fold_ledger.py check` gives 113 rca entries and 0 violations at the merge base 46e368127, and 114 and 0 at the head (ev/fold_ledger_base.txt, ev/fold_ledger_head.txt). This matches the body.
- Carry routing: `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <PR body>` prints `CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit_body.txt).
- Roster at origin/handoff/audit-r10-roster 743463c61f6af0631f7ac20ca36561232b028b97 (ev/roster_states.txt):
  - R10-ORCH-MACHINERY and R10-FLY-ORPHANS-REWRITTEN are not-started. Every carry in the body and the record names one of them, and both are live.
  - R10-RCA-HANDOFF-SLIP is in-progress.
  - R10-TICK-OWED-LEVEL and R10-ROSTER-OPS are done. Neither is a destination of any carry. The record mentions them only as history: the landed fix, and "re-carried from R10-ROSTER-OPS by #2554".
  - R10-FLY-ORPHANS-REWRITTEN's brief does carry both halves that §7 assigns it: "cloud_relay.sh classifies handoff-no-pr from its own rules; it uses bus.sh orphans' classifier instead", and the M arm that "requires a byte-identical blob".
  - R10-ORCH-MACHINERY's carry holds `From #2545 (item 3985dac8)` and the #2554 brief-pin item, which has its control.
  - My verdict's one Carry is dismissed, so it routes nowhere.
- Mutation proof: n/a, as the body says. The diff is a record, a register entry, a round harness, one `inert_reads` line in tests/closures.json, and the PR's delivery row.
- Step 14, the closures.json line: it sits under `inert_reads["tests/harness_headers.py"]`. That is a recording of what harness_headers reads, earned by the new harness file, which harness_headers opens. Its prefix `dev/audit/` is already in `INERT`. Deleting the line leaves `tests/entities.py` at `ALL 2382 ENTITY CHECKS PASSED`, as it is unmodified (ev/inert_mutant.txt, python3.13 venv). So no gate refuses its absence. It only records what is actually read, and nothing moves that the change did not earn. `tests/harness_headers.py` at the head prints `ALL 109 HARNESS HEADER CHECKS PASSED` (ev/harness_headers.txt).
- VERSION, the manifest version and RELEASE_NOTES.md are untouched, checked three-dot from the merge base (ev/version_untouched.txt).
- Merge: `git merge-tree --write-tree origin/main(46e3681276f99e8d3e4d12e9d316a46946f666d7) 4da469164e865be71478ac1221fbd8aabf0f65db` gives `ce8521761c9ba7a52d72d9a27f9ca717858baca8`, rc=0. It is clean, and origin/main is the merge base, so no absorb is needed (ev/merge_tree.txt).
- Gate selection: `closure.py select --diff 46e368127` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` (ev/gate_select.txt). This matches the body. I did not run the gate itself; per step 11 I cite CI for it.
- Head SHA: the body's `## Head` names 4da469164e865be71478ac1221fbd8aabf0f65db, the head I measured.
- Red checks, read from the check-runs API per commit, `repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs` (ev/check_runs.txt, ev/check_runs_head.txt):
  - At this head every workflow had concluded by 01:44Z. The only red is `nightly-status` (119576285158, failure). It grades main's scheduled run, and this diff reaches nothing it reads, so it is not this PR's red (step 11, `defect-root-cause.md`). This is not a required check of this PR and does not block. Main's ci-ratchet variance belongs to R10-CI-LAYOUT.
  - Every other check at the head succeeded or was skipped, including both `pr-contract` runs, `closures` (119580653722) and `Analyze (python)`.
  - The authored commits 6a70a8f49 and 0acc2fbc1 carry no check runs.
  - The earlier reds in the range are the `pr-contract` carry-step reds at 81514b55c, 2cd325bc2 and 6e12aeb5b. The body's `## Red checks` names them and answers them with a cheaper detector (`carry_audit.py --roster-ref origin/main check`, seconds). The cancelled runs at 81514b55c were superseded and are not reds.
- Re-read before return: `pulls/2545 .head.sha` was still 4da469164e865be71478ac1221fbd8aabf0f65db at 01:44Z, after CI concluded, so the head did not move under this review.
