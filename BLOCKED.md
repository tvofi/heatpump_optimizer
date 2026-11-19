# BLOCKED: R11-SEAM-comments-tests p1 fixer, code head 09d0ec868fa37aa143a2029a270c38d63d1e90ba

Question: May this body's three carries name a group whose id holds lowercase letters (R11-SEAM-comments-tests, R11-SEAM-comments-production)? `tools/audit/carry_audit.py` drops such a token, so body_push.sh refuses the body as BODY-LINT (exit 1) rather than CARRY-LANDED (exit 4). The carries can be routed only after that instrument accepts the roster's own group ids, or after the orchestrator names other destinations.

## What is done

- The code head is pushed to refs/heads/handoff/r11-seam-comments-tests at 09d0ec868fa37aa143a2029a270c38d63d1e90ba (base 1723f9fdc9d8a6e6987190d2887686297a621dd4; `git merge-tree --write-tree origin/main HEAD` reports no conflict).
- `tools/pr/prepr.sh` on that head refuses only `ci predict` and `carry`, both for the same three UNROUTED carry items. Every other step reads ok or skip, including `figures` (13 resolved, 0 refused), `figure blocks` and `pr-body`.
- body_push.sh kept the refused body at refs/heads/handoff-wip/r11-seam-comments-tests-body.

## The cause, measured

`carry_audit.py` reads a group token through GROUP_TOK (line 180): `\A[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\Z`. `seg_dests` drops any token it does not match as prose. So the item reads as unrouted with 0 bad destinations, never as a bad destination.

`python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <one item>`:
- with `Carry: R11-PRE-SHARED-FILES` (null control): `1 routed, 0 unrouted, 0 bad destination(s)`
- with `Carry: R11-SEAM-comments-tests`: `0 routed, 1 unrouted, 0 bad destination(s)`

27 of the 111 groups in wave-r11-groups.json on origin/handoff/audit-r10-roster have a lowercase letter in their id, so a carry to any of them fails the same way.

## The body_push output

```
figure blocks ok: figure_block verify: 1 block(s), 0 refused
ref_privacy ok: ref_privacy --check at HEAD: 32 file(s) with a push site, 12 guarded, 609 line(s) added since 1723f9fdc9d8 judged, 0 refused
ref_privacy (body) ok: no host identity in the body
body_push: the pr-body lint refuses this body (above), as open_pr.sh's prepr step 7 would; repair it and push again
body_push: REFUSED BODY-LINT
fatal: expected 'acknowledgments', received 'packfile'
warning: push negotiation failed; proceeding anyway with push
remote: 
remote: Create a pull request for 'handoff-wip/r11-seam-comments-tests-body' on GitHub by visiting:        
remote:      https://github.com/tvofi/heatpump_optimizer/pull/new/handoff-wip/r11-seam-comments-tests-body        
remote: 
body_push: refused body kept at handoff-wip/r11-seam-comments-tests-body c88ee7f99faeecabf38aad8621495f1fab171c82
```
