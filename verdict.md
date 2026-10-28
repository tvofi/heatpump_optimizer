Fix review: merge 3754510d82e329cbb27d2f8ca38ed031eaafa6c2

bus-nonce: a689be79680db88af6f91725d84270fe

Round 1. Head measured: 3754510d82e329cbb27d2f8ca38ed031eaafa6c2 (PR head at read; base beb570c8 equals origin/main).

## Findings

- The body's "16 of 284 PRs merged since 2026-10-21" does not reproduce under the stated rule. First-parent merges give 18 of 327 since 2026-10-21T00:00Z and 16 of 275 since 2026-10-22T00:00Z; no window I tried gives 284. The ruling's accept does not turn on the figure, since 16 to 18 pin commits and the six pre-pin verdicts (re-derived) stand. Carry: dismissed: the ruling holds under every figure I derived, and the file is a triage record, not a gate input.
- The per-PR timing for #2612, #2775 and #2745 (pin commit time before verdict time) is not re-derived. My pin-time lookup hit the frugal inline-search guard and I did not work around it. The earliest merge-verdict commit times I saw (#2612 19:38Z and #2775 08:03Z, both matching the body; #2745 earliest 17:43Z on 10-24, against the body's 01:45Z on 10-25) leave the "4 instances in 7 days" count partly unverified. Carry: dismissed: the six-PR pre-pin-verdict count is verified and is enough for the ACCEPT, only the sub-count of 3 is open.
- The carry text for R10-FLY-CARRY-DOC-CONTEXT is not yet in the roster. The live group (handoff/audit-r10-roster, stage not-started) has no mention of app_comment or P264 in its brief; the body says the queued carry cites #P264 and the roster_edit.py triage gate needs this file on origin/main first, so the carry can only land after the merge. The group's brief must state the control (pin-only head posts with a carry line; head with a branch-own code commit still refused; mutant without the carry call fails; unmoved head posts with no carry line) as a precondition. Carry: R10-FLY-CARRY-DOC-CONTEXT

## Evidence

- Mutation proof re-run: roster_edit.py ruling_verdict reads P264 ACCEPT on the file and REJECT on a copy with the verdict rewritten; triage_refusal then refuses with "is not an ACCEPT ruling (REJECT)". Null control (file absent) returns "not on the roster branch or origin/main". Both as the body states.
- Merge: git merge-tree --write-tree origin/main head exits 0.
- VERSION, manifest version, notes heading, and both claim files are untouched; the diff is two added markdown files.
- Cited lines match the tree at the base: app_comment.sh 68-69, merge_train.py 2029, 2045-2048 and 2076.
- Verdict-count figures in the body (14, 3, 2, 2, 5, 2) re-derived exactly.
- No product code is changed, so there is no harness, drift, closure or budget movement to measure; no finder's harness is named and none applies to a triage ruling.
- CI at read time: 7 check runs on the head, arm skipped, six queued (prelude, refresh, cancel-superseded), none red or concluded. Heavy CI is cited, not re-run. The body's "Red checks: none" is consistent with this.
- carry_audit at the head: 1 item, routed, 0 unrouted. figure_lint: 0 refused.
- Forward-carry: the body's carry line names the destination group, which exists in the live roster at not-started.
