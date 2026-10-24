# D14 round 10 -- verifier report (single verifier, lenses V1-V3)

Worktree: detached at handoff/audit-r10-register 9355f107d (the branch itself is checked out in r10-repo, so `--detach`).
Load: finder harnesses ran in parallel at load1 21.5-26.0 (thread_factor 1.000, c1 0.102); all metrics are counts, contention-immune. V2 harnesses: `dev/audit/rounds/round10/D14/verify/v2_*.py`.

## D14-s1-01 -- away recovery estimate on the loop (P10) -- WEAKEN (low)
- V1: `--away` loop_kernels_all=183, away_seam=183 (6 cycles; 30.5/cycle). Null `--away --deficit 0` -> 0; base -> 0; `--perturb` -> 6967 (moves up as stated). Reproduced exactly.
- V2 (own metric: simulate_step calls and wall time of one `away.estimate_recovery_hours` at the worst case): 96 calls, 0.25 ms wall (load1 ~5.6). Under-target cases return before any call.
- V3: reachable in real HA: `coordinator.py:5693` calls `self._resolve_away()` inline in the optimization cycle, no executor (comment says "resolves on the event loop"); not a hastub artefact. The P10 barrier (tests/replay.py) has no away arm: confirmed. Severity: mechanism matches P10, but consequence is <=0.25 ms per cycle of loop time, far below any starvation threshold; low. Seam rule enumerates (AST lists every widened-kernel call site, not just away). Class P10 confirmed.

## D14-s2-01 -- narrative uses instance currency, units use feed currency (P8) -- VERIFY (low-medium)
- V1: mismatch_eur_feed_on_sek=3/3 lines; coordinator_unit_mismatch=0; null SEK feed 0; `--perturb` -> 0. Reproduced exactly.
- V2 (own metric: static count of `narrative.render` call sites in coordinator.py fed `resolve_currency` rather than `self.currency`): 1 of 1. `narrative.render`'s docstring premise ("the two are the same decision") is false since units became feed-declared: on a EUR feed numeric values are EUR and labelled SEK.
- V3: reachable (EUR/kWh Nord Pool feed on a SEK-configured instance is a real configuration). Consequence: mislabelled money in a user-facing text attribute; no control impact. Seam rule enumerates (9 static label seams + all published surfaces). Class P8 confirmed. Same defect as D14-s3-01 (duplicate; one fix).

## D14-s3-01 -- same defect via nightly replay (P8) -- VERIFY (low-medium), duplicate of D14-s2-01
- V1: base mismatched_seams=1 of 14 (plan_narrative attr.lines[]); clean 0; narrative_fixed 0; reintroduce 14. Reproduced exactly.
- V2: as D14-s2-01 (1/1 render sites on resolve_currency).
- V3: reachable; seam rule enumerates every published entity/field over a replayed day (all 14 money seams); class P8.

## D14-s3-02 -- report-on-change power meter read stale (N-staleness) -- VERIFY (medium)
- V1: polling 0; power stale 39/48, mode stale 47/48; newly unavailable 78 entity-cycles (measured_power x39, compressor_starts x39); perturbation (limit -> 1e9) -> 0 for both. Reproduced exactly.
- V2 (own metric, from fixture rows only, no coordinator: 30-min cycles where time since last value CHANGE exceeds INPUT_MAX_AGE_MINUTES): power 39/48, mode 47/48, outdoor 0/48 (null). Matches.
- V3: inputs.py prefers `last_reported`; a report-on-change device (Zigbee/Z-Wave meter idling at 0 W) does not refresh it in real HA, so reachable. A select written only on change is the exact rationale const.py:900 uses to leave the disinfection switch unbounded, yet the mode select has a 60 min limit. Consequence: two sensors unavailable most of the day; mode staleness produced 0 newly unavailable entities. Seam rule enumerates only the fixture's guarded inputs (5 of the INPUT_MAX_AGE keys); energy, house power, solar, floor-return and buffer keys are not exercised -- partial. Class N-staleness confirmed.
