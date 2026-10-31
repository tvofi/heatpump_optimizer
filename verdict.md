Fix review: merge ff4e8cd492a42d9daf4d380ce4680bc76242fc13

bus-nonce: 6778aac42ced451b35573f35bf5a6410

## Summary
Round 1, a record PR at head ff4e8cd492a42d9daf4d380ce4680bc76242fc13. The diff is two markdown files (dev/programme/triage/s6-batch77.md, dev/programme/delivery/3019.md) and no production code.

## Findings
none

## Evidence
- Ruling evidence: `carry_audit.py pr 3013` at this tree prints `UNROUTED #3013 review 6533404333 item fccf8846 (## Summary) [non-blocking]`, quoting the away.py code-owned line. This matches the cited park.
- carry_audit.py:205-216 shows the current Evidence-only arm, then the all-sections NONBLOCK arm for other merge-verdict sections. This matches the ruling's account of the trigger.
- Triage gate: `ruling_verdict` reads P314 as ACCEPT and `triage_refusal` returns None for the carry citation. With the verdict line mutated to REJECT it refuses (`is not an ACCEPT ruling (REJECT)`). With the file absent it refuses (`not on the roster branch or origin/main`). See ev/triage-gate.txt.
- Roster ops: the batch names one held op, append-carry on R10-FLY-RELAY-REVIEW-FF (group exists on origin/main), citing P314. Its text agrees with the ruling: widened structural rule, blocked verdicts and Findings unchanged, no keyword exclusion, one mutant. P308 exists in s6-batch74.md.
- The 21 PARK lines on 16 PRs come from the orchestrator's out-of-tree train.log, which I could not re-derive. I rely on the PR body for that count and verified only the #3013 instance.
- Merge with origin/main: `git merge-tree --write-tree` exit 0, clean (ev/merge-tree.txt).
- VERSION, manifest and RELEASE_NOTES are untouched. The diffstat lists only the two files.
- CI: `merge_train.py classify` exited 0 (GREEN) at this head. The packet's carry_audit reports 0 finding items and figure_lint reports 2 resolved, 0 refused.
- Red checks: none, so root-cause owes nothing. Forward-carry: none beyond the held append-carry, which is carried by the ruling itself.
