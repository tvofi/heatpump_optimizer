Fix review: blocked 1cf4d759c5022d4a51a93f2c6f9aaac2afe6d008 code: the D1-s1-03 trailing refresh is dropped under Home Assistant's real debouncer when the refresh it trails came through async_request_refresh

bus-nonce: 7b8d4ad668f0ad7b6e73faa344b92c5b

Round 1 (first review of this PR; no reviewed head before it). Reviewed against the approved design `design.md` at 29f8ba81157134ab65ab38a45c4668b6c4834ef5.

## Block

- **Design §3 B's trailing arm does not do what it claims under upstream Home Assistant.** `_async_update_data`'s `finally` (`coordinator.py:6196-6197` at the head) spawns `self.async_request_refresh()` through `self._spawn`, which calls `self.hass.async_create_task(coro)`. Upstream (2025.2.0, `homeassistant/core.py:793-832`) defaults `eager_start=True`, so that coroutine runs synchronously inside the `finally`. If the refresh that is ending was started by the debouncer (`async_request_refresh` → `Debouncer.async_call`, which holds `_execute_lock` and has no `_timer_task` until the job returns), `_async_schedule_or_call_now` returns False on `self._execute_lock.locked()`. The trailing request is then dropped. That refresh is D1-s1-03's own `--origin debounced`, which every user writer and the setup's first solve use. The `# lands once the debouncer is free` comment is false there.
  - Reproduction (reviewer-built, not the finder's harness): `ev/block.py`, a features block that swaps in upstream 2025.2.0's own `Debouncer` source (`ev/upstream_2025.2.0_debounce_excerpt.py`). It also gives the stub hass upstream's eager `async_create_task` and `async_run_hass_job`. A user write lands mid-refresh while the plan is not being solved. Results (`ev/repro_run1.log`, `ev/repro_run2_controls.log`):
    - `origin=debounced` (eager spawn, upstream's default): `debouncer_refreshes=1`, so the trailing refresh is lost.
    - Positive control: `origin=direct` (the scheduled-interval shape, lock free): `debouncer_refreshes=1`, so the trailing refresh runs.
    - Cause control: the same debounced run with the trailing spawn made non-eager (`spawn=task`) or deferred 10 ms (`spawn=later`): `debouncer_refreshes=2`, so the drop is the eager spawn meeting the held lock.
  - Why CI and the PR's checks are green: `tests/hastub`'s `Debouncer.async_call` awaits the job coroutine inline and arms its timer synchronously before any spawned task runs. The stub `HomeAssistant` has no `async_create_task`, and `"D1-s1-03: a request landing while a refresh runs is answered by one more debounced refresh …"` replaces `_debounced_refresh.async_call` with a counter, so no check exercises the lock. The finder's `m4_race.py` lands its write during the solve (the `rerun` arm), which works, so the harness's `7 → 0` does not cover the trailing arm.
  - Owed: a spawn that cannot run while the debouncer still holds the lock. For example `eager_start=False` on that one spawn, or a hop past the lock, chosen by the fixer. Also owed: a check that drives the trailing arm through a debouncer whose job runs as a separate eager task, as upstream's does. It fails at this head and passes at the fix. `ev/block.py` is a starting point.

## Findings

- The `"shutdown"` reason that `async_run_optimization` now returns at Home Assistant stop goes, on the `run_optimization` action, to the generic `run_optimization_solve_failed` error. A call at stop raises a "solve failed" message for a solve the stop broke. It is cosmetic, reachable only during shutdown, and nothing persists. Carry: dismissed: shutdown-only wording; no state or notice outlives the stop

## Evidence

- Mutation proof re-run at the head (`ev/mut_summary.txt`, `ev/mut.sh`, `ev/mutant_m_*.log`), block `# -- R11-SEAM-cycle-solve: when a solve runs (solve_gate)`:
  - unmutated: rc 0, 0 FAIL;
  - `begin_solve`'s `gate.background_taken = False` deleted: 1 FAIL ("D9-s1-02: one background what-if per main solve …");
  - `absorb_request`'s refreshing arm deleted: 2 FAIL ("solve_gate: an idle request …", "D1-s1-03: a request during a refresh trails it …");
  - `user_slot`'s supersede test made `if False:`: 1 FAIL ("D9-s1-03: of four overlapping user what-ifs …").
  - Each matches the body's claims. No survivors were found among these mutants.
- `git merge-tree --write-tree origin/main 1cf4d759c5022d4a51a93f2c6f9aaac2afe6d008`: rc 0, tree 7e566daee1ed (`ev/merge_tree.txt`). origin/main equals the merge base 8751943e17, so the head is not behind main.
- Across the merge base to the head (three-dot), no diff touches `VERSION`, `manifest.json`, `RELEASE_NOTES.md`, `tests/golden/claimed_drift.txt` or `tests/golden/card_claimed_drift.txt`.
- The body's head (`1cf4d759c5…`) is the head reviewed. `refs/pull/3738/head` was read back at the same SHA.
- CI: `merge_train.py classify 1cf4d759c5022d4a51a93f2c6f9aaac2afe6d008 --pr 3738` printed `WAIT … pending: gate red: none` on every poll (`ev/classify_polls.txt`). The poll was stopped once the code block was established. A blocked verdict does not depend on CI, and no red was read.
- The review packet refused `introduced-red: unreadable` because `instrument-self-tests` was still queued at render (`ev/review-packet.md`).
- Design departures 1–7 in the body were judged against the design note:
  - 2 (`hass.data` key in place of a module Event): accepted, measured by the body's D1-s2-55 failure;
  - 3 (diagnose publishes without `async_set_updated_data`): accepted; upstream's re-arm and cancel is real;
  - 4–7: accepted as shape;
  - 1 (no at-exit WNOHANG reap): accepted, since D1-s3-04's peer-wait harm needs a peer solve, which no longer exists at exit.
  - None of them is the block.
- Figures under `## Figures` were not re-derived at both ends. The block is independent of them, and the finder's harnesses do not reach the trailing arm (see Block).
