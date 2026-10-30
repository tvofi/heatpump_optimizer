# 0016 — A major version is a closed audit round

Status: recorded 2026-10-29 from the repository owner's ruling of that day.
Lands as roster group R10-STAMP-ROUND-MAJOR, under the mandate in force with
scope all (#201 comment 6329234399), and merges before round 10's closeout
stamp.

## Context

`tools/release/stamp.py` took `--bump patch|minor|major` and nothing tied a
major to anything, so a version number said nothing about which audit round a
release has passed.

## Decision

The owner, verbatim (tvofi, 2026-10-29): *"I am also changing the versioning,
each full audit round means a new major version, and it should match the round
number on closeout, so the programme closeout release will be v10.0.0"*.

1. **The closeout stamp of audit round N is N.0.0**, whatever the current
   major: round 10's programme closeout is v10.0.0.
2. **Between closeouts a stamp is `--bump minor` or `--bump patch`**, as
   before; the next stamp, for the Marketplace work, is v7.1.0 by
   `--bump minor`.
3. **No other major exists.** A plain major bump is refused, so no stamp can
   reach a major without closing a round.

## How stamp.py enforces it

`stamp.py --round-close N` sets the version through `next_version`, which
refuses, before anything is fetched or written:

- an N not above the current major (a round closes once, upward);
- an N that is not the round of the newest roster, read through
  `roster_lib.roster_path` and `roster_round`, and a checkout with no roster;
- an N given beside `--bump`.

`--bump major` stays a parseable choice and refuses with a pointer to
`--round-close`; `bump()` itself has no major arm, so a caller cannot skip
`next_version`. Rule 3's tag checks then apply to N.0.0 as to any version.
`stamp.py --self-test` drives each refusal, and a null control over patch and
minor.

## Consequences

- Versions jump at a closeout (7.x to 10.0.0): the gap is the rule, not a
  missing release.
- Rule 4 of `CLAUDE.md` is unchanged: versions are still assigned after the
  merge, by `stamp.py`, and never in a branch.
- `dev/governance/` is `@tvofi`'s in `.github/CODEOWNERS`: this record merges
  on the owner's approving review, or under a mandate in force with scope all.
