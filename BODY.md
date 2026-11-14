R10-CI-PRIORITY-PAUSE, carries 0-6, round 2: the repair of the fix review blocked `mutation-vacuous` at ff8b073827a8 (`cancel_superseded.priority_pass has_merge_verdict guard survives`). The group builds the CI-priority tier module and config (`tools/audit/seat/ci_priority.py`, `dev/audit/config/ci_priority.json`), the merge train's pause/resume (`tools/audit/seat/ci_pause.py`, hooked into `merge_train.py`), the owed-line ordering and paused-CI bucket in `orchestrator_tick.py`, the priority hold/cancel/re-run and the zombie memory in `tools/pr/cancel_superseded.py` and the beat's cancel-sweep row, and the roster fields (`roster_lib` readers, `roster_edit.py set-field`, `append-group` requires `source`).

This round adds:
1. **The verdict lookup is pinned.** `priority_pass` is split past its roster read into `priority_act`. A self-test stub answers the comments read: `Fix review: merge` on #12 and #13, and unreadable comments on the second pass. With `priority_cancel` on, it asserts that only #11's queued run is cancelled, and that unreadable comments cancel nothing.
2. **Carry 6 (ii), the hold, is built.** `CiPause.hold(sha)` returns the queued priority run (a `never_cancel` tier) while the pull request at `sha` is not priority. Main's tip is no pull request and reads as `main-push`, so it is never held, and an unreadable listing holds nothing. `Train.hold_reruns` asks it before the stale re-run (`Train.unstale`, which `merge_pr.sh unstale_head` also runs). It waits `POLL_SECONDS` a poll, logs `HOLD` once and `HOLD-END` when the run clears, and after `HOLD_POLLS` (6 polls, 30 min) it re-runs anyway with `HOLD-EXPIRED`, so a priority queue that never drains cannot stall the train.
3. **The pause is decoupled from `priority_cancel`** (orchestrator ruling on this review: carry 6 is not extended to the pause). `CiPause.poll` no longer reads the switch, so the P267 pause fires as the owner directed on 2026-10-28. `PAUSE-HELD` is gone. `priority_cancel` now switches only the sweep's cancels of queued runs.
4. **Carry 4's measure is built.** `ci_priority.py queue-wait` reports the minutes from a run's creation to its first job's start, split by the roster tier of its head branch. The before figure is below.

Carry 0: the tier module, its config and the train's pause/resume are built (`ci_priority.py`, `ci_priority.json`, `ci_pause.py`). Carry: dismissed: built in this pull request (commits 882a6385c2, 98650d10f3)
Carry 1: CARRY A and B built as amended: `paused.json` beside the train state, PAUSE/RESUME lines, one victim per pass, at most one pause per 5 minutes, resume on exit and at start, `tier()` the one class rule, group-keyed setting refused. The pause is no longer behind `priority_cancel`.
Carry 2: owed lines ordered by `ci_priority.rank`; a `paused.json` record older than 60 minutes with no train running is the owed line `paused CI never resumed`.
Carry 3: `roster_lib` readers, `roster_edit.py set-field` and the `source` requirement of `append-group` built; the backfill of live groups is the roster relay's (Forward-carry).
Carry 4: built into the sweep as the hold/cancel/re-run rule. Its queued-run cancel stays behind `priority_cancel` (false) by Carry 6. The before figure is measured; the after figure is owed once the switch is on (Figures).
Carry 5: built (zombie memory in `cancel_superseded.py`, beat filter).
Carry 6: built: (i) verdicted, spooled and queued PRs and the train's current one are never cancelled, now pinned at the live lookup; (ii) the train's stale re-run of a non-priority head holds while a priority run is queued; (iii) the main-branch queue share is reported in Figures.
Carry 7: moved to R11-INTAKE-R10-RESIDUE by the roster; not built here.
Carry 8: moved to R10-ROUND-PLAYBOOK-FINAL by the roster; not built here.
Carry 9: moved to R11-INTAKE-R10-RESIDUE by the roster; not built here.
Carry 10: dismissed by the roster as a duplicate of R10-OUTSIDE-CONTRIBUTOR-CYCLE carry 2; not built here.
Carry 11: moved to R11-INTAKE-R10-RESIDUE by the roster; not built here.
Carry 12: the same three gate-conclusion residuals as Carry 11 (same text, item 6e06de7f), which the roster moved to R11-INTAKE-R10-RESIDUE; not built here (Forward-carry).

## Head

d061e934fd0b0ff806c6274f3e001f17edf49d36, the repair commit and the wip marker merge on 56923ce8dd8d92aabcd894c6e23c5310d7b1144a (five commits on the reviewed head ff8b073827a8938d679ced28644cd28401f16dbc). Merge base 154dbb4c61652135381ce66646d23f7109d1c142. `git merge-tree --write-tree origin/main HEAD` at origin/main e23124ff6e45 reports no conflict, so main is not merged (fixer step 6).

## Mutation proof

Driver: the reviewer's `evidence/mut.py` from review/3560, extended with M10-M15. Each mutant is applied to the production text, the owning `--self-test` is run, and the text is restored. Run at fc156a4c9c00 (the fourth and fifth commits add self-test checks only, no production line; ci_pause 19 -> 25 checks, beat_jobs 203 -> 204):
- M1 `zombies[rid] = now` -> `pass`: killed, 2 FAIL (zombie re-POST, summary line).
- M2 ` or pr in protected` -> ` or False`: killed, 5 FAIL.
- M3 `if prio:` -> `if True:`: killed by a crash (IndexError, rc 1), as before.
- M4 the `allow_cancel` hold removed: killed, 2 FAIL ("with priority_cancel off ... cancels nothing (hold)", "with priority_cancel off the sweep cancels nothing").
- M5 the pause CP guard (`may_pause`) -> `if False:`: killed ("the critical-path tail is never paused").
- M6 the pause dormancy switch: anchor absent; this round removes the switch from the pause (M10 is its inverse).
- M7 the pause verdict guard -> `if False:`: killed.
- M8 `or rl.is_outside(g)` removed from `tier`: killed.
- **M9, the round-1 survivor**, `if has_merge_verdict(api, a.repo, pr) is not False:` -> `if False:` in the sweep: **killed**, 2 FAIL ("the live verdict lookup protects #12 and #13 ... only #11's queued run is cancelled": got 501, 502, 503 cancelled; "comments that cannot be read protect too").
- M10 the pause re-coupled to the switch (`if not setting["priority_cancel"]: return` before the pick): killed ("the pause is not the sweep's switch: with priority_cancel off a head job queued 6 min still pauses #13").
- M11 the hold dropped from `Train.unstale`: killed, merge_train 3 FAIL (the HOLD/HOLD-END arm, the null arm, the HOLD-EXPIRED arm).
- M12 `is_priority` dropped from the hold's queued-run test: killed ("a non-priority head waits ... naming it", "hold null: only non-priority runs queued holds nothing").
- M13 main's tip read as `instrument` instead of `main-push`: killed ("main's tip ... never waits").
- M14 the priority-head exemption dropped: killed ("a priority head (#10, critical path) never waits").
- M15 the `HOLD_POLLS` bound replaced by a stop: killed ("a priority queue that never drains holds HOLD_POLLS polls, then re-runs (HOLD-EXPIRED)").

## Null control

- Verdict lookup: with no `Fix review: merge` comment on #11, its queued run is cancelled. With M9 applied, the verdicted #12 and #13 runs are cancelled too. The self-test therefore separates the guard from its absence.
- Hold: "hold null: only non-priority runs queued holds nothing"; "carry 6 (ii) null: no priority run queued, the stale re-run is asked once and never waits" (no HOLD line). With the hold removed (M11), the HOLD arm fails.
- Pause: "null: no queued job pauses nothing" and "a head job queued under the bound pauses nothing" stand. With the pause re-coupled (M10), its switch-off arm fails.
- Queue-wait: "queue-wait null: with no critical path the same runs measure no priority wait". The same live window's non-priority runs are the comparator in Figures.

## Figures

- Self-tests at 56923ce8dd8d, run as `PYTHONPATH=tests/hastub python3 <file> --self-test` with the summary line read: ci_priority 14, ci_pause 25, cancel_superseded 61, roster_lib 92, roster_edit 311, beat_jobs 204, orchestrator_tick 319 and merge_train 746 checks, each 0 failed. `beat_jobs_selftest.py` rc 0.
- Carry 4 before figure, the minutes a priority pull request's first job waits queued: `python3 tools/audit/seat/ci_priority.py queue-wait --since 2026-11-12T15:00:40Z --until 2026-11-13T15:00:40Z --ref 154dbb4c61652135381ce66646d23f7109d1c142`. The window is the 24 h ending at the merge base's commit time; the tiers come from the roster at the merge base; run 2026-11-13T19:45Z. Result: 1876 runs, 1180 of them on main, 0 unstarted. Priority PR first job: n=276, median 0.1, p90 12.8, max 34.0 min. Other PR first job: n=420, median 0.1, p90 11.3, max 27.4 min. The non-priority runs are the comparator: in this window priority runs waited no less than the others.
- How the after figure is taken: the same command over a 24 h window after `priority_cancel` is switched on, with the roster ref of that day. Keep the switch only if the priority p90 and max drop below this before figure and below that window's non-priority comparator.
- Carry 6 (iii), the main-branch share: 1180 of the 1876 runs created in the window above are on main (same command). In a live listing, `gh api 'repos/tvofi/heatpump_optimizer/actions/runs?status=queued&per_page=100'` grouped by `head_branch == main`, 2 of the 11 queued runs were on main at 2026-11-13T19:37Z. That is a sliding window, so read the rule, not the number. Main runs are exempt from every cancel and hold, so they bound what cancelling non-priority runs can free.
- **What a critical-path, outside or hotfix PR's queued wait changes by at merge:** no cancel happens, because `priority_cancel` stays false. The one live change is that the train no longer starts a stale re-run of a non-priority head while a priority run is queued, for at most 30 minutes. That keeps at most one re-run per merge attempt out of the queue ahead of the priority run. The size of the effect on the priority wait is not measured. The before figure above shows a median of 0.1 min, so in this window the wait is a tail effect (p90 12.8 min). The P267 pause changes the train head's wait, not a priority PR's.
- Enumeration of the class "a seat or workflow starting a re-run or dispatch of a pull request's CI". Command: `git grep -nE '(/rerun|rerun-failed-jobs|/dispatches|gh workflow run|"workflow", *"run")' -- tools/ .github/ ':!*.md'`, with self-test lines removed. Every site and its disposition:
  - `merge_train.Train.unstale` (`POST .../rerun`; also `merge_pr.sh unstale_head`): **held in this diff** (M11).
  - `merge_train.Train.infra_rerun`: re-runs main's tip (`main_green`), the `main-push` tier, so it is never a non-priority PR's CI. The hold reads a sha with no open pull request as `main-push` and never holds it; that is pinned by "main's tip ... never waits" (M13).
  - `merge_train.Train.launch` (`gh workflow run` on a proof branch): the train's own batch head, the structural `train-head` guard; not held.
  - `ci_pause.CiPause.resume_all` (`rerun-failed-jobs`): the P267 pause, which the orchestrator ruled outside carry 6; not held.
  - `cancel_superseded.priority_step` re-run: already fires only when no priority run is queued ("the cancel is recorded, then re-run once no priority run is queued").
  - `tools/ci/gate.py` job re-run, and `tests.yml`/`merge-main.yml` `gh workflow run ci.yml` after a bot commit: these run inside Actions with no roster read. Holding them is a workflow change outside this part (Forward-carry).
  - `beat_jobs.py` `pages.yml` (main) and `ci_probe.py` (probe branches, by hand): no pull request; not held.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL` (tests/closure.py is in the diff), so CI runs the full gate.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Unpinned sites

`prepr.sh` diff mutants (MUTANT_CMD: `sh -c` running the ci_pause, beat_jobs, cancel_superseded and beat_jobs_selftest self-tests) found 18 survivors at fc156a4c9c00. The fourth commit kills 14 of them with checks (a re-run at ca250c18fcf0 left 8: the four below, `_api`'s except-return, and three in the new beat_jobs_selftest arm, two of which the fifth commit kills; the re-run at 56923ce8dd8d leaves the six listed here): the `--train-state` forwarding in `beat_jobs.cancel_sweep`; and in `ci_pause`, the minutes divisor of `queued_minutes`, the inclusive `pause_queued_min` and `pause_gap_min` bounds of `poll`, `_note`'s once-per-key, `_api`'s failure, unparsable and empty answers, and `write`'s empty list and new state dir. The other four, at three sites, and `_api`'s except-return are equivalent, so no check can kill them:
- `ci_pause.py` module head, `sys.path.insert(0, str(HERE))` deleted, or at index 1 (two mutants): run as a script, Python puts the script's directory first; imported, `merge_train.py` and `cancel_superseded.py` have already inserted the seat directory. The imports resolve the same either way.
- `ci_pause._epoch`, `return None` in the `except` deleted: the function then falls off its end and returns None anyway.
- `beat_jobs_selftest.py`, the `--train-state` arm's `res[...] = (...)` statement deleted: that deletes the check itself, so it cannot fail; the statements it reads are pinned by the two kills above.
- `CiPause._api`, `return None` in the `except ValueError` deleted: the function falls off its end and returns None anyway.
- `CiPause.__init__`, `self.last = 0.0` -> `1.0`: `last` is compared as `now - self.last < pause_gap_min * 60` with an epoch-seconds wall clock, and 1 s against 0 s changes no comparison.

## Red checks

`instrument-self-tests`, red at 070118088ac3 and green at the merge base; the branch's own, three steps, repaired:

- `tools/audit/seat/sweep_render.py` self-test: the overlay declared `train_state` and no sweep step used it. Step (4e) now renders `cancel_superseded.py sweep --repo R --priority {{train_state}}`, `train_state` is an optional flag (`--train-state`), and a new check pins value-renders and empty-leaves-out. Passes locally: `sweep_render self-test: 39 checks, 0 failed`.
- `selftest_scope.py --self-test` (one of 120 checks, "the live job parses and its gating is consistent"): the `ci-priority` step read no `steps.scope.outputs.<id>`, which `selftest_scope.py static` refuses as UNGATED. The step is gated and its closure recorded with `selftest_scope.py record --step ci-priority`. Passes locally: `117 checks, 0 failed`; `static: 115 gated step(s), 0 problem(s)`.
- `selftest_scope_mutants.sh --self-test` (`LINE RED: the unmutated self-test fails`): its baseline was the previous failure; no change of its own.

Cheaper detector: `ci_predict` ran none of these (a data-file read is not seen), so the standing detector is `selftest_scope.py static`, not in `prepr.sh`; recorded as not built, the owner-held lane. `prepr.sh` at this head: PRE-PR rc=0.

## Forward-carry

- Backfill of `source`/`hotfix`/`savings_source` on the live roster groups (carry 3 item 4) is a roster write this seat may not make. (into the round-11 opening list held by R10-ROUND-PLAYBOOK-FINAL) Carry: R11-INTAKE-R10-RESIDUE
- Enabling `priority_cancel` needs the after figure, taken by `ci_priority.py queue-wait` as stated in Figures. (into the round-11 opening list held by R10-ROUND-PLAYBOOK-FINAL) Carry: R11-INTAKE-R10-RESIDUE
- `roster_lib.is_hotfix` still treats `kind == "bug"` as a hotfix beside `hotfix: true` and the name rule; carry 3 defines it as the flag or the name only. (into the round-11 opening list held by R10-ROUND-PLAYBOOK-FINAL) Carry: R11-INTAKE-R10-RESIDUE
- Carry 6 (ii)'s hold at the workflow-side re-runs and dispatches (`tools/ci/gate.py`'s gate-job re-run, `tests.yml`/`merge-main.yml` `gh workflow run ci.yml` after a bot commit). They run in Actions without the roster, so whether carry 6 reaches them needs a ruling before a build. Carry: R11-INTAKE-R10-RESIDUE
- Carry 12 (item 6e06de7f), the gate-conclusion residuals: the same item as Carry 11, which the roster moved. Carry: R11-INTAKE-R10-RESIDUE

## Friction

- review: cost: round 1's mutants covered the pure `priority_plan` filter but not the live lookup that fills it, and a reviewer's mutant found the gap. The repair pins the lookup at `priority_act`. Carry: dismissed: resolved in this diff
- measure: cost: a filtered runs listing stops at 1000 results and the 24 h window held 1876, so `queue-wait` reads it in hour slices; one HTTP 502 mid-run aborted the first measurement, so the reader retries twice. Carry: dismissed: resolved in this diff
