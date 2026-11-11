Triage batch 198 rules P622 (queue line 302: the two remaining reds in main's governance / instrument-self-tests at ee64358be7), 2026-11-11. It holds one ruling.

- **P622, ACCEPT: folded into R10-HOTFIX-PUSHER-CENSUS as items 3 and 4.** No new group is created.
  - `sweep_render.py --self-test` still refuses the unused `plan_coordinator_cap` at `0a2139b1dd`, measured locally. #3425 (commit `c6c04f21b5`) declared the placeholder and never used it in the sweep body. The fix is about 2 lines: an `OPTIONAL_FLAGS` entry, and the placeholder in step (4b).
  - The drift check's 19 refusals break down as follows:
    - 6 are UNMEASURED steps, skipped after the sweep-template failure.
    - 1 is a `<unknown>` probe left by the crash.
    - 6 are already added by #3446 (R10-HOTFIX-SELFTEST-SCOPE-UNION part 1).
    - 4 are `remerge_main_selftest.py` reads that #3425 introduced.
    - 2 are run-to-run variance reads.
  - Item 4 adds the last 6 to the table by union only. Null control: 8 refusals at `cbd23f1c8b`, before #3425.

The diff is one file against the merge base: `dev/programme/triage/s6-batch198.md`, the ruling. No product behaviour changes.

## Head

`937825bfd5bfa196056d9eca88996edaaef7eb7e`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P622 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the P622 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P623 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 0a2139b1dd...937825bfd5bfa196056d9eca88996edaaef7eb7e`: 1 file, 96 insertions, 1 commit. `tests/layout.py --guard`: 0 refusals.
- The figures come from job logs 130489627879, 130415622883, 130402966157, 130398921357 and 130394909969; from `sweep_render.py --self-test` run at `0a2139b1dd`; and from #3446's diff at `4cc5d8b962`.

## Red checks

none

## Forward-carry

none

## Friction

none
