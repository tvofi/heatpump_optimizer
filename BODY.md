# R10-STRUCTURE-BLIND: the ratchet prices class growth, and a load's receiver is typed

`tests/structure.py` measured two things by proxy, and both let a defect pass
unmeasured.

`max_class_loc` is a `max()` over the god-class table, so only the largest
class was budgeted. 1201 lines of new, called, CC-1 code in `HeatPumpOptimizer`
-- the runner-up, at 3495 lines against the coordinator's 8688 -- moved 0 of
the 16 budget keys (D7-s1-01). `dead_members` kept a member alive when another
class defined its name and some untyped receiver read `x.<name>`, so six
members with no production call sat outside the metric and outside
`dead_methods`'s zero budget (D7-s3-01, whose probe reads
`candidates_with_zero_typed_hits=6`).

The fix adds `class_excess_loc` -- every class's span past `GOD_CLASS_LOC_LIMIT`
summed, the coordinator's span counting its `coordinator.py` helpers, so a
verbatim move into a helper is not a gain and a merge is -- and gives
`dead_members` a `ReceiverTypes` pass that resolves each load's receiver to the
classes the source types it to, so a load reaches its class's family only. The
four members that census now measures dead are deleted; the two it can still
only keep by name stay on the record.

`Closes #2235.`

## Head

`540ede178c846c7270465161d967bf5b7e2182e3` on `handoff/r10-structure-blind`, measured with
`origin/main` at `e8718ec3b52e24531236c30e508a4d1b3cf086ed`, which is also `git merge-base origin/main HEAD`.
`date -u` at the run: 2026-10-16T16:27Z.

## Mutation proof

Four runs against this head's own `tests/structure.py`, each restored afterwards;
`sha1sum tests/structure.py` reads `56c816051e70c9984cb4a034a1fb573d64be4944` before and after all of them.

**M0, the null run.** Unmodified, `PYTHONPATH=tests/hastub python3 tests/structure.py`
prints `ok 56 counting rules hold` and `STRUCTURE RATCHET PASSED`.

**M1, the helper-line predicate removed** from `class_excess` (the two lines
`if mod == COORDINATOR_MODULE ...: loc += helper_loc`), which is the perturbation
the companion harness's own docstring names:

    FAIL  a method moved verbatim into a coordinator.py helper moves no class row
    1 COUNTING RULE(S) BROKEN -- the structure rows cannot be trusted

and `dev/audit/harnesses/r10_structure_blind.py` reads `RESULT move_class_excess_delta=-12`
where the unmodified tree reads `0`.

**M2, the defect itself**: `class_excess` pricing only the largest class
(`total = max(total, max(0, loc - GOD_CLASS_LOC_LIMIT))` in place of `total += ...`):

    FAIL  a class below the largest is priced when it grows
    1 COUNTING RULE(S) BROKEN -- the structure rows cannot be trusted

and the finding's own harness reads `RESULT keys_moved_second_class=0`, where the
unmodified tree reads `1`.

**M3, `dead_members`' typed branch reverted to the name-based edge** it replaced:

    FAIL  a load on a constructor-typed attribute reaches that class only
    FAIL  a return annotation and a tuple unpacking type a local
    FAIL  a parameter only placed calls pass takes their arguments' class
    3 COUNTING RULE(S) BROKEN -- the structure rows cannot be trusted

and the companion harness on the merge base's package reads `six_measured_dead=0`,
`six_name_kept=6` -- the base census exactly. This one is why the mutant is run
there rather than on the head tree: the head tree has already deleted the four,
so a blind census and a sharp one both read `dead_methods=0` on it, and only the
merge base's package separates them.

`tests/structure.py`'s counting-rule self-check runs before it measures anything
and returns 1, so every mutant above is a red on the script the scoped gate runs,
not on a probe kept beside it.

## Null control

- **The unmodified tree**: M0 above, plus the companion harness's own null arm,
  `RESULT null_keys_moved=0` -- the unchanged tree measured twice, every metric
  equal.
- **The budget gate**: `python3 -I tools/policy/budget_raise_gate.py --base <merge base> --head HEAD --pr <N>`
  reads `RESULT budget_raises=0 count` here. The same command against a head whose
  `max_class_loc` is one higher (8688 -> 8689, committed in a scratch commit and
  reset away) reads `RESULT budget_raises=1 count`, `RAISE tests/structure_budgets.json:
  max_class_loc: 8688 -> 8689 (a cap went up)`, `REFUSED`. So `class_excess_loc`
  is not a raise by the gate's own rule: its SCHEMA is `MAX`, and a `max` leaf
  absent at the base and present at the head is signed routine. Nothing else in
  the diff moved a cap up; `duplication_copies` moved down, 35 -> 34.
- **The class enumerator**: `enumerate.py --null` reads `RESULT null_fixture_instances=0`.
- **The corpus re-measure**: `calibrate.py --measure-corpus --jobs 4` prints the
  committed `corpus_vectors.json`, byte for byte, both before and after the
  entity-key change below -- the same command's output is not constant, since the
  merge base's file hashes differently and differs on exactly one leaf.
- **The golden fixtures**: the strict-mode red under `## Red checks` reproduces
  on `origin/main`'s own tree with this branch's changes removed.

## Figures

Every line below was re-taken at `540ede178c846c7270465161d967bf5b7e2182e3`; a figure
that is a function of `origin/main`'s tip is dated above. The prose figures --
1201 lines added per arm (`class_growth.py`'s `RESULT lines_added_per_arm`), 16 budget
keys (`python3 -c "import json;print(len(json.load(open('tests/structure_budgets.json')))-1)"`),
3495 lines for `HeatPumpOptimizer` and 8688 for the coordinator (`tests/structure.py`'s
`classes over 300 LOC` table), 56 counting rules and 10 seams (`tests/structure.py`'s
`ok 56 counting rules hold`; the enumerator's `RESULT seams=10`) -- are each their
instrument's own line, re-taken in the same pass.

**The finding's own harnesses, both ends.** The baseline end is an export of
`e8718ec3b52e24531236c30e508a4d1b3cf086ed` (`git archive $(git merge-base origin/main HEAD)`),
and both harnesses are the round-10 record's, at `dev/audit/rounds/round10/D7/`.

- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/s1/class_growth.py` --
  D7-s1-01's harness. Merge base: `RESULT keys_moved_second_class=0 count`,
  `RESULT keys_moved_coordinator=1 count`. Head: `RESULT keys_moved_second_class=1 count`,
  `RESULT keys_moved_coordinator=2 count`. It moves, and the coordinator arm stays
  a control: both ends move `max_class_loc` by exactly +1201 for the same pad.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/s3/namekept_receivers.py` --
  D7-s3-01's harness. **Flat at both ends**: `RESULT candidates_with_zero_typed_hits=6`
  and `RESULT total_typed_hits=0 sites` on the merge base and on the head. It is
  keyed to the instance it demonstrated (a text hint on the receiver's name), not
  to the property, so the fix is invisible to it. Its own perturbation still
  moves it: with `HPO_RECV_EXTRA='drift.py:Cusum:reset:cusum.reset()'` the head reads
  `RESULT Cusum.reset_typed_hits=1 sites`, 0 -> 1.

**The companion that applies the tree's own rule to the same six**,
`dev/audit/harnesses/r10_structure_blind.py`, sha1 `072d5d6c94526fcabdbef893d23474c92a076bdd`.
Three arms, the same command with `--structure` and `--package-ref`:

| arm | command suffix | six_measured_dead | six_name_kept | name_kept | dead_methods | second_keys_moved |
|---|---|---|---|---|---|---|
| head census, head tree | (none) | 0 | 2 | 39 | 0 | 1 |
| head census, merge base's package | `--package-ref $(git merge-base origin/main HEAD)` | 4 | 2 | 39 | 4 | 1 |
| base census, merge base's package | `--structure <merge base>/tests/structure.py --package-ref ...` | 0 | 6 | 153 | 0 | 0 |

The middle arm is the finding's verdict: the census the branch ships measures 4
of D7-s3-01's 6 dead on the tree where all 6 stand, against 0 for the census it
replaces. The move and merge arms are `RESULT move_class_excess_delta=0 lines` and
`RESULT merge_class_excess_delta=-12 lines` at the head, `absent` at the base, and
`RESULT move_max_class_loc_delta=-12 lines` at both -- the row the fix leaves in
place still prices a verbatim move as a gain; the one it adds does not.

**The seam enumeration (fixer.md step 8).** The class's own enumerator,
`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-N-structure-blind/enumerate.py`,
reads `RESULT seams=10` / `RESULT instances=5` at the head and the same at the merge
base, and `--perturb` (one count-over-threshold key planted on `god_classes`) moves
it to `RESULT instances=4`. Every returned seam, against its disposition:

| seam | disposition |
|---|---|
| `A measure:max_class_loc` | **closed in this diff**, by `class_excess_loc` |
| `A measure:max_cc` | already guarded (its threshold siblings are on the table) |
| `A measure:max_method_loc` | already guarded |
| `B dead_members:name_kept` | **closed in part**: 153 -> 39 on the merge base's package, and 4 of the finding's 6 now measured dead. The residual 2 are the census's documented boundary, printed by the census itself and counted by the companion (`six_name_kept=2`) |
| `B HA_CONVENTION_NAMES` | already guarded (`0` convention-named defs outside the HA-loaded modules) |
| `C card.js` | a distinct finding, D7-s3-02, in `R10-ARCHSCORE-COVERAGE`'s scope |
| `D is_any` | a distinct finding, D7-s3-52, in `R10-ARCHSCORE-COVERAGE`'s scope |
| `D is_coord_annotation` | already guarded |
| `D annotation_members` | not applicable (unparse used for display only) |
| `E Flow.returned_keys` | a distinct finding, D7-s3-51, in `R10-ARCHSCORE-COVERAGE`'s scope |

Seam A needs its reason said out loud, because the command still returns it.
Rule A's text is "a budget key = `max()` over a unit table with no
threshold-count sibling on the same table (a non-max unit grows unpriced)" --
the *property* in its second clause. `class_excess_loc` prices a non-max unit
growing, so the property no longer holds; what still matches is the rule's
first clause, a shape. The rule looks for a `len()` sibling, and a sum of
excesses is not one; `--perturb` shows how narrow that test is, since planting a
count key on the table flips the row to `guarded` while changing nothing about
whether growth is priced. The rule that checks the property is the one the
finding itself names, `class_growth.py`, and it reads 0 -> 1. Editing the
round-10 enumerator to recognise the new sibling would make the record agree with
the fix rather than with the tree (fixer.md step 8), so it is left as it stands.

**The entity convention key (fixer.md step 14).** `available` and
`target_temperature` are the HA-read members D7-s3-01's typed receivers took the
luck away from; `HA_CONVENTION_METHODS` is keyed on the member name alone, and
the companion's separation arm (`RESULT entity_members_keyed=21 count`,
`RESULT same_name_not_keyed=2 count`) names the two members that key would have
silenced as well:

    not keyed (a name-only entry would silence it): coordinator.HeatPumpOptimizerCoordinator.target_temperature
    not keyed (a name-only entry would silence it): open_meteo.OpenMeteoSolar.available

Both are live today by a real edge, so the entry would have hidden nothing yet --
it would have hidden their deaths. They went instead to `HA_ENTITY_METHODS`,
matched only where the member's class family derives from an external `*Entity`
base, which is also what reaches the entity mixins in `entity.py`; the two
halves are pinned by `entity_self_check`. Measured effect of the narrowing on
every tree the corpus stores: none -- the corpus re-measure after it is byte-identical.

**The structure ratchet**, `PYTHONPATH=tests/hastub python3 tests/structure.py`:
`class_excess_loc=18498 count`, `dead_methods=0`, `name_kept` 39 members printed,
`max_class_loc=8688`, `duplication_copies=34`, `ok 56 counting rules hold`,
`STRUCTURE RATCHET PASSED`.

**The corpus**, `PYTHONPATH=tests/hastub python3 tools/audit/archscore/calibrate.py --measure-corpus --jobs 4`:
the committed `tools/audit/archscore/calibration/corpus_vectors.json` is its
output, `sha1sum` `51ad156c162979f5304bc85f56e43aa42cbf87f9`; the merge base's file
is `91700eaaee729d8d93f8b4a9338496696af5e8b7`, and `diff` between them names one key,
`dead_members`, on 85 of the 87 stored trees. `tests/arch_score.py` passes on it,
`ALL 64 ARCHITECTURE SCORE CHECKS PASSED`.

## Architecture score

`PYTHONPATH=tests/hastub python3 tools/audit/archscore/score.py --diff origin/main`:
`Architecture score: dS +1.7787 IMPROVES`, admissible, no metric up.

- `dead_members 5 -> 1` (+1.5850) -- the four members the sharper census measures dead.
- `duplication_copies 66 -> 65` (+0.1937) -- one of the four deleted members was a copy.

`tools/audit/archscore/ABOUT.md` carries the change: the corpus leaf that moved,
the one planted verdict that turned (`a3_dead_by_reachability_fix`, GOOD, NULL ->
IMPROVES -- the fix the case is, and the pre-study's own reading), and the
retired row in its pre-study difference table.

## Red checks

`tests/golden.py` in `GOLDEN_MODE=strict`, the only red the scoped gate reports
(`1 TEST SCRIPT(S) FAILED`, `55 of 56 GOLDEN SCENARIOS CHANGED`).
**Not this diff.** The strict mode compares this machine's scenarios against the
committed fixtures, which were recorded on CI's x86_64 BLAS; solver floats are
not bit-stable across builds, which is why CI runs
`GOLDEN_MODE=drift` (fixer.md step 5). Three readings:

- `GOLDEN_MODE=drift PYTHONPATH=tests/hastub python3 tests/golden.py` -- the mode CI
  runs: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`. This
  tree computes what `origin/main` computes, in this environment.
- The same strict command on `origin/main`'s own tree, with none of this branch's
  changes (`git worktree add <dir> origin/main`, `GOLDEN_MODE=strict GOLDEN_REF=<head> python3 tests/golden.py`,
  worktree removed afterwards): `55 of 56 GOLDEN SCENARIOS CHANGED`, the same count
  and the same fields, on the machine that ran the gate.
- `git diff $(git merge-base origin/main HEAD)...HEAD --stat` touches no solver, no
  `tests/golden/` fixture and no `tests/golden/claimed_drift.txt`; both claim files
  are byte-identical to the merge base's.

The cheaper detector that could have run this before CI: `GOLDEN_MODE=drift` is
already the mode the run sheet names, and this seat ran the gate without it the
first time; the standing cost of the drift gate is one baseline capture per
`origin/main` tip (~70 s against the strict comparison's ~230 s), which the scoped
gate already pays.

**The one red this branch predicted for itself, and repaired before the handoff**:
`tools/pr/prepr.sh`'s `ci predict` arm read
`PREDICT closures INERT READS tests/harness_headers.py: dev/audit/harnesses/r10_structure_blind.py
(a new file beside 35 it lists)`. `tests/harness_headers.py` reads every harness in
`dev/audit/harnesses/`, so a new harness leaves its recorded closure one file short.
`tests/derive_closures.sh --single` does not clear it (`dev/audit/rca/R10-HANDOFF-PREPR-BOUNCE.md`
on `handoff/r10-rca-prepr-bounce` measures the attempt), and the repair is the one that
arm's RCA prescribes: `dev/audit/harnesses/r10_structure_blind.py` added to
`inert_reads["tests/harness_headers.py"]` in `tests/closures.json` by hand, one line
(precedents 387128bb, fbc9400a9, d7bfeb0dd). `prepr.sh` then reads `clean no refusal`.
This is not a defect this diff introduced -- any new harness beside 35 hits it -- and
the standing cheaper detector is the `prepr.sh` `ci predict` arm itself, which runs in
seconds at the local head.

## Unpinned sites

`none`: `prepr.sh` reads `skip unpinned sites -- the diff adds no unpinned mutation site`.

## Forward-carry

- `R10-ARCHSCORE-COVERAGE` (`dev/programme/rosters/wave-r10-groups.json`, its
  entry's `carry`): it reads `tests/structure.py` through
  `tools/audit/archscore/vector.py`, so its corpus re-measure after this merge
  starts from `dead_members` 85 trees higher and from
  `a3_dead_by_reachability_fix` reading IMPROVES; if its `expected.json` is
  re-recorded from a base without this change, that verdict turns back to NULL.
  Reported to the orchestrator, which owns the roster.

## Friction

`fixer.md#8: cost: the class's seam rule (`enumerate.py` rule A) tests a shape -- a `len()` sibling on the maxima table -- while its own text states a property ("a non-max unit grows unpriced"), so a fix that closes the property leaves the rule firing and the disposition has to be argued rather than read. Measured: `--perturb` flips the row to `guarded` without changing whether growth is priced.`
