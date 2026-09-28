# Round 9 endgame, re-planned: review of DRAFT-ENDGAME-PLAN.md and the alternative

**Status: for tvofi's decision, not dispatched.** Written 2026-09-28 by a cloud review seat, with the owner
directing it in session. Measured at origin/main `31394964` (#1734). The handoff branch was at `694af34c`.

**What ships with it:**
- **Roster:** `ALT-ROSTER.json`, beside this file. `brief_lint.mjs` reports `TOTAL: 0 error(s)` against
  origin/main with the round-9 evidence refs fetched. The live roster on `handoff/audit-r9-fixplan` is untouched.
- **Evidence:** `alt/evidence/` (commit `a163db90`). Every lead has a measured arm and a null control; its
  README indexes them.
- **Carry drafts:** `alt/carries/`, all four linted in-tree against main `686239d2`.
- **EG-B5 design spec:** `alt/EG-B5-DESIGN.md`. It covers the DHW planner split tvofi opted in to: two mapping seats and one skeptic seat, with every correction applied.
- **Issues:** #1736 to #1745, #1747 and #1748, each body read back against the file sent (`alt/issues/readback.out`).
- **Branch:** this plan lives on `handoff/audit-r9-alt`. `handoff/audit-r9-plan` carries only the resume doc (owner, 2026-09-28).

**Owner direction this plan applies:**
- The deliverable is a per-wave, per-PR plan sequenced with the running programme, plus the roster.
- Every new fix is filed as an issue.
- B1 goes in, after F10.4.
- **B5, the DHW planner split, goes in** (2026-09-28). Its design spec sequences it after F10.4 and before B1, preceded by the EG-B8 fix and the EG-B5a dedupe (§4).
- "The ratchets are not set in stone and not inherently perfect; the end goal is optimal architecture." See §3.

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

Generated from `ALT-ROSTER.json`. The `wave` is the dependency depth over open groups, where 1 means startable now. **Bold** issues are ones the PR fixes (`Fixes #N`); the rest are `Part of #N`.

| wave | PR | lane | open after-edges | issues (**Fixes**) | owner gate | carry in | what | stage |
|---|---|---|---|---|---|---|---|---|
| 1 | F1.5 | F1 | — | #1644, #1651, **#1670**, **#1676**, **#1682** | — | — | Cycle failures: swallowed errors, late try, reap, P6 defaults, defrost fold | not-started |
| 1 | EG-B0 | EG | — | #1736 | — | — | Root-cause seat: solve-scoped hub writes (not a PR) | not-started |
| 1 | F7.2 | F7 | — | #1644, **#1669** | — | — | Sensors: schedule count, duplicate entity, valve recommendation | not-started |
| 2 | F1.6 | F1 | F1.5 | #1647, **#1659** | — | — | Plausibility bounds and the P1 load-layer barrier | not-started |
| 3 | F2.4 | F2 | F1.6, F7.2 | #1644, **#1664** | — | — | On/off pump threshold at both seams; multi-start seeds | not-started |
| 3 | F9.3 | F9 | F1.6 | **#1647** | — | — | P1 declared-domain barrier: stored fields held to their writers' domains | not-started |
| 4 | F1.7 | F1 | F1.6, F2.4 | #1644, #1649, **#1658** | — | — | Coordinator readers across lanes: loop CPU, auth, settlement scale | not-started |
| 4 | EG-B8 | EG | F2.4 | **#1747** | — | — | DHW block ignored by the co-optimisation replan | not-started |
| 5 | F1.8 | F1 | F1.7 | #1644, **#1657** | — | — | Currency and unit (P8) and entry identity | not-started |
| 5 | F10.1b | F10 | F1.7 | **#1649**, #1740 | — | A4 #1740 | Aware-default Home Assistant stub clock | not-started |
| 6 | F1.9 | F1 | F1.8 | **#1660** | — | — | Persisted future instants: the outage decision and the coordinator regressions | not-started |
| 6 | F10.2 | F10 | F10.1b | **#1653**, **#1656** | stress.py code-owned; budget rows (B1, B2) | — | CPU gate blind spots; per-solve CPU budget | not-started |
| 6 | F6.3 | F6 | F1.8 | **#1652** | card_browser.mjs code-owned | — | P9 class barrier in the browser lane | not-started |
| 7 | F1.10 | F1 | F1.9, F2.4 | #1645, **#1654**, #1741 | — | A2 #1741 | P3 class barrier: one floor per thermal parameter; comment drift; the fourth on-threshold copy | not-started |
| 7 | F10.3 | F10 | F10.2 | **#1646**, **#1663**, #1748 | gate scripts code-owned | #1748 | Owned gate scripts: verdict pins, mutation inventory, child-process closures; I1 barrier | not-started |
| 7 | F6.4 | F6 | F6.3, F1.8 | **#1687** | — | — | Language-aware setup text; raw-thermometer source for staleness gaps | not-started |
| 8 | F1.11 | F1 | F1.10, F6.4 | **#1644**, **#1651** | — | — | Class barriers P2 and P6; horizon_hours and the boost test hook | not-started |
| 9 | EG-B2 | EG | F1.11 | #1739, **#1742** | — | — | Surface identity and public accessors | not-started |
| 9 | F10.4 | F10 | F10.3, F1.11 | **#1645**, #1650, **#1661**, **#1686**, #1738 | B5 raise if honest re-record raises; #1738 arm (c) re-definition | A1 #1738 | Structural ratchet truth: dead members and uncounted helpers; I5 barrier | not-started |
| 10 | EG-B3 | EG | F10.4, EG-B2 | **#1737** | — | — | Typed payload contract | not-started |
| 10 | EG-B5a | EG | F2.4, F10.4 | #1743 | downward re-record | — | One builder for the duplicated solve closures | not-started |
| 10 | F10.5 | F10 | F10.4 | — | new writer identity (0011); code-owned | — | Nightly mutation-kill ledger writer | not-started |
| 10 | F11.4 | F11 | F10.4 | **#1650** | audit-find.js code-owned | — | Class roster readers agree (I4 barrier); owed driver fixes | not-started |
| 11 | EG-B4 | EG | F10.1b, F10.4, EG-B3 | **#1740** | — | — | Store version seam | not-started |
| 11 | EG-B5 | EG | EG-B5a, EG-B8, F1.10, F10.4 | **#1743**, #1748 | opted in; classes_over_300 unless re-defined | — | DHW planner extraction (opted in) | not-started |
| 11 | F10.6 | F10 | F10.5 | — | mutation_table.py code-owned | — | Comparison-bound mutation operator | not-started |
| 11 | F11.5 | F11 | F11.4 | — | policy text (A1-A9) | — | Round-9 RCA policy text | not-started |
| 12 | EG-B1 | EG | F10.4, F2.4, F10.6, F11.5, EG-B0, EG-B4, EG-B5 | **#1736** | any raise asked before push | — | Per-solve immutable inputs | not-started |
| 13 | EG-B6 | EG | EG-B1 | **#1739** | — | — | Collaborator interfaces | not-started |
| 14 | EG-B7 | EG | EG-B1, EG-B6 | **#1744** | classes_over_300 unless re-defined | — | Coordinator seams, measured go/no-go | not-started |

### 4.2 Threads

The lanes run as they do today. The EG lane is new and owns no file until its after-edges merge.

- **F1, the critical path:** F1.4 (merged as #1735) → F1.5 → F1.6 → *(F2.4)* → F1.7 → F1.8 → F1.9 → F1.10 (+A2) → F1.11.
- **F7 / F2 / F9:** **F7.2 starts now.** Both its edges are merged, and it gates F2.4. Then F2.4 (after F1.6) and F9.3 (after F1.6).
- **F6:** F6.3 (after F1.8) → F6.4.
- **F10:** F10.1b (+A4; after F1.7) → F10.2 → F10.3 → F10.4 (+A1; after F1.11) → F10.5 → F10.6.
- **F11:** F11.4 (after F10.4) → F11.5.
- **EG:**
  - EG-B0 now; it is a seat, not a PR.
  - EG-B2 after F1.11.
  - EG-B8 right after F2.4.
  - EG-B3, then EG-B4, after F10.4.
  - EG-B5a (after F2.4 and F10.4), then EG-B5 (after EG-B5a, EG-B8, F1.10 and F10.4). The preconditions are
    in `alt/EG-B5-DESIGN.md` §7.
  - EG-B1 after the fix stamp and EG-B5.
  - Then EG-B6, and last EG-B7.
  - EG-B5a, EG-B5, EG-B1 and EG-B7 are all structure-budget writers, and never two in flight at once
    (principle 2).

### 4.3 Critical path

- **Fix programme:** F1.4 → F1.5 → F1.6 → F2.4 → F1.7 → F1.8 → F1.9 → F1.10 → F1.11 → F10.4 → F10.5 → F10.6, twelve serial PRs.
- **With the EG lane:** EG-B1 → EG-B6 → EG-B7 adds three after the stamp. EG-B5a → EG-B5 runs beside F10.5 and F10.6 and adds nothing to the chain.
- **Calendar time** is the sum of each of those PRs' fix, review and merge cycles. The draft's 0.8 PR/h is a throughput figure and does not shorten this chain.

### 4.4 Windows

**W0, now, inside the mandate:**
- F1.4 merged as #1735 (`686239d2`). F1.5's branch is cut.
- Start F7.2.
- Dispatch the EG-B0 seat.
- Do the gen.py resume carry-forward (§6 step 2).
- Land the record PR carrying the four carry files and the dispositions of #1736 to #1745, #1747 and #1748 (§6 step 3). The #1748 carry must be in the tree before F10.3 starts.
- Post on #201.

**W1 to W6:**
- **W1:** F1.5 → F1.6. That is stamp point (b) in FIX-PLAN, after the P1 barrier.
- **W2:** F2.4 ‖ F9.3, then EG-B8.
- **W3:** F1.7, then F1.8 ‖ F10.1b.
- **W4:** F1.9 ‖ F6.3 ‖ F10.2, then F1.10 ‖ F6.4 ‖ F10.3.
- **W5:** F1.11, then F10.4 ‖ EG-B2.
- **W6:** F10.5 ‖ F11.4 ‖ EG-B3 ‖ EG-B5a, then F10.6 ‖ F11.5 ‖ EG-B4 ‖ EG-B5. EG-B5 may ship in v6.8.0; it does not gate the stamp.
- **Stamp v6.8.0:** stamp point (c). It releases the round's fixes before any structural refactor lands.

**W7, the structural window:**
- EG-B1.
- Then EG-B6.
- Then EG-B7.
- Then a stamp.

**Endgame, as in the draft:**
- the friction dispositions (#1640, #1700, #1706, #1712);
- closing #1655;
- #1730's row;
- the register PR (harnesses, salvage keepers, seat tooling, generator, the pre-study reports and this review);
- the stamp;
- the branch prune, last.

### 4.5 Stamps and fixtures

The FIX-PLAN rule is unchanged: when a fixture mover claims drift, no new branch is cut between its merge and its stamp. The remaining movers are F1.7, F1.10 and F2.4.

The EG PRs claim nothing. Byte-identical goldens are their null control, and a golden that moves means the PR is not the pure refactor it says it is.

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

## 6. Adopting this plan

1. **Approval.** tvofi approves or amends this file and `ALT-ROSTER.json`.
2. **The roster.**
   - Replace `.claude/workflows/wave-r9-groups.json` on `handoff/audit-r9-fixplan` with `ALT-ROSTER.json`.
   - If the live file moved in the meantime, apply ALT's three deltas to it instead: the truthed `resume` fields, the carries into R9-F1.10, R9-F10.1b, R9-F10.3 and R9-F10.4, and lane EG.
   - Before any regeneration, make gen.py carry each group's existing `resume` forward. Otherwise it wipes them again, which is the EG-0a bug; alternatively, stop regenerating.
   - Re-run `brief_lint.mjs` on the result.
3. **The record PR** (by the `hpo-author` App, via `tools/audit/app_push.sh`):
   - add `alt/carries/carry-1686.json`, `carry-1654.json` and `carry-1646.json` under `.claude/workflows/`;
   - append `alt/carries/carry-1649.entry-to-append.json` to the existing `carry-1649.json` (a full copy made at `31394964` is beside it; copy it over only if main's file is unchanged);
   - disposition #1736 to #1745, #1747 and #1748 in the plan of record (`delivery-status-tracking.md` step 5).
4. **#201.** One comment, posted with `gh_comment.py` and read back.
5. **Dispatch** per §4. EG PRs follow `fixer.md` / `fix-review.md` like any fix PR, and EG-B0 follows `root-cause.md`.
