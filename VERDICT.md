Fix review: merge 94c8b0006782dd020d24df4f89ce9880b2ead1d5
bus-nonce: 0100c50263344c13e5c515f764b7a0c5

# Fix review — PR #2869 (R10-FLOW-AUDIT-PLAN), round 2

Measured at `94c8b0006782dd020d24df4f89ce9880b2ead1d5` from detached worktrees
(`/tmp/wt-review-2869-r2` at head, `/tmp/wt-base-2869` at `2f15a24cd`), with the
finder's committed harnesses at both ends. The head was the PR head when I
started and is still the head when I post: `git ls-remote` and `git rev-parse`
both return `94c8b0006…`; the only movement is `origin/main`, which advanced from
the branch's last merged `d620369fa` to `4f3c7302` while I measured (see the
conflict section). Nothing in this verdict is a CI re-run; `gate` is cited from
CI's own run at this head.

## Both ends, finder's harness, re-derived rc

| harness | base `2f15a24cd` | head `94c8b0006` |
|---|---|---|
| `python3 -I tools/audit/seat/plan_audit.py --self-test` (identity stripped: `env -u GIT_AUTHOR_NAME -u GIT_AUTHOR_EMAIL -u GIT_COMMITTER_NAME -u GIT_COMMITTER_EMAIL GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null`) | rc 1, `CalledProcessError … 'commit' … exit status 128` | rc 0, `plan_audit self-test: 27 checks, 0 failed` |
| `python3 tests/closure.py selftest` | rc 1, `1 of 117 closure shrink pins FAILED` (`no rename-detecting --name-only diff under RENAME_SITES [tools/audit/seat/plan_audit.py:314 …]`) | rc 0, `ALL 117 closure shrink pins PASSED` |
| `is_inert('.claude/workflows/audit-plan.js')` | `True` | `False` |
| `closure.py check --in-dir <entities recording listing audit-plan.js in inert_reads> --partial` | rc 1, `INERT READS UNDER-APPROXIMATED … tests/entities.py: .claude/workflows/audit-plan.js` | rc 0, `closure: committed closures cover every file this run touched` |

RESULT both-ends: the fixer's 1→0 / 128→27 / INERT→cover claims reproduce
exactly. I did not run the fixer's transcript; each row is my own execution of
the same committed harness at its own tree.

## Mutation proof, re-run by me (edit → observe → `git checkout --`)

- `with throwaway_git_environ(), tempfile…` → `with tempfile…`: identity present
  → `FAIL the fixture commits under the harness's own identity, not the box's
  tvofi <…>`; identity stripped → `CalledProcessError … 'git … var
  GIT_AUTHOR_IDENT' … exit status 128`. Restored.
- `--name-status -M` → `--name-status --no-renames`: `FAIL a rename alone is one
  module, so it adds no co-change pair {'merges': 3, 'pairs': 2, 'occurrences':
  2, 'cochange_per_100': 66.6667}`. Restored.
- `--name-status -M` → `--name-only`: `python3 tests/closure.py selftest` →
  `FAIL no rename-detecting --name-only diff under RENAME_SITES
  [tools/audit/seat/plan_audit.py:322 …]`, `1 of 117 … FAILED`. Restored.
- `INERT_EXCEPT` entry removed: `closure: files on the INERT list are inside a
  recorded closure (committed tests/closures.json): .claude/workflows/audit-plan.js`
  (#357). Restored.
- closure entry removed: `UNDER-SCOPED: tests/entities.py really reads 1 file(s)
  the committed closure does not list: .claude/workflows/audit-plan.js`.
  Restored.
- Both restored: rc 0. Working tree clean after every mutant.

## The `INERT_EXCEPT` move — attacked hardest, as dispatched

1. **The machinery really reads this file.** `tests/entities.py` (the
   codeql paths-ignore sweep at `tests/entities.py:21046-21065`) globs the
   ignore patterns, then reads every matched file's bytes through
   `node --check`. `.github/workflows/codeql.yml`'s only pattern is
   `.claude/workflows/*.js` (`paths-ignore`, line 190), which matches 9 tracked
   files including `audit-plan.js`. The committed `closures['tests/entities.py']`
   records it as read (a strace measurement). Independently, the file is
   unparseable under both grammars (`node --check` rc 1 for `module` and
   `commonjs`; top-level `return` at line 181), which is the property entities.py
   pins for an ignored file — so it is genuinely the same class as
   `web-fix-wave.js` and `audit-find.js`.
2. **`INERT_EXCEPT`, not the wider `INERT`.** `is_inert()` is `is_handover or rel
   in INERT_EXCEPT or … or any(prefix match in INERT)`. The file was inert only
   because `.claude/` is an `INERT` prefix. `INERT_EXCEPT` is an exact-match
   (per-file) escape, not a prefix, and is the tree's documented route for a
   read file under an inert prefix. Adding it to `INERT` instead would have been
   a no-op (already matched by the prefix) and would not have made the closure
   legal.
3. **It does not disable the check that was catching something.** The two
   directions both still fire, proven by the mutants above: keeping it inert with
   a closure entry is the #357 refusal; removing it from the closure is
   UNDER-SCOPED. And the exemption is not silent: planting a real but unread
   tracked file (`.claude/settings.json`) into `INERT_EXCEPT` makes
   `orphan_files()` return it, which `tests/entities.py` refuses ("these force the
   FULL suite when touched"). `orphan_files()` is empty at head (null control).
4. **The move strengthens the gate, it does not relax it.**
   `closure.py affected --files .claude/workflows/audit-plan.js` goes from
   `CASE: SKIP -- … every one of them is INERT` at base to
   `CASE: SCOPED … REDERIVE tests/entities.py <- .claude/workflows/audit-plan.js`
   at head. `inert_closure_violations(committed closures)` is `[]` at head.
5. **Class closed.** Every one of the 9 `.claude/workflows/*.js` the glob matches
   is `INERT_EXCEPT` (none inert). The `RENAME_SITES` census covers
   `tools/audit/seat/*.py` and is green at head. The identity class is closed
   empirically: `governance / instrument-self-tests` passed at this head
   (step 32 runs the self-tests outside `tools/audit/seat/`; step 23 the P3
   arm), which is the lane that caught the base defect.

## `MODE: FULL` is the honest mode

`tests/closure.py` and `tests/closures.json` are both `GATE_FILES`. Running the
instrument at this head:

```
python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)   # d620369fa
  MODE: FULL -- every test script runs, nothing is scoped out.
  reason: tests/closure.py changes the gate itself, so every closure is suspect
```

The same line prints with `--diff 484d99022`. The body says FULL for exactly this
reason and does not quote the stale `SCOPED` figure as current.

## The six reds: per-step conclusions, and the dispatcher's correction

Read from the Actions API at base `2f15a24cd` (`gh api …/actions/jobs/<id>
--jq '.steps[]'`), not from log text. All six match the body's names and step
numbers: `instrument-self-tests` step 23, `tests / closures` step 10,
`closures-autofix` step 9, `fast (3.14)` step 11, `pr-contract` step 10, `gate`
step 4. The body answers each with a cheaper detector (or the finding that the
checking lane is the cheapest); none is left unanswered.

The dispatcher's earlier reading was wrong, and the body does **not** rest on it:
the `BAD … FAIL closed: analysis 11 (actions): HTTP 404` lines are a passing
`local_alerts.py --self-test` mutant arm, and the `MUTATION TABLE REFUSED` line in
`fast (3.14)` is a self-test fixture. The body records both readings explicitly so
the next re-read does not repeat them.

## CI at this head (cited, not re-run)

The `CI code` run for `94c8b0006` concluded **success**. All 42 check runs are
`success` or an intentional `skipped`; `gate`, `pr-contract / pr-contract`,
`tests / closures`, `governance / instrument-self-tests` and `tests / fast
(3.14)` are all `success`. `pr-contract` ran after the last settle and accepted
this body. I did not re-run the gate or the mutation table.

## Non-findings — measured here, all holding

- No protected artifact in the diff: three-dot name list has no `VERSION`,
  manifest, `RELEASE_NOTES.md`, budget file, golden fixture, claim file or
  mutation ledger. Both claim files are byte-identical base→head; `VERSION`
  equals `origin/main`'s.
- No policy file in the diff (`dev/governance/`, `.claude/rules/`, `cursor`,
  `CLAUDE.md`, `AGENTS.md` absent), so no owner-approval flag.
- `node tools/policy/check-wave-script.mjs` → `224 passed, 0 failed`;
  `node tools/policy/brief_lint.mjs` → rc 0, `TOTAL: 0 error(s) across 48
  file(s)`; `ref_privacy.py --check` → `0 refused`; `selftest_wiring.py --check`
  → `98 self-testing, 98 wired, 0 unwired`; `throwaway_git.py --check` → `0 raw
  git init or clone site(s) refused`; `--self-test` → `44 checks, 0 failed`.
- The coupling "flat by design" claim reproduces: `399098f63` → `merges 184,
  pairs 403, occurrences 586, cochange_per_100 318.4783`; `57f0c9c77` → `merges
  189, pairs 114, occurrences 145, cochange_per_100 76.7196`; identical under
  `--name-status -M` and `--name-only` at both refs.
- Architecture (`fixer.md` 17): the fix uses the tree's existing mechanism
  (`throwaway_git_environ()`) rather than adding an `env=` parameter to
  production `git()`/`coupling()`; the body names that alternative and why it
  lost. No parallel mechanism, no production signature widened for a test.
- Conflict: `git merge-tree --write-tree origin/main HEAD` → rc 0. Against the
  advanced `origin/main` (`4f3c7302`) the stderr carries `LEDGER-MERGE: resolved
  tests/closures.json` (the `merge.ledgermerge` driver), rc 0 — no unresolved
  path. That merge is the orchestrator's resolution delta to land, not a conflict
  for this review.
- Forward-carry: the body's `## Forward-carry` and `## Friction` are `none`; the
  fix round introduces no constraint on a later stage, so there is nothing to
  open.

## Residual (non-blocking) — one stale figure label

`## Figures` reads `… ten files, 1027 insertions and 1 deletion, against merge
base 484d9902222031f8e081df9f53b52ffd50fcc0af`. The counts are right for the
printed command, but the merge base is not `484d99022`: `git merge-base
origin/main HEAD` is `d620369fa…`, and `git diff 484d99022...HEAD --stat` is
`13 files changed, 1030 insertions(+), 3 deletions(-)` while `git diff
d620369fa...HEAD --stat` is `10 files changed, 1027 insertions(+), 1
deletion(-)`. So the number is re-derivable and the label is stale — a leftover
from the round-1 body, the same class as round 1's finding 5. It does not change
`MODE: FULL` (FULL either way) and no tree artifact carries it, so it is a body
correction, not a blocker.
Carry: R10-FLOW-AUDIT-PLAN

## Not re-taken — said rather than trusted

- The 13 `audit-plan.js` mutants: unchanged by this round, and round 1 measured
  them.
- The `score.py --diff` null control (`dS +74.6109`): six-plus minutes on a
  shared box, and no blocking finding turns on it; the plan's own comparison
  reproduces the numbers it quotes.
- The heavy gate (`tests/structure.py`, `entities.py`, the full suite): cited
  from CI's green `fast (3.14)`/`gate` at this head.

## Disclosure

I wrote no harness for the fix's findings — each both-ends row and each mutant is
the committed harness run at its tree. For the "flat by design" companion I did
build one small local instrument: a `--name-only` re-implementation of
`coupling()` called beside the production function, to confirm the flatness
claim; it is mine, not the finder's, and its output is in
`evidence/coupling_flat.txt`.

Round 2 for this PR; no re-cut is owed.

bus: verdict/2869 to publish; evidence: `/tmp/ev2869`
