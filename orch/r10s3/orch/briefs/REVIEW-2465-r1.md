# Reviewer seat — PR #2465 (R10-SETPOINT-BOOST), round 1 at head 44ea3af3

You are the **adversarial fix reviewer**. Read `dev/governance/roles/fix-review.md` in the worktree you
create (it is the contract; it states what a verdict must carry). Repository `tvofi/heatpump_optimizer`.

**This is a LOCAL seat. Cloud dispatch is forbidden in this session.**

## What you review

- PR **#2465**, branch `fix/r10-setpoint-boost`, roster group **R10-SETPOINT-BOOST**.
- Head to measure: **`44ea3af3f1b8c6ca3ad32c6d4edb45920fcf5687`**.
- `bus-nonce:` **`da4664480025ee08a56aadf47e523638`** — carry this exact line in the verdict file.

The fix makes set-point-driven heat pumps plan at a sensible flow temperature instead of a 25 °C floor
(three changes: the heating floor sits above the flow gate, the draw window is censored, and every
set-point write is quantised to whole degrees at the single write owner). Its handoff body claims 9
unpinned mutation sites disposed: 8 `killed_by` entries written into the mutation ledger and 1 measured
`survivor_triage equivalent` (`pump_arbiter.py` `_flow_target`, CLAMP_DROP, anchor `38a077e7`). Re-derive
those; do not take the body's word.

## Environment

- Working checkout for the tools: `/Users/timmalmstrom/hpo-seats/r10s3/orch-wt` (has `tools/audit/seat/`,
  and the bus dispatch record for #2465 lives on this host's bus state).
- Your own absolute scratch directory: **`/Users/timmalmstrom/hpo-seats/r10s3/rev-2465`**
  (create it). Your detached review worktree goes under it, e.g.
  `git -C /Users/timmalmstrom/heatpump_optimizer worktree add --detach /Users/timmalmstrom/hpo-seats/r10s3/rev-2465/wt 44ea3af3f1b8c6ca3ad32c6d4edb45920fcf5687`.
  Evidence files go under `/Users/timmalmstrom/hpo-seats/r10s3/rev-2465/ev/`.
- Put the seat venv shims first on PATH for anything you run by hand:
  `export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH`.
  Direct script runs use `PYTHONPATH=tests/hastub`.
- Never write under another seat's directory, never `pkill -f` (it kills other seats), and stop only a
  PID you started.

## In-flight update — read this before you post

An `update_pr.sh` for this branch (**pid 3561**) is running right now to replace the PR body with the
fixer's corrected one. It may push a new head while you work.

- Do all your measurement at `44ea3af3` and start immediately; do not wait for it.
- **Before posting, re-read the head** (`gh pr view 2465 --json headRefOid`).
- If the head is still `44ea3af3`, post your verdict normally.
- If it has moved, post `blocked <sha> head-moved: measured 44ea3af3f1b8c6ca3ad32c6d4edb45920fcf5687, head is <other>`
  and say in the verdict **which of your numbers survive the delta** (the delta should be `origin/main`'s
  newer commits plus the body rewrite — verify that from `git diff 44ea3af3..<new head>` rather than
  assuming). Round 2 will be dispatched at the new head; your measurements are not wasted.

## What the contract owes, applied here

1. **Mutation proof**: delete the lines the fix names, run the closure, confirm the named checks fail,
   restore. In particular re-derive each of the 8 `killed_by` ledger entries and the one triage — a
   triage on a killable mutant is `metric-gamed`.
2. **The finder's harness, not the fixer's**: run it at the baseline SHA and at the head, printing your
   own `RESULT` lines.
3. Null control on every quantified claim (the unpinned count going back to the base is one).
4. Claim files vs actual drift (`env_drift.py --all` against the merge base; `card_drift.mjs` only if card
   files move).
5. `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading untouched.
6. **Every red check owes an answer** in `## Red checks` — read the head's own check-runs, not the body's
   account. The body currently answers `mutation` and `pr-contract`; check the answers are present and
   that the body has not claimed an autofix would clear what the autofix left alone.
7. **Forward-carries**: open the destination each `Carry:` line names (a roster carry is at the
   `handoff/audit-r10-roster` SHA the body cites) and confirm it states its control. A marker alone is
   `blocked <sha> carry-missing`.
8. Attack the fix at other configurations the finding's harness accepts; open the class (the body names
   mypy, the features suite, the entity suite, the structure ratchet and the mutation table at its
   `## Figures`).
9. Judge `fixer.md` step 17 (architecturally sound) on added lines.

**CI is the authority for the heavy lanes** — cite its runs, do not re-run the gate or the mutation
table. Your targeted mutants and cheap checks are yours.

## Deliver

1. Write `VERDICT.md` and the evidence directory, then push with:
   `cd /Users/timmalmstrom/hpo-seats/r10s3/orch-wt && bash tools/audit/seat/bus.sh push-verdict 2465 <VERDICT.md> <evidence dir>`
   The first line is the grammar: `Fix review: merge <40hex>` or
   `Fix review: blocked <40hex> <class>: <reason>`.
2. Report back: the verdict line, the review ref SHA `push-verdict` prints, your RESULT lines, and
   anything you could not verify (say so; do not report a number as confirmed).
