prepr's step 7 (`body_line`) and step 7c (`reds_line`) reported a refused body check by its count line alone unless the refusal was an unnamed red, and step 7 appended its budget verdict to that line. Three unrelated pull requests, #2545, #2558 and #2582, were refused within about an hour with `PR-BODY: N error(s) in .../BODY.md -- no budget leaf raised over 5a755f53e...<head>`. That read as a budget refusal. The real ground in all three was a `## Friction` line written as prose, not in the template's `<rule_id>: <class>: <evidence>` form; the budget arm had passed. This change prints the ground.

One helper, `body_refusal`, used by both callers, prints the red gate's own sentence when a red went unnamed (unchanged), else the first `ERROR` line `policy_lint.mjs --pr-body` printed, else the count line, followed by the count of error lines.

## Head

`400e15d277c7fb7c9e27aa1c203de282e0c51c4f` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2591.md`. The authored code head is `c3d66bca3f161d15b7df440c01ff982a58902e5e`.

`47e03696d9230aa21e13823b554860a28ae84b4b` merges origin/main `302f66571` into the authored code head `c3d66bca3f161d15b7df440c01ff982a58902e5e` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`c3d66bca3f161d15b7df440c01ff982a58902e5e`, the tip of `handoff/r10-fly-budget-leaf`, cut from origin/main `5a755f53efda` (#2529). Everything below was measured at that head.

## Mutation proof

The fix reverted is the mutant: `body_refusal` replaced by the old `grep -m1 'does not name it' || tail -1` (the tree at the first commit's parent plus the two new self-test rows). `bash tools/pr/prepr.sh --self-test` then fails exactly the two new rows: `and the refusal prints the error, not only its count` (7c) and `and the refusal prints the error ahead of the budget verdict` (7). With the fix, both rows pass and no other row changes.

Replay on #2582's refused body at its update head `b237d6688`, the functions sourced from each tree: origin/main's prints `PR-BODY: 1 error(s) in .../BODY.md -- no budget leaf raised over 5a755f53e...b237d6688`, byte-identical to the logged refusal; this head's prints the `## Friction` line does not parse error, then the same budget verdict.

## Null control

The answered fixtures stay green: `red-answered.md` through 7c and `unnamed-red.md` over the `docs` branch through step 7 pass before and after, and they are the bodies the plants are derived from by one line. #2582's body with its Friction line set to `none` passes the replay at `b237d6688` (`PR-BODY: 0 error(s)`, rc 0), so the refusal was that line and nothing else.

## Figures

none

## Red checks

none

## Root cause

Trigger: a recurrence, three prepr refusals of the same printed shape on #2545, #2558 and #2582, and no check went red on this branch. Cause: `grep -m1 'does not name it' || tail -1` in `body_line` and `reds_line`, from R9-FR-12 (05ae6d239, 2026-10-06); it was written for the red-check refusal only and its fallback is the count line. The trigger is old: `no budget leaf raised` has been appended to every step-7 line since 05ae6d239, and the PR template's Friction format has not changed since 2026-10-18. Process state (c): step 7 ran and refused each body correctly, before the push, at the cheapest point; its report did not produce the intended result, an author who can act on the line. Not (b): no instruction was disobeyed by the instrument. Not (a): the check existed. Not (d): nothing under it changed. The bodies' own defect (prose Friction) was caught where it should be; no cheaper detector is owed for it. Cost test: the countermeasure's standing cost is two greps on a refused body and two self-test rows; the defect cost each refusal a hand re-derivation of the error, and here a root-cause seat. Built.

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)

