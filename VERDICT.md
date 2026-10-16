Fix review: blocked 264027cc862516abf623ee17d9c7b21b55e80b47 carry-missing: not carried to R10-ARCHSCORE-COVERAGE -- the destination the body names holds no copy of it (`dev/programme/rosters/wave-r10-groups.json`'s R10-ARCHSCORE-COVERAGE `carry` is byte-identical to origin/main's, sha1 cfbada4657a7c3561315d78c4913657421b1137b), so the verdict turn and the 85-tree corpus delta reach no later stage's brief. The fix itself is sound: every number re-derives, every mutant and null control reproduces, and no metric was gamed. This is a record-and-body block only.

bus-nonce: fbe7ad3000aab0782007511eb3106201

Head measured: 264027cc862516abf623ee17d9c7b21b55e80b47 (re-read at post time, unchanged; PR headRefOid, state OPEN).
Merge base: 81ae048e8bbdf2335fe2016e987ec2739481f293 (`git merge-base origin/main HEAD`). Round 1 (no prior review/verdict ref for 2340).
Reviewer seat: hpo-approver path via tools/audit/seat/bus.sh; contract read at the head, dev/governance/roles/ untouched vs main.

## 1. The block: forward-carry

Body: "`R10-ARCHSCORE-COVERAGE` (`dev/programme/rosters/wave-r10-groups.json`, its entry's `carry`): ... if its `expected.json` is re-recorded from a base without this change, that verdict turns back to NULL. Reported to the orchestrator, which owns the roster."

Opened: the R10-ARCHSCORE-COVERAGE entry's `carry` is the two strings below, and neither mentions structure.py, `dead_members`, the corpus delta or `a3_dead_by_reachability_fix`:

    "A weight change re-records expected.json and states the reason in the commit message."
    "This group runs BEFORE R10-BRIEFS-FOLD, ... and before R10-PARAMS-OWNER, ..."

    RESULT roster_sha_head=cfbada4657a7c3561315d78c4913657421b1137b
    RESULT roster_sha_origin_main=cfbada4657a7c3561315d78c4913657421b1137b   (same file)
    RESULT diff_touches_rosters=0 files   (git diff --name-only MB...HEAD -- dev/programme/rosters/ .claude/workflows/)

The stage is live, not finished, so the destination is a real one: R10-ARCHSCORE-COVERAGE is 2 of 5 parts merged (#2293 2026-10-16T00:10Z, #2311 14:29Z) with part 3 (#2320) OPEN, and the group's own brief makes it re-record `calibration/expected.json`. `git merge-base --is-ancestor origin/fix/r10-archscore-coverage-p3 origin/main` is false, so p3's re-record starts from a base without this change -- exactly the state the body says turns the verdict back to NULL.

The route is the established one (all 24 non-merge commits to `dev/programme/rosters/wave-r10-groups.json` are tvofi's; carries land via `handoff/audit-r10-roster-cN` PRs and `roster_edit.py append-carry`), and #2293 used the same phrasing -- but #2293's carry was ON main 2.5 h BEFORE it merged (roster commit ffcf1a46a, 2026-10-15T21:38Z; #2293 merged 2026-10-16T00:10Z). finding-propagation.md is explicit that the producing PR does not merge until the carry is in the tree, and `dev/audit/rca/2028/verdicts_review_refs.tsv:83` is a prior reviewer block of exactly this shape ("carry-missing: not carried to R9-RO-9 (its roster carry holds ... not the follow-up text)").

Remedy, one command: append to that entry's `carry` a line such as "From #2340 (STRUCTURE-BLIND): tests/structure.py's dead_members census resolves a load's receiver (`ReceiverTypes`), so its vectors' `dead_members` leaf rose on 85 of 87 stored trees and `a3_dead_by_reachability_fix` reads IMPROVES; re-record expected.json and the corpus from a base that INCLUDES this change, or that verdict turns back to NULL." Nothing in the fix has to change.

## 2. Two body figures that do not re-derive (fix-review step 8)

- The companion harness sha1. Body: "`dev/audit/harnesses/r10_structure_blind.py`, sha1 `072d5d6c94526fcabdbef893d23474c92a076bdd`".

      RESULT companion_sha_at_540ede178=155b99597372c0bc3b7b2cdcea5a66172aef83d4
      RESULT companion_sha_at_b3090df34=155b99597372c0bc3b7b2cdcea5a66172aef83d4
      RESULT companion_sha_at_264027cc=155b99597372c0bc3b7b2cdcea5a66172aef83d4

   No ref of the branch carries the quoted sha1; the fixer.md step 3 "sha1-cited companion" resolves to nothing.

- "16 budget keys", listed among the prose figures the body says were "re-taken at `b3090df34`" under `python3 -c "import json;print(len(json.load(open('tests/structure_budgets.json')))-1)"`.

      RESULT budget_keys_at_MB=16
      RESULT budget_keys_at_b3090df34=17
      RESULT budget_keys_at_264027cc=17

  16 is the merge base's count (right for the finding sentence "0 of the 16 budget keys"); the head's is 17. The other five prose figures in that sentence do re-derive at b3090df (1201 / 3495 / 8688 / 56 / 10).

Both are body-accuracy defects, not measurement defects; a body re-take should fix them alongside the carry so the re-verdict has one document to read.

## 3. Every number re-derives (step 8), with the instruments re-run

    RESULT structure_self_check=56 counting rules hold      (PYTHONPATH=tests/hastub python3 tests/structure.py, head)
    RESULT class_excess_loc=18498 count
    RESULT dead_methods=0 count
    RESULT name_kept=39 count
    RESULT max_class_loc=8688 count
    RESULT duplication_copies=34 count
    RESULT dead_top_level_symbols=1 count
    RESULT ratchet=STRUCTURE RATCHET PASSED

`class_excess_loc=18498` I re-derived by hand off the `classes over 300 LOC` table, which the same run prints: (8688+410-300) + (3495-300) + (1929-300) + (1896-300) + (1063-300) + (965-300) + (849-300) + (812-300) + (652-300) + (493-300) + (453-300) + (369-300) + (315-300) + (309-300) = 18498, exact. The metric is a sum of excesses, not a re-scaling, and no other key moved.

## 4. The mutation proof re-runs (step 1) -- all four, at the head tree

`sha1sum tests/structure.py` = 56c816051e70c9984cb4a034a1fb573d64be4944 before and after every mutant below.

    M0 (unmodified)                         RESULT ok 56 counting rules hold / STRUCTURE RATCHET PASSED
    M1 (drop `loc += helper_loc`)           FAIL  a method moved verbatim into a coordinator.py helper moves no class row
                                            1 COUNTING RULE(S) BROKEN
    M2 (`total += ...` -> `total = max(...)`) FAIL  a class below the largest is priced when it grows
                                            1 COUNTING RULE(S) BROKEN
    M3 (typed branch -> `set(by_name[name])`) FAIL  a load on a constructor-typed attribute reaches that class only
                                            FAIL  a return annotation and a tuple unpacking type a local
                                            FAIL  a parameter only placed calls pass takes their arguments' class
                                            3 COUNTING RULE(S) BROKEN

M2 exits 1 (the self-check runs before measurement), so each mutant is a red on the script the scoped gate runs.

## 5. The FINDER's harnesses, both ends (step 2) -- not the fixer's

`dev/audit/rounds/round10/D7/s1/class_growth.py`, baseline export of 81ae048e8 vs head export of 264027cc:

    merge base   RESULT lines_added_per_arm=1201 / keys_moved_second_class=0 / keys_moved_coordinator=1
    head         RESULT lines_added_per_arm=1201 / keys_moved_second_class=1 / keys_moved_coordinator=2

The coordinator arm stays a control at both ends (`max_class_loc` 8688 -> 9889, +1201 for the same pad). I also ran it on an export of e8718ec3b, the body's stated baseline: same three numbers -- immaterial, since `git diff e8718ec3b 81ae048e8 -- tests/structure.py tests/structure_budgets.json` is empty.

`dev/audit/rounds/round10/D7/s3/namekept_receivers.py` -- flat at both ends as the body says: `candidates_with_zero_typed_hits=6`, `total_typed_hits=0 sites` on both, and its own perturbation still moves it (`HPO_RECV_EXTRA='drift.py:Cusum:reset:cusum.reset()'` -> `Cusum.reset_typed_hits=1 sites`).

`tests/structure.py` at the merge base: `ok 41 counting rules hold`, `duplication_copies=35`, `dead_methods=0`.

## 6. The fixer's own companion (disclosed as theirs, not the finder's), three arms

sha1 155b99597372c0bc3b7b2cdcea5a66172aef83d4 (the body's quoted sha1 is wrong; see 2).

    head census, head tree            six_measured_dead=0  six_name_kept=2  name_kept=39  dead_methods=0  second_keys_moved=1
    head census, MB's package         six_measured_dead=4  six_name_kept=2  name_kept=39  dead_methods=4  second_keys_moved=1
    base census, MB's package         six_measured_dead=0  six_name_kept=6  name_kept=153 dead_methods=0  second_keys_moved=0

Every cell matches the body's table. `move_class_excess_delta=0`, `move_max_class_loc_delta=-12` at both ends, `merge_class_excess_delta=-12`, `merge_class_excess_delta=absent` at the base, `entity_members_keyed=21`, `same_name_not_keyed=2`, and the two names it prints are the two the body lists (`coordinator.HeatPumpOptimizerCoordinator.target_temperature`, `open_meteo.OpenMeteoSolar.available`).

## 7. Null controls (step 3)

    RESULT null_keys_moved=0 count                      (companion, unchanged tree twice)
    RESULT null_fixture_instances=0                     (enumerator --null)

    python3 -I tools/policy/budget_raise_gate.py --base 81ae048e8 --head 264027cc --pr 2340
      RESULT budget_raises=0 count / PASS: no budget raise; no owner review is owed

The gate's own control reproduces too: `tests/structure_budgets.json`'s SCHEMA is `(("*",), MAX)` over everything but `recorded_at`, a MAX leaf absent at the base and present at the head is routine, and the fixer's planted `max_class_loc 8688 -> 8689` reads `budget_raises=1` / `REFUSED`. The CI `budget-raise-gate` check is green at this head.

Cost of the tightened ratchet, per the dispatch: NOT a raise. The only pre-existing key that moved moved DOWN (`duplication_copies 35 -> 34`); `class_excess_loc` is a new MAX row recorded at the value the tree already has, so nothing was loosened, and the group carry's "may raise a measured figure -- stop and ask" precondition was not triggered. Flagged loudly as instructed; the gate is the instrument that answers it.

## 8. Step 14: the movements are earned, not the instrument

Removed the mechanism the body names -- restored the four deleted members (`InputReader.value/text/flag`, `Cusum.reset`) on the head tree:

    duplication_copies   34 -> 35        (the -1 is the deletion)
    dead_methods          0 -> 4         (the head census measures exactly those four dead)
    class_excess_loc  18498 -> 18508
    archscore dead_members 1 -> 5 ; duplication_copies 65 -> 66 ; headline dS +0.0000 NULL

So both archscore gains (dead_members 5 -> 1 +1.5850, duplication_copies 66 -> 65 +0.1937) and the whole `dS +1.7787 IMPROVES` vanish when the deletion is undone: earned, not a metric re-definition. Re-measured at the head: `Architecture score: dS +1.7787 IMPROVES / duplication_copies 66 -> 65 +0.1937 / dead_members 5 -> 1 +1.5850`, exactly the body.

Corpus, as a null control for the re-record: the committed `tools/audit/archscore/calibration/corpus_vectors.json` is sha1 85d62c4e23c2f201d5bdf8ac081e6ab619ef1f14; `calibrate.py --measure-corpus --jobs 4` on this tree leaves `git status` clean with the sha unchanged (byte-identical output). The merge base's is d15148f80221ab333ce48ded8509959d84b76629, and the two differ on `dead_members` and nothing else, on 85 of 87 stored trees.

Step 14's second half: the diff's own kind of move planted on the same instrument reproduces nothing -- the counts above move only with the deletion. The one residual is DISCLOSED, not gamed: `move_max_class_loc_delta=-12` at head and base, i.e. `max_class_loc` still prices a verbatim move as a gain. The diff does not move `max_class_loc` (8688 at both ends) and adds the row that does not reward a move, so under step 14 this is an instrument finding, carried (see 9), not a block on this diff.

## 9. `HA_ENTITY_METHODS` is not a blinding (step 14, fixer.md step 14)

The new root is keyed on (name, the class's family derives from an external `*Entity` base), not the name. The companion's separation arm prints the two members a name-only key would have silenced (`...Coordinator.target_temperature`, `...OpenMeteoSolar.available`) and `entity_self_check` pins both halves: an entity's `available` is a root, the same name on a class HA never instantiates is still measured dead. `entity_members_keyed=21`, `same_name_not_keyed=2`, and the corpus re-measure after the narrowing is byte-identical, so the entry hides no live death today and cannot hide one later on a non-entity class.

## 10. Class / enumeration (step 6)

`dev/audit/rounds/round10/D14/sweep-N-structure-blind/enumerate.py`: `RESULT seams=10 / RESULT instances=5`, `--perturb` -> `RESULT instances=4`, `--null` -> `RESULT null_fixture_instances=0`. The body dispositions all 10 seams against their disposition; none is returned-and-unmentioned, so no `class-open`. Seam A (`measure:max_class_loc`) still returns because rule A's first clause tests a shape (`max()` with no `len()` sibling) while its text states a property ("a non-max unit grows unpriced"), and the property is what the fix closes -- the finder's own harness reads 0 -> 1. The body says so out loud rather than editing the round-10 record to agree with the fix.

## 11. Red checks (step 11)

Read from the API, not the body. Across every commit of the range `81ae048e8..264027cc` the only non-success check-run conclusions are `cancelled` (superseded by the next push) at b3090df34; at the head every run is success or skipped, `Tests` is green, and the combined status carries no failing entry. So no gate check went red on a commit of this branch. The body nonetheless answers the two reds it names -- `tests/golden.py` in `GOLDEN_MODE=strict` (three readings, including the same 55/56 on origin/main's own tree) and the `prepr.sh` `ci predict` INERT-READS red it repaired by adding the new harness to `tests/closures.json` in this diff -- each with its cheaper detector. Trigger answered.

## 12. Provenance, claims, version, conflict

    env-ish: git diff MB...HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt
    RESULT claim_files_moved=0   (byte-identical to the merge base; nothing claimed, nothing to claim)
    RESULT version_files_touched=0  (VERSION 7.0.0, manifest 7.0.0, RELEASE_NOTES heading untouched)
    git merge-tree --write-tree origin/main HEAD -> exit 0, no conflicting path
    RESULT merge_tree_conflicts=0   (mergeStateStatus BLOCKED is the review gate, not DIRTY)

`Closes #2235` is present and #2235 is this group's only issue. The deleted mutation-ledger row `inputs.py/InputReader.value.RETURN_DEL.6cf530e8.json` pins `return reading.value`, which has 0 occurrences in custom_components at the head -- the row is stale, and `tests/mutation_budgets.json` is untouched.

## 13. What I did not re-run

`tests/arch_score.py` (the 72-check calibration) I did not finish locally; cited instead from CI's green `arch-score` at this head, with the corpus byte-identity above standing in for its heaviest input. Per fix-review step 11 I re-ran no gate and no mutation-table lane.

## 14. Architecture (step 15)

Judged on added lines: the new census is in the module that owns the concept, no `homeassistant` import, no side effect, no new public surface, `tests/structure.py` and `score.py --diff` not regressed (dS improves), the group's architect note has no entry here. `class_excess` is five lines and `ReceiverTypes` is a pure pass over an AST already in hand. No `architecture-unsound`.
