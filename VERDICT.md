Fix review: blocked 7e9fea6acb929bf8eecd279096d99fafb208ac56 architecture-unsound: a heat-counter install with the electric energy counter but no power entity never folds its span COP -- _fold_measured_cop returns no_measured_power before its counter branch, so clean["cop"] is False every cycle and close_span's cop gate stays shut; the approved design names four span gates and says a counter install folds at the span close

bus-nonce: b788d427003319cd773da96106e8b7d5

# Fix review: PR #2854, R10-HEAT-METER (#2261), XL

Round 3 (the dispatch's review worktree is `rev-2854-r3`). Measured at
`7e9fea6acb929bf8eecd279096d99fafb208ac56`, merge base
`3b4180dcc680e2e2e06f4d8ed0a0839a7374d78f` (`git merge-base origin/main HEAD`,
re-computed at publish time; `origin/main` is now `6fe5170cd`, three merges
past the base the body names). The head is `ci: pin killed mutants` by
`github-actions[bot]`, parent `a0ffc44074711bb4fbff35d509d26ee0230ab730` (the
head the body names), 44 ledger files, no production line. Evidence in
`evidence/`, `HEAD.txt` naming the head.

This review blocks. Two findings, the first in the routing line.

## Finding 1 (architecture-unsound, first line): no span COP on a heat + energy counter install without a power entity

The group's brief: "when both meters exist, measured COP (heat delta over
electric delta) is the COP sample". The approved design note: "On a counter
span, the electrical figure is the electric counter delta. With no electric
counter, the fold refuses with `COP_REFUSED_UNALIGNED`" (line 120), and
"On a counter install, COP folds at span close, not per cycle" (carry
R10-COP-GATE, line 212). The design's per-cycle gates are four: frozen, frost,
distorted, duty floor (line 118). The body itself says: "The per-cycle fold
runs its gates and stops at `COP_REFUSED_SPAN_OPEN` ... at the close
`_async_learn_heat_span` folds heat over electricity on the two deltas".

The code at this head does not do that on an install with
`heat_pump_heat_energy_entity` and `heat_pump_energy_entity` configured and
no `heat_pump_power_entity`:

- `coordinator.py:5091` — `_fold_measured_cop` returns
  `COP_REFUSED_NO_POWER` as its **first** check, before the counter branch at
  `coordinator.py:5113` (`if heat_energy.meter_of(self).counter: return
  COP_REFUSED_SPAN_OPEN`). `_measured_power` is `None` on that install:
  `coordinator.py:6473` reads only `CONF_POWER_ENTITY`, and its own comment at
  `coordinator.py:5634` says "Observed COP (a power entity only)".
- `coordinator.py:5642` — `clean["cop"] = self._measured_cop.refusal ==
  COP_REFUSED_SPAN_OPEN`; with the refusal above it is `False` on every cycle,
  and `HeatEnergyMeter.settle` ANDs it across the span.
- `heat_energy.py:512` — `close_span` sets `cop = bool(ev.clean.get("cop"))
  or e is None`; with the heat and electric deltas present `e` is a
  `SpanEnergy`, so `cop` is `False`.
- `coordinator.py:1102` — `if close.cop:` is then false, so
  `_fold_cop_evidence` is never called: `_cop_samples` (incremented only at
  `coordinator.py:5178`) never rises, `_measured_cop` never records, and the
  span's measured COP is silently absent for the life of the install.

Executed proof (this seat's probe, disclosed as its own instrument,
`evidence/probe-no-power-head.txt`): P1 the real `_fold_measured_cop` returns
`no_measured_power` with no power entity; P2 the clean gate is `False`; P3 the
span is valid on both arms (heat 9.0 kW, elec 3.0 kW, no refusal) and only the
gate differs; P4 with a power entity `close.cop` is `True`, without it `False`.
4 checks, 0 failed. So this is not a claim about intent: the shipped gate
chain produces it.

This is a departure from the approved note, not the note's own rule: the note
adds a fifth gate (`no_measured_power`) the design does not name, and that
gate is the one that defeats the fold on the install shape the brief promises.
The consequence is user-visible and documented as working: `strings.json`'s
option description ("With the energy meter it makes efficiency an
observation") and `docs/configuration.md` ("efficiency is measured as heat
over electricity for the span") are false on that install, and the body's
consumer-1 sentence is false there. No check covers the configuration:
`tests/features.py:70836` `_he_cop_span` always passes
`heat_pump_power_entity="sensor.hp_power"` and sets `c._measured_power =
elec_kw`; its `energy=False` arm is the design's `unaligned_meters` case, not
this one.

The design's own remedy, smallest diff: make the counter branch precede the
power check (or make the no-power refusal conditional on `not
meter.counter`), so a counter install returns `COP_REFUSED_SPAN_OPEN`
regardless of the power sensor and the four named gates still AND across the
span. Add the features case: heat + energy counters, no power entity, one span
sample exactly heat/elec, and its null (heat = model COP x electricity)
holding the scale. Either way the body's consumer-1 sentence needs the
install named.

## Finding 2 (class-open): the body's own seam rule returns seams it does not disposition

The body's step-8 rule is
`git grep -n "_commanded_split()\|dhw_share\|space_share" a441d2e15 -- custom_components/heatpump_optimizer/coordinator.py`,
and the body's sentence claims "each now asks `heat_energy.attribution`
(`_interval_measured_heat_kw`, `_cop_reference_curve`, `_accumulate_energy`,
`_settle_interval_diag`)". Run at the body's ref (a441d2e15) and at the head,
the rule returns seams outside that list:

- `coordinator.py:885` (`_fold_flow_lift`) reads `_commanded_split()` at the
  head; untouched by the diff; not named in the body.
- `coordinator.py:4782,4803,4833,4840` (`_commanded_power` and its readers),
  untouched, not named in the body.
- `coordinator.py:9855` (`draw_range.fold`'s plan split), untouched, not
  named in the body.
- `coordinator.py:1091` passes the plan split to `close_span` (by design, but
  still a returned line the body does not list).

The design note dispositions `_fold_flow_lift` and `_commanded_power` as
out-of-scope ("these concern the plan's ask", line 154) and does not name
`draw_range.fold`. fixer step 8 requires **every** returned seam in
`## Figures` against a disposition (closed here, already guarded, or a
distinct finding id); the body does not list them, and its sentence reads as
if all of them converted. That is `class-open` by fix-review step 6's letter.
The material risk is not bookkeeping only: `_fold_flow_lift`'s gate is a duty
classifier ("the curve is a SPACE heating curve; a hot-water interval runs the
supply at the tank's charge temperature"), it reads the **commanded** split,
and this PR's whole point is that the interval's duty is now **observed**
(`heat_energy.meter_of(coord).attribution(...)`, the owner every other split
site asks). Where the plan commanded space-dominant and the live mode was DHW
for the interval, the gate still folds the tank's supply reading into the
space curve bias. I state that consequence as read-level, not executed: the
code fact is the predicate's input, and the observed duty it ignores is on the
same coordinator.

Remedy: put the rule's full output in `## Figures` with each seam's
disposition, naming the design's out-of-scope list for `_fold_flow_lift` and
`_commanded_power` (and `draw_range.fold` with it), or convert the duty gate
to the attribution. The second touches `coordinator.py` outside this group's
owning seam and needs the orchestrator's after-edge first.

## What I verified (findings and numbers)

- **Mutation (step 1, step 11).** CI's lane is the authority: `tests / mutation`
  `success` at the head, check-run `121826424174` (20:23:50Z) and
  `121826323731` (20:23:39Z). This seat's targeted mutants, its own instrument
  on private copies of `heat_energy.py` (`evidence/mutants-seat.txt`, harness
  `harness/rev_heat_meter.py`): null row passes 17 checks; 14 mutants, 14
  killed, 0 survivors — C1 R15, O/L/P R4, U R6, G R7, I R13, R R9, Q R12,
  A R17, M R14, N R11, D R16, H R10. A missing harness summary is an
  instrument error, not a survivor.
- **Harness (step 2, step 9).** This group has no finder's harness (owner
  feature request; the fixer discloses its own in the body). I built my own
  and disclose it: `harness/rev_heat_meter.py`, 17 checks, 0 failed at the
  head (`evidence/harness-head.txt`), importing the production module only,
  driven through the production `close_span`:
  R1 elapsed-time 1.0 h spans at the plant's rates (5 spans, 4.5/1.5);
  R2 delta conservation (22.5 kWh over 5 spans);
  R3 null no counter (no span, no refusal, counter False);
  R4 20/40 split at `last_changed` (space 1.5 of 4.5);
  R5 null no mode change (observed, all space);
  R6 unseen excursion unobserved, plan split governs;
  R7 last-good read unobserved;
  R8 combination mode unobserved, duty map;
  R9 reset refused at span 4, next spans read 4.5;
  R10 rollover past 1.5x nameplate;
  R11 exactly 1.5 h read, 1.6 h `span_too_long`;
  R12 resolution bound: 1.5 accepted, 2.0 refused at EPS 1.0;
  R13 point reading never time-split (2.0 integrated);
  R14 unaligned electric counter refuses COP, heat still replays;
  R15 `close_after_h` 0.95 (0.5 h) and 1.2 (0.25 h);
  R16 `cop_duty`/`dhw_share`;
  R17 gates ANDed across the span (one dirty cycle refuses house, lower still
  replays).
- **Both-ends/null (step 3).** R3, R5, R12's edges, and the probe's P3/P4
  both-arms row above. The design's own null (heat = model COP x electricity
  holds the scale) is the suite's, green in CI.
- **Claim files vs actual drift (step 4).** `tests/env_drift.py --all`
  against the merge base (`evidence/envdrift-all.txt`): 56 scenarios
  captured from branch and baseline; `config_flow` CLAIMED with exactly the
  three leaves the note names (`_seed.heat_pump_heat_energy_entity`,
  `_seeded.entities_metering.meters.fields.heat_pump_heat_energy_entity`,
  `entities_metering.meters.fields.heat_pump_heat_energy_entity`, each
  "present on one side only"); 55 value-only diffs reported never failed; no
  committed fixture stale; `NO UNCLAIMED DRIFT`; `NO STALE FIXTURE`. All five
  coordinator captures (`coord_all_features`, `coord_dhw`, `coord_grid_fee`,
  `coord_minimal`, `coord_two_zone`) byte-identical to the merge base, which
  is the design's null for an install with neither counter nor mode entity.
  The claim-file diff is one replaced line in `claimed_drift.txt`; the card
  file is untouched (no card change, so no `card_drift` run); `claims-for:
  7.0.4` on both files equals `VERSION` 7.0.4.
- **Versions (step 5).** `VERSION`, `manifest.json` and `RELEASE_NOTES.md`
  byte-identical to the merge base.
- **Head and carry (step 7).** Body names `a0ffc4407`; the measured head is
  its child `7e9fea6`, the autofix pin commit the body says will follow the
  push ("the remaining 44 are pinned by `mutation-autofix` after the push").
  Verified: parent, author `github-actions[bot]`, 44 files, ledger only.
- **Figures re-derived (step 8).** `tools/pr/ci_predict.py --base
  3b4180dcc680` at the head prints no unpinned-site line, which its code emits
  only for a non-zero count: **0** added unpinned sites at this head (the
  body's 44 are pinned). `tests/structure.py` at the head: `STRUCTURE RATCHET
  PASSED`, all rows at budget (`coordinator_attrs` 142, `multiassigned` 109,
  `max_class_loc` 8181, `seam_cut_total` 423 — `evidence/structure-head.txt`).
  Not re-derivable at this head, and stated as such: the body's `## Figures`
  are at `db4493c3e` / base `0137c4cb0` (4494 feature checks, 31 scripts, 4
  seat-local failures, 44 unpinned, structure 143/110/8236/424 recorded down
  to 142/109/8186/423). The body's sentence "main moved none of them" is
  stale at the current base: main's own commits moved `max_class_loc`
  8236->8181 and `class_excess_loc` 18079->18076 down, and the head's budgets
  now carry those lower rows (checked: every row in
  `tests/structure_budgets.json` moves down or stays, none raised).
- **No finder's harness / disclosure (step 9).** Stated above; the fixer's
  own instruments are disclosed in the body, mine here.
- **Forward-carry (step 10).** The three carries the body names are in their
  destination briefs on `origin/main` in
  `dev/programme/rosters/wave-r10-groups.json`, each with its control as a
  precondition: R10-COP-GATE carry 11 (span_open rendered as open; control:
  a counter install's span shows measured COP while cycles read span_open);
  R10-UX-HEALTH carry 16 (Health string for span_open and the span refusal
  codes; control: the panel mid-span renders the string); R10-REPLAY-REAL-DAY
  carry 4 (`unhealthy_input`; controls: an all-reporting week names none, one
  silent input names that input). The group's own carry 5 is met where the
  design says it is: `tests/features.py:71037` — "the ledger and the diagnosis
  triple split by the same observed dwell (one third space)": space 0.5, dhw
  1.0, realised electrical 1.0.
- **Red checks (step 11).** Check-runs at the head, all concluded
  (`evidence/check-runs-head.txt`, ids and timestamps in it): one red,
  `gate` `121847065820` (started 21:04:06Z, concluded 21:16:09Z). Its log
  (`evidence/gate-red-log.txt`): `FAIL run(s) [40395153198] at this head are
  still being judged; their gate decides` — a twin-wait refusal to grade, not
  a graded failure; the twin `gate` `121853927269` is `success` at 21:17:46Z
  on the same head, and `pr-contract` `121853533166` is `success` at 21:16:58Z
  after the red concluded, i.e. the body at this head passed the contract
  check. Every other check on the head is green, including `tests / fast
  (3.14)` `121826660712`/`121826545644`, `tests / closures`
  `121826661144`/`121826545529`, `tests / mutation` above, `tests /
  coverage-ratchet` `121841429677`/`121841400480`, `tests / claims` family
  skipped where it has nothing to do, `governance / record` skipped,
  `nightly-status`/`delivery-status` green. No root-cause trigger: the only
  red is a queue refusal, answered by its twin's green, and no cheaper
  detector could have pre-empted it.
- **Merge state (step 13).** `git merge-tree --write-tree origin/main HEAD`
  exits 0 (tree `4aa1b5e173e4b345604d8855db4a9502eb02cf4c`) against the
  current `origin/main` `6fe5170cd`, so there is no conflict and the claim
  driver is not invoked. No `MERGE-CLAIM` marker.
- **Metric movements (step 14).** Mechanism the body names: the day-health
  flag moved onto the snapshot ring, and the span close/replay/cycle read
  moved into `heat_energy.py`. Removed as the null: the moved-out
  coordinator body no longer sits in `coordinator.py`, so the attribute count
  falls by exactly the one attribute that moved (143->142, 110->109), and the
  archscore `dS +0.0131` is that same `coordinator_multiassigned_attrs`
  110->109 (`evidence/structure-head.txt`, archscore block). No row raised;
  every budget row moves down or holds. Ledger deltas: the two
  `_fold_cop_evidence` triages moved from `_fold_measured_cop` (same mutant
  ids), plus one new `resolution_refusal.RETURN_DEL` triaged equivalent on
  every input; no killable survivor triaged.
- **Architect/design note (step 15).** Finding 1 is the departure; the four
  design points and the design review's two carries are otherwise met:

  A (span closes on elapsed time, allowance, max refusal): R15, R11, and the
  five byte-identical coordinator captures.
  B (per-learner gates ANDed, ventilation per-cycle, no window counted twice):
  R17 and the earned-basis save/reload check at `tests/features.py:70966`;
  `replay_gate`/`spans_own_scale` are the one owner.
  C (a point reading is never time-split): R13.
  D (no version bump or migration; the basis is the existing choice field,
  missing reads unearned): `VERSION`/manifest/notes untouched; `store.py`
  changes are the basis `unread` string and the `unhealthy_input` snapshot
  field, no migration.
  dr3-earned-in-memory: `_heat_loss_anchors` reads `meter.earned`, and the
  save/reload/save-after-earn check is in the suite.
  dr3-eps-at-span: re-measured at the ~1 h span in the fixer's harness; I
  re-derived the shipped bound's edge only (R12: 1.5 reads, 2.0 refuses at
  EPS 1.0). The integer-counter means/sds in the body are the fixer's
  instrument, not re-run here.

## Not established

- The body's `## Figures` at its older base (4494 feature checks, 31 scripts,
  4 failures, 44 unpinned sites, row values 8186/18077/8236) are not
  re-derived; at this head I measured 0 added unpinned sites and rows
  8181/18076 with budgets to match, and the "main moved none of them"
  sentence is stale as above.
- The fixer's in-tree harness and mutation table were not re-run: fix-review
  step 11 forbids re-running the gate and the mutation table, and I ran my
  own targeted mutants instead. The four seat-local failures the body lists
  (optimality, stress, card.mjs, four py-spy heartbeat checks) are CI's to
  grade, and CI's `tests / fast` is green.
- Finding 2's behavioural consequence (a DHW supply reading folding into the
  space curve bias when the plan commanded space) is read-level; I built no
  probe for `_fold_flow_lift` because the seam is outside this group's owning
  seam. The code fact and the ignored observed duty are direct.
- The mode entity being optional (against the brief's REQUIRED) is the
  approved design's ruling, not a finding here.
