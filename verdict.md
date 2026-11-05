Fix review: blocked 611e1aa6fc004d5f5666ca99efc402a1003c0849 ci-red: gate failed at this head on tests / mutation's unpinned-site refusal; the bot pin commit 8050a943c that cures it is a new head, and a red CI never carries

bus-nonce: 6d48b5899c0bdc26905658f948dade19

This is the third fix review of #3195 (R10-SAV-COMFORT part 3). It is a delta review after verdict/3195 blocked `c383169a5` with `ci-red`. The body's "Fourth round" counts the fixer's rounds. I measured head `611e1aa6fc004d5f5666ca99efc402a1003c0849`. `review_carry.py c383169a5 611e1aa6f` printed FRESH-REVIEW because of the repair commit `3ed99bc46`, so that commit was reviewed in full. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current. I reviewed from a detached worktree at the head.

## Block

- `gate` (127051493004) concluded `failure` at 04:39:22Z, and its only line is `FAIL tests / mutation: failure (this run)` (`ev/job_127051493004.tail.txt`).
  - `tests / mutation` (127014280973) is the unpinned-site refusal: `MUTATION TABLE REFUSED -- 3183 unpinned site(s) against 3174 at the ratchet base 7c274274..., 12 of them added by this diff`.
  - `merge_train.py classify` exited 1: `RED 611e1aa6... pending: none red: gate` (`ev/classify.txt`).
- This red is the one `ci-autofix.md` expects. All three `mutation-pins` shards killed every site they drove: `PIN KILLED: 4 pinned, 0 left unpinned` each. `mutation-autofix` then pushed `8050a943c` (`ci: pin killed mutants`), which adds 11 `killed_by` anchors and nothing else.
  - `review_carry.py 611e1aa6f 8050a943c` prints `CARRY` (`ev/review_carry.txt`), so the patch is the one I reviewed.
  - `fix-review.md` step 12 says a red CI never carries. A merge verdict therefore needs `8050a943c`'s own CI to come back green.
- Owed: a CI-only delta at `8050a943c`, which `review_carry` reports as CARRY. If `gate` is green there, every result below carries. Nothing in the reviewed patch needs to change for this block. The PR body's `tests / replay` line is a separate repair, under Findings.
- Last round's block is cured.
  - `prelude` no longer outlives its cap: shards 1, 2 and 3 ran 41 min, 42 min and 52 min, against 8700 s (`ev/check_runs.tsv`).
  - `pr-contract / pr-contract` (127051257852) concluded `success` at 04:34:38Z, after the `mutation` and `replay` reds.
  - The two `cancelled` prelude/gate pairs belong to the superseded `CI edit` runs 41956875918 and 41956961819. The `CI code` run 41956875245 carries this head's gate.

## Findings

- M2 still survives. In the two-zone branch, `zone = lowers` → `zone = rooms` (`optimizer.py:468`) fails nothing beyond the null control's environmental FAIL (`ev/mutant_12_EXTRA_M2_468.log`). The new comfort checks drive only `two_zone=False`. Verdict/3195 listed M2, but the body neither fixes it nor routes it under `## Forward-carry`, which names only M13, M3 and M9/M10. Carry: R10-SAV-COMFORT
- The body says "A mutant that crashes fails a named check (the call is wrapped)". That holds only for the state-field checks. The comfort loop and the baseline check index `_sw_run`'s `repr` string result. Under `optimizer.py:454 BOOLOP` and `optimizer.py:515 CMP_BOUND`, `tests/features.py` aborts at line 42881 with an uncaught `TypeError: string indices must be integers` (`ev/mutants_results.txt`). Both mutants are still killed by named checks that fail before the abort. Every check after that line goes unrun. Carry: R10-SAV-COMFORT
- `## Red checks` gives `tests / replay` a stale account. It says the cause is `synthetic-dhw-only.json` `cpu_ratio` over budget and calls it "Green at `c383169a5`". At this head, `tests / replay` (127019165648) is red with `4 of 181 replay checks FAILED`. Every FAIL reads `runner class unknown: ref_ms 20.54 lies in no band of COST_RUNNER_CLASSES`, with no budget assumed (`ev/job_127019165648.tail.txt`). The runner's speed fell between the bands. `gate` does not list it. The body owes a line for this head's replay red. Carry: R10-SAV-COMFORT
- The `COST_RUNNER_CLASSES` table has no band for a runner with `ref_ms` ≈ 20.3–20.7. That runner can redden `tests / replay` whatever the diff. This belongs to the replay cost budget's owner (#3174 merged it), not to this PR. Carry: R10-REPLAY-COST-BUDGET
- The body routes the test gaps M13 (`baseline_kw` end to end through `get_current_action`), M3 (the midpoint rule) and M9/M10 (calibrated-month scaling) as "Carry: #2492". Neither #2492's body (no comments) nor the roster group on `handoff/audit-r10-roster` states them yet. The body's `Carry:` line is the only record. Carry: #2492
- Carry 5 and the summer start-bound limit stay residual on #2492, as the body's `## Forward-carry` says. Carry: #2492

## Evidence

- Mutants: `ci_predict.py` at this head lists 11 sites. They are the body's 11 (`ev/ci_predict.txt`); CI counts 12 mutants because `:512 CLAMP_DROP*2` is two. I applied each mutant that `tests/mutation_table.py::_generate` produces for those lines, exactly as the tool generates it. I ran the full `tests/features.py` on each, in a copy of the tree without `.git` (`ev/mutants_run.py`, `ev/mutants_results.txt`). The unmutated copy (NULL) prints `1 of 4810 FEATURE CHECKS FAILED`. That one FAIL is `#363 recorded_at = 'unknown'`, which reads git metadata, so it appears in every row and is environmental. Every mutant adds at least one named R10-SAV-COMFORT FAIL:
  - `ledger.py:309 CLAMP_DROP`: the zero-COP check fails with `ZeroDivisionError`.
  - `optimizer.py:485`, `:488`, `:497`, `:500 GUARD_OFF`: the state-field checks fail (4, 2, 4 and 2 of them).
  - `:515 GUARD_OFF`: the baseline-coverage check fails.
  - `:454 BOOLOP`, `:454 CMP_BOUND` and `:515 CMP_BOUND`: the state-field checks fail, and the first and third also abort the run (see Findings).
  - `:493 CLAMP_DROP`: the COP-floor check fails.
  - `:512 CLAMP_DROP` (each half): the zero-floor comfort check fails at outdoor 20.2.
  - CI agrees: `mutation-pins` (1), (2) and (3) each print `PIN KILLED: 4 pinned, 0 left unpinned` (`ev/job_*.summary.txt`).
- Every site verdict/3195's block listed is accounted for:
  - `:454` BOOLOP and CMP_BOUND are killed.
  - `:485` and `:488` GUARD_OFF are killed.
  - `:494` CMP_BOUND and GUARD_OFF are now `:493` CLAMP_DROP (killed): `if cop < 1e-3: cop = 1e-3` became `max(..., 1e-3)`.
  - `:499` GUARD_OFF is now `:497` (killed).
  - `:519` CMP_BOUND is now `:515` (killed).
  - The body's equivalence reasoning for the old `<=`/`>=` mutants holds: at equality the assignment writes the value it already has.
- The rewrite is not `metric-gamed`. It is behaviour-identical, and every finder-harness figure is the same as at `c383169a5`. The kills come from the new checks, which fail under the new shape's own mutants. `## Unpinned sites` lists only sites that survived until the pins lane ran, and none survives it.
- Mutation proof: in `savings_months`, `baseline_sek ... * scale + stored_sek` became `... * scale`. The named FAIL `R10-SAV-COMFORT: the month row settles the plan's stored-heat change at the row's metered kWh price` appears beside the environmental `#363` (`ev/mutant_13_PROOF_429.log`). In a git checkout, the unmutated `tests/features.py` prints `ALL 4810 FEATURE CHECKS PASSED`, matching the body's 4810.
- Finder's harness at this head (`dev/audit/harnesses/r10_sav_null_settled.py`, sha1 `eca29a18...`), rc=0 (`ev/null_settled_head.txt`):
  - vary: saved 32.16 (19.23 %), `stored_heat_sek` 13.15, `comfort_sek` 8.28, comfort-matched 23.88 (+14.28 %), SOUND.
  - const: saved 6.62 (4.77 %), `stored_heat_sek` -11.15, `comfort_sek` 6.23, comfort-matched 0.39 (+0.28 %), SOUND.
  - Null control (no readings): vary 12.34 %, const 11.86 %.
  - `r10_sav_baseline.py transient`: spread 0.00 kW, SOUND (`ev/baseline_transient.txt`).
  - Every figure in the body re-derives exactly.
- `tests/closure.py select --diff <merge-base>` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` `tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Merge: `git merge-tree --write-tree origin/main 611e1aa6f` exits 0 against `7c274274` with tree `7c165900a`. Its stderr says `LEDGER-MERGE: resolved tests/closures.json` and has no MERGE-CLAIM line (`ev/merge_tree.txt`).
- These are empty in the three-dot diff against merge base `499162c89`: `VERSION`, `manifest.json`, `RELEASE_NOTES.md`, `tests/golden/`, and the structure, mutation and typing budget files.
- Other reds at this head:
  - `governance / delivery-status` (127014280946) is OVERDUE on rows #3174, #3091, #3089 and #3192, not #3195. This PR's own row file was not flagged.
  - `tests / nightly-status` (127014280889) says `NIGHTLY FAILED: record-autofix failed`, which grades main's nightly.
  - Neither is this PR's. On main's latest commits, `tests / replay` is `skipped` by scope, so there is no base ancestry red to cite for replay.
- Green at this head: `fast (3.14)`, the three `mutation-pins` shards, `pr-contract / pr-contract` and `budget-raise-gate`. The full check list is in `ev/check_runs.tsv`.
- The head moved after measurement, to `8050a943c`. That is the bot's pin commit, and `review_carry` reports CARRY, so this is not `head-moved`. None of my local numbers depend on the ledger rows it adds.
- Figures I did not re-derive: the 5000-input bit-identity claim of earlier rounds. The body drops it, and the script is outside the tree.

## Friction

- The container restarted once during the CI wait. The background classify watcher was lost and re-armed. No local result was lost.
- `classify` returned RED early, at 03:18Z, on a `cancelled` gate from a superseded `CI edit` run. I waited for the `CI code` run to complete before taking its verdict.
- I pushed no `handoff-wip`. The brief allows only the probe return ref.
