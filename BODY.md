Hotfix: `Nightly / record-autofix` is red on every push to main below the batch floor. Its batch gate called `record_row.py --batch-due` bare and read `batch=$?` on the next line. GitHub runs a `run:` block under `bash -e` (the step's own `set -uo pipefail` does not clear `-e`), so the gate's by-design exit 4 (`batching`, fewer than `BATCH_FLOOR_ROWS` owed) ended the step before `batch=$?` ran, and `status=batching` never reached `GITHUB_OUTPUT`. Job 121376503388 at main d181d014 ended with exit code 4 right after `BATCH WAIT: 5 row(s) below the floor of 8`. The bug came in with #2836 (R10-FLOW-RECORD-PITCH).

The fix, in `.github/workflows/nightly.yml`'s record-autofix step "Write the rows and push the record branch": `batch=0`, then the call with `|| batch=$?`. Exit 0 still goes on to `--apply`, 4 still ends `batching`, and any other nonzero still ends `skip-batch-gate`. I took the `||` form over an `if ...; then batch=0; else batch=$?; fi` wrapper because it changes one line and keeps the three-way branch below it untouched. Both forms are exempt from `-e`.

Hotfix ruling (orchestrator): this merges on a green gate with the review afterwards. A delta-size reviewer is pooled at this head for `merge_pr.sh`'s verdict.

## Head

`b68601e06b6cf8bc50c1611127a4546b8d45beba` merges main `b281d03` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`2c7016ce6745d19336bb2f90a7f6fb04a37ceac6` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2848.md`. The authored code head is `44e3668427d4932abfaee7f4e83d61bb7babf98f`.

`9c9c749655d59b564eaada5720171b263960fb59` merges origin/main `f6784210c` into the authored code head `44e3668427d4932abfaee7f4e83d61bb7babf98f` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

44e3668427d4932abfaee7f4e83d61bb7babf98f, on origin/main d181d014a0d9681b4f4ca217a540f7bd1bf932a2 (main tip when measured, taken with `date -u` at 2026-10-26T03:31:00Z).

## Mutation proof

The control is a new check in `tests/entities.py`, beside the existing record-autofix wiring pin: "nightly.yml's batch gate, run under the runner's `bash -e`". It cuts the gate's lines out of the real job, from the `fi` that closes the previous block through the `skip-batch-gate` line. It runs them in a one-try loop under `bash --noprofile --norc -eo pipefail` plus the step's own `set -uo pipefail`, with `python3` stubbed as a shell function that exits 0, 4, 1 and 2. It wants `{0: apply, 4: batching, 1: skip-batch-gate, 2: skip-batch-gate}`.

Mutants: the gate's lines from mutated copies of the fixed `nightly.yml`, run through the same `_raf_batch_outcomes`:
- m1, delete `batch=0`: `{0: 'died:1', 4: 'batching', 1: 'skip-batch-gate', 2: 'skip-batch-gate'}`. Killed: `-u` aborts on the unset variable when exit is 0.
- m2, revert to the base form (bare call, `batch=$?` on the next line): `{0: 'apply', 4: 'died:4', 1: 'died:1', 2: 'died:2'}`. Killed.
- m3, drop `|| batch=$?` only: `{0: 'apply', 4: 'died:4', 1: 'died:1', 2: 'died:2'}`. Killed.

3 mutants, 3 killed, 0 survivors. Full `tests/entities.py` at the base, which is m2 in the real tree: the new check reads `FAIL ... [got {0: 'apply', 4: 'died:4', 1: 'died:1', 2: 'died:2'}, ...]`. At the head it reads `ok`.

## Null control

The check has a second, built-in null control: "and the run reads the job's own lines". It re-bares the call in the real job text and must see exit 4 kill the step (`died:4`). It passes at both base and head, so the harness is the runner's shell and not one that swallows `-e`.

Unmodified tree (origin/main d181d014): the gate dies with the stub's own code on every nonzero exit (`4: died:4`), the same exit code 4 that job 121376503388 recorded.

Two other `tests/entities.py` checks fail locally at both base and head: `gate-sweep.yml: on CI's completion ...` and `graders-head-copy's delivery_status step ...`. The cause is the seat container's `BASH_ENV` (a toolchain profile that puts the venv back first on PATH in every non-interactive bash), which defeats those checks' PATH stubs. The new check stubs with a shell function, which takes precedence over PATH, and passes no `BASH_ENV`, so this does not affect it. These two are not this diff's and are not red on CI at main.

## Figures

- Gate outcomes at head vs base: `PYTHONPATH=tests/hastub python3 tests/entities.py`. Base `3 of 2450 ENTITY CHECKS FAILED` (the new check plus the two local `BASH_ENV` ones above). Head `2 of 2450 ENTITY CHECKS FAILED` (the two local ones only). The new check and its null control read `ok` at head.
- Same-class sweep: `grep -nE '\$\?' .github/workflows/*.yml` at head returns 7 lines, each with its verdict:
  - `nightly.yml` (record-autofix, comment line): `# The \`|| batch=$?\` is load-bearing`. A comment, no capture.
  - `nightly.yml` (record-autofix gate): `... --event "$EVENT" || batch=$?`. Closed in this diff.
  - `nightly.yml` (pitch step): `pitch=$?`. Safe: it sits in the `else` arm of `if python3 -I tools/audit/seat/record_row.py --pitch-check ...`, and `$?` there is the condition's exit, which `-e` does not see.
  - `nightly.yml` (merge step, comment line): `# A CONDITION, not a bare \`guard --require-green; rc=$?\``. A comment, no capture.
  - `nightly.yml` (merge step): `if guard --require-green; then rc=0; else rc=$?; fi`. Safe: a condition, already pinned by `_raf_merge_pinned`'s `_RAF_BARE_GREEN`.
  - `tests.yml` graders-head-copy: `base_rc=$?`. Safe: inside `set +e` ... `set -e`.
  - `tests.yml` graders-head-copy: `head_rc=$?`. Safe: inside `set +e` ... `set -e`.
- Sweep null control: the same grep over `git show origin/main:.github/workflows/nightly.yml` returns the bare `batch=$?` line (the defect) plus the three nightly lines above. So the grep does find the bare form when it is there.
- #2836's workflow steps: `git show --stat c24adf589 6b1aa629f`. The only workflow it touches is `.github/workflows/nightly.yml`, which the sweep covers.
- `PIPESTATUS` captures: `grep -cE 'PIPESTATUS' .github/workflows/*.yml` reads 0 in every workflow.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL`, because `.github/workflows/nightly.yml changes the gate itself`. CI runs the rest. Locally I ran `tests/entities.py` and run.sh's `run_always` scripts: `tests/env_drift.py --claims-only` ok, `tests/closure.py selftest` `ALL 117 closure shrink pins PASSED`, `tests/layout.py` ok, `tests/harness_headers.py` `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`Nightly / record-autofix` (check-run `record-autofix`, workflow `Nightly`, job 121376503388 at main d181d014, step "Write the rows and push the record branch", exit code 4). This diff fixes it. Cause, named rather than analysed: the batch tests pinned `record_row.py`'s exit codes (its `--self-test`) and the wiring as strings (`_raf_batch_gated`). Neither ran the YAML's lines under `-e`, which is where the defect lived. The cheaper detector is this PR's behavioural control, standing cost four `bash` subprocesses in `tests/entities.py`. A root-cause seat runs beside this fix (topic `r10-rca-hotfix-batch-errexit`) and owes the analysis, process state and countermeasure. None of that is done here.

- `prelude` (gate prelude, exit 3, `RATE-LIMITED reset_epoch=1792991224`, 04:52-05:07Z on 2026-10-26) was the installation rate limit, not this PR's code, and was rerun green. The cheaper detector is gate-sweep's RATE-LIMITED classification, standing cost zero extra calls. The countermeasure belongs to the root-cause seat R10-RCA-RATELIMIT-RECUR, which halves the record job's per-push API reads.

## Forward-carry

none

## Friction

none

