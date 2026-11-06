Fix review: blocked f02530f49181dd4ff43ff214aad884b1b3fbb17a figures-uncited: the ruling still carries its arm table, marker cost and calibration figures at four commits that do not exist on origin

bus-nonce: 704bb9ec05b50744d349366e0ccde6c3

## Block
- `git cat-file -t` after fetching origin (ev/cat-file.txt): `d8eeae8f8` and `88697cf19` are commits; `4fff42664`, `39143c38f`, `e1ee044cc` and `77af298ef` are "Not a valid object name". The delta added three more unresolvable SHAs (`39143c38f`, `e1ee044cc`, `77af298ef`) beside the original `4fff42664`, so it moved the figures from one unpushed commit to several.
- The arm table (R 1.03 to 7.70) is now sourced to "`r10_sav_wood_reference.py` at `39143c38f`, as the fix seat reported them" and the paragraph says "The figures are the seat's, not re-run here". That is carrying, which proposal-triage.md rules out ("cite, don't carry"). No command sits beside any arm figure, and none can be re-run, because the tree is not on origin.
- The marker cost (+44 -8, +3 -1, +14 -2) and the "metered half the plan gives 50.0 %" finding are still stated at `4fff42664`. The ruling does answer the finding, but its answer ("driven at its checkout `77af298ef`, 50, 75, 87.5 %") is also at an unpushed commit.
- The hotfix carry was not restated against what is pushed. At `88697cf19` (ev/ledger-88697cf19.txt), `savings_months(now, *, wood_configured)` already floors calibration with `max(1.0, calibration)` when wood is configured. The ruling says "answered" but cites `77af298ef` and not `88697cf19`, so a reader cannot resolve it. The carry on R10-HOTFIX-SAV-ESTIMATE still describes the pre-fix behaviour at `4fff42664` and was not restated.
- Check (1) of the brief fails, so checks (2) and (3) fail with it. To clear: re-take the arm table, the marker cost and the calibration drive at pushed refs (`88697cf19`, `d8eeae8f8`, or main at `7d95405e3`, which carries the merged hotfix #3220). Put each command beside its figure, and name the commit each finding is about. Drop "the figures are the seat's" in favour of figures this seat can re-run. Restate the hotfix carry against the wood floor now on main.

## Findings
- Residual (first verdict, still unanswered): the floor's benefit is about 1.1 h per release and it catches 1 of 3 measured instances. The ruling still carries both, now without a resolvable source. Carry: R10-RCA-SAV-ESTIMATE
- Residual (first verdict, still open): R10-SAV-METER-FLOOR is named as a new group, but it is not in any roster yet. Carry: R10-TRIAGE-S6

## Evidence
- Head reviewed: f02530f49181dd4ff43ff214aad884b1b3fbb17a (ev/HEAD.txt).
- Merge with origin/main: `git merge-tree --write-tree` exited with a tree and no conflict (ev/merge-tree.txt).
- merge_train classify: GREEN, pending none, red none (ev/classify.txt). governance/delivery-status and tests/nightly-status show failure in the packet digest; classify does not treat them as red for this head. I did not read their logs.
- carry_audit at the head: 0 finding items, none unrouted. figure_lint: 0 resolved, 1 not verified (the three-dot diff stat in the PR body).
- No mutation or harness applies: the PR changes ruling text only.
