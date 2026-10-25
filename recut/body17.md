Roster for round 10, seventeenth landing (after #2626, batches 15 and 16). It re-cuts R10-ORCH-MACHINERY into five owned groups and six single-file groups, lands the Batch 3 triage carries and the carries that routed the open pull requests' bodies, records the merged groups, and refreshes the state docs. Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

The authored code head is `16370d882f9171df79413d2b0fa2680227f16812`, the tip of `handoff/audit-r10-roster`; the pull request head is `7a3e640d01ffdfe3e74c64fc4e3ede06c087489c`, which merges it with `origin/main` and adds this pull request's delivery row. Its merge base with `origin/main` `e45fc34fb1459e67f01ea50399b970f0e9aff2da` is `cccbf4fb508cca8ce711dd06add13cc034ac0edb`, the roster as #2626 landed it. The diff against that base is one file, `dev/programme/rosters/wave-r10-groups.json`, 498 insertions and 56 deletions (`git diff --stat origin/main...16370d882` prints them) over 66 commits (`git rev-list --count origin/main..16370d882` prints 66, none a merge), each pushed by `roster_edit.py --push` or `roster_sync.py --apply` after its lint gate printed `TOTAL: 0 error(s)`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git diff --exit-code e45fc34fb1459e67f01ea50399b970f0e9aff2da cccbf4fb508cca8ce711dd06add13cc034ac0edb -- dev/programme/rosters/wave-r10-groups.json` has rc 0: the roster on main equals the merge base, so nothing main wrote since is overwritten. The `removed` list below is empty.

## Figures

The ops, by commit (`git log --format='%h %s' origin/main..16370d882` prints all 66):

- Carries for open pull requests' bodies and standing rulings, before the re-cut: `1f35f6d20`, `d0b49bc68`, `5a762df2e` (R10-FLOW-POSTMERGE, -AUTOTRAIN, -ARCH-PLANNER, for #2628); `0f690a952` (R10-CI-LAYOUT-P2, for #2627); `a46a37a87`, `5ba47bffc` (R10-FLOW-JIDOKA, for #2625); `0ae379878` (R10-FLY-OPENPR-ATOMIC); `cccbf4fb5` (R10-LIVESTATE); `e381aff4f`, `224dfb4ed` (R10-POLICY-FIXER-MD, R10-ORCH-MACHINERY, routing the R10-BRIEFS-FOLD body).
- The R10-ORCH-MACHINERY re-cut, from the designer note on `design/R10-ORCH-MACHINERY` at `2fc665c61` (sections 3 and 4), 57 ops. Five groups appended: R10-ORCH-LEDGER (`fd6ab6404`), DISPATCH-REG `e76de0b10`, BEATD `194895ad6`, PLANPAGE `d18d2da9c`, ROSTER-SCHEMA `510d7e3c1`; six single-file groups appended: R10-FLY-WORKTREE-GC `57f8692d2`, -DAEMONIZE-ARGV `0b0412cb9`, -CIPREDICT-LAYOUT `50169b224`, -CLOUD-SETUP-TOOLCHAIN `3d42fc2cd`, -YIELD-GUARD `8b2818ce9`, -ENVMATRIX-NOREMOTE `26fc1a153`. Carries moved to existing owners: R10-FLY-CARRY-DISPOSITION (`699006cf5`, `dd7962ecf`), R10-UPDATE-PR-SIGNALS `fc81bbcae`, R10-FLY-CAP-LINE `d076d7eee`. 34 carries dropped from R10-ORCH-MACHINERY (`198970538` through `03acbf981`), which keeps its 12 no-build carries; its note `c322af44c`; its stage set to absorbed `65f327f22` (the schema has no closed-superseded stage). R10-FLOW-TOOLKIT-MODEL set after R10-ORCH-PLANPAGE `2803b0f3e`; R10-ROUND-PLAYBOOK set after R10-ORCH-LEDGER, -DISPATCH-REG, -BEATD and -PLANPAGE `ae27f3946`, because absorbed is not a done stage.
- Batch 3 triage carries: R10-FLOW-DESIGN-STAGES `770048ac2`, R10-FLY-PRUNE-REFS `b032771c1`, R10-FLY-RELAY-REVIEW-FF `5ac811f35`, R10-ORCH-BEATD `146f32ce0`.
- Stages: R10-RCA-BODY-LINT done at `cf01e82eec281c0d4e4141beb8fd5a8834cf99de` (#2625) `1923e29cc`; R10-FLOW-PULL done at `fc7173fe7876e9973a170675d25337a810a40c59` (#2628) `618c8a202`; `roster_sync.py --apply` `16370d882` recorded pull-request numbers on five in-progress groups (#2627, #2629, #2631, #2632, #2633).
- Carries for #2629 and #2627: `1eee009fd` (R10-RECORD-API-BUDGET), `f664d7b5d` (R10-FLOW-JIDOKA), `51d9ddc63` and `6fe5deb29` (R10-FLY-CLOUD-SETUP-TOOLCHAIN).

Re-route owed after this merges: #2627's and #2629's bodies route their toolchain items to R10-ORCH-MACHINERY, the only destination main's roster knew when their bodies were patched; the carries themselves sit on R10-FLY-CLOUD-SETUP-TOOLCHAIN. Once this pull request merges, re-route those two body bullets to R10-FLY-CLOUD-SETUP-TOOLCHAIN.

Measured with `B=origin/main`, `H=16370d882`, `R=dev/programme/rosters/wave-r10-groups.json`: `jq -n --slurpfile b <(git show $B:$R) --slurpfile h <(git show $H:$R) '($b[0].groups|map({(.group):.})|add) as $B|($h[0].groups|map({(.group):.})|add) as $H|{nb:($B|length),nh:($H|length),removed:[$B|keys[]|select($H[.]==null)],new:[$H|keys[]|select($B[.]==null)],changed:[$H|keys[]|select($B[.]!=null and $B[.]!=$H[.])]}'` prints 154 and 165 groups, none removed, 11 new (the five R10-ORCH groups and the six R10-FLY groups above) and 18 changed. Groups by `resume.stage`, main then this head: done 84 then 86, in-progress 15 then 13, not-started 49 then 59, queued 6 then 6, absorbed 0 then 1. `node tools/policy/brief_lint.mjs` on the roster at `H` prints `TOTAL: 0 error(s) across 1 file(s)`, and `python3 tools/audit/seat/ref_privacy.py --check` at `H` prints `86 line(s) added since cccbf4fb508c judged, 0 refused`.

## Red checks

Read 2026-10-23 from `repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs`: main's tip `e45fc34fb1459e67f01ea50399b970f0e9aff2da` has no completed failure. `nightly-status` was red on main at `8a009877502b384ea0460855c44993c826f6080a`; it grades main's scheduled Tests run, and this diff touches nothing it reads. Owed by the orchestrator on main; #2627 fixes its false ABSENT. The 66 commits of this branch carry no completed failure other than `pr-contract`, which the contract excludes. Checks at this pull request's own head are read by CI.

## Forward-carry

none

## Friction

none
