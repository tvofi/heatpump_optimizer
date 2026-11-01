## Raise justification

`seam_cut_total` 422 -> 423, approved by orchestrator s9 under mandate 6329234399 (scope all, budget-raise covered); the reason is in the commit message of `21ed69e8`. The crossing: the undo point must wait for the snapshot store's read, so the learning seam reads the core-owned `_snapshot_store`.

Payments tried: six, one line each below; none improves the code.

- `async_factory_reset` in the `core` seam: +2 (core calls the learning void path; core reads the grid-owned `_price_model_store`), worse.
- Dropping the snapshot-store wait: +0, unsound -- the undo point can be written over a ring not yet loaded, replacing eight weeks of snapshots.
- Refusing the reset while `_snapshots_loaded` is false: +0, but a user-facing refusal and new strings for a window no user reaches, worse than waiting.
- Adding the snapshot store to `_restored_stores`: the same (learning, `_snapshot_store`) pair, +1.
- Handing the unload to a learning helper as a callback: moves the metric by making the code worse, declined.
- Re-labelling `_apply_house_heat_loss_scale`, `_apply_lower_floor_loss_ratio` and `_apply_buffer_cooling_rate` from core to learning in `tests/seam_map.json`: -1, a map edit made to pass the budget -- gaming, declined (and declined by the orchestrator).

Architecture score: dS +0.0030 IMPROVES

(`python3 tools/audit/archscore/score.py --diff 92588d581fde4ce287af3db5e8bb61461dc28015` at this head, `coord_footprint 2389 -> 2384` (the same against `8fec54ee`); earlier takes read dS +0.0036 against `8fec54ee` at `96211117`, +0.0048 against `0cae227c`.) The fix review at `96211117` judged the six payments and found no missed one.
