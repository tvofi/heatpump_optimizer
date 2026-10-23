Fix review: merge 488cbef71b0ded138cd75b0f1ea0542350a6f52b

bus-nonce: 2fe32f1208ceef2db69dbff9efd478aa

PR #2647, group R10-SCORES, fix round 3. This is not the fourth round, so a repair was owed, not a re-cut. Round 2 (`probe/rev-2647-c6edd5b0`, at `ff6cfdaab`) blocked on mutation-vacuous R7/R13 and on carry-missing. Both are resolved at this head.

Measured head: `488cbef71b0ded138cd75b0f1ea0542350a6f52b` (`ev/HEAD.txt`), from a detached worktree at that SHA. It was still the PR head at 07:43Z, re-read before writing this.
- Merge base: `a243a79f4` (origin/main's tip). The roles diff `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so `fix-review.md` is current.
- Round 3's code head `902acfe28` adds only `tests/features.py` (+47, two checks). The merge commit `488cbef71` adds only `dev/programme/delivery/2647.md`. There is no production diff since round 2.
- Toolchain: `/opt/hpo/venv-ci/bin/python`.

## RESULT

RESULT r7_mutant_with_pins=red (1 of 4330: "#2258: a restore asks for a cycle, ...")
RESULT r7_mutant_without_pins=green (ALL 4328, tests/features.py at 19319cc13)
RESULT r7_delete_mutant_with_pins=red (1 of 4330, same check)
RESULT r13_mutant_with_pins=red (1 of 4330: "#2258: one cycle view offers the refit and grades the house against it")
RESULT r13_mutant_without_pins=green (ALL 4328)
RESULT null_control=green (ALL 4330 FEATURE CHECKS PASSED)
RESULT carry_audit=7 routed, 0 unrouted, 0 bad
RESULT seam_cut_total base=708 head=714 (re-derived by my own per-unit probe and by structure.py)
RESULT archscore=dS +0.0105 IMPROVES (coord_footprint 2489 -> 2471)
RESULT ci_predict=no closures or fast red predicted
RESULT merge_tree=clean (rc 0)
RESULT ref_privacy_round3=rc 0 (902acfe28, ac0ca52b3, 488cbef71)
RESULT ci_red=budget-raise-gate only (answered)

## Brief items

### (1) R7 and R13 are no longer mutation-vacuous

Each mutant was planted alone in a copy of the head and run with `PYTHONPATH=tests/hastub tests/features.py`.

- **R7.** At coordinator.py:9525, `await self.async_request_refresh()` becomes `self.async_update_listeners()`.
  - Result: `1 of 4330 FEATURE CHECKS FAILED`. The failing check is `#2258: a restore asks for a cycle, and that cycle's advice offers no refit and grades the house on the restored scale` (`refreshes 0`).
  - A stronger variant replaces the line with `pass`. It fails the same check.
- **R13.** At coordinator.py:10575, `self._scores_view(advice)` becomes `self._scores_view({})`.
  - Result: `1 of 4330 FEATURE CHECKS FAILED`. The failing check is `#2258: one cycle view offers the refit and grades the house against it`.
  - Under R13 the envelope grades 58.3 with no `envelope` reason while the advisor offers 1.16.
- **Without the pins.** I put `tests/features.py` from `19319cc13` back into the same two mutant copies. Both read `ALL 4328 FEATURE CHECKS PASSED`.
- **Null control.** The unmutated head reads `ALL 4330 FEATURE CHECKS PASSED`.
- **The ledger.** `tests/mutation_table.py --list <kind>`, over every ratcheted kind, generates no site at 9525 or 10575. The only nearby site is 9526 `return True` RETURN_DEL. It is UNPINNED, but it predates this branch (blame `86425b9ad`).
  - So R7 and R13 have no ledger row and no `killed_by`. Their pins are the two features checks, as the body says.
  - The 25 ledger rows the branch adds or renames carry `killed_by` `tests/features.py` (23) or `tests/structure.py` (2) (`ev/ledger_rows_killed_by.txt`).
- The R7 check kills through the stub's `refresh_requests` counter. Its view assertions hold under the mutant, because the test calls `_insight_view()` itself. The counter pins the production line, which is what the design verdict asked: "both must refresh".
- Evidence: `ev/mut-*.diff`, `ev/mut-*-features*.log`, `ev/mutants_summary.txt`, `ev/ledger_sites_R7_R13.txt`.

### (2) The three carries resolve on the roster

`59c2ebc02`, `524d335a0` and `1f27f9daf` are each a `roster_edit append-carry` commit and an ancestor of `origin/handoff/audit-r10-roster` `bb7c6eb27`. I read each group's `carry[]` back at that tip (`ev/carries.txt`).
- R10-LEARNER-ETA, R10-UX-HEALTH and R10-ARCH-DOCS each hold the body's Forward-carry text verbatim, prefixed `(from R10-SCORES #2647, Forward-carry)`.
- `carry_audit.py check --body` reads `7 routed, 0 unrouted, 0 bad destination(s)` here (`ev/carry_audit.txt`) and in CI's `pr-contract`.

### (3) The seam_cut_total raise (708 -> 714) is honestly unpayable

- **Where the +6 sits.** I re-derived it with my own instrument, `ev/probe_seam_units.py`: per-unit crossings counted by `structure.py`'s `seam_metrics` rule. Base and head read 708 and 714, matching `structure.py` (`ev/seam_units_diff.txt`). The cause:
  - **+5 `model_restart_advice`.** The cycle now hands it the coordinator, so it becomes a priced helper. Its four reads (`_accuracy`, `_config`, `_house_heat_loss_scale`, `_thermal_params`) cross views, and the scale also crosses learning. This is the design's holder: advice taken once per cycle.
  - **+1 net in `_scores_view`.** It adds `_house_heat_loss_samples` (+2, the convergence dash) and `_score_day` (+2, the operation reason). Three `_thermal_params` reads collapse into one (-3). The restore's refresh swap is net 0.
- **Each payment the body lists**, judged against that table:
  - (1), (2) and (4) are taken. They moved code out of the class, and `class_excess_loc` and `max_class_loc` now sit under main's budget.
  - (3), the in-place write and the reassignment, was correctly refused. Archscore and `coordinator_attrs` respectively rule it out.
  - (5), a re-seat to `learning`, measures 714 with my probe, so it buys nothing. That agrees with the body.
  - (6) and (7) only move the same reads, or hide them.
- **Payments I hunted that the body does not list:**
  - Re-seat `model_restart_advice` to `core`: it reads 711. It is a relabel of the seam map, with no code moved and no read removed. That is gaming the score, which pays nothing, so it is not a payment.
  - A core or grid method composing the operation `(grade, why)` so that `_scores_view` stops reading `_score_day` and `_operation_score`: by the rule, -4 +2 +1 = -1 on the seam cut. It adds a unit to the coordinator span, though, and `class_excess_loc` and `max_class_loc` are at zero headroom. It trades one capped metric for another and does not improve the architecture.
- No unpaid payment improves the architecture. The `## Raise justification` lists each payment with the `Architecture score: dS +0.0105` line, and I re-took archscore at the head: `dS +0.0105 IMPROVES`.
- The raise itself is main's to rule under the mandate; I did not judge it.

### (4) Author identity

- **Footers.** `ref_privacy.py guard --commits` judges only commits no remote-tracking ref holds. I ran it in a scratch repo where the only remote refs were origin/main `a243a79f4` and the previous head `ff6cfdaab`, so it judged exactly this round's three commits (`902acfe28`, `ac0ca52b3`, `488cbef71`). The result was rc 0, no refusal (`ev/ref_privacy_round3.txt`). This round's messages carry no attribution class.
- **Author identity is not refused.** The guard reads only the author and committer emails. `noreply@anthropic.com` is a public domain, so `host-email` passes. The author name "Claude" is not judged by any class.
- **The whole range.** Run against only origin/main, the guard refuses `co-author-trailer` on `ff6cfdaab` (rc 3). Rounds 1-2's Claude-authored commits carry session-link, session-trailer and co-author-trailer (`ev/attribution_per_commit.txt`). The brief scopes footers to this round, and those commits are already on the remote, so this does not block.

### (5) Red checks

- **CI read.** I read CI with one bulk read: `commits/488cbef71/check-runs?per_page=100`, 41 runs, all completed (`ev/check-runs.json`, `ev/check-runs.txt`).
- **The only red is `budget-raise-gate`** (two runs): `RAISE tests/structure_budgets.json: seam_cut_total: 708 -> 714` and `REFUSED: no decisive review by tvofi`. The body's `## Red checks` names it and answers it.
- **`pr-contract` checked the body after the red.** The run that started at 06:46:10Z, after the last red concluded at 06:45:59Z, is green. It shows no version edit and `CARRY-AUDIT ... 0 unrouted`.
- **`mutation` is green, and its log separates the cases** (`ev/ci_mutation_summary.txt`):
  - the baselines for env_drift, features and entities are rc 0;
  - the null control survived;
  - `PIN RE-VERIFICATION: 5 reproduced`;
  - `0 survivor(s) of 5 evaluated`;
  - `MUTATION TABLE PASSED`.

  It was evaluated, not INCONCLUSIVE.
- **The rest.** `fast (3.14)` is green (07:42Z), and so are `closures`, `env-matrix`, `coverage`, `browser`, `typing` and `instrument-self-tests`. `nightly-status` is green.
- **`ci_predict`.** `tools/pr/ci_predict.py --base origin/main` at the head reads `CI PREDICT: no closures or fast red predicted`. No ADDED UNPINNED and no stale pin means no mutation red is predicted (`ev/ci_predict.log`).

## Other steps

- **Step 2/9, the harness.** The roster group's `harness` is null. The design's finder harness (`study-reseed/live_store.py`) needs the owner's bundle. That arm stays carried to R10-PARAMS-OWNER (`c3711a1f0`), as round 2 found. Round 3 moved no production line, so round 2's both-ends envelope measurement stands.
- **Steps 4 and 5.** Neither claim file nor any golden moved in round 3. `VERSION`, the manifest and the notes heading are untouched (the diff is 0 lines, and pr-contract reads no version edit).
- **Step 7.** The body's head and code head (`902acfe28`) match what I measured.
- **Step 13.** `git merge-tree --write-tree origin/main 488cbef71` exits 0 with no conflict (`ev/merge-tree.txt`).
- **Step 14.** The structure budgets are as above. `structure.py` reads `STRUCTURE RATCHET PASSED` (`ev/structure.log`). The two falls are earned by the payments that moved code out of the class (`ev/structure_base_results.txt` against `ev/structure_head_results.txt`).
- **Step 15.** The added lines are two test checks, with no architecture change.

## Findings (non-blocking)

- **The three new carries state no control.** The LEARNER-ETA carry states its precondition ("must read it, never a second threshold"), but none of the three names the check that would show a breach. UX-HEALTH and ARCH-DOCS record facts about what landed rather than a measured finding, and the destination stages re-measure at their own merge base. The predicate's own control, `#2258: Health's learned and the score's heat_loss_learning are one predicate`, is in the tree. Carry: dismissed: the destinations hold the precondition text and the control check is in the tree, findable by its name.
- **The `core` re-seat reads 711 and is not a payment.** That relabel and the operation-part method are recorded under (3) so a later seat does not re-hunt them. Carry: dismissed: neither improves the code, so neither is owed.
- **The PR body repeats a heading.** It carries a malformed `## Mutation proof`), ...` heading line, which yields two `## Mutation proof` sections. It is cosmetic, and `pr-contract` is green. Carry: dismissed: cosmetic, no reader is misled
- **Rounds 1-2's commit messages carry tool-attribution trailers.** They are refused by `ref_privacy` when the full range is judged; see (4). The brief scopes footers to this round's commits. Carry: dismissed: already published, outside this round's commits by the brief's scope
