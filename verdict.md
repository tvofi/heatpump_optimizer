Design review: revise 2212054e93c344d62762ac52e3b891bcce93d31d architecture-unsound

Reviewed: `dev/programme/designs/R10-CEILING-PROBE.md` at 2212054e93c344d62762ac52e3b891bcce93d31d, read in a detached worktree. The code was read at origin/main cabfaadc3a13f61eaf0303918c7b1d5beda9c07c. The note names 6fe5170cd as its base. Between the two, `draw_range.py` and `sysid.py` are unchanged. `coordinator.py` (+/-1064), `pump_arbiter.py` (197), `thermal_model.py`, `sensor.py`, `button.py`, `payload.py` and `tests/structure_budgets.json` have moved. Nothing was rerun. Token count: not reported by this harness.

decision: orchestrator. The brief says this re-cut "has never been reviewed". `design-verdict/R10-CEILING-PROBE` e8da829f1 (2026-10-27) already returned `revise 2212054e9` on this SHA, as the rev-4 note. Under `design-review.md` it was the last note. This verdict re-reviews the same text against the moved main and the new downstream constraint. Its revise points are written so that they can also be handed over as carries (items 29–30).

## Rev-1 points, re-checked against the re-cut at cabfaadc
- Comfort sizer bypass: closed. §1 keeps `_size_step_power` for the fit and gives the probe a duration search. `sysid.py` is unchanged at main.
- The adoption refusal targets no state: closed. It was dropped; `_adopt_system_identification` (`coordinator.py:10884`) still consumes and replaces the result.
- Probe cadence shares the fit's `last_run`: closed by §1's per-kind clock and carry 7 (persisted).
- Sibling sites `_flow_target` and coordinator override/booking/gate: these are still the right sites at main (`pump_arbiter.py:625-659`, `coordinator.py:10827-10883`, `pump_arbiter.py:774`). The gate still aborts unconditionally (`10846-10848`). Main has added a new site; see carry 31.

## Revise point 1: the agreement rule is inside the store's accessor (`R10-CEILING-PROBE.md` F11, F9 control, Evidence plan "the sub-ceiling filter", §3 last bullet)
§3 defines `learned_max_kw()` as raw: the median of `ceiling`, `None` below twelve samples or past 45 days. The rest of the note contradicts that definition:
- F11 and its control say "twelve at 4.5 kW -> `None` where twelve at 3.0 returns 3.0".
- F9's control says "twelve at 4.5 kW -> not adopted".
- The mutation targets list "the sub-ceiling filter".
- §3 calls the 15 % rule the ruling's "only gate".

Twelve 4.5 kW samples on a 5.0 kW configuration can return `None` only if the `0.85 x p_max` comparison (`AGREE_TOLERANCE`, `draw_range.py:63`) runs inside the accessor or at the feed. R10-COP-GATE part D (`design/R10-COP-GATE` dc18f2f85, `R10-COP-GATE-D.md:20`, `:28`, `:71`) depends on the raw value. It owns the 15 % comparison once, so that its published reason can tell `not_below_configured` from `awaiting_probe`. Its null control is "a store within 15 % (4.5 of 5.0)" (`:58`).

**Fix wanted:**
- The accessor and the feed apply no agreement test.
- Replace the F11/F9 control with: twelve samples at 4.5 kW on a 5.0 kW configuration return 4.5 from `learned_max_kw()`. Its negative arm is eleven samples returning `None`.
- Strike "the sub-ceiling filter" from the mutation targets.
- In §3, say that the 15 % comparison belongs to COP-GATE part D and that this group publishes the raw median.

## Revise point 2: re-cut A builds a capture that main already has (`R10-CEILING-PROBE.md` §3 re-cut A; `coordinator.py:9749-9753`, `9840-9848` at cabfaadc)
Re-cut A says that at the base the fold's ask and command describe the next interval. It proposes capturing the pair after `_apply_action` and consuming it on the next cycle. Main already does this. R10-COP-GATE (#2262, 3ea1d8d48) made the fold read `pending["split"]` and `pending.get("flow_command")` from `_pending_prediction`. That dict is written at the end of `_record_accuracy` (`9840-9848`, after `_apply_action` at `5779`) and gated by `pairs_interval`. The comment at `9749-9751` describes exactly re-cut A's rule.

If a fixer follows the note as written, they will add a second carrier of the same interval's pair. That gives two owners of one concern. The note's F9 "live pairing" figures (`[1.5, 3.0, 3.0, 3.0]`, median 2.25) describe 6fe5170cd, not main. Rev-4 revise point 1 (the routing reads the kind from `_current_action` one interval late) is still open. The natural fix now has one place to go.

**Fix wanted:** rewrite re-cut A to consume `_pending_prediction`:
- Add the action's kind there (for example `"mode": self._current_action.get("mode")`, beside `"split"` and `"flow_command"`).
- Route on `pending["mode"]` at the fold.
- Drop the new capture and the "capture site" mutation target, and replace that target with the routing key.
- Re-derive F9 at cabfaadc. Expect the 2.25 bias to be gone on main. The known-maximum-pump control stays, as a regression pin on #2262's pairing.

## Carries (fixer notes; not revise points)
- Carry: R10-CEILING-PROBE (item 29). This is the residue of revise point 1. Keep `learned_max_kw()` raw, with no 15 % test in the accessor or at the feed. Pin twelve samples at 4.5 kW on a 5.0 kW configuration returning 4.5, against eleven returning `None`.
- Carry: R10-CEILING-PROBE (item 30). This is the residue of revise point 2, and it subsumes item 23. Put the kind in `_pending_prediction` (`coordinator.py:9840-9848`) and route on it at `9753`. Build no second capture. Keep both of item 23's ordering tests: a plan p_max interval just before a run goes to `samples`; a run's last step interval goes to `ceiling`.
- Carry: R10-CEILING-PROBE (item 31). This is a new sibling site at main. `step_supply` (`pump_arbiter.py:1179-1196`, R10-SAV-ACTUATION 5a4db822d) excludes `mode == "system_identification"` (`:1190`), so the one-minute tick leaves the supply switch alone during an experiment. That is the same predicate §1 removes from `_planned_duty` (`:774`). State and test the switch a probe interval runs under. The cycle's own write must turn it on, and the tick must not turn it off between cycles.
- Carry: R10-CEILING-PROBE (item 32). The override now books `heat_pump_on` through `planned_draw_runs(...)` (`coordinator.py:10875`). §1's duty threshold must call that helper, not repeat the 0.05 kW literal.
- Carry: R10-CEILING-PROBE (item 33). Citations drifted at cabfaadc:
  - `pump_arbiter.py`: `_step_kw` 482-484, `_flow_command` 592-618, `_flow_target` 625-659 (the level call is at 649), `_planned_duty` 759-786.
  - `coordinator.py`: `_record_accuracy` 9724, defrost close 9736, fold 9753, `_run_system_identification` 10827, override 10870-10883, `_adopt_system_identification` 10884.
  - `_commanded_split` is at 4653.

  Re-resolve every cite at the fixer's fork.
- Carry: R10-CEILING-PROBE (item 34). The budget figures in F8 and items 22/24 are stale. At cabfaadc: `class_excess_loc` 17656, `max_class_loc` 8061, `coordinator_attrs` 142, `seam_cut_total` 422, `coordinator_private_reach` 0. Re-measure. Item 24's per-row payment rule stands. Item 30 adds one dict key and no attribute, so `coordinator_attrs` is unaffected.
- Carry: R10-COP-GATE (item 2). Part D's "arbiter maps by the solve's band" edits the same `_flow_target` space path (`pump_arbiter.py:649`) as §1's action-power level mapping. D is ordered after this group. D's band must still send a probe step at configured p_max to the heat level.
- Carry: R10-CEILING-PROBE (items 7–28 stand as written in the note and in e8da829f1).
