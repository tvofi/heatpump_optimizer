R11-PRE-BRIEFS-CENSUS: seven dimension briefs name their step's universe as a command, and the command is built. Policy pull request (dimension briefs, `policy_budgets.json`); finder-critical.

Built from the round-11 start evaluation at `9de7c2bdc73361a5428d85bc444bf973c43bb593`, the tip of `eval/r11`, which the review commit `f6d35cf73f` on `eval-review/r11-4` approves (`review.verdict` `approve` naming that sha, round 4, replacing round 3's approve of `02a48db212`). At that sha all seven cards this group closes carry `decision` `accepted` with tvofi's ruling: E11-D0, E11-D1, E11-D2, E11-D8, E11-D12, E11-D15 ("Accept all 14", made final) and E11-D9 ("Accept all four"). Work began at `7891b714f8` and each card was re-read at `02a48db212` and again at `9de7c2bdc7`: E11-D2 gained one input at the first re-read (a learned draw range fed censored samples), built here; at the second, three proposals changed only to say `escapes and seat-found defects`, with no input added or dropped, and no card was dropped. Merge timing (decision 0018 section 6): this head is not an ancestor of `f6d35cf73f`, and each card's object file is changed here.

**Wording.** A dimension brief is in the owner's words. Every sentence added to `D0.md`, `D1.md`, `D2.md`, `D8.md`, `D9.md`, `D12.md` and `D15.md` was drafted by this seat under mandate 6893738184 (scope all, in force to 2026-12-15T12:00Z).

**Card E11-D9** was built last, in its own commit (`db626fb9dd`), held out until the evaluation recorded its ruling, and is in this head.

**What a brief now names, and the ledger row each new input answers** (`dev/audit/rounds/round11/evaluation/escapes_hand.tsv` at `9de7c2bdc7`; a row marked seat-found is `out` there, a defect a programme seat found with no report from an install, whose input the card keeps; step numbering is kept, and two steps are added):

| brief | universe command(s) | input added, at the step the ledger names | ledger row |
|---|---|---|---|
| D0 | step 4 `enumerate.py d0-grid`; step 8 (new) the same-information oracle per grid cell and per install-day of `d15-installs`, with `C_real`, `C_same` and the model gap side by side | plant `flow-setpoint-behind-valve`; plant `manual-valve-buffer` (step 4) | R10-SETPOINT-POWER; R10-BUFFER-STORE (seat-found) |
| D1 | steps 1 to 6: `d1-lifecycle`, `d1-stores`, `d1-inputs`, `d1-solve-state`, `d1-excepts`, `d1-parsers` | a stored override across restore then resolve (1); a save during the learners' load, and the previous release's persisted record driven to the first actuator write (2); a presence entity changing between two updates, a price fetch raising while the last prices cover now, an input missing and back inside one interval (3) | R10-HOTFIX-AWAY-LIVE; R10-LEARNED-STORE-LOAD (seat-found), R10-HOTFIX-FLOW-SETPOINT-STUCK; R10-HOTFIX-AWAY-PRESENCE, R10-OUTSIDE-PRICE-OUTAGE-LAST-VALID, R10-INPUT-REAPPEAR |
| D2 | `d2-identities --cells`, read from the new register `dev/audit/config/identities.json` | the switch-back slab (1); the savings identity on a valve house with the buffer above the curve and on a month upgraded mid-month (3); the pump's own power estimate, a moved covariate, the tank's fall after a charge starts, booked against metered space energy, a draw range fed censored samples (5) | R10-COP-GATE-E (seat-found); R10-HOTFIX-SAV-ESTIMATE, R10-SAVINGS-NEGATIVE; R10-HOTFIX-LEARNER-INPUTS, R10-OUTSIDE-DHW-CHARGE-SETTLE, R10-DEMAND-OVERBOOK, R10-SETPOINT-BOOST (second cause) |
| D8 | step 1 `d8-cells` (entity by state by language); step 3 compares every translation file, where it said both | a step's reason above a 1.1 heat-loss scale under flat weather; a merged slot's average power on a non-modulating pump with a minimum power (2) | R10-HOTFIX-PREHEAT-LABEL; R10-MIN-POWER-FLOOR |
| D9 | per metric: `d9-solves` (full solves per cycle), `d9-collections` (retained bytes), `d9-attributes` (payload bytes); each row reports examined over its metric's universe | none: the card names no escape | none |
| D12 | `check_scopes.py --repo . --population` plus the card and the blueprints, printed per cell by `d12-cells [--pairs]`; the cell ledger through `--ledger` | a counter-metered pump whose spans hold hot-water charges, and a short boost (3) | R10-OUTSIDE-LEARNER-ROBUSTNESS |
| D15 | `d15-installs`, read from the new register `dev/audit/config/bundles.json`; a round with no bundle reports 0 of its lines; step 9 (new) the oracle per install-day | a real download whose replay half is empty because one entity id escapes the mask (1) | R10-FLY-REPLAY-MASK |

Intake carry 175 is built by the same rows. D12 declares the two NO-READ axes' levels as the flow row's minimum, default and maximum and says where they are read (`objective.json` `population`, through `--population`); the levels themselves are R11-PRE-OWNER-CRITERIA's file.

**The enumerator** is `tools/audit/enumerate.py`: the prototype at `530cda6a24` ported (`d0-grid`, `d0-modules`, `d1-stores`, `d1-excepts`, `d1-lifecycle`, `d3-sites`, `d14-classes`, `d16-writes`, `d17-features`) and ten universes added. Design choices a reviewer should not read as bugs:

- It refuses in two places only: `run()` turns a missing source (an `OSError`) and a zero-line universe into exit 2. A per-universe guard remains only where its removal changes an outcome, and each has a self-test arm.
- `d9-solves` climbs callers by name inside the solver's own module and prints, without climbing, a site in another module. Climbing across modules by name prints every caller of any function sharing a name with one on the path; the self-test's not-climbed arm is the control.
- `--ledger TSV` joins any universe to the asserting test of each line, or `not run` (decision 0018 section 1 asks D1 and D8 for the census with its driving test). A generality cell also carries its source, one of 0018's four, and prints `not run` with no ledger.
- `d0-grid`'s plant, zone, hot-water and horizon levels are literals in the script, as in the prototype, pinned by a self-test arm: D0 step 4 no longer types them.
- A self-test line is mutated like any other added line; a survivor there is a mutant of the test, not of the instrument, and is listed without an arm.
- `--briefs` is this group's acceptance as a command: every `enumerate.py <universe>` a dimension brief cites runs non-empty, and a tree citing none is refused.

The two registers hold what no source prints: `identities.json` the identities D2's steps execute with each one's grid, `bundles.json` the one bundle a round has read (round 10's, 2026-10-14, by `dev/audit/rounds/round10/D15/s1/intake.py`; steps from `rotation.json`'s round-10 coverage other than `none`). The install label is opaque.

Files outside the group's list, each because the brief's own terms require it: `dev/audit/config/rotation.json` and `scopes.json` (rows D0.M8 and D15.M9, which `check-wave-script.mjs` requires of an added step), `.github/workflows/governance.yml` (one line: the self-test rides the step that already runs `check_scopes.py --self-test`, as the prototype's did), and the new files.

Alternatives that lost: one enumerator per dimension (seven scripts, seven self-tests, one refusal rule copied seven times); the identity list parsed out of `D2.md`'s prose (a wrapped sentence is no register, and the grid has no place there); cutting D2's identity prose to pay its cap once the register held it (prose moved to an uncapped file is the hole `ratchet-budgets.md` closes).

## Head

db626fb9dde5ca152ce45e7c216e3c7676553b4e

## Mutation proof

`python3 -I tools/audit/seat/mutant_run.py --diff <merge base>...HEAD --cmd "python3 -I tools/audit/enumerate.py --self-test" --report-only --in-place`, in a detached worktree. Two earlier passes drove the repairs: at `1ebe9f57d1` (cap 40) 10 survivors, nine of them guards whose removal changed no outcome; at `0c0eec4248` the production lines left 17 more, in the ported option branches of `d3-sites` and `d0-modules`, the `d9-solves` worklist and three index constants. Commits `0c0eec4248` and `2afcb72317` deleted what changed nothing and added an arm for each of the rest.

At this head:

- prepr.sh's diff-mutant step (`MUTANT_CMD` the self-test, `MUTANT_IN_PLACE=1`, the first 40 mutants of the added lines): see `## Figures`.
- The lines changed since the last complete pass, `mutant_run.py --diff 0c0eec4248...HEAD --max-mutants 22` (the production lines of that delta: `joined()`, `run()`, the `d9-solves` closure, the population line split, the two `sys.path` appends): 22 mutants, 0 `SURVIVED`, exit 0.
- The D9 commit on top adds no Python line, so the two readings above (taken at `2afcb72317`) are of this head's `tools/audit/enumerate.py`, byte for byte; prepr's step was re-run at this head all the same.
- Not re-run end to end at this head: the production lines untouched since `0c0eec4248`, whose survivors that pass listed and the two commits above answered. A pass over every added line takes over an hour here (about 13 s a mutant), which is why the last one is the delta.

By hand, predicates and not tails, each restored after:

- run(): the zero-line refusal off: self-test exits 1; 18 arm(s): d0-grid  source emptied; d1-lifecycle  source emptied; d1-inputs  source emptied ...
- run(): a missing source not turned into the refusal: self-test exits 1; it stops on the uncaught FileNotFoundError of the first removed source (d0-modules' emptied-source arm)
- joined(): a row with no test accepted: self-test exits 1; 2 arm(s): d12 ledger: a row asserting nothing is refused; ledger: a census row naming no test is refused
- joined(): any source accepted: self-test exits 1; 1 arm(s): d12 ledger: an unknown source is refused
- joined(): a row naming no item accepted: self-test exits 1; 4 arm(s): d12 ledger: a row naming no cell is refused; d12 ledger: a pair row without --pairs is refused; a ledger refusal names the row's line ...
- d15: evidence not checked: self-test exits 1; 1 arm(s): d15 a bundle whose evidence is not in the tree is refused
- d0-grid: one escape plant dropped: self-test exits 1; 3 arm(s): d0-grid  planted; d0-grid  one item deleted; d0-grid the two plants round 10's escapes name are levels
- d9-solves: the climb not bounded to the solver's module: self-test exits 1; 4 arm(s): d9-solves  planted; d9-solves  one item deleted; d9-solves lines: the solver's call, the recursive call inside its module, the coordinator's call and its bare reference ...
- --briefs: an empty citation set accepted: self-test exits 1; 1 arm(s): briefs: a tree whose briefs cite none is refused
- d12: level count not asserted: self-test exits 1; 1 arm(s): d12 a cell count that disagrees with the population's LEVELS is refused

## Null control

- The unmodified tree: `python3 -I tools/audit/enumerate.py --briefs --repo <a checkout of 26dbf7c43e>` exits 2, `REFUSE: no dimension brief cites a universe`; `d15-installs` and `d2-identities` against that checkout exit 2 on the missing register. At this head `--briefs` exits 0.
- The cards' own control: `dimension_read.py` prints 0 round-10 rows carrying examined over a universe, and a brief left unchanged keeps printing 0. No round-11 report exists yet, so this pull request moves the brief, not that count; the count is the round's to read.
- `check-wave-script.mjs` is unchanged by this diff, so the base's copy grades the head: 0 failed. With `rotation.json` restored from the merge base it fails on `rotation.json D0 lacks D0.M8` (the null for the added steps).

## Figures

- `python3 -I tools/audit/enumerate.py --self-test` at db626fb9dde5ca152ce45e7c216e3c7676553b4e: `SELF-TEST passed (134 arms)`. The arm count is what the script prints; an arm is one comparison in `self_test()`.
- `python3 -I tools/audit/enumerate.py --briefs` at db626fb9dde5ca152ce45e7c216e3c7676553b4e: exit 0, 15 `ok` lines, one per brief and distinct cited command (D0 2, D1 6, D2 1, D8 1, D9 3, D12 1, D15 1). Against a checkout of 26dbf7c43ec3742101398b098dbdcc61bbee8f19: exit 2, `REFUSE: no dimension brief cites a universe`.
- `node tools/policy/check-wave-script.mjs` at db626fb9dde5ca152ce45e7c216e3c7676553b4e: 223 passed, 0 failed; the same file at 26dbf7c43ec3742101398b098dbdcc61bbee8f19: 223 passed, 0 failed (this diff does not change it). At this head with `dev/audit/config/rotation.json` restored from 26dbf7c43ec3742101398b098dbdcc61bbee8f19: 221 passed, 2 failed, naming `rotation.json D0 lacks D0.M8` and `D15 lacks D15.M9`.
- `node tools/policy/policy_lint.mjs` at db626fb9dde5ca152ce45e7c216e3c7676553b4e: `TOTAL: 0 error(s)`. With `policy_budgets.json` restored from 26dbf7c43ec3742101398b098dbdcc61bbee8f19: `TOTAL: 14 error(s)`, all `[budgets]`: the line row and the token row of D0, D1, D2, D8, D12 and D15, D9's token row, and the corpus.
- `python3 -I tools/audit/check_scopes.py --repo .` at db626fb9dde5ca152ce45e7c216e3c7676553b4e: exit 0.
- Gate scope, `python3 tests/closure.py select --diff 26dbf7c43ec3742101398b098dbdcc61bbee8f19`: `MODE: FULL`, reason `tools/ci/selftest_closures.json changes the gate itself`; before that file changed the same command read `MODE: SCOPED -- 3 script(s) run` (`tests/entities.py`, `tests/harness_headers.py`, `tests/layout.py`). Those three, with `PYTHONPATH=tests/hastub`, at db626fb9dde5ca152ce45e7c216e3c7676553b4e: `ALL 2723 ENTITY CHECKS PASSED`, `ALL 115 HARNESS HEADER CHECKS PASSED`, `layout self-test: ok`, each exit 0. The rest of the full suite is CI's.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (prepr's merged-structure step, HEAD merged with origin/main).
- `python3 -I tools/pr/ci_predict.py --base origin/main`: no closures, fast, governance or instrument red predicted.
- `python3 -I tools/ci/selftest_scope.py record --step self-tests-outside-seat` (Linux, strace): 1 step recorded, 0 failed, 0 broken traces; 559.4 s.
- `python3 -I tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- `tools/pr/prepr.sh` at db626fb9dde5ca152ce45e7c216e3c7676553b4e with `MUTANT_CMD` the self-test and `MUTANT_IN_PLACE=1`: every branch step `ok` or `skip`, among them `diff mutants: no survivor among the diff's first 40 mutant(s)`, `throwaway git`, `ci predict` and `merged structure`; `tools/pr/prepr.sh --body-check` on this body: `PR-BODY: 0 error(s)`. One of the 40 (the visited-set update of `d0-modules` deleted) never returns and is killed by `mutant_run.py`'s own timeout.

## Raise justification

Rows of `node tools/policy/policy_lint.mjs --budgets` raised, each to the value it measures at this head (the literal values are in the diff of `dev/governance/config/policy_budgets.json`): the `lines` and `~tokens` rows of `tools/audit/briefs/D0.md`, `D1.md`, `D2.md`, `D8.md`, `D12.md` (the keys the lint keeps for the files now under `dev/governance/dimensions/`) and `dev/governance/dimensions/D15.md`, the `~tokens` row of `tools/audit/briefs/D9.md` (its `lines` row had room and is untouched), and `corpus:`. The other aggregates are inside their band and untouched. `INSTRUMENTS.md` has no row.

Payments tried: (1) taken: the typed lists the enumerator now prints are cut from the briefs (D0 step 4's axes and its typed profile count, D1 step 2's store list and step 4's read list, D12 step 1's scenario names, its `Derive the cell count` sentence and step 2's axis list, D15's no-bundle rule); they did not cover the growth. (2) not taken: cutting D2's identity prose now that `identities.json` lists the identities: the prose would move to an uncapped file, the reclassification `ratchet-budgets.md` refuses, and a finder would lose each identity's tolerance. (3) not taken: cutting a brief's `Traps` or `Reuse` section: each line there is a live constraint (a refused technique with its issue, a stub artefact), none spent or duplicated. (4) not taken: stating the census commands once in `COMMON.md` and not per brief: the universe differs per step, and `COMMON.md` is R11-PRE-BRIEFS-TEXT's. (5) not taken: leaving out the escape inputs: they are the cards' substance. No code payment exists: the diff adds no line under `custom_components/`.

Architecture score: dS +0.0000 NULL

## Approval

Pending; none is claimed here. This is a policy pull request (seven dimension briefs and `policy_budgets.json`): it merges on tvofi's approving review at the head, or, under mandate 6893738184 (scope all, in force to 2026-12-15T12:00Z), on the orchestrator's declared review after the fix review, which is also what approves the budget raise (decision 0013). The wording of the briefs is the seat's draft under that mandate and is the owner's to change at review.

## Red checks

- budget-raise-gate: red by design, not a defect: this diff raises rows of `dev/governance/config/policy_budgets.json`, and the gate stays red until an approving review at the head, tvofi's or the mandated one under 6893738184 after review (`## Raise justification` above is what it reads). Cheaper detector: none is owed, the red is the gate doing its work; `node tools/policy/policy_lint.mjs --budgets` prints each raised row locally before any push, at no standing cost.

## Forward-carry

- Carry 0 (intake carry 175, from #3575 body item 7ce997a6: decision 0018 section 1's brief edits): built in this pull request for the files it gives this group. D12 names `--population` plus the card and the blueprints as its universe, declares the two NO-READ axes' levels and keeps the cell ledger (`d12-cells --ledger`); D0 and D15 gain the same-information oracle step with the realised-cost record per install-day and the model gap beside both; D1, D2, D8 and D15 name their census. Its two other parts are already in their groups' briefs on the round-11 roster (the roster branch at 032023814b): the actuator-write half in R11-PRE-NEW-DIMENSIONS' and the D11 half in R11-PRE-BRIEFS-TEXT's. Carry: dismissed: built here, and its other two halves already sit in their owners' briefs
- `d16-writes [--cells]` and `d17-features` are in `tools/audit/enumerate.py` under the prototype's names, which card E11-U10 also uses, for the two new dimension briefs to cite; `--briefs` will then run them as acceptance. `rotation.json` and `scopes.json` already carry D0.M8 and D15.M9 from this head, so that group's rows for the new dimensions land on distinct keys. Carry: R11-PRE-NEW-DIMENSIONS
- `tank_volume` and `house_size` print `NO-READ` from `--population` until `dev/audit/config/objective.json` `population` declares their levels; D12 states them as the flow row's minimum, default and maximum. Once declared, `d12-cells` prints them with no change here: it asserts its level and pair counts against the totals `--population` prints, and refuses on a disagreement. Carry: R11-PRE-OWNER-CRITERIA
- `d9-collections` reads `coordinator.py` only, at each class attribute's first container binding; a collection a learner or a side table in another module retains is not a line. A D9 seat that measures one reports it beside the universe. Carry: dismissed: the rule is stated in the script's docstring and D9's text sends the seat to the command; widening it is a finding for round 11's D9 seat to raise with a measurement
- `d1-parsers` reads names and three call shapes; a parser of pump-signal states that is neither is not a line, and D1 step 6 keeps its prose list for that reason. Carry: dismissed: the brief carries the list the census cannot, as written in this diff

## Friction

- orchestrator: cost: `eval/r11` moved twice under this seat (`7891b714f8`, `02a48db212`, `9de7c2bdc7`), and for one of those tips the approving `review` field was on `eval-review/r11-3` only while the dispatch names the field on `eval/r11`; each move cost a re-read of seven cards, and the last one moved D9 from held out to included after a clean pre-handoff run. Carry: dismissed: the brief ordered the re-read and it found one input and one ruling; nothing to build
- fixer: cost: `python3 -I tools/ci/selftest_scope.py record --step self-tests-outside-seat` took 559 s under strace for a one-line change to the step's `run:` text, and rewrote duplicate probe entries in six other steps. Carry: dismissed: one occurrence, and the recorder's output is the measured table
- ratchet-budgets: stale: `policy_budgets.json` keys six of the seven briefs as `tools/audit/briefs/D<n>.md` while the files are under `dev/governance/dimensions/`; `--budgets` prints the old path, so a body naming its row names a path that does not exist. Carry: dismissed: the lint resolves the alias and the rows are named here as printed
- fixer: cost: `prepr.sh` refused the self-test's raw `git init` (the throwaway-git rule) only at the pre-handoff run; `python3 -I tests/throwaway_git.py --check` reads HEAD and takes under a second, and nothing ran it at the commit that added the line. Carry: dismissed: one occurrence, repaired in this head, and the check is already in prepr and CI
