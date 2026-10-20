Roster for round 10, fourth landing: brings main's `dev/programme/rosters/wave-r10-groups.json` up to the roster branch tip, so that open pull requests' carries resolve against the tree's roster (finding-propagation.md). #2469 (R10-UPDATE-PR-LOCK) routes three `Carry:` lines to R10-UPDATE-PR-SIGNALS, which `carry_audit` reads as bad destinations until that group is on main. Part of #201.

## Head

The authored code head is `7e8e5e5ab97479a1d63fde668c6011334be492db` (`handoff/audit-r10-roster`). `git diff --name-only origin/main...7e8e5e5a` lists exactly one file, `dev/programme/rosters/wave-r10-groups.json`; the PR head adds only this PR's own delivery row.

The diff, enumerated from the JSON at `origin/main` and at `7e8e5e5a` (groups 90 to 91, stage `done` 43 to 43, carries 198 to 201):

- New group (1): R10-UPDATE-PR-SIGNALS, wave 2, stage `queued`, 1 carry. It holds the signal-safety work split from #2469 at round 4 under the three-round rule: the SIGKILL drain, whole-group signals, and the 75-under-`set -e` reading. No group is removed.
- Carries appended to existing groups (2): R10-CI-LAYOUT 13 to 14 (from #2464 round 3: later lane edits keep `tests/harness_headers.py` in the alone phase), and R10-ROSTER-OPS 2 to 3 (from #2469 round 3: the `ps` dependency of the leader check and the holder).
- No stage changes, and no brief or owner-gate text edits on existing groups.

This PR leaves #201 open and closes nothing by keyword.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

n/a: no measured claim. The lists above enumerate a JSON diff between `origin/main` and the head.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
