Roster for round 10, fifteenth landing (after #2613's batch 14). It records eight groups done (R10-SOLVER and seven whose pull requests merged unrecorded), eight groups set in-progress (fixers out), three groups appended and one re-anchored since batch 14, one fly-in group, two carries on R10-FLOW-ARCH-PLANNER and one stale carry dropped from R10-FLOW-JIDOKA. Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

`6026806236591c7f74e356e82dc4a8cf221d3a1c` merges the authored code head `814cffede7d67a4e05780094c432e78dc05de04c` and then merges origin/main `de69745ff` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

The authored code head is `814cffede7d67a4e05780094c432e78dc05de04c`, the tip of `handoff/audit-r10-roster`. Its merge base with `origin/main` `de69745ffcab66b566b3e75aee0b572023f80857` is `008ad15bbba4df3dc6cb3afaee4ef7120557739d` (#2612's merge, the branch's last merge of main). The diff against that base is one file, `dev/programme/rosters/wave-r10-groups.json`, 172 insertions and 31 deletions (`git diff --stat origin/main...814cffede` prints them) over 27 commits (`git rev-list --count origin/main..814cffede` prints 27, one of them the merge `525b20241` of main), each pushed by `roster_edit.py --push` or `roster_sync.py --apply` after its lint gate printed `TOTAL: 0 error(s)`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git diff --exit-code de69745ffcab66b566b3e75aee0b572023f80857 008ad15bbba4df3dc6cb3afaee4ef7120557739d -- dev/programme/rosters/wave-r10-groups.json` has rc 0: the roster on main equals the merge base, so nothing main wrote since is overwritten (main's later commits are delivery rows). The `removed` list below is empty.

## Figures

The ops, by commit (`git log --format='%h %s' origin/main..814cffede` prints them):

- `d82bfefce`, `91108ea13`, `26645ca88` `R10-RCA-BODY-LINT` appended, set in-progress, branch set.
- `a332e09e3`, `9c6d30a5a` `R10-SCORES` brief pins re-anchored to `coordinator.py` :1081 then :1083 after #2612.
- `1946d3e31`, `805a8915f` `R10-NIGHTLY-ABSENT-NEW` appended, set in-progress.
- `525b20241` merge of `origin/main` (line pins track main's tree).
- `1a3921ae1` `R10-NIGHTLY-ABSENT-NEW` brief: the bare token for GitHub's inactivity-disabled workflow state read as a symbol missing from the tree and refused every later lint gate; it is reworded as prose, nothing else in the brief changes.
- `89ad8e416` `R10-SOLVER` done at `008ad15bbba4df3dc6cb3afaee4ef7120557739d` (#2612).
- `96b14cbea`, `054621bc3` two carries appended to `R10-FLOW-ARCH-PLANNER` (the owner's 2026-10-22 critical-path cap exemption; the four standing seats as role contracts).
- `c8c7ae046` `R10-FLOW-JIDOKA` first carry dropped (its decision-0012 ruling is moot, 0014 having revoked 0012); the one entry matching was the one dropped.
- `ca48ff790` `R10-FLY-PRUNE-REFS` appended, stage not-started.
- `89625c06b` `roster_sync.py --apply` over a pull-request list that omits #2514 and #2589: seven groups done at their merge commits, `R10-CURRENCY` and `R10-RCA-BODY-LINT` given their pull-request number, and ten carries appended to `R10-ORCH-MACHINERY` (35 to 45 entries). Done: `R10-SENSOR-PAYLOAD` #2379 at `5756f2b15`, `R10-RCA-HANDOFF-SLIP` #2545 at `f35a5a373`, `R10-PLAN-ARTIFACT` #2558 at `383bca2be`, `R10-FLOW-ANDON` #2582 at `fea3d3ca6`, `R10-FLOW-BODY-PATCH` #2578 at `8a4c438e7`, `R10-FLOW-DISPATCH` #2577 at `b980e2fa0`, `R10-FLY-BUDGET-LEAF` #2591 at `1787ffd08`. Each body was read for an owed further pull request first; none names one. `R10-SENSOR-PAYLOAD` leaves the D8-s1-01 remainder to `R10-ARCH-SHAPES`, which already carries it. The sync's one refusal, `Carry: R10-PLAN-ARTIFACT` from #2558, is a self-route stating the review survivors are closed in that pull request, so nothing is owed.
- `5876f3b74`, `6e8141eae`, `0a326689b` `R10-SCORES`, `R10-LOOP-CPU` and `R10-RECORD-API-BUDGET` set in-progress (their fixers are out).
- `da995b7b8` carry appended to `R10-FLY-DEPGRAPH-STALE`: the 57 Dependabot alerts (85-141) were dismissed by hand at the owner's request, so its verification step 3 becomes reopen-and-confirm-they-close. `8ad62be53` that group set in-progress.
- `ed82e8038`, `cf4cf35dc`, `a22407d46`, `8afb18cd9` `R10-FLOW-PULL`, `R10-FLOW-TOOLKIT-MEASURE`, `R10-BRIEFS-FOLD` and `R10-FLOW-ARCH-PLANNER` set in-progress (cloud fixers out).
- `c7fd05680` carry appended to `R10-FLOW-JIDOKA`: #2625's CI `instrument-self-tests` failed on `ref_privacy --check` after prepr passed, the third such instance on 2026-10-22; the prepr replay must include that check.
- `1e1521847`, `814cffede` the `R10-FLOW-ARCH-PLANNER` seats carry re-appended without the one host path the coordinator's text file held (`drop-carry`, matching its first words, then `append-carry`); it is again that group's last carry, and the roster holds no `/Users/` or `/private/tmp` string.

Left unchanged on purpose: `R10-FLY-GH-READ-RETRY` (#2589 reads "PR 1 of 2", with a PR 2/3 carry) and `R10-REPLAY-LANE` (#2514 leaves its headline recorded-day item and a cap re-record owed). Both stay in-progress; the sync list omitted them for that reason.

`R10-SOLVER`: its brief and 4 carries name no owed pull request. #2612 disposes of #2240 as a re-measured duplicate of the owner's refusals #1293 and #1294 and addresses #2250; its forward-carries route to `R10-BRIEFS-FOLD`. The group's `after` groups are done.

Measured with `B=origin/main`, `H=814cffede`, `R=dev/programme/rosters/wave-r10-groups.json`: `jq -n --slurpfile b <(git show $B:$R) --slurpfile h <(git show $H:$R) '($b[0].groups|map({(.group):.})|add) as $B|($h[0].groups|map({(.group):.})|add) as $H|{nb:($B|length),nh:($H|length),removed:[$B|keys[]|select($H[.]==null)],new:[$H|keys[]|select($B[.]==null)],changed:[$H|keys[]|select($B[.]!=null and $B[.]!=$H[.])]}'` prints 151 and 154 groups, none removed, 3 new (`R10-FLY-PRUNE-REFS`, `R10-NIGHTLY-ABSENT-NEW`, `R10-RCA-BODY-LINT`) and 19 changed (the 4 above plus `R10-CURRENCY`, `R10-FLOW-ANDON`, `R10-FLOW-BODY-PATCH`, `R10-FLOW-DISPATCH`, `R10-FLY-BUDGET-LEAF`, `R10-LOOP-CPU`, `R10-ORCH-MACHINERY`, `R10-PLAN-ARTIFACT`, `R10-RCA-HANDOFF-SLIP`, `R10-SCORES`, `R10-SENSOR-PAYLOAD`, `R10-SOLVER`, `R10-FLOW-ARCH-PLANNER`, `R10-FLOW-JIDOKA`, `R10-RECORD-API-BUDGET`, `R10-FLY-DEPGRAPH-STALE`, `R10-FLOW-PULL`, `R10-FLOW-TOOLKIT-MEASURE`, `R10-BRIEFS-FOLD`). Groups by `resume.stage`, main then this head: done 76 then 84, in-progress 8 then 15, not-started 60 then 49, queued 7 then 6. `node tools/policy/brief_lint.mjs` on the roster at `H` prints `TOTAL: 0 error(s) across 1 file(s)`.

## Red checks

Read 2026-10-22 from the check-runs API at main's tip `de69745ffcab66b566b3e75aee0b572023f80857` and at each commit of this pull request's own earlier head (`d0df7ed3b`, `def9eba78`), failures only, excluding `pr-contract`:

- `instrument-self-tests` (job 120100952326, red at `d0df7ed3b`): `ref_privacy --check` refused `dev/programme/rosters/wave-r10-groups.json` line 6595, a host path in an added line. The cause is the seats carry the coordinator supplied, whose text named an out-of-tree brief by its absolute path; I appended it unscrubbed. Fixed in `1e1521847` and `814cffede` (above); `python3 tools/audit/seat/ref_privacy.py --check` at `814cffede` prints `46 line(s) added since 008ad15bbba4 judged, 0 refused`. Cheaper detector: that command itself, which runs in seconds and needs no network. `roster_edit.py` does not run it before `--push`, and prepr did not either; R10-FLOW-JIDOKA carries the same gap (its `ref_privacy --check` carry, 2026-10-22), so no new countermeasure is built here. Standing cost of running it from `roster_edit` is one process of a few seconds per op; it is owed to that group, not this pull request.
- `nightly-status` (job 120101165335, red at `d0df7ed3b`; 120100214105 at `def9eba78`; also red on main's ancestry): it grades main's scheduled Tests run, and this diff touches nothing it reads. Owed by the orchestrator on main.
- `rerun-stale-contract`: 19 runs `cancelled` at main's tip. That workflow (`.github/workflows/pr-contract-rerun.yml`) shares one concurrency group per head with `cancel-in-progress: true`, so a superseded run is cancelled by design (R10-FOLLOWER-DEBOUNCE, its header comment); none is a failure of a required check.

## Forward-carry

none

## Friction

none
