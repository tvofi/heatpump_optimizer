# policy: a mandated budget raise only when no payment improves the code

tvofi's ruling of 2026-10-14 made permanent, and bound to a mandate in force.
An agent may raise a `*_budgets.json` cap only while a mandate covering
budget raises (scope `budget-raise` or `all`) is in force. It must also first
show that no payment improving the architecture exists. A payment is moving,
deleting, sharing or refactoring code. It counts only when
`tools/audit/archscore/`, run before and after, does not worsen and judgement
agrees the result is sounder. A payment that games or worsens the score does
not count. With no mandate, a raise stays the owner's own approving review,
unchanged.

- **Policy text.** `CLAUDE.md` rule 2 states the exception. The rule
  `dev/governance/rules/ratchet-budgets.md` (and its generated twins) points
  to it, and says a prose cap's payments include step 1's cuts. Decision 0013
  gains a 2026-10-14 amendment that quotes the ruling and states the shape.
  No new policy file is added (0012's moratorium).
- **Enforcement.** `tools/policy/budget_raise_gate.py` gains
  `justification(body)`. A mandated approval is decisive only when the pull
  request body has a `## Raise justification` section that holds a
  `Payments tried:` line with text and at least one
  `Architecture score: dS <n> <IMPROVES|NULL|WORSENS>` line (score.py's own
  report line). The section ends at the next level-one or level-two heading.
  The body is read (`gh api repos/<repo>/pulls/<n>`) only when a mandated
  approval is the decisive review, and a failed read refuses. The owner's own
  approval never reads it. `approval()` takes an optional `justify`, so
  `merge_train.py`'s policy-merge reader, which passes none, is unchanged.
- **Grades only after merge.** `budget-raise-gate.yml` restores the gate from
  the base commit, so this enforcement grades pull requests only once it is
  on `main`, as 0013's 2026-10-02 amendment did. The workflow already fires
  on `edited`, so a body fix re-runs the gate.

The gate checks the shape. Whether the payments tried were real is judged by
review.

## Head

`31db3dc60e90270d3579cb00e2b9bad07fa65458`. Every figure below was measured at
this commit.

## Approval

This changes policy: `CLAUDE.md`, `dev/governance/rules/ratchet-budgets.md`
and decision 0013. `budget_raise_gate.py` is code-owned. It is policy under
mandate 6175172275. The owner's words (tvofi, 2026-10-14, in session), quoted
verbatim:

> "Budget raises are within your mandate, but only if it is truly not possible to pay in a way that improves the code."

> "moving, deleting and sharing should only pay for it if it results in a sounder architecture. Arch_score is the metric for that but good judgement is also needed. Refactoring is also an option."

> "Make this shape permanent, but exclusively permittible and possible during a valid mandate."

## Mutation proof

Eight mutants, applied one at a time and restored by
`python3 /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/r10-raise-policy/mutate.py tools/policy/budget_raise_gate.py`
(output in `/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/r10-raise-policy/mutation.txt`). Each one turns the
self-test red:

- M1 the `justify()` call skipped: `235 checks, 13 failed`
- M2 `decide` passes no body check: `235 checks, 13 failed`
- M3 the section runs to the end of the body: `235 checks, 1 failed` ("figures in a later section do not count for an empty one")
- M4 no score line required: `235 checks, 1 failed` ("a section with no arch_score figure is refused")
- M5 the heading matched as a substring: `235 checks, 1 failed` ("a heading only inside other text does not count")
- M6 the owner's own review also owes the section: `235 checks, 9 failed` ("an approved raise passes" and others)
- M7 an empty `Payments tried:` accepted: `235 checks, 1 failed`
- M8 a failed body read returns an empty body: `235 checks, 1 failed` (e2e "exits 1 when the body read fails")

Failing first: the new arms, run against the unmodified gate, printed
`budget_raise_gate self-test: 232 checks, 60 failed`. The `decide` signature
had no body reader, so every arm that calls it raised (output in
`/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/r10-raise-policy/selftest-failing-first.txt`).

## Null control

At main `554e2ecfa`: `budget_raise_gate self-test: 219 checks, 0 failed`. At
this head, the arms that need no section still pass: no raise reads no body;
the owner's own approval passes without the section and without a body read;
and every pre-existing mandate arm is unchanged (a mandated pass now carries
the section in its fixture body).

## Figures

- `budget_raise_gate self-test: 235 checks, 0 failed` -- `python3 tools/policy/budget_raise_gate.py --self-test | tail -1`
- `Architecture score: dS +0.0000 NULL` -- `python3 tools/audit/archscore/score.py --diff 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef HEAD`
- `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` and `4 TEST SCRIPT(S) PASSED; 31 SCOPED OUT AND NOT RUN` -- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`
- `claims hygiene: 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef ok` -- `python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)`
- `STRUCTURE RATCHET PASSED` -- `python3 tests/structure.py`
- `TOTAL: 0 error(s) across 40 policy file(s)` -- `node tools/policy/policy_lint.mjs`
- per-file and aggregate policy caps hold -- `node tools/policy/policy_lint.mjs --budgets`
- `RULES-SYNC ok: every generated rule is the generated form of its source` -- `node tools/policy/rules_sync.mjs --check`
- brief_lint exits 0 -- `node tools/policy/brief_lint.mjs`
- no budget, claim, VERSION, manifest or RELEASE_NOTES file in the three-dot diff -- `git diff --name-only $(git merge-base origin/main HEAD)...HEAD`

## Architecture score

n/a: no gate metric rises; the diff touches no `custom_components/` file (`dS +0.0000 NULL`).

## Red checks

- `nightly-status`: main's own red, #2205, not this branch's. This diff
  touches no file the nightly suite grades. No cheaper detector for it is
  owed here.

## Forward-carry

none.

## Friction

none.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
