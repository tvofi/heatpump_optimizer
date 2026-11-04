Fix review: merge 785d43a97fe5ca765b97090a0e735c2d5690f11e

bus-nonce: 416c0690ef6e42fb120522a730d4c62e

## Verdict

Merge at 785d43a97fe5ca765b97090a0e735c2d5690f11e (round 2). Both defects are fixed through the existing read fence and one shared scalar-learner parser. Every mutant, the body's three and my three, is killed. CI classify reads GREEN at this head, which is still the PR head.

## Evidence

- Round: second fix review (repair round f-3185-r2 returned). Head measured: 785d43a97fe5ca765b97090a0e735c2d5690f11e, which is the PR head and the head named in the body's `## Head`. Roles diff since the merge base: empty (the contract is current). Merge base equals origin/main (0 commits behind). `git merge-tree --write-tree origin/main 785d43a9`: rc=0, tree 224de792b1cc5cfc1007102c1f26d4b646bc8314, no conflict and no claim-driver run.
- Mutation proof (step 1), mine, run on `git archive` copies of the head. `tests/features.py` was cut after the two new checks (line 14131; 1089 checks). Script: ev/mutants/mut.py; outputs: ev/mutants/*.out.txt.
  - RESULT NULL: `ALL 1089 PARTIAL PASSED` rc=0.
  - RESULT M1 (the gated save moved back before `self._measured_cop`): KILLED, `1 of 1089 PARTIAL FAILED`. Failing check: `a thermal save issued mid-load keeps the stored COP and T4b learners in every payload`, raced `[(30, []), (30, ['-5'])]`. The re-anchor checks the body also lists lie past the cut.
  - RESULT M2 (the restore skips `_snapshot_store`'s read): KILLED, `1 of 1089`. Failing check: `a restore issued right after setup applies...`, raced `(False, (1.0, 0, 1.0, 0))`, null `(True, (1.4, 33, 1.1, 21))`.
  - RESULT M3 (the base setter loop back in `_apply_learner_payloads`): KILLED, `2 of 1089`. Failing checks: the new restore check `(True, (1.4, 0, 1.1, 0))` and `a snapshot restore re-anchors a pre-edit scale, not restores it`. These match the body.
  - RESULT M4 (mine; `_load_scalar_learners` keeps every live count): KILLED, `22 of 1089`.
  - RESULT M5 (mine; a missing key writes None into its count): KILLED, crashed with a TypeError, rc=1.
  - RESULT M6 (mine; the COP row dropped from the shared parser): KILLED, `8 of 1089`.
  - Every one of the body's three mutants dies at this head, as the body says. The other three show that the parser's own lines are pinned.
- Semantics read: `_stored_learner` applies the value when the key is present and defaults its count to 0 when the samples key is absent. Snapshot payloads come from `_thermal_learning_payload`, which writes all four `*_samples` keys, so a restore now rolls back counts. One edge change: a snapshot without a samples key (none written by the current producer) now zeroes that count rather than keeping the live one. This is the conservative direction.
- Null control (step 3): each new check runs its null arm in the same assertion (`_store_race(..., after=True)`). At the head both arms read the stored state (the NULL run above). The base-side figures (`2 of 1089 PARTIAL FAILED`, null `[(0, []), (30, ['-5'])]`) are the fixer's. I did not re-run the base; this figure is not re-derived by me.
- Claims and versions (steps 4, 5): the three-dot diff does not touch `tests/golden/`, either claim file, `VERSION`, the manifest or `RELEASE_NOTES.md`. There are no fixture moves to claim. CI's golden lane is part of the scoped gate (cited, not re-run).
- Structure: `python3 tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED` (ev/structure.txt). The budget moves are all downward: class_excess_loc 17637->17636, functions_cc_over_15 27->26, max_class_loc 7975->7974.
- Architecture score: `score.py --diff origin/main` at the head prints `Architecture score: dS +0.0042 IMPROVES`, `coord_footprint 2381 -> 2374` (ev/archscore.txt). This matches the body. The round-1 `reflective_writes`/`computed_attr_access` rises are gone: no setattr, and the counts are assigned by name.
- Step 14, the plant: I re-spelled only the count assignment as four plain `if n[i] is not None: self._x = n[i]` and changed nothing else. That gives `dS +0.0006`, `coord_footprint 2381 -> 2380` (ev/archscore_plain_spelling.txt). The real consolidation (the restore's setter loop and the loader's three `if`s replaced by one parser) earns 1 statement. The other 6 come from packing four conditional assignments into one generator tuple-unpack, which the AST statement count reads as one. The change stays sound and improving under either spelling, and no budget raise rests on the score, so this is an instrument finding (Findings), not `metric-gamed`.
- Class (step 6): the body names the rule ("a learned loader applies its read with no await before its last assignment"). It lists the other loaders under it (`async_load_profile`, `async_load_draws`, `_async_load_price_model`, `_async_load_accuracy`, `_async_load_snapshots`), read clean by the in-tree census. I confirmed `_async_load_snapshots` has no await after its read. I did not re-run the census (`census_lost_total=0 of 12` is the fixer's figure).
- Harness (step 9): no finder's harness is committed for this group. The finding came from the R10-FACTORY-RESET fixer, and the new in-suite checks are the fixer's own instrument, disclosed as such. The body's `ends_probe.py` stayed in scratch and is not landed; its both-ends figures were not re-derived by me.
- Forward-carry (step 10): the body says n/a, with STRANDED CARRY 55 (#2674) answered by #2674's own probe. This is accepted: the invariant is stated at the code site and pinned by the new check.
- Red checks (step 11): at this head, `tests / replay` failed (job 126613702495) with `FAIL synthetic-dhw-only.json: cycle_cost [1 offender(s): cpu_ratio 2.887 over its budget 2.173]`. That is the same main-owned host-cost flake the body's `## Red checks` answers (main failed the same check, #3174). `tests / nightly-status` is main-owned and unrequired. Round 1's arch-score red is answered and green at this head.
- CI: `merge_train.py classify 785d43a97fe5ca765b97090a0e735c2d5690f11e --pr 3185` -> `GREEN 785d43a97fe5ca765b97090a0e735c2d5690f11e pending: none red: none` (rc=0; ev/classify.txt). Head re-read just before return: refs/pull/3185/head = 785d43a97fe5ca765b97090a0e735c2d5690f11e.
- Self-audit: `carry_audit.py check` (body: the PR body's `## Friction` items, its only carried items; comments: this verdict) -> `CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)`, rc=0.

## Findings

- Instrument: archscore's `coord_footprint` counts one generator tuple-unpack assignment as one statement where the same four conditional count assignments are eight. In this diff that packing supplies 6 of the 7 statements behind `dS +0.0042`; the plain spelling reads `dS +0.0006` (ev/archscore_plain_spelling.txt). The change is sound under either spelling, so this does not block; the instrument's statement-packing blind spot is owed to the spellings work. Carry: #2259
