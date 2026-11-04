## Head
Measured at code head 607b97bfcaebd21c6cd97ebc9c25c41c2852bc25 (the pull request head is 241f47e62d1e22e78e48e1e4406da613751cf3dc, which adds only the delivery row dev/programme/delivery/3181.md), base c3a279e3252a8b57bb00b5a677318cd4fe20387f (origin/main unmoved since the single `tools/pr/prepr.sh` run, rc=0, MODE: FULL, so no second run). **Partial delivery: carries 1 and 2 are done; carry 0 is NOT built** (see Forward-carry). Carry: dismissed: statement of scope, not a finding

Roster numbering (1-based, as the review packet counts): Carry 1 = brief carry 0 (ci.yml/prelude.py, NOT built); Carry 2 = brief carry 1 (run.sh, done); Carry 3 = brief carry 2 (closure.py `--cached`, done). Carry: dismissed: numbering note, not a finding

## Mutation proof
Carry 2: restoring `"--cached"` to `_RENAME_EXEMPT` in tests/closure.py and running `python3 tests/closure.py selftest` fails exactly one pin, "the census refuses a planted --cached name-only diff that builds a list, not its --no-renames twin" (1 of 118 closure shrink pins FAILED); restored.
Carry 1: the pin in tests/entities.py drives `SUMMARY_LINE`/`ended_before_summary` lifted from run.sh on a crash log (must be named) and a failed-check log (must not be). Not mutation-run separately; no mutation was executed for it. Carry: dismissed: the pin is by construction two-sided, CI mutation lane covers tests/

## Null control
Carry 2: the six restore-count lines now carry `--no-renames` and the same selftest reports no refusal and an empty stale-RENAME_ALLOW check (`no stale RENAME_ALLOW entry` ok). A planted `git diff --cached --no-renames --name-only | wc -l` is not refused.
Carry 1: the failed-check log ("2 of 9 ENTITY CHECKS FAILED") is not named as ended-before-summary.

## Figures
- Selftest: `python3 tests/closure.py selftest | grep -E "rename|cached"` all ok at this head.
- tests/entities.py new check "run.sh names a script ended before its summary apart from a failed check" printed ok; the full entities.py run was cut short by my pipe, so CI is the authority for the rest of that script.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `tools/pr/prepr.sh`: rc=0 (closures step skipped: MODE FULL, CI re-records).
- Toolchain: numpy 2.5.4, scipy 1.18.1 match tests/requirements-ci.txt after `cloud-setup.sh`; no golden was run, CI is the authority.
- Carry 1 detection is lane mode only (GATE_JOBS>1, the default): serial runs stream and keep no log. Carry: dismissed: documented limit, host-independent in lane mode. Its summary pattern is design choice: a non-zero script whose log has none of PASSED|FAILED|UNCHANGED|ALL EDGE CASES PASS|n FAILURES|REFUSE|closure: committed closures is named `>>> ENDED BEFORE ITS SUMMARY: <script> (exit rc; last line reached: ...)`.

## Red checks
Read from the whole check-run set at 241f47e62d1e22e78e48e1e4406da613751cf3dc (every page; some jobs were still in_progress at the read). The one concluded red check is:
- `tests / nightly-status` (failure): inherited from main, not caused by this branch. Its log reads `NIGHTLY FAILED: slow failed 1 night ago` for scheduled run 41555367389 (2026-11-03, head b8e8236), a run that predates this branch. It reports the last concluded nightly, and the diff touches no nightly lane. The check is not a required context on `main-protect`. Owner: main's inherited red, the nightly `slow` lane; main at c3a279e also carries a red `slow` check-run (126403921052). Nothing to repair on this branch.
The branch's own local run printed no red (`tools/pr/prepr.sh` rc=0).

## Forward-carry
Carry 0 (edit run exits without holding a runner; code run's gate re-dispatches body units) is not delivered. Mapping done: the only caller is `tools/ci/prelude.py` `outputs()` → `wait_sources` (poll 60 s, bound 8700 s); ci.yml has no workflow_dispatch step, so a re-dispatch needs a new step in `gate` (which is read-only today, `actions: write` is held only by `cancel-superseded` and `refresh`). This changes permissions on a code-owned path and cannot be exercised locally, so I stopped rather than push an untested workflow change; it needs a design/owner call and its own fixer. Destination: re-queue carry 0 to the next fixer for this topic. Carry: dismissed: carry 0 stays in the owner's plan-regain card 9 brief for this topic (r10-ci-runner-fixes), unchanged

## Friction
none
