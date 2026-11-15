# R11-PRE-NEW-DIMENSIONS: two dimensions whose oracle is the plan (D16) and the documented effect (D17), each over a universe a command prints

Designer round 1; no verdict is on `design-verdict/R11-PRE-NEW-DIMENSIONS`. Base: origin/main b3831ff64eca1936f0b618193ee86c3e337b51a9. Predecessor heads read (neither has a `handoff/` ref yet): R11-PRE-FINDER-CONTRACT at cb6600d2f1d91ac007344bd92aade8350c9007de, R11-PRE-BRIEFS-CENSUS at 92098a0099f9a31a153d07d91dd9ec5e3aac2a20. Evaluation: eval/r11 tip ca3f872430d0f2863ac7bb7c3d4304fda538f7a5, whose `review` reads approve of 02a48db212e0e49af62863575cba86bc339d4958 (the sha an accepted card's merge must not be an ancestor of). Prototype: 530cda6a2416e3434aea699e7b7e2611e0eb5f94. Brief wording is drafted by the seat under mandate 6893738184 (scope all), declared with that id in the body.

## Figures

Literals are snapshots at the census head; re-measure at your merge base.

| id | figure | literal | enumerator (run in a checkout of the census head) |
|---|---|---|---|
| F1 | actuator universe, lines; with `--cells` | 38 (8 write, 30 hold); 456 | `python3 -I tools/audit/enumerate.py d16-writes` piped to `wc -l`; the same with `--cells` |
| F2 | feature universe, lines | 307 | `python3 -I tools/audit/enumerate.py d17-features` piped to `wc -l` |
| F3 | F1 write lines that write no actuator; writers F1 misses | 1 (`_fetch_weather_forecast`, a forecast read); 1 (the service call handed on uncalled inside `coordinator.py`) | F1's output grepped for `_fetch_weather_forecast`; `grep -n 'services\.async_call,' custom_components/heatpump_optimizer/*.py` |
| F4 | `CLAUDE.md` tokens against its cap; corpus against its cap | 3604 of 3605; 69971 of 69971 | `node tools/policy/policy_lint.mjs --budgets`, the `CLAUDE.md` and `corpus:` lines |
| F5 | U cards at the evaluation tip, by decision | 9, all accepted (U1, U2, U4 to U10) | the `cards` keys of `dev/audit/yardstick/round11/EVALUATION.json` at ca3f872430 that begin E11-U |

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

**3.1 D16, actuator write: the oracle is the plan.** The prototype's step 3 grades a write against "the documented target (docs, strings, the option's help)"; that is D6's oracle and is dropped. The target is computed from the solve result the cycle holds, before the write path is read: the step's duty by the plan's own running rule (`step_duty`), its booked power (`_step_kw`) and planned room temperature, turned into the command the arbiter's own table in `pump_arbiter.py` states (`PumpCommand`: mode, hot-water set-point, space set-point). The seat's harness records what reached `services.async_call` and compares; an oracle obtained by calling `desired` is the code under test and is void (`tests/README.md`, a re-implemented formula pins nothing; D3 step 6).

Steps of the brief, each with the card it owns and its input:

| step | what is driven | cards (input: the pull request the card's `unowned` names) |
|---|---|---|
| M1 | the universe (3.3) and the plan-side oracle per cell | none |
| M2 | the value: written value equals the plan's target, inside the entity's bounds | U2 (boost over a partial step, 3562), U4 (disinfection set-point, 3452), U9 (minimum power on a cold tank equals the do-not-heat value) |
| M3 | timing and order: the write lands in the step its action was cut for; mode before supply; minimum run and pause across a re-solve | U6 (3478), U8 (3530), U5 (3512) |
| M4 | effect: under a pump model with an integrating speed loop and a start hysteresis, measured power and started runs equal the plan | U7 (3405), U10 (3531) |
| M5 | hold and release: per hold, a transition table over the fields that gate the write, and from each reachable state a path to "writes again" needing no person | none (see 3.2, D1) |
| M6 | restore: off, unload, remove and a duty-mode change return each written entity to its baseline once | none |

**3.2 Territory, argued per neighbour.** These sentences go in the two briefs' hunting sections, once, and nowhere else.

- **D1** owns whether the cycle survives; its step 2 at the census head already drives "the previous release's persisted record driven to the first actuator write (a hold no restart released)". D16 M5 therefore takes holds on a store this release wrote; the stuck set-point after an upgrade stays D1's and D16 cites it rather than repeating it. U4, U5, U6, U8: the cycle completes and nothing is stale; the written value, its step or its order is wrong: D16.
- **D8** owns the published reason and operating state against the plan's draw (its step 2). D16 owns the command sent; an entity that reports the write wrongly is a D8 lead.
- **D12** owns setup and a published plan on every configuration level. D16 runs on the reference plant (`coord_all_features`); a write wrong only on one population level is a D12 lead with the level named.
- **D2** owns identities of the model; U9's second cause (the draw range learning from censored samples) stays with card E11-D2. U7 and U9's first cause are a write against the plan: D16.
- **D6** owns a sentence true of the code. D17 owns the feature doing what the sentence promises, end to end; where the effect is a written value D16 owns the value and D17 whether it happens at all. U1 (away with weekend or holiday comfort fields, 3013): no sentence is false and no write path is wrong; the feature does not follow a state the document names: D17 M3.

**3.3 Each universe as a command** (both printed by `tools/audit/enumerate.py`, which this group edits after CENSUS merges):

- `d16-writes --cells` today crosses sites with duty modes and four lifecycle conditions (F1), not with plan states. Change: cells are site times plan state, the states a tuple beside `CONDITIONS`: idle, partial, full, both, hot-water only, boost, disinfection, baseline, first cycle after an upgrade (the brief's five, plus the rows of the arbiter's own table and U4's step). Duty mode `observe` is the brief's null control (no write in any cell), not an axis.
- The site list is wrong in both directions (F3): it counts a forecast read as a write and misses a writer that receives the service call as a value. Change: a write line is a call of, or a reference to, the service call, less those whose literal domain is on a tuple of read-only domains in the enumerator; a call whose domain is no literal prints as `write ... domain=?` and is a cell, never dropped. Self-test arms: a planted read-only call leaves the count, a planted handed-on reference raises it, an emptied source refuses.
- `d17-features` (F2) is kept. Add `--kind` so a seat prints its own cells; the kinds are the line prefixes.

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

`git grep -n -E "D15\b|D1[0-5]\]|1\[0-5\]" -- .claude/workflows tools/audit tools/policy tests/entities.py dev/audit/README.md dev/audit/config/finding.schema.json` at the fixer's base: each hit either derives from the briefs directory (covered by landing the files), already admits 16 and 17 (the report schema's pattern and the seat-id controls at cb6600d2f1), or is a list this note names (DIMS, ISOLATED, BOXES, ISOLATED_DIMS, rotation, scopes, the `CLAUDE.md` table). A hit in none of the three classes is edited or reported. `dev/audit/config/scopes.json` D6's universe holds `dev/governance/{dimensions,roles,rules}/*.md`, so both briefs enter D6's ledger; D5's `classify` is suffix-bound and unaffected.

## 6. Evidence, by file

| claim | instrument | null control |
|---|---|---|
| scopes disjoint and complete with both dimensions | `python3 tools/audit/check_scopes.py --repo . --ref HEAD` rc 0 | `--self-test`: the two arms of 3.5 red, live green |
| the schedule holds | the **base copy** of `tools/policy/check-wave-script.mjs` run on the head's driver | its own positive control (a DIMS list short of a brief is refused) |
| each universe prints | `python3 -I tools/audit/enumerate.py --briefs` lists D16 and D17 `ok` | `--self-test`: 3.3's three arms |
| each U card has a step and input | the table of 3.1 and D17 M3 in the body, one row per card of F5 | a card id absent from the body's table is the reviewer's block |
| budgets | `node tools/policy/policy_lint.mjs --budgets` rows for `CLAUDE.md`, both briefs, `corpus:` | none: an exact cap |

No golden moves and no claim file is touched. `tests/closures.json` is re-recorded on Linux only (`gate-scoping.md`). No finder harness exists for the cards (each is an owner or outside report): no finder harness: owner report; the planted cells above are the fixture.

## 7. Cost, hot files, serial position

Size L. Commits in order: the enumerator and its self-test; the two briefs with `rotation.json`, `scopes.json` and the `check_scopes.py` arms; the driver and `prepare_baseline.sh`; `CLAUDE.md` rows and `policy_budgets.json`; closures; last, alone, D16 M4's U10 row. No p1/p2 split is needed if `check-wave-script.mjs` is untouched; if the base copy refuses the driver for a reason only a grader change cures, stop and report it as the split.

Hot files: `dev/governance/config/policy_budgets.json` (every R11-PRE finder group; aggregates re-measured by the later merge), `dev/audit/config/scopes.json`, `dev/audit/config/rotation.json`, `tools/audit/enumerate.py` and `tools/ci/selftest_closures.json` (CENSUS), `.claude/workflows/audit-find.js` (FINDER-CONTRACT), `tests/closures.json`, `CLAUDE.md`. After: both predecessors merged, and the review commit 02a48db212 exists (it does). Budgets (F4): `CLAUDE.md` has one token of headroom and the corpus none, so two table rows and two briefs cannot land unpaid. Pay first: the D17 step cut in 3.4, the territory sentences stated once (3.2), and the prototype's "Escapes this dimension exists for" lists dropped from both briefs (the cards carry them). What remains is new owner-ruled content; that remainder is a raise with its `## Raise justification` and score line, approved under the mandate.

## Notes for the fixer

- A hold line whose latch gates no actuator write (the price, weather and solar fetch latches in `coordinator.py`) is rowed "gates no write" with its reason and counts as examined; do not drop it from the universe. Carry: R11-PRE-NEW-DIMENSIONS (item n1)
- `check_scopes.py` caps each D6 seat at `ledger.max_units`; the two briefs add units to the seat holding the dimension briefs. If it goes over, re-cut D6's seats, never the cap. Carry: R11-PRE-NEW-DIMENSIONS (item n2)
- A harness under `dev/audit/harnesses/` whose header names a new brief must be cited by that brief or `check_scopes.py` refuses it. Carry: R11-PRE-NEW-DIMENSIONS (item n3)
- The six box placements of 3.4 were read against the heavy lists only, not run through the driver's own gap predicate in the time box; run it before the briefs are written. Carry: R11-PRE-NEW-DIMENSIONS (item n4)
- Carries 175 and 177 on R11-INTAKE-R10-RESIDUE name the actuator-write draft and none names the feature-behaviour draft (card E11-COMMON); the body says which this merge discharges. decision: orchestrator. Carry: R11-INTAKE-R10-RESIDUE (item n5)
- R11-PRE-BRIEFS-TEXT (head 02d85c00e7) edits D6 and D7 and the same budget file; neither new brief quotes their text. Carry: dismissed: no shared lines (item n6)
