# Proposal triage, session s10, batch 114 (P372)

The rolling batch after batch 113. Facts were read at origin/main `279cb497f`, at the round's
roster branch `origin/handoff/audit-r10-roster` (`e431aee1a`), and in the session's seat ledger.

## P372: body_push's hot-file guard refuses a pull request's own handoff (a re-file of P368)

Verdict: DEFER. The item is already owned: carry b110-P368 for R10-ORCH-REVIEW-PACKET, routed
from P368 (`s6-batch110.md#P368`, ACCEPT as a defect). No new carry and no group. The answer
changes only if R10-ORCH-REVIEW-PACKET closes without building that carry, or if the built rule
still refuses a handoff against its own pull request.

Source: the orchestrator s10's message of 2026-11-02, about 09:52Z, filed as a critical-path
deadlock. It proposes that the hot-file guard exclude the pull request the topic maps to, keyed
on topic to pull request, with a self-test arm "own verdict must not block own body" and a
killed mutant.

Instances:
- **#3065 round 7, 09:05Z.** Seat ledger at 09:52:34Z: the r7 handoff `3c00ec8c` passed prepr,
  but `body_push.sh` refused with `REFUSE hot-file: #3065 holds an unboarded merge verdict and
  shares ...`. #3065's head branch is `fix/r10-fly-relay-review-ff-2` (`gh pr view 3065`).
- **#3065 round 4, 01:54Z.** Seat ledger at 01:54:39Z: "#3065 r4 body_push self-refused". This
  is P368's own instance, the same pull request and the same mechanism.
- **#3085 is downstream, not a third instance.** #3085 is `fix/r10-closeout-cleanup`, a
  different pull request. Its refusal is the guard working as designed: another pull request
  (#3065) holds an unboarded merge verdict on a shared hot file. The ledger's OWED-ACK lines from
  04:19Z to 08:49Z say "update_pr after #3065 merges". It waits on #3065's merge, and #3065
  cannot hand off its own body.
- **The defect is still on main.** At `279cb497f`, `tools/audit/seat/review_packet.py` line 594
  calls `hot_file_refusals(touched, open_prs, boarded, 0)` in `handoff()`. The render path at
  line 548 passes `a.pr`. `hot_file_refusals` already skips `p["number"] == this_pr` (line 215).
- **The owning carry is written and held.** Line 2199 of the roster queue holds
  `#held append-carry R10-ORCH-REVIEW-PACKET` for b110-P368. It is released once
  `s6-batch110.md` is on main, through #3158, which is open with `REVIEW_REQUIRED`. On roster
  `e431aee1a`, R10-ORCH-REVIEW-PACKET is at stage `carries-open` with 12 carries, and none of
  them names P368.

Cost:
- A second carry would be a second specification of one rule on R10-ORCH-REVIEW-PACKET.
- It would also be a weaker one. The proposal keys on topic to pull request, by name. P368
  rejected a name-only rule because #3065's round-4 topic was `r10-fly-relay-review-ff` while its
  branch is `fix/r10-fly-relay-review-ff-2`. The carry identifies the pull request by ancestry
  first and uses the name only as a fallback.
- Everything else the proposal asks for is already in the carry:
  - the arm "own verdict must not block own body" is its arm (a);
  - the killed mutant is "restoring the literal 0 must fail arm (a)";
  - it also has a null control, arm (b), and an ambiguity arm, arm (c).
- No capped file is touched by this ruling.

Binding:
- **Why DEFER.** The destination already exists and holds a stronger form of this remedy. This
  instance adds a count, a second self-refusal on #3065, and it shows that the defect blocks a
  second pull request, #3085, by holding #3065 open.
- **Delivery waits on a merge, not on a ruling.** The carry cannot land until #3158 puts
  `s6-batch110.md` on main. When to board #3158, and when to dispatch the group, is the
  orchestrator's decision, not a triage one. Until then, the hand `update_pr` path is the
  workaround.
- **Not ruled under the LOG class.** P368 was ACCEPTed as a defect, not as a proposal, and this
  ruling does not re-rule it.
