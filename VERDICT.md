Design review: revise 2212054e93c344d62762ac52e3b891bcce93d31d architecture-unsound

Reviewed: `dev/programme/designs/R10-CEILING-PROBE.md` at 2212054e93c344d62762ac52e3b891bcce93d31d (blob `db2e9493b5`) on `refs/heads/design/r10-ceiling-probe`, in a detached worktree, appended on note 3 `1cd93ca6e` without a rewrite. Code read at `origin/main` 6fe5170cd7ce01e60ffebfc93e598c216e628fa3; `git diff 2212054e9 origin/main -- custom_components/heatpump_optimizer/` is empty, so the note's base and the reviewed base are one tree. The prior verdict (rev 3, `3a261d864`) was read for its two re-cut items and is re-measured below, not adopted. All 62 `path:line` citations resolve in range (`evidence/r4_cites.out`); two resolve to the wrong thing (item 25). The note's two new probes (feed, reader) were re-run at the base and reproduce (`evidence/r4_rederive_note_probes.out`), as were the three earlier probes behind F1–F5 (`evidence/r4_rederive_r3_probes.out`). One reviewer probe was added for the routing predicate (`evidence/r4_probe_routing.py`, `.out`), and the ratchet payment was measured (`evidence/r4_structure_plus_line.out`). Token count: not reported by this harness.

This appended revision of note 3 draws `revise`, and `design-review.md` allows no further note: the group does not get another design round. The two revise points are therefore written below **and** as carries (items 23–24 in `Notes for the fixer`'s grammar) so the orchestrator can hand them to a fixer instead of re-cutting the note. Everything else in the note stands as written.

## A — the store's feed point: closed

Re-cut A names the feed (`draw_range.fold`, `coordinator.py:9841`, reached from `_record_accuracy` at `5861`), states the order that breaks it (`async_run_optimization` `5826` → `_apply_action` `5845` → `_record_accuracy`; `_commanded_split` `4695` reads `_current_action`, whose one assignment is `3678`; `flow_command` `551`), and states the fix (capture the pair after `_apply_action`, consume it in the next cycle's fold). The precedent it cites (`5430-5433`) does say what it says, and it is the *opposite* ordering — the fabric learners run before the solve — which is why a capture is needed at all; the note does not conflate them.

Measured, the note's own feed probe re-run at the base (`evidence/r4_rederive_note_probes.out`):

- live pairing, 2.0 h step: 4 stored `[1.5, 3.0, 3.0, 3.0]` of 5 folded; 1.0 h: 2 `[1.5, 3.0]` of 3. Twelve samples → median 3.0 (3 runs) at 2.0 h, **2.25 kW** (6 runs) at 1.0 h, adopted against the 4.25 bar — the 25 % low bias exactly.
- interval-owned pairing: 4 and 2 stored, all 3.0; twelve → 3.0 at both step lengths.
- controls move: a gate-held pre-step draw that is idle (0.0 kW) stores 3 and 1; a gate-held 1.4 kW draw above a learned 1.1 kW idle is a running sample by `is_running_space` and is still not admitted, where the same draw with the ceiling written is; twelve plan-only intervals store nothing; twelve draws at 4.5 kW are not adopted.

The fold's `defrost` argument is `_defrost_window.close(now)` (`9829`), which runs every cycle, so the "not moved earlier" alternative is correctly refused. `tests/features.py:65456-65468` drives `fold` directly with matched pairs and does not move — verified.

## B — the reader and the latch: the reader closed, the routing not

The reader is closed. `learned_max_kw()` is a new read on `DrawRange`, published by `diagnostics_view` (`draw_range.py:464-470`) outside the `engaged` gate; at the base nothing reaches a store (`_metered_range` `162-172` reads `observed()` `147`, only from `planned` `217-226` behind `engaged`, only from `planned_range` `438`, only from `diagnostics_view` `469`; `planned_range` has one caller in the package). Reproduced: the F6 case reads `observed=(1.5, 3.0)`, `planned=None`, `effective_max_kw=None`; twelve in the window leave the high `None` (48 needed, `159`); store-only twelve reads `observed=None`, `effective_max_kw=None`; the spike reads `None` at 11, 3.0 at 12 and at 48 with `engaged=False`, `None` at day 46, `None` for twelve at 4.5 kW. Controls move.

The latch claim is closed as stated: `_disagrees` runs after every append (`190-211`) and `engaged` is sticky, so 48 ceiling samples first on an empty window engage at append 48 and 0.1429 at 336 never releases it, while the same 48 last on a full window never engage. Static shares decide nothing, as the note now says.

The routing is not closed: see revise point 1.

## Revise point 1 — `coordinator.py:10990`, `draw_range.py:190-211`: the routing predicate reads the kind one interval late

Re-cut A establishes that every `_current_action` read made at the fold describes the **next** interval, and its whole fix is to capture the interval's own values instead. Re-cut B then writes the routing predicate as `_current_action["mode"] == "system_identification"`, citing the assignment site at `10990` — the same source re-cut A proved is one interval ahead — while the captured "pair" is named as the ask and the command only (`"the pair is therefore captured..."`, `"the capture writes the pair onto the existing DrawRange"`). A fixer implementing the note literally reads the kind at the fold and routes on the next interval's action.

Measured (`evidence/r4_probe_routing.out`, real `draw_range.fold` for the window path, one probe run of `settling + N steps + relax`):

- read at the fold: the store takes 3 samples per 2.0 h run and **1** per 1.0 h run (the note's Evidence plan states 4 and 2), and the run's **last step interval falls into `observe`** — one probe sample per run reaches the window, which the same paragraph says cannot happen ("With the routing no probe sample reaches `observe`, so a probe cannot trip the latch").
- with F6's own premise, a plan interval at p_max immediately before the run (command = ceiling, a 2.6 kW mild-weather draw), the store takes that plan draw as a sample: `[2.6, 3.0, 3.0, 3.0]`.
- control, the kind carried with the captured pair: 4 and 2 samples, all 3.0, and the plan interval stays in the window — the note's stated figures.

In the plain case the plan's p_max interval and the probe's step draw and ask the same pair, so no store *value* reveals the swap — only the count and the window's content do. That is why the note's proposed test ("a probe interval writes `ceiling` and not `samples`") passes on any of the run's first step intervals and catches nothing; the test must name the run's **last** step interval. When the plan interval's own ceiling draw differs, F6's premise, the store's content shows it directly (`[2.6, 3.0, 3.0, 3.0]`).

**Fix wanted:** state that the capture carries the action's kind (or a probe flag) beside the ask and the command, and that the routing predicate reads it from the capture, not from `_current_action` at the fold. Add the two ordering controls above to the Evidence plan. Everything else in re-cut B stands.

## Revise point 2 — `tests/structure.py:2904-2911`: the ratchet payment does not pay the row it is aimed at, and a second over-limit class is unaccounted

Measured at the base (`evidence/r4_structure_plus_line.out`): one added line inside `HeatPumpOptimizerCoordinator` moves **both** rows — `class_excess_loc` 18079 → 18080 and `max_class_loc` 8236 → 8237, each a hard fail.

The note's payment is "moving a helper out of the class to module level". `tests/structure.py:2904-2911` says that move "leaves this row where it was" for `class_excess_loc` — the coordinator's span counts its `coordinator.py` helpers (449 lines at the base) — so it pays `max_class_loc` only. And self-check confirms it: the base run prints "the coordinator's 449 helper lines count in its span". A move to *another* module is priced by `coordinator_private_reach` (0 of 0) and `seam_cut_total` (424 of 424), both at zero headroom.

`SystemIdentification` (span 1065, excess 765) is also over the limit, and the design adds lines there — a probe duration field beside `_step_power` (carry 15), and the kind and clocks §1 gives it. Every one of those lines raises `class_excess_loc`, and the cost paragraph names the class without naming a payment for it.

**Fix wanted:** state, per class and per row, what line goes. At zero headroom the only honest instrument is deletion or a merge the design makes redundant (`dead_methods` 0, `dead_top_level_symbols` 1, `duplication_copies` 16 leave little), or an owner-raised budget, which the note must ask for explicitly. A move to module level pays one row only; say so rather than imply both.

## Carries (fixer notes; not revise points)

- Carry: R10-CEILING-PROBE (item 23) — the residue of revise point 1: the capture carries the action's kind beside the ask and the command, and the routing predicate reads it there. Test both orderings: a plan interval at p_max immediately before a probe run writes `samples` and not `ceiling`, and the last step interval of a run writes `ceiling` and not `samples`.
- Carry: R10-CEILING-PROBE (item 24) — the residue of revise point 2: measure the two budget rows after the edit and name in the commit body which lines went, per class. A helper moved to `coordinator.py`'s module level pays `max_class_loc` only; a move to another module must be re-measured against `coordinator_private_reach` 0 and `seam_cut_total` 424.
- Carry: R10-CEILING-PROBE (item 25) — two citations resolve to the wrong thing: F9's `coordinator.py:9861` is the tank-settlement comment (`_record_accuracy` is `9817`; the fold is `9841`), and re-cut A's "adopted at `10984`" is the `**self._current_action` line (the call is `10983`).
- Carry: R10-CEILING-PROBE (item 26) — F6's second half (`48 in 48 -> engaged=True, planned=(3.0, 3.0)`) reproduces from this round's reader probe, not from the note's earlier `probe_figures.py`, which appends straight to `samples`/`commands` and so reads `engaged` without ever running `_disagrees`. Quote the reader probe for F6 and F7; a figure whose own construction bypasses the mechanism is not evidence.
- Carry: R10-CEILING-PROBE (item 27) — the `ceiling` deque is not keyed to `config`: `observe` clears the window on a configuration change and the store would not. State whether a reconfiguration clears it, and carry the rule into `as_dict`/`from_dict`.
- Carry: R10-CEILING-PROBE (item 28) — the sibling-site sentence overstates its command: `git grep -n '_sysid_step_off_loop\|learner_samples='` returns only the entry points (`coordinator.py:1772`, `10966`, `10972`); it does not list the entity, state-list, payload or sensor sites the sentence then names. List those on their own evidence.
- Carry: R10-CEILING-PROBE (items 7–22 stand as written in the note).
- Carry: R10-COP-GATE (item 1) — unchanged: the learned top's consumption belongs to that group; this one ships the measurement only.

## Decisions (routed, not revise points)

- decision: orchestrator — the roster's `files` lists 2 of the 7 modules the note changes (`sysid.py`, `draw_range.py`); `roster_edit.py` has no files operation. The widening must land before dispatch.
- decision: orchestrator — place this group's `Carry: R10-COP-GATE (item 1)` in R10-COP-GATE's own brief (`finding-propagation.md`), not only in this note.

## Checks that hold (do not re-cut these)

- **Owning seam.** `sysid.py` runs the experiment, `draw_range.py` owns what a sample teaches (store, write and read on the one `DrawRange`), `pump_arbiter.py` the set-point, `coordinator.py` the wiring. R10-HEAT-METER explicitly puts `draw_range.fold` out of scope; R10-SCORES and R10-LIVESTATE touch `coordinator.py`/`sensor.py`/`payload.py` on other methods.
- **The defect exists at main.** The fold pairs the closed interval's draw with the next interval's ask and set-point, measured above; `_planned_duty` returns `None` for the experiment's action; `_step_kw` is what the level mapping reads.
- **F1–F5 reproduce.** Sizer 5.0 kW (ua 0.35, C 12) vs 2.25830078125 kW (ua 0.12, C 4); peaks 0.447 / 0.769 / 0.903 K; levels 5.0/1.5/0.0 kW → 55.0/37.5/55.0 °C and duty `space` against `None` for the experiment; arm 199 ready, 482 converged, 150 ready; 4 step samples per 2.0 h run, 12 at 6.0 h.
- **F6–F11 reproduce** from the note's feed and reader probes, with the F6 source caveat at item 26.
- **After edges.** SETPOINT-BOOST, CI-LAYOUT and NIGHT-FOLDS are merged before the base.
- **The entity pin.** `tests/entities.py:5854-5860` requires `system_identification` to stay in `_unrecorded_attributes`; the note's §2 sentence now says so and the new recorded attribute goes outside it.
- **The plan path.** `planned_range` has one caller, `diagnostics_view`; no code assigns `max_electrical_power`; the learned range is a diagnostics value only.
- **Cost.** 7 files in an M group, within the roster's M range (0–16 files).

## What the fixer must be told instead of a fourth note

Items 23 and 24 are the whole residue: the kind travels in the capture and the predicate reads it there, and the ratchet payment is stated per class and per row with the lines that go. Take the rest of the note as written; items 7–22 and 25–28 are fixer notes, not open design points.

## Evidence

`evidence/r4_REVIEWED.txt` (note, base, ref tips, diffs), `r4_cites.out` (62 citations with the line they resolve to), `r4_rederive_note_probes.out` (feed and reader probes re-run), `r4_rederive_r3_probes.out` (figures, sysid and arbiter probes re-run), `r4_probe_routing.py`/`.out` (the routing predicate), `r4_structure_plus_line.out` and `r4_tree_checks.txt` (budget rows, class spans, cycle order, sibling sites, pins). The rev-2 and rev-3 files are unchanged beside these.
