blocked 351b5ce74614427e46c8f79f96f25af15236058b root-cause-unanswered: briefs went red, unanswered; root-cause-unanswered: nightly-ha (stable) went red, unanswered; conflict: .claude/workflows/carry-1644.json against main 5f4f641a

# R9-F1.7 fix review, PR #1788 (round 1)

Measured at 858baeb2 (code c4e1e0c0 + merge of main 830f84ad + claims drop + row).
The live head is now 351b5ce7, one `ci: pin killed mutants` bot commit above it
that adds 8 files under tests/mutation_ledger/killed_by and touches no code, so
every number below holds for it. Reviewer: cloud seat, opus. Evidence: this directory.

## Blocking

1. **`briefs` red, caused by this diff, not named in the body.** `node .claude/workflows/brief_lint.mjs`
   exits 0 at base 830f84ad and 1 at the head (brief_lint_base.log, brief_lint_head.log, ci_briefs_job.log).
   The only new error: `[carry-1395.json carry 0] path:line: custom_components/heatpump_optimizer/sysid.py:1388:
   '_predict_step_excursion' not found`. The diff adds 28 lines above that call in sysid.py
   (`night_gains_prior_kw`, `step_detached`, the arm() seeding), so the call is at sysid.py:1422 at the head.
   Fix: re-anchor carry-1395.json's citation to the call's new line. Cheaper detector: brief_lint runs locally
   in under a second and is not in run.sh's scoped gate.

2. **`nightly-ha (stable)` red, caused by this diff, not named in the body.** CI: `FAILED: 2 of 58 checks:
   ['contract:real_provider', 'run:exit_status']` (ci_nightly_ha_stable_job.log). Reproduced locally:
   `tests/ha_contract.py --contracts-only` against real homeassistant 2026.9.3 reads `ALL 56 contracts PASSED`
   at base and `1 of 59 contracts FAILED` at the head (ha_contract_real_2026.9.3_*.log):
   `an auth failure on a steady refresh latches, does not escape, and starts reauth [AssertionError: raised
   AttributeError("'_Entry' object has no attribute 'async_start_reauth_if_available'")]`.
   Current upstream `_async_refresh` calls `config_entry.async_start_reauth_if_available(self.hass)`
   (update_coordinator.py:468 and :554 in 2026.9.3); the contract's fake entry only has 2025.2.0's
   `async_start_reauth`, and its cite names only the 2025.2.0 lines. Production is not affected: a real
   ConfigEntry has both methods, and `_if_available` forwards because config_flow.py defines
   `async_step_reauth`. Fix: give the contract's entry both methods, count either one, and cite both
   upstream versions. The body's 2025.2.0 figure (`ALL 59 contracts PASSED`) is the floor only.

3. **Conflict with main.** Main moved to 5f4f641a (#1787, R9-RCA-1747). `git merge-tree --write-tree
   origin/main 858baeb2` exits 1: `CONFLICT (content): Merge conflict in .claude/workflows/carry-1644.json`.
   It is not a claim file. Both sides append one carry after the same entry; the right resolution looks like
   keeping both entries (F1.7's published-schedule fallback, and RCA-1747's census reach clause). That is
   the orchestrator's merge to make, and it moves the head, so the merged file needs a re-check.

## Verified (no action)

- Ancestry and paths: the diff 830f84ad...858baeb2 has no handoff/ path. Main's own tree carries
  handoff/round9/fix/resume/{EG-B10,F2.4,F7.5}.md, which is main's issue and not this PR's (the body names it under Friction).
- Claim files: at the head `tests/golden/claimed_drift.txt` claims nothing. e151e57c drops EG-B8's five
  inherited coord_* claims. The scoped gate at the head reads `NO UNCLAIMED DRIFT: 56 scenario(s) checked
  against 830f84ad` and `NO STALE FIXTURE: 56`. VERSION, the manifest and the notes heading are untouched.
- Scoped gate at 858baeb2 (Haswell, 1 thread, gate_858baeb2.log): `MODE: SCOPED -- 24 script(s) run, 3 scoped out.`
  `2 TEST SCRIPT(S) FAILED`. One is typing_ruler, because the first interpreter was 3.14.0rc2; rerun below.
  The other is stress.py, `1 of 87` (shoulder/tariff+cycle 276x against 268x).
- stress.py CPU rows, run alone on this box, twice at each end (stress_*.log): at base 830f84ad run 2,
  shoulder/tariff+cycle reads 270x and tariff+pv+cycle 290x (both over the 268x budget). At the head, run 1 reads
  `ALL 87 STRESS CHECKS PASSED` (worst 231.8x) and run 2 has one row at 284x. The same rows go red at base,
  and the head's solver-work checks against main pass, so the solver's work did not change. **Judged box noise,
  not this diff.** The fixer's account holds, except that run.sh runs stress alone, so it was not other scripts
  running at the same time. (Base runs also print 4 "no baseline" fails because origin/main is that commit.)
- Typing: `tests/typing_ruler.py --mypy` on Python 3.14.7 with the pinned lock gives `ALL 9 typing-ruler checks PASSED`
  (typing_mypy_858baeb2.log). CI's `typing` is green.
- Mutation table: `mutation_table.py --scope changed --base origin/main` gives `MUTATION TABLE REFUSED --
  3577 unpinned site(s) against 3573 at the ratchet base 830f84ad` (+4 net, the same as the body's
  3582 against 3578 on its old base). The bot commit 351b5ce7 has since pinned the 8 new sites.
- My mutants, one production line each, in a copy at 858baeb2 (mutants.py, mutants_summary.txt, mut_*.log).
  **All 12 were killed:**
  - M1: rank the advisor on the loop. P10 barrier 3 FAIL.
  - M2: step sysid on the loop. 1 FAIL (sysid arm).
  - M3: executor fallback made inline. 1 FAIL (fallback arm).
  - M4: drop `auth=`. Both D10-s1-03 checks fail.
  - M5, M8, M10: drop the scale in hold demand, the forecast and `_space_demand_kw`. The linearity check fails.
  - M6, M7: drop the scale in the one- and two-zone caps. The cap-drift check fails.
  - M9: drop the arm() prior seeding. 2 R9-P5 checks fail.
  - M11: night window off by one hour. The #1655 prior check fails.
  - M12: the first-refresh wrapper catches only UpdateFailed. The first-refresh auth check fails.
  - Control: the unmutated head reads 0 FAIL on the barrier.
- Finder harnesses from 79aa98ec (sha1s match the body), at 830f84ad and 858baeb2 (finder_*.txt):
  - loop_work: `loop_simulate_steps_per_read` 384.00 to 0.00, `advisor_calls_per_read` 2.00 to 0.00.
    At base the perturbation moves it (384 to 8).
  - auth_failed: `auth_as_transient` 3 to 0, `transient_ok` 2 to 2. With --fix it reads 0 at base.
  - slab_cap_scale: `drift_max_abs_Kph` 1.4400 to 0.0000. --perturb gives 0 at base and 4.3200 at the head
    (the double application). The null arm is 0 at both ends.
  - sysid_loop: flat by design (`max_step_call_ms` 242.35 to 287.92). Its companion is the barrier's sysid arm, killed by M2.
- Enumerators:
  - S7 at 1152a74346: `candidate_sites` 6 to 4, the same sites the body dispositions (s7_enum_*.txt).
  - P2 at c44e7bcd60: 40 cells, 0 disagreements at both ends. Its --perturb arm asserts on an anchor
    main already removed, so rc=1 at both ends; this is not this PR's.
  - I did not run P11. The body's cell move is not re-derived here.
- Forward-carry: carry-1644.json gains the F2.4 review item 4 carry. carry-1655.json removes the consumed
  P5 entry and keeps F2.3's.
- Other CI on the head: fast, typing, mutation, closures, coverage, hassfest, CodeQL and nightly-ha (2025.2.0) are green.

## Observations (non-blocking)

- The sysid step now runs in the process worker, where logging has no handler. The INFO lines
  "Starting system identification" and "System identification complete: tau=..." and the #1396
  `_LOGGER.exception("System identification fit raised")` no longer reach Home Assistant's log.
  This follows the precedent of the solve's own logging in the worker. The published result and reason are unchanged.
- The `## Head` section labels e151e57c as the merge; the merge is da9cc162, and e151e57c is the claims drop.
- A step's worker copy replaces `self._sysid.config` after the await, so a `config.enabled` write from
  the arm service during that await is lost. arm() refuses while active, so the race has no effect today.
