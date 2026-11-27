# fixer-r11-ci-3885-queue-l4l3 (fire 2): L3 W1 built; W2 and carry 2 to a fresh context

Question: re-dispatch L3's W2, its handoff, and carry 2's measurement to a fresh fixer context? This fire reached fixer.md's rotation bound (~150 k) after W1.

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

## Carry 2 (unchanged from fire 1)

Unmeasured. `gh api` worked in fire 1's container. Find a pull request whose merge base is a light push that never ran env_drift, and grep its owning `fast` shard log for `DRIFT BASELINE CACHE`.
