# R11-CARRY-DRAWMAP: port the approved draw-map parts A, B and F onto main (architect note)

Designer seat, round 1. Base origin/main 7c2f4c30cab5610cf8f5b040c326836ab544d27d (no predecessor: `after: none`), the code read there. Extends, never contradicts, the approved note at tag archive/design/R10-DRAW-MAP-EVIDENCE (9aa450f55e; `Design review: approve` at archive/design-verdict/R10-DRAW-MAP-EVIDENCE f10dd41856), whose sections A, B, [CE], [R3], [R4], C and F stay the specification; this note says only what moved, how the archived builds land, and where each carry goes. No finder harness: owner report (#3106 item 4), as in the approved note.

**Part labels.** The group brief's parenthetical ("part A (the sweep…), part B (the ceiling probe and pass_origin)") does not match the approved note or the carries, which bind: **A** = pass record, map rows, learner exclusion; **B** = the sweep and [CE] (probe before fit); **F** = the trace and the bundle readers. A correction to the roster text, not to the behaviour.

## What already exists (tags, never merged)

| part | tag head | base | built | state |
|---|---|---|---|---|
| A | archive/handoff/r10-draw-map-evidence-a cc335482ae | 3533ba12b8 | `pump_arbiter.pass_origin`, `ArbiterState.last_pass`, `draw_range.PassRecord`, `MapRows`, `MAP_ROWS`, judge_floor's experiment refusal | fix review round 1 blocked, fixed in round 2; no merge verdict recorded |
| B | archive/handoff/r10-draw-map-evidence-b 8c1508d9c1 | A + main 6abf88e617 | `KIND_SWEEP`, the sweep button, held floor, `draw_range.SweepRun`, `last_sweep`, `DrawRange.probe_since`, [CE] 2 | handed off, no review |
| F | archive/handoff/r10-draw-map-evidence-f 880b015c8b | 3533ba12b8 (not A) | hpo-debug/2, minute trace, lifecycle rows, `debug_replay.py --trace`, `debugger.pass_record` hook | handed off, no review; D15.md and its token budget await the owner |

`git merge-tree --write-tree 7c2f4c30 <tag>` conflicts: A in `accuracy.py`, `coordinator.py`, `draw_range.py`, `store.py`, `tests/features.py`; B in those plus round-4 D6 claims; F only in `dev/governance/config/policy_budgets.json`. `git diff --stat 3533ba12b8 7c2f4c30` moves `sysid.py` and `debugger.py` by nothing, so B's sysid hunks and F's collector port clean.

## Decision: port, part by part, onto main

Each part is re-landed as a new branch from main with the tag's diff applied and its conflicts resolved against main's newer seams, then re-runs `fixer.md` steps 2–8 at its own merge base (the tags' proofs are snapshots). Alternatives: **rebuild from the note** lost: it re-spends A's two review rounds and B's measured shape (P8/P9 harness) for no change in seam; **merge the tags as they are** lost: B carries 164 files of round-10 machinery (`tools/audit/seat/*.sh`, ledgers) unrelated to the group, and A's conflicts need resolution against code it never saw.

## What moved on main, and the shape it forces

1. **The COP scale probe (R11-OUTSIDE-SELF-SETTING-PUMP).** `_fold_measured_cop` (coordinator.py:5315) now runs `MeasuredCop.release` and `owed_scale` (coordinator.py:5343) **before** `judge_floor` (coordinator.py:5345), and `MeasuredCop.judge_floor` (accuracy.py:1221) gained the window `draw`. A's experiment flag is added after `draw` as a keyword; the refusal stays `COP_REFUSED_OFF_ASK` and is returned before `_judge_ratio` reaches `ScaleProbe.admit` (accuracy.py:1310), so an experiment interval is never a dither row. The probe's `owed_scale` still steps on an experiment cycle; `ScaleDither.step` only counts an admitted row live, so the experiment cycle is no reading. Null (new): the dither's rows, `scale_response` and stored scale are byte-identical with and without a sweep on the synthetic run.
2. **The metered floor (R11-OUTSIDE-HONEST-METERED-FLOOR).** `DrawRange.floor_kw` moves in `update_floor` (draw_range.py:611), called from `observe` (draw_range.py:326), on window pairs (`_run_asked`, draw_range.py:243). `draw_range.fold`'s routing (draw_range.py:701-704) stays the one place: a sweep interval never reaches `observe`, hence never `floor_kw`, `floor_since`, `power_floor_kw` or `ask_evidence`. A's window null gains `floor_kw`, `floor_since` and `SolveBand`'s bottom fields.
3. **`SolveBand` bottom fields** (draw_range.py:760): B's sweep ceiling rows move only `learned_max_kw`; the r14 reader split (B's `probe_since`) keeps `ceiling_since` on every row for `learned_max_kw` and `solve_band` (draw_range.py:819), `armable` (sysid.py:1332) reading probe rows only.
4. **`store.DOMAINS`** gained the floor leaves; A's column leaves are additive beside them; `ACCURACY_STORE_VERSION` unchanged.

Owning seams are the approved note's, unchanged: `pump_arbiter.py` (origin, held floor), `draw_range.py` beside `fold` (rows, routing), `accuracy.py` `MeasuredCop` (efficiency judgement), `sysid.py` `armable` (which kind), `debugger.py` (the week), `tools/replay/` (D15 readers); `coordinator.py` wires.

**Sibling sites**, by `git grep -n -E "\.observe\(|\.observe_ceiling\(|_run_asked\(|update_floor\(|judge_floor\(|ceiling_since\(|\.admit\(|owed_scale\(" -- custom_components`: every window reader (draw_range.py:528, :577, :605) and `update_floor` sit behind `observe` at :704; the ceiling readers at :172, :186, :819 and sysid.py:1332 are r14's; `judge_floor` has one call (coordinator.py:5345) plus the counter span close (coordinator.py:1193), which A's flag also covers; `ScaleProbe.admit` is reached only past the refusal. The other `.observe` hits are other learners' (flow bias, defrost, peak, frequency map), reached by no sweep interval because the [R3] refusal and the [CE] routing govern them through the same capture; the fixer confirms each with the sweep null.

## Parts, order, hot files

A first; then B (stacked on A) and F (rebased on A, wiring `debugger.pass_record` to `pump_arbiter.state_for(coord).last_pass`, pump_arbiter.py:497). B and F share `strings.json`, `translations/`, `tests/features.py`: the second to land rebases. Hot: `draw_range.py`, `accuracy.py`, `coordinator.py`, `store.py`, `tests/features.py`.

**Owner gate.** Rulings S1–S4 (2026-11-14, carry 2) are on record and the archived B and F implement them; the fixer confirms with the owner that they still stand before part A pushes, as the brief asks, and builds [CE] 2 only on that yes (r18).

## Evidence, by file

- **A**: the tag's part A block of `tests/features.py`, re-run failing at main and passing at the head; `dev/audit/harnesses/draw_map_rows.py --synthetic` (at the A tag); the window null extended per item 2; the dither null per item 1; mutation over the port's diff. Carry 12: take B's typing narrowing (commit 8b4c27bb52) into A — at the A tag standalone mypy reports 5 errors in `draw_range.py`, at the B tag 0.
- **B**: the tag's block; `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/draw_map_sweep.py` (needs `tests` on the path; without it, `ModuleNotFoundError: harness`); null control (brief): `r10_cop_gate_band.py` and the routing checks fail with the sweep interval routed to `DrawRange.observe` and pass with it excluded — one mutant flipping the `fold` guard at draw_range.py:701.
- **F**: `tests/debug_collect.py`; `d15_trace_budget.py` (at the F tag) on the synthetic week with A's stored rows and B's sweep record; the trace null `--replay-null`.

## Carries

- C0 (D15 scope): built by F's debug week, re-measured. Carry: R11-CARRY-DRAWMAP
- C1 (empty ceiling store): mechanism re-read at main — `armable` (sysid.py:1321) still returns the fit first while unconverged; answered by [CE] 2 under S3; `draw_map_linearity.py --bundle` needs the owner's bundle, which is not in the tree: re-measured where it lives or recorded unmeasured. Carry: R11-CARRY-DRAWMAP
- C3, C4, C5, C6: B's tag builds them (`_EXPERIMENT_ORIGINS` maps the sweep kind; level kW in the run key; r17 `ceiling_sample_kw=[3.2] row_drawn_mean_kw=[3.2000000000000006]`; r12 lower bound "zero" `k5=25/60` at -5 °C; r14 `probe_since`; r15 band gate on the stand-down path; r16 floor cleared on any non-sweep action); re-proved on the port. Carry: R11-CARRY-DRAWMAP
- C7 and C11 (P7 with stored rows): `draw_map_rows.py --synthetic` at the A tag prints `added_bytes=58058` for `MAP_ROWS` rows; F re-measures the 168 h budget with those bytes and B's 167-byte sweep record before choosing a drop. Carry: R11-CARRY-DRAWMAP
- C8: `r10_cop_gate_band.py --synthetic` at main reproduces `synthetic-linear steps=4 distinct_c=4 gain_kw_per_k=0.1 max_resid_kw=0.0`; the owner-data half needs the bundle (as C1). Carry: R11-CARRY-DRAWMAP
- C9: closed by the port wiring above. Carry: R11-CARRY-DRAWMAP
- C10 (store wear with the trace on): kept as disclosed; a per-day trace store loses on a second store document and its migration, and the owner's scope asks one mechanism; F re-measures the day-7 write volume. Carry: R11-CARRY-DRAWMAP
- C13 (stale fit/probe hold): B re-derives `held` each cycle for every kind in the one place B built for the sweep (`sysid.sweep_hold_reason`'s path), with the tag's check's probe arm turned from expected-stale to fresh. Carry: R11-CARRY-DRAWMAP
- C14: F's bundle reader and `draw_map_linearity.py` weigh a sweep level by its steady minutes in the stored last sweep. Carry: R11-CARRY-DRAWMAP

## Notes for the fixer

- The ratchet sits at budget at main (`python3 tests/structure.py`: `max_class_loc`, `seam_cut_total` and the method caps `ok` at their caps); the tags' re-records were against older budgets, so each part pays again. F's archscore read `coord_footprint 2497->2500` inadmissible: pay it before handoff. Carry: R11-CARRY-DRAWMAP
- F's D15.md line and its `files_tokens` raise merge only on the owner's approving review (`budget-raise-gate`, 0013). Carry: R11-CARRY-DRAWMAP

## Decisions routed

- decision: owner. Do S1–S4 still stand at this base (sweep on a flat price; text trace columns; probe before fit where the top is unlearned; F prepares the D15.md line)?
