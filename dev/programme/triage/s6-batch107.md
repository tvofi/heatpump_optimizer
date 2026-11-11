# Proposal triage, session s10, batch 107 (P365)

The rolling batch after batch 106. Facts were read at origin/main `7f849a249`, at the round's
roster branch `origin/handoff/audit-r10-roster` (`a7856cd5c`), at pull request #3077's head
`aa6148d4f`, and in the session's seat ledger. P364 was never assigned: the queue line numbers
this proposal P365.

## P365: a merge verdict cannot be posted at a head it carries to

Verdict: ACCEPT, by owner ruling (tvofi, 2026-11-01T20:34:40Z, queue line: "P365 should be
approved as owner rules"). The destination is the existing carry 3 of R10-FLY-CARRY-DOC-CONTEXT
(P264, `s6-batch53.md#P264`), which is already built in #3077. No new carry is queued.

Source: the orchestrator s10's queue line of 2026-11-01T20:40Z. It marks the proposal as blocking a
production merge: #3047, the v7.1.1 fix, whose head moved from `9cddcb4f` to `ace2e21a`.

Instances:
- **The refusal, read from code at `7f849a249`.** `tools/pr/app_comment.sh` lines 68-69 refuse any
  merge verdict whose SHA is not the live head ("head moved").
  - `tools/audit/seat/bus.sh` line 512 refuses a second reviewer when `review_carry.py` prints
    CARRY (tvofi, 2026-10-27).
  - `tools/pr/app_approve.sh --carry` accepts a carried verdict, but it needs an approver comment
    that `app_comment.sh` will not post.
  - So a head that moved without new code can be neither re-reviewed nor approved.
- **#3047, from the seat ledger.**
  - Between 20:25Z and 20:27Z, an orchestrator line records that `app_comment.sh --dry-run` refused "head moved (verdict 9cddcb4f, live ace2e21a)".
  - 20:27:51Z: dispatch did not render a re-review, because `bus.sh dispatch --reviewed-head
    9cddcb4f` refuses on "review_carry CARRY".
  - 20:37:15Z: #3047 was merged by hand outside the train. The carry was `review_carry` CARRY
    with an identical tree (`e58eadb7`).
- **The same defect was ruled before.** P264 (2026-10-28, four instances in seven days: #2612,
  #2775, #2745 and #2912) is R10-FLY-CARRY-DOC-CONTEXT carry 3. It specifies exactly this change:
  in `check_pr`, a moved merge head runs `app_approve.sh --carry` and posts on `CARRY: yes` with
  one body line, `carry: <verdict-head> -> <live-head>, app_approve.sh --carry: yes`.
- **It is built.** #3077 (head `aa6148d4f`, open, in the stamp-batch train `54386` with #3050, #3118,
  #3142 and #3141 per the merge seat's ledger line of 20:11:37Z) changes `check_pr` so that a merge
  verdict posts at the verdict's SHA or at a head it carries to. Its diff against main is
  `tools/pr/app_comment.sh` with 56 lines added and 8 removed. Its self-test arms are:
  - a pin-only head posts with the carry as the body's last line;
  - a branch's own code commit is refused "head moved";
  - the carried body reads back identical.
- **It covers #3047's merge-shaped move.** `review_carry.py` prints CARRY only where
  `app_approve.sh --carry` carries, by its own docstring: "One predicate, asked rather than copied".
  #3047's move printed CARRY (ledger, 20:37:15Z). So the `check_pr` in #3077 would have posted
  the verdict at `ace2e21a`.

Cost:
- **Zero new work.** The change is written, reviewed and queued in #3077.
- **A second carry would cost.** It would duplicate P264, and `brief-carries` would refuse
  #3077's in-flight packet, as it does for any carry added to an in-flight group.

Binding:
- **Why ACCEPT with no new carry.** The owner ruled ACCEPT. The architecturally sound fix is the
  one already accepted: one carry rule (`app_approve.sh --carry`) read by `app_comment.sh`,
  `bus.sh` and `merge_train.py`. Under the 19:50Z owner rule it also qualifies on its own, because
  it blocked a production merge (#3047).
- **Delivery is #3077's merge.** Until then, a carried head needs the manual path the orchestrator
  used on #3047.
- **`bus.sh` stays unchanged.** Refusing a second reviewer on CARRY is right once the carried
  verdict can be posted. That matches P264 ("bus.sh and train.sh unchanged").
