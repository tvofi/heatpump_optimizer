# D7#1 verification (round 10), one verifier, lenses V1-V3

Worktree: detached at handoff/audit-r10-register 9355f107d. Static counts: contention-immune. load1 5.2-17, thread_factor 1.000.
Own harnesses: `verify-tools/pad2.py` (on-disk pad and the real `tests/structure.py` CLI), `verify-tools/inplace.py` (an AST census of in-place writes through `<x>.<hub>` or a local alias).

## D7-s1-01: verify, low, class N-structure-blind
- V1: `class_growth.py` gives second_class=0 and coordinator=1 (8705 -> 9906), an exact match. Perturbation (`max(` -> `sum(` in measure, with `default=` dropped): second_class becomes 1 (22314 -> 23515). The number moves in the stated direction. The null arm (coordinator) moves 1.
- V2: a different pad shape (20 chained XOR/mod methods, 1641 lines) on a disk copy, through the real CLI. With `HeatPumpOptimizer` it reached 5151 LOC and `structure.py` exited 0 (`ok max_class_loc 8705 <= 8705`). The same pad in the coordinator exited 1.
- V3: this is about the gate, not runtime, so reachability is not applicable. The consequence is up to 5195 unpriced lines per non-largest class. Seam rule: there is no `seam_rule` field. The perturbation covers every god class, so it enumerates the phenomenon's seams. Class: `new` is corrected to N-structure-blind (bugclasses.json: a ratchet measures a proxy, `max`, instead of the property it gates).

## D7-s1-51 (arch1-01, P1): verify, low (finder: medium)
- V1: P1 gives delta_S +6.5186, hub_solve_writes 38 -> 16, footprint +3 (WORSENS alone). `--revert` gives 0.0000. Exact. Baseline 554e2ecf: its custom_components is byte-identical to 17f1c55 (`git diff` is empty).
- V2: my AST census of `_current_state` in-place writes is 21 (18 in `_update_current_state`, 2 from the ECL110 MQTT callback, 1 power event). After P1 it is 3. There are 7 awaits between the first and the last write of `_update_current_state`.
- V3: reachable in real HA. The cycle runs on the loop, and the awaits let other loop tasks read a half-updated live state. No consumer was shown to read a torn value and no golden drift was recorded, so this is hygiene. I lower severity to low. Seam rule (`git grep _current_state\.x =`) gives 21, equal to my AST census. It enumerates the attribute-store seams, not setattr or mutating calls. Class: N-shared-config is defensible only through its detector (hub_solve_writes). The mechanism (off-loop solve) is not shown.

## D7-s1-52 (arch1-02, P2): weaken, low; class corrected
- V1: delta_S +2.3771, shared_inplace 22 -> 16. Revert gives 0.0000. Exact.
- V2: my AST census finds 10 in-place AwayState writes in async_set_away and _resolve_away (11 package-wide), not 6. After P2 there are 4. The finder's metric dedupes differently; both definitions are given for the judge.
- V3: reachable, through the service call and the cycle. There is no await between the writes (the finder agrees), so there is no torn read, and the consequence is clarity only. Seam rule grep gives 9. That is narrower than the AST census of 11, and it misses AwayState mutation under other names (the finder's own boost.restore_session lead). It enumerates partially. Class: not N-shared-config (no solve, no concurrent reader). It is hygiene, and no class fits: new.

## D7-s1-53 (arch1-03, P3): weaken, low; class corrected
- V1: delta_S +1.5020, shared_inplace 22 -> 18. Revert gives 0.0000. Exact.
- V2: `lead_pending.clear()` sites go 4 -> 1, and external `.heat_output_kw =` in flow_meter goes 1 -> 0. Total 4 (with the solar append), which matches.
- V3: reachable, but the finder notes the mutation time is unchanged, so this is a Demeter cleanup with no hazard removed. Seam rule as written does not enumerate. Run with PYTHONPATH=tools/audit, it exits 0 and prints nothing (`details.sites` is never evaluated); without that path it fails with ModuleNotFoundError. Class: not N-shared-config. It is hygiene: new.
