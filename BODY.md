This is roster group R10-STORE. The persistence boundary in `store.py` now owns four rules: how a restore starts (its load prelude), when a save is skipped (its digest), what the debugger and the replay tools report about a stored document (its report rules), and how far ahead of the clock a stored instant may lie. The coordinator only calls these rules. The price learner owns the days it has folded.

Closes #2224.

Part of #2232, Part of #2236 and Part of #2238. Each of those issues covers a whole class, and this group closes only its own findings in each.

**D1-s2-01 (#2224), the defect.** The snapshot store was built with `lead=0`, but the ring embeds the accuracy learner's payload, and that payload holds promises falling due up to `max(LEAD_BUCKETS)` hours ahead. So every restart rewrote each pending due to "now" and logged one WARNING per due. A rollback to such a snapshot would restore promises that are all due now.

**The fix the cause asks for: a field declares its own lead.** `Domain` gains `ahead_h`. `lead_pending/#/0` declares `ahead_h=max(LEAD_BUCKETS)`, and `_bound_instants` now walks the store's `DOMAINS` trie beside the payload. A field's allowance is therefore its writer's declaration, and it travels through every `DOMAINS` alias, which is how an embedded payload is declared. Because of that, the accuracy store's store-wide `lead=24 h` is no longer needed, and the coordinator drops it. As a result, the accuracy store's past instants (`samples/#/t`, `evidence_since`, the comfort stamps, `promises/*/start`) are now bounded at the clock again. This tightens the round-9 property rather than loosening it.

**Alternatives, and why each lost (fixer.md step 17):**
- *Give the snapshot store (and the debug ring) the accuracy store's 24 h lead.* This is one line and closes the instance. It loses because it would also accept a clock-ahead `taken_at` and debug `started_at` up to 24 h ahead, which reopens the round-9 window on the host's own stamps (`snapshots.py` `due()` reads `taken_at`, and `DebugCollector` bounds collection by `started_at`). It would also keep two sources for one lead.
- *A registry of leads by store name, filled in at construction.* This loses because it is module state that depends on construction order, and it would be a second mechanism beside the `DOMAINS` declaration that already says "the domains are the writers'".
- *Move every store's lead into `DOMAINS` (boost and manual-plan expiries too).* This is the end state, but it would touch `boost.py`, `away.py` and the manual-plan wiring, which are outside this group's files. The store-wide `lead` stays for stores whose instants are all expiries, and `ahead_h` covers a field that another store embeds.

**D7-s4-81, the notifier's load prelude (a P1 instance under #2236).** The finder's ARCH2-s4 P2 is applied. The ledger, price-model, accuracy, energy and snapshot loaders, the DHW draws loader and the notifier all now start from `store.load_mapping`. A notifier store holding valid JSON that is not a mapping no longer raises out of entry setup.

**#2232's owner moves (ARCH2-s2 P3 and P7) and #2238's (ARCH3-s6 P3), applied as the finder prototyped them.** `QuarantiningStore.async_save_if_changed` owns the digest: a plain `async_save` forgets it, and it is recorded only after a save returns. `PriceShapeLearner` (in `price_model.py`) owns the shape and both seen-sets, together with their fold, store and restore. The coordinator keeps a read-only `_price_model` property. `store.store_name`, `store.off_domain` and `store.quarantines` replace the copies in `debugger.store_report`, `store._log_off_domain`, `tools/replay/debug_ingest.domain_suffix` and the two `_sanitize` comparisons. Forward-carry (2) is followed: the debugger and replay interfaces are exactly as the P3 patch left them.

## Head

`766b5eb46eb21892f8d87a3853269a679ff5e4f9`. Three commits sit on the fork `6e5753a4a`:
- `40ad33528`: the fix.
- `558d113d0`: `quarantines` returns a `bool` (the typing ruler's `no-any-return`), and the five mutation-ledger pins whose lines this branch rewrote are dropped.
- `766b5eb46`: records the structure rows this branch improved.

There is one merge of origin/main, `e11222c5c` at main `e5f7e169d`. It needed no resolution, and main's delta touches no file in this diff (`git diff --stat HEAD^1 HEAD -- custom_components tests/finite_boundary.py tests/features.py tests/mutation_ledger` prints nothing). Main-merge catch-up count: 1.

Every figure below was taken three-dot against merge base `e5f7e169d` (main's tip at 2026-10-18).

## Mutation proof

Each mutant is applied to a detached copy at the head by `mutate.sh` (scratch), run under the named script, and restored with `git checkout`. Each mutates the predicate, not the tail.

- M0, a comment-only edit to `store.py` (null): `tests/finite_boundary.py` rc=0, 0 FAIL.
- M1, `lead_pending/#/0` declared `_AT` again (the field's lead removed): rc=1, `FAIL an instant inside its store's lead survives the load (a lead is not lost) [lead_lost=['accuracy (writer round trip)', 'snapshots (writer round trip)']]`.
- M1b, `_bound_instants` ignores the declaration (`limit = bound`): the same FAIL, naming both the accuracy and the snapshot round trips.
- M2, the notifier reads `self._store.async_load()` raw again: rc=1. It fails with `FAIL a store holding JSON that is not a mapping fails no loader (load_mapping, D7-s4-81) [raised=['notifier<-[1]: AttributeError', "notifier<-'x': AttributeError", 'notifier<-7: AttributeError']...]`. It also fails the existing version-mismatch check (#1740) for the notifier.
- M3, `async_save` no longer forgets the digest: rc=1, `FAIL the save digest skips only the payload its store last accepted, forgets it on a plain save and retries a failed one (ARCH2-s2 P3) [save counts [1, 2, 1] (want [1, 3, 1])]`.
- M3b, the digest's skip removed: the same check fails with `[save counts [2, 4, 1] (want [1, 3, 1])]`.
- M4, `quarantines` returns `False`: rc=1, `FAIL quarantines() is the next load's scrub, keys included; a foreign key declares nothing [wrong=['non-finite leaf', 'poisoned key'] ...]`.
- M5, `PriceShapeLearner.fold` no longer marks a day seen: `tests/features.py` rc=1 with 4 FAIL. These are `a complete hourly day is folded into the shape and persisted once`, `the same prices on the next refresh are folded in again zero times`, `a 15-minute day trains the hourly shape and the quarter factors both`, and `the quarter seen-set has its own skip, checked separately from the hourly one`.

## Null control

- The finder's D1-s2-01 harness has its own control row, the accuracy store's rewrites. It reads 0 at both ends. The harness's `--perturb` reads 0 at the baseline.
- The ARCH3-s6 P3 differential run unperturbed reads 0 mismatches at the head. Its `--perturb` arm (a `quarantines` that ignores poisoned keys) reads 1764, which is forward-carry (1).
- ARCH2-s4's `load_prelude.py --perturb` routes the notifier through `load_mapping` in memory. At the baseline that arm is the fix's effect.
- `tools/audit/archscore/score.py --diff e5f7e169d e5f7e169d` reads `dS +0.0000 NULL`.
- M0 above is the mutation driver's own null.

## Figures

Finder harnesses, run in the tree or from the baseline export, at fork `6e5753a4a` (baseline) and at the head:
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D1/s2/snapshot_bound.py` (blob `59047d6a0201`): baseline `snapshot_instants_rewritten=5`, `snapshot_ahead_warnings=5`, `ring_instants_changed_vs_disk=5`. Head: 0, 0, 0. Control `control_accuracy_instants_rewritten` is 0 at both ends. `--perturb` at the baseline reads 0, 0, 0.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round10/D7/arch2-s4/load_prelude.py` (blob `cf8f195ddb83`, from `b202335e2`): baseline `raising_seams=1`, `setup_notifier_raises=1`. Head: `raising_seams=0`, `setup_notifier_raises=0`. Both ends read `seams=17`, `driven_seams=16`; the undriven seam is `store:load_mapping`, the prelude itself.
- `PYTHONPATH=tests/hastub:custom_components python3 $EXPORT/dev/audit/rounds/round10/D7/arch3-s6/store_report_equiv.py` (blob `5fe6f3a067b6`, from `532d8d09d`): head `pairs=36279`, `mismatches=0`. `--perturb` gives `mismatches=1764`. The baseline has no `store.quarantines`, so the harness cannot run there (AttributeError); it compares the old expressions against the new functions by construction.
- `python3 tools/audit/archscore/score.py --diff e5f7e169d HEAD`: `Architecture score: dS +1.3265 IMPROVES`. The moves are `shared_inplace_writes 22 -> 19`, `coordinator_multiassigned_attrs 118 -> 115`, `private_cross_module 17 -> 15` and `coord_footprint 2547 -> 2508`. This is ARCH2-s2's own re-derivation rule (its `arch2_delta.py` header: "a fix review re-derives it by scoring its own head against the same baseline"). Its prototypes measured P3 at `shared_inplace_writes 22 -> 21` and P7 at `22 -> 20` / `118 -> 115`, which sum to what the head reads.

The class's seam rule (fixer.md step 8), N-future-clamp:
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep/future_clamp_seams.py` (blob `ffd0633baec0`) enumerates every instant leaf of every store, with aliases resolved. Baseline: `instant_leaves=55 flagged_leaves=7 flagged_host_origin_pairs=2 [('debug', 'accuracy'), ('snapshots', 'accuracy')]`. Head: `instant_leaves=55 flagged_leaves=0 flagged_host_origin_pairs=0 []`.
- This enumerator reads store-level leads off the AST, so at the head it reads the accuracy store at 0 h. The due's lead now lives in its declaration. The standing companion is `tests/finite_boundary.py`'s instant arm. It reads each field's allowance off the declaration (`_declared_ahead`), checks every store through its real loader, and drives the snapshot ring through the real writer the heartbeat calls. A precondition (`each writer round trip carries an instant ahead of the clock (not vacuous)`) requires the accuracy, boost and snapshot round trips each to carry an instant ahead of the clock.
- Disposition of the 7 baseline seams:
  - Six are `snapshots:snapshots/#/learners/{accuracy,comfort}/...`. They are closed by this diff: they inherit the accuracy table, `lead_pending/#/0` keeps its 24 h through the alias, and the past stamps are bounded at the clock.
  - One is `debug:rows/#/accuracy_sample/t`. It is closed by this diff: the alias names `samples/#`, a settled interval's past stamp, which declares no lead.

The class's seam rule, the load prelude (D7-s4-81): `load_prelude.py`'s SEAM rule, every function that awaits `<store>.async_load()` or calls `store.load_mapping`, returns 17 seams at the head, with 0 raising. `tests/finite_boundary.py`'s new `store_non_mapping_raises` drives every loader in `LOADERS` with `[1]`, `"x"` and `7`. `LOADERS` is the reach arm's map, which that script already holds equal to the AST-derived boundary set. It reads 0 at the head and 3 under M2.

Standing scripts:
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir ...`: `MODE: SCOPED -- 23 script(s) run, 10 scoped out.` This was measured at merge base `e5f7e169d` on 2026-10-18; the rule is the mode line, not the count.
- `GATE_SCOPE=auto GOLDEN_MODE=drift bash tests/run.sh` at the head: `MODE: SCOPED -- 23 script(s) run, 10 scoped out.`, then `25 TEST SCRIPT(S) PASSED; 9 SCOPED OUT AND NOT RUN` (the run_always lines added to the scope), rc=0. It includes `tests/env_drift.py --all origin/main`: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`, so no golden moved and both claim files are byte-identical to main. The heavy lanes (`stress.py`, the mutation table over every driver) run in CI.
- `python3 tests/structure.py --record` (commit `766b5eb46`) records five rows:
  - `class_excess_loc 18468 -> 18382`
  - `max_class_loc 8635 -> 8553`
  - `coordinator_attrs 151 -> 148`
  - `coordinator_multiassigned_attrs 118 -> 115`
  - `seam_cut_total 752 -> 720`
  
  Each row moved for the reason that commit message states. `functions_cc_over_15` stays at 31: the first cut of `_bound_instants` measured cc 16 against the base's 14, and the walk was simplified to 14 (`getattr` over the declaration, a read-only empty default) rather than raising a budget.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `19 unpinned site(s) the diff adds` and `no closures or fast red predicted against e5f7e169d64b`.

## Architecture score

`Architecture score: dS +1.3265 IMPROVES` (see `## Figures`). No gate metric rose:
- shared_inplace_writes 22 -> 19
- coordinator_multiassigned_attrs 118 -> 115
- private_cross_module 17 -> 15
- coord_footprint 2547 -> 2508

## Unpinned sites

Each site is left to `mutation-autofix` (`ci-autofix.md`: killed unpinned mutants are the bot's, not duplicated). Each line names the check expected to kill it; that is a forecast unless an M-series arm above measured it, which is cited where it did. If the autofix summary is not `changed`, the seat pins.
- custom_components/heatpump_optimizer/coordinator.py:7870 GUARD_OFF: mutation-autofix; expected killer (forecast, not measured) `tests/features.py` `a store that has never been written leaves an empty model, not an error` (the price-model loader's `None` arm).
- custom_components/heatpump_optimizer/coordinator.py:7885 GUARD_OFF: mutation-autofix; expected killer (forecast, not measured) `tests/finite_boundary.py` `store_non_mapping_raises` (the ledger loader).
- custom_components/heatpump_optimizer/coordinator.py:7946 GUARD_OFF: mutation-autofix; expected killer (forecast, not measured) `tests/finite_boundary.py` `store_non_mapping_raises` (the accuracy loader).
- custom_components/heatpump_optimizer/coordinator.py:7983 GUARD_OFF: mutation-autofix; expected killer (forecast, not measured) `tests/finite_boundary.py` `store_non_mapping_raises` (the energy loader).
- custom_components/heatpump_optimizer/coordinator.py:8207 GUARD_OFF: mutation-autofix; expected killer (forecast, not measured) `tests/features.py` `a 23-hour day trains neither shape and is not marked seen` (no save when nothing folded).
- custom_components/heatpump_optimizer/coordinator.py:8213 RETURN_DEL: mutation-autofix; expected killer (forecast, not measured) `tests/features.py` `a finite store round-trips to the identical model, warning-free`.
- custom_components/heatpump_optimizer/coordinator.py:9402 GUARD_OFF: mutation-autofix; expected killer (forecast, not measured) `tests/finite_boundary.py` `store_non_mapping_raises` (the snapshot loader).
- custom_components/heatpump_optimizer/dhw_learning.py:302 GUARD_OFF: mutation-autofix; expected killer (forecast, not measured) `tests/finite_boundary.py` `store_non_mapping_raises` (the draws loader).
- custom_components/heatpump_optimizer/price_model.py:454 RETURN_DEL: mutation-autofix; expected killer (forecast, not measured) `tests/features.py` `a complete hourly day is folded into the shape and persisted once`.
- custom_components/heatpump_optimizer/price_model.py:469 GUARD_OFF: mutation-autofix; expected killer (forecast, not measured) `tests/features.py` `a payload with no lists, or a string where a list belongs, adds nothing`.
- custom_components/heatpump_optimizer/price_model.py:472 GUARD_OFF: mutation-autofix; expected killer (forecast) the same check (its quarter-set arm).
- custom_components/heatpump_optimizer/store.py:164 CMP_BOUND: mutation-autofix; expected killer (forecast, not measured) `tests/finite_boundary.py` instant arm (the writer round trip at exactly the longest lead).
- custom_components/heatpump_optimizer/store.py:164 GUARD_OFF: mutation-autofix; expected killer (forecast, not measured) `tests/finite_boundary.py` `no stored instant reaches a loader beyond the clock plus its store's lead`.
- custom_components/heatpump_optimizer/store.py:545 BOOLOP: mutation-autofix; expected killer (forecast, not measured) `tests/finite_boundary.py` `quarantines() ... a foreign key declares nothing` and the domain arm.
- custom_components/heatpump_optimizer/store.py:545 RETURN_DEL: mutation-autofix; the same.
- custom_components/heatpump_optimizer/store.py:555 RETURN_DEL: mutation-autofix; expected killer (forecast, not measured) `tests/debug_collect.py` (`admitted` drops an off-domain record).
- custom_components/heatpump_optimizer/store.py:572 RETURN_DEL: mutation-autofix; killer measured by M4.
- custom_components/heatpump_optimizer/store.py:578 RETURN_DEL: mutation-autofix; expected killer (forecast, not measured) `tests/finite_boundary.py` `a store key names its DOMAINS entry, and a foreign key names none`.
- custom_components/heatpump_optimizer/store.py:746 GUARD_OFF: mutation-autofix; killer measured by M3b.

## Red checks

Locally, before this head, three scripts failed at the first commit `40ad33528`; each is answered in a later commit:
- `tests/structure.py`: `5 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED` (recorded in `766b5eb46`). Before that, `functions_cc_over_15 32 > 31` at the uncommitted first cut, paid by simplifying `_bound_instants`. **Cheaper detector:** `python3 tests/structure.py` itself, seconds, already owed before every push; it caught both. Nothing to build.
- `tests/typing_ruler.py`: `by_code[no-any-return] 0 -> 1`, from `quarantines` returning `!=` of `Any`; fixed in `558d113d0`. **Cheaper detector:** the ruler is the detector, run in the scoped gate; nothing cheaper exists for a mypy count.
- `tests/entities.py`: the mutation-table selftest refused five ledger dispositions naming lines this branch rewrote. They are dropped in `558d113d0`, and the new sites are listed above. **Cheaper detector:** `mutation_table.completeness_problems(load_budgets(), inventory())`, source-only, seconds. It is the same rule the ledger refusal runs, so no new detector is owed.

No CI check has run on this branch yet.

## Forward-carry

`none`. Forward-carry (1) is satisfied by `## Null control` (0 unperturbed, 1764 perturbed). Forward-carry (2) binds R10-DIAG-REPLAY, which already carries it in its roster entry. That group inherits the interfaces as the P3 patch left them: `store.store_name`, `store.off_domain` and `store.quarantines` are public, and `debug_ingest.domain_suffix` is gone.

## Friction

- `fixer.md: cost: the scoped gate took about 45 minutes under a load average of about 165 on this seat (arch_score.py alone ran more than 13 minutes), so every catch-up merge's re-execution of steps 2-8 costs the better part of an hour of wall clock.`
