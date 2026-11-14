Fix review: merge aeb5f761cb62840ec481d9cb4df97bebadcbafbb

bus-nonce: 3baf5e50ca947d9632c995b02acca393

## Scope

This is round 4. It is a delta review at the same code head aeb5f761cb62840ec481d9cb4df97bebadcbafbb as round 3's blocked verdict. `git diff aeb5f761 aeb5f761` is empty, so the only delta is the PR body. It touches no line under custom_components/, so the review does not widen (fix-review.md step 12). Per the brief, everything round 3 resolved stands, and the code is not re-reviewed. Under "Say which round this is": this is the fourth round, so fixer.md's re-cut clause is reached. This round exists only because the carry was outside the fixer's power, and the code was settled at round 3. The orchestrator decides whether a re-cut is owed.

## Round-3 block item 0: resolved

- The PR body now names the roster SHA. `## Head` says "the carry of carry-201 entry 22, second half, is on the roster branch at db1943958e3cde237393ad8493bd3bd577e7f9c5". `## Forward-carry` says "Folded: ... in the `carry` list of R11-INTAKE-R10-RESIDUE on origin/handoff/audit-r10-roster at db1943958e3cde237393ad8493bd3bd577e7f9c5" and quotes the appended text. The "FOR THE ORCHESTRATOR TO FOLD" placeholder is gone.
- One roster read at db1943958e: the commit's subject is "roster_edit append-carry R11-INTAKE-R10-RESIDUE (carry-201 entry 22 second half, #3553 fix-review round 3)". It is an ancestor of origin/handoff/audit-r10-roster, whose tip is now 00e3c2f8c0. In dev/programme/rosters/wave-r10-groups.json, R11-INTAKE-R10-RESIDUE (resume.stage not-started, so live) has 175 carry items. Item 174 is the only item in the file matching `window_work_minutes|timing-inferred|QUEUE_EPS` (file-wide count 1; ev/roster_e22b.txt). Its text equals the body's quoted text.
- The carry states its control as a precondition (finding-propagation.md): "Keep only edges to the workflow's declared needs:". It also gives a re-measurement instruction: "re-measure it at your merge base with dev/audit/harnesses/r10_hotfix_ci_critpath_4/replay.py section 6". That harness path exists on origin/main and at db1943958e.

## Findings

- Follow-up: the roster carry item as appended has no trailing `Carry:` marker, while its neighbours have one. It already sits inside its destination group's own carry list, so a marker would only restate where it is. Carry: dismissed: the item is in its destination; nothing to route

## Evidence

- RESULT head-measured: aeb5f761cb62840ec481d9cb4df97bebadcbafbb. refs/pull/3553/head reads the same SHA at review time, and the body's head line names it (ev/HEAD.txt).
- RESULT delta: `git diff aeb5f761cb62840ec481d9cb4df97bebadcbafbb aeb5f761cb62840ec481d9cb4df97bebadcbafbb` is empty. The delta is the body only.
- RESULT roster-carry: db1943958e3cde237393ad8493bd3bd577e7f9c5 R11-INTAKE-R10-RESIDUE carry[174] matches window_work_minutes / timing-inferred / QUEUE_EPS. The file has 1 match (ev/roster_e22b.txt; diff from 05188a4777 in ev/roster_delta.diff).
- RESULT carry-audit: the packet's carry_audit at the head reports `CARRY-AUDIT: 33 finding item(s): 33 routed, 0 unrouted, 0 bad destination(s)`. I ran the closing self-audit over this verdict as the comment, with a stub body because this seat has no gh to fetch the body file; the body's 33 items are the packet's run above. It printed `1 routed, 0 unrouted, 0 bad destination(s)`, rc 0 (ev/carry_audit_self.txt).
- RESULT merge-tree: `git merge-tree --write-tree origin/main aeb5f761` gives rc 0 against origin/main 6abf88e617 (ev/merge_tree.txt).
- RESULT policy-drift: `git diff merge-base...origin/main -- dev/governance/roles/` adds only the two outside-contributor bullets (decision 0017) to fix-review.md. They do not bear on this in-house review (ev/role_drift.diff).
- RESULT owed-reds: the set is in ev/owed_reds.txt. `tests / nightly-status` reads failure in the packet digest and is outside the set, so it is not this PR's and blocks nothing.
- RESULT CI: `merge_train.py classify aeb5f761... --pr 3553` printed WAIT (`pending: gate red: none`) from 23:27Z on, then `GREEN aeb5f761cb62840ec481d9cb4df97bebadcbafbb pending: none red: none`, rc 0, at 2026-11-14T23:36:12Z (ev/classify_log.txt). No required check is red, so no `## Red checks` answer is owed at this head beyond the body's existing ones.
