Fix review: blocked 361be3cd6cdc6a594b542956403220efdd4f0803 mutation-vacuous: the two apply_plan projection calls the round-2 fix threads legacy into survive with legacy dropped (A4 dry-run, A5 write-path), and A5 writes a done group holding a STRANDED carry

bus-nonce: dfbbba6651d19d2403cc6d3abb6a7bf2

Round: 2 (a delta repair over round 1's 598ed188f, not a re-cut).
Measured head: 361be3cd6cdc6a594b542956403220efdd4f0803, a fast-forward over 598ed188f. Branch-only code: f2d9ae537 (the tests) and 784f8391b (the apply_plan fix). The rest is merges of origin/main 8fec54ee2. Contract: dev/governance/roles/fix-review.md at origin/main. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty. I judged from detached worktrees at the head. Head re-read before return: origin/fix/r10-roster-schema-pr = 361be3cd6cdc6a594b542956403220efdd4f0803 (ev/head-reread.txt).

## Block

784f8391b says it threads the cut-over set to "all three apply_plan calls (both projections and the write)". Only the write call is pinned. My own plants are in ev/mut2.py. Each is one exact single-occurrence replacement in its own detached worktree at the head, run through the file's own `--self-test` under `env -u BASH_ENV python3 -I` and then restored clean (ev/mutants-r2b.txt):

- A5 roster_sync.sync write path: the re-derive projection `apply_plan(projected, changes, [], legacy)` becomes `apply_plan(projected, changes, [])`. Result: rc=0, `roster_sync self-test: 82 checks, 0 failed`. SURVIVED.
- A4 roster_sync.sync dry run: the first projection `apply_plan(projected, changes, [], legacy)` becomes `apply_plan(projected, changes, [])`. Result: rc=0, 82/0. SURVIVED.

A4 and A5 are not equivalent mutants. ev/projection_probe.py (my own probe, output in ev/projection-probe.txt) runs one pass that merges R9-LEG, whose only carry is legacy, and R9-OTH, whose body routes `Carry: R9-LEG`:
- At the head, the projection makes R9-LEG `done`, so the carry is refused ("the destination is done") and R9-LEG is written `done` with `stranded=[]`.
- Under A4/A5, R9-LEG projects `carries-open`, so the carry is appended. The write path then writes R9-LEG `done` holding that post-cut-over carry: `stranded=[('R9-LEG', 'done', 1, ...)]`.

So the projection's legacy set decides whether a same-pass `Carry:` lands on a group this pass closes. That is the defect class this group exists to stop, and it is unpinned. Under A4, the dry run prints acceptance where the head prints the refusal.

Repair owed: one sync()-level check per projection, each with its null. Drive one pass that merges a legacy-only group and another PR whose body carries `Carry: <that group>`. Require the carry to be refused, nothing appended, and the group written `done` with no stranded carry, in both the `--apply` write and the dry-run print. The null is the same pass with the destination holding a post-cut-over pending carry: it projects carries-open, the carry appends, and the group is written carries-open. Then re-run A4 and A5 and require a kill.

## Findings

- Block repair: the A4/A5 projection pins and their nulls above. Carry: R10-ORCH-ROSTER-SCHEMA
- The body's prepr figure is not at this head. `## Figures` gives `PRE-PR: 784f8391b... rc=0` with the `closures` step skipped to CI on darwin. The brief asks for a full prepr rc=0 at this head; the body states neither "full" nor this head (361be3cd6 adds the main merge 8fec54ee2). I did not re-run prepr. Owed at the next head: the body names prepr at the head it hands off. Carry: R10-ORCH-ROSTER-SCHEMA
- Round-1 findings are routed in the body, not yet on the roster, and none is claimed fixed. They are the closing_stage rewrites only `done` finding (rca-done/absorbed, stated honestly, exposure zero), the mark-shaped append, the exact-text legacy match, and the committed replay harness. Each carries R10-ORCH-ROSTER-SCHEMA; the 19-STRANDED item and the row-viii policy question carry R10-ORCH-LEDGER; M9 carries #2505. At roster tip a18ac4404, both destinations are `carries-open` and so can receive. roster_sync appends a body's `Carry: <GROUP>` at the merge transition, so these are owed after the merge. Carry: R10-ORCH-LEDGER

## Evidence

- The five round-1 plants, re-run with the round-1 reviewer's anchors (ev/mut2.py, reworked to give each plant its own worktree; ev/mutants-r2.txt). All are KILLED now:
  - X1 (write-path re-derive without legacy): rc=1, roster_sync 82/1, `FAIL sync --apply writes done over a group whose only carry is legacy`.
  - X2 (sync's unreadable cut-over swallowed): rc=1, 82/2, `FAIL an unreadable cut-over refuses sync --apply rc 2, naming it` and `FAIL and the unreadable cut-over wrote nothing`.
  - X6 (roster_edit's swallowed): rc=1, roster_edit 153/2, set-stage and set-resume.
  - X7 (moved to a closed group): rc=1, 153/5.
  - X8 (`]` value): rc=1, 153/2.
  These match the body.
- Each kill has its null, read in the same unplanted self-tests at the head (ev/self-tests.txt): roster_lib 60/0, roster_edit 153/0, roster_sync 82/0, r10_roster_ops_mutants 180/0, carry_audit 214/0. The named nulls are all present and green: `mark-carry moved to an open group lands (null control)`, `mark-carry with a plain value lands (null control)`, `a legacy carry alone leaves set-stage done as done`, `sync --apply writes done over a group whose only carry is legacy`, and `with no cut-over the same carry is pending and sync --apply writes carries-open (null control)`.
- X7's rca-done and absorbed arms failed under X7 partly by cascade: the done arm's successful move marks carry[3], and the next arms then read "already marked". Plant A6 (`if stage == 'done':`, only done refused) is KILLED independently: rc=1, 153/4, `FAIL mark-carry refuses moved to a rca-done group` (ev/mutants-r2b.txt). The per-stage pin holds.
- The apply_plan fix (the brief's ask). Omitting legacy in apply_plan itself is killed three ways, each failing `sync --apply writes done over a group whose only carry is legacy`, with the written stage carries-open while the dry run printed done:
  - A1: op_set_stage called inside apply_plan without legacy.
  - A2: the write call `apply_plan(roster, changes, appends)`.
  - A3: the legacy parameter overwritten to None inside apply_plan.
  The projections are the block above.
- sync() through apply_plan over a group with a post-cut-over pending carry, with a readable cut-over: my probe adds a third case to the head's own fixture (ev/probe-post-cutover.diff, reverted after). It writes `R9-LEG: stage in-progress -> carries-open ... (1 pending carries)`, rc 0, written stage carries-open (ev/probe-post-cutover.txt). The legacy-only case writes `done`, so the printed and written stages agree on both sides.
- Replay (the round-1 reviewer's ev/replay.py; ev/replay2.py differs only in the worktree path, a range ended at the round-1 roster tip ce4a2386, and each roster_sync flip also taken through `apply_plan(..., legacy)`): output ev/replay-r2.txt.
  - `legacy at cut-over: 498 carries over 206 groups`.
  - `done-flips today: 21; would now be carries-open: 6`. The per-flip outcomes are identical to round 1's q1-replay.txt (`diff` empty), so the 15 zero-pending flips stay done and the 6 pending-carry flips stay carries-open.
  - The two slips, #3016 R10-WOOD-NOTIFY (a3553d6d5) and the 15:53Z R10-ORCH-ROSTER-SCHEMA close (52aea59b1), are written carries-open, not done. On all 10 derive-replayed sync flips, the derived stage equals the written stage (`AGREE=True` 10, `AGREE=False` 0).
  - The brief asks that the two slips "must now NOT write carries-open" and also that the 6 pending-carry flips "stay carries-open". The two slips are among those 6, so I read the first clause as "must not write done". At this head they write carries-open, which is the correct outcome for a done over post-cut-over pending carries.
- Cut-over constant: a4c9fa3d629017fb1a0e5394bbae79cdbdfa4f9b is an ancestor of origin/handoff/audit-r10-roster a18ac4404. At it, 206 closed groups hold 498 carries.
- `git merge-tree --write-tree origin/main 361be3cd6` (origin/main 8fec54ee2) exits 0, tree aa1b25593, no MERGE-CLAIM line (ev/merge-tree.txt).
- Claim files tests/golden/claimed_drift.txt and card_claimed_drift.txt are byte-identical to origin/main. VERSION, the manifest and RELEASE_NOTES.md are untouched.
- The delivery row dev/programme/delivery/3054.md is in the three-dot diff (`**open**`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `tests/closure.py select --diff <merge-base>`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, RUN tests/entities.py (ev/structure-scope.txt).
- CI on this head: `merge_train.py classify 361be3cd6...` was polled from about 02:13Z, at least 60 s apart, and still reads rc=3 `WAIT ... pending: gate red: none` at 02:20:54Z (ev/ci-classify.txt). The head's check runs at about 02:20Z show no failure. tests/coverage, tests/closures, governance/instrument-self-tests and codeql python were in progress. CI had not concluded, so this verdict does not rest on it. The block is a mutation finding, independent of CI. `## Red checks: none` matches what has concluded so far.
- Review packet rendered here (ev/review-packet.md): no refusals; `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted`; `FIGURES: 10 resolved`. Its finder's-harness section says "none named". The finder's harness for this round is the round-1 reviewer's ev/mut.py and ev/replay.py, as the brief names. The harnesses in ev/ here are those two, reworked as stated; projection_probe.py and the fixture probe are my own.
