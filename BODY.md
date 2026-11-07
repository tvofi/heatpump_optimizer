R10-CI-EDIT-RUNNER: Carry 1 (edit runs, the brief's carry 0) and Carry 2 (review runs, the brief's carry 1). If a body run (an `edit` or `review` run) finds an unfinished code run for its PR at its head, and that code run is not yet `judging`, it now runs no unit and exits. `prelude.defer_to` empties its workset, and its gate publishes `SELF_DEFERRED` at once instead of waiting. The code run's gate re-runs the latest deferring run of each kind once that code run is judging (`gate.redispatch`, through an `actions: write` grant on `ci.yml`'s `gate` job), and defers to that re-run at once; the sweep re-judges it. Every other gate at the head treats the pending re-run as busy (`gate.pending`), so no gate passes the head before its latest body and review are judged. The re-run's prelude finds the code run judging, runs its full workset and waits on nothing. Review runs (Carry 2) go through the same `defer_to` change. Their re-run is the "code run's gate re-judges the latest review" step. This supersedes R10-CI-SLIM card C3's partial edit workset (`EDIT_UNDER_CODE`, removed).

The change touches the code-owned `.github/workflows/ci.yml` and `tools/ci/`. It forces a `MODE: FULL` gate and merges only on the owner's approving review, or under mandate 6624093439 while that mandate is in force. Main moved (r10-gate-busy-defer-3 landed, which makes every deferral publish at once and has the sweep re-run it), so `origin/main` (53273de4d449) was merged in, with a hand-resolved conflict in `tools/ci/gate.py`: main's at-once deferral is kept for every gate, and this change's `redispatch` and `pending` ride on it. A code run's gate re-runs the latest deferring body run, then defers to it at once (the sweep re-judges it) instead of waiting. Three gate self-test expectations that assumed a wait were changed to the at-once result; both self-tests pass at the head (gate 86 checks, prelude 65). The mutation results and replay figures below were taken before that merge, on the wait-based gate: the prelude mutants M1-M4 are unchanged by it, but M5-M8 and the code-gate wait figures were not re-taken at this head.

Design choice, stated so a later seat does not read it as a bug: a deferring run's gate publishes a red at once, for a head that is still undecided. That reverses r10-gate-busy-defer-2's "a deferring edit gate waits like any other". The carry asks for exactly this: the run exits without holding a runner. The red belongs to that run's first attempt. The code run's gate re-runs the whole run, and the new attempt replaces it with a verdict.

Alternatives considered:
(a) Keep C3's partial workset for the case where the code run's `pr-contract` has not started, add a gate that publishes at once, and re-run only when `pr-contract` had started. On this window that is cheaper for edit runs, because the arch-score and budget-raise-gate work is not repeated. It lost because it needs two deferral shapes and two re-judge mechanisms (the re-run, and gate-sweep clearing an at-once red that nobody re-runs).
(b) A separate `redispatch` job beside `gate`. It lost because it races the gate's first read: the gate could judge before the re-run is queued. It would also add a runner to every code run.

## Head

daa600e64c477630674f534e2b7d9e82a7e2e286 (`origin/main` at 53273de4d449 merged in; `date -u`: 2026-11-07T20:10:00Z)

## Mutation proof

Each mutant below was applied to a production line, both self-tests were run (`python3 -I tools/ci/prelude.py --self-test`, `python3 -I tools/ci/gate.py --self-test`, with `__pycache__` cleared) and the line was restored. Each result is the count of checks that turned red.

- M1, `defer_to` never defers (`if False and not judging(...)`): prelude 5 red, including `defer: beside a started pr-contract the edit run exits within one poll (no wait)` and `defer: a review run beside an unfinished code run exits within one poll, running no unit`.
- M2, `defer_to` ignores `judging`: prelude 1 red (`null: beside a JUDGING code run ..., the full edit workset, no wait`).
- M3, only `edit` defers (`kind == "edit"`): prelude 1 red (the review deferral).
- M4, `deferring` reads `any` for `all`: prelude 1 red and gate 7 red (`deferring: ...`, `busy-defer`, `C3: the code run's gate takes the edit run's body units`, `#3261 ...`).
- M5, no re-run POST: gate 3 red (`edit-runner: the code run's gate re-runs the latest deferring edit and review run once each ...`, `... still at its own gate ... re-run`, `a refused re-run is published at once`).
- M6, the deferring gate waits (its `return False, [SELF_DEFERRED]` removed): gate 9 red, including `edit-runner: a deferring edit gate beside a busy code run publishes at once, holding no runner`.
- M7, nothing is pending (`deferring(r)` replaced by `False`): gate 5 red.
- M8, every gate kind re-runs (`kind != "code"` dropped): gate 1 red (`edit-runner: only a code run's gate re-runs; another gate waits on the pending run, bounded`). An earlier version of that test passed no `post`, so this mutant survived it. The test now passes the recorder.

Failing test first: on the base predicate, the new prelude checks read `got (('arch-score budget-raise-gate pr-contract', ''), [60])` beside a started pr-contract and `got (('budget-raise-gate', ''), [60])` for a review run: each waited one poll or more. The check names are in `tools/ci/prelude.py`'s self-test.

## Null control

- An edit run beside a judging or finished code run still runs the full workset `arch-score budget-raise-gate pr-contract` with no wait (two prelude checks, green at base and head).
- A review run beside a finished code run still runs `budget-raise-gate`.
- A code run for another PR at the head is still waited on.
- A code run's gate beside an edit run that ran its units re-runs nothing and judges at once (`edit-runner null: ...`).
- A superseded deferring gate, re-run by the sweep once nothing is pending, judges like every other gate (`edit-runner null: ... converges`).
- Replay null control: code runs pass through the same predicate with 0 deferred and job-minutes equal before and after (Figures).

## Figures

All figures come from `dev/audit/harnesses/r10_ci_slim/body_defer.py`. Its docstring states the cost rule; read it there rather than here. The input is $SAMPLE (sha1 fb0d479ba40d694d8feeb5ffc864084fd89df034), recorded by `python3 dev/audit/harnesses/r10_ci_slim/edit_runs.py --fetch $SAMPLE --since 2026-11-05T13:26:00Z --until 2026-11-07T22:00:00Z`. It is not committed: at 3.4 MB, the machinery ratchet's churn_per_kilo_product_lines refused it, so the in-tree fetch re-records it. The last run was created at 2026-11-07T15:14Z. The window starts with the s12 study's window. The prelude floor is the median code-run prelude, 0.45 min.

- `python3 dev/audit/harnesses/r10_ci_slim/body_defer.py $SAMPLE --since 2026-11-07T05:00:00Z`. This is the merge-base regime: C3 and r10-gate-busy-defer-2 were both on main from 04:47Z. Edit runs: 70 runs, 70 deferred, 53 re-run. Job-minutes 358 -> 426. Prelude wait above the floor 12 -> 0. Code-gate wait added 122. Review runs: 20 runs, 20 deferred, 19 re-run. Job-minutes 180 -> 57. Prelude wait above the floor 127 -> 0. Null control: code runs, 0 deferred.
- The same command without `--since`, over the whole window, which includes heads whose base predated C3. Edit runs: 399 runs, 396 deferred, 271 re-run. Job-minutes 3524 -> 2187. Prelude wait above the floor 2022 -> 0. Code-gate wait added 625. Review runs: 99 runs, 95 deferred, 69 re-run. Job-minutes 889 -> 263. Prelude wait above the floor 652 -> 2. Null control: code runs, 368 runs, 0 deferred.
- Control at the merge base: `python3 dev/audit/harnesses/r10_ci_slim/body_defer.py $SAMPLE --prelude $EXPORT/tools/ci/prelude.py`, where $EXPORT is b4ec2f332fe3 and that file's sha1 is 72652866a9273e2d0641b32cb8924f2c6bf18237. Review runs: 99 runs, 0 deferred. At the base a review run never defers, which was Carry 2's open case.
- Carry 1's figures were re-measured at the merge base and no longer hold. That carry's 24 h window was 2026-11-01, before C3. In the same recording, edit preludes since 2026-11-07T05:00Z have a median of 0.48 min, p75 0.52 and max 5.8 (68 preludes); the carry's figure was a median of 37.2 min. In that regime edit runs hold their runner in the gate instead: the gate job's p90 is 11.92 min against a median of 0.58, which is C3's deferring gate waiting up to its 12-minute bound. That gate wait is what this change removes for edit runs. Rule: the gate job's completed_at minus started_at over edit-titled runs created since that instant. Instrument: a one-off over the sample with `edit_runs.minutes`; no tree command prints these two figures.
- Carry 2's figure was re-measured under a different rule: review prelude minutes above the floor, rather than waits beyond one minute. The result is 652 over the whole window and 127 since 05:00Z (body_defer.py, above).
- What the trade is. Since 05:00Z, edit runs cost about 68 job-minutes more under this model. The model's code-gate wait is an estimate: it over-counts by summing arch-score and budget-raise-gate, which run side by side, and it leaves out job pickup latency. Review runs cost 123 fewer. The minutes body runs spend holding a runner by waiting in their prelude go to 0 for both kinds. The edit gate's wait moves into the code run's gate, which holds a runner only for the re-run's body units, not for the code run's own units.
- Class seams. The rule is `outputs()`: every kind it sends to `wait_sources` (`kind != "code"`), which is edit, review, label and kernel-points. Edit and review are closed in this diff. Label and kernel-points still wait: the sample holds 0 runs of either kind (rule: titles that `prelude.parse_title` reads as each kind), so no cost was measured. They are left to a later seat by name.

## Red checks

none: no check has gone red yet. `tools/pr/prepr.sh` predicted one red on `tests / closures` (`INERT READS tests/harness_headers.py: dev/audit/harnesses/r10_ci_slim/body_defer.py`), and `tools/pr/ci_predict.py --apply-inert` repaired it before the handoff.

## Forward-carry

- Finding, not fixed here. `gate.gate` picks each unit's source from the highest-id run at the head that owns it. A body run numbered below its code run is the R10-RCA-CODESCAN-WAIT case: the edit run got the lower id in 27 of 94 same-second pairs, a figure recorded there and not re-measured. When that happens, the code run's own arch-score and budget-raise-gate shadow the body run's, even after its re-run. This change does not create the case, which was open under C3 and under the wait before it, but it does not close it either. It lands in that group's brief in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Label and kernel-points prelude waits (see Class seams). Carry: dismissed: zero label or kernel-points runs in the sample, so no cost was measured to act on

## Friction

- frugal-inline-budget: cost: the session's frugal routing hook refused a seventh plain file read in one prompt, which pushed reads of the repository's own files into subagents. Carry: dismissed: session tooling outside the repository
