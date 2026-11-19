Fix review: merge 28977f9e820ee1813eccd5952484e0365e72f91a
bus-nonce: f2c80bdc476f166c2b68e342f14c0d8f

Note: mutation-red: tests / mutation (job 135339893295) is red on the merge ref only: "MUTATION TABLE REFUSED ... coordinator.py:HeatPumpOptimizerCoordinator.async_simulate RETURN_DEL 1457a93f: disposition names no site the inventory generates (old pin '        return payload')". That pin was added on main (tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.RETURN_DEL.1457a93f.json, absent at the merge base, the reviewed head and this head), and this PR re-indents that return inside user_slot (head coordinator.py:11312). mutation-autofix concluded success without a commit. Owed before the train lands it: drop or re-pin 1457a93f against the new site; no production change. Not caused by the delta under review. bus.sh post refuses merge while it is red (C8).
Note: stale-figure: the body's ## Architecture score still quotes "score.py --diff ae0ed64af898" at the earlier base ("dS +0.0208 WORSENS (inadmissible: coord_footprint 2505->2517)"); the delta scores score.py --diff 1cf4d759 6b9b3ce8 = "dS +0.0000 NULL" (ev/archscore_delta.txt), and the arch-score check is green at the head, so the gate does not refuse it; owed: re-take the paragraph at the current base.

Round 2, delta only (tvofi 2026-11-09): git diff 1cf4d759c5..28977f9e82 = c06d2fb954 (bot: 34 mutation kill pins, tests/mutation_ledger only) + 6b9b3ce8a7 (the fix; coordinator.py, tests/features.py, tests/harness.py), merged at 28977f9e. Reviewed head from probe/rev-3738-7b8d4ad6 (verdict 3738 1cf4d759): no review/3738 or verdict/3738 ref exists on origin.

## Prior findings
- Block (D1-s1-03 trailing refresh dropped under upstream's debouncer): RESOLVED. The finally now spawns self.async_refresh() with eager_start=False (design Amendment 1, design-verdict 6b017208 approve 85feefcc). Re-ran the round-1 reproduction with Home Assistant 2025.2.0's own helpers/debounce.py, verbatim (ev/ha/debounce.py; ev/block.py), and a 2-cycle count per origin plus null controls (no write -> 1 cycle):
  - head: debounced+write 2 cycles (s1 e1 s2 e2, sequential), direct+write 2, both no-write 1; 17/17 block checks pass (ev/run_fix.log).
  - old line restored (async_request_refresh, eager): debounced+write 1 cycle -> block reproduces; the PR's two D1-s1-03 checks FAIL (ev/mut_old_request_refresh.log).
  - async_request_refresh non-eager: still 1 cycle; confirms the commit's "eagerly or not" (ev/mut_request_noneager.log).
  - async_refresh eager: PR's upstream-debouncer check FAILs on nesting "(())" (ev/mut_eager_direct.log).
  - The new test drives the trailing arm through a debouncer whose job is a separate eager task; it fails at the reviewed shape and passes at the fix, as owed.
- Finding (shutdown reason wording): carried dismissed in round 1; unchanged.

## Evidence
- eager_start is in HomeAssistant.async_create_task since 2024.3; hacs.json minimum is 2025.2.0; nightly-ha (2025.2.0) and (stable) are green at the head.
- A direct async_refresh takes no debouncer lock, the same shape as 2025.2.0's _handle_refresh_interval (ev/ha/update_coordinator.py:265-268); a request during it is absorbed by solve_gate (refreshing arm), so no new overlap class.
- git merge-tree --write-tree origin/main(7ae05284) 28977f9e820ee1813eccd5952484e0365e72f91a: rc 0 (ev/merge_tree.txt). Three-dot from the merge base: VERSION, manifest.json, RELEASE_NOTES.md and both claim files untouched.
- The body names 28977f9e820ee1813eccd5952484e0365e72f91a as the head; refs/pull/3738/head read back at 28977f9e820ee1813eccd5952484e0365e72f91a.
- Checks at dispatch: all concluded green but tests / mutation (above) and gate (failure "still being judged", job 135340374682); closures, coverage, fast (3.14), replay still in progress. Review packet: Refusals none.
