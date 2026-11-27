# fixer-r11-ci-3885-queue-l4l3 (fire 3): carry 2 measured; W2 and the L3 handoff to a fresh context

Question: re-dispatch L3's W2 and its handoff to a fresh fixer context? Fire 3 measured carry 2, then reached the rotation bound. It did not see this ref until after it had rebuilt L4 locally (its comms init printed no `snapshot` line); that duplicate was discarded and never pushed. The next fire should read this ref first.

## Fire 3: carry 2 measured (commit on this ref, `dev/programme/carries/carry-3885.json` carry 2 `control` and `brief`)

- Source: GitHub MCP `list_workflow_jobs` and `get_job_logs`. `gh` is for search only in this container.
- Producer: light push fd93aa3e9b, CI run 45907525407, `tests / fast (3.14, 3/4)`, job 140208021805, the shard that owns env_drift. It logged `SKIP  tests/env_drift.py  (closure: 218 files, no changed file is in its measured closure)` and `Path(s) specified in the action for caching do(es) not exist, hence no cache is being saved`.
- Consumer: PR 3845, CI run 45907841043, `tests / fast (3.14, 3/4)`, job 140209859526, forked at fd93aa3e9b. It logged `Cache not found for input keys: drift-baseline-fe12a528...`, then `262s  python3 tests/env_drift.py --all fd93aa3e9b...`, then `Cache saved with key:` for the same key.
- The rule for which forks are exposed: a merge base whose first-parent diff is light by `prelude.light` and reaches no file in `tests/closures.json`'s env_drift closure, crossed with a PR diff that does reach it. The census script is in scratch only; re-derive it. At 190ffb10c2, 12 of the last 40 first-parent main commits are light and reach no env_drift file. Two open fix/ branches fork at one: fix/r11-owner-fault-text at 7194ff84c0 and fix/r11-seam-cycle-reporting-pr at fd93aa3e9b.
- The null control is not separated. PR 3870 run 45818958831 (job 139912619679) forked at full push 1d3077736d while that push's run was still running, and also missed: it saved a fresh entry, `326s`. Main push runs are often `cancelled`, and a cancelled full push warms nothing either. Still owed: a miss forked at a full push whose run did save, and the hit duration that prices a miss.
- Cache scope: actions/cache entries saved by a `pull_request` run are scoped to that PR's merge ref, so every PR forked at a light commit misses separately. This is from the actions/cache scoping rule, not measured here.
- The remeasure clause's push-log reading cannot show this, because a push restores no drift entry; the carry now says so.
- Destination: carry 2 belongs in L4's PR by the design (§5), but L4's head is frozen at its handoff. So it rides L3's PR: cherry-pick the carry commit onto the L3 handoff branch, and name it in the L3 body's `## Forward-carry` with `Carry: #3885`.

## State

- L4: unchanged since fire 1. It is at `handoff/r11-ci-3885-queue-l4` 77f41cbb0d, with its body on `handoff-body/r11-ci-3885-queue-l4`.
- L3 W1 is the commit below this one on this ref (cherry-picked; the handoff branch is that commit alone on 77f41cbb0d, without this file). It is not yet handed off.
  - `tools/ci/prelude.py`: `busy_sources` replaces `wait_sources`. It makes one runs listing and never sleeps. `outputs` gains a `defer` key and loses its `sleep` parameter. `WAIT_MAX_S` and `import time` are gone. `POLL_S` stays, because gate.py imports it.
  - `.github/workflows/ci.yml`: a prelude step `Defer: sources still running` runs `if: steps.derive.outputs.defer != ''` and exits 1. The prelude's `timeout-minutes` drops from 150 to 30. Check whether a `tests/entities.py` pin reads either line; neither has been checked.
  - `tools/ci/sweep.py`: `DEFER_STEP`, `deferred(jobs)` and `Sweep.undefer(runs, head)`, called in `run()` right after `runs_at`. `undefer` takes each completed run whose prelude failed on DEFER_STEP and asks `prelude.busy_sources` about it. If no source is busy, the run goes through the cap, then `stale_pin` and `fresh`, then POST `actions/runs/<id>/rerun-failed-jobs`. `judge` skips `deferred_ids`.
  - Self-tests: prelude 162 checks and sweep 133 checks, 0 failed at this commit.
  - Mutation proofs, run and restored:
    - Replacing the `self.undefer(runs, head)` call with `pass` fails 5 sweep rows: the four W1 re-run rows and the stale-pin null.
    - Making `out["defer"]` always `''` fails 4 prelude rows: three C3 rows and the W1 null control.
- Not yet run: closure scope (`tests/closure.py select`), `tests/structure.py`, archscore `--diff`, `prepr.sh`, the harness `dev/audit/harnesses/ci3885_queue.py waits` arm at both ends, and the per-poll API seconds the design §4 W1 row asks for.

## Next: W2 (design §4 W2 row; "the existing poll rows become completion rows, with the same POST set")

The plan this fire reached, not yet built:
1. `Sweep.run`, symmetric arm. When V's gate is completed and red, and another run G at the head has a green gate that `covers_newest` and that completed strictly BEFORE V's gate completed (`<`, so that row 354's case stays G's), re-judge V via `judge`. Leave V where `settled(v, vg, others)` holds, which bounds the arm to once per source change. Otherwise fall through to `settle`.
2. `Sweep.run`, the poll. Stop polling `pollable` gates, which are in progress. Print that their completion sweeps instead. Keep the arm for a gate that has completed in a run still running (its own sweep-self, seconds). Rows 265, 270 and 313 pin that arm, and removing it leaves a hole for bot-actor runs. Raise this departure in the body.
3. `settle`: drop the loop and read once. Any gate in progress, or completed in a run still running (other than the caller), means SKIP, because their completion sweeps.
4. Convert the poll rows (223, 246, 249-250, 253-254, 257, 260, 300, 307 and 407 at the base numbering) into two-sweep completion rows with the same POST set.
5. Then: `GATE_WAIT_MAX_S` to `GATE_ABSENT_MAX_S` per W3's cap, only if W1 removes every source wait (the design names it as conditional). Then scope, structure, prepr with `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`, the body, and `handoff/r11-ci-3885-queue-l3` plus `body_push.sh r11-ci-3885-queue-l3`.

