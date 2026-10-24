# Review — PR #2485, round 2 (the budget-override withdrawal, body repaired)

Role: **fix reviewer**, round 2. Repository `tvofi/heatpump_optimizer`. **LOCAL seat only — no cloud.**
Read `dev/governance/roles/fix-review.md` first. You review the head, adversarially, with your own harness; a
round-1 verdict is evidence to check, never a conclusion to inherit.

## What you review

- PR **#2485**, head **`478cc27efd03d59d97899cff0d67f2e912ce7918`** (branch `fix/r10-stamp`), *stress: drop the
  inherited coverage_floor_override; the literal floors*.
- Bus nonce for your verdict: **`4162309a01046b05b79c53f3e102f4aa`** (`bus.sh dispatch 2485 <head> rev-2485-r2`).
- Detached worktree at the head:
  `git -C /Users/timmalmstrom/heatpump_optimizer fetch origin fix/r10-stamp` then
  `git -C /Users/timmalmstrom/heatpump_optimizer worktree add --detach /Users/timmalmstrom/hpo-seats/r10s3/rev-2485-r2 478cc27efd03d59d97899cff0d67f2e912ce7918`
- Scratch: `/Users/timmalmstrom/hpo-seats/r10s3/rev-2485-r2-ev` (create it).
- `export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH`.

## What round 1 said, and what the fixer did

Round 1 (`verdict/2485` at `edb8e615`, head `22ed5ed7`) returned
`Fix review: blocked 22ed5ed7… root-cause-unanswered`: `pr-contract` was red because the body's `## Forward-carry`
began `none.` and then carried items, a shape `carry_audit.py` refuses (`UNROUTED body item … (## Forward-carry)`),
and the body neither named nor answered that red.

The fixer's claims, each of which you verify rather than accept:
1. `## Forward-carry` is now a genuine `none.`; the #2445 stamp-time substance moved into the opening paragraph,
   which still records that the R10-STAMP roster entry carries it.
2. `## Red checks` now names `pr-contract` with a `defect-root-cause.md` answer: the cheaper detector is
   `carry_audit.py` (seconds, local, already wired into `prepr.sh`).
3. `## Head` now points at `478cc27e`.
4. `carry_audit.py check --body <body>` returns 0 findings at the head's body.
5. `prepr.sh` returns 0 at `478cc27e` (log `fix-stamp/logs/prepr2.log`; do not take the log as proof — re-run what
   is cheap, and for anything expensive say what you did instead).
6. Nothing substantive changed: the diff is still the `coverage_floor_override` withdrawal; floors `(40, 15)`,
   54 scenarios / 20 families at this head; `budget_raise_gate` says no raise is owed; claim files byte-identical.

## What you must establish at this head

- **The block is actually cleared.** Read the body as it is on the pull request *now* (`gh pr view 2485 --json body`),
  not the file the fixer kept, and run `carry_audit.py check` against it. Then read `pr-contract`'s check run at
  `478cc27e` through `/repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs` — a body edit fires the `edited`
  event, so the latest run must be at this head. **Do not use `gh pr checks`** (it hides red-then-green).
  If `pr-contract` has not yet re-run at this head when you look, say so and time it; it is a five-minute job.
- **Re-run round 1's substantive measurements yourself at `478cc27e`**: the direction (a withdrawal, not a raise),
  `lowers()`'s one-sidedness in `tests/stress.py`, the floors at this head, and the budget-raise gate.
- **§Response to the round-1 verdict.** Confirm every round-1 finding has an answer in the body or the tree. A
  finding answered only in a commit message is unanswered.
- **Any new red at this head** with its cause in the body's `## Red checks`, or an answer owed. `nightly-status`
  grading `main` is not this head's red — say so and move on.
- **Do not run the full local gate.** Cheap re-runs are yours; the suite is CI's at this head.

## Deliver, in the bus's shapes

```
bash /Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/bus.sh push-verdict 2485 <VERDICT.md> <evidence dir>
```

Verdict line: `Fix review: merge 478cc27efd03d59d97899cff0d67f2e912ce7918` or
`Fix review: blocked 478cc27efd03d59d97899cff0d67f2e912ce7918 <class>: <reason>`.

Report back: the verdict line, the review ref SHA, the `carry_audit` and `pr-contract` results you saw with the time
you read them, and what you re-ran versus left to CI.
