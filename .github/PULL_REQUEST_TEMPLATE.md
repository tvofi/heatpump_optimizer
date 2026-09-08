<!--
The headings below are the ones `pr-contract` requires. Each is content or an
explicit `n/a: <reason>`; a heading with nothing under it is refused, because
silence and "nothing to report" are not the same claim.

Run `tools/audit/prepr.sh <this body>` before opening. The job re-executes what
it can, so the PRE-PR line is a claim and the re-execution is the proof.
-->

Why this change, and what it measures.

## Head

The SHA you measured everything below at. CI compares it with the head it ran.

## Mutation proof

Break the fix and paste the checks that go red. A proof that does not name a
failing check proves nothing.

## Null control

What the unmodified tree does. Every cost, gain or timing claim needs one.

## Red checks

`none`, or each failing check by name, with the answer the root-cause rule
requires: the cheaper detector and its standing cost, or the finding that none
exists.

## Forward-carry

`none`, or the path of the brief, contract or roster this finding lands in.
A pull-request comment is not propagation.

## Friction

`none`, or one line per event: `<rule_id>: <unclear|contradiction|unenforced|stale|cost>: <evidence>`.
