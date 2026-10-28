Fix review: merge 6e65b77ed379b9825e885362dbe9117dcb41281c

bus-nonce: f92a8ab1f6d8c6fb9a8d84b185d3e884

Round 1. Measured head 6e65b77ed379b9825e885362dbe9117dcb41281c (base beb570c817c4efcae0d5f6f4bba52f3383baf8db, still origin/main). Diff is two markdown files: dev/programme/triage/s6-batch52.md and dev/programme/delivery/2924.md. No production code.

## Findings

- The four ACCEPT rulings (P254, P256, P259, P261) owe roster carries that are queued, not yet landed: roster 2ce021c has no string for any of them in 215 groups. They land after this merge through roster_edit, which reads this file. Carry: R10-FLOW-TOOLKIT-MODEL | #P254 | O1 | dismissed: queued by the body's Forward-carry section, which names the group; the triage gate refuses them until this file is on main
- P256 carry (R10-ORCH-REVIEW-PACKET), P259 carry (R10-FRICTION-REGRESSION, 0 carries today) and P261 carry (R10-ARCH-DOCS) are owed the same way after the merge. Carry: R10-ORCH-REVIEW-PACKET | #P256 | O2 | dismissed: queued, see previous bullet
- P257 and P262 are DEFER rulings and P263 leaves a measurement (n>=8 windows, load1<20) to the triage seat; each is a task owed after the merge. Carry: R10-TRIAGE-S6 | #P263 | O3 | dismissed: the ruling file records what would change each DEFER, and the P263 re-take is the triage seat's own follow-up
- The body cites pr_cap.py:54 for the HPO_WIP_CAP default of 6; the default is WIP_CAP_DEFAULT at line 53 and line 54 is the env-var name. Value 6 is right, citation is one line off. Carry: R10-TRIAGE-S6 | #none | O4 | dismissed: off by one line, value correct, no ruling rests on the line number
- review_packet.py render refused with home-directory on s6-batch52.md:203: this seat's HOME is /root and "roles/root-cause.md" contains "/root". A false positive of the privacy check on cloud seats, not a defect in the PR. The packet was therefore not written and I worked from the PR, not the packet. Carry: R10-TRIAGE-S6 | #none | O5 | dismissed: host-specific match of ref_privacy on a path component, not this PR's content; no home path exists in the added lines (grep for /home, /Users, ~/, /root/ found none)

## Evidence

- RESULT mutation: ruling_verdict reads P254 P255 P256 P259 P260 P261 P263 ACCEPT, P257 P262 DEFER, P258 REJECT. Gate passes the four carry texts (P254 P256 P259 P261). Mutant (P259 verdict DEFER in a copy) is refused: "#P259 is not an ACCEPT ruling (DEFER)". Null control (file absent) returns "the triage ruling dev/programme/triage/s6-batch52.md is not on the roster branch or origin/main". Output in ev/mutation.txt.
- RESULT figures re-derived: replan.py:188 is_done counts only done and rca-done; the done set is built at line 232 area; four absorbed groups on roster 2ce021c are R10-ORCH-MACHINERY, R10-ROUTING-INVARIANTS, R10-FLY-POOL-INSTRUMENT, R10-FLY-RECORD-BEAT; R10-ARCH-DOCS has 81 after-edges and 7 carries; no roster group names ROWONLY; refs/pull/2923/head is b04f9e93bd4ec068436a90f000a98851ed44318c; HPO_WIP_CAP default 6.
- Not re-derived (the body also says so): the research seat's 71 blocked verdicts, +4.3 h per round, 2.13 h median, 50 min gap, CodeQL 33.3 min, the 92 % figure and the 140.82 h to 132.55 h forecast. No ruling rests only on them, per the file's own statement.
- Merge: git merge-tree --write-tree origin/main HEAD exits 0, no conflict, no MERGE-CLAIM lines.
- VERSION, manifest and RELEASE_NOTES untouched; no golden or claim file in the diff; no budget, closure or ledger file touched.
- Commit messages carry no Claude attribution.
- CI on this head: check-runs API shows arm skipped and prelude, refresh, cancel-superseded queued; no workflow had concluded and none is red, so no red-check answer is owed. pr-contract had not run; I could not confirm the body check. Not a required-check verdict of mine.
- Forward-carry (step 10): the four carries are queued ops against this file, not yet in the roster; confirmed that none exist yet and the gate will refuse them until the file is on main.
