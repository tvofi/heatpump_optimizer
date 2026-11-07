Fix review: blocked 61f1ec71a428b43fc2965379ab08c6747d214e5b architecture-unsound: sweep_runner.sh is a second copy of six beat_jobs.py rows, not an update of the tracked sweep scripts the owner ruling names

bus-nonce: 96c989956d6388b5c07d3d4b99445a4f

## Block

Round: first review of #3267 (R10-SWEEP-TEMPLATE-SYNC), at head `61f1ec71a428b43fc2965379ab08c6747d214e5b`. Role checked: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract I read is current.

The owner ruling the brief quotes is "There should already be tracked sweep templates/scripts for these, update them if needed". The PR body says the opposite: "Tracked counterparts: only `sweep_render.py` and `sweep_template.md` existed". That is false at the merge base `f2a01514`. `tools/audit/seat/beat_jobs.py` (run by `beatd.py` from `beatd.jobs.json`) is the tracked script for the sweep's mechanical steps. Its `ROWS` are `tick-digest, owed-check, roster-drain, plan-beat, pulse, cancel-sweep, disk, opener, head-watch, audit-dispatch` (ev/base-beat_jobs-rows.txt, ev/base-beatd.jobs.json).

The new `tools/audit/seat/sweep_runner.sh` (ev/head-sweep_runner.sh) is a parallel loop. It re-implements six of those ten rows: the roster drain, `pulse.py`, `cancel_superseded.py sweep`, the disk floor with `worktree_gc.sh`, `replan.py` + `state_docs.py --push --mirror --plan` (plan-beat), and `owed_unactioned.py` (owed-check). The new `roster_drain.py` re-implements the `roster-drain` row's drain through `roster_queue.py run`, and its own page has to rule that "the two do not run together on one queue". Running both loops in one session runs `state_docs.py --push` twice against one state ref, with nothing to serialise them.

`sweep_template.md` now names both owners for the same step. (4b) says the beat's `plan-beat` row replans and pushes the state docs every 30 minutes. The new (4b+) says `sweep_runner.sh` re-renders and republishes them every second pass. Its consumer (`sweep_render.py` renders the template for the orchestrator) gets two contradictory instructions.

The sound shape is the one the ruling asks for. Make `sweep_gantt.py` and `verdict_audit.py` new rows of `beat_jobs.py`, with their lines going to the digest the orchestrator already reads. Add the `PLAN MOVED` compare to the `plan-beat` row. Fold the roster-drain differences (exact-line `#refused` + ROSTER-CASCADE/UNRUN) into the existing row or `roster_queue.py`. Do not ship a second loop, a second drain and a template step that duplicates (4b).

Harness: the base tree's `beat_jobs.py` ROWS against the runner's step list. Metric: the number of runner steps that already exist as a beat row, 6 of the runner's 9 steps. Perturbation: delete the runner's six duplicated steps. The template's (1b), (4b) and (4e) steps, run by beatd, still cover every one of them, so they are redundant, not new coverage.

## Findings

- Defect: `sweep_runner.sh` and `roster_drain.py` add a parallel sweep loop and drain beside `beat_jobs.py`/`beatd.py` instead of updating them (the owner's ruling), and `sweep_template.md` (4b+) contradicts (4b) on who replans and pushes the state docs. Claim, evidence, harness and metric are as in `## Block`. Repair: Gantt and verdict audit become `beat_jobs.py` rows, PLAN MOVED goes into `plan-beat`, and the runner and second drain are dropped. Carry: R10-SWEEP-TEMPLATE-SYNC
- Defect: the body's "Tracked counterparts: only `sweep_render.py` and `sweep_template.md` existed" is false at the merge base (`beat_jobs.py`, `beatd.py`, `beatd.jobs.json`, `tick_loop.sh`), so the body's justification for adding files rather than updating them does not stand. Carry: R10-SWEEP-TEMPLATE-SYNC
- Defect: alert 51's repair has no local check that reads the file mode. The 0o755 copy of `sweep_runner_selftest.py` (89f08728^) prints `sweep_runner self-test: 11 checks, 0 failed`, the same as the 0o700 head (ev/selftest-0o755.txt, ev/selftests-head.txt). The only detector that moves under the mutation is CodeQL `py/overly-permissive-file` on CI, as the body itself says. The repair is at the root (both `w(...)` callers pass 0o700, with no suppression), but the brief's "a named check goes red" holds only for CI's CodeQL. Carry: R10-SWEEP-TEMPLATE-SYNC
- Defect: `.github/workflows/governance.yml`'s new step runs `sweep_runner_selftest.py` twice, because `sweep_runner.sh --self-test` already `exec`s it. Carry: R10-SWEEP-TEMPLATE-SYNC

## Evidence

- HEAD reviewed: `61f1ec71a428b43fc2965379ab08c6747d214e5b` (ev/HEAD.txt); merge base `f2a015142714383722bf49d7ab20d8398ec9674c`; three-dot diff in ev/three-dot.diff (14 files, +813/-1).
- RESULT: self-tests at head: sweep_gantt 16 checks, 0 failed; verdict_audit 14 checks, 0 failed; roster_drain 9 checks, 0 failed; sweep_runner_selftest.py 11 checks, 0 failed; sweep_runner.sh --self-test 11 checks, 0 failed; selftest_wiring --check: 123 self-testing, 123 wired, 0 index gap(s). All five body figures re-derived.
- RESULT: self-test count unchanged by the repair: 11 checks, 0 failed at 0o755 (89f08728^) and at 0o700 (head). `sweep_runner_selftest.py` does not exist at the merge base, so there is no base-side count; the comparison is across the repair commit.
- RESULT: `git merge-tree --write-tree origin/main HEAD` exits 0 (ev/merge-tree.txt).
- RESULT: VERSION, manifest, RELEASE_NOTES.md and every `*_budgets.json` are untouched in the three-dot diff. The four new tracked Python and shell files are classified in `tests/closures.json`, and `dev/programme/delivery/3267.md` is in the diff.
- RESULT: `## Head` names `61f1ec71` as merging code head `89f08728`, which is current. Its second paragraph still carries an older note about 89f08728 and prepr.
- Scope: no production code is touched. The scope is the sweep instruments plus the governance step, which is in the brief.
- Mutation proofs the body names (LIVE_H, the `held` guard, `--handoff-rows`, `#refused`) are pure-instrument mutants. They do not bear on the block, so I did not re-run them.
- CI: see the CI section appended below.
- CI on this head (`merge_train.py classify 61f1ec71... --pr 3267`, log in ev/ci-log.txt): `RED 61f1ec71a428b43fc2965379ab08c6747d214e5b pending: none red: gate` at 02:57:44Z. The one concluded red is `gate` (check run 128279140047, workflow run 42331132062), which concluded `failure` with an empty output. The code run 42331131423's jobs were still `in_progress` at that time (`tests / fast (3.14)`, `tests / coverage`, `tests / closures`, `governance / instrument-self-tests`, `codeql / Analyze (python)` among them), which matches the edit-run deferral R10-HOTFIX-GATE-BUSY-DEFER, so run 42331131423's gate decides. I could not read the gate's deferral text, because its check-run output is empty. That red is not the ground of this block, and I did not wait the 60 minutes for it: the architecture block stands whatever the code run concludes. All 47 check runs were on one page (`total_count` 47). `CodeQL` was `neutral` before `Analyze (python)` concluded, so whether alert 51 is closed at this head is not yet shown.
- `## Red checks` in the body covers the prior head 0ae78ac1's reds (CodeQL/alert 51, pr-contract, gate). The gate red at this head is the same deferral class.
