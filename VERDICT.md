Fix review: blocked 2c8f2bacc796af7b29cda621ccb9a48dfc255c6f mutation-vacuous: the `<` to `<=` arm and the one-line restriction survive reviewer mutants R8 and R5, and the operator emits two provably equivalent mutants (away.py:558, optimizer.py:4742) the body does not disclose

bus-nonce: c4054e89ab39063e836eca3b32e49277

Review round 1, PR #1861 (R9-F10.6), fix-review.md. Measured head 2c8f2bacc796af7b29cda621ccb9a48dfc255c6f, merge base and origin/main aa7a81192. The body's `## Head` names this head. Worktree: detached at the head, ~/hpo-seats/1861-review/wt. My copy of fix-review.md is current (the three-dot diff of tools/audit/briefs/ against origin/main is empty). tvofi's ruling to enable at the measured cost is not re-opened here. Nothing below argues against the cost, only against the test and the disclosure.

## What blocks (three repairs, all small)

1. **Equivalent mutants are emitted and not disclosed** (dispatch item 1). `rv_equiv.py` (my own instrument, in evidence/) scans for the max/min idiom, where both arms are equal at equality. Two production sites match, and both are in the 946:
   - `away.py:558`, `if last < first:` then `last = first`. With `<=`, the equal case assigns the same value.
   - `optimizer.py:4742`, `idx = i if i <= last else last`. With `<`, the equal case yields `last == i`.
   No driver can kill either one. Each leaves the unpinned count only through a `survivor_triage` `equivalent` verdict. The body's figures are silent on this: the "about 24 nights at a 100% kill rate" estimate assumes they do not exist.
   - Owed: disclose the class in the body, with these two sites and that rule, or exclude the idiom from the operator.
   - My scan covers only that idiom and the integer-against-fraction shape (0 hits for the second). It is not a proof that no other equivalents exist, and the disclosure should say so too.
2. **R8 survives.** Mutating `ast.Lt: ("<", "<=")` to `("<", ">")` passes all three new checks plus the operator-coverage check: 0 failed. The fixture module (`bounds.py`) carries `<=`, `>` and `>=` but no `<`, so the body's first named flip, `<` to `<=`, is pinned by nothing.
   - Owed: a `<` in the fixture.
3. **R5 survives.** Dropping `_one_line(node, lines)` from the CMP_BOUND arm passes the block (0 failed). It moves the production inventory from 946 to 948 sites: `defrost.py:373` `was < DERATE_CONFIDENCE_SAMPLES` and `optimizer.py:4502` `if float(dhw_prices[idx]) <= float(` (a mutant of a line that does not parse alone). The ratchet would not refuse that change either, because `mutation_table.py` is not a production file. The body states multi-line comparisons stay out (C7's residual), and no check holds that.
   - Owed: a two-line comparison in the fixture, generating nothing.

## What holds (RESULT lines, all at the head above)

- Inventory, both ends (fixer's `inventory_identity.py`, sha1 064b4c50):
  - `RESULT inventory head sites=5466 sha1=1ba97b4cecd5 unpinned=4855`
  - `RESULT inventory origin/main sites=4520 sha1=c141b52379cc unpinned=3909`
  - The difference, +946 sites and +946 unpinned, equals `LIST CMP_BOUND: 946 site(s) in 55 file(s), 946 unpinned, ratcheted`.
- Generation, my own instrument (`rv_check.py`): `RESULT rv sites=946 expected=946 line_mismatch=0 bad=0`.
  - It makes an independent AST count of ordering operators in one-line `Compare` nodes, per line.
  - Every mutant changes exactly one operator, by one step (`<`/`<=`, `>`/`>=`), with no parse-status change.
  - `==`, `in` and `is` are never touched, and a chain yields one mutant per operator.
- Ratchet at the head: `4855 unpinned site(s) of 5466 candidate sites, 4855 at the ratchet base aa7a8119...` then `MUTATION TABLE PASSED (empty scope)`. CI's `mutation` job prints the same lines.
- Perturbation (mine, different file from the fixer's): adding `_rv_probe = first >= last` at away.py:560 printed `ADDED UNPINNED ...away.py:560 CMP_BOUND` and `MUTATION TABLE REFUSED -- 4856 unpinned site(s) against 4855`. The null control, the same line with `==`, printed `4855 ... PASSED`. Restored, tree clean.
- D3-s1-01:
  - Fixer's `d3s101_mutant.py` (sha1 df943039): `-5.0 production=-5.0 mutant=None DIFFERS`. At `0.0` and `35.0` the two agree.
  - My own eval of both mutants on coordinator.py:1735: `-5.0 -> [None, -5.0]` and `35.0 -> [35.0, None]`. At `0.0`, `-5.000001`, `35.000001` and `None` every result equals production. So each bound's mutant differs exactly at its own bound.
- The fixer's mutants, re-run with the fixer's block runner (`run_block.py`, sha1 1cc0dcf8): M0 0 failed, E1 4 failed, M1 1 failed, M4 1 failed. All as the body says.
- My own mutants:
  - Killed: R2 (chain not advanced, 2 failed), R3 (no `>`/`>=`, 2 failed), R7 (bounds never generated, 3 failed), R10 (LISTED empty, 3 failed).
  - Survivors:
    - R5 and R8: the blocks above.
    - R6, the gap check dropped: equivalent. The production inventory is identical, 946 sites.
    - R9, the kinds filter dropped: equivalent today, because `LISTED == RATCHETED`.
- `mutation_budgets.json`: `RESULT budgets keys_changed=['_comment']`. No cap, no `last_measured` value and no ledger row moved.
- VERSION, manifest, RELEASE_NOTES and both claim files: untouched (three-dot).
- `git merge-tree --write-tree origin/main HEAD`: rc 0.
- Code owner: `tests/mutation_table.py` is `@tvofi` in CODEOWNERS. Its approving review at the head comes under tvofi's mandate and is not this verdict's to give.

## CI (check-runs API, every run, head 2c8f2bac; waitci DONE total=35)

The only non-green conclusions:
- `nightly-status=failure`. Its log reads `NIGHTLY ABSENT: ... mutation-ledger, mutation-ledger-push did not run in that scheduled run`. That is main's `always()` defect, fixed by #1859. This diff does not reach the reporter (no workflow, plan, HANDOVER or foreign delivery row), so it is exempt under fix-review.md step 11 and owes no Root cause section.
- `pr-contract` and `budget-raise-gate` show `cancelled` runs, each superseded by a `success` run on the same head.
- Earlier branch heads (a5f4e1c1, 97fba3f0, c117c2b3, cd04771a) carry no red run.

Non-blocking, for the repair round:
- The refusal text at mutation_table.py:2473 still lists "guard, clamp, removable return or doubled constant" and does not mention a comparison bound.
- Not run locally: entities.py in full, closures, features.py and goldens. CI ran them on this head and they are green.
