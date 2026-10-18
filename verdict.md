Fix review: blocked e3a6f0729dbb5053bd92a5fb8168b3e74edbaa65 [null-control-false: finding-propagation drops .claude/workflows/wave-*-groups.json, still a live roster home]

bus-nonce: 72cc4a245ab4dd79f5a7b9efe343acc5

Round 1. No earlier `Fix review:` comment is on #2408. Measured head
e3a6f0729dbb5053bd92a5fb8168b3e74edbaa65, and it was still the PR head on
`git ls-remote` just before writing. Merge base 63816b85706b; origin/main
c8cc75ea9. The contract is current:
`git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.

## Blocking finding

The body's null control says every changed line except the `## Enforcement`
paragraph "rewords a sentence without changing what it requires". The
**Friction** line calls `.claude/workflows/wave-*-groups.json` a stale roster
home. The tree says otherwise. That path is still a live roster home, and the
head removes it from the rule in two places:

- `paths:` swaps `.claude/workflows/*.json` for `dev/programme/rosters/*.json`.
  The rule stops auto-loading on the files that live there.
- "Where it goes" changes a live group's brief destination from
  `.claude/workflows/wave-*-groups.json` to "the round's roster under
  `dev/programme/rosters/`".

Evidence at the head (`ev/roster_home.txt`):
- `tools/policy/brief_lint.mjs:92` says: "Rosters stay under
  `.claude/workflows/` until they are archived". Its live-roster scan at the
  head lints `.claude/workflows/wave-3l-groups.json`. That roster still holds
  a non-done group (`3L-G6` is `blocked`), so it has not been archived.
- `tests.yml:3906-3911` says `dev/programme/rosters/` is kept *out of* the
  live-roster scans (`briefs`, `wave-script`), and those scans assert
  web-fix-wave's vocabulary. So there are two roster homes: the
  orchestrator's round rosters (`roster_lib.py`) and web-fix-wave live
  rosters (`.claude/workflows/`). `roster_lib.py:37` speaks only for the first.
- `.claude/workflows/web-fix-wave.js:151` still requires a committed
  `groupsFile`, and its example is `.claude/workflows/wave-ux-groups.json`.
- `.claude/workflows/audit-verify.js` still writes the draft roster to
  `.claude/workflows/wave-r${round}-groups.json`. This is the same stale
  pointer the PR fixes in the rule, and it is neither changed nor
  dispositioned in the body.
- `.claude/workflows/carry-1921.json` is a carry at the old path. brief_lint
  still reads it, and the glob no longer covers it.

What this does: a finding for a stage that runs from a web-fix-wave roster no
longer has a named destination in `finding-propagation`, and a seat editing
that roster no longer loads the rule. That changes what the rule requires. The
null control's claim is false for these lines, and the Friction claim
overstates the evidence.

Fix: name both homes (both globs, and both destinations, or a pointer to
`roster_lib.roster_path` plus the web-fix-wave `groupsFile`). Alternatively,
show that no web-fix-wave roster is live and archive `wave-3l-groups.json`.
Either way, disposition `audit-verify.js`'s draft-roster path. finding-propagation
has 1 token of headroom (1335/1336), so the fix must be paid for in-file.

## RESULT lines (head unless stated)

- RESULT budgets head: finding-propagation 98/101 lines, ~1335/1336 tokens; orchestrator.md 319/319, ~4513/4513; fix-review.md 140/140, ~2451/2451; corpus ~61136 (cap 61026 + band 500). Matches the body. `ev/budgets_head.txt`
- RESULT null control (budgets at merge base 63816b857): 100/1329, 319/4513, 140/2451, corpus ~61130. Matches the body. `ev/budgets_base.txt`
- RESULT policy_lint head: `TOTAL: 0 error(s) across 41 policy file(s)`. Base: the same. `ev/lint_head.txt`, `ev/lint_base.txt`
- RESULT rules_sync --check head: `RULES-SYNC ok`. `ev/rules_sync_head.txt`
- RESULT mutant, the base `.cursor/rules/finding-propagation.mdc` restored: `RULES-SYNC: 1 file(s) out of date`. Killed. `ev/mutation_policy.txt`
- RESULT mutant, the base `policy_known_bad.json` restored (count 8): `[known-bad] ... 6 occurrence(s) left of 8 recorded`, TOTAL 1 error. Killed, so the 8 to 6 re-record is earned by the duplicate removal. `ev/mutation_policy.txt`
- RESULT mutant, the deleted section-13 sentence re-added to orchestrator.md: 320 lines / ~4529 tokens, against caps 319/4513, 2 errors. The payment is real. Judgement on the deletion: the bold sentence just before it ("An instrument the programme runs is a tracked, self-tested file; a session-local copy is a defect") covers it. Accepted as a duplicate. `ev/mutation_policy.txt`
- RESULT policy_lint.mjs fix: at the head, `--record-known-bad` prints `recorded 7 entr(ies), 13 occurrence(s) ... +0 -0 ~0`. This is idempotent, so the committed file is what the tool writes. Mutant: restoring the shadowing `const at` crashes with `TypeError: at is not a function`. Killed by manual drive only. No test pins it, as the body's Unpinned sites section says. `ev/mutation_record.txt`
- RESULT entities.py (`env -u BASH_ENV PYTHONPATH=tests/hastub`): `ALL 2346 ENTITY CHECKS PASSED`, exit 0. `ev/entities_head.txt`
- RESULT closure select: `MODE: SCOPED -- 1 script(s) run, 32 scoped out` (tests/entities.py). Matches the body. `ev/closure_select.txt`
- RESULT merge-tree origin/main(c8cc75ea9) with head: tree 1c39ae654452, exit 0, no conflict and no MERGE-CLAIM line. `ev/merge_tree.txt`
- RESULT VERSION, RELEASE_NOTES.md, manifest and tests/golden are untouched (three-dot). `ev/version_untouched.txt`
- RESULT CI on e3a6f0729: every check run is success or skipped, and none failed. On the previous head 36b4a1cf4, only cancelled runs (superseded) and a neutral CodeQL, none failed. `## Red checks: none` holds for the range. `ev/check_runs.txt`
- RESULT `git log -L` attribution of the shadowing to 98ee99263: not re-derived. The line-range log I ran printed 2b5e41670 (#608, the linter's landing) as the oldest commit touching that range. 98ee99263 may be the commit that introduced the module-level `at(path)` that the local then shadowed. I did not verify this, and it is not load-bearing.

## Steps without a harness, and advisory notes

- Steps 2, 3 and 9: this is a policy PR from an owner-accepted pre-study, and it has no finder's harness. The instruments are the policy lints above, which I ran at both ends. The pre-study's figures (14 roster-only PRs, median 49 min, 54.1 runner-min on #2380) are quoted from outside the tree. I did not re-derive them.
- Step 10: the forward-carry is `none`, which is consistent: the PR is itself the rule text.
- Advisory, fix-review.md step 10: "confirm it is there, carrying the control and stated as a precondition" became "confirm it states its control as a precondition". The old text set two separate checks, and finding-propagation keeps them separate as "Carry the control" and "State the precondition". The new text fuses them into one. Splitting them back costs a few tokens at 0 headroom.
- Advisory, null-control wording: the orchestrator.md section-10 bullet "Land the roster on main only when the tree needs it" also adds an obligation. It is declared under "The change", but the null control says only `## Enforcement` adds one.
- Owner approval of the policy (tvofi) is still owed, and the body says so.
