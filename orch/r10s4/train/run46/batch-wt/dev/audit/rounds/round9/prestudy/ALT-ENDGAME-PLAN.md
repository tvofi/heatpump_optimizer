# Round 9 endgame, re-planned (rev 2): review of DRAFT-ENDGAME-PLAN.md, the alternative, and the RCA-1736 follow-up

**Status.**
- **Rev 1** was adopted on 2026-09-28. The roster deltas are on `handoff/audit-r9-fixplan` at `0f1f5263`/`27049219`, and record PR #1749 merged.
- **Rev 2** is for tvofi's decision and is not dispatched.

Rev 2 was written 2026-09-28 by the same cloud review seat, answering tvofi's request after the EG-B0 root-cause analysis. It was measured at origin/main `3490cb16` (v6.7.10), and re-based on 2026-09-29 to `5a2a62ff`. That merge (#1750, record-class merges self-disposing) touches only `policy_lint.mjs` and `stamp.py`. The one measurement it could move, the dead merge-subject arm behind #1041's guard, still reads 0 of 8 at `5a2a62ff`. tvofi asked to:
- screen the codebase for more RCA-1736 shapes and assess their blast radius;
- enumerate, classify and update the bug-class register for every finding of rounds 1–8, together with a permanent mechanism;
- sweep for RCAs conducted but not documented, and RCAs already scheduled;
- conduct the owed RCAs in bulk;
- then revise this plan, the roster and the handover prompt.

**What rev 2 adds:**
- **Shape screen:** `alt/SCREEN-1736-SHAPES.md`. Three read-only screens, then one probe seat. Every lead has a probe arm and a null arm, in `alt/evidence/screen/` (commit `8061ec9b`).
- **Register v2:** `alt/register/`.
  - `bugclasses.v2.json` (commit `53a9bbab`) is built by `build_v2.py` from `rows_v2.tsv`. That is 574 rows for rounds 1–9: 549 counted, 22 unclassified and 3 excluded, including 88 round 1–7 survivors the old source omitted. `build_v2.py --check` rebuilds it and exits 1 on drift.
  - `REGISTER-V2.md` explains every change and lists what tvofi reviews.
  - `RCA-INVENTORY.md` covers all 95 RCAs: where each is recorded, and what is owed.
- **Bulk RCAs:** `alt/rca/RCA-BULK-1..4.md`. They cover P4, P7, P8, P10, I2, N-structure-blind, R-register, #1721, #1545, #1070, the v6.6.0 freeze, the #1041 re-run and N-name-sort, with helpers and outputs beside them.
- **Issues:** #1752 to #1760, filed and read back. Each carries its disposition, and #1736 carries the screen addendum (comment `5879641429`).
- **Roster rev 2:** `ALT-ROSTER.json`, now the **live** roster plus the deltas in §6. `brief_lint.mjs` reports `TOTAL: 0 error(s)`. It is acyclic, with 66 groups.

**Owner direction this plan applies:**
- The rev 1 directions stand: the per-wave, per-PR plan plus the roster; every new fix filed as an issue; B1 after F10.4; B5 opted in; the ratchet stance (§3).
- Rev 2 adds: "screen for these shapes; enumerate and classify the register for rounds 1–8 plus a permanent mechanism; record undocumented RCAs; conduct owed RCAs in bulk; revise plan, roster and prompt".

## 0. The verdict on each draft item

| draft item | verdict | the measured reason | replaced by |
|---|---|---|---|
| EG-0a roster resume sidecar | **keep, out of tree** | The round-9 roster is not on main, so an in-tree sidecar is an orphan tracked file. `delivery-status-tracking.md` and `brief_lint` both read `resume` from the groups file. The wipe is live: the live roster shows 17 of the 27 merged groups as `not-started`. | Fix gen.py to carry each group's existing `resume` forward on regenerate, on the fixplan branch (§6 step 2) |
| EG-0b symbol-anchor 19 line pins | **drop** | The 14 "pins" are `last_measured.*.survivor_lines` in `tests/mutation_budgets.json`, a record of one run that no check reads against the tree. The ledger is already content-anchored. carry-1645's anchors are prose the carry itself tells readers not to trust. It would also have collided with F10.3/F10.5/F10.6 on `mutation_table.py` (principle 2). | none |
| EG-S1 surfaces identity core | **keep, re-scoped and re-timed** | In W3 it collides with the `sensor.py` borrows of F1.7, F6.4 and F1.11. A merged-config helper in `entity.py` would make the core import the surface layer. The surfaces already have `coordinator.effective_config`. It had no identity null control. | **EG-B2** (#1742) |
| EG-C1 clock/helper dedup | **shrink and re-home** | Not F1.6's files (`optimizer.py` is F2's). The "70 raw clock sites" are the P7 behaviour surface, not a dedup (72 real calls by AST). The rounding lead is refuted (§2.2). | Carry **A2 → R9-F1.10** (#1741) |
| EG-O1 `optimizer_dhw.py` | **keep, redesigned and re-sequenced** | In W2 it lands before the optimizer borrows of F1.7, F1.10 and F10.4 (principle 3) and before the F10.4 instrument (principle 1). It is unpriced: the tests call private DHW methods (the design spec counts them exactly), and a per-module duplication detector cannot see duplication a split leaves across modules. | **EG-B5a then EG-B5** (#1743), opted in; **EG-B8** (#1747) first |
| EG-X1 closures.json split | **drop** | `.gitattributes:24` already routes `tests/closures.json` to the `ledgermerge` driver: key-by-key merge, 60 conflicts to 0 on its own replay. Neither pre-study mentions it. | none |
| EG-X2 features.py split | **defer, round-10 pre-study** | Five premises fail (§1.1). | §5 |
| EG-S2 availability rule | **defer** | Unknown versus unavailable is a product ruling (the A3(e)/C15 precedent), and D8-s3-61 is F7.2's to fix. | §5 |
| EG-N1/N2 coordinator seams | **replace** | Not refused on budget grounds (§3). The #193 halts say hub attributes bind the class; B1 removes three of those hubs' per-solve writes, so re-measure and then extract. | **EG-B7** (#1744) |

**New, found by this review:**
- **EG-B0 and EG-B1** (#1736): solve-scoped hub writes, a five-instance recurring class.
- **EG-B3** (#1737): typed payload.
- **A1 → F10.4** (#1738): the ratchet misprices decomposition.
- **EG-B2 and EG-B6** (#1739): collaborator interfaces.
- **A4 → F10.1b and EG-B4** (#1740): store versions.
- **EG-B8** (#1747): the DHW-block replan defect, found while designing B5.
- **Carry → R9-F10.3** (#1748): the per-site ratchet is blind to a move.
- **Deferred:** #1745, typed configuration.

## 1. Review of the draft

### 1.1 Premises that do not hold

**EG-X2's five failed premises:**
1. **Classes are not the unit.** The 112 top-level classes of `tests/features.py` are fakes and stubs (`_T3Store`, `_R9F13Hass`), not test blocks. The units are 196 `R.section` blocks over one shared header: `NOW` is used 110 times, and helpers are defined mid-file and reused 13k lines later. `features.py` takes no CLI arguments.
2. **The ledger pins name the file.** 352 of the 415 `killed_by` ledger pins name `tests/features.py` as their killer (`grep -rh '"killed_by"' tests/mutation_ledger | sort | uniq -c`). The pre-study's "zero formal pins" is wrong, and a split has to re-attribute every one.
3. **Autofix cannot record new scripts.** `ci-autofix.md` says autofix "cannot invent a trace", so the pre-study's "~120-150 closures re-derived by CI autofix" does not happen. Each new script needs a recording.
4. **New scripts must be wired.** A new `tests/*.py` fails `run.sh` as `UNWIRED TEST` unless it is wired in, and `tests/README.md`, which describes the scripts, is code-owned policy.
5. **Touches are not conflicts.** "8 of 8 merges touched it" measures touches. No conflict count exists yet.

**EG-O1, EG-0b and EG-X1:** see the table in §0.

### 1.2 Sequencing against the draft's own principles

- **EG-O1 in W2.** It violates principle 3 against the optimizer borrows of F1.7, F1.10 and F10.4, and principle 1 against F10.4. The source pre-study said "after F2 drains **+ F10.4**".
- **W6 before W7.** W6 (X1/X2) is placed before W7 (F10.4), while the draft's own open question 2 recommends after F10.4.
- **EG-N timing.** EG-N is placed "post-F1.11, pre-register"; the pre-study says "last: after F1 drains, F10.4, register, prune".
- **EG-0b.** "Infra wave, immediately, no lane conflicts" is false (§0).

### 1.3 Costs it did not price

- **Per-module duplication.** `duplication_blocks` compares functions within one module (`structure.py:1080-1085`). Measured: a copy in another module leaves it unmoved, the same copy in its own module moves it by two. A move that splits a duplicated pair across modules therefore lowers it with no duplication removed. That is #1738 arm (a). For EG-B5 specifically, the design keeps both closures in `optimizer.py` and removes them in EG-B5a.
- **Out-of-class reads.** Out-of-class reads of coordinator state are unpriced (measured; #1738 arm (b)). A seam moved into its own module escapes the ratchet in exactly the way `docs/HANDOVER.md:58` refuses.
- **`classes_over_300`.** It scores the extraction itself as the one regression (#750; #1738 arm (c)).
- **EG-S1's registry sensitivity.** The `entity_id` pin is registry-compatibility sensitive, and the draft named no before/after identity snapshot.

### 1.4 Slips

- F1.4 appears in both the merged list and the remaining list.
- 30 PRs at 0.8 PR/h is about 37 h, not 30-34 h. Either way, a throughput figure does not bound a serial chain; §4.3 does.
- The surfaces pre-study's "rationale comment copied verbatim 5×" is one comment plus four pointers.
- Its count of 67 `coordinator.data or {}` sites in `sensor.py` is 66.

### 1.5 The draft's open questions, answered

1. **EG-O1 against F10.2:** a non-question. F10.2 owns `stress.py`, `stress_budgets.json` and `replay.py`, and a pure move changes no solve CPU. The real constraints are the optimizer borrows of F1.7, F1.10 and F10.4, the F10.4 instrument, and B1's interface, so EG-B5 goes after F10.4. The design spec showed B1 is not a prerequisite, so B5 goes before B1.
2. **EG-X2's window:** neither. Round 10, behind a pre-study (§5).
3. **EG-N opt-in:** replaced by EG-B7, a measured go/no-go after B1.
4. **Reviewer seats for EG items:** yes, all of them. That means `fix-review.md` from a detached worktree at the head SHA with the finder's enumerator at both ends. EG-B0 is a `root-cause.md` seat.
5. **Mandate:** W0 and W1 fit inside 2026-09-29T18:15Z. Nothing in lane EG gates an F-lane, so the EG tail can wait for renewal without holding the fixes.

## 2. What the draft misses: filed, verified, dispositioned

| issue | finding (measured at `31394964`) | evidence (`alt/evidence/`) | destination |
|---|---|---|---|
| **#1736** | Each solve writes 23 fields at 26 sites into the live, unfrozen `_opt_config` / `_thermal_params` / `_current_state`; the `finally` unwinds only the 6 setback fields. Four closed issues (#240, #1517, #1529, #1683) plus the configured-target rule are one class across three rounds. | `m1_hub_writes.*` | **EG-B0** root-cause seat now; **EG-B1** refactor |
| **#1737** | The payload is untyped: the coordinator base is unparameterised, and there are 0 TypedDicts. 120 top-level keys are read at 212 sites; `horizon_hours` has no producer (F1.11 fixes that instance). | `m2_payload.*` | **EG-B3** |
| **#1738** | The ratchet misprices decomposition in three ways: (a) per-module duplication, (b) out-of-class reach, (c) `classes_over_300` on extraction. | `m5_dup_control.*`, `m3_ratchet_control.*`, `m7_classes_over_300.out` | Carry **A1 → R9-F10.4** |
| **#1739** | 84 private coordinator reaches across 13 modules (`pump_arbiter.py` 37), including 3 writes; several reads bypass existing public accessors (`effective_config`, `mode`, `optimization_running`). | `m3_reach.*` | **EG-B2** (surfaces), **EG-B6** (collaborators) |
| **#1740** | No store can change version: there is no migration hook, and the stub drops `version`. On a bump, `legionella.py` would re-stamp its last cycle. | `m4_store_version.*`, `ha_storage_dev.py.txt` | Carry **A4 → R9-F10.1b** (P11, `Fixes #1649`); **EG-B4** |
| **#1741** | The step-start clock is defined twice, and the 20 °C tank-room ambient is a literal at 8 sites. | `m6a_step_starts.*` | Carry **A2 → R9-F1.10** |
| **#1742** | Identity is pinned at 9 constructors, and two platforms keep private config copies. | (the grep in the issue) | **EG-B2** |
| **#1743** | The DHW planner core is 19 methods, 1,851 lines, inside the 5,453-line `HeatPumpOptimizer`, and calls no other optimizer method. | `alt/EG-B5-DESIGN.md` | **EG-B5a**, then **EG-B5** (opted in) |
| **#1744** | The coordinator seams should be re-measured once the hubs stop being written per solve. | `tests/structure.py` | **EG-B7**, conditional |
| **#1747** | `_co_optimize`'s replan omits the DHW block. With mostly negative prices it ships DHW heat while blocked and masks the tank-floor breach: 9.22 kWh at a -2.0 shift, against 0 in the control. | `b8_replan_blocked.*` | **EG-B8**, before EG-B5 |
| **#1748** | R9-F10.3's per-site mutation ratchet keys a site by file, so a move counts every moved unpinned site as added. | the prototype at `8eda51a2`; a skeptic simulation | Carry → **R9-F10.3** |
| **#1745** | Configuration is read per site: 281 `.get(CONF_…)` reads of 149 keys in 20 modules, each with its own default and coercion. | (the enumerator in the issue) | **Deferred to round 10** |

### 2.1 Already scheduled, so not filed

- D1-s2-05 (worker reap under the solve lock) and D1-s2-04 (DEBUG-swallowed cycle failures): F1.5.
- D9-s1-03 (sysid fit on the event loop): F1.7.
- `horizon_hours`: F1.11.
- The #1686 instrument: F10.4.

### 2.2 Leads refuted, not filed

- **The `_utc_step_starts` rounding.** Unreachable, because `dt_hours` is `time_step_minutes / 60` (`optimizer.py:1343`): the two clocks agree on all 18 reachable grids across both DST days. What remains is structural (#1741).
- **`CONF_OPTIMIZATION_INTERVAL` in three coercion styles.** They cannot disagree, because the selector (`config_flow.py:1680`) stores a number. What remains is evidence for #1745.
- **`optimizer.py:2861` naive `datetime.now()`.** Unreachable in production: both solve callers (`coordinator.py:5109`, `:10807`) reach `start_time` positionally.

### 2.3 Rev 2: the RCA-1736 follow-up

**Code shape: other objects that carry an operation's value in place.** The full table is in `alt/SCREEN-1736-SHAPES.md`.

| issue | finding (probe vs null at `3490cb16`) | first release | destination |
|---|---|---|---|
| **#1752** (sev:high) | The boost overlay mutates `_current_action` in place. After a cancel, a `no_prices` or `solve_failed` cycle keeps the pump on at 5.0 kW and displace 20 for 90 min; the null gives off / 0 / -3. | v6.4.0 | **EG-B9**, in the F1 serial slot after F1.5 |
| **#1753** | The price tile and fuse advisor borrow the what-if limiter and cache and restore them unconditionally: a spurious rate limit and a lost user answer. | v4.0.0 | **EG-B9** |
| **#1754** | The "already in flight" guard drops the re-solve an input change asked for, so a manual plan applied mid-solve is not actuated for up to one interval. It also inherits the old plan's releases (O2 carries O1's 41). | v3.2.0 | **EG-B10** |
| **#1755** | The worker-fallback streak is per hass, so one entry's success resets another's #783 cap (8 in-process solves against 3 then capped). The trigger is conditional. | v6.4.2 | **EG-B10** |
| (#1736) | Blast radius the hub RCA did not list, carried into **EG-B1**'s brief:<br>- H1: a concurrent cycle publishes the setback into the card editor's pre-fill (day 16.0 vs 21.0).<br>- H3: two writers of `dhw_hourly_draw_pattern`.<br>- H4: the DHW learner's freeze reads a per-solve copy, frozen 6 of 6 cycles in comfort.<br>- H2: mechanism only, no effect reproduced.<br>- P12's argument blindness. | v2.8.0–v4.0.0 | EG-B1 carry |
| — | C3, what-if side effects on published PV and price-known. Cosmetic and self-healing, so not filed. | — | — |

**Process shape: the register and the RCA record.** Measured in `alt/register/REGISTER-V2.md`, `RCA-INVENTORY.md` and `rca/RCA-BULK-2.md` §3.
- At main, 186 register rows sit in no class; round 8 was never classified.
- The round-9 judge re-minted 20 of its 31 new classes and split mechanisms below the trigger.
- No step folds a round in.
- 40 of 82 RCAs are recorded in neither the register nor an issue, and 9 are lost.
- The 14 round-9 class RCA documents survive only in `handoff/audit-r9-plan` history.
- The rounds 1–7 source (`findings.tsv`) omitted **88 survivors**, including all of round 5's first run, and counted 3 non-survivors. The reconciliation adds and excludes them (`register/missing_rows.tsv`, `excluded.tsv`, `RECON.md`). With them, N-name-sort and I2 each reach 3 in round 5.

**The owed RCAs, conducted in bulk.** Four seats: RCA-BULK-1 to 4.

| issue / carry | RCA verdict | destination |
|---|---|---|
| **#1756** | P7: F1.1's DST tracer catches 1 of 3 historical members. Add a config arm and a straddle arm. | **F10.1c**, new, tests only |
| carry | P10: 2304 model-kernel calls on the loop at main (`topology.py:_advisor_replay`). Barrier: kernel calls outside the worker = 0. | **F1.7** (#1658) |
| carry | P8: the one resolver canonicalises the instance label, not the feed. Carry the feed currency; refuse #1657's metric. | **F1.8** (#1657); owner rules on the displayed currency |
| carry | P4: barrier refused on numbers (owner refusals #1293/#1294); the certificate is the detector. | **F2.4** (#1664) |
| carry | I2: a nightly strace oracle; 3 of 8 members reclassified. | **F10.3** (#1663) |
| carry | N-structure-blind: reachability liveness with a planted-shape self-check. #1545: a check for `qs_py_typed_files`. | **F10.4** |
| carry | #1041 silent-zero: the refusal is overturned, so land `merge_shape_guard` in `agreement.mjs`. The class barrier is tvofi's call. | **F11.4** (#1650) |
| **#1757** | #1721, trigger 2: `graders-head-copy` omits the governance graders, which ran under a different principal. | **F11.7**, new |
| **#1758** | The v6.6.0 options-flow freeze, trigger 1: cause not established. Instrument first. | **F10.7**, new; tvofi runs the host profiler |
| **#1759** | R-register: land register v2, then a deterministic fold with a check. | **EG-R0** (data) then **EG-R1** (fold; owner-gated policy) |
| **#1760** | N-name-sort, 8 instances: families are declared nowhere. Declare them, then one contiguity check. | **F7.4**, new |
| record | #1070: the band landed (#1124); the plan row still says "seat in flight". | the record PR corrects the row |

## 3. Ratchet stance

**The owner's direction (2026-09-28):** "The ratchets are not set in stone, and not inherently perfect. The end goal is optimal architecture." It restates the fixplan standing rule, "shape before flatness".

**How this plan applies it:**
- **Fix the instrument where it is wrong.** #1738 corrects the ratchet where it prices decomposition backwards, before any move lands.
- **Name the expected movement.** Every EG item states which budgets it expects to move, and in which direction.
- **Ask for the raise the better shape needs.** Do not avoid the shape to dodge the raise. The gate itself is unchanged: `CLAUDE.md` rule 2 still means the owner's confirmation before the push, and budget-raise-gate at the head. The owner's direction changes the default answer, not the gate.
- **No flatness trades.** No EG item may trade a proven-better shape for flatness.
- **Reinstated on architectural grounds.** The coordinator seams were deferred for architectural reasons (the hub coupling), not budget ones, and are reinstated as EG-B7 behind the change that removes that reason.

## 4. The schedule

### 4.1 Per PR

Generated from roster rev 2 (`ALT-ROSTER.json`) by `gen_table_rev2.py`:
- The `wave` is the dependency depth over open groups; 1 means startable now.
- **Bold** issues are ones the PR fixes (`Fixes #N`); the rest are `Part of #N`.
- 37 groups are open.

| wave | PR | lane | open after-edges | issues (**Fixes**) | owner gate | carry in | what | stage |
|---|---|---|---|---|---|---|---|---|
| 1 | F1.5 | F1 | — | #1644, #1651, **#1670**, **#1676**, **#1682** | — | — | Cycle failures: swallowed errors, late try, reap, P6 defaults, defrost fold | in-review |
| 1 | EG-R0 | EG | — | #1759 | tvofi reviews the move list | — | Register v2 data: rounds 1-9 classified, enum, RCA docs in-tree | not-started |
| 1 | F7.2 | F7 | — | #1644, **#1669** | — | — | Sensors: schedule count, duplicate entity, valve recommendation | fixing |
| 2 | EG-B9 | EG | F1.5 | **#1752**, **#1753** | — | — | Boost overlay acts on a copy; tile and advisor stop borrowing the what-if cache (sev:high actuation) | not-started |
| 2 | F7.4 | F7 | F7.2 | **#1760** | away and sv compressor: rename or allow | — | Declared entity families and one contiguity check (N-name-sort barrier) | not-started |
| 3 | F1.6 | F1 | F1.5, EG-B9 | #1647, **#1659** | — | — | Plausibility bounds and the P1 load-layer barrier | not-started |
| 4 | EG-B10 | EG | EG-B9, F1.6 | **#1754**, **#1755** | — | — | Solve lifecycle: dropped re-solve, override identity, per-entry fallback streak | not-started |
| 4 | F2.4 | F2 | F1.6, F7.2 | #1644, **#1664** | — | P4 refusal | On/off pump threshold at both seams; multi-start seeds | not-started |
| 4 | F9.3 | F9 | F1.6 | **#1647** | — | — | P1 declared-domain barrier: stored fields held to their writers' domains | not-started |
| 5 | F1.7 | F1 | F1.6, F2.4 | #1644, #1649, **#1658** | — | P10 barrier | Coordinator readers across lanes: loop CPU, auth, settlement scale | not-started |
| 5 | EG-B8 | EG | F2.4 | **#1747** | — | — | DHW block ignored by the co-optimisation replan | not-started |
| 6 | F1.8 | F1 | F1.7 | #1644, **#1657** | — | P8 feed currency | Currency and unit (P8) and entry identity | not-started |
| 6 | F10.1b | F10 | F1.7 | **#1649**, #1740 | — | A4 #1740 | Aware-default Home Assistant stub clock | not-started |
| 7 | F1.9 | F1 | F1.8 | **#1660** | — | — | Persisted future instants: the outage decision and the coordinator regressions | not-started |
| 7 | F10.1c | F10 | F10.1b | **#1756** | override-length fix or exemption | — | P7 tracer: config and straddle arms | not-started |
| 7 | F10.2 | F10 | F10.1b | **#1653**, **#1656** | stress.py code-owned; budget rows (B1, B2) | — | CPU gate blind spots; per-solve CPU budget | not-started |
| 7 | F6.3 | F6 | F1.8 | **#1652** | card_browser.mjs code-owned | — | P9 class barrier in the browser lane | not-started |
| 8 | F1.10 | F1 | F1.9, F2.4 | #1645, **#1654**, #1741 | — | A2 #1741 | P3 class barrier: one floor per thermal parameter; comment drift; the fourth on-threshold copy | not-started |
| 8 | F10.3 | F10 | F10.2 | **#1646**, **#1663**, #1748 | gate scripts code-owned | #1748; I2 strace | Owned gate scripts: verdict pins, mutation inventory, child-process closures; I1 barrier | not-started |
| 8 | F6.4 | F6 | F6.3, F1.8 | **#1687** | — | — | Language-aware setup text; raw-thermometer source for staleness gaps | not-started |
| 9 | F1.11 | F1 | F1.10, F6.4 | **#1644**, **#1651** | — | — | Class barriers P2 and P6; horizon_hours and the boost test hook | not-started |
| 10 | EG-B2 | EG | F1.11 | #1739, **#1742** | — | — | Surface identity and public accessors | not-started |
| 10 | F10.4 | F10 | F10.3, F1.11 | **#1645**, #1650, **#1661**, **#1686**, #1738 | B5 raise if honest re-record raises; #1738 arm (c) re-definition | A1 #1738; N-structure-blind; #1545 | Structural ratchet truth: dead members and uncounted helpers; I5 barrier | not-started |
| 11 | EG-B3 | EG | F10.4, EG-B2 | **#1737** | — | — | Typed payload contract | not-started |
| 11 | EG-B5a | EG | F2.4, F10.4 | #1743 | downward re-record | — | One builder for the duplicated solve closures | not-started |
| 11 | F10.5 | F10 | F10.4 | — | new writer identity (0011); code-owned | — | Nightly mutation-kill ledger writer | not-started |
| 11 | F11.4 | F11 | F10.4 | **#1650** | audit-find.js code-owned | merge_shape_guard (#1041) | Class roster readers agree (I4 barrier); owed driver fixes | not-started |
| 12 | EG-B4 | EG | F10.1b, F10.4, EG-B3 | **#1740** | — | — | Store version seam | not-started |
| 12 | EG-B5 | EG | EG-B5a, EG-B8, F1.10, F10.4 | **#1743**, #1748 | opted in; classes_over_300 unless re-defined | — | DHW planner extraction (opted in) | not-started |
| 12 | EG-R1 | EG | F11.4, EG-R0 | **#1759** | policy clauses; audit-verify.js code-owned | — | Deterministic register fold and its check | not-started |
| 12 | F10.6 | F10 | F10.5 | — | mutation_table.py code-owned | — | Comparison-bound mutation operator | not-started |
| 12 | F11.5 | F11 | F11.4 | — | policy text (A1-A9) | — | Round-9 RCA policy text | not-started |
| 13 | EG-B1 | EG | F10.4, F2.4, F10.6, F11.5, EG-B4, EG-B5, EG-B9, EG-B10 | **#1736** | any raise asked before push | H1-H4, P12 (#1736) | Per-solve immutable inputs | not-started |
| 13 | F10.7 | F10 | F10.6 | #1758 | host Profiler run (tvofi) | — | nightly-ha loop-stall heartbeat (v6.6.0 freeze diagnosis) | not-started |
| 13 | F11.7 | F11 | F11.5 | **#1757** | tests.yml code-owned | — | graders-head-copy governance arm under the Actions token | not-started |
| 14 | EG-B6 | EG | EG-B1 | **#1739** | — | — | Collaborator interfaces | not-started |
| 15 | EG-B7 | EG | EG-B1, EG-B6 | **#1744** | classes_over_300 unless re-defined | — | Coordinator seams, measured go/no-go | not-started |

### 4.2 Threads

- **F1, the critical path:** F1.5 → **EG-B9** → F1.6 → *(F2.4)* → F1.7 (+P10 barrier) → F1.8 (+P8) → F1.9 → F1.10 → F1.11.
  - EG-B9 is a behaviour fix that stops unrequested maximum actuation, so it takes the F1 serial slot.
  - It is the one EG group an F lane waits on. EG refactors still never block an F lane.
- **F7 / F2 / F9:** F7.2 now, then **F7.4** (N-name-sort barrier). F2.4 (+P4 refusal) and F9.3 after F1.6.
- **F6:** F6.3 (after F1.8) → F6.4.
- **F10:** F10.1b (after F1.7) → **F10.1c** ‖ F10.2 → F10.3 (+I2) → F10.4 (+N-structure-blind, #1545) → F10.5 → F10.6 → **F10.7**.
- **F11:** F11.4 (+merge_shape_guard; after F10.4) → F11.5 → **F11.7**.
- **EG:**
  - **EG-R0** now, after tvofi reviews the move list.
  - EG-B9 (F1 slot).
  - **EG-B10** after EG-B9 and F1.6.
  - EG-B8 after F2.4.
  - EG-B2 after F1.11.
  - EG-B3, then EG-B4, after F10.4.
  - EG-B5a, then EG-B5.
  - **EG-R1** after F11.4 and EG-R0.
  - EG-B1 after the fix stamp, EG-B5, EG-B9 and EG-B10.
  - Then EG-B6, then EG-B7.
- **Structure-budget writers are serialised** (principle 2): EG-B5a, EG-B5, EG-B1 and EG-B7, as before. EG-B9 and EG-B10 are behaviour fixes. Any `coordinator_loc` raise either needs is asked before the push, and neither is in flight beside those four (they land earlier).

### 4.3 Critical path

- **Fix programme:** F1.5 → EG-B9 → F1.6 → F2.4 → F1.7 → F1.8 → F1.9 → F1.10 → F1.11 → F10.4 → F10.5 → F10.6.
  - That is twelve serial PRs from here; F1.4 is merged. EG-B9 adds one small PR to the chain.
- **After the stamp:** EG-B1 → EG-B6 → EG-B7. F10.7, F11.7 and EG-R1 run beside them and add nothing to the chain.

### 4.4 Windows

**W0, now, inside the mandate** (it expires 2026-09-29T18:15Z):
- F1.5 is in review: PR #1751, CI green at `e3ad93d0`. Merge it, then **EG-B9**.
- F7.2 is being fixed (failing test at `84d99a9b`).
- Apply roster rev 2 (§6 step 2).
- Land the record PR (§6 step 3).
- Post on #201.
- **EG-R0** once tvofi has reviewed the move list.

**W1 to W6:**
- **W1:** F1.5 → **EG-B9** → F1.6 (stamp point (b)); F7.2 → **F7.4**.
- **W2:** F2.4 ‖ F9.3 ‖ **EG-B10**, then EG-B8.
- **W3:** F1.7, then F1.8 ‖ F10.1b.
- **W4:** F1.9 ‖ F6.3 ‖ F10.2 ‖ **F10.1c**, then F1.10 ‖ F6.4 ‖ F10.3.
- **W5:** F1.11, then F10.4 ‖ EG-B2.
- **W6:** F10.5 ‖ F11.4 ‖ EG-B3 ‖ EG-B5a, then F10.6 ‖ F11.5 ‖ EG-B4 ‖ EG-B5 ‖ **EG-R1**.
- **Stamp v6.8.0**, stamp point (c). **EG-B9 should not wait for it:** it is a sev:high actuation fix, so stamp at the next point after it merges. FIX-PLAN's stamp point (b) sits right after F1.6.

**W7:**
- EG-B1 → EG-B6 → EG-B7, with **F10.7** and **F11.7** beside them.
- Then a stamp.

**Endgame, as in rev 1:**
- friction dispositions;
- #1655;
- #1730's row;
- the register PR;
- the stamp;
- the branch prune.

### 4.5 Stamps and fixtures

Unchanged from rev 1. The remaining fixture movers are F1.7, F1.10 and F2.4. The EG refactors claim nothing. EG-B9, EG-B10 and F7.4 move no golden: goldens never boost, never swap an override mid-solve, and do not publish names.

## 5. Deferred and dropped

**Round 10, pre-study only:**
- **The features.py split.** Measure first:
  - actual conflicts, with a replay in the style of `tools/merge/ledger_merge.py --replay`;
  - the dependency graph of the sections on the shared header;
  - the cost of re-attributing the 352 `killed_by` pins;
  - `run.sh` wiring and the `tests/README.md` policy edit.
  Candidate shape: about ten files, grouped by lane-owned module, not one per class.
- **#1745, typed configuration.** After EG-B1.
- **EG-S2.** Only after the owner rules on unknown versus unavailable.
- **The 121 `getattr(self, "_ctx", self)` sites** beside the `_hub` facade (`coordinator.py:1382`). Measure their effect on the cut metrics (#510, `docs/HANDOVER.md:316`) after #1738 has landed.

**Dropped:** EG-0b, EG-X1, and the 70-site clock migration.

## 6. Adopting rev 2

Rev 1's steps are done (roster deltas at `0f1f5263`/`27049219`, record PR #1749). Rev 2 needs:

1. **Approval.** tvofi approves or amends this file, roster rev 2, and the owner decisions in §7.
2. **The roster.** Replace `.claude/workflows/wave-r9-groups.json` on `handoff/audit-r9-fixplan` with `ALT-ROSTER.json`.
   - If the live file has moved since `27049219`, apply the deltas `build_roster_rev2.py` states in its docstring instead. It takes the live file and ALT's rev-1 resumes as its inputs:
     - (a) resume truthing. The live file shows 17 merged groups as `not-started`, and it has EG-B0's `rca-done` on EG-B1.
     - (b) the carries into R9-EG-B1, F1.7, F1.8, F2.4, F10.3, F10.4 and F11.4.
     - (c) the new groups: EG-B9, EG-B10, EG-R0, EG-R1, F7.4, F10.1c, F10.7 and F11.7.
     - (d) the edges: F1.6 after EG-B9; EG-B1 after EG-B9 and EG-B10.
   - Then assert that every group merged on main reads `done`. The 17-group regression reappeared after rev 1's adoption, so a regeneration or merge is still dropping them.
   - Lint the result.
3. **The record PR** (the `hpo-author` App, via `tools/audit/app_push.sh`):
   - disposition #1752 to #1760 in the plan of record, and correct #1070's row;
   - add carry files only if any destination stage has started before the roster lands (none has at `3490cb16`).
4. **EG-R0.** It is a separate data PR, after tvofi has reviewed the move list. It copies `alt/register/bugclasses.v2.json` and the enum, and moves the RCA documents into `tools/audit/rca/`.
5. **#201.** One comment, posted with `gh_comment.py` and read back.
6. **Dispatch** per §4.

## 7. Owner decisions rev 2 needs

| # | decision | where it gates |
|---|---|---|
| 1 | Review register v2's move list and low-confidence placements (`rows_v2.tsv`, `REGISTER-V2.md`). | EG-R0 merge |
| 2 | P1's mechanism text: widen it, or mint an input-boundary class. | EG-R0 |
| 3 | Do RCA-seat-found instances count (P9 12 vs 5)? | EG-R0 / EG-R1 |
| 4 | Are round 5's two runs one round? If so, N-name-sort hit 3 in one round. | register |
| 5 | Policy clauses: `judge.md` reuse-before-mint; the cross-round trigger in `defect-root-cause.md`; where an RCA is recorded; `D8.md` declared families. | EG-R1 |
| 6 | Displayed currency follows the price feed? | F1.8 |
| 7 | Record the P4 refusal on #1664. | F2.4 |
| 8 | N-silent-zero class barrier (the perturb-to-red registry): build or refuse. | F11.4 |
| 9 | DST: fix the 20 h override that lasts 21 h, or name an exemption. | F10.1c |
| 10 | The `away` and Swedish `compressor` family splits: rename or allow. | F7.4 |
| 11 | Run HA's Profiler on the host across an options round-trip. | F10.7, any time |
| 12 | EG-H2: judge quiet periods against the configured band or the effective band. | EG-B1 |
