# R11-PRE-NEW-DIMENSIONS: two dimensions whose oracle is the plan (D16) and the documented effect (D17), each over a universe a command prints

Designer round 2, on top of eb49f17976c34f6400a9d0e68c58d22f6523f4ee, answering `Design review: revise` at f050ffc77006c53d6654c0404028b0e9db3a7ba9: point 1 in 3.1, point 2 in 3.3, point 3 in section 5; its notes r1 to r3 are folded into the header, 3.3 and section 7. Base: origin/main b3831ff64eca1936f0b618193ee86c3e337b51a9. Predecessor heads read (neither has a `handoff/` ref yet): R11-PRE-FINDER-CONTRACT at cb6600d2f1d91ac007344bd92aade8350c9007de, R11-PRE-BRIEFS-CENSUS at 92098a0099f9a31a153d07d91dd9ec5e3aac2a20. Evaluation: eval/r11 tip 9de7c2bdc73361a5428d85bc444bf973c43bb593 (revision_3; U5 and U10 reworded "no escape behind it", decisions and paths unchanged), whose `review` reads approve of 02a48db212e0e49af62863575cba86bc339d4958 (the sha an accepted card's merge must not be an ancestor of). Prototype: 530cda6a2416e3434aea699e7b7e2611e0eb5f94. Brief wording is drafted by the seat under mandate 6893738184 (scope all), declared with that id in the body.

## Figures

Literals are snapshots at the census head; re-measure at your merge base.

| id | figure | literal | enumerator (run in a checkout of the census head) |
|---|---|---|---|
| F1 | actuator universe, lines; with `--cells` today (lines x 3 duty modes x 4 conditions); after 3.3 (lines x 14 states) | 38 (8 write, 30 hold); 456; derived, never carried | `python3 -I tools/audit/enumerate.py d16-writes` piped to `wc -l`; the same with `--cells` |
| F2 | feature universe, lines | 307 | `python3 -I tools/audit/enumerate.py d17-features` piped to `wc -l` |
| F3 | F1 write lines that write no actuator; writers F1 misses | 1 (`_fetch_weather_forecast`, a forecast read); 1 (the service call handed on uncalled inside `coordinator.py`) | F1's output grepped for `_fetch_weather_forecast`; `grep -n 'services\.async_call,' custom_components/heatpump_optimizer/*.py` |
| F4 | `CLAUDE.md` tokens against its cap; corpus against its cap | 3604 of 3605; 69971 of 69971 | `node tools/policy/policy_lint.mjs --budgets`, the `CLAUDE.md` and `corpus:` lines |
| F5 | U cards at the evaluation tip, by decision | 9, all accepted (U1, U2, U4 to U10) | the `cards` keys of `dev/audit/yardstick/round11/EVALUATION.json` at 9de7c2bdc7 that begin E11-U |
| F6 | per-dimension lists in the role contracts and rules; briefs stating their own worktree | 2 (`dev/governance/roles/COMMON.md` lines 22 and 30 at cb6600d2f1); 3 (D3, D9, D13) | `git grep -n -E "D[0-9]+(, \| and \|/\| or )(and )?D[0-9]+" -- dev/governance/roles dev/governance/rules`; `git grep -n -i "worktree" -- dev/governance/dimensions` |
| F7 | `COMMON.md` against its cap | 117 of 117 lines, 1756 of 1756 tokens | `node tools/policy/policy_lint.mjs --budgets`, the row keyed `tools/audit/briefs/COMMON.md` |

## 1. What the approved evaluation changed since this group was cut

- **Every U card names a file**, `dev/governance/dimensions/D16.md` or `dev/governance/dimensions/D17.md` (U1 alone names D17; both exist at 530cda6a24, neither on main). The fold (a path ending in a slash read as a prefix in `tools/audit/check_scopes.py`) is therefore **not built**: its condition, "unless the approved evaluation names file paths", is met (review finding S2, resolved). The two file names are now binding: a brief landed under another name leaves every card unmerged.
- **E11-U9 is ruled** (accepted, "Accept all four"), so it is built with the rest, not held out.
- **E11-U10 is new and accepted** (R10-OUTSIDE-DHW-START-HYSTERESIS, path D16.md) and is not in this group's card list. It is designed in below as D16 step 4, in its own commit. decision: orchestrator, whether U10 closes here; if not, that commit is dropped and nothing else moves.
- **CADENCE no longer exists**: FINDER-CONTRACT deletes the table and `check-wave-script.mjs` at cb6600d2f1 refuses a driver that names one. This group adds no cadence row; both dimensions run every round by being in DIMS.

## 2. Owning seams (governance instruments; `tests/seam_map.json` maps product modules only and none changes)

| concern | owner | callers only |
|---|---|---|
| a dimension's method, oracle and territory | its brief under `dev/governance/dimensions/` | `CLAUDE.md` (index row), `tests/entities.py` |
| the item universe a seat reports against | `tools/audit/enumerate.py` | the briefs, `tools/ci/selftest_closures.json` |
| seat ownership of (file, step, axis) cells | `dev/audit/config/scopes.json`, proved by `tools/audit/check_scopes.py` | `.claude/workflows/audit-find.js` |
| the schedule: DIMS, ISOLATED, BOXES | `.claude/workflows/audit-find.js` | `tools/audit/prepare_baseline.sh` (ISOLATED_DIMS mirrors it), `dev/audit/config/rotation.json` (step list mirrors the brief) |

One owner per concern; no production code moves.

## 3. The shape

**3.1 D16, actuator write: the oracle is the plan.** The prototype's step 3 grades a write against "the documented target (docs, strings, the option's help)"; that is D6's oracle and is dropped. Round 1 of this note named `step_duty` and `_step_kw` as the plan-side reader and the arbiter's module docstring as the mapping; both are withdrawn (verdict point 1): they share `_step_index` with the write path, and the docstring is a document in the file under test.

*The step and its booked values.* The seat's harness builds the solve result itself, so it knows the step: it sets the clock to the k-th entry of `timestamps` plus an offset it chose, and reads index k of the result's own arrays (`power_schedule`, `dhw_power_schedule`, `optimal_setpoints`, `room_temp_trajectory`, and `duty_floor_kw`) by plain indexing. It imports nothing from `pump_arbiter` and calls no bisect of the package's. Whether a circuit runs in step k is decided by construction, not by a rule: every state of 3.3 books a circuit at exactly zero or at no less than twice the floor, so no threshold enters the oracle; the one cell that sits on the floor (U9's) states its booked kW as a number. `planned_draw_runs` is neither called nor copied.

*The mapping, as the D16 brief's own invariants* (the brief's wording, drafted under the mandate; the docstring table and its dated rulings are a lead source for the wording and never the oracle). Per state, what reached `services.async_call` must satisfy:

| state | invariant on the command sent |
|---|---|
| a step booking hot water only | nothing asks the house circuit to start: the mode is the pump's hot-water-only one where it offers one, else the space set-point is the value that calls for no heat; the tank set-point is the configured one |
| a step booking the house only | nothing asks the tank to charge; an indoor set-point equals index k of `optimal_setpoints`, inside the entity's bounds; a water set-point is strictly above the do-not-heat value whenever booked kW is above zero, does not fall as booked kW rises, and its effect is M4's |
| a step booking both | hot water is asked first, then the house, inside the one step |
| a step booking neither | no mode is written and no circuit is asked to start |
| no step covers now | the pump is handed back to its own thermostats: both circuits allowed, the configured tank set-point |
| boost over a booked step | the space channel's target is the top of the band, never a value between floor and top |
| disinfection held on | the tank write reaches the disinfection target, and the run is recorded complete only once it is reached |
| duty mode observe; off | no write in any state; each written entity returned to its baseline once |

A water set-point has no number in the plan, so its value is graded by the necessary conditions above (M2) and by its effect under the pump model (M4), never by re-deriving the arbiter's curve.

*The perturbations that show the oracle is not the code's* (the brief owes both, in D16's isolated worktree): P1, the arbiter's step selection moved one step late: the harness's k does not move and M3 is red (U6's defect); P2, the docstring row for a house-only step and the code edited together to allow the tank: the invariant does not move and M2 is red (decision 0018's gaming case). Null controls: the unedited tree is green, and the docstring edited alone moves no cell. An oracle obtained from `desired`, `step_duty` or `_step_kw` is void (`tests/README.md`; D3 step 6).

Steps of the brief, each with the card it owns and its input:

| step | what is driven | cards (input: the pull request the card's `unowned` names) |
|---|---|---|
| M1 | the universe (3.3) and the plan-side oracle per cell | none |
| M2 | the value: the command satisfies its state's invariant, inside the entity's bounds | U2 (3562; cell `boost-partial`), U4 (3452; `disinfection`), U9 (`min-cold-tank`) |
| M3 | timing and order: the write lands in the step its action was cut for; mode before supply; minimum run and pause across a re-solve | U6 (3478; `partial`, the cycle held across the end of step k), U8 (3530; `partial` entered from `idle`), U5 (3512; `idle` entered by a re-solve minutes after `partial` switched the supply on) |
| M4 | effect: under a pump model with an integrating speed loop and a start hysteresis, measured power and started runs equal the plan | U7 (3405; `partial`, water set-point), U10 (3531; `dhw-only`, tank above its set-point less the hysteresis) |
| M5 | hold and release: per hold, a transition table over the fields that gate the write, and from each reachable state a path to "writes again" needing no person | none (see 3.2, D1) |
| M6 | restore: off, unload, remove and a duty-mode change return each written entity to its baseline once | none |

**3.2 Territory, argued per neighbour.** These sentences go in the two briefs' hunting sections, once, and nowhere else.

- **D1** owns whether the cycle survives; its step 2 at the census head already drives "the previous release's persisted record driven to the first actuator write (a hold no restart released)". D16 M5 therefore takes holds on a store this release wrote; the stuck set-point after an upgrade stays D1's and D16 cites it rather than repeating it. U4, U5, U6, U8: the cycle completes and nothing is stale; the written value, its step or its order is wrong: D16.
- **D8** owns the published reason and operating state against the plan's draw (its step 2). D16 owns the command sent; an entity that reports the write wrongly is a D8 lead.
- **D12** owns setup and a published plan on every configuration level. D16 runs on the reference plant (`coord_all_features`); a write wrong only on one population level is a D12 lead with the level named.
- **D2** owns identities of the model; U9's second cause (the draw range learning from censored samples) stays with card E11-D2. U7 and U9's first cause are a write against the plan: D16.
- **D6** owns a sentence true of the code. D17 owns the feature doing what the sentence promises, end to end; where the effect is a written value D16 owns the value and D17 whether it happens at all. U1 (away with weekend or holiday comfort fields, 3013): no sentence is false and no write path is wrong; the feature does not follow a state the document names: D17 M3.

**3.3 Each universe as a command** (both printed by `tools/audit/enumerate.py`, which this group edits after CENSUS merges):

- **The cell formula (verdict point 2): cells = sites x states**, one axis, a tuple of 14 named states in the enumerator, each a (duty, level, overlay, lifecycle) the harness realises at step k. `PUMP_DUTY_MODES` and `CONDITIONS` both **leave the product as factors** and stay as rows: every state but the last two runs under duty mode control, the lifecycle rows run on `partial`. A full cross (sites x 9 x 4 x 3) would row combinations no card and no hold's gating field names; M5's transition table adds a row for any other state a hold's gate reads, and a seat may add rows, never drop one.

| state | the plan and plant that realise it (space kW, hot-water kW at step k; f the floor, P the maximum) |
|---|---|
| `idle` | 0, 0 |
| `min-cold-tank` | f, 0; tank reading 20 C (U9) |
| `partial` | (f+P)/2, 0 (U5, U6, U7, U8) |
| `full` | P, 0 |
| `dhw-only` | 0, 2f or more (U10) |
| `both` | (f+P)/2, 2f or more |
| `boost-partial` | `partial` with a space boost live (U2) |
| `disinfection` | `partial` with the disinfection cycle held on (U4) |
| `baseline` | the clock past the last step's end |
| `restart`, `upgrade`, `unavailable` | `partial` after a reload on this release's store; on the previous tag's store; with the written entity unavailable |
| `observe`, `off` | `partial` under that duty mode (null control: no write; restore once) |

  The self-test arm at `tools/audit/enumerate.py:648` becomes sites x the tuple's length, its perturbation one state cut from the tuple (the count falls by the site count), and its refusal stays `const.py` without `PUMP_DUTY_MODES`: the enumerator refuses unless `observe`, `off` and `control` are all in it, so a duty mode added in production fails the universe instead of going unrowed. U1's cell is D17's `option` line for the away step's comfort fields.
- The site list is wrong in both directions (F3): it counts a forecast read as a write and misses a writer that receives the service call as a value. Change: a write line is a call of, or a reference to, the service call, less those whose literal domain is on a tuple of read-only domains in the enumerator; a call whose domain is no literal prints as `write ... domain=?` and is a cell, never dropped. Self-test arms: a planted read-only call leaves the count, a planted handed-on reference raises it, an emptied source refuses.
- `d17-features` (F2) is kept. Add `--kind` so a seat prints its own cells; the kinds are the line prefixes. `scopes.json`'s `kind` values are a second copy of those prefixes (verdict note r2): a `check_scopes.py` self-test arm reads both and refuses unequal sets, its control a planted extra prefix.

**3.4 Seats, boxes, isolation.** Three seats each (the cards' cost line; `scopes.json` `_rule`). Mode cells.

- D16: universe `custom_components/heatpump_optimizer/*.py`; s1 M1+M2, s2 M3+M4, s3 M5+M6, every file.
- D17: universe the package's `*.py`, `services.yaml`, `strings.json` and `blueprints/**` (the prototype also listed `README.md`, `docs/*.md` and the translations: dropped, they are the oracle's source and D6's universe, not cells D17 owns); axis `kind` with the enumerator's prefixes; every seat holds steps M1 to M3; s1 option and options-step, s2 config-field and config-step, s3 service, entity and blueprint. Brief steps: M1 the universe and, per item, its documented effect as one sentence with file and key; M2 that sentence made an executable check before the implementation is read; M3 end to end through the options flow, the service schema or the entity's own method, in every plan state that reaches the feature, across a restart, with one named state changed (weekend, holiday, presence). The prototype's fourth step (null control and perturbation) is cut: `COMMON.md` already owes both.
- ISOLATED gains D16 and not D17. D16's perturbation is a one-line edit in the write path, which `COMMON.md` allows only in an isolated worktree, and its upgrade cell reads the previous tag's package from `.git`; this replaces the prototype's `old-releases/` export, which no predecessor lands. D17 perturbs configuration only. `tools/audit/prepare_baseline.sh` ISOLATED_DIMS gains D16 in the same commit (the wave-script check refuses the two lists unequal).
- BOXES: all six seats heavy (each drives cycles on a real loop). D16-s1 to s3 on B11, D17-s1 to s3 on B13, whose heavy lists are empty at cb6600d2f1; no box is added.
- `dev/audit/config/rotation.json` gains both entries with the briefs' step lists and empty rounds.

**3.5 `check_scopes.py`.** The prototype's territory construct is not kept: no card names it and it rewrites every dimension's entry. The change is two self-test arms that read the new dimensions' seat keys off the file: a block of D16's first seat copied into its second is refused as owned twice; D17's last seat emptied is refused as unowned; the live file passes (null control).

## 4. Alternatives, and why each lost

- **Plan states as a `scopes.json` axis for D16.** Seat ownership would then be cut by plan state, but every card's step needs all states at one site; three seats would each rebuild the same harness per state. Steps cut the work where the harness differs.
- **The oracle from `desired`.** One call, no duplication, and it grades the arbiter against itself: U2 and U9 are defects inside that function.
- **One dimension for both.** U1 has no write-path defect and U2 no feature that is off; one brief would need both oracles and its seats both harnesses, and `unowned` could not say which half failed.
- **A new box per dimension.** Two more containers for seats that already have their own worktree (D16) or share an export read-only (D17).

## 5. Sibling sites

Three commands at the fixer's base. (a) `git grep -n -E "D15\b|D1[0-5]\]|1\[0-5\]" -- .claude/workflows tools/audit tools/policy tests/entities.py dev/audit/README.md dev/audit/config/finding.schema.json`: each hit either derives from the briefs directory (covered by landing the files), already admits 16 and 17 (the report schema's pattern and the seat-id controls at cb6600d2f1), or is a list this note names (DIMS, ISOLATED, BOXES, ISOLATED_DIMS, rotation, scopes, the `CLAUDE.md` table). (b) and (c), F6's two enumerators, added for verdict point 3 because (a) cannot match a list of single-digit dimensions. A hit in no class is edited or reported.

F6's hits, per line (`dev/governance/roles/COMMON.md` at cb6600d2f1):

- **Line 22, "read `docs/` (D5, D6)": edited, D17 added.** D17's oracle is read from `README.md` and `docs/`; D6's brief does not state the exposure duty itself, so the list is what binds and must be complete.
- **Line 30, "an isolated worktree for that purpose (D3, D11, and D0/D9 when instrumenting)": edited, D16 added.** The list cannot be cut instead: D0's and D11's briefs do not state the licence (F6's second figure), so the line is their only grant. D16's brief also says it has the worktree and what for (the one-line perturbations P1 and P2), as D3's and D9's do.
- Both edits stay on their lines; the row is F7, with no headroom in tokens. Pay inside `COMMON.md` by cutting prose another line of it already carries; failing that, the body's `## Raise justification`.
- `dev/governance/dimensions/D3.md:6`, "the one finder with an **isolated worktree**", is untrue of the driver's ISOLATED set today and of D16: cut "the one" (a cut, so it pays) and name the line in the body.

`dev/audit/config/scopes.json` D6's universe holds `dev/governance/{dimensions,roles,rules}/*.md`, so both briefs enter D6's ledger; D5's `classify` is suffix-bound and unaffected.

## 6. Evidence, by file

| claim | instrument | null control |
|---|---|---|
| scopes disjoint and complete with both dimensions | `python3 tools/audit/check_scopes.py --repo . --ref HEAD` rc 0 | `--self-test`: the two arms of 3.5 red, live green |
| the schedule holds | the **base copy** of `tools/policy/check-wave-script.mjs` run on the head's driver | its own positive control (a DIMS list short of a brief is refused) |
| each universe prints | `python3 -I tools/audit/enumerate.py --briefs` lists D16 and D17 `ok` | `--self-test`: 3.3's three site arms and the state-tuple arm |
| the D16 oracle is the plan's | the D16 brief's text: the eight invariants of 3.1, P1 and P2 as owed perturbations, and the rule that the oracle half of a harness imports nothing from `pump_arbiter` (the verifier's check on each D16 finding; no grader is added) | the unedited tree green; the docstring edited alone moves nothing |
| each U card has a step and input | the table of 3.1 and D17 M3 in the body, one row per card of F5 | a card id absent from the body's table is the reviewer's block |
| budgets | `node tools/policy/policy_lint.mjs --budgets` rows for `CLAUDE.md`, both briefs, F7's row, `dev/governance/dimensions/D3.md`, `corpus:` | none: an exact cap |

No golden moves and no claim file is touched. `tests/closures.json` is re-recorded on Linux only (`gate-scoping.md`). No finder harness exists for the cards (each is an owner or outside report): no finder harness: owner report; the planted cells above are the fixture.

## 7. Cost, hot files, serial position

Size L. Commits in order: the enumerator and its self-test; the two briefs with `COMMON.md`'s two lines, D3's cut, `rotation.json`, `scopes.json` and the `check_scopes.py` arms; the driver and `prepare_baseline.sh`; `CLAUDE.md` rows and `policy_budgets.json`; closures; last, alone, D16 M4's U10 row. No p1/p2 split is needed if `check-wave-script.mjs` is untouched; if the base copy refuses the driver for a reason only a grader change cures, stop and report it as the split.

Hot files: `dev/governance/config/policy_budgets.json` (every R11-PRE finder group; aggregates re-measured by the later merge), `dev/audit/config/scopes.json`, `dev/audit/config/rotation.json`, `tools/audit/enumerate.py` and `tools/ci/selftest_closures.json` (CENSUS), `.claude/workflows/audit-find.js` (FINDER-CONTRACT), `tests/closures.json`, `CLAUDE.md`, `dev/governance/roles/COMMON.md` (FINDER-CONTRACT). Open designs R11-PRE-STANDING-SCRIPTS (d1a4ae6a74: `CLAUDE.md`, `policy_budgets.json`) and R11-PRE-SHARED-FILES (281e74a24e: `CLAUDE.md`, `tests/closures.json`) share hot files and no seam; the later merge re-measures (verdict note r3). After: both predecessors merged, and the review commit 02a48db212 exists (it does). Budgets (F4): `CLAUDE.md` has one token of headroom and the corpus none, so two table rows and two briefs cannot land unpaid. Pay first: the D17 step cut in 3.4, the territory sentences stated once (3.2), and the prototype's "Escapes this dimension exists for" lists dropped from both briefs (the cards carry them). What remains is new owner-ruled content; that remainder is a raise with its `## Raise justification` and score line, approved under the mandate.

## Notes for the fixer

- A hold line whose latch gates no actuator write (the price, weather and solar fetch latches in `coordinator.py`) is rowed "gates no write" with its reason and counts as examined; do not drop it from the universe. Carry: R11-PRE-NEW-DIMENSIONS (item n1)
- `check_scopes.py` caps each D6 seat at `ledger.max_units`; the two briefs add units to the seat holding the dimension briefs. If it goes over, re-cut D6's seats, never the cap. Carry: R11-PRE-NEW-DIMENSIONS (item n2)
- A harness under `dev/audit/harnesses/` whose header names a new brief must be cited by that brief or `check_scopes.py` refuses it. Carry: R11-PRE-NEW-DIMENSIONS (item n3)
- The six box placements of 3.4 were read against the heavy lists only, not run through the driver's own gap predicate in the time box; run it before the briefs are written. Carry: R11-PRE-NEW-DIMENSIONS (item n4)
- Carries 175 and 177 on R11-INTAKE-R10-RESIDUE name the actuator-write draft and none names the feature-behaviour draft (card E11-COMMON); the body says which this merge discharges. decision: orchestrator. Carry: R11-INTAKE-R10-RESIDUE (item n5)
- R11-PRE-BRIEFS-TEXT (head 02d85c00e7) edits D6 and D7 and the same budget file; neither new brief quotes their text. Carry: dismissed: no shared lines (item n6)
