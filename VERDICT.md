Fix review: blocked 08ba3d9d7b115bf4f8b0f592d34397862622c5a3 metric-gamed: seam_cut_total: the route-1 payment is a local alias of self.currency that only cuts an occurrence count; the same alias planted on self._prices with nothing improved moves the metric further

bus-nonce: 62684c0b8e02184e0fc78a37e44faa7f

Round: 2 (the first full review of this head, after round 1 stopped at seam_cut_total 709 > 708).
Roles contract: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the copy is current.

## Block

Rule 14 (fix-review.md). The body's route 1 pays `seam_cut_total` 709 -> 708 with one hunk in `_raise_cop_issue`: `currency = self.currency`, and the two reads now read the local. Behaviour does not change. The body says so itself: the new R10-CURRENCY check "cannot fail on any shipped tree", because `_raise_cop_issue` already read `self.currency`.

- **Remove the mechanism.** At the head I inlined the alias back to two `self.currency` reads and kept the corrected comment. `tests/structure.py` then reads `seam_cut_total=709` and exits 1 (ev/structure_unalias.txt). The whole payment is the alias. The comment correction moves no metric.
- **Plant the same move with nothing improved.** At the head I aliased `prices = self._prices` in the same method (ev/plant.diff). `seam_cut_total` reads 706, down 2 (ev/structure_plant.txt). `structure.py` counts attribute-reference *occurrences* that cross a seam (`structure.py` ~L1076-1118). An extraction of `learning` would still have to make each attribute explicit exactly once, so binding a local cuts the count without cutting the coupling. The plant reproduces the movement, and the diff's change has exactly that shape, which rule 14 blocks.
- **Architecture score:** `score.py --diff 4d407a35f HEAD` prints `dS +0.0000 NULL` (ev/archscore.txt). The payment does not read as better, and CLAUDE.md rule 2 says gaming the score pays nothing.
- The +1 LOC that the alias costs on `class_excess_loc` and `max_class_loc` was paid by shortening a comment. That part is legitimate, but it pays for the alias, not for an improvement.

What would clear it (for the orchestrator, not prescribed): a payment that removes a real cross-seam dependency. Failing that, a `seam_cut_total` raise under 0013, either with the owner's approving review or under a mandate scoped `budget-raise`/`all`, with a `## Raise justification`. The fix itself (the narrative and the comment) is sound and stands. See Evidence.

## Findings

- The structure instrument counts cross-seam attribute occurrences, not distinct attributes, so aliasing a `self.<attr>` read into a local lowers `seam_cut_total` with no structural change. The `self._prices` plant here gave -2. Every seam-cut payment is exposed to this. It is an instrument finding: per rule 14 it goes to the structure ratchet's owner, not to this fix. Carry: dismissed: owed by the orchestrator to the structure-ratchet stage via finding-propagation.md, which this reviewer cannot route to a group or issue from a cloud seat; raised here so it is not lost.
- `pr-contract` is red on this head (job 120045400798, and 120032771136 before it). `carry_audit.py` refuses the body: `UNROUTED body item fb7bb9ae (## Friction)`. The Friction bullet's `Carry: orchestrator.md section 5` is not a valid destination (`<GROUP> | #<issue> | O<n> | dismissed: <reason>`). The body has to route or dismiss it before this PR can merge. Carry: R10-CURRENCY
- Rule 11: that red check is a gate check, and the body's `## Red checks` names only the local structure.py red, not `pr-contract`. It owes an answer (the cheaper detector: `carry_audit.py check --body` run locally before the push). Carry: R10-CURRENCY

## Evidence

- Head measured: 08ba3d9d7b115bf4f8b0f592d34397862622c5a3, still the branch head at review (`git ls-remote`). Merge base 4d407a35f. No reviewer-turn move, so step 12 does not apply.
- Null control (brief item 2), finder's harness `dev/audit/rounds/round10/D14/s3/p8_replay_currency.py`, sha1 1acaac17… (identical at base and head), run from each tree:
  - base 4d407a35f: RESULT base_mismatched_seams=1, clean_mismatched_seams=0, narrative_fixed_mismatched_seams=0, reintroduce_mismatched_seams=14 (of 14).
  - head: RESULT base_mismatched_seams=0, clean_mismatched_seams=0, narrative_fixed_mismatched_seams=0, reintroduce_mismatched_seams=14.
  - The reintroduce arm reads 14 and the clean arm 0 at both ends, as the brief requires.
- Mutation proof (step 1):
  - Head: `ALL 4303 FEATURE CHECKS PASSED`.
  - `_narrative_view` mutated back to `resolve_currency(hass)`: `1 of 4303 FEATURE CHECKS FAILED`, the D14-s3-01 check, `{'EUR/kWh': ['SEK'], 'SEK/kWh': ['SEK']}`.
  - `_raise_cop_issue` mutated to `currency = resolve_currency(self.hass)`: `1 of 4303 FEATURE CHECKS FAILED`, the R10-CURRENCY check. Disclosure: my sed also hit an identical pre-existing line at coordinator.py:7121, but the only failure is the R10-CURRENCY check, which matches the body's single-line mutant.
  - Both mutants were restored, and the tree is clean.
- Structure ratchet (brief item 3): head `STRUCTURE RATCHET PASSED`, `ok seam_cut_total 708 <= 708`, class_excess_loc 18272 and max_class_loc 8514 at their caps. No budget file in the diff, so no raise. It passes only through the payment blocked above.
- #2243 (D14-s3-01) is substantiated: the harness base arm goes 1 -> 0 and the narrative check pins it.
- #2222 (D5-s3-01) is substantiated: comment_symbols `MISSING coordinator.py \`money_currency\`` is present at base and absent at head, and that is the only difference between the lists. Absolute figures at this base are untriaged_missing 10 -> 9. The body's 7 -> 6 was taken at its older base 50808a755, which I did not re-derive; the delta of -1 matches.
- Class (step 6): `grep -rn "resolve_currency(" custom_components/` lists 10 call lines at base (ev/class_enum_base.txt). After the fix, those left are the instance-labelled ones the body dispositions (`__init__`, `_audit_price_units`, `config_flow.py`).
- VERSION, the manifest version, RELEASE_NOTES and goldens are untouched (empty diff), so no claim files apply.
- Merge: `git merge-tree --write-tree` exits 0 against both 4d407a35f and the current origin/main 86425b9ad.
- CI on the head (check-runs API):
  - Green: fast (3.14), coverage, typing, mutation, arch-score, budget-raise-gate, browser, env-matrix, hassfest, policy-docs, CodeQL.
  - `closures` was still in progress.
  - `pr-contract` is red (see Findings).
  - `nightly-status` is red; it is not this PR's, since the diff does not reach what it reads (fix-review.md 11).
- Harness setup: deps came from tests/requirements-ci.txt pins installed into a scratch venv without hashes (the hashed install refused on typing_extensions under this python). Disclosed as my environment, not the finder's.
