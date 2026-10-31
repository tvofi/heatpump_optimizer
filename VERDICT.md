Fix review: merge a85aea80db2b5af603fe813658cc75800bc05daf

bus-nonce: f01ed00d3279a1b7c6cbbc20545887ba

## Round

Round 1. The reviewed head is `a85aea80db2b5af603fe813658cc75800bc05daf`. Every number below was taken at this head, or at the merge base `a9ba3022e` with this head's tests.

## Findings

- The finding has no committed finder's harness, because it came from a live bundle (tvofi, 2026-10-30). The fixer's four R10-HOTFIX-AWAY-LIVE checks in `tests/features.py` are the fixer's own instrument, and the body says so. My reviewer block (`ev/reviewer_harness_block.py`) is also my own, built out of tree. Both are red at the base and green at the head, so the in-tree checks now serve as the regression harness. Carry: dismissed: live-bundle finding; the fixer's in-tree checks are red at base and green at head and pin it
- The body's real-Home-Assistant confirmation (a scratch venv outside the tree) did not land as an instrument, so I could not re-run it. The in-tree stub checks pin the same restore-then-resolve behaviour. Carry: dismissed: one-off confirmation; the in-tree checks through the production coordinator cover the behaviour
- `coordinator.py` and `away.py` are code-owned, so tvofi's approving review is required at merge. I flag this and do not block on it. Carry: dismissed: enforced by main-protect-checks' code-owner rule at merge

## Evidence

- RESULT mutation proof, run myself. The closure is `tests/features.py` with my reviewer block appended, run in a worktree at the head with one change each (diffs in `ev/variant_*.diff`):
  - head: `ALL 4533 REV FEATURE CHECKS PASSED`, rc 0.
  - base production (coordinator.py and away.py at a9ba3022e): 4 FAIL, namely both fixer checks (reload `(True, False, (21.0, 19.0, False), 21.0)` and resolve-first `((21.0, 19.0, False), False)`, matching the body's figures) and both of my held-read checks.
  - M1 (no gate in `_resolve_away`): 3 FAIL, the fixer's resolve-first check and both of my held-read checks.
  - M2 (no gate in the light refresh): 4 FAIL, the fixer's reload check, my two held-read checks, and my same-override null check.
  - M3 (`published_under` clause removed): 2 FAIL, the fixer's reload check and my held-read home-handover check.
  - No mutant is vacuous.
- RESULT, my own harness, independent of the fixer's.
  - The store read is held on an event while the setup refresh and a resolve start inside it. At the head both stay pending for 50 loop turns, then carry the stored override (`away_override_active True`, the return time matches, `away_active True`). A home handover is dropped.
  - At the base, neither the refresh nor the resolve waits, and both publish override false.
- RESULT null controls at the head:
  - Away off with a reload republishes the handover (the fixer's check: ok at base and head).
  - The same away override before and after a reload republishes the handover (mine: `(True, True)` at head).
  - Away on with no reload: the light refresh publishes the restored override.
  - The gate always resolves on a cold start, within a 5 s timeout, in all of these cases: an empty migrated store, no stored payload (the helper-migration path), a store read that raises, and no restore spawned (`_RESTORES` has no key).
  - The gate opens on task completion whatever the outcome, or at once when `spawn` returns None (`boost.spawn_restore_session`).
  - `spawn_restore_session` runs in the coordinator constructor, before `async_config_entry_first_refresh`. The restore never awaits a refresh, so there is no deadlock path.
- RESULT class census (fixer.md step 8), re-run under the body's rule: 41 hits (`ev/census_grep.txt`, enclosing functions in `ev/census_enclosing.txt`). Every enclosing function matches a disposition in the body.
  - `boost.apply`, `_apply_action` and the pump_arbiter readers are reached only from `_async_update_data`. `async_simulate` and the entity readers (`switch.is_on`, `datetime.native_value`, through the `away_state` view) exist only after the first refresh.
  - No seam is left open.
- RESULT timing: on a dropped handover the light refresh publishes no plan, the same as a fresh start. `async_setup_entry` then starts `async_request_refresh` as an entry background task, so the window without a plan lasts one solve; the body puts that at 30 to 70 s on a Pi, a figure I did not re-derive on hardware. The added wait is the restore's store reads only.
- RESULT figures:
  - `tests/features.py` at the head prints `ALL 4609 FEATURE CHECKS PASSED`, which matches the body's denominator.
  - `tests/structure.py` passes at the head (`STRUCTURE RATCHET PASSED`). Budgets move only down (class_excess_loc 17672 to 17670, max_class_loc 8065 to 8063). The payment is a shorter docstring, which is a real reduction and not instrument play.
  - The scoped-gate counts (22 run, 24 passed) are cited from the body and not re-run (CI's heavy runs are cited, fix-review.md 11).
- RESULT forbidden files:
  - VERSION, the manifest, the RELEASE_NOTES heading and both claim files are untouched (three-dot diff is empty), so there is no golden drift to claim.
  - The governance roles diff from base to main is empty.
- RESULT merge: `git merge-tree --write-tree origin/main a85aea80db2b5af603fe813658cc75800bc05daf` gives rc 0, tree be2e5792 (`ev/merge_tree.txt`). Main's 17 newer commits touch nothing under custom_components.
- RESULT mutation ledger: the stale GUARD_OFF 026f6cc7 pin is removed. BOOLOP and GUARD_OFF aa838ac4 are pinned as killed by tests/features.py. My M3, which drops the clause, is killed too.
- RESULT forward-carry: the census-header carry is in the tree at tests/features.py (the null-control comment). R10-HOTFIX-AWAY-SETBACK is routed by the body; carry_audit at the head reads 3 routed, 0 unrouted.
- CI at this head, read from the check-runs API at review time:
  - Most checks are success, nightly-ha / record / kernel-points / arm / delivery-status-publish are skipped, and CodeQL is neutral.
  - Still in progress: tests / fast (3.14), coverage, closures, mutation, governance / instrument-self-tests, codeql python, and the second prelude.
  - No check is red. No pr-contract run appears yet. The body declares no red CI check; the census null-control red was local, caught and answered in the body.
