The root-cause record for R10-HOTFIX-BATCH-ERREXIT. It ran beside the hotfix and not inside it: no workflow is edited. The change is docs plus one instrument: `dev/audit/rca/R10-RCA-HOTFIX-BATCH-ERREXIT.md`, its `_rca` row in `dev/audit/config/bugclasses.json`, the read-only harness `dev/audit/harnesses/r10_errexit_capture.py`, and that harness's INERT READS entry in `tests/closures.json`.

**Cause, reproduced.** `nightly.yml`'s record-autofix reads `batch=$?` after a bare `record_row.py --batch-due`. The step runs under GitHub's default `/usr/bin/bash -e {0}`, so the designed exit 4 ends the step before the read. This turned jobs 121376331566 and 121376503388 red with exit code 4. The step body under `bash -e` with a stub returning 4 exits 4. With `|| batch=$?` it prints `status=batching`. `record_row.py`'s exit mapping is right and pinned (`6b1aa629f`). The YAML is what is wrong.

**State (c).** A barrier for this exact hazard, `_RAF_BARE_GREEN` (`bc2ad6964`), ran and passed: its unit is one literal call, `guard --require-green`. #2836's `_raf_batch_gated` pins the dead line's text. The executed-step harness `_train_hold_status` runs `bash -c` with no `-e`. The job is `main`-only, so no PR head ran it. It is not (b): the same PR wrote `--pitch-check` as a condition.

**Class.** This is the 3rd workflow-step errexit instance in 31 days: I1 `dc66cc878` (fixed by `718c94c84`), I2 `47add7334` (fixed by `bc2ad6964`), and I3 `c24adf589`. It is the 2nd of the `$?` shape. Of the 5 `$?` reads across every run block, 1 is defective.

**Cost test: passes.** 0.54 s x 113 runs/day = 61 runner-s/day, against a break-even of 940 s per defect at 0.065/day measured. I2 alone cost 6.3 days. **Countermeasure (proposed, not landed):** (A) a tree-wide `$?`-after-bare-call check replacing `_RAF_BARE_GREEN`, which must land with or after the hotfix line; (B) executed step harnesses run under `bash -e -c`.

## Head

a1c8d7f0c6cb6779dfbbb8f572bd5a39c1804e3c

It is two commits on `origin/main` `d181d014a0d9681b4f4ca217a540f7bd1bf932a2`: the record, and the closures classification `ci_predict.py --apply-inert` wrote. API figures were read on 2026-10-26 between 03:20Z and 04:10Z.

## Mutation proof

- The harness `--selftest` printed `selftest: 9 checks, 0 failed`. Each case expecting 1 hit (bare call, same line, `case $?`, continuation, shell arm) depends on the `hits.append` line, so deleting it fails 5 of them.
- Countermeasure A on the defect: `python3 -I dev/audit/harnesses/r10_errexit_capture.py` at this head printed `HIT .github/workflows/nightly.yml job=record-autofix step='Write the rows and push the record branch'` and `RESULT hits=1`, exit 1.
- With the hotfix line applied to a scratch `git archive` copy of `d181d014a` (`batch=0` and `--batch-due ... || batch=$?`; never landed), `--root <copy>` printed `RESULT hits=0`, exit 0.
- Mutant: `nightly.yml:1049` reverted to a bare `guard --require-green; rc=$?` printed `hits=1`. Backtest at `bc2ad6964^` (I2 live) printed `hits=1` on `tests.yml`.

## Null control

- On the hotfixed copy the harness still prints `RESULT reads=5`, so its green comes from reading every site, not from skipping them. An empty `.github/` prints `REFUSED` with `blocks=0 reads=0`, exit 2.
- Backtest at `718c94c84^` (I1 live) printed `hits=0`: I1's pipeline shape is outside the check's unit. Record section 6 says so.
- The scoped gate (`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`) printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out` and named `tests/entities.py`. With `PYTHONPATH=tests/hastub` it printed `2 of 2448 ENTITY CHECKS FAILED` at this head, and the same `2 of 2448` with the same two names in a detached worktree of `origin/main` `d181d014a`: the `gate-sweep.yml ... (U0c)` check and `graders-head-copy's delivery_status step ...`. Neither reads a file this diff touches. `run_always` scripts: `tests/closure.py selftest` (`ALL 117 closure shrink pins PASSED`), `tests/layout.py` (`ok`), `tests/harness_headers.py` (`ALL 112 HARNESS HEADER CHECKS PASSED`), and `tests/structure.py` (`STRUCTURE RATCHET PASSED`).
- `python3 tools/audit/fold_ledger.py check` printed `0 violation(s)` with 122 rca entries (121 at the base).
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` predicted no red.

## Figures

- `.github` run blocks, `$?` reads and hits: `python3 -I dev/audit/harnesses/r10_errexit_capture.py`, printed at `d181d014a`.
- The 5 `$?` sites: `grep -n -E '=\$\?|case "?\$\?|\$\? ' .github/workflows/*.yml`.
- Prior instances: `git log --all -i -E --grep='errexit|set -e|bash -e'`, each read by hand (record section 3). Landing times come from the first first-parent commit of `origin/main` that contains each commit. `grep -c -i -E 'errexit|set -e|bash -e' RELEASE_NOTES.md` printed 0.
- Red runs: Actions API, Nightly push runs 40262054722 and 40262110887 (`failure`, record-autofix exit code 4) and 40259634492 (`success`, `RECORD AUTOFIX: held`).
- Countermeasure cost: `scan()` timed in-process 5 times, 0.25 to 0.54 s. 113 `ci.yml` runs/day is R10-RCA-CI-RATCHET-RUN-NAME's measurement for 2026-10-24 and was not re-taken.

## Red checks

none

## Forward-carry

- Countermeasure A and B, record section 5. A: a tree-wide check over every errexit `run:` block that refuses a `$?` read whose producer is a bare call, replacing `_RAF_BARE_GREEN`, with `dev/audit/harnesses/r10_errexit_capture.py` as the reference logic and its demonstrations. It fails on main until the hotfix line is in, so it lands in the hotfix's PR or after it merges. B: `tests/entities.py:27925` executes step text under `bash -e -c`. Also there, the class proposal: I1 to I3 as `non_round_instances` of a new class, the judge's or orchestrator's to mint. Carry: R10-HOTFIX-BATCH-ERREXIT

## Friction

- brief: stale: the brief names `dev/programme/rca` as a possible records directory. Records live in `dev/audit/rca/`, which `defect-root-cause.md` names. Carry: dismissed: brief wording only
