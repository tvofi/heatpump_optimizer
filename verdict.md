Fix review: merge b293f317913042a0c7c3b40dc7e0df81c97923ef

bus-nonce: 5b4285ac7689bbb555a23b49b9b92b22

Round 1 (first round, full scope). Head measured: b293f317913042a0c7c3b40dc7e0df81c97923ef (re-read before posting). Record-only PR: no production, test or instrument code, so no mutation proof (the body says n/a, and the diff confirms it).

## Evidence

- RESULT roster: every changed line of dev/programme/rosters/wave-r10-groups.json at the head, against the roster branch tip f8d3342d50d1651c197d8e157bbfa8ce3daab302, differs only by inserted `archive/` prefixes (422 hunks, 0 beyond archive; ev/roster_archive_only_check.py compares each hunk with every `archive/` removed from both sides). The head holds 584 `archive/` strings against the tip's 22. Against main the head's roster is the branch's own edits plus those prefixes. wave-r9-groups.json is not in the three-dot diff (main already carries it).
- RESULT null control: keyed on `group`, main and head both hold 544 groups, 0 added, 0 removed, 11 differ; re-derived, matches the body.
- RESULT DROPPED line: R11-INTAKE-R10-RESIDUE.carry is 175 entries on main, 183 at the head; carries 66 and 72 are equal at the head and on main, and both hold `archive/`. The DROPPED print is field granularity, as the body says.
- RESULT state docs: `state_docs.py --roster-ref origin/handoff/audit-r10-roster --mirror dev/programme/round10/state` re-run in a detached worktree at the head leaves all four files byte-identical (git diff empty). Caveat: resume_doc needs an open-PR list and gh GraphQL is refused here, so the `--pr-state` input was the PR table of the committed RESUME-CURRENT itself. That proves the render is a pure function of the roster and that table; it does not check the table against live PRs.
- RESULT paths: three-dot diff touches exactly the roster, the four state docs, HANDOVER.md and delivery/3604.md. VERSION, the manifest and RELEASE_NOTES are untouched. No claim, budget or closures file moved.
- RESULT handover (14 facts checked): updated-for 29b3e5a74c is an ancestor of the head; #3601 merged as 29b3e5a74c; #3575 as 4eea986a62; #3600 as 2a257fce08 (merged 2026-11-15T00:52Z); #3553 as a72ae19952 and dev/programme/carries holds only carry-1645, so the five others are gone; 16e8fef927 exists; corpus_tokens 68618 to 69333 across #3575 (policy_budgets.json); decision 0018 and roles/evaluator.md exist; probes rev-3599-a6c8a024 (94f29ddb) and rev-3599-21c42d32 (996b06f9) exist; #3599 is open at head b58c6ca368; #3491, #3451, #3602, #3598, #3593 are open; handoff/r10-draw-map-evidence-b is at 8c1508d9c1; handoff/r10-arch-docs-delta tip was committed 2026-11-14 17:29Z; the shas aeb5f761cb, e3df1f1ca6, 76aca12e6f, 75d6b5fe82 and e698502972 resolve. I did not verify the handover's verdict wording on those SHAs (verdict refs are out of reach here).
- RESULT merge: `git merge-tree --write-tree origin/main b293f317913042a0c7c3b40dc7e0df81c97923ef` rc 0, no conflict.
- RESULT CI: `merge_train.py classify` prints `GREEN b293f317913042a0c7c3b40dc7e0df81c97923ef pending: none red: none`. The only reds in the digest are governance / delivery-status and tests / nightly-status, which grade main and are outside the owed-reds set (neither is listed).
- RESULT carry audit: carry_audit at the head, 1 item, routed to R11-INTAKE-R10-RESIDUE (the prune_refs tip_ages forward-carry); that group exists in the roster at the head.
- Not re-derived: the body's `cited bare` counts (286 to 0) and the closeout dry pass lines. Those need the closeout run over every fetched head and the out-of-tree runbook scripts (retarget.py, main_archive_lines.py). The shipped roster is, however, shown to be the branch blob plus prefixes only, which is the thing those passes were to produce. Not re-run: the closeout dry plan.
- Round 1; no prior findings.
- The body's forward-carry on prune_refs tip_ages (exit 128 on one missing sha) is landed in R11-INTAKE-R10-RESIDUE by this PR's roster; I did not reproduce the exit-128 claim, so it stands as the body's unverified measurement.

## Findings

none
