R11-PRE-PRODUCT-READS part 2 of 2 (design `design/R11-PRE-PRODUCT-READS` at 8daf118368, `Design review: approve` at a08d8f47c9; Carry 1, items 6ceaaf5d): `tools/audit/regret_oracle.py`, which reads decision 0018's `regret` per cell of `enumerate.py d0-grid` (`grid`) and the cost record per line of `enumerate.py d15-installs` from a bundle (`installs --bundle LABEL=PATH`), and its guide. Universes are imported from `tools/audit/enumerate.py`, never enumerated again. No production file and no test script is edited; `tests/layout.json` lists the new tool.

How the read is built (design 3.4):
- `grid`: per cell, the integration's loop on the configured model, re-planned every 2 h and applied step by step to a plant whose heat loss is `--plant-error` times the model's. `C_real` is the commanded energy times the price; `C_model` the executed steps' booked cost off the plans that executed them; `C_same` the least cost among the executed plan, the same loop given the plant's parameters, and `tests/optimality.py`'s two challengers on the executed space series (greedy same-energy, energy-preserving perturbations), the row naming the winner. Regret `C_real - C_same` is a lower bound and never negative, the executed plan being a candidate. The loop's forecast is the realised series, so `C_fore = C_same` and the floor prints 0 with that reason (n4). A plant level the loop does not model (`valve-storage`, `wood`, the two plants round 10's escapes name) prints NO-READ and is not examined.
- The loop is `run_rolling`'s, proved rather than asserted: the self-test runs `tests/rolling.py`'s own `run_rolling`, extracted by AST without the module's checks, beside the oracle's loop and requires the identical executed series and cost.
- `installs`: `C_real` is the bundle's energy store `total_cost` (NO-READ when the store counts from before the window), beside the metered power times the price over the window; `C_model` is the accuracy store's day-ahead promise cost summed over the window's local dates; the gap beside both. `C_same` per install-day prints NO-READ with the reason derived at run time from `replay_doc.py`'s `ATTRIBUTE_KEYS` (Carry 2, items d65f4c4c).
- Each model gap is `undecided` while `thresholds.band_model_gap` is null.

Departures, raised here:
1. **Admission.** The design says "every candidate is feasible" without naming against what. A candidate is admitted when it is inside 0..`max_electrical_power` and no further outside the bounds on the plant (comfort floor and ceiling, the hot-water minimum in its windows, the tank rating) than the executed plan, `optimality.py`'s own `v <= v0` rule; an open-loop challenger must also end the window with no less heat stored (room, slab, zones, tank). Without that last check the window's end is free to borrow from: the self-test arm `admits: greedy holds the bounds but ends colder` shows greedy at zero bound violation refused only for it. A comfort-matched rule (degree-hours below target no worse than the executed plan's) was tried and lost: under it a model overstating loss buys comfort the oracle cannot count, and the planted control reads 0.
2. **The plant equal to the model reads 0 where no challenger wins, not everywhere.** On `summer_typical/winter_mild` the greedy challenger beats the executed plan at plant error 1.0: the solver's share of regret, which decision 0018 counts, not model error. The null arms read the model-error share on every self-test cell (no winner is the plant-model candidate) and regret 0 on the three where no challenger wins; the live plane's readings are in Figures.
3. **The plane's levels.** `--plane price-weather` (the default) runs its cells at `PLANE_LEVELS` (single-zone, dhw, plain, 24 h: `run_rolling`'s defaults); `--plane all` names every level.
4. **CI.** governance.yml's `instrument-self-tests` runs the runner's bare python3, with no numpy or solver stack. The oracle's step there takes an interpreter of its own (`actions/setup-python` with `update-environment: false`, so every other step keeps the job's python3), installs `tests/requirements-ci.txt` from its hashes, and is gated by its measured read set like every step in the job (`tools/ci/selftest_closures.json`, recorded on Linux). It was first wired into `tests.yml`'s graded `arch-instrument` job: there `codeowners_gap.py --check` read the oracle and the eight files it loads (`tests/rolling.py`, `replay_doc.py`, `tools/replay/*` among them) as unowned enforcement surface, and `field_coverage.mjs` lost its pinned `tests/structure.py`. `instrument-self-tests` grades nothing (`HPO_JOB_GRADES: nothing`), so neither applies there.
5. **Install-day `C_model`.** The payload's `predicted_cost` is a horizon total, not a day; the day's booked cost is the accuracy store's promise for that local date, which this reads.

The group's roster carries: Carry 1 (part 2) and Carry 2 (`C_same` per install-day NO-READ, and the brief wording) are built here. Carry 3 (n11, the row shape of `dev/audit/rounds/round10/objective/escapes_hand.tsv`) is not: Carry 0's seam ruling gives the escapes record to R11-PRE-ROUND-METRICS, and part 1 left the note on this group's roster carries for the relay to fold.

Policy text: D0 step 8 and D15 step 9 now name the instrument and record `C_same` per install-day as NO-READ, drafted under mandate 6893738184 (scope all) per Carry 2; decision 0018's D0 row, `regret` row and its gaming row name the instrument where they said NO-READ or none. Each is code-owned: the owner's approving review merges it.

## Head

f4029c34e4f2651969cca4ffb8a5e70fd4aa17b3. Merge base 2d7161a4b70923da910f9997e18db632c0d4ec2d; origin/main 4ecca4cc580b1065e366bf12bd5a917d40d03c0e at 2026-11-17T04:14:44Z, `git merge-tree --write-tree origin/main HEAD` exits 0 (no conflict). `tools/audit/regret_oracle.py` is unchanged since 056b367e2a, where the mutation spec, the self-test and the live reads below were taken; the commits after it move the CI step and record its read set.

## Mutation proof

Rule: the design's named targets (section 6: the least-of-candidates line, each half of the admission rule, the plant-model candidate, the regret sign, the exit-2 guard, `C_same` per install-day never a number, the store's window guard, the greedy challenger's order) and the two installs lines run 2 left alive, as a spec run unchanged at 056b367e2a: `python3 tools/audit/seat/mutant_run.py --spec <spec> --cmd 'python3 -I tools/audit/regret_oracle.py --self-test'`, rc=0. `NULL` is the driver's built-in no-op and `null-noop` a comment-only edit; both SURVIVED as they must.

~~~text
SURVIVED NULL
KILLED least-of-candidates-inverted
KILLED admits-bounds-dropped
KILLED admits-terminal-dropped
KILLED admits-limits-dropped
KILLED plant-model-never-raced
KILLED plant-model-skipped-always
KILLED regret-sign
KILLED universe-refusal-swallowed
KILLED c-same-install-a-number
KILLED store-window-guard-off
KILLED greedy-not-cheapest
KILLED unread-404
KILLED mean-417
SURVIVED null-noop
~~~

The tracked driver over every added line, `python3 tools/audit/seat/mutant_run.py --diff 2d7161a4b7...HEAD --path tools/audit/regret_oracle.py --cmd 'python3 -I tools/audit/regret_oracle.py --self-test' --report-only`, ran twice before this head, each survivor list driving new arms (the commits after 68f9458274 name them): run 1 (at 68f9458274, stopped by a container restart at line 261) and run 2 (at 78c5741297, every mutant on a production line; the remaining mutants sit in the self-test's own arms, where deleting an arm cannot fail the arms). Run 2's production survivors were then re-run as a spec at ac7f7812be: 20 KILLED, and 36 survive; two of those (the installs not-read row and MEAN line) are killed above, and every other one is under `## Unpinned sites`.

## Null control

- `python3 -I tools/audit/regret_oracle.py --self-test` prints `SELF-TEST passed (64 arms)` at the head (27 s wall).
- The plant equal to the model (`--plant-error 1.0`, the default) on the default plane: no row's winner is the plant-model candidate (it is the executed loop), and 37 of 40 cells read regret 0 (Figures).
- A flat price at the plant equal to the model reads regret 0 on all five flat cells (Figures); the self-test's `null: a flat price reads regret 0` arm on a 6 h flat cell.
- `installs` at the head with no bundle: every line `not read`, `examined=0`, exit 0, `value=NO-READ`.
- The parity null: the oracle's loop on another plant than `run_rolling`'s reads a different executed series (`parity null` arm), so the parity arms can fail.

## Figures

- Live, the default plane at the head: `python3 -I tools/audit/regret_oracle.py grid --jobs 4` -> exit 0, `RESULT read=regret universe=40 examined=40 value=0.0355`, `MEAN regret=0.0355 2se=0.0438 floor=0.0000 2se=0.0000 gap=0.0000 2se=0.0000` (77 s wall on 4 cores). Rows with regret above 0, each won by the greedy challenger (the solver's share): `summer_negative/winter_mild` 0.7585, `summer_typical/winter_cold` 0.3781, `summer_typical/winter_mild` 0.2825; the rule: rows whose sixth field is not `regret=0.0000`. Identical rows at 68f9458274.
- Planted, the same plane at `--plant-error 0.8` (the model overstating heat loss by a quarter): `RESULT read=regret universe=40 examined=40 value=1.4542`, `MEAN regret=1.4542 2se=0.7331` (128 s wall); the plant-model candidate wins 24 cells, 16 read 0. Flat cells there read the energy share as regret (`flat/winter_cold` 6.5502), which a flat price does not null: the flat-price null holds for timing, at the plant equal to the model.
- `python3 -I tools/audit/regret_oracle.py installs` -> exit 0, `RESULT read=regret-installs universe=1 examined=0 value=NO-READ` (the universe is `enumerate.py d15-installs`; round 10's bundle is not in the tree).
- Install-day on a generated bundle (the self-test's): `C_real` the store's `total_cost`, metered beside it; the x2-power bundle reads twice the metered cost and a different gap; the unscaled bundle reads the same gap twice.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`. `python3 -I tools/audit/archscore/score.py --diff 2d7161a4b70923da910f9997e18db632c0d4ec2d` -> `Architecture score: dS +0.0000` (no package file changes).
- `python3 -I tools/audit/seat/selftest_wiring.py --check` -> `147 self-testing, 147 wired, 0 unwired`; `python3 -I tools/ci/selftest_scope.py static` -> `123 gated step(s), 0 problem(s)` (122 at the merge base, plus `regret-oracle`); `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` -> `uncovered_files=0` (9 with the step in `arch-instrument`).
- `node tools/policy/policy_lint.mjs` -> `TOTAL: 0 error(s)`; `node tools/policy/brief_lint.mjs` exit 0; `python3 -I tools/audit/enumerate.py --briefs` exit 0.
- Scope: `tests/closure.py select` prints `MODE: FULL`; CI runs every script.

<!-- figure-block: scope-line mb=2d7161a4b70923da910f9997e18db632c0d4ec2d head=f4029c34e4f2651969cca4ffb8a5e70fd4aa17b3 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Unpinned sites

`prepr.sh`'s mutant step (its first 40 mutants of the added lines, `MUTANT_CMD` the self-test) leaves these ten; each is equivalent at the self-test's resolution or a tolerance with no observable step, and none is in `custom_components/`, so `mutation-autofix` pins nothing here. The full-diff survivors run 2 left are dispositioned by the same rule in the spec run above.
- `tools/audit/regret_oracle.py:43 CONST_SWAP`: equivalent: the order of the tool's own directory on `sys.path` changes no import it resolves.
- `tools/audit/regret_oracle.py:95 CONST_SWAP`: equivalent: `_paths`' insertion index, the same.
- `tools/audit/regret_oracle.py:50 CONST_SWAP`: equivalent on the grid: `START` copies `tests/rolling.py`'s; `profiles.py`'s prices and weather and the comfort bounds read the hour of day, not the year. A value check against rolling's literal would pin a copy; the parity arm pins the loop it feeds.
- `tools/audit/regret_oracle.py:51 CONST_SWAP`: equivalent: 301 against 300 perturbation draws changes no winner on the self-test cells; the arm `perturbed: cheaper, admitted, the same energy` pins the challenger's rule, not its draw count.
- `tools/audit/regret_oracle.py:52 CONST_SWAP`: equivalent: `EPS` at 1e-10 against 1e-9 separates no two candidate costs on the self-test cells (both are float-noise floors).
- `tools/audit/regret_oracle.py:53 CONST_SWAP`: equivalent: `VIOL_TOL` at 1e-7 against 1e-6 degree-hours; the arms' admitted and refused plans sit at 0 or above 1.
- `tools/audit/regret_oracle.py:133 CONST_SWAP`: equivalent: `span` is padding past the last horizon slice; one step more is never read.
- `tools/audit/regret_oracle.py:144 CONST_SWAP`: equivalent on one-day loops: the initial hours since disinfection (`run_rolling`'s 20) reach no disinfection within the self-test's horizons, so the parity arm reads the same series.
- `tools/audit/regret_oracle.py:146 CONST_SWAP`: unpinned: shifting the bound grid by one step (15 min) moves no admission on the self-test cells; the bound is read at each step's end, the convention `score`'s `room[1:]` fixes.
- `tools/audit/regret_oracle.py:147 CONST_SWAP`: equivalent: `minute / 120` against `/ 60` keeps every quarter-hour inside its hour, and `get_temp_bounds` compares the hour against whole-hour day bounds.

## Approval

Pending: the owner's approving review at the head. Policy paths this diff touches: `dev/governance/dimensions/D0.md` step 8 and `dev/governance/dimensions/D15.md` step 9 (wording drafted under mandate 6893738184, scope all, per Carry 2), `dev/governance/decisions/0018-objective-function.md` (the D0 row, the `regret` row and its gaming row name the instrument), and `.github/workflows/governance.yml` (the new self-test step). Each is code-owned.

## Red checks

none

## Forward-carry

none

## Friction

- fixer.md: cost: the job that runs every tools/ self-test installs no pinned stack, so a tool that solves pays its own interpreter and install in that job (departure 4); `selftest_scope.py record --step` also re-measures the background steps it launches, whose entries were left as committed. Carry: dismissed: recorded here; the reviewer judges the step
