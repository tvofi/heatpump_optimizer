# Round 8 fix plan: by bug class, in three waves

Planning seat, 2026-09-24 (UTC). Fork: `origin/main` `0011bc7` (after #1509). Evidence baseline: `cdf82daa`.
Input: 38 judged findings, filed as #1512–#1549 (`issues-filed.json`). Draft roster: `wave-r8-groups.json`, beside this file.

## Summary

15 class groups cover 33 findings. The other 5 findings get a ruling, a fold or a deferral, and no group.

| wave | group | class | issues (R8 id) | sev | code-owned | coordinator.py hunk | budget risk | root-cause seat |
|---|---|---|---|---|---|---|---|---|
| 1 | R8-P8 | P8 unit blind at input seam | #1513 (D2-s2-02) | **H** | no | `_pv_export_price`, inlet read | down (re-record) | – |
| 1 | R8-P11 | **P11 (new)** billing rule not modelled | #1512 (D2-s2-01) | **H** | no | none | cc rows on `_close_window` | – |
| 1 | R8-I3 | I3 required-check / release hole | #1514 (D11-s1-01), #1515 (D11-s2-01), #1516 (D11-s2-02), #1547 (D11-s1-03) | **H H H** L | **yes** (workflows, CODEOWNERS, hooks) | none | none | **#1514, #1515** |
| 1 | R8-I1a | I1 kill rule, and the I2 cache key | #1521 (D3-s1-01), #1531 (D3-s1-02) | M L | **yes** (`mutation_table.py`, `env_drift.py`) | none | none | – |
| 1 | R8-P9 | P9 card rule misses a control | #1522 (D4-01) | M | **yes** (`card_browser.mjs`) | none | none | – |
| 2 | R8-P5 | P5 sysid gate (+P2 freeze seam) | #1523 (D7-s1-01), #1524 (D7-s1-02), #1525 (D7-s1-03) | M M M | no | sysid run/adopt | **likeliest raise** (`internal_call_edges`) | **#1525** |
| 2 | R8-P1 | P1 unvalidated value at a boundary | #1518 (D1-s2-01), #1519 (D1-s3-01), #1541 (D8-s1-01) | M M L | no | none | none expected | – |
| 2 | R8-P2 | P2 "has DHW / has probe" sibling seam | #1527 (D12-s1-02), #1542 (D8-s2-02) | M L | no | none | none | – |
| 2 | R8-P12 | **P12 (new)** live state across await/thread | #1517 (D1-s1-01), #1529 (D1-s1-02) | M L | no | none (fix goes in `away.py`) | none | – |
| 2 | R8-P6 | P6 accepted ≠ actuated | #1526 (D12-s1-01) | M | no | `_apply_action` | flat (helper outside class) | – |
| 2 | R8-P3 | P3 sibling COP formulas disagree | #1520 (D2-s1-01), #1530 (D2-s1-02) | M L | no | none | cc rows in optimizer | – |
| 3 | R8-I5a | I5 quality_scale claims | #1545 (D10-s1-01), #1546 (D10-s1-02) | L L | no | 4 `UpdateFailed` sites | flat (helper outside class) | **#1545** |
| 3 | R8-I5b | I5 docs/comment/string drift | #1534, #1535, #1536, #1537 | L×4 | no | none | none | – |
| 3 | R8-I1b | I1 deletable guards | #1532 (D3-s2-01), #1533 (D3-s2-02), #1540 (D7-s2-03) | L×3 | no | none | `unpinned_sites` down | – |
| 3 | R8-I4 | I4 ratchet measures by name | #1538 (D7-s2-01), #1539 (D7-s2-02) | L L | no | none (deletes dead symbols elsewhere) | seam rows identical by construction | – |
| – | ruling | P4 solver cost | #1543 (D9-s1-01) | L | – | – | – | – |
| – | fold → #1508 | I2 gate blind to cycle cost | #1544 (D9-s2-01) | L | – | – | – | – |
| – | defer (D11 round) | I3 install hash-pins | #1548 (D11-s2-03) | L | – | – | – | – |
| – | defer (D13 round) | I4 yield metric | #1549 (D13-s1-01) | L | – | – | – | – |
| – | ruling | I3 verdict on owner path | #1528 (D13-s1-02) | M | – | – | – | – |

**Owner rulings (6).** Each has a recommended default, and a seat can start on the default. See §5.
1. #1524, two-zone sysid: refuse to arm.
2. #1512, distinct-days default for existing installs: ON where `peaks_averaged` is above one.
3. #1543 against the #1463 refusal: refuse.
4. #1528, fix-review verdict on owner-approved merges: require it, with no new check.
5. The v* tag ruleset for #1516: a settings action for the owner.
6. Confirm the move-4 folds and deferrals: #1544, #1548, #1549.

**Budget raises.** Planned: 0. Likely: 1, in R8-P5 (`internal_call_edges`, possibly `cross_seam_edges`). Every row sits at zero headroom at `0011bc7`: `python3 tests/structure.py` printed `ok` with the measured value equal to the budget on every row. The owner's raise mandate expires **2026-09-24T13:55Z**. After that time, a raise needs the owner's own explicit confirmation.

**Blockers.**
- Nothing blocks wave 1.
- R8-P3 waits on #1487 (`optimizer.py`).
- R8-P11 sequences with #1499.
- The three code-owned wave-1 groups need tvofi's review, inside the mandate if possible.
- The orchestrator's clone must fetch the transport branch, so that `6f58e33` resolves. It carries the round-8 harnesses. Without it, `brief_lint` prints warnings instead of verifying.

---

## 1. Binding frame

- **Strategy, owner moves 1, 2, 4 and 5.** Every group ships a *barrier* that runs in CI, plus every instance its enumeration returns, and each instance gets a regression test (move 5). Barriers go into existing scripts wherever possible, for two reasons:
  - It avoids new closure/INERT classification (`tests/entities.py` refuses an unclassified tracked file).
  - The process moratorium (move 4) forbids new policy files and new lint classes, except where a class barrier or a high D11 finding requires one.
- **Move 3 is not adopted.** No feature is cut. #1524's recommended refusal is a named refusal inside an existing feature (sysid on a two-zone house), not a removal.
- **The fixer's contract caps a group** at five findings and about 400 production lines (`fixer.md`). Every group here fits: the largest carries four findings.
- **Harnesses** stay out of the tree (`fixer.md` step 3, commit `21acaf8e`). Seats run them from the evidence export and cite `$EXPORT/<path>` with its sha1. The briefs cite `handoff/round8/evidence/…` together with the transport commit `6f58e33`, which is how `brief_lint` resolves them. Once the register PR lands the evidence under `tools/audit/round8/`, the two copies are the same files.
- **Judge instrument notes that bind the fixers.** Each is carried into the relevant brief.
  - D8's finite harness needs real orjson on the path.
  - Several harnesses hard-code seat temp roots. Derive them from `TMPDIR`.
  - D1-s3's isinstance guard alone leaves 1 shape, so the fix needs the fence too.
  - The D7 sentinel re-took at 14, not 12.
  - D5's step-number regex under-counts: it found 3 mismatches where there are 4.
  - D8-s2-02's finder harness is void. Use the judge's harness.

## 2. Classes: reuse and new

| class | source | round-8 instances | barrier this plan ships |
|---|---|---|---|
| P1 | classes.md | #1518, #1519, #1541 | `tests/finite_boundary.py`: reach arm gains non-numeric and wrong-type leaves; a publish arm over all six platforms. `tests/open_meteo.py` gains a hostile-shape arm |
| P2 | classes.md | #1527, #1542 (#1523's freeze half rides P5) | `tests/entities.py`: every DHW-subject entity takes availability and enabled-default from the one mixin |
| P3 | classes.md | #1520, #1530 | static seam rule (every COP call carries humidity); dhw-vs-buffer COP-law property test |
| P5 | classes.md | #1523, #1524, #1525 | one pure adoption-decision function in `sysid.py` that returns a reason on every path; a test drives every refusal path; a learner-seam freeze enumeration |
| P6 | classes.md | #1526 | a table test: every domain an accept-list admits has a route in the consumer |
| P8 | classes.md | #1513 | a unit-aware price normaliser in `inputs.py`; a `tests/entities.py` check that refuses any `float(<entity>.state)` outside `inputs.py` that is not normalised or dispositioned |
| P9 | classes.md | #1522 | a reading-order arm in `tests/card_browser.mjs` |
| **P11** | **new** | #1512 | a bill oracle driven from each `CapacityTariff`'s stated rule, over every catalog entry |
| **P12** | **new** | #1517, #1529 | a `tests/entities.py` check that refuses an executor hand-off of a bound coordinator method; compare-and-restore in `away.py` |
| I1 | classes.md | #1521, #1532, #1533, #1540 | a kill needs a failing-count rise, and a comment-only mutant must survive; killed sites recorded under `killed_by` |
| I2 | classes.md | #1531 (rides I1a), #1544 (fold) | a cache key only on the names the capture reads |
| I3 | classes.md | #1514, #1515, #1516, #1547; #1528, #1548 ruled/deferred | the checker runs from the base ref; `codeowners_gap.py` transitive walk; an ancestry step in release |
| I4 | classes.md | #1538, #1539; #1549 deferred | liveness resolved through imports; an explicit method-to-seam map |
| I5 | classes.md | #1534–#1537, #1545, #1546 | `tests/doc_claims.py` arms: the quality_scale censuses, and README requirements = manifest |
| P4 | classes.md | #1543 (ruling) | none: ruling |

Why the two new classes don't fit an existing one:
- **P11** is a rule the tariff states (three peaks on three days) that the aggregation never implemented. The code does compute the quantity it names, so this is not P5 (wrong quantity keyed). No producer or consumer pair is involved either, so it is not P6.
- **P12** covers both halves of D1-s1. The state is correct at each instant, but a write lands across the solve's `await` (#1517), or a read lands on a thread (#1529). No existing class names that mechanism.

## 3. Groups: files, code-owned paths, budget, classification

Each group's full brief is in `wave-r8-groups.json`. What the orchestrator needs for sequencing:

| group | files touched | new files | code-owned | structure rows likely to move | fixture |
|---|---|---|---|---|---|
| R8-P8 | `inputs.py`, `price_model.py`, `coordinator.py` (`_pv_export_price`, the DHW-inlet read, module fn `_grid_fee_entity_value`), `tests/entities.py`, `tests/features.py` | none | no | `coordinator_loc` ↓ (re-record, reason in commit) | maybe (claim) |
| R8-P11 | `tariff.py`, `grid_fee.py`, `config_flow.py`, `strings.json`, `translations/{en,sv}.json`, `tests/features.py`, `tests/finite_boundary.py` | none | no | `functions_cc_over_15` / `max_cc` if `_close_window` grows | yes (optimality goldens) |
| R8-I3 | `.github/workflows/governance.yml`, **new** `.github/workflows/<pr-contract>.yml`, `release.yml`, `.github/CODEOWNERS`, `.claude/hooks/stop-selfcheck.sh`, `tools/audit/round6/D11/fix/codeowners_gap.py` | 1 workflow file | **all** | none | no |
| R8-I1a | `tests/mutation_table.py`, `tests/env_drift.py` | none | **yes** | none | no |
| R8-P9 | `www/heatpump-optimizer-card.js`, `tests/card_browser.mjs` | none | **yes** (`card_browser.mjs`) | none | card (claim) |
| R8-P5 | `coordinator.py` (sysid pair), `sysid.py`, `tests/features.py` | none | no | `coordinator_loc` ↓ from the move; `internal_call_edges` ↑1 risk; `cross_seam_edges` by bucket | maybe |
| R8-P1 | `ledger.py`, `open_meteo.py`, `entity.py`, `sensor.py`, `tests/finite_boundary.py`, `tests/open_meteo.py` | none | no | `duplication_blocks` may fall | no |
| R8-P2 | `boost.py`, `switch.py`, `sensor.py`, `tests/entities.py` | none | no | none | no |
| R8-P12 | `away.py`, `services.py`, `tests/entities.py`, `tests/features.py` | none | no | none (`async_run_optimization` must not grow) | no |
| R8-P6 | `coordinator.py` (`_apply_action`), module-level helper, `tests/features.py` | none | no | flat | no |
| R8-P3 | `thermal_model.py`, `optimizer.py`, `tests/features.py` | none | no | `functions_cc_over_*`, `max_cc` | **yes** |
| R8-I5a | `diagnostics.py`, `config_flow.py`, `coordinator.py` (4 raise sites), `quality_scale.yaml`, `strings.json`, translations, `tests/doc_claims.py` | none | no | flat (helper outside the class) | no |
| R8-I5b | `README.md`, `const.py`, `optimizer.py` (comment), `translations/sv.json`, `tests/doc_claims.py` | none | no | none | no |
| R8-I1b | `tests/features.py`, `tests/mutation_budgets.json` | none | no | `unpinned_sites` ↓ (that file's ratchet) | no |
| R8-I4 | `tests/structure.py`, a committed seam map (**new** data file under `tests/`), `grid_fee.py`, `presets.py`, modules with unused loggers | 1 data file | no | `dead_top_level_symbols` held; seam rows identical at introduction | no |

**Classifying new files.**
- **R8-I3's new workflow file** is not INERT. `tests/entities.py` reads every workflow file (it counts the seat-author token across all of them), so the new file enters that script's recorded closure, as `governance.yml` and `release.yml` already have (see the comment block in `tests/closure.py`'s INERT list). Let `closures-autofix` record it (`ci-autofix.md`).
- **R8-I4's seam-map data file** is read by `tests/structure.py`, so it belongs in that script's measured closure. Record it with `closures-autofix` (`ci-autofix.md`: wait for the bot commit). Never run a full `derive_closures.sh` off Linux (`gate-scoping.md`).
- **No other group creates a file.** That is deliberate. Each barrier extends one of these existing scripts: `entities.py`, `features.py`, `finite_boundary.py`, `open_meteo.py`, `doc_claims.py`, `card_browser.mjs`, `mutation_table.py` or `structure.py`.

**Code-owned work and the mandate.** Three groups are code-owned: R8-I3, R8-I1a and R8-P9. All three are in wave 1, so that tvofi's review can land under the thread mandate (until 2026-09-24T13:55Z). If any slips past that time, it waits for the owner's own review. That costs time but blocks nothing else, because no later group depends on them except R8-I1b, which depends on R8-I1a.

**The structure ratchet and parallel merges.** Every row is at zero headroom, and a row that goes *down* must be re-recorded. So parallel coordinator-touching branches will each edit `tests/structure_budgets.json` and collide on it: the #1122 shape.
- Merge them **serially**.
- After each merge, the next branch merges `origin/main` and re-measures. It re-records at the merged tree, and never takes either side's number.
- No group may pad a re-record.

## 4. Waves and ordering

Order key: severity × blast radius × file collision. The five highs go first.

### Wave 1: the five highs, plus the code-owned work (dispatch now)

The groups are R8-P8 (#1513), R8-P11 (#1512), R8-I3 (#1514/#1515/#1516 + #1547), R8-I1a and R8-P9. All five run in parallel.
- **Only R8-P8 touches `coordinator.py`.**
- R8-I3 and the in-flight #1508 both edit CODEOWNERS (one line each). Resolve by union.
- R8-P8 and #1508 both edit `tests/entities.py`. Resolve by union.
- **#1499 sequencing for R8-P11.** #1512 is a different mechanism from #1499's widened part (b):
  - #1512 is the aggregation inside `PeakTracker`, in `tariff.py`.
  - #1499's part (b) changes the kW the no-meter path feeds to `PeakTracker.observe`, in `coordinator.py`.

  The files are disjoint, so the seats can run alongside each other. The merge order is **#1499 first when both are ready**, and R8-P11's bill oracle then gains #1499's no-meter arm. If #1499 has no PR when R8-P11 is ready, R8-P11 merges and the #1499 fixer inherits the oracle. That instruction belongs in #1499's brief when it is dispatched. It has no roster group, so the destination is a `carry-1499.json` written by R8-P11's PR (`finding-propagation.md`: "the stage has no live roster group").
- Root-cause seats for #1514 and #1515 start beside R8-I3.

### Wave 2: the production mediums (after R8-P8 merges)

The groups are R8-P5, R8-P1, R8-P2, R8-P12, R8-P6 and R8-P3.

**Coordinator hunks are disjoint**, so parallel seats are allowed:

| group | coordinator hunk |
|---|---|
| R8-P5 | `_run_system_identification` / `_adopt_system_identification` |
| R8-P6 | `_apply_action` |
| R8-P12 | none: its fix lives in `away.py`, and `async_run_optimization` (the class's longest method) must not grow |
| R8-P1, R8-P2, R8-P3 | none |

Constraints on the wave:
- R8-P5 and R8-P6 are listed `after` R8-P8 only because all three touch the coordinator class and its budget rows. Their hunks never meet.
- **R8-P1 and R8-P2 both edit `sensor.py`.** The hunks are disjoint (the `_finite` block versus the DHW sensor), so they run in parallel and merge serially.
- **R8-P3 is `blocked_on` #1487** (`optimizer.py` `_dhw_coil_wood_forecast`). Start it after #1487 merges, or cut from main and leave that function untouched.
- **Merge order within the wave:** P5, then P6, then P12, then P1, then P2, then P3. The coordinator groups go first so the budget re-records settle early.
- The root-cause seat for #1525 starts beside R8-P5.

### Wave 3: the lows and the instruments

The groups are R8-I5a, R8-I5b, R8-I1b and R8-I4.
- R8-I5a edits the 4 `UpdateFailed` sites. Two of them sit just above `async_run_optimization`, so it runs `after` R8-P12.
- R8-I1b runs after R8-I1a, so the fixed kill rule scores its mutants.
- **R8-I4 runs last, after every coordinator-touching group.** It deletes symbols in many files and freezes the method-to-seam map, which must include every method the earlier groups added.
- The root-cause seat for #1545 starts beside R8-I5a.

**In-flight work this plan does not touch:**
- #1499: it only sequences against it (see wave 1).
- #1487: R8-P3 waits for it.
- #1495 and #1497: card mold warning. R8-P9 edits the WhatIfPanel markup, which is a different region of the card JS; merge serially if both are open.
- #1508 and #1510: the notes in §6 are additions for their authors, not collisions.
- #1501 and #1502: friction issues. Nothing here touches the stats keying.

## 5. Owner rulings, each with a recommended default

| # | question | recommended default | why |
|---|---|---|---|
| 1 | **#1524**: two-zone sysid, refuse or model? | **Refuse to arm** on `two_zone_enabled`, with a named reason in the learning view. A two-zone model becomes a later feature decision. | 0 of 3 two-zone presets adopt, and every experiment overshoots the comfort allowance. A named refusal ends the harm now. Modelling is a feature-sized change that doesn't fit a class PR. |
| 2 | **#1512**: distinct-days default for existing installs | **ON where `peaks_averaged` is above one.** The catalog carries the rule per tariff, and a custom tariff shows the option. | The catalog's Ellevio entry already records three peaks on three days (#926/#968). The published billed peak falls for affected installs, and the release notes should say so. |
| 3 | **#1543**: discarded L-BFGS-B polishes, against the #1463 refusal | **Refuse.** Record it on #1463's refusal as a new quantity measured, and close. | The only lever the finder measured (`--maxls 5`) worsens the objective in 9 of 51 solves. The discard can't be known before the polish runs. The stake is a fraction of gradient evaluations in a lane with no measured user-visible cost. |
| 4 | **#1528**: owner-approved merges without a fix-review verdict | **Require the verdict**, enforced by the orchestrator's existing merge checklist (`orchestrator.md` §11), with no new check (move 4). The alternative is to record an exemption in decision 0011. | The fix-review verdict is one of the design's four "keep" items. The gap is on one approval path, not in the rule. |
| 5 | **#1516**: v* tag ruleset | The owner creates it in repository settings, restricted to the stamp's deploy-key path. | It is a settings change, not a file, so R8-I3 can only ship the ancestry step. |
| 6 | move-4 folds and deferrals | **#1544** folds into #1508 as a cycle-cost invariant. **#1548** is deferred to the next D11 round. **#1549** is deferred to the next D13 round. | #1544: a new budgeted gate lane is new machinery, and the replay runs the real coordinator anyway. #1548: hash-locking installs is new lock machinery for a low finding. #1549: reporting only, and D13 runs every third round. |

A deferral is recorded in the plan's disposition list with its reason (`delivery-status-tracking.md` item 5). Each deferred or refused issue stays open, or is closed with its reason, per the owner's ruling. That choice is the orchestrator's to record, not a seat's.

## 6. Root cause, replay invariants, D14 and rotation hooks

### Root-cause seats (`defect-root-cause.md`, `root-cause.md`)

**Four regressions**, each with its own seat, running beside its fix and never inside it:

| issue | regression of | runs beside |
|---|---|---|
| #1525 | #942's decision that refusals carry a named reason | R8-P5 |
| #1545 | #1466 / #1490 | R8-I5a |
| #1514 | the #1474 fix, #1484 | R8-I3 |
| #1515 | #1402 / #1403 | R8-I3 |

- **Under the moratorium**, each seat's countermeasure should be *this plan's class barrier*, or a recorded decision not to build one. Never a new rule file.
- #1514 and #1515 share a process shape: a D11 fix verified at its own seam and not at its sibling path. One seat may analyse both, but it names a process state (a–d) for each separately.
- **Every other production finding reached a release** (the first trigger). For those, the class PR's body carries the Root cause section:
  - the cause;
  - the process state (for most, (a): no barrier existed for the class);
  - the cost test, with the barrier's standing gate seconds as the countermeasure cost.

  A separate seat is owed only where the class PR can't honestly name its own process state. That stays the reviewer's call.

### Replay invariants to add to #1508

`tests/replay.py` already has `finite`, `unit`, `no_default`, `agreement`, `cycle` and `not_frozen`. The export records `unit_of_measurement` and `device_class`. Additions from round 8:

1. **`price_scale`** (#1513): the published current price equals the recorded price entity's state converted by its recorded unit to the instance currency per kWh, within rounding. The fixture set needs one day from an öre/kWh or MWh-unit sensor, or a synthetic one.
2. **`billed_peak`** (#1512): `billed_peak_kw` and `threshold_kw` equal a bill oracle computed from the recorded meter series under the configured tariff's rule, including distinct days.
3. **`no_phantom_dhw`** (#1527): on a no-DHW install, no published action carries DHW power and no DHW-active flag is on. This needs a no-DHW fixture beside `synthetic-dhw-only.json`.
4. **`sysid_reason`** (#1525): the learning view never publishes a completed experiment with reason ok beside an unchanged heat-loss scale.
5. **`actuation_domain`** (#1526): every service call the cycle issues targets a service the target entity's domain implements. This needs service-call recording in the replay's `hass`.
6. **Hostile-input arms on `finite` and `cycle`** (#1541, #1519):
   - a NaN price step, with `finite` read on all six platforms' attributes, not only sensors;
   - a malformed Open-Meteo body, where the cycle must still return data.
7. **`enabled_follows_input`** (#1542): an entity whose input is configured and readable is not disabled by default.
8. **`cycle_cost`** (the #1544 fold): CPU seconds per replayed cycle, as a ratio to a calibration loop run in the same process, ratcheted one-sided. Nightly only, like the rest of the lane.
9. **`params_persist`** (#1517, optional): a service write injected between cycles survives to the next cycle's solve inputs.

These go into #1508's brief, or a follow-on PR's brief if #1508 merges first. That is a carry, and its destination must exist: #1508 has no roster group, so the destination is `carry-1508.json`.

### D14 and rotation hooks (#1510)

- **Class ledger.** Seed `tools/audit/bugclasses.json` with P11 and P12. Append the round-8 instances to P1, P2, P3, P5, P6, P8, P9, I1, I2, I3, I4 and I5, with the issue numbers above.
- **Barrier status.** Mark a class `barriered` only when its group merges, and name the check.
- **Round-9 D14 picks, by this round's data.**
  - **P2:** it recurs again, 3 instances counting #1523's freeze half. The P2 checks this plan adds are family-specific (DHW capability, learner freeze), so D14 should generalise them.
  - **P1:** 3 instances across store, fetch and publish. D14 verifies the extended `finite_boundary.py` re-finds #1518, #1519 and #1541 at their pre-fix SHAs, as a positive control.
  - **P8:** the unit lint's allow-table is the class's open surface.
- **Rotation `unfinished` seeds from round 8:**
  - D2-s1: capacity envelope, M2;
  - D1-s1: slow-Store race;
  - D3: quiet-window re-take.
- **Driver repairs from the judge's instrument notes** go to #1510's follow-on (design §F1), not to this wave:
  - derive seat temp roots from `TMPDIR`;
  - perturb in memory, or hold the gate lock for edits on disk;
  - pin orjson in `BASELINE.md`;
  - `pip download` writes into the cwd;
  - id shapes: #1510 widens the schema.

## 7. The orchestrator's checklist for this plan

1. **Land the register PR first.** It carries the evidence under `tools/audit/round8/`, a `docs/audit-2026-09.md` round-8 section and a #201 comment. The briefs don't depend on it (they cite `6f58e33`), but the record does.
2. **Land the roster.** A plan PR adds `.claude/workflows/wave-r8-groups.json` from the draft, and the plan's dispositions for the 5 ungrouped issues. Run `node .claude/workflows/brief_lint.mjs` on it and read the exit code and the error lines.
   - Measured here: 0 errors and 0 warnings, in a worktree of `0011bc7` with `6f58e33` resolvable.
   - Control: a brief given a bogus symbol, a bogus path at the tag and a metric literal gave 4 errors and rc 1.
   - The roster carries two non-standard keys, `class` and `wave`, which the wave script ignores. Drop them if a reviewer prefers.
3. **Ask the owner for the six rulings in one message, before 13:55Z.** Also ask for R8-P5's possible `internal_call_edges` raise, pre-cleared as "up to the measured value, confirmed before the push".
4. **Dispatch wave 1** and the #1514/#1515 root-cause seats.
5. **After each merge:** write a delivery row, update the roster's `resume`, and post one #201 comment per state change (`delivery-status-tracking.md`).
