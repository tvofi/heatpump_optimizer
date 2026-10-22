Roster for round 10, fifteenth landing (after #2613's batch 14). It records one group done (R10-SOLVER), three groups appended or re-anchored since batch 14 (R10-RCA-BODY-LINT, R10-NIGHTLY-ABSENT-NEW, R10-SCORES), one fly-in group, two carries on R10-FLOW-ARCH-PLANNER and one stale carry dropped from R10-FLOW-JIDOKA. Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

The authored code head is `ca48ff790b804d7d30c6d93d26ad05d3ead879ba`, the tip of `handoff/audit-r10-roster`. Its merge base with `origin/main` `de69745ffcab66b566b3e75aee0b572023f80857` is `008ad15bbba4df3dc6cb3afaee4ef7120557739d` (#2612's merge, the branch's last merge of main). The diff against that base is one file, `dev/programme/rosters/wave-r10-groups.json`, 131 insertions and 5 deletions (`git diff --stat origin/main...ca48ff790` prints them) over 14 commits (`git rev-list --count origin/main..ca48ff790` prints 14, one of them the merge `525b20241` of main), each pushed by `roster_edit.py --push` after its lint gate printed `TOTAL: 0 error(s)`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git diff --exit-code de69745ffcab66b566b3e75aee0b572023f80857 008ad15bbba4df3dc6cb3afaee4ef7120557739d -- dev/programme/rosters/wave-r10-groups.json` has rc 0: the roster on main equals the merge base, so nothing main wrote since is overwritten (main's later commits are delivery rows). The `removed` list below is empty.

## Figures

The ops, by commit (`git log --format='%h %s' origin/main..ca48ff790` prints them):

- `d82bfefce`, `91108ea13`, `26645ca88` `R10-RCA-BODY-LINT` appended, set in-progress, branch set.
- `a332e09e3`, `9c6d30a5a` `R10-SCORES` brief pins re-anchored to `coordinator.py` :1081 then :1083 after #2612.
- `1946d3e31`, `805a8915f` `R10-NIGHTLY-ABSENT-NEW` appended, set in-progress.
- `525b20241` merge of `origin/main` (line pins track main's tree).
- `1a3921ae1` `R10-NIGHTLY-ABSENT-NEW` brief: the bare token for GitHub's inactivity-disabled workflow state read as a symbol missing from the tree and refused the lint gate; it is reworded as prose, nothing else in the brief changes.
- `89ad8e416` `R10-SOLVER` done at `008ad15bbba4df3dc6cb3afaee4ef7120557739d` (#2612).
- `96b14cbea`, `054621bc3` two carries appended to `R10-FLOW-ARCH-PLANNER` (the owner's 2026-10-22 critical-path cap exemption; the four standing seats as role contracts).
- `c8c7ae046` `R10-FLOW-JIDOKA` first carry dropped (its decision-0012 ruling is moot, 0014 having revoked 0012); the one entry matching was the one dropped.
- `ca48ff790` `R10-FLY-PRUNE-REFS` appended, stage not-started.

`R10-SOLVER`: its brief and 4 carries name no owed pull request. #2612 closes #2240 as a re-measured duplicate of the owner's refusals #1293 and #1294 and fixes #2250; its forward-carries route to `R10-BRIEFS-FOLD`. The group's `after` groups are done.

Measured with `B=origin/main`, `H=ca48ff790`, `R=dev/programme/rosters/wave-r10-groups.json`: `jq -n --slurpfile b <(git show $B:$R) --slurpfile h <(git show $H:$R) '($b[0].groups|map({(.group):.})|add) as $B|($h[0].groups|map({(.group):.})|add) as $H|{nb:($B|length),nh:($H|length),removed:[$B|keys[]|select($H[.]==null)],new:[$H|keys[]|select($B[.]==null)],changed:[$H|keys[]|select($B[.]!=null and $B[.]!=$H[.])]}'` prints 151 and 154 groups, none removed, 3 new (`R10-FLY-PRUNE-REFS`, `R10-NIGHTLY-ABSENT-NEW`, `R10-RCA-BODY-LINT`) and 4 changed (`R10-FLOW-ARCH-PLANNER`, `R10-FLOW-JIDOKA`, `R10-SCORES`, `R10-SOLVER`). Groups by `resume.stage`, main then this head: done 76 then 77, in-progress 8 then 9, not-started 60 then 61, queued 7 then 7. `node tools/policy/brief_lint.mjs` on the roster at `H` prints `TOTAL: 0 error(s) across 1 file(s)`.

## Red checks

Read 2026-10-22 from `repos/tvofi/heatpump_optimizer/commits/de69745ffcab66b566b3e75aee0b572023f80857/check-runs` (main's tip, 59 runs), failures, cancellations and timeouts only: 10 runs of `rerun-stale-contract`, all `cancelled`. That workflow (`.github/workflows/pr-contract-rerun.yml`) shares one concurrency group per head with `cancel-in-progress: true`, so a superseded run at a head is cancelled by design (R10-FOLLOWER-DEBOUNCE, its header comment); none of the ten is a failure of a required check. 4 further runs (`Analyze (python)`, `closures`, `coverage`, `fast (3.14)`) were still in progress at the read and have no conclusion yet. Checks at this PR's own head are read by CI; this diff changes only the roster and one delivery row.

## Forward-carry

none

## Friction

none
