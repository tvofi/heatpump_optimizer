Fix review: blocked 8584e81580213478226b78409b2d3f8ed16b52c2 head-moved: measured 8584e81580213478226b78409b2d3f8ed16b52c2, head is d4f71c00acdedb70f9fcdbf619030a7766b76d04

bus-nonce: f701ad71bae821da952737ca19c43a89

## Block

Contract: `dev/governance/roles/fix-review.md` steps 7 and 12 (current: no diff to origin/main under `dev/governance/roles/`). I was dispatched to review the re-cut head 8584e81580213478226b78409b2d3f8ed16b52c2. When I read the PR (2026-10-25 ~20:25Z) its head was d4f71c00acdedb70f9fcdbf619030a7766b76d04, committed 2026-10-25T20:19:57Z, and the body's `## Head` names d4f71c00acdedb70f9fcdbf619030a7766b76d04, not the head I measured. Step 12: "one that moved under you is a broken rule rather than an accident: `blocked <sha> head-moved`". This is round 2. The orchestrator decides whether d4f71c00acdedb70f9fcdbf619030a7766b76d04 is re-dispatched. Below, the delta 8584e81580213478226b78409b2d3f8ed16b52c2..d4f71c00acdedb70f9fcdbf619030a7766b76d04 is checked as an offer, which step 12 says is "yours to offer, never owed". It is not a verdict on d4f71c00acdedb70f9fcdbf619030a7766b76d04.

What survives at each head, against the round-1 verdict on ef926de78 (verdict 6402517605):

1. Block item 1 (P169, P170, P173, P174 ACCEPT unmeasured): **closed at 8584e81580213478226b78409b2d3f8ed16b52c2.** Each one's `Verdict:` is DEFER and names its measurement. P169: "the share of round-10 blocked verdicts a shadow reviewer ... would have pre-empted, by verdict id". P170: "the train's recarry CI wait per batch from the train logs". P173: "the count of blocked verdicts whose class is a missing body section, harness or mutant scaffold". P174: "a small model's rubric findings scored against real verdicts".
2. Block item 2 (P172 and P175 ACCEPT to D13): **closed at 8584e81580213478226b78409b2d3f8ed16b52c2.** Both are DEFER, "D13 owns the measurement". P175's carry to R10-ROUND-PLAYBOOK is gone.
3. Block item 3 (P168): **closed at 8584e81580213478226b78409b2d3f8ed16b52c2.** The entry is "Verdict: DEFER (ordering)", and the cancel arm is "REJECTED on its binding cost" in the same line. `ruling_verdict` reads DEFER (ev/ruling_verdict.txt), so no roster op can cite it as an ACCEPT.
4. Block item 4 (P171): **closed at 8584e81580213478226b78409b2d3f8ed16b52c2.** "Verdict: DEFER -> owned by the carries named below".
5. Finding: P175 "38/71 = 0.54 (plan-opt flow_metrics)". **Open at 8584e81580213478226b78409b2d3f8ed16b52c2, closed at d4f71c00acdedb70f9fcdbf619030a7766b76d04.** Changed to 117/255 (0.46) with the command and window. Re-derived at d4f71c00acdedb70f9fcdbf619030a7766b76d04's command: "first-pass yield 117/255 (0.46)" (ev/flow_metrics.txt).
6. Finding: figures with no command (P168 1.45-2.35 h, P169 2.26, P170 920 s / 10.4, P172 63 blocks). **Open at 8584e81580213478226b78409b2d3f8ed16b52c2, closed at d4f71c00acdedb70f9fcdbf619030a7766b76d04.** Each figure is dropped, or marked out of tree and "not used as a figure".
7. Finding: dependencies stated as settled. **Open at 8584e81580213478226b78409b2d3f8ed16b52c2, closed at d4f71c00acdedb70f9fcdbf619030a7766b76d04.** P158 is now "an ACCEPT trial on #2829, not yet on main", P153 "itself DEFER on #2828, not on main", P176 "itself DEFER on #2831, not on main". These match the sibling branches: batch28 5d093b09f P153 DEFER, batch29 9ddadc766 P158 ACCEPT as a trial, batch31 b6df9b2b9 P176 DEFER (ev/sibling_rulings.txt).
8. Finding: citations beside their claim. **Open at 8584e81580213478226b78409b2d3f8ed16b52c2, closed at d4f71c00acdedb70f9fcdbf619030a7766b76d04.** `ci.yml:169-241` (`needs: prelude`) and `:301-302` (`gate: needs: [prelude, pr-contract]`) are re-anchored. So is `fix-review.md:13-14` (step 2, the finder's harness) (ev/citations.txt).

At 8584e81580213478226b78409b2d3f8ed16b52c2 itself, the rulings conform to the triage rule. Findings 5-8 are still open there, so 8584e81580213478226b78409b2d3f8ed16b52c2 could not take a merge in any case. On the delta I read, d4f71c00acdedb70f9fcdbf619030a7766b76d04 closes them, and I found nothing in it I would block. That reading was not a full review of d4f71c00acdedb70f9fcdbf619030a7766b76d04.

## Findings

- **The head moved after dispatch, from 8584e81580213478226b78409b2d3f8ed16b52c2 to d4f71c00acdedb70f9fcdbf619030a7766b76d04.** That delta (ev/head_move_diff.txt) is what closes findings 5-8 and needs its own dispatched review at d4f71c00acdedb70f9fcdbf619030a7766b76d04. Carry: dismissed: re-dispatch at d4f71c00acdedb70f9fcdbf619030a7766b76d04 is the orchestrator's next routing step under fix-review.md step 12, not a later stage

## Evidence

- Head dispatched and reviewed: 8584e81580213478226b78409b2d3f8ed16b52c2 (ev/HEAD.txt). Current head: d4f71c00acdedb70f9fcdbf619030a7766b76d04 (ev/current_head.txt).
- Diff vs merge base c9cbe6b45 (three-dot) at 8584e81580213478226b78409b2d3f8ed16b52c2: only `dev/programme/triage/s6-batch30.md` (+85) and `dev/programme/delivery/2830.md` (+1) (ev/diffstat.txt). 8584e81580213478226b78409b2d3f8ed16b52c2..d4f71c00acdedb70f9fcdbf619030a7766b76d04 touches only the batch file (ev/head_move_diff.txt).
- No host or home path in the batch file at 8584e81580213478226b78409b2d3f8ed16b52c2 (`grep -nE '/home|/Users|/root|/tmp|~/'`: no match).
- `git merge-tree --write-tree origin/main 8584e81580213478226b78409b2d3f8ed16b52c2`: exit 0, tree 3aea0fad7, origin/main 8aee66b77 (ev/merge_tree.txt).
- Verdict count at both heads: 8 `Verdict: DEFER`, 0 ACCEPT, 0 REJECT lines. This matches the body's "8 DEFER". `roster_edit.ruling_verdict` gives DEFER for P168-P175, and None for P176 (the body's null control, re-run) (ev/ruling_verdict.txt).
- No ACCEPT remains, so no destination group has to be live. The DEFERs name their measurement, which is what the contract's DEFER needs. "D13" is a dimension brief, not a roster group, and the DEFERs do not need one.
- CI on d4f71c00acdedb70f9fcdbf619030a7766b76d04 (check-runs API, ~20:25Z): 7 runs, prelude/refresh/cancel-superseded queued, arm skipped, none red. CI had not run to completion when I read it. The head-moved block does not depend on it. No CI read was taken on 8584e81580213478226b78409b2d3f8ed16b52c2.
- Round: 2 (round 1 blocked at ef926de78).
