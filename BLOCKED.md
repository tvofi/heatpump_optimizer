# BLOCKED: body_push.sh exit 4 (CARRY-LANDED), r10-review-dispatch-residue-p3 at bd34f6b06b2b4a343cc8a0e80dc750d5c7d2995d

Code is at refs/heads/handoff/r10-review-dispatch-residue-p3 (bd34f6b06b2b, prepr rc=0); the refused body is at handoff-wip/r10-review-dispatch-residue-p3-body 587a30e2c0299419ed13cda03db685d66e54bcbf. The relay folds the carry and re-runs body_push.sh.

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-REVIEW-DISPATCH-RESIDUE at bd34f6b06b2b, 24 carries, 0 refused
CARRY-MISSING R10-REVIEW-DISPATCH-RESIDUE body item 9215543e: not in its brief or carries: "- review-packet-brief-carries: contradiction: `review_packet.py handoff` refused this part's body fo"
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-review-dispatch-residue-p3-body 587a30e2c0299419ed13cda03db685d66e54bcbf
```
