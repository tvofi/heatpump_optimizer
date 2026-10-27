The house grade placed the envelope time constant on one log band spanning every
shipped preset, so the configured era, structure and area never entered it: at
3b4180dcc the twenty structure-by-era presets, each at its own typical loss,
spread 67.7 points, and the owner's house (pre-1960, 1.5x its era's typical
loss) graded between 20.3 and 44.3 depending on which structure was configured.

This grades the house against what it is. `presets.house_grade` takes the ratio
typical_tau / tau, whose log is the sum of three terms -- the model's envelope
loss against the loss `derive()` gives the configured answers, the learner's
scale, and the thermal-mass correction -- and maps it to `100 / (1 + r**1.5)`,
floored at 1 (0 stays reserved for no data). Typical grades 50 for every type
and era; the owner's case grades 35.2. The three terms are published as
`scores["envelope_drivers"]` with points that sum to the grade's distance from
50, and the card renders them with their signed contributions and the metric in
plain words on hover and in the breakdown.

An absent building answer is the default house, not a different one. The reads
in `preset_from_config` name the preset's own default as their fallback, so the
tree's absent-key proof in `tests/config_flow_steps.py` -- which skips
`config_flow.py`, where those reads used to live -- can read them, and a house
with no configured era grades exactly as one configured 1980-2005. There is
therefore no `era_assumed` driver: a read that told absence from the default
apart would fail that proof, and the grade's docstring says so where a reader
would look for the missing driver.

`dev/audit/harnesses/r10_scores_envelope.py` drove the removed name through
`getattr`, so its split arm silently fell back to the merge base's 20-100 h
band: it read 36.5 at this head, where the tree's own rule reads 0.0. Its
`tree_grade` now applies `presets.house_grade` to the Health tab's published
loss.

The tests pin the coordinator's own publication, not only the grade:
`tests/features.py`'s `#2816` block and its `#65 the scores` block each drive
`_scores_view` -- the same house configured pre-1960 grades better than
configured post-2005, the published drivers are the three log terms rounded to
one decimal and summing to the grade less 50, and a house with no configured era
matches one configured with the form's default, driver for driver.

Two files outside this group's roster `files` move with it, both disclosed
rather than incidental: `config_flow._derive_preset` now delegates to
`presets.preset_from_config`, so the questionnaire-to-preset shape has one owner
instead of the flow's own reads, and `payload.py` declares the new
`envelope_drivers` member on the `Scores` TypedDict. `presets.py` and the card
are in the roster's list. The rest of the diff is tests and evidence:
`tests/features.py`, `tests/card.mjs`, `tests/entities.py`'s census entry, the
two harnesses (one new, registered in `tests/closures.json`), the three
mutation-ledger entries the removed `envelope_score` and `envelope_band_hours`
lines owned, and the two claim files.

Part of #2258, #2816. Neither closes here: the roster gives this group
`fixes: []`, so the orchestrator decides their disposition at the merge.

## Head

c89e5b5db1a8c2bfddbb9a9259f8dc319187eee9

## Mutation proof

Each mutant is one line changed in its own worktree at this head. The reds are
the suite's own checks, executed from `tests/features.py`'s own source (the
region compiled as it stands, with the tree's `harness.Results`, `_t2_coord`
and `_rs_advice`), not a copy of them; both regions pass 7 of 7 on the
unmutated head, so the reds below belong to the mutants.

M1 -- `house_grade` grades against the default preset
(`preset_from_config({}, config)`), the merge base's behaviour. Red on
`#2816 null control: every preset house at its own type and era's typical loss
grades 50, and its drivers say nothing moved it` (240 presets; the printed
grades run from 3.584 to 87.002, none of them 50), on `#2816: the owner's house, a century old at 1.5x the typical pre-1960
loss, grades low but clearly nonzero -- 30 to 40` (9.07), on `#2816: one
envelope is graded against its own era`, on `#2816: the drivers account for the
grade`, and in the scores block on `#2816: the same house grades better as a
pre-1960 house than as a post-2005 one` (pre-1960 20.2, post-2005 20.2). Not
red: the absent-era equality, which M1 moves on both sides at once -- M5 and M7
are that check's mutants.

M2 -- the `_GRADE_FLOOR` max is dropped from the grade expression. Red on
`#2816: the grade falls strictly with the loss ratio until the floor, and a
measured house never grades 0`: the curve's last cell reads 1.0e-07 instead of
1.0.

M3 -- `compose_scores` publishes `"envelope_drivers": []`. Red on `#2816: the
scores publish the grade's drivers, their points rounded to one decimal and
summing to its distance from 50` (40.6 from `[]`) and on `#2816: a house with no
configured era grades exactly as one configured with the form's default era,
drivers included, and the points still account for the distance from 50`.

M4 -- `r10_scores_envelope.py`'s `tree_grade` reverted to not seeing the tree's
rule (the pre-port `getattr` fallback). `RESULT split_max_abs_gap=36.5`, against
0.0 at the same head.

M5 -- the absent era reads `ERA_PRE_1960` instead of `ERA_1980_2005`. Red on
`_ABSENT_FALLBACKS is exactly the proven set` (`unproven but listed:
['building_era']`) and on both absent-era checks above.

M7 -- the removed `era_assumed` driver is reintroduced. The same three reds,
which is why the removal is pinned from both sides: the absent-key proof rejects
the read, and the two grade-level checks reject the extra driver.

## Null control

At ratio 1.0, all 240 preset cells (4 structures x 5 eras x 3 foundations x 2
emitters x two-zone off/on), each at the loss `derive()` gives its own answers,
grade exactly 50 with every driver at 0 points (`#2816 null control: every
preset house ...`). At the merge base the same cells spread 67.7
(`RESULT era_spread=67.7`), so the null is the base's failure. The harness reads
the same property from the published side: its `band` rows report
`tree_grade=50.0` for every preset house at this head against 48.7 to 83.6 at
the merge base.

The null is also why M1 needs the era arm and not only the null: the same house
with no building answers grades 20.2 whether or not a structure is configured
(both fall to the default preset), so a grade that ignores the answers is
invisible at the default and only an era pair separates them. The absent-era
equality is the same statement from the other side: absence is the default, so
answerless and answered-with-the-default must be the same house.

The independent arm: `r10_scores_envelope.py --ratio-override 1.0` reads
`RESULT split_max_abs_gap=0.0` at both ends -- the split arm's gap is the
split's, not a scale-only drift.

## Figures

- `era_spread` 67.7 -> 0.0, `owner_min`/`owner_max` 20.3/44.3 -> 35.2/35.2,
  `monotone` False -> True, `curve_min` 0.0 -> 4.23, `drivers_max_gap` None ->
  0.0: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_house_grade.py`
  at the merge base (3b4180dcc) and at this head.
- `RESULT era_spread=50.5`, `owner_min` 16.8, `curve_min` 1.61 at this head
  under the harness's own `--era-blind` perturbation (the same command with
  `--era-blind`), against 0.0 unperturbed.
- `RESULT split_max_abs_gap=0.0` at this head and 0.0 at the merge base, and the
  `band` rows' `tree_grade=50.0` against 48.7-83.6:
  `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_scores_envelope.py`.
  36.5 under M4.
- `ALL 6 ABSENT-FALLBACK SLICE PASSED` -- the tree's own
  `absent_fallbacks_are_proven` from `tests/config_flow_steps.py`; and
  `ALL 7 FEATURES SLICE presets PASSED` / `ALL 7 FEATURES SLICE scores PASSED`
  from `tests/features.py`'s own two regions. The slice drivers live in the
  seat's scratch directory, not in the tree; each compiles the region from the
  tree's own source.
- `node tests/card_drift.mjs`: `1 state(s) moved and claimed, 44 identical`.
- Scoped gate, `GATE_SCOPE=auto` on this head: `MODE: SCOPED -- 27 script(s) run,
  6 scoped out.`, 23 of the 27 green. The four red are this host's, not the
  branch's, and each is red identically at the merge base — `tests/entities.py`
  (4 of 2463), `tests/optimality.py` (1 of 84), `tests/stress.py` (1 of 113) and
  `tests/golden.py` in strict mode, which the contract's `GOLDEN_MODE=drift`
  replaces. The drift lane, `python3 tests/env_drift.py --all origin/main`,
  reads its whole run: 5 committed fixtures stale and all 5 `CLAIMED`, 0
  `UNCLAIMED`, every backtest scenario `byte-identical to origin/main here`.
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`, every metric at or under
  its budget.

## Unpinned sites

- `custom_components/heatpump_optimizer/presets.py:323 CONST`: `_GRADE_SLOPE = 1.5`. Written triage: the checks pin the owner's 30-40 band, not the value; a 1.0 slope lands the owner's case on exactly 40.0 and passes, and the harness's `EXPECTED curve_min=4.23` line is not executed by any check. Left for `mutation-autofix` to pin with the driver that kills it.
- `custom_components/heatpump_optimizer/presets.py:325 CONST`: `_GRADE_FLOOR = 1.0`, pinned by the value check `#2816: the grade falls strictly with the loss ratio until the floor, and a measured house never grades 0` (`min(_env_curve) == 1.0`).
- `custom_components/heatpump_optimizer/presets.py:361 CLAMP_DROP`: the `max(...)` floor, pinned by the same check (mutant M2).
- `custom_components/heatpump_optimizer/coordinator.py:2902 RETURN_DEL`: `return grade, None, drivers`, pinned by `#2816: the scores publish the grade's drivers, their points rounded to one decimal and summing to its distance from 50` (mutant M3).

## Red checks

At this branch's first gate (785f226f) four scripts were red. Each is answered
here, and each fix carries its own mutant above.

- `tests/config_flow_steps.py`, 2 of 502:
  `_ABSENT_FALLBACKS is exactly the proven set` reported five building keys
  "unproven but listed". The reads had moved out of `config_flow.py`, the one
  module that proof skips, and a one-arg `.get(K)` under `or ""` is not a shape
  it can prove against a truthy form default. Fixed by reading each key with the
  preset's own default as the fallback; M5 shows the proof is live on the fixed
  read and M7 shows the other direction.
- `tests/entities.py`: `UNCLASSIFIED ['presets.py']` in the mapping-read census.
  Classified in `_EC_RESIDUAL` with the reason that EntryConfig declares none of
  the building keys; the module-wide entry and the limit of that granularity are
  stated in the census comment too. That limit is the finding, and it is not
  answered by widening the census: `_EC_RESIDUAL` is keyed by module, so a read
  added anywhere else in `presets.py` would inherit this disposition unjudged,
  and the census has no rule that could express "this read is a questionnaire
  answer, that one is not". The alternative — a per-site disposition — is a
  change to the census's own shape, for its owner.
- `tests/env_drift.py`: five coord captures gained
  `data.insight.scores.envelope_drivers` and the same key under
  `sensors.optimization_score.extra_state_attributes`, both added at this head
  and both the whole diff, with no value leaf moved. Claimed, one line per
  fixture, in `tests/golden/claimed_drift.txt`; no golden is re-recorded.
- `tests/card_drift.mjs`: `score_open` moved because the House row's explanation
  is rewritten and gains its driver line. Claimed in
  `tests/golden/card_claimed_drift.txt`; the other 44 states are identical.

Not a red of the branch: `tests/arch_score_head.py` in that first gate was
killed by a SIGTERM to the process group that launched the gate (its log reads
`Terminated: 15`), not by a failing assertion; the gate on this head ran it.

Not the branch's either, and not repaired here: four scripts this host reddens
are red at the merge base `3b4180dcc` too, measured there in this environment.

- `tests/entities.py`, 4 of 2463: `hb:positive_control survives one hung py-spy
  sample`, `and a try whose sample misses the spin, or names it at rc!=0, is
  retried, not accepted`, `the control rests between tries`, and `the control
  survives two hung samples, answering on try 3`. Each wants the stub's second
  answer and gets the first: `_hb_spy_run` dispatches on `case $(wc -l < calls)
  in` with a `  1)` arm, and this host's `wc -l` writes `       1` (seven
  leading blanks, `od -c`), so every call takes the `*)` fallback and the last
  answer is the only one ever given (`calls=1`). The region compiled from the
  tree's own source and run at 3b4180dcc: `4 FAILED`, the same four, the same
  `calls=1`; the stub is byte-identical at 3b4180dcc and on `origin/main`. GNU
  `wc`, which the Linux runner carries, prints the count unpadded and the arm
  matches. The heartbeat tests' owner's to repair.
- `tests/optimality.py`, 1 of 84: `one|summer_negative|shoulder: a recorded
  claim still has a gap (not stale)` — `claimed but gap 0.0000% is at or below
  the bar`. The same check fails the same way at 3b4180dcc (`1 of 84`).
- `tests/stress.py`, 1 of 113: `shoulder: cheaper than holding the setpoint`,
  `4.67 vs 3.96` — the same check, the same two numbers, at 3b4180dcc
  (`1 of 113`).
- `tests/golden.py` in strict mode: `55 of 56 GOLDEN SCENARIOS CHANGED`, value
  leaves only. Strict mode compares committed fixtures recorded on another
  machine against this one's floats; `tests/run.sh`'s own comment says so. The
  mode the contract names, `GOLDEN_MODE=drift`, replaces this comparison with
  `tests/env_drift.py --all origin/main`, which reads every backtest scenario
  `byte-identical to origin/main here` and the five coordinating fixtures
  `CLAIMED` with `0 UNCLAIMED` (the claims this branch adds).

## Forward-carry

- The heat-pump grade must mirror this branch's driver interface rather than invent a second one (R10-COP-GATE's brief: "the same hover reason codes as the house grade"): `scores["envelope_drivers"]` is a list of `{"code": str, "points": float}`, points rounded to one decimal and summing to the grade minus mid-scale because they are the log shares of one ratio and not independent scores; the renderer drops zero-point drivers and falls back to a "typical" line when none moves, so a grade always carries at least one line, while `reasons[...]` stays the separate absent-grade channel and drivers exist only on a grade. Controls to mirror: every preset-sized cell at its own typical state grades exactly mid-scale with zero drivers (240 cells here, and `tree_grade=50.0` for every preset house in the scores harness), and one perturbed input moves the headline figure (era_spread 0.0 -> 50.5 under `--era-blind`). Carry: R10-COP-GATE, into that group's `carry` list in `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster` (a live group takes the brief, not a `carry-<N>.json`) — landed as `a4a348a6dc67e30ef6644ab73b5da60d4f45f4da`, lint gate `TOTAL: 0 error(s)`.

## Friction

none
