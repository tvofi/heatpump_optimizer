<!-- The headings below are what `pr-contract` requires: each is content or an
explicit `n/a: <reason>`, since silence and "nothing to report" differ. Run
`tools/audit/prepr.sh <this body>` before opening; the job re-checks what it can. -->

Why this change, and what it measures.

## Head

The SHA you measured everything below at.

## Mutation proof

Break the fix and paste the checks that go red. Naming none proves nothing.

## Null control

What the unmodified tree does.

## Figures

`none`, or one line per figure the body states, with the command that printed it;
name the instrument rather than restate what it prints. `pr-contract` refuses a
command that does not resolve, and never re-runs one.

The required check `arch-score` scores the change (`python3 tools/audit/archscore/score.py --diff
origin/main`). A gate metric that rises passes only when a `## Architecture score` section below has
one line per risen metric, naming it and saying why, as a budget raise is argued; delete the section
when nothing rises. The score is a review trigger, never a target.

## Red checks

`none`, or each failing check by name, with the answer the root-cause rule
requires: the cheaper detector and its standing cost, or the finding that none
exists.

## Forward-carry

`none`, or the path of the brief, contract or roster this finding lands in.

## Friction

`none`, or one line per event: `<rule_id>: <unclear|contradiction|unenforced|stale|cost>: <evidence>`.
