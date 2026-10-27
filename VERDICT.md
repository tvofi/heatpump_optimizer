Fix review: blocked 340b3298ac6645883fecf1d5aefe08132735db62 delivery-row-stale: `dev/programme/delivery/2878.md` still names `(R10-ORCH-ROSTER)`, a group no roster carries, while `roster_lib.group_for_branch("fix/audit-r10-roster-pr")` answers `R10-ROSTER-BATCH24`; the body records the contradiction as `## Friction` and a carry instead of correcting the one-line suffix, so `record_row` and the row disagree. Round 4: `fixer.md` owes a re-cut, not a repair.
bus-nonce: 2ba1b589f7caf0d71b0ac99f7231bc33

## Head

Reviewed `340b3298ac6645883fecf1d5aefe08132735db62` from a detached worktree at that SHA (`~/hpo-seats/r10s6/review-2878-r4`); `git rev-parse HEAD` and `gh pr view 2878 --json headRefOid` both answer it. `origin/main` is `a0e7664ea`, `git merge-base origin/main HEAD` is `6eb552157`. The head did not move. Round 3 blocked `b0920b94a`; this is round 4.

The worktree's `dev/governance/roles/fix-review.md` is three editorial lines behind the live contract (`git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is non-empty for that file only); the live copy was read instead, and it changes no rule this verdict turns on.

Three-dot, as the brief requires: `git diff --numstat $(git merge-base origin/main HEAD)...HEAD` is `1 0 dev/programme/delivery/2878.md` and `259 49 dev/programme/rosters/wave-r10-groups.json` — exactly two files. `git log --no-merges --format=%H origin/main..HEAD | wc -l` is 76, the number the body states.

## B1 — the body is this pull request's own

RESULT b1-body-is-own: PASS — `diff` of this body against `gh pr view 2866 --json body` is one hunk, 157 lines removed and 33 added. Everything round 3 named as carried over is gone: #2866's `### The ops, oldest first, by kind` list, its 95-commit enumeration over `6fe5170..1e9180dc9`, its five-row `**open**` flip and its #2866 record beat. Every section the body now states describes #2878: `## Head` pins this head and its two merged inputs; the record beat names `b0920b94a`, whose `git show --stat` is one file, one insertion, `dev/programme/delivery/2878.md`; `## Null control` names this PR's two files; `## Forward-carry` is `none`; `## Friction` is this PR's own row. Carry: R10-ROSTER-BATCH24

## B2 — every figure re-derives at the SHA the body pins

| claim | stated | measured | command |
|---|---|---|---|
| group-diff at this head | `208 212 4 25` | `208 212 4 25` | the body's python one-liner, `origin/main HEAD` |
| group-diff at the roster ref | `208 212 4 33` | `208 212 4 33` at `2b1fefed1`; `208 212 4 34` at the live ref | same, ref vs `2b1fefed1` |
| numstat `origin/main...b0920b94a` | `1 0`, `29 20` | `1 0`, `29 20` | `git diff --numstat` |
| numstat at the roster ref | `259 49` | `259 49` at `2b1fefed1`; `262 52` live | `git diff --numstat origin/main...<ref>` |
| no-merge commits over main at HEAD | 76 | 76 | `git log --no-merges --format=%H origin/main..HEAD \| wc -l` |
| roster-ref no-merge count | 75 at tip `2b1fefed1` | 75 at `2b1fefed1`; 77 live | `git rev-list --count --no-merges origin/main..<ref>` |
| merged-tree roster blob | `eb7252e2e` | `eb7252e2e` (`git rev-parse HEAD:…`) | `git rev-parse` |
| roster tip blob | `c20ee1a87` | `c20ee1a87` at `2b1fefed1`; `1bc4b9446` live | `git rev-parse <ref>:…` |
| this PR's own commits | 27 | 27 | `git rev-list --count --no-merges origin/main..b0920b94a` |
| roster tip "adds 49 more" | 49 | 49 (75 − 26 common) | `comm -12` of the two sets |
| union over main | 76 | 76, and HEAD's 76 are exactly that union | the body's `sort -u \| wc -l` |
| nine groups the PR's own commits change | 9 | 9 against `524c1896b`; 17 against the live merge base `6eb552157` | the group-diff one-liner |
| thirteen gain carries / twelve move resume / 25 change | 13 / 12 / 25 | 13 / 12 disjoint / 25 | group-dict comparison |
| `size: XS` | 0 main, 8 roster ref, 8 at `524c1896b` | 0 / 8 / 8 | the body's `grep -c` |
| `Triage P199\|P200\|P203` | 3, 3 | 3, 3 | the body's `grep -c` |
| check-runs at `b0920b94a` | `{"skipped":19,"success":36}` | `{"skipped":19,"success":36}` | the body's `gh api` rollup |
| `brief_lint` | `TOTAL: 0 error(s)` | `TOTAL: 0 error(s) across 1 file(s)` | `node tools/policy/brief_lint.mjs` |
| `roster_sync --self-test` | `64 checks, 0 failed` | `64 checks, 0 failed` | `env -u BASH_ENV python3 -I … --self-test` |

RESULT b2-figures: PASS — every value reproduces at the SHA the body names. Two labels have aged and are named rather than inferred: the body calls `524c1896b` "the merge base" and it is now only an ancestor of main (the live merge base is `6eb552157`), and its four live-ref spellings of `origin/handoff/audit-r10-roster` now print the newer values in the table because that ref took two commits after this head was cut. Carry: R10-ROSTER-BATCH24

## B3 — Forward-carry orders nothing already carried

RESULT b3-forward-carry: PASS — `## Forward-carry` is `none`, so no `append-carry` op is ordered and no op can duplicate a carried one. The superset check the brief also asks for is clean: the head loses 0 groups, 0 carries, 0 issues, 0 `after` edges and 0 resume keys against `origin/main`. P199/P200/P203 are already carried in the head roster, at `R10-FLOW-WIP` / `R10-ORCH-REVIEW-PACKET` / `R10-ORCH-ROSTER-SCHEMA`. Carry: R10-ROSTER-BATCH24

## B4 — the row's group name is still dead, and that is the block

The head row reads `- [#2878](https://github.com/tvofi/heatpump_optimizer/pull/2878) — **open**, roster: round-10 batch 24 (R10-ORCH-ROSTER)`. `R10-ORCH-ROSTER` is absent from all three rosters measured — main, this head and `origin/handoff/audit-r10-roster` — while `R10-ROSTER-BATCH24` is present in this head and in the roster branch. `roster_lib.group_for_branch(head_roster, "fix/audit-r10-roster-pr")` answers `R10-ROSTER-BATCH24`, and that is the name both `record_row.py` (which calls `group_for_branch`) and `open_pr.sh`'s `$G` are supposed to write, so the generator and the row disagree. The body records the contradiction in `## Friction` with `Carry: R10-ROSTER-BATCH24` and leaves the suffix wrong; `brief_lint` and `pr-contract` both pass on it, so nothing else will catch it. A one-line edit in this PR's own record commit fixes it; carrying it forward does not.

RESULT b4-row-group: FAIL — row names `(R10-ORCH-ROSTER)`; absent from main's, the head's and the roster branch's rosters; `record_row`'s rule answers `R10-ROSTER-BATCH24`. Carry: R10-ROSTER-BATCH24

## B5, B6 — the self-test and the red check

RESULT b5-self-test: PASS — `env -u BASH_ENV python3 -I tools/audit/seat/roster_sync.py --self-test` prints `roster_sync self-test: 64 checks, 0 failed`, exit 0. The head's own `governance / instrument-self-tests` run concluded success at 19:40:35Z, so the check the round-3 block named is green on this tree. Carry: R10-ROSTER-BATCH24

RESULT b6-red-check: PASS — `gh api repos/tvofi/heatpump_optimizer/commits/1dbf3f674/check-runs` carries `governance / instrument-self-tests` with conclusion `failure` (run 122390395354, started 18:37:33Z), so the red the body answers is real at that SHA. The answer is the one `defect-root-cause.md` accepts: it names the cheaper detector, `python3 -I tools/audit/seat/roster_sync.py --self-test`, with its standing cost (~16 s per roster-touching push), and records that wiring it into `prepr.sh` is a `prepr.sh` change this roster-data PR does not carry. Carry: R10-ROSTER-BATCH24

## Settled: the head is 2 commits behind the roster ref, and that is neutral

`git rev-list --count HEAD..origin/handoff/audit-r10-roster` is 2. The commits are `7322d0deb set-stage R10-PREPR-CAP` (to `fixing`) and `8f7e252fe set-stage R10-ORCH-REVIEW-PACKET` (to `done`); both are timestamped 20:29:34 and 20:35:59, after this head's 20:16:16, so the head could not have carried them. Neither is state this PR takes away from main: main and this head both read `R10-PREPR-CAP` `done` and `R10-ORCH-REVIEW-PACKET` `in-progress`, and `git diff origin/main HEAD -- dev/programme/rosters/wave-r10-groups.json` has no line for either group. Merging this PR therefore regresses nothing and closes nothing falsely; the two ops stay on the branch and land at the next stamp. Not a block — but a re-cut must re-take the four live-ref figures in the B2 table.

RESULT roster-ref-behind: PASS as a measurement — 2 commits, both postdating the head, neither changing a group this diff touches. Carry: R10-ROSTER-BATCH24

## Checks and instruments

The head's rollup is `{"skipped":19,"success":36}` with 0 failures, and `pr-contract / pr-contract` concluded `success` at 19:45:43Z–19:46:57Z, after the last push — so the body's own contract check has read the body it is being judged on. `git merge-tree --write-tree origin/main HEAD` exits 0 with tree `399d62c3c` (no conflict; `mergeStateStatus: BLOCKED` is the review requirement, not a dirty tree). `VERSION`, the manifest, `RELEASE_NOTES.md`, both claim files and every `*_budgets.json` are absent from the diff, so steps 4, 5 and 14 have nothing to measure. Roster data only: no production line is added, so the mutation proof is correctly `n/a` and there is no enumeration-rule class to open. `python3 tools/audit/carry_audit.py pr 2878` prints `1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`.

## Not established

Nothing material. I did not re-run `prepr.sh`, per the brief, and did not independently verify the `## Head` claim that the two merges were "an automatic merge by the orchestrator's script" beyond `merge-tree` finding them conflict-free; the merged tree is the pushed head, whose blob `eb7252e2e` matches the body.
