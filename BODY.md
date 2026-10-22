Roster for round 10, seventh landing (PR-B of the Lean flow study's two roster pull requests, after #2576). It registers the `R10-FLOW-*` groups from the study's pack, the fly-in and playbook groups, the carries the pack and the fix reviews owed, and the post-merge stage changes. Part of #201. It closes nothing by keyword and leaves #201 open. The diff against the merge base is `dev/programme/rosters/wave-r10-groups.json` and the record bot's `dev/programme/delivery/2588.md`.

## Head

`ad10fd2153c6c8fe2e1d56c8b0302c5b057cc37a`, the PR head. Every figure below was taken at it; its parents are the authored code head `306a96d5f21f7876070d48c194fd4be99b64022c` (tip of `handoff/audit-r10-roster`, frozen for this round) and `origin/main` `93e6a63d2855651448a2b8f677b392feddc03c99`, which is also the merge base. Commits since the reviewed head `922640dcd6ca515040d18a12a0a4e74aaa5eb8fb`: roster_edit `append-carry R10-FLOW-BODY-ONLY`, `append-carry R10-ORCH-MACHINERY`, `edit-brief R10-SCORES`, `set-stage R10-ADVISOR`, `set-stage R10-RCA-ORCH-CONTINUITY`, and merges of `origin/main`. This is a body-only re-take: no code or roster byte differs from the head named.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

The base is main's own roster: `git diff --exit-code origin/main 93e6a63d2855651448a2b8f677b392feddc03c99 -- dev/programme/rosters/wave-r10-groups.json` has rc 0, so nothing main wrote since the merge base is overwritten. A `removed` count above zero would show a dropped group; the program prints 0.

## Figures

Two jq programs over the roster at the base and the head (`B=93e6a63d2855651448a2b8f677b392feddc03c99`, `H=ad10fd2153c6c8fe2e1d56c8b0302c5b057cc37a`, `R=dev/programme/rosters/wave-r10-groups.json`). A group is new when its `.group` is absent from the base, changed when present in both and unequal as JSON.

- Groups base and head: `for r in $B $H; do git show $r:$R | jq '.groups|length'; done` prints 108 and 144.
- New, removed, changed: `jq -n --slurpfile b <(git show $B:$R) --slurpfile h <(git show $H:$R) '($b[0].groups|map({(.group):.})|add) as $B|($h[0].groups|map({(.group):.})|add) as $H|{new:[$H|keys[]|select($B[.]==null)]|length, removed:[$B|keys[]|select($H[.]==null)]|length, changed:[$H|keys[]|select($B[.]!=null and $B[.]!=$H[.])]|length}'` prints new 36, removed 0, changed 30.
- The 36 new are 23 `R10-FLOW-*`, 12 `R10-FLY-*` and `R10-ROUND-PLAYBOOK`: the same program with `|keys[]|select($B[.]==null)` listing names, counted by prefix. The twelve fly-ins: `RELAY-REVIEW-FF`, `CAP-LINE`, `CARRY-DISPOSITION`, `OPENPR-ATOMIC`, `ORPHANS-REWRITTEN`, `CARRY-DOC-CONTEXT`, `ROW-HEAD-CARRY`, `DEPGRAPH-STALE`, `GH-READ-RETRY`, `BUDGET-LEAF`, `STAMP-CHECK-NOTES`, `MANDATE-REVOKE-GUARD`. `R10-FLY-CARRY-DISPOSITION` is new: its files are `carry_audit.py` and `bus.sh` and its after is `R10-FLY-ORPHANS-REWRITTEN`.
- Changed groups by field: the same program with `|. as $g|[$H[$g]|keys[]|select($B[$g][.]!=$H[$g][.])]` per changed group, counted by field, prints `carry` in 22 groups (18 carry-only), `resume` in 10 (the stage changes below; `R10-CI-LAYOUT` and `R10-RCA-ORCH-CONTINUITY` change carry as well), and beyond carries two groups change other fields: `R10-SCORES` (brief; files gain `payload.py`) and `R10-ORCH-MACHINERY` (files gain `tools/audit/seat/orchestrator_tick.py`; after gains `R10-TICK-OWED-LEVEL`, `R10-FLOW-MAIN-GATE`, `R10-CI-LAYOUT-P1`).
- Stage changes, all `in-progress` to `done` with `resume.commit` set to the merge commit on main: `R10-CI-RATCHET-RED` d7121f32b, `R10-REPLAY-CAP` 290712ec0, `R10-I5-DOCS` 92b5bf442, `R10-FREQ-DEFROST` 4b36dc730, `R10-TICK-OWED-LEVEL` 295c874e8, `R10-CI-LAYOUT` 5a755f53e, `R10-HANDOVER-REFRESH` 302f66571 (#2566), `R10-ROSTER-PUSH-RACE` 3a9c6f849 (#2569), `R10-ADVISOR` f24895c0c, `R10-RCA-ORCH-CONTINUITY` 93e6a63d2. Read with `git show $B:$R | jq -c '.groups[]|select(.group==G)|.resume'` against the same at `$H`.
- `R10-FLOW-RECHAIN` is registered already `done`: its substance merged as #2576 (500668757). Its `resume.commit` is null and its `next_step` is stale ("dispatch a fixer once every after group is done"); the roster is frozen for this round, so it is left as is and named for the roster seat (an optional edit; no group can take it, since the group is done).
- Waves and path: `python3 tools/audit/seat/plan_table.py --roster-ref origin/main` and `--roster-ref $H` both print `8 wave(s)` and a critical path of length 8. The path differs: main's starts `R10-ADVISOR -> R10-SCORES`, the head's starts `R10-NIGHT-FOLDS -> R10-LOOP-CPU`; the last six nodes (`R10-LIVESTATE` to `R10-ARCH-DOCS`) are identical. `R10-ADVISOR` is `done` at the head and `in-progress` on main.
- Carry routing: `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <this body>` prints `0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`; `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster sweep` prints the same counts.

## Red checks

State at ad10fd21 from `gh api repos/tvofi/heatpump_optimizer/commits/ad10fd2153c6c8fe2e1d56c8b0302c5b057cc37a/check-runs` (read 2026-10-22):

- `nightly-status` is `failure`. It grades the last scheduled run on `main` (`tests/nightly_status.py`, run from the base), not this branch; the diff changes the roster and a delivery row, neither of which it reads. Per `defect-root-cause.md` it is the orchestrator's on main.
- `closures`, `env-matrix` and `instrument-self-tests` are `in_progress` at that read; none has concluded, so none is red or green. They are not claimed here.
- Every other run at the head is `success`, `skipped` or `neutral` (CodeQL), including both `pr-contract` runs.
- The intermediate commits `23cc013fa` and `306a96d5f` show no non-green check-run in the same API call (the failing-or-pending filter prints nothing for them).

## Forward-carry

- The `R10-FLOW-BODY-ONLY` P22 carry cites `update_pr.sh` "l.42", which at main is the unpushed-worktree refusal; the 75 exit for "branch checked out elsewhere" is at `update_pr.sh:46` at `93e6a63d2`. Its "28 permanent (topic, handoff-sha) entries ... 17 / 6 / 5" counts come from the relay's out-of-tree state and are not tree-derivable. The fixer locates the exit by its message text and re-measures the counts at its own start. Carry: R10-FLOW-BODY-ONLY
- `brief_lint`'s `METRIC_LITERAL_RE` catches only the comparator form of a metric literal; a prose literal ("The class_excess_loc budget is N.") lints clean. Dismissed: the rule enforces #411 class 4 as defined, no stage depends on widening it, and this PR adds no such literal. Carry: dismissed: the rule enforces #411 class 4 as defined and no stage depends on widening it.

## Friction

none
