R10-CI-PRIORITY-PAUSE, carries 0-6. Builds the CI-priority tier module and config (`tools/audit/seat/ci_priority.py`, `dev/audit/config/ci_priority.json`), the merge train's pause/resume (`tools/audit/seat/ci_pause.py`, hooked into `merge_train.py`), the owed-line ordering and paused-CI bucket in `orchestrator_tick.py`, the priority hold/cancel/re-run and the zombie memory in `tools/pr/cancel_superseded.py` and the beat's cancel-sweep row, and the roster fields (`roster_lib` readers, `roster_edit.py set-field`, `append-group` requires `source`). The orchestrator's ruling governs: the roster brief's shape (pause/resume in the train), not the withdrawn cancel-sweep home; Carry 6 overrides any cancel rule.

Carry 6 decision, stated up front: the setting `priority_cancel` is **false**. The one measurement in hand (the 2026-11-11 local cancel shim: 21 cancels, no priority run drained, 10 verdicted PRs reddened, 6 cancelled runs never completed) says cancelling does not shorten a priority PR's wait, so the sweep and the train **hold** (cancel nothing, print one summary/`PAUSE-HELD` line) until a before/after measure justifies turning it on. The cancel, re-run and pause paths are built and tested but dormant.

`after` groups: R10-TICK-LEVELS and R10-OUTSIDE-FIRST are merged on main (`git log origin/main` shows `fix/r10-tick-levels-p2` and `fix/r10-outside-first` merges); `roster_lib.is_outside` and the tick's `owed_levels` from them are relied on.

Carry 0: the tier module, its config and the train's pause/resume are built (`ci_priority.py`, `ci_priority.json`, `ci_pause.py`). Carry: dismissed: built in this pull request (commits 882a6385c2, 98650d10f3)
Carry 1: CARRY A and B built as amended: `paused.json` beside the train state, PAUSE/RESUME lines, one victim per pass, at most one pause per 5 minutes, resume on exit and at start, `tier()` the one class rule, group-keyed setting refused.
Carry 2: owed lines ordered by `ci_priority.rank`; a `paused.json` record older than 60 minutes with no train running is the owed line `paused CI never resumed`.
Carry 3: `roster_lib` readers, `roster_edit.py set-field` and the `source` requirement of `append-group` built; the backfill of live groups is the roster relay's (Forward-carry).
Carry 4: built into the sweep (`sweep --priority`) as the hold/cancel/re-run rule, dormant behind `priority_cancel` by Carry 6.
Carry 5: built (zombie memory in `cancel_superseded.py`, beat filter).
Carry 7: not this part's; MAIN-CANCEL-BOUNDED stays in round 10 as another part's carry.
Carry 8: moved to round 11, not built here.
Carry 6: built; it overrides Carry 4 and the pause's cancel: verdicted, spooled and queued PRs and the train's current one are never touched, and cancelling is off.

## Head

fbdfd5ddf25f8bd98e2a2dfc17b08bc5969ebad1 (code: handoff head ec3c6b8b29f1a5207c3315c6ee7d6b1f07f99335 with origin/main e4ca2d940efd1e87912d80cb3ebddf8240ba0729 merged in), first built at 232af53a9fb1c583d324d4288a11697685f9763e. The earlier head's only change after the build was tests/closure.py INERT_EXCEPT gaining `tools/audit/seat/ci_priority.py` and `tools/audit/seat/ci_pause.py` and tests/closures.json gaining their entries under tests/entities.py.

Merge resolution: the one content conflict was `tools/audit/seat/roster_edit.py`, the `op` choices of `build_parser`: this branch added `set-field`, main added `set-price`. Resolved as the union (`"set-source", "set-field", "set-price"`); the merged file reads back both ops' functions (`op_set_field` with its dispatch and `--field` checks, `op_set_price` with `--price-cite`), both self-test blocks, and `STRUCTURAL_OPS` as on this branch (main's does not lane-guard `set-price`). `tests/closures.json` merged through the ledger merge driver with no conflict.

## Mutation proof

Each mutant applied to production text, `--self-test` run, text restored (driver: scratchpad `mut.py`; the production lines are the predicates, not tails):
- `zombies[rid] = now` -> `pass` (carry 5, drop the record): fails "zombie: the 409 run is POSTed on the first pass, never on the second" and "zombie: the second pass counts it in the summary line".
- `if prio:` -> `if True:` in `priority_plan` (drop the priority check): the null control "priority null: no priority run queued selects nothing" crashes the self-test (rc 1, IndexError) — killed, though by a crash rather than a FAIL line.
- ` or pr in protected` -> ` or False` (drop the verdict/train check): fails "priority: a queued priority run cancels ... not ... verdicted ones", "priority carry 6: a queued run of a verdicted/spooled/train PR is never selected" and the cancel/re-run check.
- `ci_priority.may_pause(...)` guard -> `if False:` in `ci_pause.pick` (drop the CP guard): fails "the critical-path tail is never paused".
- `p["n"] in held or` removed (drop the train-head/train-held guard): fails "carry 6: a verdicted PR ... train-held one" and "the train head is never a victim".

Merge re-check: with `"set-field",` removed from the choices the roster_edit self-test fails ("set-field class is accepted", "set-field source with a word outside SOURCES is refused"); with `"set-price"` broken it fails ("set-price stores the citation stripped ..."); restored, `roster_edit.py --self-test` prints 310 checks, 0 failed.

## Null control

The unmodified tree (origin/main) has no tier rule, no pause, no zombie memory: a 409 run is POSTed on every pass. Pinned nulls: no queued head job pauses nothing and a job queued under `pause_queued_min` pauses nothing (`ci_pause`); no priority run queued selects no victim (`priority_plan`); a non-409 failure (`None` answer) is POSTed again on the second pass ("zombie null"); a roster with no new fields loads unchanged and the default setting reproduces the old owed order (the existing "hotfix first, outside and critical path by number, then the rest" tick checks pass unchanged); with `priority_cancel` false a queued priority run cancels nothing.

## Figures

- Self-tests at the head: `python3 tools/audit/seat/ci_priority.py --self-test`, `python3 tools/audit/seat/ci_pause.py --self-test`, `python3 tools/pr/cancel_superseded.py --self-test`, `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test`, `python3 tools/audit/seat/orchestrator_tick.py --self-test`, `python3 tools/audit/seat/beat_jobs.py --self-test`, `python3 tools/audit/seat/roster_lib.py --self-test`, `python3 tools/audit/seat/roster_edit.py --self-test`: each prints `0 failed`.
- Queue share (Carry 6 iii), instrument: `gh api 'repos/tvofi/heatpump_optimizer/actions/runs?status=queued&per_page=100'` grouped by `head_branch == main` and `event`, at 2026-11-11T23:26Z (a sliding window, so the rule not a number to carry): main-branch `workflow_run` runs are the largest single group of the queue, 18 of the 43 queued, and the other 25 are `pull_request`, `pull_request_target`, `pull_request_review` or `workflow_dispatch` runs; main runs are exempt from the rule, so they bound what cancelling non-priority PR runs can free.
- Queue wait, before (Carry 4): same listing, median age of a queued run `created_at` to now was 33 min and the oldest 50899 min (a ghost run); `gh api '...actions/runs?status=in_progress&per_page=1' --jq .total_count` gave 11 running. This is the queue-wide wait, not a priority PR's first job; no after figure can be taken before merge. The body does not claim a gain. Re-measure with the two commands after merge, and turn `priority_cancel` on only if a priority PR's first-job wait drops.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` selects `tests/entities.py` (mode SCOPED).
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` (the new code lives in new modules, not in `coordinator.py`; `merge_train.py` gained one call per hook and four small methods).
- Enumeration for the class "something that re-runs or dispatches CI for a PR head", by grep of `rerun|dispatches` over `tools/`: `merge_train.Train.unstale` (train/`merge_pr.sh` PRs only: protected by carry 6 (i)), `Train.infra_rerun` (main), `tools/ci/sweep.py` and `gate.py` (run inside Actions, no queue view), `ci_probe.py` (manual). None is held by this PR; the hold in carry 6 (ii) is the sweep's own re-run, which fires only when no priority run is queued.

Figures re-run on the merged head: ci_pause 14, ci_priority 12, merge_train 670, orchestrator_tick 317, roster_lib 92, roster_edit 310, cancel_superseded 58 checks, each 0 failed; beat_jobs_selftest rc 0. `tools/pr/prepr.sh` at the merged head: `PRE-PR: fbdfd5ddf25f... rc=0`, merged structure ratchet passed, CI predict no red; closures skipped (CI re-records). `carry_audit.py landed` on this body: 0 missing.

## Red checks

`none` owed in `merge_train.py owed-reds`' set. The merge-repair: origin/main (#3471) conflicted in `merge_train.py`'s self-test; both sides' blocks are kept (the pause feed check and the one-job pulse checks), and the merged file reads back both `_ci_pause` and `one_job_pulse` in production. `dev/audit/config/ci_priority.json` was never in the built commit (the `config/` ignore rule); it is now tracked (`git add -f`) with the values the design docs and the self-tests fix, and `merge_train.py`, `ci_pause.py` and `ci_priority.py` self-tests print `0 failed`. prepr's last run still predicts reds outside the owed set, in CI-autofix's class: `tests / fast` UNCLASSIFIED and `tests / closures` UNDER-SCOPED for that file and `ci_priority.py` (read by `orchestrator_tick.py`'s self-test through `tests/entities.py`). The file is on `INERT_EXCEPT`; the closure recording cannot finish here (no homeassistant, `tests/entities.py` a3 checks fail), so closures-autofix records it in CI.

## Forward-carry

- Carry 0 (item ce279d5a), the tier module, its config and the train's pause/resume, is built in this pull request (`ci_priority.py`, `ci_priority.json`, `ci_pause.py`). Carry: dismissed: built in this pull request (commits 882a6385c2, 98650d10f3)
- Backfill of `source`/`hotfix`/`savings_source` on the live roster groups (carry 3 item 4: R10-UX-HEALTH, R10-ROUND-PLAYBOOK, the `Owner-reported` briefs) is a roster write this seat may not make; `append-group` refusing a group without `source` takes effect for new groups only. (into the round-11 opening list held by R10-ROUND-PLAYBOOK-FINAL) Carry: R11-INTAKE-R10-RESIDUE
- Enabling `priority_cancel` needs the after measure above. (into the round-11 opening list held by R10-ROUND-PLAYBOOK-FINAL) Carry: R11-INTAKE-R10-RESIDUE
- `roster_lib.is_hotfix` still treats `kind == "bug"` as a hotfix beside `hotfix: true` and the name rule (the existing dispatch-rank checks pin it); carry 3 defines it as the flag or the name only. (into the round-11 opening list held by R10-ROUND-PLAYBOOK-FINAL) Carry: R11-INTAKE-R10-RESIDUE
- Carry 9 (item 7bd3e57f), name the process sending `@tvofi` cancels at live heads, then land P267's bounded pause or refuse at that seat's cancel path: the pause is built here (`ci_pause.py`, Carry 1) but the sender naming and the landing check against R10-TRAIN-MERGE-LOOP-2 were not established in this part; re-home it with the round-11 residue. Carry: R11-INTAKE-R10-RESIDUE
- Carry 10 (item dfa8b375), three live checks on a test fork (update-branch identity, app_approve end to end, class-O commit_id): this seat has no `gh`, no App key and no fork pull request, so it cannot run them. Carry: R11-INTAKE-R10-RESIDUE
- Carry 11 (item 6e06de7f), three residuals in the gate-conclusion readers of `merge_train.py` and `orchestrator_tick.py` (a read bypassing `classify`, an empty `Busy` built from made-up runs, refusal only at run time): new code outside this part's brief. Carry: R11-INTAKE-R10-RESIDUE
- Carry 12: not built in this pull request; appended after this part's dispatch and left for the group's next part. Carry: R10-CI-PRIORITY-PAUSE

## Friction

- policy-reread: unclear: carry 3 names `source` in {user, audit, programme} while R10-OUTSIDE-FIRST already uses `source: outside`; `SOURCES` now holds all four. Carry: dismissed: resolved in this diff
- prepr: cost: the closures step re-records `tests/entities.py` under strace for roughly half an hour on every run. Carry: dismissed: known cost of the closure recording
