Fix review: merge 889c15e5efd254e5d4ca2e00cbeeda29978f04eb

bus-nonce: 9dedf3b648ee5c41deb4a3bfc9ddffaf

Round: 2 for this PR. This is a delta review of 3b437b851..889c15e5e. Round 1 blocked 3b437b851 as mutation-survivor.
Head measured: 889c15e5efd254e5d4ca2e00cbeeda29978f04eb. I re-read it at the end of the review (`ev/head_recheck.txt`), and the branch and refs/pull/2817/head both still point at it.

## Delta

The delta is four commits on the first parent:
- f130a7c2c is the bot's ledger pins for 24 killed mutants at 3b437b851.
- 9e401f833 adds two checks in `tests/features.py`.
- 9a45eca1b merges 9e401f833.
- 889c15e5e merges origin/main 16c6b9e8f.

Main's merges bring in only triage and delivery records and the `tools/site` lockfile. Those are not in the three-dot diff, because 16c6b9e8f is the merge base. The delta changes nothing under `custom_components/`, `tools/audit/` or `dev/audit/` (`ev/delta_scope.txt`). So every round-1 figure taken on the production tree carries unchanged: seam edges, placement null control, archscore dS, the finder's harnesses and the D15 reconciliation. The checks I re-took because the delta could touch them are listed below.

## Findings

- Contention with #2819, whose head is now 734ad21fa (it moved from 6feac7ece). `git merge-tree` of the two heads exits 0 with `LEDGER-MERGE: resolved tests/structure_budgets.json`. But `tests/structure.py` on the merged tree exits 2 on an unrecorded gain: `functions_cc_over_15` measures 28 against a merged budget of 29, the same as in round 1. `seam_cut_total` measures 424, within budget (`ev/structure.merged_with_2819.txt`). Whichever of the two PRs merges second has to re-record that row. Carry: R10-PARAMS-OWNER | #2232 | O1 | dismissed: serial budget-file merge, the orchestrator's merge train re-records the gain on the second merge; no defect in either diff

## Evidence

- The round-1 block is resolved. Each mutant is applied to a `git archive` of the head, then the whole of `PYTHONPATH=tests/hastub python3 tests/features.py` runs (`ev/features.*.txt`):
  - RESULT baseline (head): 1 of 4414 checks fails. It is the archive-only #363 check ("the path that proceeds still stamps a resolvable recorded_at"), as in round 1.
  - RESULT m6303 (`coordinator.py:6303` `if "ecl110_displace_min" in params:` -> `if False:`): 2 of 4414 fail, +1 over the baseline. The new failure is "the lower displace limit is mirrored where the publisher clamps against it" `[mirror -20.0, params -7.5]`, which matches the body exactly.
  - RESULT m6331 (`coordinator.py:6331` the DHW profile save -> `if False:`): 2 of 4414 fail, +1. The new failure is "an explicit cooling rate is saved with its reset count, so a restart keeps it" `[profile saves []]`, which matches the body exactly. The `[]` is also its own null control: no other path saves the profile during the call, so the check cannot pass on an incidental save.
- The new checks are value checks on the published snapshot and on the store's `async_save` payload, not checks of the source text. The capture wrapper is restored after the call. Neither one re-implements a production formula.
- CI `tests / mutation` at this head (job 121272006294, `ev/ci_mutation_head.txt`) reads "MUTATION TABLE REFUSED -- 3945 unpinned site(s) against 3957 at the ratchet base c9cbe6b45, 2 of them added by this diff". The two are exactly `ADDED UNPINNED coordinator.py:6303 GUARD_OFF` and `coordinator.py:6331 GUARD_OFF` (`ev/ci_mutation_head_added.txt`). The other 24 were pinned by f130a7c2c.
  - The two now die locally, as shown above. `tests / mutation-pins (1)` was queued when I posted. The body's 25 rows are now true: 23 are bot-pinned, and the 6303 and 6331 rows name their killing checks.
  - The ledger at the head reads `completeness_problems 0`, so no pin is stale (`ev/ledger.head.txt`).
- The bot's pin commit f130a7c2c is authored by github-actions[bot]. Its 24 `killed_by` files each record a `--pin-killed` rc change on `tests/features.py`. No pin was written by hand.
- Structure at the head (`ev/structure.head.txt`): RESULT seam_cut_total=424, `ok seam_cut_total 424 <= 424`, STRUCTURE RATCHET PASSED, rc 0.
  - Current main c9cbe6b45 still measures 419 (`ev/structure.main_c9cbe6b45.txt`).
  - The budget diff against the merge base is unchanged from round 1: seam_cut_total 419 -> 424, with class_excess_loc, functions_cc_over_15, max_class_loc and methods_over_150 lowered (`ev/budget_diff_vs_base.txt`).
- The round-1 findings O1, O3 and O4 were wording only. The body now names the twice-priced `_price_model_store` pair as the fifth cut. It says the bundle arm has no null control and defers to the D15 record, and it discloses `r10_scores_envelope.py` as this PR's edit of the finder's harness (sha1 f45215cf against 272d5175). Round 1's O2 was an instrument finding, carried there, and the delta does not touch it.
- Merge: `git merge-tree --write-tree origin/main 889c15e5e` against main c9cbe6b45 exits 0, tree d9dedc36f, no conflict (`ev/merge_tree.txt`). `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched. The delta names no host or home path.
- CI at this head when I posted:
  - `budget-raise-gate` is red by design until the mandate approval; the body answers it under `## Red checks`.
  - `tests / mutation` is red on the two added sites; the body answers it, the new checks kill both sites, and `mutation-pins (1)` is queued to pin them.
  - Passed: `validate-hacs` and CodeQL for JavaScript and Actions.
  - Still queued: `closure-scope`, `wave-script`, `hassfest`, `briefs`, `policy-docs`, `nightly-status`, `arch-score`, `instrument-self-tests`, `delivery-status` and `env-matrix`. CodeQL for Python and one prelude are in progress.
  - I did not re-run heavy CI (fix-review step 11).
- I left `env_drift --all` to CI: the delta writes no golden or claim file.
