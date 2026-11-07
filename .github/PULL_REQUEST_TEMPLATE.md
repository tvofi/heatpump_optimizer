<!-- The headings below are what `pr-contract` requires: each is content or an
explicit `n/a: <reason>`. Run
`tools/pr/prepr.sh <this body>` before opening. -->

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
command that does not resolve, and never re-runs one. Required check `arch-score`:
a gate rise passes only explained under `## Architecture score`, one line per metric.

A figure a registered instrument prints (tools/pr/figure_registry.json: scope-line, structure-ratchet, merge-base) is a generated block, never typed: write the empty marker `<!-- figure-block: scope-line -->` then `<!-- /figure-block -->` on the next line and seat/body_push.sh or prepr.sh --body-check fills it at the head; pr-contract re-renders and refuses a block that differs. Only registered figures are structurally non-stale.

## Red checks

`none`, or each failing check and each open `code-scanning alert <n> (<rule id>)`
that `pr-contract` lists, by name, with the answer the root-cause rule requires:
the cheaper detector and its standing cost, or the finding that none exists.

## Forward-carry

`none`, or per finding the path it lands in and `Carry: <dest>`.

## Friction

`none`, or one line per event: `<rule_id>: <unclear|contradiction|unenforced|stale|cost>: <evidence> Carry: <dest>`.
