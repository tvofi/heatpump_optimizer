# Class I1 sweep, round 10 (D14 method steps 3-4)

Class I1 in `dev/audit/config/bugclasses.json` is a guard that no check
exercises. The class row is `prototype-only`: the countermeasure is "per-site
mutation ratchet + widened inventory (F10.3)", and it has not landed. The
findings in the class are D3-s1-01, D3-s1-02 and D3-s2-01. This sweep ran at
handoff/audit-r10-register 9355f107d in a detached worktree.

## Property

A defensive guard protects a read or an emission. If no gate check drives the
guard's falsifying branch, the gate cannot pin it, and so a refactor can remove
the guard while the gate stays green.

## Enumerator

`python dev/audit/rounds/round10/D14/sweep-I1/enumerate_i1.py` is an AST scan
of `custom_components/heatpump_optimizer`. It generalises the three findings'
`seam_rule`s into three families:

- **LEN**: an `and` with an operand `<i> < len(<seq>)`.
- **DROP**: `if <name>:` whose body logs a Quarantined/malformed warning.
- **KEEP**: `if <x> and not self._<attr>:` whose body assigns `self._<attr>`.

It returns `RESULT seams=34 LEN=30 DROP=2 KEEP=2` (saved as `enumerate.out`).

- **Positive control.** The scan re-finds every finding site:
  - all 12 `get_current_action` guards (D3-s1-02)
  - `coordinator.py:6522` (D3-s1-01)
  - `ledger.py:306` and `snapshots.py:239` (D3-s2-01)
- **Null control** (`--fixture`): a clean synthetic module returns `seams=0`.
- **Perturbation** (`--fixture`): re-introducing one line,
  `y = xs and i < len(xs)`, moves the result to `seams=1`.

### Dynamic arm

`run_trace.sh` runs 13 closure scripts under an import hook
(`hook/sitecustomize.py`). The scripts are guard_pins, block_duty,
solar_alignment, debug_collect, wood_advisor, plan_view, manual_plan,
config_flow_steps, validate, edge, finite_boundary, optimality and features.
The hook records each LEN operand's outcome to `run.trace`. All 13 scripts
exit 0 under the hook (`rc.tsv`).

`probe_unexercised.py <seam>` exits 1 when the seam's guard never evaluated
False in those scripts. Its null control is `coordinator.py:4060`, which prints
EXERCISED and exits 0.

Cross-check: 11 of the 12 D3-s1-02 guards are never False, which agrees with
that finding.

What the trace does not cover:
- It does not prove a guard is unpinned by the scripts it did not run: env_drift,
  golden, stress, backtest, boost_drift_replay and the `.mjs` scripts.
- It does not prove that a short input is reachable in production. The finding
  makes the same caveat for D3-s1-02, which is rated low.

## Dispositions (34 seams)

- **Finding sites (15, `beyond_finding: false`)**: the 12 `get_current_action`
  guards, `coordinator.py:6522`, `ledger.py:306` and `snapshots.py:239`. Each
  has its finding's own probe.
- **Instances beyond the findings (17)**, every one never False in the gate:
  - `coordinator.py`: 2288 and 2293 (`_apply_result_payload`); 3974 and 3984
    (`_plan_slots.close`); 4110 (`reason_at`); 9040 (`_capacity_caps`)
  - `dhw_planner.py:67` (`_dhw_windows_at`): never evaluated at all, because
    `holiday_flags` is always None in the gate
  - `narrative.py:112` (`group_by_reason`)
  - `optimizer.py`: 1182 and 1188 (`classify_space_steps`); 1241 and 1244
    (`classify_dhw_steps`); 4015 (`_safety_release_steps`); 5055 and 5074
    (`_compute_baseline_power`)
  - `pump_arbiter.py`: 357 and 358 (`step_duty`)
- **Guarded (1)**: `coordinator.py:4060` (`_build_plan_views.series`). The gate
  drives its False branch. That a check asserts on the result is not proven.
- **Not applicable (1)**: `coordinator.py:9410`. It is a once-per-alarm rollback
  latch, not a keep-prior fallback. This is a false positive of the KEEP shape.

## Proposed barrier

No barrier is in place (`barriered: false`). The proposal has two parts, both
in the gate:
1. Make the LEN/DROP/KEEP enumerator a `tests/` structural check, with an
   allow-list of seams that carry a pinning check.
2. Make the trace hook an optional arm of features.py. It fails when a newly
   added seam is never False.

The cost is the AST scan, under 1 s, plus the hook overhead on features.py.
That overhead has not been measured in isolation. Measured on the
owner's 8-core Mac: features.py took 430 s under the hook, and the hook run
was unloaded.
