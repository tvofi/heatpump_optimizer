Fix review: merge fe23416d408624f59f3d36dbbcea049d138ec764

bus-nonce: 6068650e80c94ba2ab0f756086a413aa

## Previous findings

- At ee9bfa8ac5 the block was mutation-vacuous on `plan_slots.py:89`: M1 (`max(dict.fromkeys(codes), ...)` back to `max(set(codes), ...)`) passed the D1-s1-51 tie check under PYTHONHASHSEED 23 and 76. Resolved by de8181b0a0. The check now picks, under the running seed, the first pair of action codes whose two-element set iterates the same whichever code is inserted first, so a `set` returns one winner for both spellings of the tie while the expected first codes differ.
  - M1 applied in this worktree, the PR's features block (`features_block.py`, marker `# --- R11-SEAM-solver: the start set brackets`, prelude from `--emit-prelude`): rc=1 under PYTHONHASHSEED 0, 23, 24, 76, 84 and unset, each failing `a plan slot's reason tie reads the slot's first code, whatever the hash seed (D1-s1-51)`. The unmutated head reads ALL 9 FEATURES BLOCK PASSED under the same six seeds (ev/M1-seeds.txt).
  - The selection itself, swept in one subprocess per seed over PYTHONHASHSEED 0-1000, with `HEAT_PUMP_ACTION_STATES` copied from `const.py` at this head: a pair is always found, and the `set` pick fails it at 1001 of 1001 seeds (ev/seedsweep.txt, ev/seedsweep.py).

## Delta reviewed

`git diff ee9bfa8ac5 fe23416d40`. The branch's own commit is de8181b0a0 (`tests/features.py` only, +23/-7). The rest is a5300ee8cd, a `ci: merge main` of b36742b17b. Its one resolved conflict is `tests/structure_budgets.json` `class_excess_loc`: main's value less this branch's unchanged -22 (17344 -> 17322, against 17356 -> 17334 at ee9bfa8ac5). Outside `tests/features.py`, the PR's own diff lines against its merge base are identical at both heads except that line. No production delta, so the review does not widen.

## Evidence

- Head: fe23416d408624f59f3d36dbbcea049d138ec764 (ev/HEAD.txt). The live PR head was re-read before posting and is the same.
- Round: third (delta over ee9bfa8ac5). `review_carry.py ee9bfa8ac5 fe23416d40`: FRESH-REVIEW, the branch's own commit de8181b0a0.
- `git merge-tree --write-tree origin/main fe23416d40` at origin/main 698eeeb2ab (32 commits ahead of this head): rc=0, no conflict (ev/merge-tree.txt).
- VERSION, manifest.json and RELEASE_NOTES.md: untouched in the three-dot diff.
- Claim files: `claims-for: 10.1.1` in both `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` at this head, at origin/main and at the merge base, against VERSION 10.1.1 at all three. The branch's three-dot claim diff adds only the three claims reviewed earlier (`price_risk`, `start_below_band`, `confidence_margins`); the merged tree's claim files differ from main's by exactly those lines. `env_drift.py --claims-only`: rc=0, `claims hygiene: origin/main ok` (ev/env_drift-claims.log).
- `merge_train.py classify fe23416d40 --pr 3736`: rc=4, APPROVAL-OWED, 3 budget raises, first `tests/stress_budgets.json` `summer/2z/space/wood-two-tank.ratio` 2.2 -> 7.46; tvofi's approval is on ee9bfa8ac5, not this head (ev/classify.txt).
- Live check runs at this head (ev/checks.txt): 33 success, 18 skipped, 4 failure. The failures are `budget-raise-gate / budget-raise-gate` (2 runs) and `gate` (2 runs), and the packet's advisory reads `gate` red only on that owed approval. `tests / fast (3.14)`, `tests / mutation`, `tests / replay`, `tests / closures` and `pr-contract / pr-contract` are success.
- Review packet (ev/packet.md): refusals none; carry_audit 3 routed, 0 unrouted; `Finder's harness: none named`.
- The finder's race harness was not re-run: the delta touches no production line. Its readings at ee9bfa8ac5 stand as recorded in that verdict.

Note: approval-owed: the three `tests/stress_budgets.json` raises (`ratio` 2.2 -> 7.46, and the new `simulate_allowance` factor 3.25 and `baseline_below` 68093) are byte-identical to ee9bfa8ac5, where tvofi approved them. This head needs that approval again for `budget-raise-gate` and `gate` to go green. The raises are recorded at measured values: 7.46 is the body's `--record-budgets` row, 3.25 covers the measured 122592/37824 = 3.2411, and 68093 is within 2 of the counts' geometric mean, 68094.9. Their necessity rests on the first fixer's race figures, which do not reproduce on arm64. The body also lists one payment, the one-seed start set d4d1b7ef7d, that fits the unraised budgets. Its arm64 race reads 0.1383 on winter_typical against this head's 0.0093, and 0.0000 against this head's 0.1210 and 0.1292 on winter_extreme and flat. x86_64 is unmeasured for both. That is a product trade-off, not a missed payment that improves the code, so this is not metric-gamed. The approver chooses it. Carry: dismissed: the approval and the trade-off are the approver's at merge; the body records both

## Red checks

`budget-raise-gate / budget-raise-gate` and the required aggregate `gate`: red only on the owed approval above (classify APPROVAL-OWED). The body's `## Red checks` names `budget-raise-gate` as red by construction. No other check is red at this head.
