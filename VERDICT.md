Fix review: merge 60279abb4d3160ed64fd0a2fe73c4c6c3fbeed86

bus-nonce: 52c0053e0dca206605bd785ee8db74df

Round 1. Record PR for triage batch 112 (P370, DEFER). Measured at head 60279abb4d3160ed64fd0a2fe73c4c6c3fbeed86.

## Findings

none

## Evidence

- Three-dot diff against the merge base: exactly two files, dev/programme/triage/s6-batch112.md (44 lines) and dev/programme/delivery/3161.md (1 line, open-row shape matching #3152 and #3146). No claim file, VERSION, manifest, RELEASE_NOTES or production code change; no host path in added lines.
- git merge-tree --write-tree origin/main HEAD: rc 0, no conflict.
- Roster 5dc16bbe1 (origin/handoff/audit-r10-roster, wave-r10-groups.json): R10-OPENER-REUSE holds 10 carries; carry 10 opens "From triage P363" and amends rule (3) of P337 (carry 8); resume stage not-started, next step "dispatch a fixer", branch handoff/r10-opener-reuse. Five group names end in a part suffix (R10-STALE-PATHS-2, R10-CI-LAYOUT-P1, R10-CI-LAYOUT-P2, R10-ROSTER-OPS-2, R10-TICK-DRIVERS-2), as P363 states. R10-DEPS-ACTIONS-BUMP is a roster group.
- s6-batch106.md#P363 is ACCEPT and its carry text holds the exact-match-first, then strip -p<N> rule: the remedy P370 proposes. The DEFER reason (destination exists with this remedy) is testable and true; no new carry or group is claimed, so none is owed on the roster.
- 99835eadc exists and changes only dev/audit/rounds/round6/D11/fix/codeowners_gap.py against its merge base; 8247a1ed1 is an ancestor of origin/main.
- Mutation proof re-run: ruling_verdict reads P370 as DEFER and P371 as None; a text citing s6-batch112.md#P370 is refused "is not an ACCEPT ruling (DEFER)"; flipped to ACCEPT it reads ACCEPT with no refusal; file absent is refused as not on the roster branch or origin/main. Reproduced.
- Figures I could not re-derive: the driver4.log counts (8 NEEDS-TITLE, 88 RESULT) and the 03:24Z, 03:29:40Z log and ledger lines are session-local files outside the tree. The "fourth part topic" count follows from P363's three plus this one, which I did confirm in batch106.
- ## Head names the head and the authored code head a8082eec9; ## Red checks says none; the whole check-run set (45 runs, one page) at the head shows no red conclusion. pr-contract success. merge_train classify: GREEN 60279abb4d3160ed64fd0a2fe73c4c6c3fbeed86 pending: none red: none (rc 0).
- carry_audit at the head: 0 finding items.
