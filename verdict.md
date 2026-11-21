Fix review: merge 827fa67eb6ee84d8874524557cdd540ca1b54593

bus-nonce: bee67cf74bb3e1a074092a1f722b6e79
pending-ci: tests / mutation-pins (1), tests / mutation-pins (2), tests / fast (3.14), tests / closures, tests / coverage, tests / typing, tests / replay, tests / browser, tests / arch-instrument, tests / nightly-ha (stable), tests / nightly-ha (2025.2.0), governance / env-matrix, governance / instrument-self-tests, codeql / Analyze (python), codeql / Analyze (javascript-typescript)

Note: mutation-red: tests / mutation (job 136961493894, run 44940371676) is red at this head: MUTATION TABLE REFUSED, 1955 unpinned against 1953 at ratchet base 63c6d1cff9, the six added sites coordinator.py 6146 BOOLOP and 11197 GUARD_OFF, solve_gate.py 76, 78, 90, 129 -- exactly the six the body's `## Red checks` answers and `## Unpinned sites` disposes as pinned by mutation-autofix; tests / mutation-pins (1)/(2) were queued/in progress at 20:05Z to pin them (ci-autofix.md). My targeted runs kill the 6146 trailing guard (M3) at this head. Answered by the body, so not a block; the relay refuses this verdict over a red. Carry: dismissed: answered in the body's Red checks; autofix pins pending
Note: stale-figure: the body's `## Architecture score` still quotes `score.py --diff 8ab5dc566f`, two merge bases back; the PR's own production diff is unchanged across both merges (below), so the figure's substance holds; owed: re-take at the current base 63c6d1cff9. Carry: dismissed: paperwork on a body figure, not code
Note: figure-unreproduced: the body's `## Head` names tree `68a1a483fbf9` for `git merge-tree --write-tree 71c7ef0688d6 63c6d1cff9a2`; on this seat the repository's LEDGER-MERGE driver resolves `tests/structure_budgets.json` and `tests/closures.json` there and writes tree `cf1151492048`. The claim the figure supports (`-- custom_components/` diff against 5669e6e33108 empty; null control against 71c7ef0688d6 is main's 47-file delta) reproduces exactly (ev/merge_claims.txt). Carry: dismissed: a tree id that depends on the seat's merge drivers, not code

Round 4, delta only: reviewed head 9809bc79c2498f2b25867a5cc88dacd68c62a01a (round-3 verdict, merge) -> 827fa67eb6ee84d8874524557cdd540ca1b54593. `review_carry.py 9809bc79 827fa67e` prints FRESH-REVIEW (the branch carries hand-made resolution commits), so the delta was read by hand. The re-cut rule from the fourth round does not bite: no round-3 block exists, and this delta is main merges and their resolutions only.

## Delta
- The PR's own diff, merge-base-relative at each head (99436a082c...9809bc79 vs 63c6d1cff9...827fa67e, both 67 files), differs only in: hunk offsets; context lines main changed (`from . import room_record, rooms, slab_seed`; main's removal of the `# Run optimization if in auto mode` comment beside the PR's `gate.reason = await self.async_run_optimization()`); the module counts both sides moved (docs/architecture.md 99 modules, 34 importing homeassistant, 64 HA-free; round-4 claims register 98->99; deployment_shape 117->118 package files, history clauses ordered as landed); `_dhw_enabled_from_config` -> `dhw_enabled_from_config` in the P2 registry context (main's rename); the tests/features.py union (main's `R11-SEAM-solver` block beside the PR's solve_gate block); and structure_budgets' bases (the PR's own moves stay -2 on `class_excess_loc` and `max_class_loc`).
- No production line of the PR changed: git's automatic merge of the reviewed code tip 71c7ef0688d6 with main 63c6d1cff9 has an empty `git diff -- custom_components/` against 5669e6e33108, and 827fa67e has the same tree as 5669e6e331 (04c3894c35a9) (ev/merge_claims.txt).
- Widening considered and declined: main's 47-file production delta adds no new caller of the gated solve paths. At the head the callers of `async_run_optimization`, `async_simulate` and `async_optimize_now` are exactly the cycle (coordinator.py:6072, 6516), the tile/fuse background path (8993), the diagnose/advisor path (10699), debugger.py:325's `limited=False` self-test, button.py:110 and services.py:612/810; main's services.py change is a pre-write refusal (`_refuse_house_fields_on_two_zones`) that requests no refresh. So no reviewed solve-gate behaviour is put at a risk CI would not detect.

## Prior findings
- Note mutation-red (round 3, six added unpinned sites): the body's `## Unpinned sites` and `## Red checks` keep them disposed as pinned by mutation-autofix; CI's mutation lanes at this head are read below.
- Note stale-figure (architecture score base): still stale, carried above.
- Round 2's resolved block (D1-s1-03 trailing refresh): the code is unchanged (no production interdiff); its two checks still kill the mutant below.

## Evidence
- RESULT merge_tree_rc=0: `git merge-tree --write-tree origin/main 827fa67e`, origin/main at 63c6d1cff9 (ev/merge_tree.txt).
- RESULT tree_827fa67e=tree_5669e6e331=04c3894c35a9 (ev/merge_claims.txt).
- RESULT structure: STRUCTURE RATCHET PASSED rc 0 at the head (ev/structure.log).
- RESULT doc_claims: ALL 441 checks PASSED rc 0 at the head (ev/doc_claims.log), matching the body's figure for 48a4d93b4c.
- RESULT round-4 claims at the head: arch_modules_on_disk=99, arch_map_missing=0, ha_module_level_importers=34, claims_false=0 (ev/claims_round4.log); 99 `.py` files under custom_components/heatpump_optimizer/.
- RESULT scope: `tests/closure.py select --diff 63c6d1cff9` at the head prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`, the body's figure block (ev/closure_select.txt).
- RESULT solve_gate block (features_block.py, prelude from --emit-prelude at the head): unmutated `ALL 69 FEATURES BLOCK PASSED` (ev/block_unmutated.log).
- RESULT mutant M1 (`admit_background`'s `if gate.background_taken: return False` deleted): KILLED, 1 of 69, "D9-s1-02: one background what-if per main solve ..." `[admissions [True, True, True]]` (ev/block_M1.log).
- RESULT mutant M2 (`user_slot`'s `if ticket != gate.user_waiting:` -> `if False:`): KILLED, 1 of 69, "D9-s1-03: of four overlapping user what-ifs ..." (ev/block_M2.log).
- RESULT mutant M3 (coordinator.py:6146 `take_trailing` guard -> `if False:`): KILLED, 2 of 69, both D1-s1-03 trailing checks including the upstream-debouncer one (ev/block_M3.log).
- RESULT features: `PYTHONPATH=tests/hastub python3 tests/features.py` at the head: ALL 6003 FEATURE CHECKS PASSED, rc 0, the body's figure (ev/features.log).
- CI at 20:05Z (ev/check_runs.txt): green -- tests / closure-scope, tests / briefs, budget-raise-gate, arch-score, validate-hacs, governance / policy-docs, governance / wave-script, hassfest, codeql (actions), tests / nightly-status; red -- tests / mutation (above); the rest queued. `merge_train.py classify` printed WAIT from 19:33Z to 20:04Z (ev/classify.log), hence the pending-ci line.
- RESULT carry_audit: CARRY-AUDIT 8 finding item(s): 8 routed, 0 unrouted, rc 0 (ev/carry_audit.txt; the body's own items were read from its `## Forward-carry` and `## Friction`).
- Head re-read before return: refs/pull/3738/head and the PR API head are 827fa67eb6ee84d8874524557cdd540ca1b54593.
