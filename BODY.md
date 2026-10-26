Roster for round 10, batch 22, at the roster tip `b15f2633943e8be2ca9f2e7233b199f7c969b34c`: the 48 roster commits on `handoff/audit-r10-roster` after `94d14569ea32889e228c54fc082c62d968f254e0` (the roster head of batch 21, #2864), counted by kind under Figures. They are 25 `roster_edit.py` ops, 4 `roster_sync.py` commits (derived from pull requests by the tool), 6 issue wirings, 6 group appends under the completion rule (tvofi, 2026-10-26 20:20Z: every open issue and pull request on a live roster group) and 7 orchestrator resume, stage and carry edits. Part of #201. It closes nothing by keyword and leaves #201 open.

**Merge order: after #2864 (batch 21), which has merged** as `6fe5170cd7ce01e60ffebfc93e598c216e628fa3`. Batch 21's roster head `94d14569ea32889e228c54fc082c62d968f254e0` is the merge base of main and this head, so the three-dot diff carries only this batch's commits.

### The ops, oldest first, by kind

- `roster_edit.py` (25): `f7430f731bd746c1acbc32a1956cf268350e8c30` roster_edit set-stage R10-HOTFIX-BATCH-ERREXIT; `28f827e58ba0a104d994ae941d1d78c42016da41` roster_edit set-stage R10-996-RUNNER-CLAIMS; `e85ed7ddfcc606f38688d19a6d5a961fb7a6b191` roster_edit append-carry R10-996-RUNNER-CLAIMS; `9fba58840a493cf8dbbc8d1cf2b4a58ec1f2abef` roster_edit append-carry R10-FLOW-BODY-ONLY; `071c715da962ae2939926fc143495b008618daa6` roster_edit append-group R10-RECORD-HOLD-APPROVE; `4d44dcbf0005b3e35c789c832121d752630824f2` roster_edit append-carry R10-FLOW-BODY-ONLY; `2adcc52871409939e3c9adcc880966845b6f6332` roster_edit set-after R10-FLOW-BODY-ONLY; `0e1506e07427bfd7a86d171ab745246668993e33` roster_edit append-carry R10-ORCH-BEATD; `c3d17f0e57d0139c15c084a13c3a5788c83ec291` roster_edit append-carry R10-ORCH-BEATD; `78bafe8be907341277464a9a2e35d4d839090ec3` roster_edit append-carry R10-ORCH-REVIEW-PACKET; `6bd8107153404a5069770a73fea5a120e5af4cbd` roster_edit append-carry R10-ORCH-REVIEW-PACKET; `d764dd01b6409f57995e9d5129ef4d0c551fe899` roster_edit append-carry R10-ORCH-REVIEW-PACKET; `336a11ff6781825cf317e705f30bf20cc46efa45` roster_edit append-carry R10-ORCH-BEATD; `11909994b6983967b871046111342f7f01d8f424` roster_edit set-after R10-UX-HEALTH; `81a622a9cb9408ec5982cd47f5dcd04c5788af59` roster_edit set-after R10-FLY-SUITE-ENV-FLAKES; `1f440eba41a65b40c85e69439a6510e7f60ebbb9` roster_edit set-after R10-ADVISOR-WHATIF; `cb0fda5fda4283045da4e22cf72c1635f6ae1dd3` roster_edit set-after R10-IMMERSION-LATCH; `7ee0a54e119196e7a4faf9ca365111e339c907d6` roster_edit set-after R10-FLY-LEDGER-SAMPLE; `87b08975c16514e64149a9d863786e7dff77ad62` roster_edit set-after R10-HOUSE-GRADE; `ae4283ebcde0a0ebaba2508dfd0aa96e789bcffe` roster_edit set-after R10-ERREXIT-COUNTERMEASURES; `65aec1b87ae1a024fb686413dc738bb468da327b` roster_edit set-after R10-RECORD-HOLD-APPROVE; `b5d8c338b5ac12f507fb677077bec1e369639f56` roster_edit wire-issue R10-DEPENDABOT-SETUPTOOLS; `d424c5d17a2473b16d57b02ad68298093641c9e7` roster_edit wire-issue R10-FLOW-POSTMERGE; `c6c00b7bdf54c27179dcd896b7929b5e3e42b565` roster_edit wire-issue R10-FLY-LEDGER-SAMPLE; `b15f2633943e8be2ca9f2e7233b199f7c969b34c` roster_edit append-group R10-STORE-RACES.
- `roster_sync.py` (4): `3e5300557c887d59ebf74697b838fa2be7ef1863` roster_sync: derive stages from pull requests; `e6a19b0224780f978cea8b9e1c2ca6d74ef7dfa0` roster_sync: derive stages from pull requests; `92b1be071d028b7b7894389fe3de4b7ec74a9f99` roster_sync: derive stages from pull requests; `561508e9a4f8b0fffec43423c01de6bc536794b7` roster_sync: derive stages from pull requests.
- Issue wirings (6): `a07420b2685edf3e0c6b58241bfd29fee3bc7f23` roster: wire #2855 (carry-missing friction) to R10-RCA-FRICTION-RESIDUE, whose brief names the carry-missing key; `88313953913c7d86fdd800bb3fcd8f40a96c9137` roster: wire #2260 (Health-tab learner hints residual) to R10-UX-HEALTH, brief item 5; `5ad2092f713055685b979c525393b4395574cf91` roster: wire #2258 (envelope band residual, item 2c) to R10-HOUSE-GRADE; `d880e8d3cad01e7c016e598f41e126ac7c823392` roster: wire #2499 (plan vs relaxed DP overbook residual) to R10-BUFFER-STORE, whose carry holds it; `f4ff4cc13b137d5f2013b788ebe30c959e5722b4` roster: wire #2494 (merge-subject writer-scan residual) to R10-MERGE-SUBJECT-CASEARM, split from #2697; `11b53fbd79a6a764bb099b7674090fe0ff29839e` roster: wire #2271 (redaction on the owner's exported day) to R10-REPLAY-REAL-DAY.
- Group appends under the completion rule (6): `51060018dc4d7c6fef76b52b7e6725d54d61f40e` roster: append-group R10-FRICTION-REGRESSION (completion rule, tvofi 20:20Z); `ad18ee0802d6e0fa66f7723a32d426f21eefba34` roster: append-group R10-FRICTION-MUTATION-SURVIVOR (completion rule, tvofi 20:20Z); `26e70095215924deec1e6f17168904b3e1a85828` roster: append-group R10-FRICTION-GATE-SCOPING (completion rule, tvofi 20:20Z); `12b594b51db828b1e16159b6d8c91c9ebeb0e54b` roster: append-group R10-DIAG-AGES (completion rule, tvofi 20:20Z); `9df0e4266f2d4b9fa4ef2b2f11e47143ca9c0221` roster: append-group R10-ADVISOR-WHATIF (completion rule, tvofi 20:20Z); `15168182b63d0930a79ef44c0395a3b3c5f72f92` roster: append-group R10-DEPENDABOT-SETUPTOOLS (completion rule, tvofi 20:20Z).
- Orchestrator resume, stage and carry edits (7): `aa4a11e31c54528c09ebaf19c9235feb4d024dbf` roster: R10-FLOW-ROSTER-FREEZE arms (a) #2792 and (b) #2779 merged; arm (b2) + review_freeze mutant R1 remain; `09bbf7f0a85c03455511d36e93e31041761f04f5` roster: R10-CEILING-PROBE design-blocking findings (fixer seat, measured); `1cd291cbba69474c71db40d195aedaff6e0f86a0` roster: R10-CEILING-PROBE needs design; `7a9a766b4cce892d67451591ddf7afb7ed448275` roster: R10-FLOW-BODY-ONLY resume next_step; `55a26541333cd3e031e83ef68e1cf94c1c65aa47` roster: R10-CEILING-PROBE resume next_step; `7427950d57d17201bd99a7c7a04bd0a9554b5cbf` roster: R10-CEILING-PROBE design approved r2, carries 7-8; `7f5039478dc3a2db53e825008cbae3205c62a6b1` roster: R10-CEILING-PROBE in-progress (fixer).

## Head

The authored head is `b15f2633943e8be2ca9f2e7233b199f7c969b34c`, the tip of `handoff/audit-r10-roster`. Its merge base with origin/main (`6fe5170cd7ce01e60ffebfc93e598c216e628fa3` at this reading) is `94d14569ea32889e228c54fc082c62d968f254e0`. `git merge-tree --write-tree 6fe5170cd7ce01e60ffebfc93e598c216e628fa3 b15f2633943e8be2ca9f2e7233b199f7c969b34c` prints the tree `01ea1fad3d00d9ae0114dd9eb6dc039b53664ea1` and no conflict. The only file these ops touch is `dev/programme/rosters/wave-r10-groups.json`, the pull request's own delivery row apart. `git diff --stat 6fe5170cd7ce01e60ffebfc93e598c216e628fa3...b15f2633943e8be2ca9f2e7233b199f7c969b34c` prints:

```
dev/programme/rosters/wave-r10-groups.json | 422 +++++++++++++++++++++++++++--
 1 file changed, 396 insertions(+), 26 deletions(-)
```

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

The blob hashes come from `git show <ref>:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin`: origin/main prints `3813b744f69b0b914ae29a7712de7c37ce27431f`, the same blob as batch 21's head (`3813b744f69b0b914ae29a7712de7c37ce27431f`), and this head prints `30eea08a32352c157dce62e29da490f2b45bef1a`. A script that loads both files as JSON and keys groups by `group` printed `groups 199 207`, added 8 (R10-ADVISOR-WHATIF, R10-DEPENDABOT-SETUPTOOLS, R10-DIAG-AGES, R10-FRICTION-GATE-SCOPING, R10-FRICTION-MUTATION-SURVIVOR, R10-FRICTION-REGRESSION, R10-RECORD-HOLD-APPROVE, R10-STORE-RACES), removed 0 (none), and `changed 21`, each with the keys that moved: R10-996-RUNNER-CLAIMS (`carry`, `resume`); R10-ADVISOR-RESIDUE (`resume`); R10-BUFFER-STORE (`issues`); R10-CEILING-PROBE (`carry`, `resume`); R10-ERREXIT-COUNTERMEASURES (`after`); R10-FLOW-BODY-ONLY (`after`, `carry`, `resume`); R10-FLOW-POSTMERGE (`issues`); R10-FLOW-ROSTER-FREEZE (`resume`); R10-FLY-LEDGER-SAMPLE (`after`, `issues`); R10-FLY-OPENPR-ATOMIC (`resume`); R10-FLY-SUITE-ENV-FLAKES (`after`, `carry`); R10-HOTFIX-BATCH-ERREXIT (`resume`); R10-HOUSE-GRADE (`after`, `issues`); R10-IMMERSION-LATCH (`after`); R10-MERGE-SUBJECT-CASEARM (`issues`); R10-ORCH-BEATD (`carry`); R10-ORCH-DISPATCH-REG (`resume`); R10-ORCH-REVIEW-PACKET (`carry`); R10-RCA-FRICTION-RESIDUE (`issues`); R10-REPLAY-REAL-DAY (`issues`); R10-UX-HEALTH (`after`, `issues`). No other group moved.

`node tools/policy/brief_lint.mjs <this head's roster file>` from a fresh origin/main checkout (`6fe5170cd7ce01e60ffebfc93e598c216e628fa3`), as `roster_edit.py`'s lint gate runs it, exited 0 with `TOTAL: 0 error(s) across 1 file(s)`.

## Figures

`git log --no-merges --format=%s 94d14569ea32889e228c54fc082c62d968f254e0..b15f2633943e8be2ca9f2e7233b199f7c969b34c -- dev/programme/rosters/` prints the 48 commit subjects; piping it through `grep -c '^roster_edit'` prints 25, `grep -c '^roster_sync'` 4, `grep -c '^roster: wire'` 6, `grep -c '^roster: append-group'` 6, and `grep -c '^roster: R10'` 7.

The 21 changed and 8 added groups come from the script named under Null control.

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON and its delivery row. The orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
