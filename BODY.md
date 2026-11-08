R10-RCA-COP-UNMEASURED: the root-cause seat for R10-HOTFIX-COP-UNMEASURED (#3297).

- **Trigger:** 1. The defect reached v4.0.0 through v7.1.5.
- **Scope:** this seat ran beside the hotfix fixer. It edits nothing under
  `custom_components/` and does not touch #3297's branch.

The product is `dev/audit/rca/R10-RCA-COP-UNMEASURED.md`, cited from
`dev/audit/config/bugclasses.json` `_rca["R10-RCA-COP-UNMEASURED"]`. Its
reproduction and detector is `dev/audit/harnesses/r10_rca_cop_unmeasured.py`.
The four parts follow.

- **Named cause.** One COP sample per interval serves both a learner (the
  COP scale) and two graders: the last measured COP and the COP health watch.
  The sample carries no provenance.
  - With no heat input, `flow_meter.cop_evidence` infers the COP as the model
    times ask over draw.
  - A vendor-estimated thermal power entity was read as metered heat.
  - Either way, the watch's bands and `machine_score` compared the model with
    itself.
  - By `git log`, the inference came first, named "measured" from
    `df7db8215` (PR #11, v2.8.0). The watch was built onto it in `a63b576cd`
    (PR #50, v4.0.0) and had no metered input until v7.0.5. The watch did not
    degrade: it was born on an inference.
- **Process state: (c).** Three processes read this seam and passed it.
  Each judged whether the sample was clean. None traced where its inputs came
  from.
  - `D1.md` hunts "fabricated data as measured" but has no method step that
    reaches it.
  - The round-10 P5 sweep (`dev/audit/rounds/round10/sweep-P5.md:37`) cleared
    `_cop_health_cusum` as "an empirical per-bucket, per-curve baseline ...
    not a model residual".
  - STUDY R10-IDENT Q2 (#2262) found "COP is not observable without a heat
    meter". The R10-COP-GATE group carried it as a draw-follows-plan state.
    Its null control was "an install whose draw does follow the plan still
    reaches a COP model": the learner only, never the graders.
  - Not (a), not (b) and not (d): the reasons are in the document's
    section 2.
- **Cost test.**
  - P = 0.1 per round, estimated from one release escape over ten rounds
    (78 days). No class frequency exists.
  - cost(defect) is at least 12 h of fix wall-clock, plus an RCA seat and 73
    days of exposure.
  - The expected cost is 1.2 to 1.5 h per round.
  - A D1 provenance step costs about 10 min a round, covering only the
    `measured` / `observed` names a round adds (23 today), so it **passes**.
  - A CI-wide provenance type on every reading **fails**: it would rewrite
    the readers, and #3297 already concentrates the decision in
    `InstallCapability.cop_measured`.
- **Countermeasure.**
  - **Built:** the harness's `--check` is the detector. It exits 1 on v7.1.5
    and on main, 0 at the fix head, 2 on a skip tree, and 1 on each of two
    single-door trees. It is hand-run and wired into no gate: #3297's own
    `tests/features.py` section is the instance's CI barrier, and a second
    copy would pin the same line twice.
  - **Proposed to the owner, not landed:** the D1 step "Measured means
    measured". It is quoted in the document's section 5, with its planning
    counterpart. Both are policy, so both wait for the owner's approval.
  - **Refused, and recorded:** the static provenance check.
- **Class.** No class is minted. The shape has one instance on the register,
  closed through one function.
  - The class search is in the document's section 3. It traced 23 names and
    the sample's readers.
  - It found one more self-referential seam, `_fold_capacity_envelope`'s
    no-heat branch. That is a learner, off by default, and kept by the owner's
    ruling of 2026-11-07 that no learner is gated.
  - The nearest classes are N-unmetered-reference and P11.
- **No issue comment.** `defect-root-cause.md` asks for a Root cause section
  on the defect's issue. This hotfix has no issue, and this seat's brief
  forbids comments. If the orchestrator opens one, the section is state (c),
  the cost-test numbers above, and the document's path, all in the
  document's section 6.
- **Owner decision owed.** The D1 step and its planning counterpart are
  policy. The register's `_rca["R10-RCA-COP-UNMEASURED"].parts_missing`
  holds both, `status` `proposed`, until the owner rules. Neither is landed
  here.

## Head

The head is `b8fba2c8d5ab03067539c7e8d06e369f85162c31`. The code was measured at `11fb790082eff5436cb7e63e27ecea837a779abd`; `b8fba2c8d` adds only a merge of origin/main (`6e459e0e6`, which brought in the v7.1.6 stamp) and the delivery row `dev/programme/delivery/3316.md` (`b8fba2c8d record: the delivery row for #3316`). The diff against the merge base still touches the same five paths under `dev/` and `tests/closures.json`, nothing under `custom_components/`.

- The prepr run below was at `11fb79008`, on origin/main `73365699a`. Main has since moved; per the owner's ruling of 2026-11-07 it is not re-run for that.
- `git merge-tree --write-tree origin/main HEAD` at `b8fba2c8d` reports no conflict.

## Mutation proof

`tools/pr/prepr.sh`'s diff-mutant step lists no mutants, because
`tools/audit/seat/mutant_run.py` skips `dev/` (`SKIP_PREFIXES`) and every
added line is under `dev/audit/`. So the detector was mutated by hand. Each
mutant was applied alone to `dev/audit/harnesses/r10_rca_cop_unmeasured.py` and
restored.

The scored command requires all of these together:

- rc 0 on the fix head `2d010b091`;
- rc 1 on v7.1.5;
- rc 2 on the skip tree;
- rc 1 on door N and on door T.

Unmutated it passes. Each mutant below fails it, so 6 of 6 are killed:

| mutant | the edit |
|---|---|
| M-a | the verdict line becomes `return 0` |
| M-b | the skip guard becomes `if False:` |
| M-c | the null verdict is forced to `withheld` |
| M-d | the tuya verdict is forced to `withheld` |
| M-e | `null` is dropped from the verdict |
| M-f | the metered verdict is forced to `graded` |

M-c, M-d and M-e survived until the two door trees were added. At v7.1.5
both doors are open, so either verdict alone refuses.

## Null control

- **Metered control.** The metered install (plain ids, 6.0 kW of heat over
  2.0 kW of power) grades `{(2, False): [3.0, 1]}` on every tree, defective
  and fixed. So the detector can see a sample.
- **Skip control.** The fix head with `if measured:` turned to `if False:`
  withholds all three samples, and the detector exits 2, not 0. A tree that
  grades nothing does not pass.
- **No production change.** This branch changes nothing under
  `custom_components/`:
  `git diff --stat $(git merge-base origin/main HEAD)...HEAD` lists the
  `dev/audit/` paths and `tests/closures.json`. The closures change is one
  line: `tests/harness_headers.py` reads the new harness, written by
  `python3 tools/pr/ci_predict.py --base origin/main --apply-inert` after
  `ci predict` refused it. `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`
  prints `ALL 112 HARNESS HEADER CHECKS PASSED`.

## Figures

- **The detector across trees.** Command:
  `python3 -I dev/audit/harnesses/r10_rca_cop_unmeasured.py --check <checkout>`.
  Each checkout was a detached worktree.
  - v7.1.5 (`516ad1b6b`): `RESULT null=graded tuya=graded metered=graded`,
    rc 1, 0.62 s. The null band is `{(2, True): [2.5533587538536424, 1]}`,
    equal to `compute_cop_dhw(8, 48)`.
  - origin/main `73365699a`: the same, rc 1, 0.68 s.
  - #3297 head `2d010b091`: `null=withheld tuya=withheld metered=graded`,
    rc 0, 0.70 s.
  - Skip tree: rc 2.
  - Door N: `null=graded tuya=withheld`, rc 1.
  - Door T: `null=withheld tuya=graded`, rc 1.
- **Release reach.** `git tag --contains a63b576cd -l 'v*'` lists 134 tags,
  v4.0.0 (2026-08-26) to v7.1.5 (2026-11-07).
- **The name census.** `grep -ohiE '"[a-z_]*(measured|observed)[a-z_]*"' custom_components/heatpump_optimizer/*.py | sort -u | wc -l`
  prints 23.
- **The register.** `python3 tools/audit/fold_ledger.py check` prints
  `fold_ledger: 50 classes, 755 instances, 121 in-tree judge survivors (rounds [8, 10]), 138 rca entries`
  and `0 violation(s)`. On main it printed 137 rca entries.
- **Diff mutants.** The step lists 0 mutants, because `dev/` is skipped
  (`tools/audit/seat/mutant_run.py` `SKIP_PREFIXES`). Its wall time is under
  1 s and it reports 0 survivors. The hand mutation proof is above.
- **prepr.** `tools/pr/prepr.sh` with this body, `MUTANT_CMD` set to the hand-proof scorer above and `MUTANT_MAX=0`: `PRE-PR: 11fb790082eff5436cb7e63e27ecea837a779abd 000000000000000000000000000 rc=0`. Earlier runs refused, and each refusal was repaired: `ci predict` on the new harness (the `--apply-inert` line), the carry routing, and the body's path. `tests/entities.py` prints `3 of 2665 ENTITY CHECKS FAILED` both at this head and at origin/main `73365699a` (`PYTHONPATH=tests/hastub python3 tests/entities.py`): the coverage-job, release-ZIP and Pages-workflow checks, the same three #3297 found on this environment.

## Red checks

Every concluded red at `b8fba2c8d` is a **cancellation**, not a failure. The check-run list (read across all pages, re-read once for this take) has no `failure` conclusion on any test job except `gate`. No job log shows an assertion or an `UNDER-SCOPED` line. Each cancelled job ended at 08:47:24 to 08:47:40Z, inside one run, `CI code pr=3316` (run 42463804677), which itself concluded `cancelled` at 09:55:34Z. This diff is RCA documentation and one closures line; the cancellation belongs to the run, not to a test.

Each concluded red, by exact check name:

- `tests / fast (3.14)`: cancelled. The log ends at `start python3 tests/entities.py` then `The operation was canceled.` Not caused by this diff: the job was killed before a verdict.
- `tests / graders-head-copy`: cancelled, empty output. Not caused by this diff.
- `tests / lane-proofs`: cancelled, empty output. Not caused by this diff.
- `tests / closures`: cancelled, empty output. The closure recording is therefore neither shown stale nor shown under-scoped by this run. The diff's one closures change is the `tests/harness_headers.py` line in `tests/closures.json`, written by `ci_predict.py --apply-inert`. `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` passes locally (see Null control).
- `tests / closures-autofix`: cancelled. No bot commit exists beyond the head (`git ls-remote origin fix/r10-rca-cop-unmeasured` returns `b8fba2c8d`), so nothing was repaired and nothing was owed.
- `tests / claims-autofix`: cancelled, empty output. This branch claims nothing: `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are not in the diff (five paths, all under `dev/` plus `tests/closures.json`), so claim-file state cannot be the cause.
- `tests / coverage`: cancelled, empty output. The diff touches nothing under `custom_components/`, so no covered line changed. Not caused by this diff.
- `tests / coverage-ratchet`: cancelled, empty output. Same reason: no production line moved, and the ratchet never ran to a verdict.
- `tests / ci-ratchet`: cancelled, empty output. Not caused by this diff.
- `governance / instrument-self-tests`: cancelled, empty output. Not caused by this diff.
- `pr-contract / pr-contract`: both recorded runs are success. The earlier refusal named in the dispatch no longer stands.
- `gate`: failure in two completed entries (09:54:51Z to 09:55:33Z, and 10:00:08Z to 10:00:49Z). It is a required aggregate. It is red only because it lists the cancelled jobs above. It is a derived red, not an independent one. Two newer `gate` entries were `in_progress` (started 10:01:16Z) when read; their state is the next verdict.

Comparison with origin/main `6188936a8`: its check runs had not concluded when read (only `sweep` runs, all in progress, none failed). So an inherited-from-main cause is neither shown nor excluded; the evidence is that every red here is a cancellation with no failing assertion.

Cause and cheaper detector (`defect-root-cause.md`):

- Cause: the runs were cancelled while the test jobs were running, and the run ended `cancelled`. Why it was cancelled was not established here. I have no evidence that the diff caused it, and the workflow `concurrency` block is `cancel-in-progress: false`, so a newer push did not cancel it by that route.
- Cheaper detector: none applies. A cancellation is not a defect a local check can predict, and `tools/pr/prepr.sh` has no step for it. The failures a local check does predict (`ci predict`, the carry routing, the body path) were run and repaired before the handoff (see Figures, prepr).
- A re-run of the cancelled jobs at this head will show whether any fails. If one does, that failure is the finding, not this paragraph.

## Forward-carry

- **Doc claims #3297 leaves stale.** These are for the user-docs
  verification pass, once #3297 merges:
  - `README.md:614`: Observed COP "Needs measured power".
  - `docs/how-it-works.md:1240`: the watch "compares each measured COP".
  - The `ObservedCOPSensor` docstring: "derived from measured electrical
    input".

  At the fix head, observed COP needs a heat reading over a power reading,
  neither of them an estimate. Carry: #3139

## Friction

none
