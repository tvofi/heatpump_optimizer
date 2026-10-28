Fix review: merge 2bb638af88f6373fe208dd2e57676dfac723bec8

bus-nonce: 4c449d579ce051cacc85535029ceb8b0

Round 1. No group; reviewed against the PR body. Head measured: 2bb638af88f6373fe208dd2e57676dfac723bec8 (ev/HEAD.txt). Roster-only PR: mutation, finder-harness, drift and null-control steps are n/a (body says so; the diff is 2 files, the roster and its own delivery row).

1. Three-dot diff of wave-r10-groups.json against origin/main (a243a79f4) changes exactly the listed items and nothing else:
   - R10-CI-LAYOUT-P2: the "refuses rather than mixing" carry replaced by the corrected drop-edge carry.
   - R10-CURRENCY: the O19 carry added; its fix-shape clause begins "Roster-seat wording, not #2620's".
   - R10-LEARNER-ETA, R10-UX-HEALTH, R10-ARCH-DOCS: one carry each, prefixed "(from R10-SCORES #2647, Forward-carry)", text equal to #2647's live body Forward-carry item, less the trailing "Carry: ..." marker (checked programmatically).
   - R10-FLY-NO-FOOTERS: stage done, commit 7deeef1b6b083b0fb5a8379717f3facd61897c6a, pr 2636.
   - R10-FLY-NO-FOOTERS-EMITTERS: added, after R10-FLY-NO-FOOTERS, stage in-progress, resume.branch fix/r10-trailer-emitters, one carry.
   The only other file is dev/programme/delivery/2651.md (the PR's own row).
2. 7deeef1b6b is an ancestor of origin/main: yes.
3. Groups 167 on origin/main, 168 at head, unique names, none removed, one added.
4. brief_lint: "TOTAL: 0 error(s) across 47 file(s)" (ev/total.txt). The "issue 990004" lines in the output are its own malformed-fixture self-test. ref_privacy --check: 0 refused.
5. Merge with origin/main: merge-tree rc=0, clean (ev/merge-tree.txt). dev/governance/roles/ unchanged between the merge base and origin/main (fresh contract).
6. CI, one bulk read of check-runs at this head (39 runs, ev/check-runs.json): no failed, cancelled or timed-out run; four still in_progress when read (closures, fast (3.14), env-matrix, instrument-self-tests). No red check, so no root-cause answer is owed. budget-raise-gate, pr-contract, briefs, delivery-status, nightly-status, mutation, closure-scope, arch-score and policy-docs are success. The in-progress heavy runs are cited from CI, not re-run; if one goes red the orchestrator should treat this verdict as not covering it.
7. VERSION, manifest version and notes heading: untouched (diffstat shows two files). Forward-carry: the body states none; none is owed beyond the carries the diff itself writes.
Caveats: the body's Head section lists three head SHAs in successive paragraphs; the first is the measured head, the others are stale text from earlier handoffs. Not a defect in the roster.
