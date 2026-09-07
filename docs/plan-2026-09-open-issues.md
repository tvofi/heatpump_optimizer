# The open-issues program, September 2026

Written 2026-09-03 against `main` at `4b6e076` (v6.3.9, eight merges
unstamped). This is the worklist for every issue open at that moment — 61 of
them — planned in one pass after three sessions stood down and handed over
(`tvofi-claude-09` and `tvofi-claude-40`, both on #201; `cloud-ratchet` is
one-way). What those stand-downs established that is still in force was folded
into `docs/HANDOVER.md` when the dated handover series was retired (#518).

It supersedes `docs/plan-open-issues.md`, which covered #86–#101 and is
complete. The audit register stays `docs/audit-2026-09.md`; this file is the
delivery plan, that file is the evidence.

**Session:** `tvofi-claude-web`, label `owner:claude-web`, branch prefix
`claude-web/` — an identity, not a runner; see Model routing, every seat is a
Cursor Task agent. Owner decisions recorded 2026-09-03: full merge-and-stamp
authority under the standing protocol; #372, #373 and #374 released from
`owner:cloud-ratchet` to this session on the owner's instruction; the triage
judge settles the money-attached questions with numbers; the #193
decomposition program runs to its end state.

## Why this order

Five principles decide it, each a measured fact rather than a preference.

1. **Instruments before the fixes they judge.** `structure.py --record` cannot
   tell an improvement from a regression (#370), headroom never fails (#350),
   `duplication_blocks` has never been able to fire (#369), the ratchet has no
   method-level metric (#374), `stamp.py --self-test` has never run (#372) and
   the closure table contradicts the INERT list (#357). Every later wave is
   judged by these, so they land first.
2. **Budget-table writers never run in parallel.** `tests/structure_budgets.json`
   is rewritten by six separate pieces of work; one at a time, each rebasing
   on the last.
3. **A behaviour fix in a region lands before that region's move PR.** A fix
   inside relocated lines is reverted silently by the move's rebase, with no
   conflict and no failing test — #324 nearly lost that way inside #340.
4. **Fixture-movers share a fork and a stamp**, and a mover never claims a
   fixture that is already `may-drift` (`env_drift.may_drift_error` refuses
   the pair).
5. **Measure-first issues are triaged, not coded.** Eight close on a number;
   nine are re-scoped before a fixer is spent on them.

## Delivery status

Updated as the program lands; each row names the release that carried it.
Where this table and a wave body disagree, this table is the truth.

| Wave | Scope | Issues | Release | Status |
|---|---|---|---|---|
| 0 | stamp REST fallback (#376); then #367, #368 | #364, #282 | **v6.3.10** | **done** — all three merged, both reviews `merge`, tag `d7fa97f`, 0 unstamped |
| triage A | closed or re-scoped on a measured number | #197 #233 closed; #195 #244 #325 #334 re-scoped | — | **done** |
| 1a | the stress ruler, alone on an idle box | #346 | v6.3.11 | **done** — W1-G7 merged PR #378 (`291ae76`), 0 unstamped |
| triage B1 | read-only judges, run beside the ruler | #281 #225 closed; #303 #224 #193 re-scoped | — | **done** |
| triage B2 | solver, suite, browser and timing judges | #304 #258 re-scoped; #242 weakened to a structural zero; **#291 closed** (keep `_MULTI_START_SOLVES=4`); **#232 scoped** (smooth top-k alone → W3-G1) | — | **done** |
| 1b half I | gate instruments, suite gaps, ratchet, entity pins | 16 issues in 7 groups: #369 #370 (W1-G1), #350 #374 (W1-G2), #372 #357 (W1-G3), #373 (W1-G4), #334 (W1-G5), #247 #248 #249 #250 #251 #252 (W1-G10), #246 #251 #395 (W1-G11) | **v6.3.12** (tag `84a27b6`) | **done and released, 2026-09-04** — all seven groups merged, issues closed: PR #383, #406, #397, #384, #386, #385, #402 (merge SHAs in `.claude/workflows/wave-1b-groups.json`, each group's `resume.merge_sha`). `main` green after every merge, head `841fe0f`, stamped `84a27b6`. Five more PRs landed in the same run with no tracked issue of their own — #396 (roster/plan truth-up), #399 (the #387 coverage-floor backstop), #407 (operational docs), #409 (the ratchet-raise policy), #410 (claim priority) |
| 1b half II | card contrast/geometry, coordinator loaders, wood_share, may-drift partition, layout-editor recovery | 12 issues in 8 groups: #288 (W1-G6), #238 (W1-G8), #260 #261 #263 #266 (W1-G12), #262 #258 (W1-G13), #403 (W1-G16, added 2026-09-04), #265 (W1-G14), #254 (W1-G15), #245 (W1-G9) | **v6.3.13** (tag `f94ae13`) | **done and released, 2026-09-05** — all eight groups merged, issues closed: PR #419 (`7cc75a1`, W1-G6/#288), #421 (`a7c1e54`, W1-G8/#238), #424 (`47ded95`, W1-G14/#265), #427 (`598c83d`, W1-G15/#254), #431 (`cabcce1`, W1-G9/#245), #428 (`6bee53f`, W1-G12/#260 #261 #263 #266), #432 (`1801b76`, W1-G13/#262 #258), #433 (`ac35bf8`, W1-G16/#403). Record/tooling since v6.3.12 stamp: #414/#398, #415, #417, #418, #416/#411, #420, #426, #413; inherited-card-claims fix `7044a27` before stamp. Stamped `f94ae13`, 0 unstamped |
| — | **#387, the blocker**: the basin coverage floor is runner-dependent | #387 | v6.3.12 | **fixed** — merged as `32f309f` (PR #388); sixth acceptance criterion ruled (comment 5541519696): the WORK-channel stale-cheap downgrade is kept as necessary to the `env_drift` shape, and the coverage floor's strictness is restored by a follow-up PR that hard-codes it |
| 2 | coordinator lifecycle, learners, options grouping | #236 #237 #240 #239 #243 #283 #284 #277 #244 #325 #279 #278 #280 #198 | **v6.3.14** (tag `ef539be`) | **done and released, 2026-09-05** — seven groups merged, issues closed: PR #437 (`44a6351`, W2-G1/#236 #237 #240), #440 (`90c71c4`, W2-G2/#239 #243; duplicate #441 closed unmerged), #444 (`dc3bb8e`, W2-G3/#283 #284), #447 (`851c555`, W2-G4/#279 #278), #449 (`f492b1f`, W2-G5/#277), #451 (`efe5a27`, W2-G5 follow-up/#244 #325, review `merge` 5551113810: mid-step abort 36→0, 21 leftovers named), #438 (`e1a14f9`, W2-G6/#280), #436 (`3c141d7`, W2-G7/#198). Record/tooling since v6.3.13 stamp: #434, #435, #439, #442, #443, #446, #448, #450. Stamped `ef539be` as v6.3.14. Next seat **W3-G1** |
| 3 | solver, DHW planner, GIL process route | #232 #234 #289 #290 #199 | **v6.3.15** (tag `f0866c8`) | **done and released, 2026-09-06** — three groups merged, issues closed: PR #454 (`1585435`, W3-G1/#232 #234), #455 (`aa61130`, W3-G1 follow-up), #456 (`ebf7170`, W3-G2/#289), #461 (`8542e51`, W3-G3/#290 #199; review `merge` at `7076075`, comment 5554485684). Record/tooling since v6.3.14 stamp: #452, #458, #459, #468, #469. Stamped `f0866c8`. **W3-G4 is struck**. Everything after this tag was stamped by **v6.3.16** and **v6.3.17**; the individual PRs are named in the rows below and in the record-PR class, not summarised as a range here — a range reads as complete while naming a fraction of what it covers |
| **3L** | mid-programme leftovers, one burst | #400 #401 #404 #405 #408 #457 #460 #463 #465 | after Wave 3 | **done** — **3L-G1** #470 (`81aa0c3`). **3L-G2** #472 (`2abe2f7`). **3L-G3** #474 (`e8adfe4`) + #479 (`8ea27d4`) + #480 (`162e759`). **3L-G4** #477 (`531d8b7`). **3L-G5** #483 (`6f02b8a`) closed #408. **3L-G7** #485 (`bf08217`) closed #460. **3L-G8** #487 (`a19ba03`). **3L-G9** #489 (`b29fd1e`) closed #463. **3L-G10** #492 (`e4bc375`) closed #465. **3L-G6** (#457) never implemented: the seat returned NEEDS_CONTEXT (no production `conflict` symbol; nearest twins are read-only `setup_overview` and `reconfigure`), and the owner then closed #457 as `COMPLETED` by hand on 2026-09-06T03:40:23Z with no PR and no commits. Discharged, not blocked — do not reopen it and do not invent a backend. **W4-G6** (S5) merged #529 (`8281f54`); **W4-G7** (S6) merged #537 (`d04ed89`); **W4-G8** (S7) merged #551 (`0f9eb71`); **W4-G9** (S8) merged #555 (`52d38d9`); **W4-G11** (S10) merged #543 (`e072b2d`, closed #304). Next is W4-G10 (S9, #224). Do not stamp. #481 leftover closed. #412 stays last of the programme |
| 4 | the #193 decomposition programme, S0–S13 | #193 #223 #224 #225, and **#304 as S11's precursor** | one per stage | **S0–S8 and S10 done; next W4-G10 (S9, #224)** — S0 #497 (`c197b01`), S1 #500 (`67e1cf3`, closed #377; **corrected 2026-09-06**: the reported 138-point drop across all five cuts was `structure.py` losing sight of `getattr(self, "_ctx", self)` references S1 introduced 131 of, not decoupling — fixed by #512, S1's other results (`CoordinatorContext`, the attribute count, the facades) stand unchanged), S2 #502 (`d979110`, review `merge` 5558785350), S3 #506 (`5a4e6ff`, review `merge` 5559638736 at `258b245`: cut_views 94→85, coordinator_loc/max_class_loc 10305→10164, functions_cc_over_15 39→38, methods_over_150 21→20; earlier `blocked` 5559418212 at `341c596` cleared). **S4 (W4-G5, fetch) is a RECORDED HALT, merged as `e46fb15` (#508), with no production change** — measured then as 92 of cut_fetch's 115 being other seams reading the 15 fetch-owned attrs (60) and calling into fetch (32); **re-measured after #512**, cut_fetch is 132, not 115 (the whole +17 is fetch's own reads of attributes it does not own, previously invisible through the same idiom — see the roster note for the full recount), the other-seams-reaching-in share is unchanged in absolute count at 92, and the halt's actual basis — the judge's #193 finding that no component of size>1 detaches at any k — is untouched, so the seam move stays sequenced to S12/W4-G13, not banned. **S5 (W4-G6, dhw) merged as `8281f54` (#529, review `merge` 5561488083)**: cut_dhw 194→103 (-91, -47%), cut_learning 350→321, total cut across all five seams 1022→902 and `core` 15→14 (the control that distinguishes a real decoupling from moving points to a neighbouring seam). **The constraint S5 produced, carried into the W4-G7/G8/G9/G13 briefs:** the ownership lever is legitimate only where a seam's entire contact with an attribute is the assignment — no reads, no other writes — demonstrated per attribute, never assumed; `_helper(self, ...)` at S3 and `getattr(self, "_ctx", self)` at S1 were both refused on exactly that. Measured by moving twelve non-hot-water attributes `_init_dhw_learning` misplaced into a new `_init_thermal_learning` (learning seam). Do not Closes #193. Roster `.claude/workflows/wave-4-groups.json`. #225 stays closed. #412 not in this wave. Do not stamp |
| R | reliability, instruments and harness — hotfixes and findings made alongside Wave 4, not wave work | #510 #511 #513 #518 closed | v6.3.16 (`#512`, `#515`); unstamped (`#517`, `#519`) | **delivered 2026-09-06** — #512 fixed `structure.py`'s cut-walk blindness to `getattr(self, "_ctx", self)`, closed #510; #515 fixed the release-critical unpickle failure (every install produced no plan), closed #511; #517 added `tests/deployment_shape.py`, closed #513; #519 consolidated the handover series into one file, closed #518. Detail below |
| UX | the UX programme: **34 items in five lanes**, B/C/D/E concurrent with the waves, **F last of the whole programme** | tracking **#558**; items land under their own numbers (#509 done, #516 = E4) | B, C, D now; E1–E3 after S11; **F after Wave 5 and #412** | **lanes B, C, D started 2026-09-07.** Docket: the *Optimizer UX Docket* artifact. Independence is by **file**, not only by budget — see the collision table below |
| 5 | typing lane, and the coverage deficit #195 raised | #303 #195 | per tranche | pending — roster `.claude/workflows/wave-5-groups.json` prepared; **seats not started**. After Wave 4. **#304 is Wave 4**, not here. #412 not in this wave |
| last | CI Node majors, then **UX lane F** | #412, then UX F1/F2 | after Wave 5 | pending — owner: #412 is the last *task*; **lane F is the last work of the programme**, because it is the only lane that adds lines to `coordinator.py` |

### Wave 3L — leftovers, after Wave 3, before Wave 4

Every open issue that is not already in Waves 3–5 or #201, filed after the 2026-09-03 plan cut, plus #460 (monthly savings), #463 (wood furnace economics), and #465 (Plan-page away toggle). One burst so they are not lost again, and **before** Wave 4 because #400, #408, #463 and #465 are behaviour in the DHW/optimizer/config/card region a move PR would silently revert (principle 3). Wave 3 is released (`f0866c8`); 3L-G1–G5 and 3L-G7–G10 are done (`e4bc375`). **3L-G6** (#457) shipped nothing and #457 was closed `COMPLETED` by the owner on 2026-09-06 — discharged, not blocked. **W4-G6** (S5) merged #529 (`8281f54`); **W4-G7** (S6) merged #537 (`d04ed89`); **W4-G8** (S7) merged #551 (`0f9eb71`); **W4-G9** (S8) merged #555 (`52d38d9`); **W4-G11** (S10) merged #543 (`e072b2d`, closed #304). Next is W4-G10 (S9, #224). Do not stamp. #465 is closed. #412 stays last of the programme and is not in this burst.

| group | issues | model | after | scope |
|---|---|---|---|---|
| **3L-G1** | #400 | Grok 4.6 extra high | W3-G3 | DHW planner sees the wood-tank refill coil. Measured 5.394 SEK/day; plan is byte-identical coil-on/off today. Claims, never re-record goldens |
| **3L-G2** | #401 | Composer 2.5 | 3L-G1 | `closure.py` `_record_node()` strace availability guard. Unblocks a full derive on macOS. Before #404 |
| **3L-G3** | #404 | Composer 2.5 | 3L-G2 | Gate lock becomes a renewed lease + `flock`. Lives in `tests/`, needs the derive #401 unlocks |
| **3L-G4** | #405 | Composer 2.5 | 3L-G3 | `SolarIrradianceSensor` / `OptimizationScoreSensor` data-driven keys: state the bound in the holes list, no exact-set pin |
| **3L-G5** | #408 | Grok 4.6 extra high | 3L-G4 | Optional set-point entities + **consistency** repair issue only. Optimality / Fix-to-argmin half is refused (50→65 °C instability) |
| **3L-G6** | #457 | Composer 2.5 | 3L-G5 | Card setup-page button that opens the conflict flow. Card-only. **Not implemented** — no production `conflict` symbol; #457 closed `COMPLETED` by the owner 2026-09-06 |
| **3L-G7** | #460 | Grok 4.6 extra high | 3L-G6 | Monthly savings history card page. Realised thermostat-baseline ledger lines; calendar pro-rata for the open month. After #457 (or after #408 if #457 stays blocked). Spec/plan `docs/superpowers/{specs,plans}/2026-09-05-monthly-savings-history*.md` |
| **3L-G8** | #463 | Grok 4.6 extra high | 3L-G7 | Wood-furnace toggle, firewood price, `wood_fuel.py`, cheaper-than-pump sensor. Does not close #463. Spec/plan `docs/superpowers/{specs,plans}/2026-09-05-wood-furnace-economics*.md` |
| **3L-G9** | #463 | Grok 4.6 extra high | 3L-G8 | Plan banner, Wood lane, what-if wood slots. `Closes #463`. Same spec/plan |
| **3L-G10** | #465 | Grok 4.6 extra high | 3L-G9 | Plan-page Away toggle and return datetime. Service-backed store; published switch and datetime; optional person/calendar. `Closes #465`. Spec/plan `docs/superpowers/{specs,plans}/2026-09-05-away-plan-toggle*.md` |

Do not fold 3L into a closed Wave 3. 3L-G10 merged as #492 (`e4bc375`); #465 closed. W4-G1 #497 (`c197b01`), W4-G2 #500 (`67e1cf3`), W4-G3 #502 (`d979110`) and W4-G4 #506 (`5a4e6ff`) merged; #377 closed. W4-G5 (S4, fetch) recorded a halt with no production change, merged as `e46fb15` (#508). W4-G6 (S5) merged #529 (`8281f54`); W4-G7 (S6) merged #537 (`d04ed89`); W4-G8 (S7) merged #551 (`0f9eb71`); W4-G9 (S8) merged #555 (`52d38d9`); W4-G11 (S10) merged #543 (`e072b2d`). Next is W4-G10 (S9, #224). Do not stamp or start #412 from this record.

### Wave 4 — #193 decomposition, S0–S13 (S0–S8 and S10; next W4-G10)

Roster: `.claude/workflows/wave-4-groups.json`. Serial, one group per stage. Worker briefs live out of tree under `/Users/timmalmstrom/wt/briefs/w4-gN-*.md` (same convention as 3L). **#223 issue text allows parallel with coordinator moves; this table does not authorize a second lane.** Plan numbers the registry as **S11**; #193 numbers it S10 — the issue number is the stable reference. **#304 is S11's precursor** (W4-G11), not Wave 5. **#225 is closed** (triage B1) — struck in the roster, do not reopen. **#412 is not in this wave.** **#457 / 3L-G6 is not Wave 4**, and #457 is closed `COMPLETED` (2026-09-06) with nothing shipped — do not go looking for that work. S2–S8 and plan S12 have no child issue: they track #193 and must not `Closes #193`. A survey stage **halts** (record only, no invented backend) when the named seam is not extractable at this merge-base, an open PR holds the region, or a ratchet metric would rise. The `model` column names Claude seats for groups not yet started and the model that actually ran for groups already delivered — see Model routing.

| group | stage | issues | model | after | scope |
|---|---|---|---|---|---|
| **W4-G1** | S0 | #377 | Grok 4.6 extra high | 3L-G10 merge | `CoordinatorContext` defined; nothing relocates. Do not close #377 |
| **W4-G2** | S1 | #377 | Grok 4.6 extra high | W4-G1 | Migrate hub refs; facade properties stay. `Closes #377` |
| **W4-G3** | S2 | #193 (tracking) | Grok 4.6 extra high | W4-G2 | Pure-function extractions. Survey-first; halt if not this seam |
| **W4-G4** | S3 | #193 (tracking) | Opus 5 | W4-G3 | views, thinned, stays the facade. Survey-first; halt if not this seam |
| **W4-G5** | S4 | #193 (tracking) | Opus 5 | W4-G4 | fetch/sources. Survey-first; halt if not this seam |
| **W4-G6** | S5 | #193 (tracking) | Opus 5 | W4-G5 | dhw. Survey-first; halt if not this seam |
| **W4-G7** | S6 | #193 (tracking) | Opus 5 | W4-G6 | grid/bookkeeping. Survey-first; halt if not this seam |
| **W4-G8** | S7 | #193 (tracking) | Opus 5 | W4-G7 | learning A (thermal). Survey-first; halt if not this seam |
| **W4-G9** | S8 | #193 (tracking) | Opus 5 | W4-G8 | learning B (curve/comfort/drift-watch). Survey-first; halt if not this seam |
| **W4-G10** | S9 | #224 | Opus 5 | W4-G9 | optimizer.py judge-corrected splits; first PR is the cheap `optimize` tail |
| **W4-G11** | S10 | #304 | Sonnet 5 | W4-G10 | 21 named `config_flow.py` statements; test-only; before #223 |
| **W4-G12** | S11 | #223 | Opus 5 | W4-G11 | config_flow settings registry; serial after #304 |
| **W4-G13** | S12 | #193 (tracking) | Opus 5 | W4-G12 | Delegate seams / facade deletion (#193's S11). Halt if S3–S8 all halted. #195 coordinator half is Wave 5; #374 already done |
| **W4-G14** | S13 | #193 | Sonnet 5 | W4-G13 | Close-out: Delivery-status, roster, #201. Do not stamp. `Closes #193` only if S0–S12 are done or recorded-halted |

### Wave 5 — #303 typing and #195 coverage (roster prepared, seats not started)

Roster: `.claude/workflows/wave-5-groups.json`. After Wave 4. Serial. **#304 is not here.** **#412 is not here.** #303 is four named tranches (parent may split G3 further). #195 coordinator modules stay last (after #193 seams). Models are the Claude seats of the 2026-09-06 routing.

| group | issues | model | after | scope |
|---|---|---|---|---|
| **W5-G1** | #303 | Sonnet 5 | Wave 4 S13 merge | Land the pinned stub-free ruler. Do not close #303 |
| **W5-G2** | #303 | Opus 5 | W5-G1 | `sensor.py` annotations (142 at filing) |
| **W5-G3** | #303 | Opus 5 | W5-G2 | Remaining modules except `coordinator.py`. Parent may split further |
| **W5-G4** | #303 | Opus 5 | W5-G3 | `coordinator.py` typing after Wave 4 seams. May `Closes #303` |
| **W5-G5** | #195 | Sonnet 5 | W5-G4 | `climate.py` / `open_meteo.py` / `frontend.py`. No coordinator |
| **W5-G6** | #195 | Sonnet 5 | W5-G5 | `diagnosis.py` / `curve_learning.py` / `grid_fee.py` / `switch.py`. Cleanup is not this tranche |
| **W5-G7** | #195 | Opus 5 | W5-G6 | `coordinator.py` coverage (789 missed) after #193 seams. May `Closes #195` |

### Reliability, instruments and harness — delivered 2026-09-06 (not a wave)

The Delivery-status table above accounts for wave stages and their records.
It does not, on its own, account for the other kind of work this session
produced: hotfixes, an instrument repair and a harness gap, found while
doing something else rather than surveyed into a stage. It is not Wave 4 work
and is not forced into that table beyond the summary row above.

| PR | what | issue | state |
|---|---|---|---|
| #512 | `structure.py`'s cut walk matched only `ast.Attribute` on `ast.Name("self")`, so a reference through `getattr(self, "_ctx", self)` — an idiom S1 (#500) introduced 131 times — had a `Call` as its value and was invisible. The walk now resolves that idiom, the direct `self._ctx` form, and local aliases bound to either. The five cut budgets are re-recorded upward to their true values: `cut_views` 85→112, `cut_fetch` 115→132, `cut_dhw` 160→194, `cut_grid` 209→234, `cut_learning` 315→350 — they rise only because the true number was always higher; no coupling is added | #510 | merged `af47c96`, released **v6.3.16** |
| #515 | the process-solve worker could not unpickle its job on any Home Assistant install. A solve is shipped to the child by pickling a function, and pickle records it by qualified name; under Home Assistant that name begins `custom_components.`, a path the child's search path did not resolve, so every optimization on every v6.3.15 install failed, permanently and silently. Now an unloadable job is reported rather than killing the worker, and a worker fault falls back to an in-process solve | #511 | merged `98a7574`, released **v6.3.16** |
| #517 | `tests/deployment_shape.py` runs the integration under an installation's real module name and directory layout — the gap #513 named as the reason no test caught #511: the suite imports the package under a different name and runs with a `tests/` directory no installation has | #513 | merged `6cd2c28`, **unstamped** (lands after v6.3.16) |
| #519 | one living `docs/HANDOVER.md` replacing the dated handover series (`docs/handover-<date>.md`), with `tests/entities.py` refusing a second dated file from re-forming | #518 | merged `b6a21f1`, **unstamped** (lands after v6.3.16) |

#510, #511, #513 and #518 are closed by the fixes above, not by wave work.

**Every other open issue, with its disposition.** "Not mentioned" is not a
disposition, so each open issue is scheduled, deferred with a reason, or
refused with a reason — and the PR carrying it is named where one exists.

**The completeness check covers three sets, not two.** Open issues and open
pull requests are the obvious two, and checking only those is structurally
blind to the largest set: **merged** pull requests, which by definition stop
appearing in any "open" listing the moment they land. That blindness is not
hypothetical — it hid #491 and #498 among others, #498 being the pull request
that built `closures-autofix`, the job this repository makes load-bearing. **The
count is deliberately not stated here**: the first attempt at it said "twenty",
measured with `--limit 120`, and the re-derivation under the same rule gives a
different answer again. Run the check rather than reading a number off this
page. A **range in prose is not a disposition** either: `#470–#500` reads as
complete and absorbs thirty-one numbers while naming eight. The check is
therefore per-number over all three sets:

```
gh pr list --state merged --limit 300 --json number -q '.[].number' |
  while read n; do [ "$n" -ge 375 ] || continue
    grep -q "#$n\b" docs/plan-2026-09-open-issues.md ||
      echo "MERGED PR #$n has no disposition"; done
```

and the same loop, without the `375` guard, over `--state open` and over
`gh issue list --state open`. **Use a `--limit` that reaches past the oldest
number you are checking** — a truncated listing under-reports silently, and a
`--limit 120` run is what first reported this gap as twenty.

**The scope boundary, stated so the check terminates — and what it does not
claim.** This document is the plan of record for the #201 open-issues
programme, created by **#375** (`8e99ad1`), and it accounts for every pull
request merged **from #375 onward**. At this head that check returns **zero**.
Without the boundary the loop demands this file account for the entire
repository history and can never come back clean, which is the failure mode
that makes a check get quietly dropped rather than fixed.

**The boundary is a limit on this document's scope. It is *not* a claim that
the earlier work is recorded elsewhere, and an earlier draft of this paragraph
said it was.** Measured against this file **as it stood on `origin/main` before
this paragraph existed**: of the merged pull requests below #375 with no
disposition here, **147 appear in none** of the three programme documents this
file cites. Those documents reach only into the low hundreds and the double
digits respectively, and `docs/audit-2026-08.md` carries no issue or
pull-request reference at all — so this is not an artifact of citation style.

**Why the baseline is named, and why two figures that used to be here are
gone.** The check is a bare `grep -q "#$n\b"`, which cannot tell a disposition
from an incidental mention. An earlier draft of this paragraph *cited the two
highest-numbered references in those documents by number* — and that sentence
put those tokens into this file, which handed both pull requests a
"disposition" and moved them out of the miss set. The paragraph's own
measurement of itself was destroyed by the act of recording it. So: measure
against a fixed baseline, not the live file, and read every count the check
produces as a **lower bound** on what is genuinely undispositioned.

That gap is real, it predates this programme, and it is **#575**. Naming it is
the point: a boundary that quietly reassigns 147 unrecorded merges to a
document that does not contain them is the same defect as the prose range it
replaced — something that reads as complete while covering a fraction.

| issue | disposition | carried by |
|---|---|---|
| **#504** ruler will not install (Python 3.13.1 < 3.13.2) | **scheduled — W5-G1, as a precondition of it.** The choice between raising the box, re-pinning, or CI-only is made *in* that PR, with its reason | W5-G1 |
| **#505** #195 tranches miss nine below-bar modules | **scheduled — W5-G5 re-partitions before extending coverage.** `process_worker.py` at 0.0 % is a candidate to pull forward | W5-G5, inherited by G6/G7 |
| **#509** diagnostics publish home latitude/longitude unredacted | **in flight** — coordinates coarsened to 1 dp rather than redacted, so a swapped lat/lon or wrong country still shows; `config.name` redacted. The "land it before #522" sequencing was **void**: #522's review measured that the lane never calls diagnostics and uploads no artifact | [#535](https://github.com/tvofi/heatpump_optimizer/pull/535) |
| ~~**#514**~~ Python floor undeclared, 3.14 untested | **DONE** — closed by #520, merged `36b71dd` | [#520](https://github.com/tvofi/heatpump_optimizer/pull/520) |
| **#516** config-flow options are ungrouped | **deferred to the UX programme, lane E.** Not blocked on HA version once #520 lands, but still blocked on the golden capture walking schemas one level deep — grouped fields would fall silently out of the fingerprint. That is the constraint to solve, not the HA floor | UX lane E |
| ~~**#521**~~ no test runs the integration in a real HA install | **DONE** — closed by #522, merged `824fd84`. Residuals recorded, not swept: the lane reaches ~15 of the ~58 container-reachable escapes, and its incompleteness was silent → **#533** | [#522](https://github.com/tvofi/heatpump_optimizer/pull/522) |
| **#523** `closures-autofix` reported success without repairing | **in flight, blocked once** — review measured a *residual* silent path: `any(rc != 0)` (a failed recording) is folded into the same quiet status, so one unrelated failure hides a real repair while the job exits 0. Being fixed | [#528](https://github.com/tvofi/heatpump_optimizer/pull/528) |
| **#524** an unpicklable solve result is returned as the plan | **in flight** — and *worse than filed*: `_run_in_process` **returns** the `RuntimeError` rather than raising, so the chain publishes it as the plan, resets `_solve_failures` to 0 and deletes the repair notice. The bug erased its own evidence | [#540](https://github.com/tvofi/heatpump_optimizer/pull/540) |
| **#525** two blocking calls in the event loop | **in flight** — the filed mechanism was **wrong**: `_shutdown_process_pool` is never reached from the loop, and `protect_loop` fires because it compares thread ids while `atexit` runs on the main thread. Also **three** loop-side `_lazy` imports, not two — `frontend` was missed | [#540](https://github.com/tvofi/heatpump_optimizer/pull/540) |
| **#527** a full `derive_closures.sh` silently shrinks the node lanes | **scheduled — after #528 lands**, since the refusal message that tells you to run one is the same code path | follows #528 |

| **#533** the nightly lane's incompleteness is silent | **scheduled — A3 first** (class 3, published state wrong or non-finite, is the largest reachable gap at 16 escapes), then A10, which would pin #509 directly | follow-up to #522 |
| **#536** `tests/hastub` can diverge from Home Assistant | **scheduled — inventory first.** A green test can pin the stub instead of HA: the #509 fix was green while returning `None` on every real install, because upstream skips `None` before redacting and the stub did not | follow-up to #535 |
| **#542** saving the learning options page **wipes `external_heat_entity`** | **scheduled as a hotfix, ahead of S11.** User-facing data loss on an ordinary action: `async_step_learning` cleans a key its own form never presents — the learning schema holds five booleans and one number and no entity field, so `cleaned.get(key)` is always falsy and the page always writes `None`, which `_save_or_menu` then merges over the real value set on the *building* page. Found by W4-G11 (S10) while covering #304 and **correctly filed rather than fixed** — a test-only stage may not touch production. Five unreachable statements ride along | its own fix PR |
| **#559** B1, **#560** B2, **#561** B3, **#562** B4, **#563** B5 — UX lane B | **in flight.** B1 answers first because it decides B4–B7: whether HACS's in-app README view renders mermaid was never checked, and `hacs.json` sets `render_readme: true`. B5 needs B4 landed | lane B seat |
| **#564** UX lane C, item C1 — four contrast fixes in one PR | **in flight.** 1.05:1, 1.089:1, 2.63:1 and 1.098:1, all invisible to the CI witness because it measures four *text* sites under a light theme only. One PR because all four claim drift over the same state list | lane C seat |
| **#565** D2, **#566** D3 — UX lane D | **in flight.** D3 must land before D4 because the icon state keys must match its options — and `ENUM` **constrains what a sensor may publish**, so a missed state is a runtime error on a real install | lane D seat |
| **#558** UX programme tracking — 34 items in five lanes | **scheduled, lanes B/C/D started 2026-09-07.** Carries every item, the three in-lane sequencing rules, and the collision table. **E1–E3 follow S11 (#223)**; **F1/F2 are the last work of the whole programme**, after Wave 5 and #412, because lane F is the only one adding lines to `coordinator.py` at zero headroom | #558, items under their own numbers |
| **#550** the `apply_topology` set check pins the reverse direction against the module constant, not the schema | **scheduled — ~3 lines, after #548 lands.** Re-adding `slab_shunt` *plus an arbitrary junk key* to the schema passes all 2002 checks, while the check's own name claims it verifies exactly that. Probe the schema instead of reading the constant. Also records that `slab_shunt` was **re-tenanted, not eliminated** — `accepted − card_boxes` is `['slab_shunt']` at base and `['floor_loop']` at head, still one, disclosed and costed rather than missed | follows #548 |
| ~~**#544**~~ every branch conflicts in the two claim files | **DONE — closed by #545, merged `4f6a8b1`.** Prevented, not repaired — a `claimnotes` merge driver unions the note comments and **refuses** a claim list both sides rewrote, since union reinstates a deleted claim past the `#495` guard. Five branches, ten conflicts, in one session | [#545](https://github.com/tvofi/heatpump_optimizer/pull/545) |
| ~~**#546**~~ pressing **Tidy** made the setup page unsaveable | **DONE — closed by #548 (`137b6d5`), shipped in v6.3.17.** Released severity — `apply_topology` rejects `positions.outdoor`, which the card always emits. **Not drag-only**: the RCA ran the card's own `layoutArrange` and Tidy alone emits it on every configuration. **Shipped v3.16.0, 80 releases ago.** A stamp follows the merge | [#548](https://github.com/tvofi/heatpump_optimizer/pull/548) |
| **#547** four config-flow pages have a stored-value arm that is executed but unpinned | **in flight — [#553](https://github.com/tvofi/heatpump_optimizer/pull/553).** The golden now seeds options and the arm went from **1-of-12 mutants killed to 11-of-12** (the twelfth is `learning`, dead code per #542, where a surviving mutant is correct). Mutating the arm on `building`, `hot_water`, `entities` or `comfort` leaves the whole scoped gate green, because `capture_config_flow()` seeds no options and only renders the *empty* arm. A registry dropping that arm re-creates #542's wipe on the page owning `CONF_EXTERNAL_HEAT_ENTITY` | folds into #195's W5-G5/G6, or its own PR |
| **#539** `tools/audit` *generates* the forbidden `mkdir` gate lock | **scheduled, and ordered** — `prepare_baseline.sh:53` emits it into the text new auditors read, so **fix the generator first**; correcting the four prose sites while the generator stands means they come back. One section recounts the 113-minute incident that motivated #404 and then prescribes its cause | follows #534 |
| **#577** nine measured divergences between `tests/hastub` and Home Assistant | **filed by the #536 seat, in the pass that built the mechanism.** Each measured against Home Assistant **2025.2.0** — the floor `hacs.json` declares — and recorded in `tests/ha_contract.py` as a `DIVERGENT` entry carrying an `expect="real"` contract: a statement of upstream behaviour that **must fail against the stub**, so each is pinned in both directions | #578 |
| **#584** nightly A3: the published-state sweep | **filed by #533's seat, which asked for it by name.** The largest single unimplemented gap in the container lane — **15 past escapes, more than the four already-implemented assertions cover between them** | own PR |
| **#585** nightly A10: the diagnostics privacy probe | **filed by #533's seat**, second priority after A3 because it pins an **open, still-shipping** defect directly: no token and no latitude/longitude beyond two decimals anywhere in the diagnostics payload | own PR |
| **#587** nightly A5/A8/A9: options round-trip, service registration, reload | **filed by #533's seat.** One issue, three tranches, because all three need what the lane lacks — a **second** config entry and a reload rather than the single boot it does today. Split if a seat takes one alone | own PR |
| **#588** the loop detector cannot tell "no blocking call" from "no log" | **filed by #533's seat as the residual its own fix left**, stated rather than left to be rediscovered. #533's fix made the pin a two-directional ratchet; this is the case the ratchet still cannot see | own PR |
| **#580** a check earns its place once and is never asked again | **filed this session; under refutation.** Eight instances in one day of one class — an absent signal reading as a passing one. Three refutation seats and a judge are deciding whether it stays, stays modified, or closes | under review |
| **#581** `brief_lint` refuses a literal metric but not a literal anything-else | **filed this session; under refutation.** Ten stale figures in one day. The issue **carries its own falsification test**: if no rule can separate an observation from a definition, it closes rather than being built | under review |
| **#582** lanes B–F have no roster, so propagation has no destination | **filed this session; under refutation.** Two seats tried to comply with `finding-propagation.mdc` and had nowhere in-tree to write | under review |
| **#583** stopping a seat mid-mutation leaves a production file broken | **filed this session; under refutation.** Measured once, harmed nothing — the resolver's dirty-tree guard held | under review |
| **#574** two residues of #572 | **filed this session, unclaimed.** `fix-review.md` step 13 exempts a claim-file conflict from blocking, but omits the one case where such a conflict *is* meaningful — `merge_claim_file` deliberately refuses when both sides rewrote the bare claim list, which is the driver's entire safety argument. And `tests/features.py:21373` still says "all 22 metrics" where the derived count is 24. Part 1 is policy | own PR |
| **#575** 147 merged PRs below #375 have no disposition anywhere | **filed this session, unclaimed.** #531's scope boundary originally asserted that pre-#375 work "is recorded there, not here" in three cited documents. Measured: of 157 such merges, **10** appear in one of them and **147 in none**; those documents top out at #121 and #65, and `audit-2026-08.md` carries no PR reference at all. The boundary stays — without it the check never returns clean and gets dropped — but it is a limit on this document's scope, not a claim about another's contents. Whether those 147 need a disposition at all is the owner's call | own PR |
| **#570** GitHub cannot run the `claimnotes` merge driver | **CLOSED by [#572](https://github.com/tvofi/heatpump_optimizer/pull/572), merged `059881e`.** A merge driver's implementation is a `git config` entry and git never clones config, so GitHub — which computes `mergeStateStatus` — falls back to a plain text merge and calls every open PR `DIRTY` the moment `main` touches a claim file. GitHub then will not build a merge commit, so the `pull_request` workflows **never queue**: such a PR does not go red, it cannot run. Measured on #569 (CodeQL alone; `fast`, `closures`, `browser`, `briefs` absent). The fix is a subtraction — nothing requires a branch to write a note into a claim file, so a branch that claims nothing does not touch them | policy PR |
| **#541** verifiable proof that a PR followed the *process* | **split three ways, not deferred wholesale** (disposition: comment 5562208736). **Mechanism 3** (GitHub as witness — 14 obligations, one API call, additive) **now**. **Mechanism 1** (replay the branch) at a **wave boundary**, since its value is concentrated in the fixer PRs of Wave 4 S7/S8/S12 and Wave 5 and a gate change is only cheap when nothing is in flight. **Mechanisms 2, 4, 5** as a new programme after #201, whose **first task is an independent re-derivation of the taxonomy** — 94 rows are one agent's judgement over a heuristic split, and if the class distribution moves the ranking moves with it | own programme |

Policy and contract PRs this session opened, which close no issue and belong to
no wave:

- [#530](https://github.com/tvofi/heatpump_optimizer/pull/530) — **merged `f4ed26c`.** Tracking covers every PR and every open issue; and `finding-propagation.mdc`: a finding that changes how a later stage must work goes into that stage's own brief before the producing PR merges. Enforced at `fix-review.md`, verdict `blocked: finding not carried to <stage>`.
- [#526](https://github.com/tvofi/heatpump_optimizer/pull/526) — root-cause doctrine. Blocked once for having **no enforcement point**; now trigger *red on a check a cheaper detector could have run*, checked at `fix-review.md` step 11, verdict `blocked: root-cause trigger unanswered for <check>`.
- [#532](https://github.com/tvofi/heatpump_optimizer/pull/532) — the handoff to review freezes the branch. Blocked once for naming the **coordinator** where the tree means the **orchestrator** (`coordinator` is the production god-class Wave 4 is decomposing); verdict `blocked: head moved under review, measured <sha>`.
- [#534](https://github.com/tvofi/heatpump_optimizer/pull/534) — three permanent documents that contradicted the code: `fixer.md` step 5 mandated the `mkdir` gate lock two other permanent files forbid, and prescribed an unconditional local gate. Blocked once on a null control that reproduced at **neither** head, with the false form committed to a claim file. Cleared; `merge`.
- [#543](https://github.com/tvofi/heatpump_optimizer/pull/543) — **W4-G11 / S10, `Closes #304`.** `config_flow.py` 96.13 % → 99.26 %, all 21 named statements individually pinned. Blocked twice: a forward-carry that told S11 four pages were inert, and a body whose "Does not close #195" **parsed as a closing keyword**.
- [#545](https://github.com/tvofi/heatpump_optimizer/pull/545) — the `claimnotes` merge driver (#544). `merge`. The seat was asked for a third autofix job and **refused it with arithmetic**, which is the right outcome.
- [#548](https://github.com/tvofi/heatpump_optimizer/pull/548) — **`Closes #546`**, the released Tidy defect. In review; a stamp follows.
- [#549](https://github.com/tvofi/heatpump_optimizer/pull/549) — the policy text split verbatim out of #545, **awaiting the owner's approval**. Split so a working fix does not wait behind a 46-line docs diff.
- [#538](https://github.com/tvofi/heatpump_optimizer/pull/538) — **merged `17dc30a`.** `finding-propagation.mdc` routed cross-cutting findings to a destination `git grep` cannot find, *and made reaching it a merge blocker*. It also **deleted the clause deferring the in-tree carry to the record PR**, which retroactively bound #540 — a verdict correct when written stopped being correct without the code changing.
- [#552](https://github.com/tvofi/heatpump_optimizer/pull/552) — **merged, closed #539.** `tools/audit/prepare_baseline.sh` was *generating* the forbidden `mkdir` gate lock into every new auditor's text; the generator is fixed first, because correcting the prose alone leaves it re-emitting. Wider than filed: the same instruction also sat in agent prompt strings under `.claude/workflows/`.
- [#554](https://github.com/tvofi/heatpump_optimizer/pull/554) — `Closes #550`. Probes the registered schema instead of the module constant. Reviewed `merge`: fails on the junk-key reproduction that passed all 2002 shipped checks, and passes on **both** plausible fixes where the shipped check fails 4 of 7, because both directions became bounds rather than an equality.
- [#556](https://github.com/tvofi/heatpump_optimizer/pull/556) — the README section on AI use, its failure mode and what the gate costs a human contributor. Reviewed `merge`; contains no digits, by regex.
- [#557](https://github.com/tvofi/heatpump_optimizer/pull/557) — **W4-G10 / S9**, the first split of #224. Does not close it; five implementable pieces plus a design brief remain.
- [#375](https://github.com/tvofi/heatpump_optimizer/pull/375) — **merged `8e99ad1`**, this document and the workflows that run it. The programme's own first commit, and the boundary the completeness check above uses.
- [#379](https://github.com/tvofi/heatpump_optimizer/pull/379) / [#382](https://github.com/tvofi/heatpump_optimizer/pull/382) — **merged `db13fba` / `f7b5881`**, triage B1 and B2. B1 found the decomposition order **inverted** and its first stage overscoped, which is why Wave 4 runs S0→S13 in the order it does. B2 established the card residual is vertical and the coverage gap 21 statements.
- [#381](https://github.com/tvofi/heatpump_optimizer/pull/381) — **merged `a2c4982`**, a blocked tag push is *reported*, not raised over an already-public commit. One of `stamp.py`'s refusals.
- [#389](https://github.com/tvofi/heatpump_optimizer/pull/389) / [#390](https://github.com/tvofi/heatpump_optimizer/pull/390) — **merged `c06932a` / `81216e6`**. Everything a cold session needs is on `origin`, and the recorded resume state can be *executed* rather than only read. Together with #391–#393 these are why `resume` fields are machine-usable.
- [#467](https://github.com/tvofi/heatpump_optimizer/pull/467) — **merged `2ba8367`**, production: the heat-pump switch turns off on DHW-only idle.
- [#490](https://github.com/tvofi/heatpump_optimizer/pull/490) — **merged `62799e4`**, display-only DHW band: live probe σ(0) and an in-window lo floor.
- [#493](https://github.com/tvofi/heatpump_optimizer/pull/493) / [#494](https://github.com/tvofi/heatpump_optimizer/pull/494) — **merged `ae97a65` / `a26bb76`**, the Wave 4 and Wave 5 rosters prepared with no seat started, and the inherited DHW card claims emptied behind them.
- [#464](https://github.com/tvofi/heatpump_optimizer/pull/464) — **merged `7a233f7`**, seat 3L-G8/G9 wood furnace economics (#463). Seat work, not a record.
- [#466](https://github.com/tvofi/heatpump_optimizer/pull/466) — **merged `186be0c`**, seat 3L-G10 plan-page away toggle (#465). Seat work, not a record.
- [#498](https://github.com/tvofi/heatpump_optimizer/pull/498) — **merged `5234024`**, `closures-autofix`: the CI job that re-records `UNDER-SCOPED` closures from the failed job's own recordings. `CLAUDE.md` makes it load-bearing — *do not open a second PR, do not Darwin `--single`, wait for the bot commit.* Its successor #528 had a row; the job that introduced it did not.
- **The doctrine PRs that predate the wave rows** — [#391](https://github.com/tvofi/heatpump_optimizer/pull/391) (a cold session is oriented by the repository, not by a programme — the ancestor of this `CLAUDE.md`), [#392](https://github.com/tvofi/heatpump_optimizer/pull/392) (the handover says where the session *stopped*), [#393](https://github.com/tvofi/heatpump_optimizer/pull/393) (the wave-resume machinery). All merged. They are why a resuming session needs no briefing.
- **The record PRs — all of them, by rule.** A record PR carries one group's Delivery-status and roster update and closes nothing; its content is the rows above rather than a row of its own. Naming three of them and calling the enumeration complete is how #491 and #498 went 20 merges without a mention. The complete set, so the rule can be checked rather than trusted: waves 1–2 — [#422](https://github.com/tvofi/heatpump_optimizer/pull/422), [#423](https://github.com/tvofi/heatpump_optimizer/pull/423), [#425](https://github.com/tvofi/heatpump_optimizer/pull/425), [#429](https://github.com/tvofi/heatpump_optimizer/pull/429), [#430](https://github.com/tvofi/heatpump_optimizer/pull/430); wave 3L — [#471](https://github.com/tvofi/heatpump_optimizer/pull/471), [#473](https://github.com/tvofi/heatpump_optimizer/pull/473), [#476](https://github.com/tvofi/heatpump_optimizer/pull/476), [#478](https://github.com/tvofi/heatpump_optimizer/pull/478), [#482](https://github.com/tvofi/heatpump_optimizer/pull/482), [#484](https://github.com/tvofi/heatpump_optimizer/pull/484), [#486](https://github.com/tvofi/heatpump_optimizer/pull/486), [#488](https://github.com/tvofi/heatpump_optimizer/pull/488), [#491](https://github.com/tvofi/heatpump_optimizer/pull/491); wave 3L close-out — [#496](https://github.com/tvofi/heatpump_optimizer/pull/496), [#499](https://github.com/tvofi/heatpump_optimizer/pull/499); wave 1a — [#380](https://github.com/tvofi/heatpump_optimizer/pull/380); wave 4 — [#501](https://github.com/tvofi/heatpump_optimizer/pull/501), [#503](https://github.com/tvofi/heatpump_optimizer/pull/503), [#507](https://github.com/tvofi/heatpump_optimizer/pull/507).
- [#567](https://github.com/tvofi/heatpump_optimizer/pull/567) — **UX lane B, items B1–B5** (#559–#563). Establishes by execution that **mermaid does not render in HACS's in-app README view**: the chain is `hacs/integration` → `<ha-markdown>` with no `allow-svg` → `home-assistant/frontend`'s plain `marked` + `js-xss` worker, and this README run through HACS's own pinned versions yields zero `<svg>`. The entity count re-derives to **69, not the docketed 66** — the old pin compared the README against the literals it supplied, so it never saw `wood_cheaper` make a fifth binary sensor. In review.
- [#568](https://github.com/tvofi/heatpump_optimizer/pull/568) — **teaches the config-flow golden's fingerprint to recurse into `section()`**, the hard precondition for #223's registry. Corrects #516's body: `section` is in `homeassistant/data_entry_flow.py`, not `helpers/selector.py`, and has existed since 2024.7.0. The sharp finding: grouping moves the fixture **once**, then goes silent — field removal, addition and selector-bound rewrites all left it byte-identical afterwards. **33 one-level schema walks remain in the assertion layer** (`entities.py` 28, `config_flow_steps.py` 4, `features.py` 1) and fail the same way. In review.
- [#569](https://github.com/tvofi/heatpump_optimizer/pull/569) — **UX lane C, item C1** (#564): the chart's four contrast defects, measured in both stock Home Assistant themes with WCAG relative luminance and, for the two colours that share lightness, CIE Lab ΔE76 through a deuteranope model — because a contrast ratio cannot see that defect at all. In review.
- [#571](https://github.com/tvofi/heatpump_optimizer/pull/571) — **UX lane D, items D2/D3** (#565, #566): the English narrative priced in the instance currency rather than hardcoded Swedish, and `SensorDeviceClass.ENUM` with state translations for the string-state sensors. In review.
- [#572](https://github.com/tvofi/heatpump_optimizer/pull/572) — **merged `059881e`, closed #570.** Owner-approved and reviewed. GitHub cannot run the `claimnotes` driver, so a claim-file `DIRTY` blocks CI from queuing at all; a branch that claims nothing does not touch those files; the ratchet metric count is derived rather than stated (**24**, not the 22 the file had said); and `fix-review.md` gains step 13. Its own branch touched neither claim file, which is the rule it proposes. Residues in #574.
- [#573](https://github.com/tvofi/heatpump_optimizer/pull/573) — **#195 coverage tranche 1**, `climate.py` / `open_meteo.py` / `frontend.py` to 100 % statement coverage. Leaves #195 open; the brief's figures were 204 commits stale and were re-derived rather than carried. In review.
- [#540](https://github.com/tvofi/heatpump_optimizer/pull/540) — **merged `9da726a`, closed #524 and #525.** Home Assistant's loop detector fired twice on every install, at setup and at worker shutdown, both warnings telling the user to file against this repository; invisible to every lane in `tests/` because the stub has no loop protection. Reviewed at the fourth attempt — the first three blocked on process grounds and never reached the code, because the branch was `DIRTY` and its gate lanes had therefore never run (#570).
- [#576](https://github.com/tvofi/heatpump_optimizer/pull/576) — **UX lane B, items B6–B11**: eight figures, none drawn by hand — B6/B7 from the shipped card, B9 reusing `setup_qa_render.mjs`, B8/B11 calling production. Establishes that **`docs/*.md` is not HACS-rendered at all**, so the image constraints are README-only. **Collides with #567**, and the shape is worse than "git will stop". It does stop — `merge-tree` exits 1 on `tests/entities.py` — **but the conflict hunk does not contain the colliding code.** #567's `_readme_table_rows` loop and `README.md` both auto-merge; the conflict is between two unrelated adjacent additions, so a resolver is never shown what breaks. Resolved the natural way (keep both sides), the check then fails: *table has 63 row(s), there are 56* — 63 = 56 + 8 tables − 1 header. **The merge instruction is explicit: remove `("sensors", "sensor", "Sensors")` from #567's row-count loop and keep this PR's name-set check.** Reviewed `merge`. 
- [#578](https://github.com/tvofi/heatpump_optimizer/pull/578) — **#536, the hastub fidelity mechanism.** The highest blast radius in flight: every lane runs with `PYTHONPATH=tests/hastub`. In review.
- [#579](https://github.com/tvofi/heatpump_optimizer/pull/579) — **`Closes #542`**, the options-page data-loss bug. The defect class was derived by AST rather than taken from the issue body: nine option pages clean an entity key, eight clean only keys they present, and `learning` was **the only one** cleaning a key its schema never shows. All six named statements fixed. In review.
- [#586](https://github.com/tvofi/heatpump_optimizer/pull/586) — **W4-G10 / S9 continued**: `optimize`'s comfort envelope and power ceiling leave. In review.
- [#589](https://github.com/tvofi/heatpump_optimizer/pull/589) — opened after this record's last sweep; disposition owed in the next record.
- [#531](https://github.com/tvofi/heatpump_optimizer/pull/531) — this record. Blocked once: it claimed nine roster briefs had received a carried finding when only two had. The script used `str.replace`, which does not raise on no match, and printed success either way — the same shape as #523. The fix asserts the string changed and re-reads the file from disk.

**A pattern worth naming**, since most of these were blocked for it: every one of those blocks was a document asserting something that was not true of the tree — a stale head, a count, an actor, a carry that did not land. None was a disagreement about the change itself.

### The UX programme — 34 items, five lanes, tracking #558

Thirty-four graphics and interface changes the owner selected from a
forty-two item survey. **Tracking issue #558** carries every item; the
*Optimizer UX Docket* artifact is the source of record. Three items were
dropped and two reshaped so they stop being breaking changes — both recorded
there with reasons.

**The lanes run concurrently with the waves, and that is measured rather than
assumed.** `docs/` is an INERT prefix, so lane B selects zero test scripts.
`tests/structure.py` walks `*.py` only, so lane C moves no ratchet metric at
all — its only cost is a golden drift claim. Lane D is Python outside the
coordinator, so repo-wide budgets bind but `coordinator_loc` does not.

**Independence by budget is not independence by file.** The docket's original
claim was measured against the ratchet, which was true and incomplete: two
lanes share files with remaining wave stages.

| lane | items | collides with | on | sequence |
|---|---|---|---|---|
| **B** docs | 12 | — | — | **now**, concurrent |
| **C** card | 9 | — | — | **now**, concurrent |
| **D** ha | 6 | W5-G2 | `sensor.py` | **now** — Wave 5 has not started, so D lands first and W5-G2 re-measures |
| **E** flow | 4 | **W4 S11 (#223)**, W5-G3 | `config_flow.py` | **E1–E3 after S11**; **E4 (#516) now**, because its blocker is in `golden.py` |
| **F** post-W4 | 2 | S12/S13, W5-G4, W5-G7 | `coordinator.py` | **last work of the programme**, after #412 |

**Why E1–E3 wait.** S11 rewrites `config_flow.py` as a settings registry.
Landing the token masking, the finish-setup-now step and the `setup_overview`
move first means S11 restructures work that has just landed; landing them
after makes each one row in the registry instead of three separate edits.

**Why F is last.** It is the only lane that adds lines to `coordinator.py`,
where `coordinator_loc` and `max_class_loc` sit at zero headroom — three added
lines would fail two budgets and eat the headroom the seam stages need. It
therefore follows Wave 4, Wave 5 **and** #412, which makes it the final work
of the whole programme rather than merely late.

**How HACS eats an image, measured — this binds every figure lane B ships.**
`hacs.json` sets `render_readme: true`, and HACS rewrites image sources before
`<ha-markdown>` sees them. Three constraints, each established by running HACS's
own pipeline rather than by reading its source:

1. **A relative `src` is blanked** unless HACS rewrites it to an absolute URL.
2. **The rewriter's regex has no `s` flag**, so an image whose alt text wraps
   across lines is skipped — and then blanked. This caught the lane's own hero,
   which was written wrapped and would have shipped broken in the one view B4
   exists for.
3. **The rewriter's lookahead `(?!.*?://)` scans the whole line, not the link.**
   So a relative image that *shares a line with any absolute URL* is never
   rewritten, and vanishes. The construct that matters is exactly the one a
   figure lane reaches for — a figure linked to a larger version:

   ```markdown
   [![alt](docs/img/fig.svg)](https://example.com/full.svg)
   ```

   This is the same mechanism as the `(LICENSE)` badge defect, whose target has
   no extension and which HACS therefore rewrites into a broken link. Rule 3 is
   **not covered by the pin B1 landed**: all three such constructs pass it.

Establish separately whether `docs/*.md` is subject to any of this. HACS renders
the README; `docs/` may reach the reader only through GitHub, and a constraint
applied where it does not hold costs quality for nothing.

**Three sequencing rules inside the lanes**, each of which costs a red main or
a wasted PR if ignored: **C4** (the contrast witness) runs **last** in its
lane, because extended today it fails immediately on four measured ratios;
**C1 is one pull request, not four**, since the four colour fixes claim drift
over the same state list; and **B5 needs B4 landed**, or the README opens with
nothing where the flowchart used to be.

**#516 (E4)**'s original blocker is discharged — #520 raised the Home
Assistant floor to 2025.2.0, where `section()` exists. Its real blocker
survives and is sharper: `golden.py`'s `fingerprint` walks schemas one level
deep, so grouped fields would fall **silently** out of the fingerprint and a
byte-identical golden would prove nothing. That is the defect class #553 fixed
for the stored-value arm, and the capture work is in flight.

### Wave 1b, half I delivered 2026-09-04

Twelve PRs merged in sequence, `main` green after each, ending at `841fe0f`: #383 (W1-G1, #369 #370), #385 (W1-G10, #247 #248 #249 #250 #251 #252), #396 (truth-up), #384 (W1-G4, #373), #386 (W1-G5, #334), #397 (W1-G3, #372 #357), #399 (the #387 coverage-floor backstop), #402 (W1-G11, #246 #251 #395), #407 (operational docs), #409 (the ratchet-raise policy), #410 (the claim priority), #406 (W1-G2, #350 #374). **Released**: `v6.3.12` is tagged at `84a27b6f21690edcd340c6d74ff303c8e0774180`, now `origin/main`.

Half II (`.claude/workflows/wave-1b-groups.json`) started 2026-09-04 and completed 2026-09-05. **Released**: `v6.3.13` tagged at `f94ae13a75ed58ab53b70b5dbb13786c1c081a4c`, 2026-09-05. Eight fixer groups merged in sequence, `main` green after each; record PR #433 at `3bcea26`, inherited-card-claims fix `7044a27`, then stamp. Merge SHAs in the roster's `resume.merge_sha` fields. Record/tooling since v6.3.12: #414/#398, #415, #417, #418, #416/#411 (Wave 2 prerequisite), #420 (stress closure 64→22), #426 (W2-G2 citation re-anchor), #413 (brief corrections, W1-G16 added).

Wave 2 (`.claude/workflows/wave-2-groups.json`) forked at `f94ae13` and completed 2026-09-05. **Released**: `v6.3.14` tagged at `ef539bec138392217bce7d51c96e4c49d0e456c2`, 2026-09-05. Seven fixer groups merged in sequence, `main` green after each; record PR #450 at `6cc3318`, then stamp. Merge SHAs in the roster's `resume.merge_sha` fields. Record/tooling since v6.3.13 stamp: #434, #435, #439, #442, #443, #446, #448, #450.

Wave 3 (`.claude/workflows/wave-3-groups.json`) forked at `ef539be` and completed 2026-09-06. **Released**: `v6.3.15` tagged at `f0866c8e5600902276fd0fb32e3e1d5f64f0a0c2`, 2026-09-06. Three fixer groups merged in sequence, `main` green after each; record PR #468 at `7f5b674`, then stamp. Merge SHAs in the roster's `resume.merge_sha` fields. Record/tooling since v6.3.14 stamp: #452, #458, #459, #468, #469. Unstamped #451 from v6.3.14 included in this stamp.

### The #387 blocker, 2026-09-04

**Fixed 2026-09-04, merged as `32f309f` (PR #388), released under the v6.3.12 framing decision above.** The reasoning below is kept because it is what the fix rests on, including the "one CI runner is not the fleet" lesson.

`main` is red on roughly half of all merges and the v6.3.12 stamp is blocked
behind it, from a regression this programme itself introduced in #346 / PR #378
and released as v6.3.11. Every push to `main` forces `GATE_SCOPE=full`, so
`tests/stress.py` runs on every merge; its coverage check demands **≥ 40 of 51**
scenarios land in a *recorded* solver basin, and on a runner whose basins are not
the recorded set it gets **29**.

Exactly 22 entries in `tests/stress_budgets.json` carry an `alt_basins` list, and
exactly those 22 flip together — one cause (the CPU model and its BLAS kernels
choosing the multi-start basin), one cohort. The floor was sized on the
assumption in its own comment that "a third platform may hold a third basin *for
some scenario*", i.e. that the misses are per-scenario and independent, leaving
eleven scenarios of slack. They are not independent. Four full-scope pushes after
#378: two green, two red, on commits differing only in INERT paths.

The owner chose **the `env_drift` shape** — capture each scenario's solver work
twice in one run, tree and merge base, compare computed against computed, no
basin table — at an accepted **≈ +500 s** on full-scope runs, and chose to fix it
**alone before anything else merges**. Recording the observed basins was rejected
as a treadmill (the `ubuntu-latest` fleet is heterogeneous and not enumerable, so
each new runner model contributes another basin for all 22); lowering the floor
was rejected as discarding what #346 existed to buy.

The general lesson, which the remaining gate-instrument groups are now reviewed
against: **one CI runner is not the fleet.** #378's reviewer asked exactly the
right question — whether a 2× regression is still caught on a machine whose
basins are not the recorded set — and the answer was measured on a single runner
and generalised.

### What triage changed, 2026-09-04 (batch B2)

Three read-only judges, run on this idle box (`load1` 0.17–0.58, `thread_factor` 1.00) at
`291ae76`. Two of the three overturned a brief this plan had already written, so the
corrected version is recorded here as well as on the issues.

- **#258 is re-scoped, and W1-G13's brief was wrong.** #333 did fix the clipping half:
  `units_with_ink_on_top_row` **12/12 → 0/12**. But its `uy` clamp traded the clipping for a
  new ink collision — the value-axis unit and the top tick of its own axis overlap by
  **1.00–1.25 px vertically and 4.0–8.5 px horizontally** on every tile that engages the
  font floor, **9 of 13** measurable pairs, leave-one-out **9 of 9**. This plan's hypothesis
  (a horizontal right-axis unit at `ux = x + 5` running past the viewBox) is **refuted**:
  right-edge headroom is −21.5 to −80.7 viewBox units and `ink_at_right_col` is false in
  every arm. The residual is vertical, not horizontal, and W1-G13's brief has been rewritten
  to say so. The finder's `card_geometry.mjs` is **void** for this row — its
  `text_overlap_pairs` reads 941 before and 941 after a perturbation that takes the collision
  9 → 0. The measured fix is `plotT = Math.max(MARGIN.top * marginScale, font * 1.45)` plus
  the `uy` offset 4 → 5.2; raising `plotT` alone does not work because `uy` tracks it.
  **No committed check can see this defect**: the DOM stub returns a constant 900×400 rect so
  the font floor never engages, the browser lane measures fonts and hit targets and never
  label proximity, and CI run 33829697839 at `291ae76` is green with the defect present. The
  fixer's failing test must therefore be a real-Chromium proximity check in the committed
  browser lane, or the fix ships without a witness.
- **#304 is re-scoped to 21 named statements, and its mechanism is refuted.**
  `config_flow.py` measures **96.2 %** (547 statements, 21 missed) — the third independent
  measurement to land on that figure, across two Python versions and two coverage cores. The
  body's mechanism (“no test submits `async_step_user` with input”) is false:
  `tests/config_flow_steps.py` is unconditional in `run.sh` and drives all three token
  verdicts plus `create_entry` through the real validation path, 89 checks passing. What made
  the gap look open was the frozen `coverage_suite.sh`, whose hand-typed `SCRIPTS` list omits
  that script — the same instrument-rot class as #334. All 21 residual statements are
  reachable by extending the existing harness with **no production change**; the largest
  single bite is 6 of 21, one repeated `return vol.Optional(key, default=existing)` idiom
  across six options pages.
  **Sequencing consequence:** #304 lands *before* the #223 registry stage, not in
  Wave 5. (That stage is numbered S11 here and S10 in #193's own stage list; the
  issue number is the stable reference, not the stage number.) #223 rewrites
  exactly those six options pages into a registry, so the coverage extension is the witness
  S11 needs, and writing it afterwards would mean writing it against code that has already
  moved.
- **#242 is weakened to a structural zero, and W3-G4 is struck.** The derivation spike
  returned **no admissible candidate**, and the obstruction is analytic rather than a
  coefficient that needs tuning. The base curve's log-slope budget is **+0.03030/K at 0 °C
  and exactly 0 above +27 °C**, while any ratio anchored on `(T_ref − T_out)` contributes
  **−0.01429/K at 0 °C, −0.04667/K at 20 °C** and diverges as `T_out → 35 °C`. The 0.0000 SEK
  plan consequence is therefore structural, not a sampling artefact: **189,882 Carnot-branch
  calls** across all nine shipped cells, every one at `T_out ∈ [−16, −8] °C`, against a
  coldest turnover of **+9.96 °C** — a 17.96 K margin. Wave 3 loses its fourth group; the
  physics half of the issue stands as verified and documented.

### What triage changed, 2026-09-03

The judges overturned this plan three times, which is what they are for. Recorded here
because the corrected version is what the waves now execute; the full numbers are in the
judge comments on each issue and summarised on #201.

- **#195 was not superseded and is now fix work.** #304's judge comment is aggregates, not
  the per-module table #195 asked for, and the only committed table on main is the stale
  88.4 % artefact. Re-measured: **89.7 %, 23 of 48 modules under the 95 % bar, and
  `coordinator.py` alone is 789 of the 1,338 missed statements** — 59 % of the deficit, so
  its half sequences behind the #193 seams. The leave-one-out is the planning fact:
  `validate`, `edge`, `backtest`, `optimality` and `plan_view` each move the total **0.0
  points**, so coverage cannot be bought with end-to-end scripts.
- **#325 is not an accepted limit.** The settle hour buys the identifiability — discrimination
  0.036 (below its own null floor) to **0.288** — but only if the settle hour's real delivered
  power is recorded. `sysid.step()` hard-codes 0 kW, and admitting those rows unchanged makes
  it *worse*: 0.012, with a −0.064 UA bias on an honest install. Record the power first,
  widen the filter second.
- **#334's residue was inverted.** `D6/claims.py` is repaired; **`D9/d9lib.py` is the one still
  dead**, in ten files. The README has contradicted `HARNESSES.md` since #348, and no file on
  main names the SHAs the tag moved between.
- **#277, #244 and #325 are one group**, three views of one lead in `sysid.py`'s
  `step()`/`identify()`; splitting them would lose #325's ordering constraint.
- **The Wave 4 order was inverted, by the ratchet's own numbers.** The plan of
  record put DHW before fetch. The measured cut costs on main read
  **views 120 < fetch 132 < dhw 195 < grid 236 < learning 350**, so the stages
  now run in that order. A stage is never justified by cut cost alone: three
  tools give three different orderings of the same class, so cut cost is a
  property of the partition rule rather than of the code.
- **The context object separates nothing, and #377 says so.** The round-2
  comment justified extracting the six hub attributes by citing a separability
  result. Leave-one-out overturns that reading: drop **all six** and 200 of 254
  methods remain one connected component, with every other component a
  singleton. What it is actually worth is a cut discount — **189 of 1,033
  cross-seam references, 18.3 %, changing no rank** — plus the deletion of a
  coordinator back-reference every later stage would otherwise need. It goes
  first because it relocates no method body, so no open fix can be silently
  reverted by it.
- **`optimize` is the most decomposable of the five monoliths, not the least.**
  The plan assumed the opposite. It has five ratchet-clean verbatim blocks at
  6–11 interface cost, the first being 64 lines at 6 in / 0 out after the solve,
  where no hot-loop question arises. The real carrier case is only the DHW tail,
  and it wants a dataclass of the 14 keys the method already returns rather than
  a state object threaded through. Constraint that decides the cuts:
  `functions_cc_over_15` sits at 39 of 39 with zero headroom, so every extracted
  helper must come in at or under complexity 15 — the otherwise obvious cut is 18
  and fails the gate.
- **#225 is closed, not re-scoped.** Its two named targets measure worst-boundary
  37 and 30 live locals inside the batched objective the gradient solver
  evaluates, no cold target remains above the 150-line mark, and `ThermalModel`
  binds no ratchet metric at all — the class contributes 3 of 23 oversized
  methods, behind the coordinator's 8 and the optimizer's 7.
- **#303 now has a ruler that cannot be gamed**: with the stub excluded by
  construction rather than subtracted afterwards, main measures **427**
  production-only strict errors, against 743 with the test fake — so 42.5 % of
  the historical headline was an artefact of a fake class. One correction to the
  brief it was given: `--warn-unused-ignores` does **not** prevent
  ignore-stuffing, since four real annotations and four live ignores move the
  count identically, so the ignore count has to be its own hard metric.
- **#197 and #233 closed**, each with a sharper reason than the plan's: 160 mypy errors was a
  *different ruler* (non-strict) rather than a stale count, and #233's restart gap fails its
  own flat-price null at both 24 and 48 hours.

## Standing rules

Unchanged from the repository's own protocol; restated here because a fresh
session reads this file first.

- **Fixer** (`tools/audit/briefs/fixer.md`): failing test first, importing the
  production symbol; mutation proof pasted into the PR body; the finding's own
  harness re-run before and after at the measured head SHA; a null control on
  every cost, gain or time claim; a learner or guard measured at both ends of
  its range; claims only for drift you measured; the scoped gate green locally
  through the gate lock; never `VERSION`, the manifest version or the
  `RELEASE_NOTES.md` heading. **After any rebase, steps 2–4 are re-executed** —
  the evidence describes one tree and a rebase makes a new one.
- **Reviewer** (`tools/audit/briefs/fix-review.md`): a fresh worktree at the
  head SHA, the mutation proof re-run, the measurement taken with the
  **finder's** harness rather than the fixer's, `env_drift.py --all` against
  the claims, and an attack at other configurations. Verdict `Fix review:
  merge` or `Fix review: blocked — <why>`. A reviewer never ranks below its
  fixer.
- **Claims.** A branch that moves fixtures claims them with a direction; the
  check is three-dot, never two-dot. A name cannot be both claimed and
  `may-drift`. Value-bearing fixtures are **never re-recorded on this box** —
  only an environment that records them all can honestly re-record one — so
  value drift is claimed and `golden.py --record --only` is for new key paths.
- **Stamps.** Only `tools/release/stamp.py --push`, only after the merge
  commit's own `fast` and `closures` are green, with a notes section naming
  every PR since the last tag. Never by hand, never in a branch. No new branch
  is cut between a fixture-mover's merge and its stamp.
- **Ratchet.** `python3 tests/structure.py` before every push. A change that
  adds coordinator lines pays for them elsewhere, re-records with the reason
  in the commit, or — for a genuine new production feature whose lines cannot
  honestly be paid for elsewhere — **raises** the budget because the capability
  is worth the structure it costs. All three are a decision, not bookkeeping,
  and all three carry their reason in the commit message. A raise additionally
  **requires the repository owner's explicit confirmation before the branch is
  pushed**: it is not a fixer's, a reviewer's or a judge's call, so an agent
  that wants one stops and asks. It is not a route for accommodating
  sloppiness, an unexamined refactor or an unmeasured feature — the first
  question is still whether the lines can be paid for elsewhere — but a metric
  at zero headroom is not a veto on new capability either (#398 read it as
  one). `cross_seam_fraction` carries a
  tolerance band and is never re-recorded: within the band there is nothing to
  record, outside it the gate fails, so a re-record can only loosen.
- **Ownership.** `owner:<session>` and a `claimed-by:` comment before a branch
  is cut. An unlabelled issue is *unknown*, not free.
- **Every fix PR body**: `Closes #N`, `Part of #201`, the head SHA measured,
  and every executed number.

## Model routing

Every seat in this programme — orchestrator, fixer, reviewer, judge, recorder —
runs as a **Claude Code subagent** inside one Claude Code session. `claude-web`
(label `owner:claude-web`, branch prefix `claude-web/`) is the session identity,
kept for continuity with the branches already on origin; since 2026-09-06 it is
also literally the runner.

The orchestrator seat is this session's parent (Opus 5), which executes
`web-fix-wave.js`'s control flow by hand. Workers are Claude Code subagents:

| seat | model | when |
|---|---|---|
| orchestrator | **Opus 5** | control flow, merges, reconciliation, all sequencing decisions |
| architectural fixer + its reviewer | **Opus 5** | W2-G1, W2-G2, every Wave 4 and Wave 5 move PR and its review |
| per-stage survey | **Opus 5** | the survey that precedes a move stage; the halt decision is the product |
| adversarial reviewer, `fix-review` with the **finder's** harness | **Opus 5** | every group whose brief carries a refuted or corrected claim; every fixture-moving group; every move review |
| judge | **Opus 5** | all triage judges, including the #291 and #232 timing judges (still solo on an idle box), and any decomposition judgement |
| fixer on production code, mutation proof required | **Opus 5** | groups the wave file marks `"fixerModel": "opus"` |
| fixer on tests, tooling or docs | **Sonnet 5** | groups the wave file marks `"fixerModel": "sonnet"` |
| record / roster / truth-up / citation-freshness PR | **Sonnet 5** | mechanical docs edits; no measured claim of their own |
| read-only reporting | **Sonnet 5** | Reconcile, post-merge gate watching, the pre-merge checklist, label hygiene, release-notes source material, issue digests, wave inventories, the #303 typing and #195 coverage inventories |
| stamp | scripted `stamp.py` via `web-stamp.js`, drafted by **Sonnet 5** under orchestrator oversight | rule 4 refuses notes omitting a merged PR, and the refusals are the product; the orchestrator reads every refusal |

**Routing moved to Claude models on 2026-09-06**, at the W4-G3 merge (`d979110`).
Delivery-status rows for groups delivered before that date name the model that
actually ran (Grok 4.6 extra high / Composer 2.5, under a Cursor Multitask
parent) and are left alone: the delivery record says what happened, not what the
routing is today. Rows for groups not yet started carry the table above.

**Fable 5.1 is deliberately routed nowhere.** No seat needs a tier above Opus 5,
and every seat that historically took Fable is an architectural fixer or
reviewer, which is Opus 5 already. The absence is a decision, not an oversight.

**The tier tokens in the wave files now map literally.** `web-fix-wave.js` ranks
`haiku < sonnet < opus` and throws if a reviewer ranks below its fixer, so the
tokens stay as they are: `opus` → Opus 5, `sonnet` → Sonnet 5, `haiku` →
Haiku 4.5 (unused today). `tierOk` still applies. The tokens do not need editing.

**`.cursor/rules/*.mdc` still hold three `alwaysApply: true` policies, and
nothing loads them for a Claude seat.** Cursor applied them automatically;
Claude Code loads `CLAUDE.md` and nothing else. The files and every pointer to
them stay — every seat is told to open all three at seat start, and `CLAUDE.md`'s
summaries are not a substitute.

**An architectural reviewer on the same model as its fixer is still a fresh
agent, not the fixer continuing.** Independence here is procedural, not
model-family: the reviewer works in a fresh worktree at the head SHA and
measures with the **finder's** harness, per `tools/audit/briefs/fix-review.md`.

## What the runner changes

This section was written for a 4-core cloud container with no `gh`. **Since
2026-09-06 the programme runs on the owner's 8-core M1 again, with `gh` 2.98
authenticated**, so the first two bullets are history rather than instruction:
`gh` is used directly, and the REST fallback is a shipped capability nobody has
to reach for. The rest still stands and is why it is kept.

- every GitHub action went through the GitHub MCP tools **on the container**;
  on the M1, `gh` is used directly;
- `tools/release/stamp.py`'s rule 2 gained a REST fallback (Phase 0), because
  it shells out to `gh` before any flag is read and would otherwise have made
  stamping impossible there. It is still in the script, and still correct;
- the drift baseline cache starts cold, so the first `env_drift --all` per
  fork pays a full baseline capture — hence one fork per wave;
- at most two agents run at once, and anything needing a quiet box (the
  stress ruler, the timing judges) runs alone;
- **the gate lock is scoped to the runs that need it.** `fixer.md` step 5
  mandates it for every local gate; that was written for a dedicated
  eight-core machine, and on a shared container it serialises every agent.
  The lock exists for one script — `tests/stress.py`, whose solve-time guard
  measures the machine while it solves — so the rule now asks
  `closure.py select` what the diff actually runs and takes the lock only
  when the answer includes `stress.py`, reports `MODE: FULL`, or fails.
  Measured on this tree: a test file selects one script, the card five, and
  none of them `stress.py`; `optimizer.py` and `coordinator.py` select
  sixteen and do. The trap the rule is written around is that a gate file or
  an unmapped file prints **zero** selected scripts while meaning *run
  everything* — so it keys on the mode line, never on the count. What is run
  locally regardless is the evidence CI cannot produce: the mutation proof,
  the failing test at the merge base, and the finder's harness;
- `tests/card_browser.mjs` runs locally against the pre-installed Chromium
  (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`) but CI's `browser` job is the
  authority, because the local Playwright is not CI's pinned version.

## When a merge turns main red

The programme has been in this state, so it gets a written answer rather than a
judgement call each time. `web-fix-wave.js` logs `MAIN IS RED after <group>` and
stops merging; `audit-merge.js` returns `{green:false}`. What follows:

1. **A behaviour change in the merged diff → revert first, diagnose after.** The
   revert is cheap and main being trustworthy is what every later merge is judged
   against. Re-land with the fix and the evidence.
2. **A failure the diff cannot reach → do not revert.** Establish it first, the
   way the register requires: an error naming a subsystem the diff does not
   touch, reproducing identically, or red on the base branch too. Then it is its
   own issue with its own number, and the wave holds until it lands. #387 is the
   worked example — a released gate instrument that was runner-dependent, found
   only because main went red on roughly half its merges.
3. **Never `--allow-red` to get a stamp out.** The flag exists for a human with a
   reason, not for an agent with a deadline.

A red main is work *now*, at every wake, whatever else is running: only a green,
mergeable head waits on reviewers.

## Documentation discipline

So that an aborted session loses nothing:

| When | Where |
|---|---|
| before a branch is cut | the issue: `owner:claude-web` + `claimed-by:` comment |
| after the failing-test commit, and after every commit | the branch is pushed |
| PR opened | the issue: PR link and head SHA |
| reviewer verdict | the PR: `Fix review: …` with RESULT lines |
| cannot finish | the issue: `state at stop:` naming branch, pushed SHA, last green check, what is missing |
| wave end | this file's Delivery status, `docs/audit-2026-09.md` status cells, a #201 comment |
| a merge that settles a decision, corrects the record or leaves work owed | `docs/HANDOVER.md`, in that merge's own PR |
| stand-down | a #201 comment — running seats, unpushed branches, next action. Durable state is already in `docs/HANDOVER.md` and is not repeated |

The per-group briefs are committed too, not only the wave tables above:
`.claude/workflows/wave-1b-groups.json` holds all fourteen Wave 1b groups as
`web-fix-wave.js` consumes them, cut from the same fork. They are worth reading
before re-deriving anything, because several exist only to stop a fixer redoing
work a judge already refuted — W1-G13 names the measured fix for #258 and the
harness that must not be used to check it. Wave 3L is `.claude/workflows/wave-3l-groups.json`. Wave 4 is `.claude/workflows/wave-4-groups.json` (S0–S8 and S10; next W4-G10). Wave 5 roster is prepared at `.claude/workflows/wave-5-groups.json` (seats not started).
