Triage batch 126 rules on the existing set under the owner's 5 % and 10 % rule: P391 on the non-production CI lanes and P392 on the triage seat itself.

- **P391: DEFER.** Twelve lanes fail the bar at the upper bound, together 25 % of sampled runner hours. Each is a proposal for the owner through the orchestrator; nothing is removed. Required safety lanes and production tests are listed separately and not ruled.
- **P392: DEFER.** The seat costs 7 to 12 % of local tokens and has no measured benefit, so it does not pass on the working reading. The seat is ruling on itself, and the entry says so.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`c1dd4a51c0aa9aaf39b0ca4556aa11e487f05824`; the one file is the whole diff against `dad3178d6c81cfe2bb410e7045de28f686a6f845`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`. `ruling_verdict` reads P391 and P392 `DEFER`, and a carry citing either is refused as not an ACCEPT ruling.

## Null control

P393 reads `None`. With the file absent, a carry citing it is refused as not on the roster branch or origin/main.

## Figures

- `git diff --stat dad3178d6c81cfe2bb410e7045de28f686a6f845...c1dd4a51c0aa9aaf39b0ca4556aa11e487f05824`: 1 file changed, 95 insertions(+).
- The ruling's figures are cited with their sources and limits at the top of the file.
- No capped file is touched.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
