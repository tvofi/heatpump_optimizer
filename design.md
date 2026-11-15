# R11-PRE-PRODUCT-READS: three product reads that count a cell only on a witness the read itself produced

Designer round 1; no verdict is on `design-verdict/R11-PRE-PRODUCT-READS`. Base: origin/main b3831ff64eca1936f0b618193ee86c3e337b51a9. No `after` group, so no predecessor handoff head; the heads this note relies on, none merged: R11-PRE-BRIEFS-CENSUS at 2afcb72317c45167ee4d963bf4ee53c2dbc74fc4 (`handoff-wip/r11-pre-briefs-census`; no `handoff/` ref), R11-PRE-NEW-DIMENSIONS design eb49f17976c34f6400a9d0e68c58d22f6523f4ee under verdict f050ffc77006c53d6654c0404028b0e9db3a7ba9 (`revise ... harness`), R11-PRE-ROUND-METRICS part 1 at ebd654c3bae14515bea4fd6536d95c98b4904289, roster `handoff/audit-r10-roster` at 3b4eb51e7f1580b1669a7f17bbbc4807e58c62d6. No finder harness: owner report (card E11-N-INTAKE-BUILDER); the planted cells of section 6 are the fixture. Seat tokens: the harness reports none.

## Figures

Literals are snapshots; re-measure at your merge base.

| id | figure | literal | enumerator |
|---|---|---|---|
| F1 | population levels; pairs; NO-READ axes | 195; 18696; 2 | `python3 tools/audit/check_scopes.py --repo . --population`, last three lines, at the base |
| F2 | generality cells with the card and blueprints; with pairs | 201; 18897 | in a checkout of 2afcb72317: `python3 -I tools/audit/enumerate.py d12-cells` piped to `wc -l`; the same with `--pairs` |
| F3 | actuator sites; cells | 38; 456 | there: `enumerate.py d16-writes`; the same with `--cells` |
| F4 | regret grid cells; its price by weather plane; install-days listed | 2400; 40; 1 | there: `enumerate.py d0-grid`; with `--plane price-weather`; `enumerate.py d15-installs` |
| F5 | spike on `tests/guard_pins.py` at the base: checks; write sites reached; checks turned FAIL by perturbing the payload from `pump_arbiter.py:1610`; by perturbing a site the script never reaches | 88; 2; 4; 0 | the appendix's script, with no site, then each site as its second argument |
| F6 | hits for an oracle or regret harness in the tree | 0 | `git grep -n -w -E "same.information\|C_same\|C_fore\|C_model" -- tools tests dev/audit/harnesses` piped to `wc -l`, at the base |

## 1. What other groups already land, and what is left

- **CENSUS (2afcb72317) lands every universe and the join**: `d12-cells [--pairs]`, `d16-writes --cells`, `d0-grid`, `d15-installs`, and `--ledger TSV`, which prints each item beside a seat's row or `not run`. It also lands the brief steps (D0 step 8, D15 step 9, D12 step 1's ledger). This group builds none of that and imports the universe from that script, never a second enumeration.
- **What the join cannot show** (`joined` at 2afcb72317 accepts any non-empty string as the test): that the named check exists, ran, asserted, or touched the cell. It prints no examined count, and 18696 pair rows cannot be typed. That is the gap decision 0018 section 1 names ("a run that asserts nothing examines nothing"), and it is this group's: **the producer of ledger rows and the count**.
- **NEW-DIMENSIONS** owns the D16 brief, the cell formula of `d16-writes --cells` and the plan-side oracle (both open under its `revise`). This group reads the cell strings as printed and takes no position on either; a changed formula changes this read's universe with no edit here.
- **ROUND-METRICS** builds the escapes record (Carry 0). Section 3.5 states the interface; nothing is built here.
- **No oracle exists** (F6): the harness behind `regret` is new and is this group's.

## 2. Owning seams (governance instruments; `tests/seam_map.json` maps coordinator methods only and none changes)

| concern | owner | callers only |
|---|---|---|
| a universe and its join to a ledger | `tools/audit/enumerate.py` (CENSUS) | the briefs, this group's reads |
| whether a ledger row is witnessed, and the examined count of `operation` and `generality` | a new script product_reads.py under `tools/audit/` | the round's objective record, D12 and D16 seats |
| `C_real`, `C_same`, `C_fore`, `C_model` per cell and install-day | a new script regret_oracle.py under `tools/audit/` | D0 step 8, D15 step 9, the objective record |
| the escapes record and `unowned` | ROUND-METRICS' instrument | the objective record |

Two scripts because the concerns share no code: the first runs test scripts under a recorder, the second runs the optimizer against a plant. No production file and no file under `tests/` is edited.

## 3. The shape

**3.1 One contract for all three reads.** Each subcommand prints its rows, then one line `RESULT read=<term> universe=N examined=n` with the term's value, and exits 0; an empty or unreadable universe exits 2 and prints no count (a refusal, as the enumerator's). `examined` counts only rows the read witnessed in this run; a row it could not witness prints with the reason and is not counted. Zero examined is a valid first read: it is the baseline (section 2 of the decision), never a failure.

**3.2 `operation`: a write is attributed to its site by the caller's frame.** The read runs each test script a ledger row cites, unedited, through `runpy` with two wrappers installed first on `tests/harness.py`: `FakeServices.async_call` records the calling frame's file and line, which is the key `d16-writes` prints (F5: both keys matched), and `Results.check` records each name and outcome. Per cited site it runs the script again with the payload written from that site perturbed (numbers offset, strings replaced). A row (cell, `script::check name`) is witnessed as:

- **moved**: the check is ok unperturbed and FAIL with that site perturbed. Counted.
- **reached** (hold sites, where a runtime wrapper cannot alter the refusal): `log_held` was called from that line before the check, and the check is ok. Counted, printed as its own number beside moved.
- **not witnessed**: unknown check, FAIL at the head, site never reached, or the check does not move. Printed with which; not counted.

Free by-product: a write whose calling line is no listed site prints `unlisted writer`, which is F3 of the sibling design (the service call handed on at `coordinator.py:3424`) found by running, not by grep.

**Cannot read**: the plan-state half of a cell (which state the check drove) and whether the expected value came from the plan or from a document. Both stay the D16 seat's claim and its reviewer's; the read says so on its `RESULT` line.

**3.3 `generality`: levels are read off the configuration the run built; pairs are derived.** The same launcher also wraps `FakeEntry` (data and options) and `profiles.prices` and `profiles.weather` (the profile argument). The instrument holds one table, axis to observable: a configuration key for the option axes, key present or absent for the 48 binary entity axes, the profile argument for price shape and climate. An axis `--population` prints with no table entry prints `no witness` per level and is never counted, so a new axis shows as a gap and not as silence (self-test arm). A level row (cell, source, check) is witnessed when one recorded configuration of that script carried the level before the check and the check is ok. **A pair is examined when one recorded configuration carried both levels and a witnessed row cites a check after it**: seats type level rows only (at most F1's first number), and the read emits the pair rows in CENSUS's three-column format for `d12-cells --pairs --ledger` to print. Source `bundle`: the levels come from the bundle's `replay` entry data and options through the same table, written by the read as a levels extract (levels only, no entity id) that the row cites. Source `install-report`: counted only against a tracked report file; none exists at the base.

**Cannot read**: that the check's assertion depends on the level (a perturbation per level is F1's pair count in script runs); language, unit and Home Assistant version axes have no observable in the stub and stay `no witness` until one is named.

**3.4 `regret`: the grid is a closed loop on a plant; an install-day is a record.**

*Grid* (universe `d0-grid`, default `--plane price-weather`): per cell three loops of `tests/rolling.py` `run_rolling`'s shape, same prices and weather known at each re-plan.
- `C_real`: the loop as the integration runs it (its model, `plant_error`, learning on), costed on the plant.
- `C_model`: the cost each executed step's own plan booked for it.
- `C_same`: the least cost on the plant found among feasible plans built from the same information: the optimizer handed the plant's parameters and the realised draw, the two challengers `tests/optimality.py` already races (same-energy shift to the cheapest slots, seeded perturbation), and the executed plan itself. The row names which won.
- `C_fore`: the same candidates given the realised series for the whole window.
- Printed per cell: the four costs, regret, the floor, the model gap, and against `thresholds.band_model_gap` the word `undecided` while its value is null; then the mean and two standard errors.

Every candidate is a feasible plan, so the `C_same` found is at or above the true least cost: **the printed regret is a lower bound**, and the read says so. The executed plan is a candidate, so regret is never negative.

*Install-day* (universe `d15-installs`, examined only for a bundle passed with `--bundle`): per day `C_real` from the energy store's `total_cost` (cross-checked against metered power times the price rows), `C_model` from that day's snapshot `predicted_cost`, and the gap. **`C_same` is NO-READ per install-day and the read prints why**: `replay_doc.py` `ATTRIBUTE_KEYS` keeps no forecast, so the forecast as issued, an exogenous input of the definition, is in no bundle; and no code identifies the measured house from a window. Regret per install-day therefore stays NO-READ; this group lands the realised-cost record and the model gap, which the brief names, and reports the rest (decisions, below).

**Cannot read on the grid**: the gap between plan and execution (the loop calls the optimizer, not the coordinator cycle; that gap is `operation`'s), and plants the loop cannot build, which print `not run`.

**3.5 `escapes` and `unowned`: the interface needed from ROUND-METRICS.** One command that exits 0 and prints one line per escape in the window (id, released version, found-by, owning dimension or `none`, and whether it is an objective bug or an owner report), then a count line with escapes, unowned and the window; with its input absent it prints unread and never a zero (already its brief's null control). Part 1 at ebd654c3ba holds no such record (its diff adds two other instruments). Gap against its carries 5, 6 and 8: `unowned` counts owner reports that are no objective bug, and none of the three names them.

**3.6 The record, at merge.** In `dev/governance/decisions/0018-objective-function.md` the rows and bullets naming the holding group for `regret`, `operation`, `generality`'s examined count, D0 and D12 name this group; `escapes` and `unowned` name R11-PRE-ROUND-METRICS. `dev/audit/config/objective.json` is not edited: `terms` is a list of names and its only `builder` keys are the two NO-READ axes', which are not these reads.

## 4. Alternatives, and why each lost

- **Count the join's rows as typed.** No new script; a row naming a check that does not exist counts, and pairs need F1's second number of typed rows.
- **A recorder inside `tests/harness.py` behind an environment variable.** Every script importing it enters the diff's closure (a full gate), and a branch is added to the path every check runs through; the launcher installs the same two wrappers with no edit.
- **Source mutants through `tests/mutation_table.py` as the witness.** Its ledger keys a site to a script, never a check, so a cell could not name its asserting check; and a source patch needs a worktree per site where the frame wrapper needs none.
- **An axis-to-key field in `objective.json` `population`.** One description per axis, but `check_scopes.py`'s reader and its population arms would carry a field they do not read, in a file two in-flight groups edit and only the owner changes.
- **An exact minimiser (dynamic programme) for `C_same`.** Independent of the solver, but the plant's state (room, slab, floors, tank, buffer) is too wide to grid; the candidate set is independent of the learned model, which is what the definition requires, and names its bound.
- **One script for all three.** The regret loop imports the product package and numpy; the ledger reads would inherit both to count rows.

## 5. Sibling sites

`git grep -n "R11-INTAKE-R10-RESIDUE" -- dev/governance/decisions/0018-objective-function.md dev/audit/config/objective.json dev/audit/README.md` at the fixer's base. Each hit is one of: a read of 3.6 (edited); the D1, D2, D8, D11, D15 census rows, `coverage` and the two axis builders (other groups' builds, not edited; decision: orchestrator, who renames them); or prose in `dev/audit/README.md` that repeats a row (edited with its row). A hit in none of the three is reported, not edited.

## 6. Evidence, by file

| read | planted control it must catch | null control it must pass |
|---|---|---|
| operation | in the self-test's fake tree: a row citing a check with a constant condition, and a row citing a site the script never reaches; neither is counted | a row citing a check that compares the recorded payload: counted as moved; the same run with no site perturbed turns no check |
| generality | a row whose level no recorded configuration carried; a pair whose two levels sit in two different configurations; neither counted | a level row and the pair from one configuration: both counted; an axis with no table entry prints `no witness` |
| regret, grid | a plant whose heat loss differs from the model's, on a non-flat price: regret above its two standard errors | flat price: regret 0; plant equal to the model with learning off: regret 0 |
| regret, install-day | a synthetic bundle (`tools/replay/dbg_bundle_gen.py`) with metered power scaled: `C_real` and the gap move | the unscaled bundle: the gap unchanged; `C_same` prints NO-READ, never a number |
| each read | an emptied universe source: exit 2 and no `RESULT` line | the head: exit 0, universe and examined printed |

Live acceptance at the head: operation and generality each run on a seed ledger the pull request lands with the first witnessed rows (operation: the four checks of F5 at their site); the regret grid on F4's plane. Failing test first: each self-test arm is written against the read's stub and seen red. Mutation proof targets: the moved comparison, the same-configuration test for a pair, the least-of-candidates line, the exit-2 guards. No golden moves; no claim file is touched; `tests/closures.json` is re-recorded on Linux only.

## 7. Cost, hot files, serial position

Size L, two parts, each its own pull request: **p1** product_reads.py with both ledger reads, its guide, and 3.6's edit; **p2** regret_oracle.py and its guide. Neither adds what a pinned grader in a restoring job must register beyond the self-test step; if `selftest_scope.py` refuses the new step for a reason only a grader change cures, stop and report it as the split.

Standing cost: nothing per gate run except two self-tests. Per round: one script run per cited script plus one per cited site (F5's script: about ten seconds a run), and the regret plane's loops, unmeasured in the time box (Notes, n2).

Hot files: `tools/ci/selftest_closures.json`, `.github/workflows/governance.yml`, `tools/audit/seat/INSTRUMENTS.md`, `dev/governance/config/policy_budgets.json` (each guide is policy), `tests/closures.json`, and the decision record (policy: the owner's approval, or the mandate's declared review). Serial position: after CENSUS merges, since the enumerator is on no main; beside the finders. The roster has no such edge. decision: orchestrator, an `after` edge on R11-PRE-BRIEFS-CENSUS; and whether this instrument group is built under R11-PRE-MACHINERY-LIMITER's one-in-one-out.

Decisions routed: decision: owner, whether a bundle should record the forecast as issued (a product change no finding names; without it regret per install-day cannot be read to the definition). decision: orchestrator, which group builds the measured-house identification for install-days; it is not designed here.

## Notes for the fixer

- `FakeServices.async_call` is a coroutine function: install the wrapper as a plain function that reads the frame and returns the coroutine, or the frame is the event loop's. Carry: R11-PRE-PRODUCT-READS (item n1)
- Time `tests/features.py` under the launcher before choosing defaults; it holds most write assertions and its run time was not measured. If one run per site is too slow, perturb every cited site of a script in one run only where their checks are disjoint, and say so in the body. Carry: R11-PRE-PRODUCT-READS (item n2)
- A script may hand the coordinator a configuration the launcher never sees (the scripts that construct it directly are what `git grep -l "HeatPumpOptimizerCoordinator(" -- tests` lists); a configuration not recorded witnesses nothing. Print the count of checks with no recorded configuration. Carry: R11-PRE-PRODUCT-READS (item n3)
- `run_rolling`'s plant differs from the model by a heat-loss scale only, and its forecast may be the realised series; if so the grid's floor prints 0 and the row says why. Carry: R11-PRE-PRODUCT-READS (item n4)
- The seed ledgers are evidence of a round: land them where `dev/audit/README.md` puts a round's evidence, not under `dev/audit/config/`. Carry: R11-PRE-PRODUCT-READS (item n5)
- The interface of 3.5 and its owner-report gap. Carry: R11-PRE-ROUND-METRICS (item n6)
- The unlisted writer of 3.2 confirms the sibling design's F3 by a run. Carry: R11-PRE-NEW-DIMENSIONS (item n7)
- D0 step 8 and D15 step 9 at 2afcb72317 ask a seat for `C_same` per install-day, which 3.4 shows no bundle can give. Carry: R11-PRE-BRIEFS-CENSUS (item n8)

## Appendix: the spike (scratch; never merges)

```
# PYTHONPATH=tests/hastub:tests:custom_components python3 witness.py tests/guard_pins.py [<file>:<line>]
import collections, os, runpy, sys, harness
script, site = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else None)
sites, checks = collections.Counter(), {}
real_call, real_check = harness.FakeServices.async_call, harness.Results.check
def call(self, domain, service, data=None, **kw):
    f = sys._getframe(1); key = f"{os.path.relpath(f.f_code.co_filename)}:{f.f_lineno}"; sites[key] += 1
    if site and key.endswith(site) and isinstance(data, dict):
        data = {k: (v + 7.0 if isinstance(v, (int, float)) and not isinstance(v, bool) else v) for k, v in data.items()}
    return real_call(self, domain, service, data, **kw)
def check(self, name, condition, detail=""):
    checks[name] = bool(condition); return real_check(self, name, condition, detail)
harness.FakeServices.async_call, harness.Results.check = call, check
sys.argv = [script]
try: runpy.run_path(script, run_name="__main__")
except SystemExit: pass
print(sorted(sites.items()), len(checks), sorted(n for n, ok in checks.items() if not ok), file=sys.stderr)
```
