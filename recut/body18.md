Roster for round 10, eighteenth landing (after #2635, batch 17). It records the R10-SCORES routings the R10-SCORES pull request's contract reads from the head roster, the Batch 4 triage carry, two groups that were opened as pull requests without a roster entry (R10-FLY-SUITE-ENV-FLAKES, R10-FLY-NO-FOOTERS), and two merged groups. Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

The authored code head is `3e7aaed31a1dd5478d7a9acd83ed16de6d9f23eb`, the tip of `handoff/audit-r10-roster`. Its merge base with `origin/main` `e364a0d73b8537e94258d5d0da98542d53793c84` is `16370d882f9171df79413d2b0fa2680227f16812`, the roster tip as #2635 landed it. The diff against that base is one file, `dev/programme/rosters/wave-r10-groups.json`, 91 insertions and 7 deletions (`git diff --stat origin/main...3e7aaed31` prints them) over 8 commits (`git rev-list --count origin/main..3e7aaed31` prints 8, none a merge), each pushed by `roster_edit.py --push` after its lint gate printed `TOTAL: 0 error(s)`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git diff --exit-code e364a0d73b8537e94258d5d0da98542d53793c84 16370d882f9171df79413d2b0fa2680227f16812 -- dev/programme/rosters/wave-r10-groups.json` has rc 0: the roster on main equals the merge base, so nothing main wrote since is overwritten. The `removed` list below is empty.

## Figures

The 8 ops, by commit (`git log --format='%h %s' origin/main..3e7aaed31` prints them):

- `9a4953627` carry on R10-UX-HEALTH: the card's null-as-0 siblings in the Advisor rows, from the R10-SCORES body.
- `c3711a1f0` carry on R10-PARAMS-OWNER: the bundle measurement the R10-SCORES harness needs a local seat for.
- `75c891e28` carry on R10-PARAMS-OWNER: the envelope band and mass basis finding with main's decision text.
- `600635c16` carry on R10-FLY-RELAY-REVIEW-FF: the triage P-C text (tick_loop passes `--confirm` to the relay), accepted as already carried.
- `d37aa1b1f` group R10-FLY-SUITE-ENV-FLAKES appended (XS, two carries): the HASTUB_TZ failures of `tests/features.py` found in the #2632 review, and a gate-lease concurrency check that flaked in CI.
- `62be37fe3` R10-BRIEFS-FOLD done at `b24cfe517bd95d30911c43184cf62e2ac781aa19` (#2631).
- `4d79efd87` group R10-FLY-NO-FOOTERS appended (lane FLY, size S, stage in-progress, #2636 recorded in `resume.pr`).
- `3e7aaed31` R10-NIGHTLY-ABSENT-NEW done at `e364a0d73b8537e94258d5d0da98542d53793c84` (#2627).

Measured with `B=origin/main`, `H=3e7aaed31`, `R=dev/programme/rosters/wave-r10-groups.json`: `jq -n --slurpfile b <(git show $B:$R) --slurpfile h <(git show $H:$R) '($b[0].groups|map({(.group):.})|add) as $B|($h[0].groups|map({(.group):.})|add) as $H|{nb:($B|length),nh:($H|length),removed:[$B|keys[]|select($H[.]==null)],new:[$H|keys[]|select($B[.]==null)],changed:[$H|keys[]|select($B[.]!=null and $B[.]!=$H[.])]}'` prints 165 and 167 groups, none removed, 2 new (`R10-FLY-NO-FOOTERS`, `R10-FLY-SUITE-ENV-FLAKES`) and 5 changed (`R10-BRIEFS-FOLD`, `R10-FLY-RELAY-REVIEW-FF`, `R10-NIGHTLY-ABSENT-NEW`, `R10-PARAMS-OWNER`, `R10-UX-HEALTH`). Groups by `resume.stage`, main then this head: done 86 then 88, in-progress 13 then 12, not-started 59 then 60, queued 6 then 6, absorbed 1 then 1. `node tools/policy/brief_lint.mjs` on the roster at `H` prints `TOTAL: 0 error(s) across 1 file(s)`, and `python3 tools/audit/seat/ref_privacy.py --check` at `H` prints `158 line(s) added since d6308d77c5d0 judged, 0 refused`.

## Red checks

Read 2026-10-23 from `repos/tvofi/heatpump_optimizer/commits/e364a0d73b8537e94258d5d0da98542d53793c84/check-runs` (main's tip, 47 runs), failures, cancellations and timeouts only: none. The 8 commits of this branch carry no completed failure other than `pr-contract`, which the contract excludes. Checks at this pull request's own head are read by CI.

## Forward-carry

none

## Friction

none
