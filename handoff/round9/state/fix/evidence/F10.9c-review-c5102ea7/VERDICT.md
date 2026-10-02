Fix review: blocked c5102ea715260c07fae83e36b3aa2bdba242d856 barrier: merge_fastpath says ELIGIBLE where run_always harness_headers reads INERT docs no closure records

Round 1, PR #1823 (stage 1), code head c5102ea7 (live head a70eb7cf adds only docs/delivery/1823.md).

BLOCKING
1. barrier (fast path). decide() checks overlap only through recorded closures. tests/harness_headers.py is
   run_always in run.sh:471 because tools/audit/round4/D6/claims.py reads DISCLAIMER.md, docs/backlog.md and
   docs/audit-2026-09.md, which are INERT and in no closure (the brief's own precondition). The fast path
   therefore scopes the merged tree's harness_headers, which the brief forbids.
   Probe (probe_c108.sh, my own instrument): PR changes only DISCLAIMER.md (adds a link to
   tools/audit/README.md); main deletes tools/audit/README.md.
     decide(pr=[DISCLAIMER.md], main=[tools/audit/README.md]) -> ELIGIBLE
     claims.py: PR side claims_false=0, main side claims_false=0, merged claims_false=1 (C108)
   claims.py's header pins claims_false=0, so harness_headers would be red on the merged tree, a merge the
   fast path let through without CI. probe_holes.out shows the same ELIGIBLE answer for every pairing of
   DISCLAIMER.md, docs/audit-2026-09.md and docs/setup.md.
   Fix direction (the fixer decides): treat each run_always script as selected, and refuse when either side
   changes a file it reads that no closure records (at least the three claims.py docs, or any INERT file
   while the other side touches that script's closure or such a file). Also add a self-test class with its
   null control.
2. conflict. git merge-tree origin/main(411368b6) c5102ea7 conflicts in tools/audit/briefs/orchestrator.md
   (#1818). Merge main and resolve it, keeping #1818's text and the new section 11 line.

CHECKED, SOUND
- Cancellation: each concurrency group is keyed on the PR number only for pull_request events from a sender
  other than github-actions[bot]. Push, schedule, workflow_dispatch, merge_group and pull_request_review
  runs each get their own run_id group, so main and scheduled runs are never cancelled. The two
  workflow_run re-run files have no concurrency block. No required job is gated on the event action, so a
  same-head edited or reopened run that replaces a cancelled one runs the same checks.
- merge_fastpath --self-test: 18 checks, 0 failed. Targeted mutant (overlap test disabled) fails 3 checks.
- The overlap test is symmetric. Defaulting to the fork point is conservative. --no-renames lists both paths.
- codeowners_gap --check: uncovered_files=0 at c5102ea7 and f88438dd.
- PINNED_OK and the prepr.sh 3e queue-base forms each have a probe and a null control.

NON-BLOCKING NOTES
- The env_drift "integration belt" (closure.select runs env_drift on any custom_components change) is not
  modelled in decide(). Today only quality_scale.yaml lies outside env_drift's closure, and probe_holes found
  no ELIGIBLE pair, so this is latent. Worth fixing together with item 1.
- contract_rerun and budget_raise_gate --rerun-stale can re-run an older head's run inside the new
  pull_request group, which cancels the current head's in-progress run. This fails closed (a cancelled
  required context) but nothing re-triggers it. The window is narrow.
- orchestrator.md says ELIGIBLE "merges as it is". Once the queue rule is active, a direct merge needs the
  ruleset bypass. Say which actor merges and how.

UNRUN: the full gate and the mutation table (cite CI; #1823 had no check runs when I looked), typing, real-HA.
