R11-PRE-BRIEFS-CENSUS, part 2: `enumerate.py d12-cells` prints the declared levels of tank volume and house size as cells. One file, `tools/audit/enumerate.py`; no dimension brief, budget or config file changes, so this is not a policy pull request and no sentence of a brief is drafted here.

**What part 1 left.** #3625 (merged `f1520e3539`) built the seven briefs and the enumerator. Read at the approved evaluation, `eval/r11` `83dc948818` (`review.verdict` `approve` naming that sha, round 4, commit `c04cef7fca`): the seven cards E11-D0, E11-D1, E11-D2, E11-D8, E11-D9, E11-D12 and E11-D15 are each `accepted` and `merged` `f1520e3539`; against `9de7c2bdc7`, the sha part 1 built from, each differs by its `gates_finders` and `merged` fields alone, so no card is rewritten or dropped and none is rebuilt here. The brief's acceptance holds at `origin/main` before this diff (`--briefs`, `check-wave-script.mjs`, both under `## Figures`).

**The gap.** Carry 0 gives D12 a cell ledger "printing each level and pair", the two continuous axes' levels declared in `dev/audit/config/objective.json`. Part 1's body carried `Once declared, d12-cells prints them with no change here` to R11-PRE-OWNER-CRITERIA. That group declared them (`8221ddad44`), and the sentence is false at `origin/main`: the two rows keep `kind` null, `--population` keeps printing both axes `NO-READ`, and `d12-cells` took its axes from the lines that print a level. So it printed no cell for either axis, wrote `no cell until dev/audit/config/objective.json declares its levels` about levels that file declares, and refused the ledger row of a level D12 step 1 tells the seat to drive (`'level tank_volume=min' is no item of this universe as printed`).

**The fix.** `population_axes` takes, for an axis `--population` prints `NO-READ`, the level names its `objective.json` row declares, and raises the two totals it returns by what those levels add (levels; pairs with every other level and between two declared axes). `d12`'s count assertions, `d2-identities`' grids and `product_reads.py`'s `generality` read all go through that one function, so each sees the axes with no change of its own. An axis declaring no level keeps the old line, which is then true. The line on stderr for a declared axis says what stays unread: no reader compares the levels with the flow rows they were taken from, which is the `no_read` reason `objective.json` records and whose builder it names.

Design choices a reviewer should not read as bugs: a cell is `level <axis>=<name>` with the declared name (`min`, `default`, `max`) and never the value, so a ledger row survives the flow row moving; `--population`'s own output and totals are unchanged (`check_scopes.py` is not this group's file, and round-11 records were measured against its totals).

Alternatives that lost: (1) `check_scopes.py --population` printing the declared levels and counting them in `LEVELS` and `PAIRS`: it moves totals the start evaluation was read against and makes the axis read while the comparison with the flow row, which is the reason it is `NO-READ`, is still unbuilt. (2) D12's prose listing the six cells for the seat to type: the ledger would still refuse their rows. (3) correcting only the stderr line: the ledger gap stays.

## Head

93f45781beff18f67719c0586f9673634c9519ca

Measured at this head, merge base and origin/main 38bf516bdd73f926ee9639ffda7b9ca5163fd50e, 2026-11-17T01:00Z.

## Mutation proof

Failing test first: with the five new arms added and `population_axes` as at the merge base, `python3 -I tools/audit/enumerate.py --self-test` exits 1 naming four of them (`d12 a NO-READ axis whose levels are declared is one cell per level`, `d12 a declared level pairs with every level of another axis`, `d12 ledger: a declared level's row is joined`, `d12 two declared axes pair with each other once`); the fifth (`d12 a NO-READ axis declaring no level is no cell`) pins the unchanged arm.

By hand at this head, predicates and not tails, each restored after (the restored tree prints `SELF-TEST passed`):

- the declared branch turned off (`if False:`): exit 1, the same four arms.
- the `PAIRS` raise deleted: exit 1, `d12 a declared level pairs with every level of another axis` and `d12 two declared axes pair with each other once`.
- the term pairing two declared axes deleted: exit 1, `d12 two declared axes pair with each other once`.
- the `LEVELS` raise deleted: exit 1 on the uncaught `Refuse: 6 level cells against the population's LEVELS: 4` of the first planted declared axis.
- the two raises swapped, so `PAIRS` reads the raised `LEVELS`: exit 1, the two pair arms and `live d12-cells {'pairs': True}`.

The driver, prepr.sh's diff-mutant step at this head (`MUTANT_CMD` the self-test, `MUTANT_IN_PLACE=1`, which runs `mutant_run.py --diff <merge base>...HEAD --max-mutants 40 --report-only --in-place`): every mutant on a line of `population_axes` is killed, and the survivors are the six lines of `self_test()` under `## Unpinned sites`. An earlier pass of the same driver at `f8d55b8bd0` listed a seventh, the `CALL_DEL` of a fixture reset no later arm read; that line is deleted in `93f45781be`.

## Unpinned sites

Each is a line of `self_test()`: a mutant of the test, not of the instrument, so no arm is added for it (as in part 1); none is under `custom_components/`, so `mutation-autofix` reads none.

- tools/audit/enumerate.py:941 STMT_DEL: deletes the arm `d12 a NO-READ axis whose levels are declared is one cell per level`; a deleted arm cannot fail.
- tools/audit/enumerate.py:943 CALL_DEL: deletes the arm `d12 a declared level pairs with every level of another axis`.
- tools/audit/enumerate.py:945 CALL_DEL: deletes the arm `d12 ledger: a declared level's row is joined`.
- tools/audit/enumerate.py:946 CONST_SWAP: changes a planted level's value from 1 to 2; a cell is the level's name and never its value, so no line moves.
- tools/audit/enumerate.py:947 CALL_DEL: deletes the arm `d12 two declared axes pair with each other once`.
- tools/audit/enumerate.py:949 CALL_DEL: deletes the arm `d12 a NO-READ axis declaring no level is no cell`.

## Null control

- The unmodified tree (38bf516bdd73f926ee9639ffda7b9ca5163fd50e): `python3 -I tools/audit/enumerate.py d12-cells` prints no line starting `level tank_volume=` or `level house_size=`, and with `--ledger` on a one-row ledger naming `level tank_volume=min` exits 2. At the head the same two commands print six such lines and exit 0.
- An axis that declares nothing: the planted `size` axis with `levels` absent or `{}` gives no cell at the head (the fifth arm, and the planted counts of the two `d12-cells` cases, which this diff leaves as they were).
- `python3 tools/audit/check_scopes.py --repo . --population` prints the same three totals at both ends: the diff does not move the command D12 names.

## Figures

- `python3 -I tools/audit/enumerate.py --self-test`: `SELF-TEST passed (166 arms)` at the head, `(161 arms)` at the merge base; the count is what the script prints, one per comparison in `self_test()`.
- `python3 -I tools/audit/enumerate.py d12-cells | wc -l`: 207 at the head, 201 at the merge base; with `--pairs`: 20082 and 18897. The rise is the six declared levels and their pairs: each with every level `--population` reads, and the two axes with each other.
- `python3 -I tools/audit/enumerate.py --briefs`: exit 0 at both ends, one `ok` line per brief and distinct cited command: every universe a dimension brief names runs non-empty (the brief's acceptance; it was already met at the merge base).
- `node tools/policy/check-wave-script.mjs` at the head: 249 passed, 0 failed.
- `python3 -I tools/audit/check_scopes.py --repo .` at the head: exit 0.
- Gate scope, `python3 tests/closure.py select --diff 38bf516bdd73f926ee9639ffda7b9ca5163fd50e`: `MODE: SCOPED -- 0 script(s) run`, the one changed file in no script's measured closure; `scope.run` is empty. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 -I tools/pr/ci_predict.py --base origin/main`: no closures, fast, governance or instrument red predicted (but see `## Red checks`: the predictor does not run the step's other programs).
- `python3 -I tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- `tools/pr/prepr.sh` at the head with `MUTANT_CMD` the self-test, `MUTANT_IN_PLACE=1` and `PREPR_SKIP_CLOSURES=1`: every step `ok` or `skip` but two, `ci predict` (three carry destinations of the first draft of this body, since re-routed) and the diff-mutant warning (the six sites under `## Unpinned sites`). Then `PREPR_SKIP_CLOSURES=1 PREPR_SKIP_CODE=1 tools/pr/prepr.sh` with this body, a text-only delta: `PRE-PR: 93f45781beff18f67719c0586f9673634c9519ca ... rc=0`, `PR-BODY: 0 error(s)`.
- The class, by a rule and not by the instance (`fixer.md` step 8): `git grep -n -E "population_axes\(|check_scopes\.population\(|[^_a-z]population\(" -- tools dev/audit tests`, less the `def` lines, names every reader of the population. Each seam and its disposition: `tools/audit/enumerate.py` `population_axes` (closed in this diff) and its callers `d2` and `d12` (closed through it); `tools/audit/product_reads.py` `read_generality` (closed through it: `observables` gives both axes `no witness: no observable in the stub`, so a row on one is printed and never re-run; first Forward-carry line); `tools/audit/check_scopes.py` `population` and its two callers (the printer itself: already guarded, a `kind` null row must carry `no_read` and `builder`, and the comparison with the flow row is the build `objective.json` names); `tools/audit/seat/plant_recall.py` `population` (a distinct finding, third Forward-carry line); `dev/audit/rounds/round9/D13/s1/dora_by_job.py` (another function of that name, over merges: not a reader of this population).

## Red checks

none at the time of writing: no check has run on this head. One is predicted and is not this diff's: `python3 -I tools/audit/product_reads.py --self-test` exits 1 at the merge base 38bf516bdd73f926ee9639ffda7b9ca5163fd50e and at this head with the same traceback (the two outputs differ in two line numbers of `enumerate.py` and nothing else), and it runs in the step `self-tests-outside-seat` beside `enumerate.py --self-test`, which this diff selects. It is inherited from `main` (second Forward-carry line; the cause is two merged heads that were each green alone, named there), and `instrument-self-tests` is not in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints.

## Forward-carry

- `product_reads.py generality` reads its universe from `enumerate.py d12-cells --pairs`, so from this merge its universe holds the six declared level cells and their pairs, none of which its stub can witness (`observables` prints `no witness: no observable in the stub` for both axes). A `RESULT read=generality` line taken before this merge has the smaller universe; re-take it at the merge base of whoever quotes it. Control: `python3 -I tools/audit/enumerate.py d12-cells --pairs | wc -l` at both ends, under `## Figures`. Carry: dismissed: the read takes its universe from the command at each run, so nothing is to be built; only a figure quoted from before this merge is stale, and the read's group is carries-open
- `python3 -I tools/audit/product_reads.py --self-test` is red on `main`: it exits 1 at `54cb721164` (the merge of #3665) and at `origin/main` 38bf516bdd73f926ee9639ffda7b9ca5163fd50e, on `enumerate.Refuse: const.py PUMP_DUTY_MODES ['control', 'off'] are not the duty modes STATES names ['control', 'observe', 'off']`. Its planted `const.py` holds two duty modes; `d16-writes --cells` refuses unless they equal the modes `STATES` names since `4632a10bff` (R11-PRE-NEW-DIMENSIONS part 2), which is an ancestor of `54cb721164`: the two heads were each green alone. Adding `observe` to the planted tuple is not the whole repair: the self-test then stops on its own seed ledger (`'write ... pump_arbiter.py:8 apply | duty=control | running' is no item of this universe as printed`). The seed rows are cells of the form `<site> | duty=<mode> | <state>`, and `d16-writes --cells` now prints `<site> domain=<d> | <plan state>`: the `operation` read was built on the universe as it was before `4632a10bff`, so the repair is a decision about that read's cell format, not a fixture edit, and is not made here. R11-PRE-PRODUCT-READS is carries-open and its part-2 head (`handoff-wip/r11-pre-product-reads-p2` at `78c5741297`) does not touch the file and fails the same way. Carry: R11-INTAKE-R10-RESIDUE
- `tools/audit/seat/plant_recall.py` `population` reads the text `--population` prints and takes a level only from a line whose second field is a count, so a config plant whose `cell` is a declared level of tank volume or house size is refused as `no population level`. It closes with no change there once `--population` prints those levels, the build `objective.json` records for both axes; until then a plant cannot sit in those six cells. Carry: R11-INTAKE-R10-RESIDUE
- Carry 0 (intake carry 175): its D12 clause, the cell ledger over each level and pair, is complete with this diff for the two declared axes; the rest was built in #3625. Carry: dismissed: built in #3625 and here

## Friction

- orchestrator: cost: this seat was dispatched on the group's whole brief after #3625 had merged it and the approved evaluation recorded all seven cards `merged`; the roster entry still reads `next_step` `fire now on the cards` with stage `carries-open`, and finding what was left took a re-read of the cards, the acceptance commands and the carries before any work. Carry: dismissed: one occurrence; the body above states what was left so a later dispatch need not re-derive it
- finding-propagation: unenforced: part 1's carry to R11-PRE-OWNER-CRITERIA stated a consequence (`Once declared, d12-cells prints them with no change here`) with no control, and it was false once the precondition was met; the rule asks for the control with the claim and nothing checked it. Carry: dismissed: corrected by this diff, whose arms are the control the carry lacked
