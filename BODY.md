Fix review: blocked bb2ab4b3b54485ba07ad4fb4ae5f7faf58a7bbd2 wrong-argument-order: _propagated_slab passes the dwell's shares to space_draw_kw as (dhw, space); space_draw_kw's split is (space, hot water)

## Block
custom_components/heatpump_optimizer/coordinator.py:1085 calls `draw_range.space_draw_kw(..., (a.dhw, a.space), ...)`. `space_draw_kw` (draw_range.py:417) computes `running_kw * space_share(*split)`, and `space_share(space_kw, dhw_kw)` (draw_range.py:389-395) returns `first / (first + second)`. Its own docstring, and `_commanded_split`'s, define the pair as (space, hot water). `heat_energy.Attribution` is `(space, dhw, observed)`. So the call hands the dwell's hot-water hours in the space position, and the apportioned draw is the hot-water share of the draw, not the space share.

## Findings
- coordinator.py:1085 — argument order swapped. Hand-derived consequences, read from the code; I did not execute them:
  - Dwell 0.25 h space, 0.75 h hot water, 4 kW draw: the fix books 3 kW as space heat. The correct figure is 1 kW.
  - A dwell wholly on hot water (space 0, dhw 1) with `space_served=True` (it is True for any observed dwell via the new `a.observed`): the fix books the whole draw as space heat, where it should book 0 kW. This is the very defect the PR names, "books the whole draw as space heat", moved to the opposite duty.
  - A dwell wholly on space books 0 kW, the null control inverted.
- tests/features.py:2305-2331 — the new checks cannot see the swap. Every case is a half-and-half dwell (switch at `gap_h/2`) or all-space in a symmetric comparison: `swback == half` and `out == half` hold for (0.5, 0.5) under either argument order. The `still` null control (all-space) expects `== heating`; under the swap the all-space dwell would book 0, so it would fail. I could not run it to confirm (see Evidence), so it may rest on an `observed`-path nuance. Still, no asymmetric dwell (e.g. 1/4 against 3/4) is tested, which is why swapping the arguments leaves the half-draw checks green. Mutation proof missing: swap `(a.dhw, a.space)` to `(a.space, a.dhw)` and the half-draw checks still pass.
- The harnesses r10_cop_gate_slab.py and r10_cop_gate_band.py were not run (see Evidence).

## Evidence
- Setup: `cloud-setup.sh --check` printed `OK python3 is /opt/hpo/venv-ci/bin/python3`; unshallowed and fetched both SHAs; head checked out detached at bb2ab4b3b.
- Diff read: `git diff a5dce6b9e...bb2ab4b3b` (7 files; production code only in coordinator.py and the draw_range.py docstring).
- `/opt/hpo/venv-ci/bin/python3 tests/features.py` and the `venv-ha` python both failed on import: venv-ci has no `homeassistant`; venv-ha lacks `paho` and `scipy`. I tried `pip install paho-mqtt` and it did not complete the environment. So the PR's own tests, the mutation proof, and the harnesses were NOT executed. The block rests on code reading alone: heat_energy.py `Attribution(space, dhw, observed)`, `dwell.shares` returning "(space hours, hot-water hours)", and draw_range.py:389-417.
- A direct import of draw_range.py outside the package failed on a relative import, so the 4-line `space_share` arithmetic above is hand-derived, not run.
- Not re-derived: VERSION / manifest / notes untouched (diff stat shows none touched), claim-file drift, and any body figures. The brief excludes CI.
