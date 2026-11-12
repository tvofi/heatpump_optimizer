Question: R10-TRAIN-RESIDUE-P2 is carries-open, so every body carry to it is BAD-DEST, and the owed item ce279d5a (Carry 0) is answered only by a dismissal to that same group. Which live group should receive the body's four carries (and ce279d5a)? Code head ec3c6b8b29 pushed to handoff/r10-ci-priority-pause with the closure classification (the UNCLASSIFIED refusal is cleared); body kept at handoff-wip/r10-ci-priority-pause-body.

body_push output, verbatim:
```
fill-red: the diff adds no unpinned mutation site; nothing written
pr-body ok: PR-BODY: 0 error(s) in /tmp/claude-0/body.md -- no budget leaf raised over 2bfa2f5fb7...ec3c6b8b29
REFUSE carry: BAD-DEST body item ce279d5a: R10-TRAIN-RESIDUE-P2: R10-TRAIN-RESIDUE-P2 is carries-open (resume.stage carries-open); a carry goes to the live group owning the seam, else the producing group keeps the fix; valid targets: unknown (no --pr-group) -- CARRY-AUDIT: 7 finding item(s): 2 routed, 0 unrouted, 5 bad destination(s), at origin/handoff/audit-r10-roster b58333d803
preflight ok
figures ok: FIGURES: 14 resolved, 0 not verified, 0 refused
figure blocks ok: figure_block verify: 0 block(s), 0 refused
ref_privacy ok: ref_privacy --check at HEAD: 30 file(s) with a push site, 12 guarded, 1261 line(s) added since 2bfa2f5fb799 judged, 0 refused
ref_privacy (body) ok: no host identity in the body
body_push: the pr-body lint refuses this body (above), as open_pr.sh's prepr step 7 would; repair it and push again
body_push: REFUSED BODY-LINT
body_push: refused body kept at handoff-wip/r10-ci-priority-pause-body cec5b653b65524562002959d185aeab726cde6f6
```
