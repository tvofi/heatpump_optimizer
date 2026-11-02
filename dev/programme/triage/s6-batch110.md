# Proposal triage, session s10, batch 110 (P368)

The rolling batch after batch 109. Facts were read at origin/main `94d8b47f6`, at the round's
roster branch `origin/handoff/audit-r10-roster` (`dff6373f7`), at pull request #3065, in the
instrument-group audit's report, and in the session's seat ledger.

## P368: the review packet's handoff check refuses a pull request against itself

Verdict: ACCEPT -> R10-ORCH-REVIEW-PACKET, one new carry (`b110-P368`). This is a defect in a
built instrument, not an improvement. The owner's rule of 2026-11-01 ~19:50Z gates proposals, and
the 21:30Z audit card keeps and routes verified defects. Owner rule in force: an instrument
deadlock is worked by hand, and its permanent fix goes through triage.

Source: the orchestrator s10's queue line of 2026-11-02T01:54:39Z (#3065 round 4).

Instances:
- **The defect, read from code at `94d8b47f6`.** `tools/audit/seat/review_packet.py`:
  - `hot_file_refusals(paths, open_prs, boarded, this_pr)` skips the pull request numbered
    `this_pr`. That is its self-exclusion.
  - The dispatch-time render (line 548) passes `a.pr`.
  - `handoff()` (line 594) passes the literal `0`, so at the handoff no open pull request is ever
    excluded, the one being updated included.
  - So a pull request that holds an unboarded merge verdict and touches a hot file refuses its own
    next handoff with `hot-file`.
  - `tools/audit/seat/body_push.sh` line 56 runs `review_packet.py handoff`, so the body push is
    refused too.
- **#3065, from the seat ledger.** It touches `tools/audit/seat/cloud_relay.sh` and
  `dev/audit/harnesses/r10_seat_selftests_mutants.py`, both in `HOT_FILES`.
  - 01:54:39Z: "#3065 r4 body_push self-refused (review_packet hot-file with this_pr=0); hand body
    re-take dispatched; P368 filed".
  - 01:54:42Z to 01:55:14Z: the body was re-taken by hand in a separate worktree.
- **A name rule alone would miss #3065.** Its handoff topic is `r10-fly-relay-review-ff` while its
  branch is `fix/r10-fly-relay-review-ff-2` (ledger, 00:12:47Z and 01:35:25Z). So the carry
  identifies the pull request by ancestry first: a re-cut is built on the pull request's head.
- **Not a production block.** `HOT_FILES` names only seat tooling, so this refusal cannot hold a
  `custom_components/` pull request. It is ruled as a defect: a guard that refuses the work it
  exists to protect, with a deadlock worked by hand once already.

Cost:
- S. One call site in `handoff()`; `hot_prs()` also returns each pull request's head branch for
  the fallback. Three fixture arms in the self-test, one of them the null control.
  `grep -c review_packet tests/structure_budgets.json` prints 0: no capped file is touched.
- **Destination.** R10-ORCH-REVIEW-PACKET owns `review_packet.py` and built `handoff()` (carry 6,
  P256). The audit's report keeps it as-is (lever L5). It has no open pull request and its last
  handoff ref is from 2026-10-31, so a new carry refuses no packet in flight.
  R10-DISPATCH-AT-HANDOFF also lists `review_packet.py`, but it is after R10-ORCH-REVIEW-PACKET
  and its subject is the dispatch moment, not this check.

Binding:
- **Why ACCEPT.** The check's own self-exclusion is dead at one of its two call sites. Each
  instance costs a hand re-take and an orchestrator turn. The fix is a parameter at a call site,
  with a null control that keeps the real collision refusal.
- **Carry text** (`b110-P368`, held until this file is on origin/main): `handoff()` passes the
  number of the open pull request the handoff updates, found by ancestry, then by the
  `fix/<topic>` branch name; ambiguity refuses and names both. Fixtures (a) own pull request not
  refused, (b) another pull request still refused, (c) ambiguous case named. The mutation
  restoring the literal 0 fails (a).
