# R11-PRE-PRODUCT-READS: three product reads that count a cell only on a witness the read itself produced

Designer round 2, on top of f5147c0e5982f4e995a8645dd8e54a27dfce2b12, answering `Design review: revise ... harness` at bdc4d6e1da3670019bc601f1cb783405c1fedaa2: point 1 in 3.2, point 2 in 3.3, both planted controls in section 6; notes r1 to r3 folded into 3.2, the header and section 5, r4 carried in the notes. Base: origin/main e0ad8b2bd32b60a67975039f8573dbba2207757f; `git diff --stat b3831ff64e e0ad8b2bd3` over every module the note names (the verdict's list plus `tests/profiles.py` and `off_restore.py`) prints nothing. No `after` group, so no predecessor handoff head; heads relied on, none merged: R11-PRE-BRIEFS-CENSUS `handoff/r11-pre-briefs-census` db626fb9dde5ca152ce45e7c216e3c7676553b4e (enumerator unchanged from 2afcb72317; F2 to F4 re-run there), R11-PRE-NEW-DIMENSIONS design a9377bcf47957e63060733e61a9cb551a8734b1c approved by daa950c68c, R11-PRE-ROUND-METRICS part 1 `handoff/r11-pre-round-metrics-p1` 686f63afa1e74e5cfca97cfb0d7b1442fc1948a9. No finder harness: owner report (card E11-N-INTAKE-BUILDER); the planted cells of section 6 are the fixture. Seat tokens: the harness reports none.

## Figures

Literals are snapshots; re-measure at your merge base.

| id | figure | literal | enumerator |
|---|---|---|---|
| F1 | population levels; pairs; NO-READ axes | 195; 18696; 2 | `python3 tools/audit/check_scopes.py --repo . --population`, last three lines |
| F2 | generality cells with the card and blueprints; with pairs | 201; 18897 | in a checkout of the CENSUS head: `python3 -I tools/audit/enumerate.py d12-cells` piped to `wc -l`; the same with `--pairs` |
| F3 | actuator sites; cells; distinct state strings per cell (duty x condition there) | 38; 456; 12 | there: `enumerate.py d16-writes`; with `--cells`; with `--cells`, fields 2 and 3 split on ` \| `, `sort -u` |
| F4 | regret grid cells; price by weather plane; install-days listed | 2400; 40; 1 | there: `enumerate.py d0-grid`; with `--plane price-weather`; `enumerate.py d15-installs` |
| F5 | spike on `tests/guard_pins.py` (round 1, base b3831ff64e): checks; write sites reached; checks turned FAIL by perturbing the payload from `pump_arbiter.py:1610`; by a site never reached | 88; 2; 4; 0 | the round-1 appendix's script at f5147c0e59, with no site, then each site |
| F6 | hits for an oracle or regret harness | 0 | `git grep -n -w -E "same.information\|C_same\|C_fore\|C_model" -- tools tests dev/audit/harnesses` piped to `wc -l` |
| F7 | modules binding `log_held` by name | 5 | `git grep -l "from .log_latch import.*log_held" -- custom_components` piped to `wc -l` |

## 1. What other groups already land, and what is left

- **CENSUS lands every universe and the join**: `d12-cells [--pairs]`, `d16-writes --cells`, `d0-grid`, `d15-installs`, and `--ledger TSV`, which prints each item beside a seat's row or `not run`, plus the brief steps (D0 step 8, D15 step 9, D12 step 1's ledger). This group imports the universe from that script and enumerates nothing a second time.
- **What the join cannot show**: `joined` accepts any non-empty string as the test, so not that the check exists, ran, asserted, or depended on the cell; it prints no examined count. That is this group's: **the producer of witnessed rows and the count**.
- **NEW-DIMENSIONS** owns the cell formula (approved: sites x 14 named states, each a (duty, level, overlay, lifecycle)) and the D16 plan-side oracle. This group reads the state tokens as `--cells` prints them at the fixer's base and hardcodes neither the census formula (F3, duty x condition) nor the approved one (verdict note r2).
- **ROUND-METRICS** builds the escapes record (Carry 0); 3.5 states the interface; nothing is built here.
- **No oracle exists** (F6): the harness behind `regret` is this group's.

## 2. Owning seams (governance instruments; `tests/seam_map.json` maps coordinator methods only and none changes)

| concern | owner | callers only |
|---|---|---|
| a universe and its join to a ledger | `tools/audit/enumerate.py` (CENSUS) | the briefs, this group's reads |
| whether a ledger row is witnessed, and the examined count of `operation` and `generality` | a new script product_reads.py under `tools/audit/` | the objective record, D12 and D16 seats |
| `C_real`, `C_same`, `C_fore`, `C_model` per cell and install-day | a new script regret_oracle.py under `tools/audit/` | D0 step 8, D15 step 9, the objective record |
| the escapes record and `unowned` | ROUND-METRICS' instrument | the objective record |

Two scripts because the concerns share no code: the first runs test scripts under a recorder, the second runs the optimizer against a plant. No production file and no file under `tests/` is edited.

## 3. The shape

**3.1 One contract for all three reads.** Each subcommand prints its rows, then one line `RESULT read=<term> universe=N examined=n` and the term's value, and exits 0; an empty or unreadable universe exits 2 and prints no count. `examined` counts only rows this run witnessed; every other row prints with its reason and is not counted. Zero examined is a valid first read (the baseline, decision 0018 section 2).

**3.2 `operation`: a cell is witnessed only when the read moved the site and recorded the cell's state from the plan.** (verdict point 1, option (a))

*The launcher.* The read runs each cited test script unedited through `runpy` with these wrappers installed first, none touching a file:
- `tests/harness.py` `FakeServices.async_call` records the calling frame's file:line, the key `d16-writes` prints (installed as a plain function returning the coroutine; carry n1); `Results.check` records name, outcome and detail.
- `log_held` is patched **in each importing module's namespace** (F7: `pump_arbiter`, `off_restore`, `coordinator`, `inputs`, `heat_curve`), never only in `log_latch` (verdict r1); it records the caller's file:line.
- `pump_arbiter.apply` (module attribute; every pass enters there, coordinator and tests alike) records the pass's inputs: the `coord` argument and `now` as `apply` resolves it (the argument, else the stub's `dt_util.now()`), and at entry the plan the coordinator holds, `coord.arbiter_inputs().plan`, the published field built from the coordinator's own result. A write or hold is attributed to the innermost open pass; one outside every pass has no plan.
- `FakeEntry` (data and options) and the coordinator's constructor, recording each configuration and how many coordinators were built on one entry (shared with 3.3).

*The state at a write, from the plan's arrays by plain indexing.* k is the largest i with `timestamps[i] <= now` and `now` before the next stamp (the last step's length is the previous step's spacing; a one-step plan has no length and records no k). No call into `pump_arbiter` (`_step_index`, `step_duty`, `_step_kw`, `planned_draw_runs`) and no bisect of the package's, as NEW-DIMENSIONS 3.1 requires of its oracle. One table maps each state token `--cells` can print to its observable; every comparison is equality or zero against the plan's own values, so no threshold enters:

| token | observable (all inputs the test set, or the plan) |
|---|---|
| `duty=<m>`, `observe`, `off` | the recorded configuration's duty-mode option |
| `idle`, `dhw-only`, `both`, `partial`, `full`, `min-cold-tank` | s = `power_schedule[k]`, d = `dhw_power_schedule[k]` (0 past its end), f = `duty_floor_kw`, P = the configuration's `heat_pump_max_power`: idle s=d=0; dhw-only s=0<d; both s>0<d; full d=0, s=P; min-cold-tank d=0, s=f; partial d=0, 0<s<P, s!=f |
| `baseline` | a plan held and no k |
| `running` (census formula) | a pass with a plan, the entity available, the coordinator the first on its entry |
| `restart` | the coordinator is not the first built on its entry |
| `unavailable` | the fake state of the written entity reads `unavailable` at the call |
| `boost-partial`, `disinfection`, `upgrade` | none at this base: printed `state not recorded` |

A token with no table entry prints `state not recorded`, so a state NEW-DIMENSIONS adds shows as a gap, not as silence (self-test arm). The overlay and upgrade rows stay unread until the fixer names an input-side observable (the service call or option the test sets to start a boost or a disinfection; the store fixture's tag) and plants its control; it never reads the package's own `boost` or legionella state, which is the code under test (carry n9).

*The witness.* Per cited site the script runs again with the payload from that site perturbed (numbers offset, strings replaced). A row (cell, `script::check`) is:
- **moved**: the check is ok unperturbed and FAIL, or its detail changes, with the site perturbed, **and** a write from that site preceded the check in a pass whose recorded state equals every state token of the cell. Counted.
- **reached** (hold sites, where a wrapper cannot alter the refusal): `log_held` was called from that line before the check, the check is ok, and the hold's recorded state equals the cell's. Counted, its own number beside moved.
- **not witnessed**: unknown check; FAIL at the head; site never reached; the check does not move; **the state recorded at the site differs from the cell's** (printed with the recorded state); or `state not recorded`. Never counted.

So one idle-plan check cited on every plan-state row of its site counts once, on the idle row, which closes decision 0018 line 431's first gaming case.

*The target half, read.* For each moved write the read compares the payload with the recorded plan at k: an indoor set-point against `optimal_setpoints[k]`, printed `target=plan` or `target=differs plan=<x> sent=<y>`; a slot with no number in the plan (water set-point, mode, tank) prints `target=no plan value` (NEW-DIMENSIONS grades those by invariants, the D16 seat's step M2). `differs` is a lead for the D16 seat, not a refusal of the row: the count measures examination; the term's numerator is the D16 ledger's verdict per examined cell. No document is read anywhere, so 0018 line 431's second case (edit the document) moves nothing.

By-product: a write whose calling line is no listed site prints `unlisted writer` (carry n7).

**3.3 `generality`: a level is witnessed only when switching it moves the check.** (verdict point 2)

The same launcher records each configuration (`FakeEntry` construction ordinal, data, options) and the profile argument of `tests/profiles.py` `prices` and `weather`. One table maps axis to observable: a configuration key for option axes, key present or absent for binary entity axes, the profile argument for price shape and climate. An axis `--population` prints with no entry prints `no witness` per level, never counted (self-test arm).

A level row (cell, source, `script::check`) is:
- **reached**: the configuration of ordinal n carried the level before the check, and the check is ok.
- **witnessed**: reached, and in the read's own run of the same script by the same launcher, with **only that level's observable in configuration n switched to the next level of the same axis** in `--population`'s order (key removed or added with an unheld entity id; option value replaced; profile argument replaced), the check turns FAIL or its recorded detail changes. Counted.

A pair is counted only when **both** level rows are witnessed in the same configuration ordinal of one script, each by its own switch run; seats type level rows only, and the read emits the pair rows in CENSUS's three-column format for `d12-cells --pairs --ledger`. `check("x", True)` after a configuration is reached and never witnessed, and no pair is counted through it: 0018 line 432's third case. Cost: one switch run per cited level row, at most F1's first number per script, never its second. The read prints witnessed and reached separately and counts only witnessed; if switch runs prove too slow at the fixer's measurement, the default narrows which rows are run, never what counts.

Determinism: before switching, the script runs twice unperturbed; a check whose outcome or detail differs between those two runs is printed `nondeterministic` and cannot be witnessed (else a timestamp in a detail would count as moved).

Source `bundle`: levels from the bundle's `replay` entry data and options through the same table, written as a levels extract (levels only, no entity id); a bundle row is **reached only**, never witnessed (a bundle cannot be re-run with a level switched), so it prints and does not count, and the read says so. Source `install-report`: likewise reached only; none tracked at the base.

**Cannot read**: language, unit and Home Assistant version axes have no observable in the stub and stay `no witness`.

**3.4 `regret`: unchanged from round 1** (held by the review). *Grid* (`d0-grid`, default `--plane price-weather`): per cell, loops of `tests/rolling.py` `run_rolling`'s shape: `C_real` (the integration's loop, costed on the plant), `C_model` (each executed step's booked cost), `C_same` (the least plant cost among feasible plans from the same information: the optimizer given the plant's parameters and the realised draw, the two challengers `tests/optimality.py` races, and the executed plan; the row names the winner), `C_fore` (the same candidates, realised series). Printed per cell: four costs, regret, floor, model gap, `undecided` against `thresholds.band_model_gap` while it is null; then mean and two standard errors. Every candidate is feasible, so **the printed regret is a lower bound**, never negative. *Install-day* (`d15-installs`, with `--bundle`): `C_real` from the energy store's `total_cost` cross-checked against metered power times prices, `C_model` from that day's `predicted_cost`, the gap; `C_same` per install-day prints NO-READ with why: `replay_doc.py` `ATTRIBUTE_KEYS` keeps no forecast as issued, and no code identifies the measured house from a window.

**3.5 `escapes` and `unowned`: the interface needed from ROUND-METRICS.** One command that exits 0 and prints one line per escape in the window (id, released version, found-by, owning dimension or `none`, objective bug or owner report), then a count line with escapes, unowned and the window; input absent prints unread, never a zero. Part 1 at 686f63afa1 holds no such record. Gap against its carries 5, 6 and 8: `unowned` also counts owner reports that are no objective bug, and none of the three names them (n6).

**3.6 The record, at merge.** In `dev/governance/decisions/0018-objective-function.md` the rows and bullets naming the holding group for `regret`, `operation`, `generality`'s examined count, D0 and D12 name this group; `escapes` and `unowned` name R11-PRE-ROUND-METRICS. `dev/audit/config/objective.json` is not edited: its only `builder` keys are the two NO-READ axes', not these reads.

## 4. Alternatives, and why each lost

- **Option (b) for `operation`** (count moved per site, every cell's state unrecorded): closes the gaming case but leaves the target half unread and every state cell at zero forever; (a) reads both from the same recorded plan for one wrapper on `apply`.
- **The state from the arbiter's frame locals (`inp.plan`, `now` inside `_write`)**: no `apply` wrapper, but it reads the code under test's choice of plan; a stale-plan defect would record the stale plan and agree with itself.
- **Count the join's rows as typed.** No new script; a row naming a check that does not exist counts, and pairs need F1's second number of typed rows.
- **A recorder inside `tests/harness.py` behind an environment variable.** Every importing script enters the diff's closure (a full gate) and every check pays a branch; the launcher installs the same wrappers with no edit.
- **Source mutants through `tests/mutation_table.py` as the witness.** Its ledger keys a site to a script, never a check, and needs a worktree per site.
- **A per-pair switch for `generality`.** F1's second number in runs; the per-level switch plus same-ordinal witness of both rows bounds a pair by two runs already made.
- **An exact minimiser (dynamic programme) for `C_same`.** The plant's state (room, slab, floors, tank, buffer) is too wide to grid; the candidate set names its bound.
- **One script for all three.** The regret loop imports the package and numpy; the ledger reads would inherit both.

## 5. Sibling sites

`git grep -n "R11-INTAKE-R10-RESIDUE" -- dev/governance/decisions/0018-objective-function.md dev/audit/config/objective.json dev/audit/README.md dev/audit/yardstick/round10/OBJECTIVE.json` at the fixer's base. Each hit is one of: a read of 3.6 (edited); the D1, D2, D8, D11, D15 rows, `coverage` and the two axis builders (other groups' builds, not edited; decision: orchestrator); prose in `dev/audit/README.md` repeating a row (edited with it); or `dev/audit/yardstick/round10/OBJECTIVE.json`, round 10's record (reported in the body, never edited; verdict r3). A hit in none of these is reported, not edited.

## 6. Evidence, by file

| read | planted control it must catch (not counted) | null control it must pass |
|---|---|---|
| operation | (i) a row citing a constant-condition check; (ii) a row citing a site never reached; (iii) **a row citing a check that drives only the idle plan, cited for the `both` (census head: `restart`) cell of the same site**: printed `state differs`; (iv) a cell token with no table entry: `state not recorded` | a check comparing the payload, cited for its idle cell: moved and counted, `target=plan` when the fake writes `optimal_setpoints[k]`; the same run with no site perturbed turns no check; a hold row with the patched `log_held` binding in `pump_arbiter`: reached (proves the per-module patch fires; with only `log_latch` patched it is not reached) |
| generality | (i) **a constant-condition check citing a level after a configuration that carries it: reached, not witnessed, and no pair through it**; (ii) a level no recorded configuration carried; (iii) a pair whose two levels sit in different ordinals; (iv) a check whose detail embeds a counter: `nondeterministic` | a check asserting on a key's presence, cited for that level: switched run FAIL, witnessed; two such levels in one ordinal: the pair counted; an axis with no table entry prints `no witness` |
| regret, grid | a plant whose heat loss differs from the model's, on a non-flat price: regret above two standard errors | flat price: regret 0; plant equal to the model, learning off: regret 0 |
| regret, install-day | a synthetic bundle (`tools/replay/dbg_bundle_gen.py`) with metered power scaled: `C_real` and the gap move | the unscaled bundle: gap unchanged; `C_same` prints NO-READ, never a number |
| each read | an emptied universe source: exit 2, no `RESULT` line | the head: exit 0, universe and examined printed |

Fixtures for operation and generality live in the self-test's fake tree (a fake script, a fake coordinator holding a hand-built result with `timestamps`, `power_schedule`, `dhw_power_schedule`, `optimal_setpoints`, `duty_floor_kw`). Live acceptance at the head: both ledger reads on a seed ledger the pull request lands (operation: F5's four checks at their site, with the cell state each actually drives); the regret grid on F4's plane. Failing test first: each self-test arm written against the read's stub and seen red. Mutation proof targets: the state-equality line, the moved comparison, the switch-run comparison, the same-ordinal test for a pair, the nondeterminism guard, the least-of-candidates line, the exit-2 guards. No golden moves; no claim file is touched; `tests/closures.json` is re-recorded on Linux only.

## 7. Cost, hot files, serial position

Size L, two parts, each its own pull request: **p1** product_reads.py with both ledger reads, its guide, and 3.6's edit; **p2** regret_oracle.py and its guide. If `selftest_scope.py` refuses a new self-test step for a reason only a grader change cures, stop and report it as the split.

Standing cost: two self-tests per gate run. Per round: per cited script two unperturbed runs, one per cited site and one per cited level row (F5's script: about ten seconds a run); the regret plane's loops unmeasured (n2).

Hot files: `tools/ci/selftest_closures.json`, `.github/workflows/governance.yml`, `tools/audit/seat/INSTRUMENTS.md`, `dev/governance/config/policy_budgets.json`, `tests/closures.json`, and the decision record (policy: the owner's approval, or the mandate's declared review). Serial position: after CENSUS merges (the enumerator is on no main), and p1 reads NEW-DIMENSIONS' state tuple if it has merged by then, else the census formula; beside the finders. Routed, unchanged: decision: orchestrator, an `after` edge on R11-PRE-BRIEFS-CENSUS and whether R11-PRE-MACHINERY-LIMITER's one-in-one-out applies; decision: owner, whether a bundle records the forecast as issued; decision: orchestrator, which group builds measured-house identification for install-days.

## Notes for the fixer

- `FakeServices.async_call` is a coroutine function: install the wrapper as a plain function that reads the frame and returns the coroutine, or the frame is the event loop's. Carry: R11-PRE-PRODUCT-READS (item n1)
- Time `tests/features.py` under the launcher before choosing defaults; it holds most write assertions. If one run per site is too slow, perturb several cited sites of a script in one run only where their checks are disjoint, and say so in the body. Carry: R11-PRE-PRODUCT-READS (item n2)
- A script may hand the coordinator a configuration the launcher never sees (`git grep -l "HeatPumpOptimizerCoordinator(" -- tests`); a configuration not recorded witnesses nothing. Print the count of checks with no recorded configuration, and of writes outside any recorded pass. Carry: R11-PRE-PRODUCT-READS (item n3)
- `run_rolling`'s plant differs from the model by a heat-loss scale only, and its forecast may be the realised series; if so the grid's floor prints 0 and the row says why. Carry: R11-PRE-PRODUCT-READS (item n4)
- The seed ledgers are evidence of a round: land them where `dev/audit/README.md` puts a round's evidence, not under `dev/audit/config/`. Carry: R11-PRE-PRODUCT-READS (item n5)
- The interface of 3.5 and its owner-report gap. Carry: R11-PRE-ROUND-METRICS (item n6)
- The unlisted writer of 3.2 confirms the sibling design's F3 by a run. Carry: R11-PRE-NEW-DIMENSIONS (item n7)
- D0 step 8 and D15 step 9 at the CENSUS head ask a seat for `C_same` per install-day, which 3.4 shows no bundle can give. Carry: R11-PRE-BRIEFS-CENSUS (item n8)
- `boost-partial`, `disinfection` and `upgrade` have no input-side observable in 3.2's table; name one per state with a planted control, or leave the token `state not recorded`. Never read `boost.held_for`, `arbiter_inputs().disinfecting` or the legionella memo. Carry: R11-PRE-PRODUCT-READS (item n9)
- Re-read the state tokens `d16-writes --cells` prints at the fixer's base (approved formula at a9377bcf47: sites times 14 states); every token printed must be a table row or print `state not recorded`. Carry: R11-PRE-PRODUCT-READS (item n10)
- `dev/audit/rounds/round10/objective/escapes_hand.tsv` is a hand-read escapes ledger with owner and ruling columns: the round-metrics instrument should read rows of that shape (verdict r4). Carry: R11-PRE-ROUND-METRICS (item n11)
