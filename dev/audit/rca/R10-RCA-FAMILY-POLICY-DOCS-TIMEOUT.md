# R10-RCA-FAMILY-POLICY-DOCS-TIMEOUT: field coverage runs three minutes inside a five-minute job

Round-end family analysis (loop card L8). Measured at `origin/main` `a39627da59` on
2026-11-15. Lands no code.

## 1. Instances

From the round-10 orchestrator's sweep log, family "policy-docs-field-coverage-slow":
- line 2605: #3451 at `93ba2271`, `governance / policy-docs` cancelled at its 5-minute timeout
  (run 43688486622); the required `gate` read red, the delta review returned "blocked ci-red";
- line 2606: main `b046b22d`, the same job timed out (run 43691296618, job 132742498619); the
  step "Refuse a governance check input field no check reads" ran 3 min 17 s;
- line 2606: the stamp commit `13cbe48d`, the step ran 3 min 7 s and the job passed at 4 min
  58 s, two seconds inside its budget.

Two of three turned the required `gate` red (`policy-docs` is in the `governance` group of
`tools/ci/prelude.py:95`, which the gate judges). Earlier `policy-docs` cancellations on main
(lines 1671, 1694, 2026-11-13) printed no error line and are not counted here: they may be the
same timeout, unproven.

## 2. Named cause

The step (`.github/workflows/governance.yml:242-256`) is skipped, "no input changed since
$SINCE", unless the diff touches one of its listed inputs; when it runs it executes `node
tools/policy/field_coverage.mjs`, which costs about three minutes of CPU. Measured here: 170 s
wall, 196 s user CPU, rc 0, at load 7-11 on an 8-core Mac. The job's `timeout-minutes: 5`
(`governance.yml:63`) dates from 2026-09-07 (#608, when the job was a linter); the other steps
of the job take most of the remaining two minutes. Each instance's diff touched a listed input:
the stamp changed `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`, #3593
`tests/structure_budgets.json`, #3451 `dev/governance/config/policy_budgets.json` (`git diff
--stat <c>^1 <c> -- <the step's input list>` for each).

## 3. Process state: (d)

The job's budget was right for the job it was written for; its precondition, the job's total
work, changed underneath it as the field-coverage check grew (32 commits to
`tools/policy/field_coverage.mjs`, `git log --oneline -- tools/policy/field_coverage.mjs | wc
-l`). Nothing re-read the budget when the step grew. Not (b): no instruction was skipped.

## 4. Class reach

Every fixed `timeout-minutes` in a workflow has this shape; `instrument-self-tests` met it in
round 10 (R10-PROCESS-SLIM carry 1, cancelled at 30:03 min against 30, since raised:
`governance.yml:297` reads `push 60 || 30`). `governance.yml` has three more jobs at 10 minutes
(lines 1592, 1710, 1876); none timed out in the s14 log (`grep -n -i "timed out\|timeout"` on it
names only `policy-docs` and `instrument-self-tests`).

## 5. Cost test

- cost(defect): each timeout costs a re-run of the job (about 5 runner minutes and a turn), and
  on a pull request a blocked verdict round (#3451: the verdict was "blocked ci-red" and a
  re-issue followed, about 50 min from 07:50Z to the merge verdict re-read at 08:32Z, lines
  2605-2610); on main it leaves the required gate red until the re-run.
- P(recurrence): the step runs on every diff touching its inputs, which includes every stamp
  (the card's version string) and every budget re-record; three of three such runs on
  2026-11-15 ended at or within two seconds of the bound.
- cost(countermeasure, recurring): raising `policy-docs` to `timeout-minutes: 10` costs zero
  seconds on a run that finishes; it lengthens only a hung run, by five minutes.

Passes.

## 6. Countermeasure

`policy-docs` `timeout-minutes: 5` to `10` in `.github/workflows/governance.yml`, with a comment
naming the measured step cost. Code-owned (tvofi's review). Admissible under the freeze: it
fixes the required gate's red on main. Group R11-HOTFIX-POLICY-DOCS-TIMEOUT (triage
`dev/programme/triage/r10-round-end.md#P786`). Demonstration owed by the fixer: a
`workflow_dispatch` of the job at a head whose diff touches a listed input passes at the new
bound (the same run timed out at the old one); null control, a diff touching no input still
prints "skipped". Not chosen: making field coverage incremental (a self-repair, L2's second rung)
is sounder in principle but unmeasured and larger; it is the follow-up if the step passes five
minutes alone.
