## Head
Measured at code head 554d06a9089e14d83566b63e61108636e8ea8798 (repair round 2 of the code head 607b97bfcaebd21c6cd97ebc9c25c41c2852bc25; the pull request head 241f47e62d1e22e78e48e1e4406da613751cf3dc added only the delivery row dev/programme/delivery/3181.md), base c3a279e3252a8b57bb00b5a677318cd4fe20387f (origin/main unmoved, no merge-tree conflict). `tools/pr/prepr.sh` ran at this head with PREPR_SKIP_CLOSURES=1, rc=0. **Partial delivery: carries 1 and 2 are done; carry 0 is NOT built** (see Forward-carry). Carry: dismissed: statement of scope, not a finding

Roster numbering (1-based, as the review packet counts): Carry 1 = brief carry 0 (ci.yml/prelude.py, NOT built); Carry 2 = brief carry 1 (run.sh, done); Carry 3 = brief carry 2 (closure.py `--cached`, done). Carry: dismissed: numbering note, not a finding

## Mutation proof
Carry 2: restoring `"--cached"` to `_RENAME_EXEMPT` in tests/closure.py and running `python3 tests/closure.py selftest` fails exactly one pin, "the census refuses a planted --cached name-only diff that builds a list, not its --no-renames twin" (1 of 118 closure shrink pins FAILED); restored.
Carry 1: the pin in tests/entities.py drives `SUMMARY_LINE`/`ended_before_summary` lifted from run.sh on a crash log (must be named) and a failed-check log (must not be). Repair round 2 mutation proof: with `-e` reverted from the site the full `python3 tests/entities.py` prints `1 of 2603 ENTITY CHECKS FAILED`, the errexit check red naming `tests/entities.py:_gl_ended_before_summary`; with `-e` restored it prints `ALL 2603 ENTITY CHECKS PASSED`. The pin's own crash/failed-check two-sidedness is unchanged.

## Null control
Carry 2: the six restore-count lines now carry `--no-renames` and the same selftest reports no refusal and an empty stale-RENAME_ALLOW check (`no stale RENAME_ALLOW entry` ok). A planted `git diff --cached --no-renames --name-only | wc -l` is not refused.
Carry 1: the failed-check log ("2 of 9 ENTITY CHECKS FAILED") is not named as ended-before-summary.

## Figures
- Selftest: `python3 tests/closure.py selftest | grep -E "rename|cached"` all ok at this head.
- tests/entities.py new check "run.sh names a script ended before its summary apart from a failed check" printed ok; the full entities.py run at this head completed: ALL 2603 ENTITY CHECKS PASSED.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `tools/pr/prepr.sh`: rc=0 (closures step skipped: MODE FULL, CI re-records).
- Toolchain: numpy 2.5.4, scipy 1.18.1 match tests/requirements-ci.txt after `cloud-setup.sh`; no golden was run, CI is the authority.
- Carry 1 detection is lane mode only (GATE_JOBS>1, the default): serial runs stream and keep no log. Carry: dismissed: documented limit, host-independent in lane mode. Its summary pattern is design choice: a non-zero script whose log has none of PASSED|FAILED|UNCHANGED|ALL EDGE CASES PASS|n FAILURES|REFUSE|closure: committed closures is named `>>> ENDED BEFORE ITS SUMMARY: <script> (exit rc; last line reached: ...)`.

## Red checks
Read from the check-run set at 241f47e62d1e22e78e48e1e4406da613751cf3dc (run 126438241409). Concluded reds:
- `tests / fast (3.14)`: 1 of 2603 entity checks failed, "every `bash -c` / `sh -c` a check runs carries errexit, as GitHub's step shell does, unless it runs no workflow step (countermeasure B)", naming this branch's new site `tests/entities.py:_gl_ended_before_summary`. Cause: the new pin drove its lifted run.sh function under a bare `bash -c`, not the step shell's `bash -e -c`. Repair: the site now runs `["bash", "-e", "-c", ...]` (the check's own `_GHA_RUN` shape); the function's non-zero return is its last command, and the rc still reads [0, 1] for crash and failed-check. The site is not on the check's exempt list. The other FAIL lines in that log are self-test fixtures.
  Root cause (trigger: a PR red on a check a cheaper detector could have run): the earlier run printed no red because `tools/pr/prepr.sh` never selects `tests/entities.py` (it ran the self-tests and predicts, rc=0) and the earlier local entities run was cut short by a pipe, so the failing check was never reached. Cheaper detector: running `python3 tests/entities.py` to completion under PYTHONPATH=tests/hastub, which is the step fixer.md step 9 asks for and costs about 7 minutes. Process state: the step was skipped, not unavailable. Countermeasure: none built. The check already exists and the standing cost of the detector is that one run; the gap was my skipping it, not a missing instrument.
- `tests / nightly-status` (failure): inherited from main, grades main, not caused by this branch. Its log reads `NIGHTLY FAILED: slow failed 1 night ago` for scheduled run 41555367389 (head b8e8236), which predates this branch; the diff touches no nightly lane. Not a required context on `main-protect`. Nothing to repair here.
The earlier body's claim that the branch's own local run printed no red was wrong: that run had not selected entities.py to completion. What ran at this head: the full `python3 tests/entities.py`, ALL 2603 ENTITY CHECKS PASSED, and `tools/pr/prepr.sh` rc=0.

## Forward-carry
Carry 0 (edit run exits without holding a runner; code run's gate re-dispatches body units) is not delivered. Mapping done: the only caller is `tools/ci/prelude.py` `outputs()` → `wait_sources` (poll 60 s, bound 8700 s); ci.yml has no workflow_dispatch step, so a re-dispatch needs a new step in `gate` (which is read-only today, `actions: write` is held only by `cancel-superseded` and `refresh`). This changes permissions on a code-owned path and cannot be exercised locally, so I stopped rather than push an untested workflow change; it needs a design/owner call and its own fixer. Destination: re-queue carry 0 to the next fixer for this topic. Carry: dismissed: carry 0 stays in the owner's plan-regain card 9 brief for this topic (r10-ci-runner-fixes), unchanged

## Friction
none
