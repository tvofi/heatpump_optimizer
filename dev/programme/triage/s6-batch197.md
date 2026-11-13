# Proposal triage, session s14, batch 197 (P621)

Sources:
- origin/main `ee64358be7` and `0a2139b1dd`. Line numbers are at `ee64358be7`.
- #3461 head `e277df592e`, its `governance / instrument-self-tests` log, job 130494859555 (the
  orchestrator's copy under the s14 body-3461 logs).
- Main's own run of the same job at `ee64358be7`: job 130489627879, read once. The check-run at
  `0a2139b1dd` (130543139624) was still in progress when read.

## P621: HOTFIX-PUSHER-CENSUS

Verdict: ACCEPT, as a new hotfix group R10-HOTFIX-PUSHER-CENSUS (S, lane C, severity high, sonnet
fixer, opus reviewer). The red is main's, not #3461's, and the strace reading was wrong. A red on
main takes the hotfix route, not the proposal bar.

Source: triage queue line 299, 2026-11-11T13:13:25Z, orchestrator s14: QUALITY GAP, measure first.
`governance / instrument-self-tests` is red at #3461 on strace-trace `FAIL wrapper:` and
`FAIL record:` lines; a seat guessed the runner lacks strace.

Instances:
- **The strace lines are not the failure.** In job 130494859555 they come from the
  `selftest_scope_mutants.sh --self-test` step. That step prints each mutant's refusals and ends
  `SELFTEST-SCOPE MUTANTS: every mutant refused`, which its own `grep -Eq` requires; it raised no
  error. The unmutated arms in the same log read `ok` for the same checks, including "wrapper: a
  gated step runs under strace -q into step-ID.trace (null control)". So the runner has strace.
- **The failure.** The job's three `##[error]` exits each follow `pr_args self-test: 199 checks, 1
  failed`, and the failing check is `FAIL the pusher census: the rule returns exactly the
  dispositioned paths, and every runner reaps` (`tools/audit/seat/pr_args.sh:829-833`).
- **The cause.** `pr_pushers` (`pr_args.sh:386`) greps `tools/` for `PR_PUSHER_RULE`
  (`:363`, any `push.sh` or `app_push.sh` name) and refuses any match not listed in `PR_PUSHERS`
  (`:364-385`). The census, run by revision with main's own `pr_args.sh`:

  | revision | rc | ok | OPEN | PR_PUSHERS entries |
  |---|---|---|---|---|
  | `ee64358be7` (main) | 1 | 22 | 1 | 22 |
  | `0a2139b1dd` (main) | 1 | 22 | 1 | 22 |
  | `e277df592e` (#3461 head, older base) | 0 | 22 | 0 | 22 |

  The OPEN line, at both main commits: `tools/audit/seat/remerge_main_selftest.py: undispositioned
  -- it names a pusher`. That file writes a fake `tools/pr/app_push.sh` into a scratch origin
  (`:7`, `:50`) and pushes nothing. It came in with `c966df8730` and `56307001fc` on
  fix/r10-tick-residue, merged by #3425 as `ee64358be7`.
- **Fleet-wide, not #3461's diff.** #3461's diff touches nothing under `tools/` (0 of 19 files), and
  the census passes at its head. CI judges the merge with main, which carries the undispositioned
  file. Main's own job at `ee64358be7` fails the same check three times (job 130489627879). Every
  pull request that merges current main inherits it.
- **Ownership.** No roster group at `handoff/audit-r10-roster` names the file, the census or this
  job's red.
- **Outside this ruling.** Main's job at `ee64358be7` has two further reds that #3461's run does not:
  `sweep_render.py` refusing ``unused: `plan_coordinator_cap` `` and `selftest_scope check: 111 gated
  step(s), 19 refusal(s)`. They are reported to the orchestrator, not ruled here.

Cost:
- One `PR_PUSHERS` entry in `tools/audit/seat/pr_args.sh`: `tools/audit/seat/remerge_main_selftest.py
  mention: a self-test; it writes a fake app_push.sh into a scratch origin and pushes nothing`. No
  new check, file or lane. One S sonnet fixer and an opus review.

Binding: a red on main in a gating job that every open pull request inherits. The fix is the
census's own documented remedy ("give it an entry in PR_PUSHERS"). The census rule is not loosened.

The fix:
1. **PUSHER-CENSUS-ENTRY.** Add the entry above. Demonstration: `pr_pushers` at the fix prints 23 `ok`
   lines and no OPEN line, rc 0, against 23 entries; the pusher-census check passes. Null control:
   with the entry removed the census prints the OPEN line and the check fails, as it does at
   `0a2139b1dd`.
2. **Root cause.** The red reached main through #3425. The defect-root-cause red-check trigger
   applies: the fixer names the check in the body and answers why #3425's gate did not run the
   pr_args self-test on a diff that added a `tools/` file naming `app_push.sh`. The root-cause seat
   is the orchestrator's to dispatch.
