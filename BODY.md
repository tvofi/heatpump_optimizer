Triage batch 114 records one ruling, P372, from the orchestrator s10's message of 2026-11-02, about 09:52Z, filed as a critical-path deadlock. The finding: `body_push.sh`'s hot-file guard refused #3065's own round-7 body, because #3065's own unboarded merge verdict shares its hot files. The proposal: exclude the pull request the topic maps to, with a self-test arm and a killed mutant. It is the rolling batch after batch 113.

- **P372: DEFER, because the item is already owned.** It re-files P368 (`s6-batch110.md#P368`, ACCEPT as a defect), whose carry b110-P368 is queued for R10-ORCH-REVIEW-PACKET. No new carry and no group.
  - **The defect is still on main.** At `279cb497f`, `handoff()` in `tools/audit/seat/review_packet.py` passes the literal `0` as `this_pr` (line 594). `hot_file_refusals` already has the self-exclusion (line 215), so it never fires at the handoff.
  - **The instances.** #3065 round 7 at 09:05Z is new; #3065 round 4 at 01:54Z is P368's own. #3085 (`fix/r10-closeout-cleanup`) is a different pull request. It waits correctly on #3065's verdict, so it is downstream, not a third self-refusal.
  - **The carry is stronger than the proposal.** It identifies the pull request by ancestry first and by name only as a fallback. A name-only rule misses #3065's round-4 topic `r10-fly-relay-review-ff` against branch `fix/r10-fly-relay-review-ff-2`. It already has the arm "own verdict must not block own body", a null control, an ambiguity arm, and the mutant "restore the literal 0".
  - **Delivery waits on a merge, not a ruling.** The carry stays held until #3158 puts `s6-batch110.md` on main. Boarding #3158 is the orchestrator's call; until then the hand `update_pr` path is the workaround.
  - **What would change it.** R10-ORCH-REVIEW-PACKET closing without building the carry, or the built rule still refusing a handoff against its own pull request.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. No roster op is queued.

## Head

`e13f1cddc78b400b8e4b8e7c4337a45993cc8b1b`; the file is the whole diff against `279cb497f`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P372 as `DEFER`, and a text citing `s6-batch114.md#P372` is refused: `is not an ACCEPT ruling (DEFER)`.
- With the verdict flipped to ACCEPT, it reads `ACCEPT` and the refusal is `None`.
- P373 reads `None`: no such entry.

## Null control

- With the file absent, the citing text is refused: `the triage ruling dev/programme/triage/s6-batch114.md is not on the roster branch or origin/main`.

## Figures

- `git show origin/main:tools/audit/seat/review_packet.py` at `279cb497f`: line 594 `hot_file_refusals(touched, open_prs, boarded, 0)`; line 548 passes `a.pr`; line 215 skips `this_pr`.
- Roster `e431aee1a`: R10-ORCH-REVIEW-PACKET at stage `carries-open`, 12 carries, none naming P368.
- `gh pr view 3158`: OPEN, `REVIEW_REQUIRED`. `gh pr view 3065`: head branch `fix/r10-fly-relay-review-ff-2`.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
