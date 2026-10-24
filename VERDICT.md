Fix review: merge 029d6ccc954a6b2cbf04aa92bb53fea23cb65a0a

bus-nonce: 9710e855ae32b85b7748e96f5f6e1743

## Scope

- Round 1 for this seat. Head reviewed: `029d6ccc954a6b2cbf04aa92bb53fea23cb65a0a` (base origin/main `806aa2ce8`). Role contracts current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- The diff adds two docs files, `dev/programme/triage/s6-batch11.md` (the P80 ruling) and `dev/programme/delivery/2748.md`. No code, no budgets, no claim files, no `VERSION`, manifest or notes heading. Mutation proof is n/a; no production line exists to delete.

## Findings

- The Instances line splits the 75 non-path errors as "5 path:line drift, 3 found at line N instead, 2 line past end of file". I re-derived the total (75) and the path count (65), but the other ten split as 3 "none of [...] found" drift, 4 "found at line N instead" and 3 "past end of file" (ev/brief-lint-carry-fold.txt). The total and the DEFER do not depend on how those ten are split. Carry: dismissed: the split misstates the breakdown of 10 of 75 errors and leaves the ruling and every figure it relies on unchanged
- The Instances line cites the roster as `handoff/audit-r10-roster` by branch name and gives no SHA. That ref has moved since (185 groups and 646 carries at 9e9ee6ce7). I found the measured state, 184 groups and 644 carries, at `f7a3b23f4` (18:39:46+02:00, just before the triage commit) and re-derived the figures there. Carry: dismissed: re-derivable from the commit time and the counts, which name one roster commit; a later re-triage reads the live roster anyway
- The body's `## Head` section says `029d6ccc` "merges origin/main `806aa2ce8` ... into this PR's previous head" and that `251ed518` is "on origin/main `73b69fe0a`". There is no merge commit. The chain is 029d6ccc -> 251ed518 -> 806aa2ce8. The head SHA and code-head SHA it names are correct. Carry: dismissed: orchestrator-script template wording that misstates no SHA the review depends on, dismissed the same way in the #2743 review

## Evidence

- RESULT brief_lint roster@f7a3b23f4 as-is: `TOTAL: 0 error(s)`. With each group's carries appended to its brief: `TOTAL: 75 error(s)`. Body: 0 and 75, re-derived (ev/brief-lint-carry-fold.txt). Linted from a worktree at the head (main's tree) with only the roster file copied in. The roster branch's own tree gives 5 and 101, so the body's figures are against main's tree.
- RESULT groups with errors: 40 (body: "40-odd"). Largest: R10-ORCH-BEATD 7, R10-ORCH-PLANPAGE 5, R10-FLY-SUITE-ENV-FLAKES 4, R10-COP-GATE 4. All match the body.
- RESULT 65 "not in the tree" path errors, as the body says. Sampled: `proposals.md`, `ev/roster_carries.txt`, `beatd.py` and `CARDS.json` are out-of-tree or not-yet-created files. This supports the body's "forward references" point.
- `lintFile` (tools/policy/brief_lint.mjs:969-990) calls `lintBrief(... g.brief ...)` and never reads `g.carry`. The one `lintBrief` over a carry text is `lintCarryFile` (line 946), which reads `dev/programme/carries/carry-<N>.json`, not the roster `carry` array. The claim holds.
- #2743 instance: the round-1 verdict on `probe/rev-2743-127d3efb` blocked at 2e2b374c on P66's `carries/carry-N.json` and reported 1 error from 7 folded carry texts and 6 clean, as the body says.
- P44 in `dev/programme/triage/s6-batch1.md` (line 75) is DEFER for the same proposal. `s6-batch10.md` (P79) exists only on `triage/s6-batch10` and is absent from the base tree, as the body says.
- DEFER soundness: `proposal-triage.md` treats an unmeasured benefit as DEFER, and a DEFER must name what would change it. P80 names it (a second carry blocked at review, or a dead carry found in the roster). The cost estimate is consistent with the measurement, since the full form fires 75 times today. No live roster group owns carry linting. I searched the non-done groups' briefs and carries. R10-FLOW-TOOLKIT-MODEL's `--dry-run --out` overlay feeds brief_lint but would inherit the same blindness, so it is not an owner.
- Carry check: the PR routes nothing (DEFER, `## Forward-carry` n/a), so there is no carry text to lint. As a probe I folded the ruling text itself through brief_lint: 2 path errors, `proposals.md` (the out-of-tree session file the text names as such) and `s6-batch10.md` (stated as unmerged). Neither is a carry.
- `roster_edit.ruling_verdict(src, 'P80')` returns `DEFER`, and the null control `P99` returns `None`. Body figure "1 DEFER" re-derived with its own `rg` command.
- `git merge-tree --write-tree origin/main 029d6ccc...`: rc 0, tree e5c1904d. No conflict (ev/merge.txt). The new file sits under `dev/programme/`, which is on `tests/closure.py`'s INERT list (line 273).
- CI on the head (check-runs API, 34 runs): no run concluded red. Concluded success include budget-raise-gate, briefs, policy-docs, delivery-status, nightly-status, mutation, closure-scope, arch-score, codeql (3), hassfest, validate-hacs, typing and wave-script. Still in progress at review time: closures, browser, coverage, fast (3.14), instrument-self-tests, env-matrix and one prelude. The body's `## Red checks: none` is accurate so far. A red on a docs-only diff that reaches no measured closure would not be this PR's.
- Head re-checked at write time: the PR head is still `029d6ccc954a6b2cbf04aa92bb53fea23cb65a0a`.
