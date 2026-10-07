Fix review: blocked e6e9b775dc775f71da7dd65fb061723912afda32 harness: CI timed the replay at 1576 s (timeout, rc=124) at the code head; the fix does not bring it under the limit

bus-nonce: 88e3ddc6ae218d8074a7753148b1699a

Seat r9c-rev-2026, round 1. Measured head e6e9b775dc775f71da7dd65fb061723912afda32. It was still the live head at posting time. The code is identical to dca94a64: e6e9b775 adds only main's merge and the delivery rows. Evidence: /Users/timmalmstrom/hpo-seats/r9c-rev-2026-ev

## Blocking

1. **Timing proof fails. The finder's harness is the nightly mutation drive.**
   - Dispatched run 37642546223, `mutation-nightly` job 112864826007, at dca94a64 (the fixed code):
     `baseline tests/boost_drift_replay.py: rc=124 failed=0 1576s`, then `MUTATION TABLE INCONCLUSIVE`
     ("timed out after 1576s"). The same job ran `features.py` in 671 s, against 750 s in the failing nightly 37595831734. So the runner was not slower than the one the fix targets.
   - The PR's own `fast (3.14)`, job 112889727516 at e6e9b775, ran the replay alone (`MODE: SCOPED -- 1 script(s) run`) and printed `ok ... (1534s)`. That is 42 s under the limit, against a predicted ~1050 s.
   - The `closures` recordings of the replay at the fixed code took 1478 s (job 112864782144, 15:29:18 to 15:53:56) and 1635 s (job 112889923161, 16:09:59 to 16:37:14).
   - Read together: on the slow runner class the forked replay costs about 1500 to 1600+ s, against about 1700 s before. That is a cut of about 10 %, not the predicted 38 %. The prediction rests on solve count times a uniform per-solve cost taken from one profiled day. The measurement says that assumption is wrong: the post-fork cycles cost more per solve, or the overhead is somewhere else. The nightly will keep timing out.

2. **Closures: this PR adds an `inert_reads` gap that main's full run will catch** (red-check trigger; the body attributes it wrongly). The dispatched run's `closures` job 112864782144 failed with `INERT READS UNDER-APPROXIMATED` naming
   `tests/harness_headers.py: tools/audit/harnesses/boost_replay_fork_parity.py` and `tests/harness_headers.py: tools/audit/harnesses/ci_script_seconds.py`, which are this PR's two new files, as well as `eg_b7_seam_hubs.py`, which #2022 has since fixed.
   At e6e9b775, `tests/closures.json` `inert_reads["tests/harness_headers.py"]` lists neither new file (checked directly).
   The PR's own `closures` (job 112889923161) is green only because the scoped run records just the replay. A push to `main` forces `full`, so main goes red after the merge: the same class #2022 fixed an hour earlier.
   The body says "This diff changes no closure input" and blames any closures red on #2022. That claim is false. `ci-autofix.md` lists INERT READS as `skip-manual-repair-owed`, so no bot repairs it. The repair: merge the CI recordings artifact (`closure.py merge --in-dir <dir> --partial`, #1886), or re-key after #2015 moves the directory.

## Verified (not blocking)

- **Equivalence (my own harness, not the fixer's).** `fork_equiv.py` runs the merge-base script's per-arm `run` (a fresh coordinator per arm) against the head's `replay` (shared prefix plus deepcopy). It compares every input that `check_arm` and `check_record` read: daily, daily_bias, folds_frozen/outside/after, hh_final, alarmed, and the full tagged/untagged sample `as_dict()` lists.
  - `stub` mode: the real 9-day schedule with the real fork at 254. `optimize` is replaced by a cheap controller that reads the live learned model. All five arms are EQUAL, including both two-zone follow-ups (stub.log).
  - Null control, head forked at 255: channel, mode and two-zone-boost read DIFFERENT, and the null arms read EQUAL (stub-control.log).
  - `real` mode: production solves, a 12-cycle schedule with a 7-cycle prefix that contains the 03:00 heartbeat. All three arms EQUAL (real.log).
  - Hidden state I checked: `boost._STATES`, `boost._PLAN_BASES` and `pump_arbiter._STATES` are WeakKeyDictionaries keyed on the coordinator, so the deepcopy drops them. This is safe because before the first boost `BoostState` is default and `_PLAN_BASES` is rewritten by `adopt_plan` before `apply` reads it every cycle. Production code has no RNG. The clock is re-frozen at the start of every cycle.
- **No pre-fork divergence at the base.** At the merge base, the solve inputs (time, state and learned params fingerprints) of channel_boost and mode_boost equal null_no_boost for cycles 0..254 and first differ at 255 (channel) and 256 (mode). So the arms do not diverge before cycle 254, and the fork hollows nothing.
- **Fork guard.** `check_fork` fails when `fork_cycle` is +1, -1 or 0, and when the schedule moves under a hard-coded 254 (BOOST_STARTS 6.5, BOOST_DAYS (4,6)). It passes when fork_cycle tracks the schedule (fork_guard_mutants.log).
  - Scope note: the guard is arithmetic. A planted surface action at cycle 100, outside `boosting_at`, leaves `check_fork` passing, while shared and unshared differ (guard_gap.log). The check's label ("no surface acts earlier") claims more than it tests. Not blocking at this head, because the cycle code does not act early, but a future edit would be erased silently.
- **Root-cause section.** It gives the cause, state (d), and a cheaper detector: compare `fast` seconds with 3x `recorded.seconds` on a main push, under 1 s. The body records that the detector is not built here and why ("gate policy ... a separate root-cause.md seat"). That is acceptable. Note, though, that the detector would not have fired on #1935's own PR, because `fast` ran the replay with no comparison.
- **Classification.** Both new harness files are under INERT `tools/audit/`. `entities.py` reports `ALL 2198 ENTITY CHECKS PASSED` (seat venv). `structure.py` reports `STRUCTURE RATCHET PASSED`. This PR must rebase after #2015 (RO-8) moves the directory to dev/audit/harnesses, which also re-keys the inert_reads repair above.
- VERSION, the manifest and the notes heading are untouched. No claim or golden file is touched. `git merge-tree --write-tree origin/main HEAD` exits 0.
- Head reds: `delivery-status` and `nightly-status` are main's, as the body says. `budget-raise-gate` was cancelled and its twin succeeded.

## RESULT lines

RESULT ci mutation-nightly 112864826007 @dca94a64 boost_drift_replay rc=124 1576s (limit 1576) TIMEOUT
RESULT ci fast(3.14) 112889727516 @e6e9b775 boost_drift_replay ok 1534s
RESULT ci closures 112864782144 @dca94a64 INERT READS UNDER-APPROXIMATED: harness_headers.py -> boost_replay_fork_parity.py, ci_script_seconds.py (this PR)
RESULT equiv stub full-schedule fork=254: 5/5 arms EQUAL; control fork=255: DIFFERS
RESULT equiv real 12-cycle fork=7: 3/3 arms EQUAL
RESULT base divergence: channel first differs at solve 255, mode at 256 (identical 0..254)
RESULT check_fork mutants: +1/-1/0/moved-schedule FAIL; tracking schedule PASS; planted pre-fork action PASS (guard scope gap)
