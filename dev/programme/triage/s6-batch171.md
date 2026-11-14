# Proposal triage, session s14, batch 171 (P587)

This batch re-rules queue line 266, which batch 170 rejected as P586, after the orchestrator gave
the replay condition P586 missed. P587 supersedes P586.

Sources:
- origin/main `a7628041dc`. Every line number below is at that commit.
- PR 3425's body as the fold read it, byte-identical to the body P586 replayed (`cmp`).
- The round roster at `e60ea43333`, the tip before the fold's write `f63227bd43`.

## P587: CARRY-SOURCE-BARE-NUMBER

Verdict: ACCEPT, as a carry on R10-CARRY-AUDIT-P5 (stage not-started, severity medium, size S;
it owns `tools/audit/carry_audit.py`). This supersedes P586's REJECT.

Source: the proposal queue, s14-12, 2026-11-11 (line 266: "carry_fold.py --pr 3425 (no #)
reports 0 missing while carry_audit landed --pr '#3425' reports 1 ... PR 3425"). The orchestrator
corrected the measurement on 2026-11-11.

Instances:
- **Why P586 missed it.** P586 replayed with `--roster-ref <one ref>` against the roster from
  before an earlier carry, `d611071d86^`. That flag reads only the named ref. The fold reads
  main plus the round roster, and the round roster was at `e60ea43333`.
- **The replay that reproduces it.** A shared clone (`git clone --shared --no-checkout`) has
  `origin/main` at `a7628041dc` and `origin/handoff/audit-r10-roster` at `e60ea43333`. Running
  `carry_audit.py --git-dir <clone> landed --body <body>` gives:
  - with `--pr '#3425'`: `CARRY-MISSING R10-TICK-RESIDUE body item 09380b99 ... CARRY-LANDED:
    1 missing`;
  - with `--pr 3425`: `CARRY-LANDED: 0 missing`.
  This matches the orchestrator's 07:11Z runs. The `#3425` fold folded 1 and wrote `f63227bd43`.
- **The mechanism.** `landed` (`carry_audit.py:620`) treats an item as landed when any source
  token is a whole token of its group's text (line 650, split on `[^\w#-]+`).
  - R10-TICK-RESIDUE's carries at `e60ea43333` contain the prose "handed off as PR 3425" four
    times, and `#3425` zero times (`jq` over the group, `grep -c '#3425'` = 0).
  - So a bare `3425` matches that prose, and the item reads as landed by its source although no
    carry holds it.
  - `own_group` and `pr_group_of` are not involved: both spellings resolve to `None` in the
    clone.
  - Had the bare number not matched prose, both spellings would have printed 1 missing.
- **Consequence.** A fold run with a bare number reports success and writes nothing, so a
  missing carry stays missing. A run with the documented spelling `#N` (`carry_fold.py:4`,
  `carry_audit.py:965`, `bus.sh:237`) is correct.

Cost:
- About 5 lines in `carry_audit.py`: one normaliser, used by both `landed` and `land_ops`, that
  maps an all-digit `--pr` value to `#<N>`. `carry_fold.py` calls both functions, so it needs no
  change.
- One self-test pair.
- No new file, and no capped file is new. The group's severity is medium, so the machinery bar
  does not apply.

Binding: a fold that silently writes nothing leaves a carry missing while every reader sees
success. The fix is a few lines in a group not yet started that already owns the file.

Rule per instance:
- **Normalise the source.** In `carry_audit.py`, an all-digit PR source becomes `#<N>` before
  `landed` splits sources, and before `land_ops` writes `From <pr>`. Any other spelling, such as
  `PR3425`, is refused with rc 2, naming `#<N>`.
- **Run against the instance:** with the normaliser, `--pr 3425` reads as `#3425` and gives
  `CARRY-LANDED: 1 missing` at `e60ea43333`, the same as the `#3425` run. The fold writes the
  carry once.
- **Self-test.** A group whose text says "PR 3425" but holds no `#3425` carry:
  - `--pr 3425` and `--pr '#3425'` both report the item missing.
  - Null control: a group holding a "From #3425" carry reports 0 missing for both spellings.
  - A mutant that drops the normaliser makes the bare arm report 0.
