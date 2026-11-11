Triage batch 197 rules P621 (queue line 299, the governance / instrument-self-tests red at #3461), 2026-11-11. It holds one ruling.

- **P621, ACCEPT: new hotfix group R10-HOTFIX-PUSHER-CENSUS** (S, lane C, severity high). The red is main's, not #3461's diff, and not strace.
  - The strace `FAIL wrapper:`/`FAIL record:` lines are the `selftest_scope_mutants.sh` step's expected mutant refusals; that step ends `every mutant refused` and passed.
  - The failing check is pr_args's pusher census: `tools/audit/seat/remerge_main_selftest.py` (from #3425) names `app_push.sh` and has no `PR_PUSHERS` entry. The census is rc 1 at main `ee64358be7` and `0a2139b1dd`, rc 0 at #3461's head; main's own job 130489627879 fails the same check.
  - The fix is one `PR_PUSHERS` entry; a red-check root cause is owed for #3425.

The diff is one file against the merge base: `dev/programme/triage/s6-batch197.md`, the ruling. No product behaviour changes.

## Head

`4920f2e24e4c2454c862c864b908e61a99871559`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P621 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the P621 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P622 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 0a2139b1dd...4920f2e24e4c2454c862c864b908e61a99871559`: 1 file, 69 insertions, 1 commit. `tests/layout.py --guard`: 0 refusals.
- The figures come from job logs 130494859555 and 130489627879 and from `pr_pushers` run at `ee64358be7`, `0a2139b1dd` and `e277df592e`.

## Red checks

none

## Forward-carry

none

## Friction

none
