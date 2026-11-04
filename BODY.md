Triage batch 124 records one ruling, P389: REJECT, already delivered by P296's supersede marker, which worked on #3185.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`15e5ebacee11809acb17728f1dc36326989d1566`; the one file is the whole diff against `783d8dc72811ab75ae4ffca367456f44896f47d3`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`. `ruling_verdict` reads P389 `REJECT`, and a carry citing it is refused as not an ACCEPT ruling.

## Null control

P390 reads `None`. With the file absent, a carry citing it is refused as not on the roster branch or origin/main.

## Figures

- `git diff --stat 783d8dc72811ab75ae4ffca367456f44896f47d3...15e5ebacee11809acb17728f1dc36326989d1566`: 1 file changed, 13 insertions(+).
- No capped file is touched.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
