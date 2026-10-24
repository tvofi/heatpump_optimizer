# Round-10 wave plan (orchestrator decision, 2026-10-18)

Inputs: `wave-data.json` (data seat, origin/main 106af95a, roster blob 78b01864). Edges are REPLAN-EDGES.json where a group is listed there, otherwise the roster's `after`. Durations are the median measured wall-clock of done round-10 groups of the same size: S 13.1 h, M 11.4 h, L 20.1 h, XL 30.2 h (1.5 × L, since no XL group has merged). Waves are DAG levels computed over the not-done groups; the computation is in this file's history.

| wave | groups | longest |
|---|---|---|
| 1 (draining now) | ARCHSCORE-COVERAGE, DIAG-REPLAY, I5-DOCS, RCA-FRICTION, RCA-STRUCTURE-BLIND, SAV-BASELINE, SENSOR-PAYLOAD, TICK-DRIVERS, TRUST-RELATIVE, VENT-DETECTOR, plus the ungrouped open PRs | 20.1 h |
| 2 | ADVISOR, ARCH-SHAPES, BRIEFS-FOLD, CONFIG-NOTICES, CURRENCY, DEEPLINK-HANDLERS, FREQ-DEFROST, INPUT-STALENESS, LOOP-CPU, NIGHT-FOLDS, POLICY-GATE-SCOPING, RATIO-ANCHOR, RCA-HEADMOVED, REPLAY-LANE, SAV-COMFORT, SAV-REASONS, TRAIN-HOLD | 20.1 h |
| 3 | LIVESTATE, POLICY-FIXER-MD, REPLAY-SCOPED, SCORES, SOLVER | 30.2 h |
| 4 | LEARNER-ETA | 11.4 h |
| 5 | HEAT-METER | 30.2 h |
| 6 | CONFIGFLOW-PAGES, COP-GATE, PARAMS-OWNER | 30.2 h |
| 7 | UX-HEALTH | 20.1 h |
| 8 | ARCH-DOCS | 20.1 h |

The strict wave sum is 182.4 h; the critical path is 146.2 h (VENT-DETECTOR → NIGHT-FOLDS → TRUST-RELATIVE → LIVESTATE → HEAT-METER → COP-GATE → UX-HEALTH → ARCH-DOCS). Both fit the mandate window (to 2026-10-28T18:14Z).

## Rules

1. **Drain, stamp, dispatch** (tvofi 2026-10-18). A wave ends when every open PR in it has merged, or is held with a recorded reason. Then `stamp.py --push --push-key`, on a green main with no train waiting, and the next wave goes out together.
2. **Hybrid admission, for wall clock.** A next-wave group may start before its wave opens when all its after-edges have merged and its files share no hunk with any open PR (`git merge-tree` against each open head). Waves 4–8 are a serial chain, so this only changes waves 2–3.
3. **coordinator.py concurrency.** Wave 2 has 13 groups whose hot file is `coordinator.py`. Before they are dispatched, an architect note (orchestrator.md §5, fixer.md 17) goes into each group's roster brief, naming the owning module, each fix's shape and the hunk regions that must not overlap.
4. **Seats.** Up to 8 local seats; cloud seats carry the rest without a cap. Fixers, reviewers and the drain work run on cloud first while the box is contended.

## Roster changes owed (one roster PR, after R10-ROSTER-OPS lands set-after / drop-carry)

- `set-after` on the 23 groups whose REPLAN edges differ from the roster's.
- Set the stage to in-progress for the six groups that have open PRs: VENT-DETECTOR #2391, SAV-BASELINE #2411, SENSOR-PAYLOAD #2379, TICK-DRIVERS #2390, DIAG-REPLAY #2399, RCA-STRUCTURE-BLIND #2415.
- Correct two stages: R10-PUMP-MODEL (marked done, but #2368 is open) and R10-ARCHSCORE-COVERAGE (#2320 has merged; #2373 and #2401 are open).
- Record each group's `wave` from the table above.
- `drop-carry` on R10-TICK-DRIVERS for the codeql delegation carry, which #2406 already did (#2417's review, comment on #2417).

## Open-PR soft cap (tvofi, 2026-10-18)

Hold open PRs to 6 or fewer, and at most 2 of them on `coordinator.py`. While the cap is full, fixers stop at their handoff refs; once the board drains to about 4, they open in critical-path order. A wave is whatever fits under the cap. `open_pr.sh` and the tick enforce it (R10-OPENPR-SILENT).
