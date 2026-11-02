Triage batch 112 records one ruling, P370, from the orchestrator s10's queue line of 2026-11-02T03:29:40Z. The proposal: the opener maps a topic to its group by uppercasing it, so a split-part topic (`-p<N>`) never matches and the opener refuses with NEEDS-TITLE/GROUP; strip the suffix before the roster lookup. It is the rolling batch after batch 111.

- **P370: DEFER, because the item is already owned.** It re-files P363 (`s6-batch106.md#P363`, ACCEPT), whose rule is R10-OPENER-REUSE carry 10 on roster `5dc16bbe1`. No new carry and no group.
  - **The new instance.** `driver4.log` at 03:24Z logged NEEDS-TITLE for `r10-deps-actions-bump-p1`, opened by hand with group R10-DEPS-ACTIONS-BUMP. Its handoff changes one file, none under `custom_components/`.
  - **Carry 10 already holds this remedy**, with the exact-match-first guard P363 found it needs (R10-ROSTER-OPS-2 and others already end in such a suffix).
  - **What this adds is a count.** This is the fourth part topic to miss since 2026-10-31; the log has 8 NEEDS-TITLE against 88 RESULT lines. Delivery waits on R10-OPENER-REUSE's dispatch (stage `not-started`), which is the orchestrator's call.
  - **What would change it.** The group closing without building the rule, or the built rule still missing a part topic.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. No roster op is queued.

## Head

`a8082eec98a46c0c9ee1471300c186bf0a998506`; the file is the whole diff against `8247a1ed1`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P370 as `DEFER`, and a text citing `s6-batch112.md#P370` is refused: `is not an ACCEPT ruling (DEFER)`.
- With the verdict flipped to ACCEPT, it reads `ACCEPT` and the refusal is `None`.
- P371 reads `None`: no such entry.

## Null control

- With the file absent, the citing text is refused: `the triage ruling dev/programme/triage/s6-batch112.md is not on the roster branch or origin/main`.

## Figures

- Roster `5dc16bbe1`: R10-OPENER-REUSE holds 10 carries; carry 10 opens "From triage P363"; its resume stage is `not-started`.
- `grep -c NEEDS-TITLE driver4.log`: 8; `grep -c RESULT driver4.log`: 88.
- `git diff --name-only $(git merge-base origin/main 99835eadc) 99835eadc`: 1 file, `dev/audit/rounds/round6/D11/fix/codeowners_gap.py`.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
