Fix review: merge 5c73750010e6b8836728268bba47c969eb4be90f
bus-nonce: d0cb5f7bf2896b9504ac1e4248e2c9a1

## Head

Reviewed `5c73750010e6b8836728268bba47c969eb4be90f` from a detached worktree at that SHA
(`~/hpo-seats/r10s6/review-2878-r4/`); `git rev-parse HEAD` and `gh pr view 2878 --json headRefOid`
both answer it. `origin/main` is `a0e7664ea`, `git merge-base origin/main HEAD` is `a0e7664ea` (this
head merges it). The head did not move under the review. `5c7375001`'s parents are `6bab7c4cb` and
`a0e7664ea`, as the body states. The worktree's `dev/governance/roles/` is identical to `origin/main`'s
(`git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty), so the
live contract was read. This is round 4 in the brief's numbering; the confirmed `verdict/2878` history
holds two blocked verdicts (`b0920b94` body-stale, `340b3298` delivery-row-stale) and this head is the
re-push that answers both. `bus.sh`'s enforced three-round counter reads `verdict/2878`, which is below
three, so no `## Re-cut` note is owed at this dispatch.
Carry: R10-ROSTER-BATCH24

## B1 — the body is this pull request's own

`diff` of this body against `gh pr view 2866 --json body` is **one hunk, 155 content lines removed and
33 added**; the only lines shared with #2866 are the seven headings `## Head`, `## Mutation proof`,
`## Null control`, `## Figures`, `## Red checks`, `## Forward-carry`, `## Friction` that
`.github/PULL_REQUEST_TEMPLATE.md` requires. Every section content line is #2878's: its own three
commits in `## Head` (`b0920b94a` adds its row, `6bab7c4cb` corrects it, `5c7375001` merges main), its
own record beat (`b0920b94a` is one file, one insertion, `dev/programme/delivery/2878.md`), its own
null control (this PR's two files), `## Forward-carry` `none`, `## Friction` `none`. #2866's 95-commit
enumeration, its five-row flip and its Forward-carry ordering of P199/P200/P203 are all absent.
Carry: R10-ROSTER-BATCH24

## B2 — every figure re-derives at this head

| claim | stated | measured | command |
|---|---|---|---|
| no-merge commits over main at HEAD | 77 | 77 | `git log --no-merges --format=%H origin/main..HEAD \| wc -l` |
| at `b0920b94a` | 27 | 27 | `git rev-list --count --no-merges origin/main..b0920b94a` |
| at roster tip `2b1fefed1` | 75 | 75 | `git rev-list --count --no-merges origin/main..2b1fefed1` |
| union over main | 76 (27+75−26) | 76; common = 26 | `{…} \| sort -u \| wc -l`; `comm -12` |
| roster tip "adds 49 more" | 49 | 49 | 75 − 26 |
| numstat `origin/main...b0920b94a` | `1 0`, `29 20` | `1 0`, `29 20` | `git diff --numstat` |
| numstat `origin/main...2b1fefed1` | `259 49` | `259 49` | `git diff --numstat` |
| three-dot numstat at this head | two files | `1 0` delivery/2878.md, `259 49` roster | `git diff --numstat $(git merge-base origin/main HEAD)...HEAD` |
| group-diff at HEAD | `208 212 4 25` | `208 212 4 25` | the body's python one-liner, `origin/main HEAD` |
| group-diff at `2b1fefed1` | `208 212 4 33` | `208 212 4 33` | same, `origin/main 2b1fefed1` |
| nine groups vs `524c1896b` | 9 | 9 (exactly the nine named) | group-dict diff `524c1896b` vs `a9c7555ad` |
| thirteen gain carries / twelve move resume / 25 change | 13 / 12 / 25 | 13 / 12 / 25 | group-dict `origin/main` vs `HEAD` |
| merged-tree roster blob | `eb7252e2e` | `eb7252e2e` = `HEAD:…` | `git rev-parse HEAD:…` |
| roster tip blob | `c20ee1a87` | `c20ee1a87` at `2b1fefed1` | `git rev-parse 2b1fefed1:…` |
| live ref tip blob | `1bc4b9446` | `1bc4b9446` at `8f7e252fe` | `git rev-parse refs/…:…` |
| main roster blob | `582f75be3` | `582f75be3` | `git show origin/main:… \| git hash-object --stdin` |
| `size: XS` | 0 main, 8 ref, 8 at `524c1896b` | 0 / 8 / 8 | the body's `grep -c` |
| `Triage P199\|P200\|P203` | 3, 3 | 3, 3 | the body's `grep -c` |
| check-runs at `b0920b94a` | `{"skipped":19,"success":36}` | `{"skipped":19,"success":36}` | the body's `gh api` rollup |
| `brief_lint` | 0 errors | `TOTAL: 0 error(s) across 1 file(s)` at main and at HEAD | `node tools/policy/brief_lint.mjs …` |
| `roster_sync --self-test` | 64 checks, 0 failed | 64 checks, 0 failed | `env -u BASH_ENV python3 -I … --self-test` |

RESULT b2-figures: PASS — every stated value reproduces at the SHA the body names. The one figure that
does not key to the live merge base is labelled as such: the "nine groups" figure is measured against
`524c1896b`, the fork point, not the live merge base `a0e7664ea`, and `524c1896b` is an ancestor of
`origin/main` and of this head. The body's `2b1fefed1` pin is honest — the live ref tip `8f7e252fe`
prints newer blobs, which the body states.
Carry: R10-ROSTER-BATCH24

## B3 — Forward-carry orders nothing already carried

`## Forward-carry` is `none`, so no op is ordered and none can duplicate a carried one. The superset
check the block also requires is clean: against `origin/main` this head loses **0 groups, 0 carries,
0 issues, 0 `after` edges and 0 top-level fields**, and P199/P200/P203 remain present in
`R10-FLOW-WIP` / `R10-ORCH-REVIEW-PACKET` / `R10-ORCH-ROSTER-SCHEMA` exactly as on main. The round-3
duplication block cannot recur.
Carry: R10-ROSTER-BATCH24

## B4 — the row's group name is now the group the roster carries

`dev/programme/delivery/2878.md` reads `… roster: round-10 batch 24 (R10-ROSTER-BATCH24)`, corrected by
`6bab7c4cb` (one line, one word). `R10-ROSTER-BATCH24` is an exact member of the head roster, of
`2b1fefed1` and of the live roster ref; `R10-ORCH-ROSTER` is an exact member of none of them (main,
head, `2b1fefed1`, live ref), and
`roster_lib.group_for_branch(head_roster, "fix/audit-r10-roster-pr")` answers `R10-ROSTER-BATCH24`, so
`record_row` and the row now agree.
Carry: R10-ROSTER-BATCH24

## B5 — the self-tests

RESULT b5-self-tests: PASS — `env -u BASH_ENV python3 -I tools/audit/seat/roster_sync.py --self-test`
prints `roster_sync self-test: 64 checks, 0 failed` (exit 0), and
`env -u BASH_ENV python3 -I tools/audit/seat/roster_edit.py --self-test` prints
`roster_edit self-test: 124 checks, 0 failed` (exit 0). The `roster_edit` self-test runs every git call
in a throwaway repository (`throwaway_git_environ`), and `git ls-remote` confirms it did not move
`origin/handoff/audit-r10-roster` (still `8f7e252fe`). Both are the `0 failed` line
`governance / instrument-self-tests` greps for (`.github/workflows/governance.yml:762`), and that check
concluded `success` at this head (`20:04:54Z` -> `20:22:35Z`).
Carry: R10-ROSTER-BATCH24

## B6 — the red check the body answers

RESULT b6-red-check: PASS — `gh api repos/tvofi/heatpump_optimizer/commits/1dbf3f674/check-runs` carries
`governance / instrument-self-tests` with `conclusion: failure` (id `122390395354`, started
18:37:33Z, completed 18:55:51Z), so the red is real at that SHA. The body's cause verifies in the tree:
at `1dbf3f674` `R10-TRAIN-OVERLAP-GRADE.resume.stage` is exactly `"done --at-sha 4db1d3e28f0dff50f6916e39d52efed0ce856d0a"`,
written by `12fd86e13` (a `roster_edit set-stage`, an ancestor of that head), and at `2b1fefed1` and
at this head it is `done`. The answer is the form `defect-root-cause.md` accepts — the cheaper detector
is the command itself, `python3 -I tools/audit/seat/roster_sync.py --self-test`, ~16 s per
roster-touching push, and wiring it into `prepr.sh` is a change this roster-data PR does not carry —
and it makes the check pass at this head, which B5 confirms. Scanning every branch head: `b0920b94a`
and `340b3298` are green (36 success, 19 skipped, no failure); `0e370d603`'s one red is
`pr-contract`, failing in `tools/ci/alert_list.py` with `http.client.IncompleteRead` (a network flake
the roster diff does not reach, and pr-contract is green at every later head); `1dbf3f674`'s five reds
are `instrument-self-tests` plus derivative ones — `pr-contract`'s own log says
`check 'governance / instrument-self-tests' is red and '## Red checks' does not name it`, and `gate`
says `FAIL pr-contract / pr-contract: failure (this run)`. So the one substantive red is the one the
body now names and answers; nothing went red that this answer does not cover.
Carry: R10-ROSTER-BATCH24

## Head versus the roster ref

`git rev-list --count HEAD..origin/handoff/audit-r10-roster` is **2**: `7322d0deb` (`R10-PREPR-CAP` ->
`fixing`) and `8f7e252fe` (`R10-ORCH-REVIEW-PACKET` -> `done`), both postdating this head. Neither is
state this PR takes away from main: main and this head both read `R10-PREPR-CAP` `done` and
`R10-ORCH-REVIEW-PACKET` `in-progress`, and this diff changes `R10-PREPR-CAP`'s `commit` line only and
`R10-ORCH-REVIEW-PACKET` not at all, so the two ref ops compose with it rather than being reverted by
it. Merging this PR therefore regresses nothing; the two ops land at the next stamp.
Carry: R10-ROSTER-BATCH24 (item bd4a24eb)

## Non-blocking notes

- The body has no `## Re-cut` note. `bus.sh`'s enforced counter reads `verdict/2878` (two blocked
  verdicts, below three) so the dispatch minted cleanly, and the body was in fact fully re-taken (B1's
  one-hunk, 155/33 diff), not patched; the prior verdict itself prescribed the one-line row edit.
  Carry: R10-ROSTER-BATCH24
- `## Red checks`'s sentence "The merged head has no rollup yet" was true at push time. The head's runs
  have since concluded and are green: `{"skipped":19,"success":36}`, zero failures, so the sentence is
  overtaken by events rather than wrong about a figure; no figure in it fails to re-derive.
  Carry: R10-ROSTER-BATCH24

## Checks and instruments

`git merge-tree --write-tree origin/main HEAD` exits 0 (tree `db8d86945`), so `mergeStateStatus:
BLOCKED` is the review requirement, not a dirty tree. The diff is two files and touches `VERSION`, the
manifest, `RELEASE_NOTES.md`, both claim files and every `*_budgets.json` not at all, so steps 4, 5 and
14 have nothing to measure. Roster data only: no production or test code line is added, so the mutation
proof is correctly `n/a` and step 6's enumeration class is empty. The head's own runs are now concluded
and green: `gh api …/commits/5c7375001/check-runs` rolls up `{"skipped":19,"success":36}` with zero
failures, `governance / instrument-self-tests` success, `gate` success, and `pr-contract / pr-contract`
success starting `20:25:06Z` — after `instrument-self-tests` concluded at `20:22:35Z` — so the body was
read by the contract at the final state, as step 11 requires. `carry_audit`: the live PR alone reads
`1 finding item(s): 0 routed, 1 unrouted` — the prior verdict's `## Settled` note `bd4a24eb` — and
`carry_audit.py check --body <live body> --comments <live comments + this verdict>` reads
`3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)`, because this verdict routes
`bd4a24eb` by id; that is what `pr 2878` will read once this verdict is posted.
Carry: R10-ROSTER-BATCH24

## Not established

Nothing material. I did not re-run `prepr.sh`, per the brief. I did not independently confirm the
`## Head` claim that the two merges were "an automatic merge by the orchestrator's script" beyond
their parentage and the conflict-free `merge-tree`; the merged tree is the pushed head, whose blob
matches the body.
Carry: R10-ROSTER-BATCH24
