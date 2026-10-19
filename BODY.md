Roster for round 10: lands the roster branch's current groups and forward-carries so that open pull requests' carries resolve against the tree's roster (finding-propagation.md). Without it #2404's and #2406's carries read BAD-DEST until the roster is on main. Part of #201.

## Head

`669074c242d9160eaa4b002a94b2f3238d1373ca` merges `origin/main` `06c6f3cf2` into a merge of the roster branch tip `73bb15fe8f5bf05ec3568927118a8d678dd8b99` (`handoff/audit-r10-roster`) into the previous PR head `c83ae12ac`. No conflict arose in either merge. The change versus main is `dev/programme/rosters/wave-r10-groups.json` and this PR's own row `dev/programme/delivery/2417.md`.

New groups (9): R10-SAV-COMFORT, R10-MUTATION-ANCHOR, R10-N-LOG-FLOOD, R10-POLICY-LINT-FAMILY, R10-DEAD-RATE-LIMIT, R10-MERGE-SUBJECT-HARDEN, R10-CI-LAYOUT, R10-OPENPR-SILENT, R10-STAMP.

Carries added to existing groups: R10-ADVISOR (2, from #2411), R10-SCORES (1, from #2411), R10-ARCHSCORE-COVERAGE (1, from #2415, plus its brief), R10-TICK-DRIVERS (2, from #2406, plus its resume), R10-BRIEFS-FOLD (2, from #2399 and the RCA harness-friction branch).

Carries added to new groups: R10-SAV-COMFORT 1, R10-MUTATION-ANCHOR 1, R10-POLICY-LINT-FAMILY 3, R10-DEAD-RATE-LIMIT 2, R10-MERGE-SUBJECT-HARDEN 2, R10-CI-LAYOUT 3, R10-OPENPR-SILENT 1, R10-STAMP 2 (the 19 may-drift restores and the #2406 beat restart).

This PR leaves #201 open and closes nothing by keyword.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

n/a: no measured claim. The group and carry lists above are enumerations of a JSON diff between `origin/main` and the head, not measurements of behaviour.

## Figures

none

## Red checks

none: the only non-success check-run on the previous head `c83ae12ac` is CodeQL, which concluded `neutral`; no check concluded failure.

## Forward-carry

dev/programme/rosters/wave-r10-groups.json (the groups and carries listed under Head)

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
