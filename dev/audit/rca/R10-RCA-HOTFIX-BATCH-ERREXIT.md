# R10-RCA-HOTFIX-BATCH-ERREXIT: record-autofix reads `batch=$?` after a bare call that `bash -e` has already ended

The root-cause seat for R10-HOTFIX-BATCH-ERREXIT (topic `r10-hotfix-batch-errexit`). It ran beside
that hotfix and not inside it (`dev/governance/roles/root-cause.md`); it edits no workflow. Every time
is UTC. Base: main `d181d014a`. Logs were read from the Actions API on 2026-10-26.

**Defect.** In `.github/workflows/nightly.yml`, job `record-autofix`, step "Write the rows and push the
record branch", the batch gate is:

    python3 -I tools/audit/seat/record_row.py \
      --batch-due --plan-file "$RUNNER_TEMP/plan.json" --event "$EVENT"
    batch=$?
    if [ "$batch" = 4 ]; then status="batching"; break; fi

`--batch-due` exits 4 (`WAIT_RC`) on purpose while a push owes fewer than the floor of 8 rows. The step
has no `shell:`, so GitHub runs it as `/usr/bin/bash -e {0}` (the log prints it), and the step's own
`set -uo pipefail` does not clear `-e`. Exit 4 therefore ends the step before `batch=$?`. Nothing is
written to `GITHUB_OUTPUT`, and the report step then fails with "the record step did not run".

## 1. Cause, reproduced

- **On main.** Two push runs of Nightly failed this way, the first two that reached the gate:
  - run 40262054722 (merge of #2845), job 121376331566, 03:05:02: `BATCH WAIT: 4 row(s) below the floor of 8 ...`, then `Process completed with exit code 4`.
  - run 40262110887 (merge of #2824, `d181d014a`), job 121376503388, 03:06:32: `BATCH WAIT: 5 row(s) ...`, then exit code 4.

  The merge run of #2836 itself (run 40259634492, job 121368987817) is green. It reported `RECORD AUTOFIX: held`, so an open record pull request skipped the loop before the gate ran.
- **The premise, executed.** The step body (lines 741-751 at `d181d014a`) was run with `record_row.py` stubbed to print the wait line and return 4:
  - `bash -e repro.sh` prints the wait line and exits **4**. No `status=` line.
  - `bash repro.sh` (no `-e`) prints `status=batching` and exits 0.
  - With the hotfix line, `batch=0; record_row.py --batch-due ... || batch=$?`, `bash -e` prints `status=batching` and exits 0.

  A condition (the left side of `||`, or an `if`) is exempt from `-e`, so the exit reaches the read.
- **Which side moved.** `git log -L` on the gate gives one commit, `c24adf589` (#2836 round 1, R10-FLOW-RECORD-PITCH). The gate and its bare call were born together. `record_row.py`'s exit 4 is the design, and its CLI mapping is pinned in both directions (round 2, `6b1aa629f`: the `cli: --batch-due exits WAIT_RC ...` arm, killed by mutants `record_row-2` and `record_row-4`). The script is right. The YAML that reads its exit is wrong. The orchestrator's hypothesis holds: the tests pinned the exit codes, and no check modelled the shell that reads them.
- **What else the cause reaches.** The same PR wrote the pitch gate, 290 lines further down the same file, as a condition (`if python3 ... --pitch-check ...; then :; else pitch=$?`). That one is correct. So did `bc2ad6964`'s `if guard --require-green; then rc=0; else rc=$?; fi`. The author knew the idiom and missed it at one site. Section 3 covers the rest of the tree.

## 2. Process state: (c), followed and not producing the intended result

Three processes covered this site. All three ran, and each passed or approved:

1. **A barrier for this exact hazard existed.** After instance I2 (below), `bc2ad6964` (#2203) added `_RAF_BARE_GREEN` to `tests/entities.py`. Its comment reads "GitHub runs a `run:` block under `bash -e`, so a BARE `guard --require-green; rc=$?` ends the STEP with the guard's own exit". Its unit is the regex `^\s*guard --require-green\b`, one literal call in one job. The new call `record_row.py --batch-due` is outside that unit. The check ran on #2836 and passed.
2. **#2836 added a wiring pin, `_raf_batch_gated`.** It asserts that the gate sits between plan and apply, that the job passes `EVENT`, and that the literal line `if [ "$batch" = 4 ]; then status="batching"; break; fi` is present. It checks text order, not shell semantics, so it is green on the defect. It also reads the dead line as evidence that the wait is wired.
3. **The executed-step harness models the wrong shell.** `tests/entities.py`'s `_train_hold_status` executes the sibling automerge step's `run:` text. It is the harness #2836's body cites as "the step's harness, executed" for the pitch. It runs that text with `subprocess.run(["bash", "-c", _HOLD_RUN], ...)` (`tests/entities.py:27925`), which has no `-e`. Even an executed harness of the record step written in that shape would have printed `status=batching` on the defect. No harness executes the record step.

On the review side: fix review `merge 54d588b56` (comment 6405493591) re-ran the seat-selftest mutants (`RESULT survivors=0`) and read the nightly.yml delta. The body's `## Red checks` answers nightly-status, delivery-status and ci-ratchet. None of them could see this site: record-autofix is `main`-only (`github.ref == 'refs/heads/main'`), so no PR head ever runs it.

**Why not (a):** a check for this hazard existed (item 1). `root-cause.md` §2 says an instance of a barriered shape is not (a) because its shape is new. **Why not (b):** no rule or brief line required the condition form at new call sites. The one written guidance is item 1's comment, scoped to `--require-green`. `fixer.md:21`'s `set -e` line concerns mutants, not workflow steps. Every listed step ran. **Why not (d):** nothing changed under the process. GitHub's default shell was `bash -e` at I2 and still is. **Recording this as (b), "write the capture as a condition", would be the common error.** The author already does that at two sites. The unit is what failed, so the countermeasure widens the unit.

## 3. Class search

**The `$?`-read shape, every run block.** `grep -n -E '=\$\?|case "?\$\?|\$\? ' .github/workflows/*.yml` at `d181d014a`:

| site | form | verdict |
|---|---|---|
| `nightly.yml:749` `batch=$?` | bare call, then read | **defect** (this one) |
| `nightly.yml:1035` `pitch=$?` | `if cmd; then :; else pitch=$?` | safe, a condition |
| `nightly.yml:1049` `rc=$?` | `if guard --require-green; then rc=0; else rc=$?; fi` | safe, a condition (I2's fix) |
| `tests.yml:1539` `base_rc=$?` | between `set +e` and `set -e` | safe |
| `tests.yml:1544` `head_rc=$?` | between `set +e` and `set -e` | safe |

There is no `if ! cmd; then ... $?` form and no `case $?` form. Shells: 5 workflow steps declare `shell: bash` (`nightly.yml:109,120,185`, `tests.yml:1045,1148`), and so do the 4 steps of `.github/actions/nightly-ha/action.yml`. That is `-eo pipefail`. Every other `run:` takes the default `bash -e`. No workflow sets `defaults.run.shell`, and none declares a non-errexit shell. `dev/audit/harnesses/r10_errexit_capture.py` makes this table mechanical: 260 errexit run blocks, 5 `$?` reads, 1 hit.

**Prior instances (measured).** `git log --all -i -E --grep='errexit|set -e|bash -e'` gives 8 non-dispatch commits. Read one by one:

| id | shape | landed / fixed | in class |
|---|---|---|---|
| I1 `dc66cc878` (#1599), fixed by `718c94c84` (#2049) | mutation pin step: `... \| tee pin-run.txt` under `-e`+`pipefail`, a refusing pin run ended the step before `measurement()` graded it | 2026-09-25 08:22 to 2026-10-08 06:40, 12.9 d | yes, a broad errexit instance; no `$?` read |
| I2 `47add7334` (#2029), fixed by `bc2ad6964` (#2203) | record-autofix: `guard --require-green; rc=$?` | 2026-10-08 05:07 to 2026-10-14 12:39, 6.3 d | yes, the `$?` shape |
| I3 `c24adf589` (#2836, merged `28800999b`) | record-autofix: `--batch-due` then `batch=$?` | 2026-10-26 02:32 to open | yes, the `$?` shape (this one) |
| `0051f1960`, `6194234bc`, `e0b501f77`, `c06a92f6b` | `set -e`/`set +e` used deliberately, fail-closed by design | | no |
| `4fd49ab07`, `e1af66910` (#2709) | errexit in a seat script's exit remap, and a mutant equivalence under `set -e` | | adjacent: not a workflow step |

`RELEASE_NOTES.md` has 0 lines that match `errexit|set -e|bash -e`. **This is the 3rd instance** of a workflow step whose meaningful nonzero exit is ended by errexit before the step's own code reads it. It is the **2nd of the `$?`-read shape**, in the same job, 18 days after the first. `dev/audit/config/bugclasses.json` has no class with this mechanism (a scan of each class's JSON for `errexit|shell|bash|exit code` matched none).

## 4. Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, wall-clock.

- **cost(countermeasure, recurring).** `scan()` over the whole tree took 0.25 to 0.54 s across 5 in-process runs; 0.375 s as a CLI. Upper bound: 0.54 s on every `ci.yml` run, at 113 runs/day (measured by R10-RCA-CI-RATCHET-RUN-NAME §3 for 2026-10-24), which is **61 runner-s/day**. A scoped gate runs it only on diffs reaching `.github/`, so this overstates it.
- **P(recurrence).** Measured class frequency: 3 instances landed in the 31 days from 2026-09-25 to 2026-10-26, 2 of them of the shape this check catches. That is **0.065/day** catchable, 0.097/day in the broad class.
- **Break-even.** 61 s/day < cost(defect) x 0.065/day holds when cost(defect) > **940 s (16 min)** per occurrence.
- **cost(defect).** Lower bounds, measured. I2 left record automerge broken for 6.3 days. I1 left the mutation pin measurement ungraded for 12.9 days. I3 has been red on every below-floor push since 03:05:02, and it has already cost a dispatched hotfix seat, its review and this seat. Any one hotfix cycle (fix, fix review, merge) exceeds 16 minutes. The two closed instances exceed it by more than 500x.

**Verdict: the cost test passes, by a wide margin, for the check below.** The ratchet cost is 0: `tests/structure.py` measures `custom_components/heatpump_optimizer/**` only, and `tests/structure_budgets.json` does not move. No policy file changes.

## 5. Countermeasure (proposed; maps to state (c): widen the unit)

**A. Replace `_RAF_BARE_GREEN`'s one-call unit with a tree-wide check.** It covers every `run:` block whose shell is errexit (default, `bash`, `sh`). A `$?` read whose producer is a bare simple command is refused. It lands as a `tests/entities.py` check (the home of the barrier it generalises), importing the logic of `dev/audit/harnesses/r10_errexit_capture.py`, or as that file promoted under `tools/ci/`. It must land **after** the hotfix, or main reddens on I3 itself. Demonstrated with the harness, all runs at `d181d014a`:

| run | result |
|---|---|
| main `d181d014a` (the defect) | **FAILS**: `HIT nightly.yml job=record-autofix step='Write the rows and push the record branch'`, `hits=1`, exit 1 |
| scratch copy with the hotfix line (`batch=0` + `... \|\| batch=$?`) | **PASSES**: `blocks=260 reads=5 hits=0`, exit 0 |
| null control, healthy tree: the hotfixed copy | still reads all 5 `$?` sites (`reads=5`), so a green result is not a skip |
| null control, empty `.github/` | **REFUSES**, exit 2, `blocks=0 reads=0` |
| mutant: `nightly.yml:1049` back to bare `guard --require-green; rc=$?` | FAILS, `hits=1` (the old barrier's case is inside the new unit) |
| backtest at `bc2ad6964^` (I2 live) | FAILS, `hits=1` on `tests.yml`'s `guard --require-green; rc=$?` |
| backtest at `718c94c84^` (I1 live) | passes, `hits=0`: **I1's pipeline shape is outside this unit** (see 6) |
| `--selftest` | 9 checks, 0 failed (bare, same-line, `case $?`, `\|\|`-capture, `if/else`, `else` line, `set +e`, continuation, and the shell arm: `shell: python` is skipped) |

**B. Execute step bodies under the shell GitHub uses.** `_train_hold_status` runs `bash -c`. Make it `bash -e -c` (`tests/entities.py:27925`), and give any new executed-step harness the same rule. Its standing cost is 0. It closes item 3 of section 2. Not demonstrated here: it changes an existing check, which is the countermeasure fixer's to mutation-prove.

Both A and B are code, not policy. Neither changes what a seat must do, so neither needs the owner's approval as policy. Placing them is the orchestrator's call, as a carry to the fixer that lands A and B after R10-HOTFIX-BATCH-ERREXIT merges. **Class registration** (proposal, the judge's or orchestrator's to make): mint a class for "a workflow step's meaningful nonzero exit ended by errexit before the step reads it", with I1 to I3 as `non_round_instances`. Three instances in 31 days would meet the cross-round count if counted. Whether process incidents count toward the audit-class barrier rule is the owner's question, and this record does not answer it.

## 6. What I did not establish

- **I1's shape** (a later step reads a file that a `-e`/`pipefail` pipeline was meant to finish writing) is not caught by A. A general detector would execute every step with stubbed commands. I did not build or cost one: commands with side effects (git push, curl) need per-step stubs, and that cost is open.
- **I3's wall-clock** is open until the hotfix merges. The figures above are lower bounds.
- I did not measure seat time for the I3 hotfix cycle.

## 7. Issue draft (for the orchestrator to post on the hotfix's issue or PR)

> **Root cause** (`dev/audit/rca/R10-RCA-HOTFIX-BATCH-ERREXIT.md`)
>
> - **Cause:** `nightly.yml` record-autofix reads `batch=$?` after a bare `record_row.py --batch-due`. The step runs under GitHub's default `bash -e`, so the designed exit 4 ends the step before the read (jobs 121376331566 and 121376503388, exit code 4). Reproduced: `bash -e` on the step body exits 4; with `|| batch=$?` it reaches `status=batching`.
> - **State (c):** a barrier for the same hazard existed (`_RAF_BARE_GREEN`, `bc2ad6964`), but its unit is one literal call, `guard --require-green`. #2836's own pin (`_raf_batch_gated`) asserts the text of the dead line. The executed-step harness runs `bash -c` without `-e`. All three ran and passed, and record-autofix is `main`-only, so no PR head exercised it.
> - **Class:** the 3rd workflow-step errexit instance in 31 days (I1 `dc66cc878` to `718c94c84`, I2 `47add7334` to `bc2ad6964`, I3 `c24adf589`), and the 2nd of the `$?` shape. A grep over every run block finds 5 `$?` reads, 1 defective.
> - **Cost test:** 61 runner-s/day (0.54 s x 113 runs) < cost(defect) x 0.065/day whenever a defect costs more than 16 min. I2 cost 6.3 days. Passes.
> - **Countermeasure (proposed, after the hotfix merges):** (A) a tree-wide `$?`-after-bare-call check that replaces `_RAF_BARE_GREEN`. Shown failing on `d181d014a`, passing with the hotfix line, refusing an empty tree, and catching I2 in a backtest; harness `dev/audit/harnesses/r10_errexit_capture.py`. (B) `_train_hold_status` executes step text under `bash -e -c`. I1's pipeline shape stays uncovered.
