Fix review: merge 6bb827793e1fff355b73cc17dd267a46b6b2a254

bus-nonce: fca4ad3d5f870f5b81b35ff475f4008c

## Evidence

Round 1 (first review; no reviewed head). Reviewed at 6bb827793e1fff355b73cc17dd267a46b6b2a254, merge base 8751943e17ef4d3ec699e7859ae829b4528d8ce7, from a detached worktree. Roles diff merge-base...origin/main touches only root-cause.md, not fix-review.md.

- Merge: `git merge-tree --write-tree origin/main 6bb827793e1fff355b73cc17dd267a46b6b2a254` (origin/main 1723f9fdc9) rc 0, tree 5fb32ce079; stderr `LEDGER-MERGE: resolved tests/closures.json`, no conflict (ev/merge-tree.txt).
- CI: `merge_train.py classify 6bb827793e1fff355b73cc17dd267a46b6b2a254 --pr 3739` exit 4: `APPROVAL-OWED 6bb827793e1fff355b73cc17dd267a46b6b2a254 4 budget raise(s), first .claude/workflows/policy_budgets.json: corpus_tokens: 71212 -> 72206 (a cap went up): a raise is the owner's (0013): no decisive review by tvofi (id 70032254) on this pull request`. Judged as GREEN under the brief; the raise's approval follows this verdict (mandate 6893738184). Log in ev/classify-log.txt.
- Mutation proof, re-run (ev/mutants.txt): each widened reader reverted to its base form on its own, with its named self-test at the head rc 0 first. ref_privacy `_DIM` rc 0->1; fold_ledger `DIM_OF` rc 0->1 (FAIL DIM_OF ... 19 briefs); finder_overlap `SEAT_RE` (--no-mutants) rc 0->1 (FAIL owner-only: DX0-s1 ...); check_scopes `BRIEF_NAMED` rc 0->1; roster_lib `_DIM` rc 0->1 (got: ['DX0']); audit-verify `ownerOnlyRecord` back to `/^D[0-9]+/` check-wave-script rc 0->1. Additional mutants of my own: dropping `ownerOnlyRecord`'s `(?![0-9])` lookahead, killed (rc 0->1, near-miss arm); reverting finding.schema.json's `dimension` pattern, killed (rc 0->1, the schema-equality check).
- Survivor: the step-yield regex at audit-verify.js:309 reverted to `/^D\d+\.(M\d+)$/` is not killed (grader rc 0). The body discloses it and I confirmed it is equivalent: audit-verify.js:219 throws on any register finding `ownerOnlyRecord` reads as owner-only, before the loop at :309, so no DX0 step reaches it. That makes it equivalent, not vacuous.
- Class (step 6): census over tracked *.py/*.js/*.mjs/*.sh/*.json, excluding round evidence, for dimension-id regexes not accepting X0 (`git grep -nP 'D\(?(\?:)?(\\d|\[0-9\]|1\[)'`, ev/class-census.txt) plus integer parses of `id[1:]`. Remaining sites: finder_overlap.py:85 `D(?:1[0-7]|[0-9])` report bound, which the body dispositions (an owner-only seat is refused before it); dev/audit/harnesses/r11_denominator_planted.py:54, a harness reading only its planted D1/D2 rows; fold_ledger.py:167 `int(r[1:])`, which parses a round (R<n>), not a dimension. No open seam. The census is a rule I built myself; the body names no committed enumerator.
- Figures re-derived: `policy_lint.mjs --budgets` at the head gives corpus ~72206, CLAUDE.md 3616 tokens, COMMON.md 115 lines/1715 tokens, DX0.md 60/799, all equal to the new caps; `policy_lint.mjs` at the head reports 0 errors (ev/budgets-head.txt, ev/policy_lint-head.txt). At the base, corpus ~71371 against cap 71212 (+band 500). The +835 delta is exactly DX0.md 799 + CLAUDE.md 12 + COMMON.md 24, so the raise is exactly the three edited files and nothing else (ev/budgets-base.txt).
- Raise justification (step 14): each payment named is visible in the landed text (60-line brief, one-line COMMON.md sentence, 12-token CLAUDE.md row). The CLAUDE.md row is required by its own "named individually" table rule, and the COMMON.md sentence by design P8. The DX0.md sections (owner-only declaration, universe, method M1..M4, territory) each carry a constraint downstream seats read. I found no payment the body missed that improves the code; archscore dS +0.0000 as quoted. Judged sound on its merits.
- Steps 4/5: no golden fixture or claim file in the diff; VERSION, manifest and RELEASE_NOTES untouched (diff stat, 17 files).
- Step 10: the three carries (2, 3, 4) are dismissed as duplicates of the group's own owner-act carries; carry_audit at the head reports `3 routed, 0 unrouted, 0 bad destination(s)`.
- Step 16: no actuator path in the diff (no custom_components/).
- Head: PR body head = 6bb827793e1fff355b73cc17dd267a46b6b2a254 = measured head; branch re-read before push (ev/head-recheck.txt).

## Red checks

- `budget-raise-gate / budget-raise-gate` (in owed-reds): answered in the body's `## Red checks`. The raise is the change; only the approving review turns it. classify reports APPROVAL-OWED.
- `tests / nightly-status` is red but not in the owed-reds set (ev/owed-reds.txt), so no answer is owed.
