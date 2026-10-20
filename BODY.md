Owner-reported savings items 3 and 4 (#2256): "Not heating" was the costliest
attribution category (137.58 SEK), and boost costs landed in "untagged"
(10.90 SEK). Two mechanisms booked money under a cause that did not draw it,
both at the reason-tagging seam this group owns.

**At booking.** `coordinator._accumulate_energy` tagged every metered kWh with
the plan step's reason, including a channel the plan was drawing nothing on. A
plan idling at zero while the meter saw a draw (a boost's overlay, a pump
running on its own, a standing draw) booked the whole draw as "idle" — which is
exactly "idle time cannot cost the most". `ledger.explain_metered` now
partitions an interval by whether each channel's reason can explain its draw: a
channel the plan ran keeps its step's reason at any meter magnitude, because a
step below the modulation floor is duty cycling *within* it
(`thermal_model.planned_draw_runs`), so a reading above the step's average is
the pump's own cycling and not an unplanned draw. A channel whose reason says
the plan drew nothing — the idle codes, `pump_mode`, or no reason at all —
books `REASON_UNTAGGED`: outside the plan. The reason lines still partition the
spot line.

The idle grouping had two definitions-in-waiting: the optimizer's
`_IDLE_REASONS` and the narrative's `ZERO_ENERGY_REASONS`, the same seven
codes. `payload.IDLE_REASONS` is now the one owner, read by the classifier's
blocked relabel, the settlement and the narrative, so a new idle sub-code
cannot be idle to one and planned to another.

**At classification.** The boost overlay rewrote its channel's power and left
the plan's reason in place, so a boost laid over a plan-idle step booked its
kilowatts as idle; and the three fixed-mode actions carried no reason at all,
so their draw booked "untagged". The overlay now tags its channel
`REASON_BOOST` (the anti-legionella cycle surviving, because `legionella.py`
reads `dhw_reason` to credit that cycle), the comfort and boost modes name
themselves, and the step-response experiment names
`REASON_SYSTEM_IDENTIFICATION` instead of blanking its cause. `payload.py` owns
the vocabulary; `narrative.group_by_reason` and the settlement read their
fallback from it rather than from a bare string.

Part of #2256: the roster files no closing keyword for this group; the
orchestrator verifies the issue after the merge.

## Head

`84eb9c1abad0a4460f764f4cab916db0f66df48e`

## Mutation proof

Each mutation is applied to the fix's own production line, the suite is run
with `PYTHONPATH=tests/hastub:tests python3 tests/features.py`, and the line is
restored with `git checkout -- <file>`; the trees are otherwise identical. Five
mutations, five reds, none survived.

1. **The partition's predicate** — `ledger.explain_metered`:
   `code = reason if planned else REASON_UNTAGGED` → `code = reason`. Red,
   four checks: `R10-SAV-REASONS: a plan that commanded nothing does not name
   the draw it never asked for -- the metered kWh book as untagged, not as
   idle` (`idle={'kwh': 0.4, 'sek': 0.8}, untagged={'kwh': 0.0, 'sek': 0.0}`);
   `R10-SAV-REASONS: a channel the plan ran explains the draw at any meter
   magnitude, and an idle step books outside the plan even at a trickle`;
   `R10-SAV-REASONS: the idle channel's share books as untagged and the reason
   lines still sum to the spot line` (`{'cheap_price': 2.25, 'idle': 0.75,
   'untagged': 0.0}`); `R10-SAV-REASONS: explain_metered returns exactly the
   shares it names -- planned, idle, no reason, already untagged, coalesced,
   empty and one channel`.
2. **The overlay's channel tag** — `boost.overlay`: delete
   `action["space_reason"] = REASON_BOOST`. Red:
   `R10-SAV-REASONS: a boosted channel is booked under the boost, not under the
   plan step's idle reason the overlay overwrote`
   (`space={..., 'space_reason': 'idle', ...}`).
3. **The anti-legionella exception** — `boost.overlay`: replace
   `if action.get("dhw_reason") != REASON_LEGIONELLA:` /
   `action["dhw_reason"] = REASON_BOOST` with the assignment alone. Red:
   `R10-SAV-REASONS: a boost never relabels the anti-legionella cycle the
   observer reads this field for -- the one cause that survives the overlay`.
4. **The comfort mode's cause** — `coordinator._async_update_data`: delete the
   `"space_reason": REASON_COMFORT_MODE` / `"dhw_reason": REASON_COMFORT_MODE`
   pair from the `MODE_COMFORT` action. Red:
   `R10-SAV-REASONS: every whole-action adoption names its cause from the
   shared vocabulary -- the fixed modes, the experiment and the solve`
   (`unvocab=[('coordinator.py', 5398, 'space_reason', None),
   ('coordinator.py', 5398, 'dhw_reason', None)]`).
5. **The experiment's cause** — `coordinator`'s `boost.adopt_plan` call in
   `_run_system_identification`: `REASON_SYSTEM_IDENTIFICATION` → `None`. Red:
   the same census check
   (`unvocab=[('coordinator.py', 10854, 'space_reason', None),
   ('coordinator.py', 10854, 'dhw_reason', None)]`).

## Null control

`dev/audit/harnesses/sav_reasons_booking.py` drives both seams and prints what
they book. Run against a checkout of the merge base and against this head, it
reads the defect at the base and not at the head:

```
$ python3 dev/audit/harnesses/sav_reasons_booking.py --worktree .   # at the merge base
BOOKING plan commanded 0.0 kW, meter read 0.4 kW for 1 h
  spot               0.4 kWh
  reason:idle        0.4 kWh
  reason:untagged    0.0 kWh
CLASSIFICATION space boost over a plan-idle step
  power          9.0
  space_reason   'idle'
  dhw_reason     'idle'
  boost_space    True

$ python3 dev/audit/harnesses/sav_reasons_booking.py --worktree .   # at this head
BOOKING plan commanded 0.0 kW, meter read 0.4 kW for 1 h
  spot               0.4 kWh
  reason:idle        0.0 kWh
  reason:untagged    0.4 kWh
CLASSIFICATION space boost over a plan-idle step
  power          9.0
  space_reason   'boost'
  dhw_reason     'idle'
  boost_space    True
```

The harness refuses a tree it did not actually load: `tests/harness.py`
prepends the relative `tests`/`custom_components`, so a run from another
checkout's root once reproduced the baseline at the head; the harness now
chdirs and checks the imported module's path.

Two controls sit in the suite. The partition is read in both directions: a
channel the plan ran keeps its reason at any meter magnitude, and an idle step
books outside the plan even when the plan booked a trickle. The roster's
flat-price control is a genuine NULL — it holds at both ends, because the
defect was which cause a kWh was named for, not how it was priced: on a
flat-price profile every reason line's unit cost is the one price and the
reason lines still sum to the spot line, so no category carries a cost a
different category would not.

## Figures

- `python3 dev/audit/harnesses/sav_reasons_booking.py --worktree .` — the two
  runs quoted above, at the merge base and at the head; the harness's sha1 is
  `5396e54c685a9faf5f6526a82dcb52440d558dbc`.
- `PYTHONPATH=tests/hastub:tests python3 tests/features.py` — 9 new checks in
  the `R10-SAV-REASONS` section; all pass on the head, and the mutation proof
  names the ones each mutant reddens.
- `python3 tests/structure.py` — `class_excess_loc` 18301 → 18299,
  `max_class_loc` 8543 → 8541, `functions_cc_over_15` 31 → 30,
  `seam_cut_total` 719 → 718: the partition moved out of the coordinator class
  into `ledger.explain_metered` and its two per-channel branches went with it.
  Recorded in its own commit with that reason.
- `python3 tools/audit/archscore/score.py --diff <merge base>` —
  `Architecture score: dS +0.0023 IMPROVES` (`coord_footprint` 2498 → 2494);
  no metric rose.
- `python3 tools/pr/ci_predict.py --base <merge base>` — `no closures or fast
  red predicted`; the five mutation sites it lists are disposed above.
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=<merge base> ./tests/run.sh` —
  `MODE: SCOPED -- 27 script(s) run, 6 scoped out`. **Left to CI, named
  unrun here**: the shared box measured load average 56-225 on 8 cores through
  the whole handoff (three other seats ran `tests/entities.py`, two ran
  `tests/features.py`, plus `validate.py`, `env_drift.py`, a closure
  re-derivation and a policy-mutant run), where `tests/features.py` alone took
  28 minutes and had not finished; an earlier scoped run is not quoted because
  it was measured across edits. `PYTHONPATH=tests/hastub python3
  tests/entities.py` did finish on this tree: `ALL 2359 ENTITY CHECKS PASSED`.

## Red checks

- `mutation` — red by the `R10-PREPR-UNPINNED-RED` rule rather than by a run:
  the diff adds five mutation sites, and `mutation-autofix` may pin a survivor
  only after the push, so the reviewed head can carry this. Answer: no cheaper
  detector exists for a mutant-survivor claim than the lane itself; the cheaper
  read is the site-level disposition under `## Unpinned sites`, where each site
  names the check that reddens under its mutation. The lane remains CI's
  authority on whether a site survives.
- No other red is known at the handoff. The scoped gate is named unrun under
  `## Figures` with the load that made it impractical, so its result is CI's to
  report; `tools/pr/ci_predict.py` turns no fast red.

## Unpinned sites

Each key is the one `python3 tools/pr/ci_predict.py --base <merge base>` lists;
each is disposed by a value check that fails when its predicate is mutated.

- `custom_components/heatpump_optimizer/boost.py:351 GUARD_OFF` — value check:
  the anti-legionella check in mutation 3 above.
- `custom_components/heatpump_optimizer/ledger.py:444 CMP_BOUND` — value
  check: the `explain_metered` arms above (`kwh <= 0.0` widened to `< 0.0`
  returns a zero share the "nothing metered" arm forbids).
- `custom_components/heatpump_optimizer/ledger.py:444 GUARD_OFF` — value check:
  the same arms (a zero share appears in every non-empty arm).
- `custom_components/heatpump_optimizer/ledger.py:451 RETURN_DEL` — value
  check: the same arms (no shares at all).
- `custom_components/heatpump_optimizer/narrative.py:113 CMP_BOUND` — value
  check: `group_by_reason books steps past a short reasons list as untagged`
  (`i < len(reasons)` widened indexes past the list and raises).

## Forward-carry

The three codes this adds to the shared vocabulary — `boost`, `comfort_mode`,
`system_identification` — have no entry in the card's `REASON_LABELS`, so the
receipt's "where the money went" bars label them with the raw token. Measured:
`tests/card.mjs` pins the fallback (`brand_new_code` renders as itself) and
`REASON_LABELS` maps only the plan-step codes plus `idle`. The card is outside
this group's owning seam and file list; R10-ADVISOR is the next card group and
is already `after` this one. Carry: R10-ADVISOR.

Destination: R10-ADVISOR's `brief` string in
`dev/programme/rosters/wave-r10-groups.json`, on `handoff/audit-r10-roster`
(tip `0d34adee1762d916ab61bfedf620b2856b4d7048` at this handoff; the roster on
`main` is the same file at its last stamp). The orchestrator lands this text
there:

```
`REASON_LABELS` and the card's `reasons.*` strings cover `boost`,
`comfort_mode` and `system_identification`, so the Savings receipt's
by-reason bars label the three codes this group added to payload's vocabulary
instead of rendering the raw token (`tests/card.mjs` pins the fallback; the
map is the gap).
```

## Friction

none

## Architecture score

`coord_footprint` 2498 → 2494; dS +0.0023, IMPROVES. No metric rose.
