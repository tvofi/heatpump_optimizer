Fix review: merge 21e87f79c0baca0a1afce61703ad54d8d0467849

bus-nonce: 3e7074227a5143dccf58976771567316

Round 3. Round 1 was `blocked e3a6f0729 null-control-false` (comment 6253163400), and round 2 was `merge 928a6727` (comment 6255476299). This round reviews a delta and is not a re-cut. I measured head 21e87f79c0baca0a1afce61703ad54d8d0467849. `git ls-remote` still showed it as refs/pull/2408/head after CI concluded. Merge base and origin/main are both 06c6f3cf2. The contract is current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.

## Delta since 928a6727 (resolution delta)

- This PR's own three-dot diff is unchanged in content between 928a6727 and this head. Only hunk offsets in `policy_lint.mjs` moved (`ev/pr_diff_delta_928a6727_vs_head.txt`). The 17+/4- in `policy_lint.mjs` between the two heads comes from main's #2423, not from this PR.
- Trees: 21e87f79, 0fd1f3e4 and `git merge-tree --write-tree 06c6f3cf2 357fe0fca` all give tree 40fb19fd78d7. So the resolution delta is empty, and the tree matches the body's `40fb19fd78d7`.
- `git merge-tree --write-tree origin/main HEAD` exits 0 with tree 40fb19fd78d7. There is no conflict and no MERGE-CLAIM line (`ev/merge_tree.txt`).
- Advisory, body `## Head` wording: the body calls 0fd1f3e4 a merge of 06c6f3cf2 "into the previous handoff head 357fe0fca". Its first parent is actually 928a6727, which already contains 357fe0fca. The tree is identical either way, and the body names the measured head.

## RESULT lines (at the head)

- RESULT policy_lint: `TOTAL: 0 error(s) across 41 policy file(s)`, `FIXTURE ok: 92 error(s) hold 246 pins across 12 check classes`, rc=0. Matches the body.
- RESULT budgets: finding-propagation 100/101 lines and 1336/1336 tokens; orchestrator.md 319/319 and 4513/4513; fix-review.md 140/140 and 2451/2451; corpus ~61137 (cap 61026 + band 500). Matches the body. No cap is raised.
- RESULT rules_sync --check: `RULES-SYNC ok`. brief_lint: `CARRY ok`, rc=0. policy_lint_mutants: `MUTANTS ok`, with ruleBindingOverTree in the corpus list. structure.py: `STRUCTURE RATCHET PASSED`.
- RESULT agreement: `RESULT divergent=0 unregistered=0 dead=0 refused=0`. delivery_status --check: `DELIVERY STATUS OK — 138 rowed, 2 pending, 0 overdue`. entities.py: `ALL 2349 ENTITY CHECKS PASSED`. All three match the body.
- RESULT closure select: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. Matches the body.
- RESULT mutation proof (my own runs, restored each time, `git status` clean afterwards; logs in `ev/M*.log`):
  - M1, `.claude/workflows/*.json` deleted from the head's globs: rc=1, TOTAL 2. The arm names wave-3l-groups and carry-1921. Matches the body.
  - M2, the two added globs deleted: rc=1, TOTAL 10. Matches the body.
  - M3, the arm's predicate made dead: rc=1, `FIXTURE VACUOUS ... 'unbound carry home' arm produced []`. Killed.
  - M4, the archive and fixture exclusion deleted: rc=1, TOTAL 47 with `FIXTURE OVER-FIRES`. Matches the body.
  - M5 (mine), `locate()` replaced by raw `tracked`: rc=1, TOTAL 5 on the real tree, from the old-spelling fixture carries. No acceptance model pins this. The body discloses that under Unpinned sites.
- RESULT class seams: the body's rule returns 59 files. 12 are live (2 in .claude/workflows, 2 in dev/programme/rosters, 8 in dev/programme/carries), 42 are under dev/archive and 5 are linter fixtures. All live files are bound, and no seam is open (`ev/class_seams.txt`).
- RESULT VERSION, manifest, RELEASE_NOTES.md and tests/golden: untouched (three-dot).

## CI and step 11

- At this head, all 48 check runs concluded success, skipped or neutral (CodeQL), with no failure (`ev/check_runs.txt`). Both pr-contract runs succeeded after the 02:31:39 body edit.
- Range: 0fd1f3e4 has no check runs. 928a6727 was red on `wave-script` and `delivery-status`. The body's `## Red checks` names both and answers both: inherited from main, cleared by #2423/#2424 and the record merges, and no cheaper detector exists for wave-script. delivery-status is not this PR's, because the diff's only delivery file is its own row.

## Step 10, forward-carry

- The body says `Forward-carry: none`. That is consistent, because the PR is itself the rule text.
- The owed `--record-known-bad` pin under Unpinned sites is nonetheless carried, on roster branch `handoff/audit-r10-roster` at 73bb15fe8f5b. It went to R10-POLICY-LINT-FAMILY, which is `not-started` and therefore a live destination. It states the control and a sequencing precondition (start after #2406/#2408 merge). It was not carried to R10-TICK-DRIVERS, which merged as #2390 and is done (`ev/carry_roster_73bb15fe.txt`).

## Not re-derived, and no harness

- Steps 2, 3 and 9: this is a policy PR from an owner-accepted pre-study, and it has no finder's harness. The instruments are the policy lints above.
- I did not re-derive the pre-study figures (14 PRs, median 49 min, 54.1 runner-min), and neither did the body.

## Advisory (not blocking)

- Carried from rounds 1 and 2: fix-review.md step 10 fuses "carrying the control" and "stated as a precondition".
- Owner gate: this is policy, so tvofi's approval is owed before merge. The body says so.
