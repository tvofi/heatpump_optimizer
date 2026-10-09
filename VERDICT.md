Fix review: blocked b731ef6b35d8d49f92d2fa098d28225cae83c8c3 harness: moving _on_off_service strands ledger pin coordinator.py:_on_off_service RETURN_DEL (mutation REFUSED, entities.py 1 FAIL in fast) and breaks D12-s2 surfaces.py --perturb (AttributeError)

bus-nonce: 19cf4e97afaa49060238234d14e26030
seat: review-2070, round 2. I reviewed the delta f74924e09..b731ef6b35d8d49f92d2fa098d28225cae83c8c3 (c3d16ace9, d02f851e1, b731ef6b3) from a detached worktree at the head.

## Blocking: the switch-router move breaks two committed instruments

1. **The mutation ledger still pins the removed site.** CI at this head:
   - `mutation` (check-run 113611382766) prints `MUTATION TABLE REFUSED -- the ledger disagrees with the deterministic inventory: coordinator.py:_on_off_service RETURN_DEL dac85d34: disposition names no site the inventory generates`.
   - `fast (3.14)` (113611382675, MODE: SCOPED, 23 run) is red on `tests/entities.py`, 1 of 2227 failed: the `--anchor` re-drive check (R9-F10.13), whose real run hits the same refusal. I reproduced it locally (evidence-r2/entities.txt).
   This is not the autofix path: autofix pins killed unpinned sites, and it does not re-key a disposition whose site moved. The pin needs re-keying to `pump_arbiter.py:on_off_service`. The body answers `mutation` as "red until mutation-autofix pins", which is no longer the reason, and it does not name the entities red (step 11).
2. **The finder's #1526 harness can no longer run its perturbation.** `dev/audit/rounds/round9/D12/s2/surfaces.py --perturb` patches `coordinator._on_off_service` and now raises `AttributeError`, rc=1 (evidence-r2/surfaces-r2--perturb.txt). Its baseline arm still passes, so no check goes red: the breakage is silent. The harness's patch target and docstring, and the docstring in `mode_domain.py`, need to move to `pump_arbiter.on_off_service`.

## Behaviour of normal plan writes (the orchestrator's focus): unchanged, null control passed

I used the finder's harness (D12-s2 `surfaces.py`) at both ends.
- **Baseline.** At f74924e and at b731ef6b35d8d49f92d2fa098d28225cae83c8c3: every switch-slot cell (switch, input_boolean, climate) has misrouted=0 and calls=2, and failing_surface_cells=0. All 13 cells are identical, so the plan write's routing and call count did not change.
- **Perturbation, retargeted by me** (evidence-r2/surfaces_retarget.py, which patches `pump_arbiter.on_off_service`): at b731ef6b35d8d49f92d2fa098d28225cae83c8c3, 0 -> 2 failing cells (input_boolean, climate). That matches the committed perturbation at f74924e (0 -> 2). The plan write now routes through `switch_supply`/`on_off_service`, and the harness still sees a misroute there.
- **The `switch_supply` fence is equivalent to the removed try/except.** It catches Exception and logs, and the cycle continues. Only the logger (pump_arbiter's) and the message, which now names the entity, changed.
- **`allow_on` with no cut on record returns the plan's value.** The features null control covers this.
- **Gap, not blocking, found by reading only, no mutant run.** No committed check drives `_apply_action` after a cut. The only `_apply_action` run in the section (`_ec_real`) has no cut, and the `allow_on` checks call the function directly. Reverting the coordinator line to `heat_pump_on = bool(...)` would therefore leave the refresh hold dead with nothing red. M14 as described cannot be that mutant. Owed: a check that cuts, re-runs `_apply_action` inside MIN_OFF and asserts the switch is not turned on, plus the null control past MIN_OFF.

## Round-1 items: resolved

- **EntryConfig.** early_cutoff reads `EntryConfig.from_mapping` and is on `_EC_MIGRATED`. The UNCLASSIFIED row is gone. The remaining entities fail is item 1.
- **One writer.** `on_off_service` and `switch_supply` now live in `pump_arbiter.py` and take values. The body names the alternatives (an import cycle; a coordinator callback, which rule A forbids). Sound.
- **archscore.** `--diff` shows coord_footprint 2587 -> 2589 (WORSENS +2). My per-function attribution matches the body exactly: the class -1, `state_for` +1, `_tail_freeze` +1, the diagnostics row +1 (evidence-r2/footprint-r2.txt). Each piece is stated and admitted by the design note.
- **structure.** max_class_loc is 8810 against 8810 and the ratchet passes. The re-record is earned by moving the writer out of the class: the try/except block left.
- **D6 headers, harness location, layout.** layout passes, with retired back to 3, which is main's count. The harness is at `dev/audit/harnesses/`.
- **UTC.** The new DST section kills my wall-clock mutant (efbbf79a3, local only): 2 of 134 failed, and the head passes 134/134.
- **Refresh hold.** The design is sound. It is let through at once on exempt steps, and on the scheduled cycle it cannot fire, because a cut is refused with less than MIN_OFF to the cycle end. The coordinator wiring is unpinned (above).

## Conflicts with #2065 and #2066

`git merge-tree` of b731ef6b35d8d49f92d2fa098d28225cae83c8c3 with each: coordinator.py and closures.json merge cleanly in both. Both conflict in diagnostics.py (the S7 loop rows), D6 claims.{py,md}, docs/architecture.md and tests/deployment_shape.py, because each PR adds a module and bumps the same counts. These are count and row conflicts that a later lander resolves, and design-note section 2 orders 6 last. None touches the moved switch writer.

## CI at b731ef6b35d8d49f92d2fa098d28225cae83c8c3

`closures` passes. `mutation` and `fast` are red (above). `nightly-status` is red and is main's, as the body says. `coverage` was still running when I posted (evidence-r2/check-runs-b731ef6.txt).

RESULT surfaces baseline failing_surface_cells: f74924e 0, b731ef6b35d8d49f92d2fa098d28225cae83c8c3 0 (switch-slot calls 2/2/2 both ends)
RESULT surfaces perturb: f74924e 0->2; b731ef6b35d8d49f92d2fa098d28225cae83c8c3 committed arm AttributeError rc=1; retargeted 0->2
RESULT archscore coord_footprint 2587->2589 (+2, attribution matches body)
RESULT dst_checks head 134/134; wall-clock mutant 2 FAIL (killed)
RESULT mutation REFUSED: stale ledger pin coordinator.py:_on_off_service RETURN_DEL dac85d34
RESULT entities 1/2227 FAIL (anchor re-drive, same refusal)
