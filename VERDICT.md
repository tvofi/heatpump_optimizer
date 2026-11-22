Fix review: merge 868e00db0bcfd5d3a5934412581fb8dd03c15157

bus-nonce: 034586e8c7da6cf722ab02fb476e2dc2

Round 1 (first review of #3845; no `--reviewed-head`). Measured at head `868e00db0bcfd5d3a5934412581fb8dd03c15157`; the PR head read back unchanged at the end of the review (`git ls-remote`).

## Evidence

- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` printed nothing.
- Merge: `git merge-tree --write-tree origin/main 868e00db0b` exit 0, with `LEDGER-MERGE: resolved tests/closures.json` (ev/merge_tree.txt).
- Step 1 mutation proof, re-run at the head by ev/mutant_driver.py. Each mutant is one string replacement, the named command is run, then `git checkout` restores the file. NULL: `ALL 12 FEATURES BLOCK PASSED` rc=0.
  - M1 (store.save_held `log_held` back to DEBUG): 3 of 12 FAILED, the three D1-s3-05 checks the body names.
  - M2 (unlatched `_LOGGER.error` in `_fail_update_held`): 1 of 12 FAILED, D1-s3-06.
  - M2b (latch keyed on the coordinator, not `coord.entry`): 1 of 12 FAILED, D1-s3-06.
  - M3 (`_lbfgsb_restart` DEBUG line deleted): 2 of 12 FAILED, the D1-s3-07 check and the census.
  - M4 (`handle_set_away` refusal predicate to `if False:`): 1 of 12 FAILED, D10-s1-01.
  - M5 (`publish_config` edits the shared config in place): 2 of 12 FAILED, D7-s2-03 and the ADR-003 stale holder.
  - M6 (`opt_config=ctx._opt_config,` deleted from `arbiter_inputs`): 1 of 12 FAILED, the ADR-003 stale holder.
  - M7 (coordinator `config_entry` annotation deleted): `tests/doc_claims.py` printed `1 of 443 checks FAILED`, on the D10-s3-02 census.
  - M8 (strict-typing row back to `status: done`): `tests/entities.py` rc=1 on "the manifest declares the tier the register supports cumulatively". The unmutated run printed `ALL 2740 ENTITY CHECKS PASSED`. The other `FAIL`-prefixed lines in that output are self-test negative-control echoes, which the passing null run also prints.
  - No survivor.
- Step 2: the finder's harnesses, exported from `git archive dbdc1d95fef3 dev/audit/rounds/round11`. Their sha1[:12] equal the body's (dee23d81ccb9, d10405db8aab, b2be71d66c80, 7cd70d243ae9, 976c2ebd0c6a, 6fa2a381dd2a, d0a0871eaa1f). Each was run at the body's base a8efe1d1c2a8, at the current merge base 608c95decc94 and at the head (ev/finder_harness_base_mb_head.txt):
  - svc_set_away: `acknowledged_unparseable` 6/6 → 0, `cleared_existing_return` 3/3 → 0, `control_accepted` 1/1 → 1.
  - m4_order_context: `holder_torn_fields` 2/2 → 0.
  - enum_m4: `ctx_inplace` rows 2/2 → 0.
  - platinum_rules: `untyped_requirements_under_done_row` 1/1 → 0, `coordinator_untyped_config_entry` 1/1 → 0, `coordinator_untyped_under_done_row` 1/1 → 0, `untyped_requirements` 1/1 → 1, `entry_point_bare` 0/0 → 0.
  - persist_seams: `persist_handlers` 18/18 → 0.
  - silent_broad `--seams`: 34/34 → 20.
  - Every body figure from these harnesses re-derives.
- Step 6, class enumeration:
  - silent_broad's 20 head seams are each dispositioned in the body: 5 record through a helper, 10 carry the failure as a value, 5 are secondary cleanups. Every seam falls in one of the three rows (ev/silent_broad_seams_wt.txt).
  - D1-s3-05: a grep of store saves at the head (`async_save(`, `async_save_if_changed(`, `async_delay_save(`) finds every persist save routed through `save_held`, except `_async_rewrite_entry`'s rewrite and `_async_load_manual_plan`'s two clears. Those are the 3 `propagates` the body states, under no broad handler.
  - D10-s1-01: the body's `cv.string` rule is a stated disposition list. I did not re-derive it.
- Step 3, null controls: control arms flat at both ends, as above (`control_accepted` 1 → 1, `untyped_requirements` 1 → 1, `entry_point_bare` 0 → 0).
- Step 4: `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 608c95decc94` printed `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`, rc=0. No claim file is in the diff.
- Step 5: `VERSION`, the `RELEASE_NOTES.md` heading and the manifest `version` are untouched. The manifest's `quality_scale` moves platinum → gold, which is D10-s3-01's own change, pinned by M8.
- Step 14:
  - `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
  - `score.py --diff 608c95decc94` printed `Architecture score: dS +5.7671 IMPROVES`, with the body's three rows.
  - `module_excess_loc` −12 is earned by moving the peak-tariff option parsers to `tariff.py`, beside `CapacityTariff`, whose options they parse. Their bodies are unchanged, and the move reads score-neutral.
  - `hub_solve_writes` 1 → 0 is earned by `publish_config`: removing it (M5) restores the in-place edit the row counts.
  - The unbound `CoordinatorContext.publish_config(_ctx_of(self), self, …)` call uses the tree's typed `_ctx_of` idiom (34 uses in coordinator.py), and `seam_cut_total` does not move. I do not read it as gaming the instrument.
- Step 15/16:
  - `ArbiterInputs` has one production builder, `arbiter_inputs`, and it passes `opt_config`. `early_cutoff.threshold`'s `inp.opt_config` therefore has no `None` path in production.
  - The diff adds no path that skips an actuator write. The `set_away` refusal is a service-validation refusal, raised before any write.
- Not re-derived (step 8): the lifecycle-injection port's readings (`excepts_inject.py --reach`, the 9 → 0, 3 → 0, 3 → 3 and 7 → 0 lines). They come from a fixer-side scratch reader over the finder's harness. The block checks that M1, M2, M2b and M3 fail are the in-tree pins for those findings.
- Not re-run, per "cite CI's heavy runs": the scoped gate and the mutation table.
- CI, step 11:
  - `merge_train.py classify 868e00db0b --pr 3845` read WAIT (`pending: gate red: none`) from 15:30 to 15:50 UTC. It then exited **2, unreadable**: `REFUSE selftests: the head's governance / instrument-self-tests job 137255502514 concluded cancelled, which reads no step: re-run it: an introduced red cannot be ruled out (fail closed)`. A second run read the same.
  - The head's runs show `tests / mutation` red. It is in the owed-reds set and answered in the body's `## Red checks`: the unpinned added sites, cheaper detector `ci_predict.py`, already in `prepr.sh`.
  - `governance / instrument-self-tests` has no conclusion to answer until it is re-run at this head.
- Self-audit: `carry_audit.py check --body <the body's ## Forward-carry and ## Friction sections> --comments <this verdict>` printed `CARRY-AUDIT: 0 finding item(s)`, rc=0. The packet's run over the full body at the head read the same.

## Findings

- Note: ci-unreadable: classify exits 2 at this head because `governance / instrument-self-tests` (job 137255502514) concluded `cancelled`. That job needs a re-run at 868e00db0b before the train can grade the head. This verdict holds only once classify reads GREEN at this head. Carry: dismissed: CI state at this head; the relay and the train re-read it before posting
- Note: body-figure: `## Mutation proof` says the unmutated block prints `ALL 11 FEATURES BLOCK PASSED`. It prints `ALL 12` at this head, and at 7dd02c4135 by the body's own later line. Carry: dismissed: paperwork in this PR's body, no stage downstream reads it
- Note: body-figure: `## Head` names `25f45896bb68` as a merge of the code head, which is not this head's history. `## Figures`' Structure line quotes `class_excess_loc` 17322 → 17318 and `max_class_loc` 7873 → 7865, but the diff records 17317 → 17313 and 7868 → 7860 after main's merges (same −4 and −8). Carry: dismissed: paperwork in this PR's body; the budget file is the record
- Note: harness-disclosure: the D1-s3-05/06/07 lifecycle-injection readings come through a port of `excepts_inject.py` and a scratch per-finding reader that are not in the tree. I did not re-derive them. The findings stand on the in-tree block checks and on the finder's own seam rules, which I re-ran. Carry: dismissed: the readings are corroboration; each finding is pinned by a committed check its mutant fails
