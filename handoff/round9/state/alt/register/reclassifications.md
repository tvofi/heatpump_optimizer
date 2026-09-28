# Reclassifications, register v1 -> v2 (phase A1)

Scope: every surviving audit finding of rounds 1-9 plus every instance counted beyond
the judged findings, one row each in `register_rows.tsv` (486 rows). The counting rule
is judged survivors plus counted instances (`.claude/rules/defect-root-cause.md:88-89`,
`.claude/workflows/audit-verify.js:211-214`). Nothing below is applied to R1-7: a
flagged row keeps its v1 `class_id` and carries `FLAG-><id>` in its note, and
`derive.py` shows the effect of applying every flag in its "flags" column and its
"FLAG move applied" view. Tables are generated from `src/build.py` (`src/gen_tables.py`).

Sources: R1-7 `12743bf7:handoff/round8/findings.tsv` (285 rows; v1 instances equal it
row for row, derive.py confirms); R8 `3490cb16:tools/audit/round8/JUDGE.json` + the
register table at `docs/audit-2026-09.md:1998-2048` (#1512-#1549; GitHub labels carry
no class, checked on #1523/#1539); R9 `bad458a38d:tools/audit/round9/judge/JUDGE.json`
+ `CLASSES.json`, sweeps S1-S7 (`handoff/audit-r9-sweep-s1..s7`), the class-to-issue
table and the beyond-judged instance table of
`27049219a8:handoff/round9/FIX-PLAN.md:797-824,825-877` (branch
`handoff/audit-r9-fixplan`), whose roster already named every judge class with a short
`N-` id; those ids are the `r9_alias` values.

## 1. R1-7 rows I would move (flag only)

30 flags. `none` = no existing or v2 class fits (architecture size, HA quality-scale
code conformance, recorder payload); these need a decision, not a guess.

| round | id | v1 class | would move to | conf | reason |
|---|---|---|---|---|---|
| R3 | D1-03 | P7 | N-future-instant | med | backward clock step makes a recorded instant lie ahead of now; the watchdog trusts it (in-process, not persisted) |
| R2 | D8-04 | P2 | N-name-sort | med | alphabetical order splits entity families: name-sort mechanism, no predicate involved |
| R3 | D8-03 | I5 | N-name-sort | med | names mix leading/trailing nouns so sort splits families |
| R4 | D8-01 | P2 | N-name-sort | med | alphabetical order interleaves foreign entities in family spans |
| R5 | D8-01 | P2 | N-name-sort | med | card-addressed sensors sort into 3 entity-id blocks |
| R5 | D8-02 | I5 | N-name-sort | med | Swedish names drop family lead tokens: R9 D8-s3-01 split in sv |
| R3 | D9-02 | I1 | N-restart | med | fuse advisor rate limit memory-only, lost at restart: state not surviving restart |
| R2 | D1-05 | P6 | N-shared-config | med | async_simulate shares live DefrostDerate/gains/dhw_windows with the loop mid-solve |
| R1 | D9-01 | P10 | N-solve-recompute | med | batched gradient bypassed: avoidable solve CPU, not event-loop starvation |
| R2 | D9-03 | P10 | N-solve-recompute | med | batched jac re-evaluates f(x): avoidable recomputation in the solve |
| R4 | D9-05 | P10 | N-solve-recompute | high | cost recomputed in a per-row Python loop: exactly R9 D9-s1-01 shape |
| R5 | D9-05 | I1 | N-solve-recompute | high | #1208 polish-every-candidate cost share: same seam as R7 D9-02 / R8 D9-s1-01; not a gate-blind (I1) finding |
| R7 | D9-02 | P10 | N-solve-recompute | high | polish-per-candidate _lbfgsb_restart share: same seam as R8 D9-s1-01 |
| R2 | D7-06 | I5 | N-structure-blind | low | dead defs no gate script starts: dead production members |
| R6 | D7-02 | I5 | N-structure-blind | med | structure.py's dead-symbol check reads 0 over a 379-line dead method: metric blind, not docs drift |
| R7 | D2-02 | I1 | N-structure-blind | low | unreachable duplicate return line: dead code, not a mutation-kill miscount |
| R1 | D7-03 | P10 | P2 | low | scalar vs batch physics duplicated (one fact computed twice); not loop starvation |
| R2 | D10-01 | I5 | P2 | med | no duplicate-entry guard: same defect as R1 D10-03 (P2) and R9 D10-s1-01 (P2), filed here as I5 |
| R2 | D10-15 | I5 | P2 | low | two energy sensors lack the ENERGY device class their siblings carry |
| R5 | D12-01 | P8 | P2 | med | ECL110 commands published where no ecl110 key: an "is configured" gate missing at a sibling seam, not unit precedence |
| R2 | D2-02 | P8 | P3 | low | COP law non-monotone with a mixing valve: physics formula, not currency/unit precedence |
| R4 | D2-04 | P8 | P3 | med | COP floor applied before Carnot/DHW factors: a floor applied inconsistently, not currency/unit |
| R6 | D2-01 | P2 | P3 | low | hard-edged buckets make COP step across 1e-9 C: discontinuity like R2 D2-05/R4 D2-03 (P3) |
| R4 | D7-02 | P3 | P5 | low | sysid sizing model ignores the house slab constants: model-structure mismatch like R4 D7-01 |
| R1 | D10-01 | I5 | none | low | HA quality-scale code conformance (service registration), not docs drift |
| R1 | D10-02 | I5 | none | low | HA quality-scale code conformance (runtime_data), not docs drift |
| R1 | D10-12 | I5 | none | low | missing diagnostics platform: code conformance, not docs drift |
| R1 | D7-01 | P2 | none | low | coordinator size/coupling: architecture finding, no mechanism class fits (candidate: coordinator concentration) |
| R2 | D7-05 | P2 | none | low | coordinator size/coupling: architecture finding, no mechanism class fits |
| R7 | D9-01 | P6 | none | low | recorder payload redundancy: an efficiency finding with no producer/consumer key mismatch |


Also noted, not flagged: v1 `P1` per-round counts in `classes.md` (R1 2, R2 1, R3 1, R5 2,
R6 2) disagree with its own `findings.tsv` (R4 2, R5 3 as well); and `classes.md`'s
headline per-round counts (R1 59, R2 75, R3 40, R4 37, R5 48, R6 31, R7 31 = 321) are not
its 285 rows (R1 42, R2 63, R3 35, R4 36, R5 48, R6 30, R7 31). The rows are what v1
seeded, so v2 keeps them; the headline is the stale number.

## 2. Round 8, first classification (39 survivors)

Round 8's judge recorded only the stop-rule class (bug/hygiene); no mechanism class
was ever assigned. 43 judged: 29 verified + 10 weakened survive, 3 refuted, 1 merged
(D11-s1-02 into D11-s2-01, not counted). D0-s1-01 survived but was not filed
(duplicate of the owner's refusal #1293); it is counted. No round-8 class sweep ran, so
R8 has no sweep rows.

| id | issue | class | conf | reason |
|---|---|---|---|---|
| D3-s1-01 | #1521 | I1 | high | refusal rc scored as a kill: R7 D3-02 shape |
| D3-s2-01 | #1532 | I1 | high | clamp deletion survives the closure |
| D3-s2-02 | #1533 | I1 | high | boundary mutant survives both service call sites |
| D7-s2-03 | #1540 | I1 | high | branch disabled, no driver notices |
| D9-s2-01 | #1544 | I1 | med | no budgeted gate covers the coordinator cycle: perf-gate blindness, I1 by R2 D9-02/R4 D9-06 precedent |
| D3-s1-02 | #1531 | I2 | med | cache key's input set diverges from what the capture reads |
| D11-s1-01 | #1514 | I3 | high | body edit re-creates skipped required check runs |
| D11-s1-03 | #1547 | I3 | high | Stop hook misses the staged policy change |
| D11-s2-01 | #1515 | I3 | high | required checks run unowned PR-editable code (merged: D11-s1-02) |
| D11-s2-02 | #1516 | I3 | high | release publishes a ref not on main |
| D11-s2-03 | #1548 | I3 | high | install commands not hash-pinned: R4 D11-07 shape |
| D13-s1-02 | #1528 | I3 | high | owner-approved merges bypass the fix-review verdict |
| D13-s1-01 | #1549 | I4 | high | two yield definitions disagree: R6 D13-01/02 shape |
| D10-s1-01 | #1545 | I5 | high | quality_scale.yaml claim contradicted by code |
| D10-s1-02 | #1546 | I5 | high | quality_scale.yaml claim contradicted by 4 raise sites |
| D4-s2-01 | #1534 | I5 | high | untranslated sv label: translation coverage, I5 by R1-7 precedent |
| D5-s1-01 | #1535 | I5 | high | README diagram vs prose numbering |
| D5-s2-01 | #1536 | I5 | high | comments name symbols that do not exist |
| D6-s1-01 | #1537 | I5 | high | README requirements omit threadpoolctl |
| D1-s1-01 | #1517 | N-shared-config | high | away-setback unwind in the solve finally reverts a concurrent set_thermal_parameters write; same mechanism as R9 D1-s3-04 |
| D1-s1-02 | #1529 | N-shared-config | med | diagnose service reads live state on the executor; alt P2 (the button path deepcopies, the service path does not) |
| D9-s1-01 | #1543 | N-solve-recompute | high | per-candidate polish spends gradients on discarded results: same seam as R7 D9-02 |
| D7-s2-01 | #1538 | N-structure-blind | med | structure.py's name-based dead-code screen reads 0 over 12 dead symbols |
| D7-s2-02 | #1539 | N-structure-blind | med | a pure rename moves the cross_seam_edges ratchet: same metric blindness as R9 D7-s1-01 |
| D1-s2-01 | #1518 | P1 | high | non-numeric ledger leaf passes from_dict |
| D1-s3-01 | #1519 | P1 | med | wrong-shaped Open-Meteo member raises out and fails the cycle: malformed live-feed value, precedent R5 D1-07 (P1) |
| D12-s1-01 | #1526 | P2 | high | domain accepted at assign_entity, actuation assumes switch: R9 D12-s2-02 shape |
| D12-s1-02 | #1527 | P2 | high | boost switch created without the has-DHW gate its siblings honour |
| D2-s1-01 | #1520 | P2 | med | DHW planner prices COP at current humidity while physics uses the forecast: one fact decided twice |
| D2-s1-02 | #1530 | P2 | med | DHW COP keeps its own lift law beside flow_lift_factor: two laws for one fact |
| D7-s1-01 | #1523 | P2 | high | sysid experiment ignores _learning_frozen the learners honour: R1 D7-05 shape |
| D8-s1-01 | #1541 | P2 | med | non-finite scrub on the sensor base only, not the shared entity base; alt P1 (R2 D8-02 precedent) |
| D8-s2-02 | #1542 | P2 | high | static enabled-default where the gating input is configured: entity default-enabled family |
| D2-s2-01 | #1512 | P3 | low | PeakTracker bills top-k windows not top-k days; alt P2 (catalog rule vs tracker rule) or P11 (external tariff modelled from the code) |
| D0-s1-01 | not filed | P4 | high | ftol=1e-6 stop short; survived, not filed: duplicate of owner refusal #1293 |
| D7-s1-02 | #1524 | P5 | high | one-room sysid cannot identify two-zone plant; #1524, which main's P5 barrier cites |
| D7-s1-03 | #1525 | P6 | med | refusal path writes no reason; published view falls back to completed/ok (#1525); alt P2 |
| D2-s2-02 | #1513 | P8 | high | entity price unit never read: öre/kWh and SEK/MWh reach the plan at 83x/829x |
| D4-01 | #1522 | P9 | med | keyboard Tab order: card a11y, stretches P9 (see mechanism_note) |


## 3. Round-9 re-maps (judge `new:` class -> v2 id)

Rule applied: re-map to an existing id when the mechanism fits it, or when R1-7 already
filed the same mechanism under that id (the register's own precedent); mint only when
neither holds. Reasons, by target:

- **P10** <- N-loop-cpu: the judge re-minted P10 (event-loop starvation by CPU work);
  inline-on-loop instead of a GIL thread is the only difference (mechanism_note).
- **I1** <- N-cpu-gate-blind: perf-gate blindness is already I1 in R1-7 (R2 D9-02,
  R4 D9-06, R5 D9-07, R6 D9-02) and R8 D9-s2-01.
- **P1** <- N-plausibility, N-min-gap, N-service-clamp: an unguarded value crossing an
  input boundary; R1-7 P1 already holds live-input rows (R5 D1-06, R5 D1-07). The
  judge's own P1 includes out-of-domain rows (D1-s5-02). Low confidence for N-min-gap
  and N-service-clamp (alternative for the latter: P2, siblings are vol.Range-clamped).
- **P2** <- N-dup-entity, N-availability (entity default-enabled/availability is P2's
  chain: R3 D8-02, R5 D8-03, R6 D8-01, R7 D8-02), N-late-try (the try fences the
  sibling calls, not `_ensure_worker`; the judge's D1-s2-51/91 are the same fence shape
  in P2), N-menu (the options-flow menu is state-gated, the config-flow one is not: S7's
  guarded sibling).
- **P3** <- N-sign-floor (a floor breaking the identity its siblings keep), N-euler-coupled
  (R2 D2-01, an Euler sub-step defect, is P3), N-clamp-range (a clamp constant sized
  against the wrong curve). The last two are low confidence.
- **P5** <- N-fit-integrator: model-structure mismatch in the sysid fit is P5 in R1-7
  (R1 D7-02, R4 D7-01). Consequence: P5 is barriered, so this instance owes the barrier
  (F4.2 already carried both).
- **P6** <- N-debug-swallow: swallowed failures are P6 in R1-7 (R1 D10-07, R2 D10-04).
- **P9** <- N-keyboard: card accessibility rule not reaching a control; with R8 D4-01.
- **I5** <- N-escape, N-service-icons, N-language (the three translation/icon classes:
  coverage was I5 in R1-7, R1 D10-13, R4 D8-02, R5 D8-02) and N-markdown (docs render
  defects are I5 in R1-7, R2 D5-03, R3 D5-03).
- **N-structure-blind** <- N-dead-member + N-structure-blind: one mechanism, the
  structural metric measuring a name proxy (R8 D7-s2-01 is both: the dead-code screen
  reads 0 over dead symbols). Kind instrument; the dead members themselves are the
  evidence, as in R6 D7-02.
- Kept as their own id (roster alias = v2 id): N-solve-recompute, N-future-instant,
  N-restart, N-shared-config, N-name-sort, N-approval-rebuy, N-finally-return,
  N-step-grid, N-reap-lock, N-staleness (section 5).

| judge class (alias) | roster id | v2 id | conf | members |
|---|---|---|---|---|
| CPU gate blind to a regression outside its sampled work | N-cpu-gate-blind | I1 | med | D9-s2-02, D9-s2-03, D9-s2-71 |
| translation leaf double-escaped | N-escape | I5 | med | D4-s2-03 |
| text producer takes no language parameter | N-language | I5 | med | D4-s2-81 |
| markdown the renderer misplaces | N-markdown | I5 | med | D5-s1-04 |
| missing icons.json services block | N-service-icons | I5 | high | D4-s2-08 |
| an approval bound to an exact head is re-bought on a diff-identical move | N-approval-rebuy | N-approval-rebuy | med | D13-s1-02 |
| return inside finally | N-finally-return | N-finally-return | med | D7-s3-51 |
| persisted future instant trusted without bound | N-future-instant | N-future-instant | high | D1-s1-04, D1-s3-05, FI-sw1, FI-sw2, FI-sw3, FI-sw4, FI-sw5, FI-rca1 |
| an entity family whose names do not lead with a shared token splits under the name sort | N-name-sort | N-name-sort | high | D8-s3-01 |
| shutdown reap waits on the lock a solve holds | N-reap-lock | N-reap-lock | low | D1-s2-05 |
| user state not surviving restart | N-restart | N-restart | high | D1-s2-52, D1-s2-53 |
| solve-scoped mutation of shared live config seen by a concurrent reader | N-shared-config | N-shared-config | high | D1-s3-04 |
| avoidable interpreter-bound recomputation in the solve | N-solve-recompute | N-solve-recompute | high | D9-s1-01, D9-s1-02, D9-s1-04, D9-s1-71, RC-sw1, RC-rca1, RC-rca2 |
| staleness limit shorter than a report-on-change sensor's quiet interval | N-staleness | N-staleness | low | D1-s5-51 |
| selector minimum off its own step grid | N-step-grid | N-step-grid | low | D4-s2-05 |
| production member reached by no production code | N-dead-member | N-structure-blind | med | D7-s3-01, D7-s3-72 |
| structure metric blind to a code shape | N-structure-blind | N-structure-blind | high | D7-s1-01 |
| series resolution inferred from the minimum gap | N-min-gap | P1 | low | D1-s5-04 |
| live input with no physical-plausibility bound | N-plausibility | P1 | med | D1-s1-03, D1-s2-02 |
| service input without an upper-bound clamp | N-service-clamp | P1 | low | D1-s2-54 |
| CPU work inline on the event loop | N-loop-cpu | P10 | high | D9-s1-03, D9-s2-01 |
| whole-entity availability gated on an optional input | N-availability | P2 | med | D8-s2-01 |
| compatibility duplicate entity enabled by default | N-dup-entity | P2 | med | D8-s3-03 |
| error-translating try opened after the call it should cover | N-late-try | P2 | med | D1-s2-55 |
| state-blind menu re-offers a completed path | N-menu | P2 | med | D4-s2-07 |
| learned-correction clamp sized against an assumed range, not the model's curve | N-clamp-range | P3 | low | D2-s2-02 |
| explicit-Euler stability judged per store instead of on the coupled step matrix | N-euler-coupled | P3 | low | D2-s1-01 |
| a sign floor on a price margin breaks the stated piecewise identity | N-sign-floor | P3 | med | D2-s3-02 |
| fit integrator differs from the simulated plant | N-fit-integrator | P5 | med | D7-s2-01 |
| persistent failure swallowed at DEBUG | N-debug-swallow | P6 | med | D1-s2-04 |
| pointer-only editing with no keyboard route | N-keyboard | P9 | med | D4-s1-04 |


### R9 judged rows kept in the judge's existing class, flagged

| id | judge class | would move to | conf | reason |
|---|---|---|---|---|
| D1-s3-01 | P2 | P1 | low | naive stored/return datetime wedges the cycle: D1-s1-01 (P1) shape at the away seam |
| D1-s5-03 | P2 | P1 | low | one huge JSON integer voids a whole fetch: malformed-input-voids-feed like R5 D1-07 (P1) |
| D1-s5-52 | P2 | P1 | med | sentinel -127/85 delivered as ok: the N-plausibility mechanism (now P1), judged P2 after G1-V3 |
| D10-s2-01 | P6 | I5 | low | preset states with no translation or icon: translation/icon coverage, I5 by R1-7 precedent |
| D2-s4-02 | P2 | P5 | low | sysid step sized to the abort bound: a sysid design defect, not a divergent predicate |
| D4-s2-01 | P6 | I5 | low | unlabelled/untranslated pre-fill fields: translation coverage, I5 by R1-7 precedent |
| D7-s3-02 | I4 | N-structure-blind | med | structure.py dead_methods census blind to properties/bare loads: same metric as R8 D7-s2-01 |


## 4. Merges of split classes

| merged into | from | why one mechanism |
|---|---|---|
| N-structure-blind | N-dead-member (D7-s3-01, D7-s3-72), N-structure-blind (D7-s1-01) | both are structure.py measuring a proxy; R8 D7-s2-01/D7-s2-02 are the same pair one round earlier |
| I5 | N-escape, N-service-icons, N-language, N-markdown | translation/icon/text coverage and doc rendering, I5 by R1-7 precedent |
| P2 | N-dup-entity, N-availability, N-late-try, N-menu | guard present at a sibling seam, missing here |
| P1 | N-plausibility, N-min-gap, N-service-clamp | unguarded value across an input boundary |
| P3 | N-sign-floor, N-euler-coupled, N-clamp-range | floor/clamp/limit constant breaking a formula's identity |

## 5. New ids (9)

| id | kind | nearest | difference | members |
|---|---|---|---|---|
| N-solve-recompute | production | P10 | avoidable CPU inside the solve (vectorise/cache), not where it runs | R8 D9-s1-01; R9 D9-s1-01/02/04/71, RC-sw1, RC-rca1, RC-rca2; flagged R1 D9-01, R2 D9-03, R4 D9-05, R5 D9-05, R7 D9-02 |
| N-structure-blind | instrument | I4 | one in-tree metric blind to a code shape; no second maintained reader | R8 D7-s2-01, D7-s2-02; R9 D7-s1-01, D7-s3-01, D7-s3-72; flagged R6 D7-02, R2 D7-06, R7 D2-02, R9 D7-s3-02 |
| N-name-sort | production | P2 | no predicate; per-entity, per-language names | R9 D8-s3-01; flagged R2 D8-04, R3 D8-03, R4 D8-01, R5 D8-01, R5 D8-02 |
| N-shared-config | production | P2 | shared mutable state across the solve boundary, no snapshot | R8 D1-s1-01, D1-s1-02; R9 D1-s3-04; flagged R2 D1-05 |
| N-approval-rebuy | instrument | I3 | enforcement keyed on head SHA, costs rounds, lets nothing through | R9 D13-s1-02 |
| N-finally-return | instrument | I1 | a code shape discards the failure signal | R9 D7-s3-51 |
| N-step-grid | production | P2 | one declaration internally inconsistent (min vs step) | R9 D4-s2-05 (low) |
| N-reap-lock | production | P2 | lock ordering between shutdown and an in-flight solve | R9 D1-s2-05 (low) |
| N-staleness | production | P6 | declares false staleness (P6 misses real staleness) | R9 D1-s5-51 (low) |

## 6. Counted instances beyond the judged findings (R9, 17 rows, kind `sweep`)

From FIX-PLAN.md:797-824 (kind `instance`). `found_by` in the note: sweep seat 6
(RC-sw1, FI-sw1..5), RCA seat 8 (RC-rca1/2, FI-rca1, P5-rca1, P9-rca1..4), the F6.1
fixer 3 (P9-f61a..c, which the table labels S5). The counting rule names judged plus
*sweep-confirmed*; FIX-PLAN and v1 (P5-rca1, FI-rca1) also count RCA-found ones, so
derive.py prints a `strict` count beside each per-round N. Not counted: P1-sw1, P1-sw2
(RCA: not store-reachable), P9-sw1 (RCA: box-metric artefact, 0 px shared ink),
P1-rca1/P1-rca2 (latent), the extra ThermalParameters seams S5 folded into D9-s1-71
(SWEEP.md says "8 additional" but counts 5 members; FIX-PLAN takes RC-sw1 only), the
S5 P9 keyboard exposure (not measured). Every other `instance` seam in S1-S7 is a
judged finding's own site or a widening of it (each SWEEP.md's count line says 0
additional), so it was dropped as the judged site itself.

## 7. Not rows

- Refuted/merged/killed: R8 D8-s2-01, D9-s1-02, D10-s2-01 (refuted), D11-s1-02
  (merged); R9 D0-s1-01, D0-s2-01, D14-s3-02 (refuted), D1-s2-01 (killed at panel),
  and the 7 merged ids (D11-s2-03, D5-s1-06, D4-s2-04, D12-s1-02, D8-s1-01, D4-s2-02,
  D6-s1-04) which travel with their canonical row.
- Owner refusals stay rows (they survived the judge): R9 D8-s2-01 (#1689 closed) and
  D11-s1-01.
- v1 non-round instances (P11: ten v6.6.12/v4.0.0/#1290/#511 incident items;
  N-restart: 'v6.6.12 bug 5 (RC2)') are not audit findings: kept in `classes_v2.json`
  `non_round_instances`, outside `total`.
