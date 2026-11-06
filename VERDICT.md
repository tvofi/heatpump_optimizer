Fix review: blocked 08d62371ac0d8170ab74042b254f3b961d26fdfc figures-uncited: the record's figures are carried, not cited; their scripts and raw JSON stay outside the tree and the git-derivable ones do not re-derive

bus-nonce: 45ac99f93011ca0f1552e72b79abdbe2

## Block

First round. Reviewed from a detached worktree at 08d62371ac0d8170ab74042b254f3b961d26fdfc, under fix-review.md and proposal-triage.md. The role files match main: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

proposal-triage.md requires `Instances:` with "each figure beside its command or log: cite, don't carry". Check 2 of the brief asks for the command at a pushed ref. `dev/programme/triage/s6-batch126.md` describes how the figures were taken: API endpoints, windows, and a definition of "PRs". It then says: "The two listing scripts and the raw JSON are kept in the seat's folder, outside the tree." So no figure in either ruling can be re-run from a pushed ref. That covers the 294 runner hours and 220-run sample, every lane share and mean, every "PRs" count, the 25 % total, the token table (5.27 M, 71.5 M, 1.92 G, 8.6/12.0/7.2 %), and the roster tallies (382 entries; 233/93/55/1; 247 carries; 56/58/5/57/71).

fix-review.md step 9: an instrument whose copy lived out of tree "is named, and lands". It has not landed.

Some figures can be re-derived from git alone. I counted them over `git log --since=2026-10-29` at merge base b88684a2 (ev/rederive.txt). My definition is my own, because the record gives none. None of them matches:
- `ci: pin killed`: record 18, re-derived 27. This changes the "nearest case": 27/228 is 11.8 %, not 7.9 %.
- `ci: record delivery`: record 46, re-derived 52.
- `ci: record nightly`: record 12, re-derived 14.
- `ci: re`: record 3. `ci: re-record closures` re-derives as 7, and the bare prefix `ci: re` also matches the record commits.
- PRs merged since 2026-10-29: record 228, re-derived 239 PR numbers on main's first parent. 228 is the denominator of every 5 % test ("5 % of 228 is 12").

The windows may differ, since the record's main and mine are not named. That is the point: without the command at a ref, the discrepancy cannot be settled either way. Both rulings are DEFERs that rest on these numbers ("under 12 pull requests at the upper bound"), so the ruling is not yet standing on measurement.

To clear the block, land the two listing scripts in the tree, either under `tools/audit/seat/` per decision 0013 or as a committed harness. Cite each figure as the command and ref that produce it, and correct the git-derivable counts. Token figures from local transcripts cannot be reproduced by another seat: say so beside each one, and give the command and window.

## Findings

- Figures carried, not cited: listing scripts and raw JSON are kept out of tree, and five git-derivable counts do not re-derive (18/27, 46/52, 12/14, 3/7, 228/239). The P391 `mutation-pins` "nearest case" moves from 7.9 % to 11.8 % under my count. Carry: R10-TRIAGE-S6
- The body's opening says "the diff is one markdown file under `dev/programme/triage/`". The three-dot diff is two files; it also adds `dev/programme/delivery/3238.md`. Red checks also reasons "A ref with no pull request has no checks", but this head has a PR and 68 check-runs. The conclusion `none` is correct; the stated reason is not. Carry: R10-TRIAGE-S6
- Two commits on the branch, 34ee0cc0 (merge of main) and 08d62371 (delivery row), are authored `tvofi`. The record itself lists "body commits under the owner's name" as a corrected slip, and CLAUDE.md (decision 0011) has the hpo-author App author. `pr-contract` passed at this head, so this is noted, not blocked. Carry: R10-TRIAGE-S6

## Evidence

- Head reviewed: 08d62371ac0d8170ab74042b254f3b961d26fdfc (ev/HEAD.txt). It is the PR head at read time and the body's `## Head` names it.
- Check 1, cites: base b88684a2, dad3178d, c1dd4a51 and 15b2376f all resolve on origin. `tools/ci/prelude.py` `UNITS` agrees with the record's "req" column for all nine lanes in the first table (ev/prelude-units.txt). `dev/governance/config/machinery_budgets.json` `exemptions` is `[]` at the head, as the record says. The roster group R10-TRIAGE-S6 exists on origin/handoff/audit-r10-roster at 0a462125.
- Check 2: no figure carries a command at a pushed ref (see Block). I could not reproduce the CI-API figures, the token figures or the roster tallies. My own definitions for the git-derivable counts are in ev/rederive.txt.
- Check 3: both rulings are DEFER. Each records why ("unmeasured does not pass") and what would change it (an owner decision, or a measured benefit), as proposal-triage.md requires. There is no ACCEPT, so no destination is owed.
- Check 4: I found no contradiction with an owner ruling. Both DEFERs go to the owner through the orchestrator, not to round 11. P391 repeats the owner's 2026-11-01 ruling against routing as CI capacity, and the record cites 2026-11-04 for ci-ratchet.
- Check 5: `dev/programme/delivery/3238.md` is in the three-dot diff. Body `## Red checks`: `none`. I read all 68 check-runs of the head on one page of 100: 0 failure, 0 cancelled. The packet digest is green.
- Mutation proof (ev/mutation.txt): `roster_edit.ruling_verdict` reads DEFER, DEFER and None for P391, P392 and P393. Flipping P391's verdict line to ACCEPT makes it read ACCEPT, so the body's mutation claim holds.
- CI: `merge_train.py classify 08d62371ac0d8170ab74042b254f3b961d26fdfc --pr 3238` printed `GREEN 08d62371ac0d8170ab74042b254f3b961d26fdfc pending: none red: none` with rc=0 (ev/classify.txt).
- Merge: `git merge-tree --write-tree origin/main 08d62371ac0d8170ab74042b254f3b961d26fdfc` exits rc=0 against origin/main 9315526f (ev/merge-tree.txt).
- VERSION, the manifest version and the release-notes heading are untouched; the diff is two markdown files.
- Review packet: no refusals and no advisories. figure_lint: 1 not verified (the body's `git diff --stat`, which I re-ran: 1 file, 95 insertions at c1dd4a51). Saved as ev/review-packet.md.
