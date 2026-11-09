Fix review: merge 40c79702c72359f00a0a932eabf727a942b1f9eb

bus-nonce: 00e8e2ab9f45823b59fc2d883c26fc9d

## Evidence
- Head measured: 40c79702c72359f00a0a932eabf727a942b1f9eb (ev/HEAD.txt). Round 1.
- RESULT merge_train self-test at head: `merge_train self-test: 580 checks, 0 failed` (body figure matches; base 564 not re-run).
- RESULT pr_args self-test at head: `195 checks, 0 failed`. The body quotes 185; the extra 10 come from main's merge into the branch (2b9984cb4 added 64 lines to pr_args.sh), so the body figure is stale but nothing is red.
- RESULT mutants: `python3 dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py` printed `MUTANTS: 20 run, 0 not as required` (M0 pass, M1-M19 KILLED), re-run by this seat (ev/mutants.txt). The harness is the fixer's own, disclosed as such in the body (no finder harness; the findings come from the owner's cards).
- Merge with main: `git merge-tree --write-tree origin/main 40c79702...` exit 0, no MERGE-CLAIM refusal.
- CI: `merge_train.py classify 40c79702... --pr 3359` exit 0, GREEN (ev/classify.txt). No red check, so no root-cause answer is owed.
- VERSION, manifest and RELEASE_NOTES are untouched in the three-dot diff; no golden or claim file moved.
- Enumeration rules (self.recarry( call sites, self.skip( sites, MERGE CONFLICT) are named in the body; the recarry call sites in the diff are all handed nr_base. No open seam found.
- Forward-carry: carry-201.json entry is in the tree at this head. carry_audit at the head: 3 routed, 0 unrouted.
- Not re-derived: the owner's waste-study figures, which the body says are the brief's. The live ruleset read (strict_required_status_checks_policy false) was not re-read from this seat.
- Role-contract diff against main touches only proposal-triage.md, which does not bear on this review.

## Findings
- Residual: the body's pr_args figure (185) is stale against the head (195); no defect, the merged-in main accounts for it. Carry: dismissed: figure drift from main's merge, 0 failed at both
