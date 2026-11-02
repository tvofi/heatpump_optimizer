Triage batch 110 records one ruling, P368, from the orchestrator s10's queue line of 2026-11-02T01:54:39Z. The defect is in `tools/audit/seat/review_packet.py`: its `handoff()` passes the literal `0` as `hot_file_refusals`' `this_pr`. So a pull request that holds an unboarded merge verdict on a hot file refuses its own next handoff, and `body_push.sh` refuses with it. #3065's round 4 body was re-taken by hand at 01:54Z. This is the rolling batch after batch 109.

- **P368: ACCEPT, as a defect.** One new carry, `b110-P368`, on R10-ORCH-REVIEW-PACKET.
  - **Why that group.** It owns `review_packet.py` and built `handoff()` (carry 6, P256). The instrument audit keeps it as-is, and it has no pull request in flight.
  - **The fix.** `handoff()` passes the number of the open pull request it updates, found by ancestry first and by the `fix/<topic>` branch name second; an ambiguous match refuses and names both. A name rule alone misses #3065, whose topic `r10-fly-relay-review-ff` differs from its branch `fix/r10-fly-relay-review-ff-2`.
  - **Fixtures.** (a) The handoff's own pull request is not refused. (b) The null control: another verdict-holding pull request on the same hot file still is. (c) The ambiguous case is named. The mutation restoring `0` fails (a).
  - **Why it is ruled as a defect.** `HOT_FILES` is seat tooling only, so no production merge is held. The 2026-11-01 proposal bar does not apply to a verified defect, and the owner's deadlock rule routes its permanent fix through triage.
- **The roster op is held.** The queue line `#held append-carry R10-ORCH-REVIEW-PACKET @.../b110-P368.txt` is released by the triage seat's release pass once this file is on main.
  - Dry-run at roster `dff6373f7`: 12 -> 13 carries, `triage_refusal` None, `brief_lint` `TOTAL: 0 error(s)`.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`46479097090e867e23b9ae6f15aba6b07d3b2286`; the file is the whole diff against `94d8b47f6`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P368 as `ACCEPT`, and a text citing `s6-batch110.md#P368` passes `triage_refusal` (None).
- With the verdict flipped to REJECT, it reads `REJECT`, and the citing text is refused: `is not an ACCEPT ruling (REJECT)`.
- P369 reads `None`: no such entry.

## Null control

- With the file absent, the citing text is refused: `the triage ruling dev/programme/triage/s6-batch110.md is not on the roster branch or origin/main`.

## Figures

- `grep -n 'hot_file_refusals(touched' tools/audit/seat/review_packet.py` at `94d8b47f6`: line 548 passes `a.pr`, line 594 passes `0`.
- `grep -c review_packet tests/structure_budgets.json`: 0. No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
