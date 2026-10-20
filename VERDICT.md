Fix review: merge 33704404d201f3ce78443e4f3636a9beeff3324e

bus-nonce: fc32532d1e6a22cf890dfc094ccdd0b4

PR #2516, group R10-CODEQL-PR-CAP, head `33704404d201f3ce78443e4f3636a9beeff3324e`, round 2.
Round 1 blocked at `55b74733` on one claim: both added comments said all three
cancellations fired while uploading results. The fixer's `7b64805` corrects the
split in both comments and in the body; `33704404` merges `7b64805` and
origin/main `9fdc5846` and is the head. Nothing else moved: the delta from
`7b64805` is four of main's own delivery rows, and the delta from `55b74733` to
`7b64805` is comment lines in the two authored files.

RESULT round-1 block addressed: `codeql.yml` now reads "2bd5e90f 30:19, 11 minutes into query evaluation; 4e5801eb 30:09 and 916431ae 30:07, both while uploading results", and `tests/entities.py` carries the same split
RESULT split re-derived from each job's own log: `2bd5e90f` job 118675172846 -- query evaluation began 14:27:57.190Z (`Starting evaluation of codeql/python-queries/...`), `Perform CodeQL Analysis` cancelled 14:39:05Z (11:08), and its only SARIF upload is the post-cancellation failed-run one at 14:39:09Z; `4e5801eb` attempt 1 job 118679535262 uploaded results at 14:46:11.848Z; `916431ae` job 118688693484 began post-processing its results at 15:02:38.483Z and uploaded at 15:02:39.100Z; both were cancelled later in that upload wait (14:47:28Z and 15:04:44Z)
RESULT body: intro and the three per-job figure lines carry the same split; `## Head` names 33704404; `## Approval` names `.github/CODEOWNERS`'s `/.github/workflows/` rule at `@tvofi` and the `POLICY_GLOBS` non-match
RESULT POLICY_GLOBS (`tools/policy/policy_lint.mjs:237-275`) matches CLAUDE.md, AGENTS.md, `.claude/rules/*.md`, `dev/governance/{rules,roles,dimensions}/*.md`, `tools/audit/briefs/*.md`, the three READMEs, web-fragments.md, `.claude/skills/*/SKILL.md` and `.github/PULL_REQUEST_TEMPLATE.md`; `.github/workflows/codeql.yml` and `tests/entities.py` match none
RESULT delta `55b74733` -> `7b64805`=two files, comment lines only; `timeout-minutes: 45` and the `R.check` predicate are byte-identical, so the round-1 mutation pair (cap 30 -> `1 of 2360 ENTITY CHECKS FAILED`, the cap check; restored 45 -> `ALL 2360 ENTITY CHECKS PASSED`) is over the same predicate and value
RESULT delta `7b64805` -> `33704404`=four of main's delivery rows (`2518`, `2520`, `2522`, `2523`); no authored file moved
RESULT final-head CI `fast (3.14)` job 118951838081 skipped on lane-proof reuse: identical base `9fdc5846` and identical diff-content hash `2873995d` (`git diff 9fdc5846...7b64805` and `...33704404` both hash to it); the recorded run is the `7b64805` fast job 118943782477, which ran `MODE: SCOPED -- 2 script(s) run` (entities.py, harness_headers.py) and printed `ALL 2360 ENTITY CHECKS PASSED` and `ALL 109 HARNESS HEADER CHECKS PASSED` at 23:31:49Z -- the same judged tree, since 33704404 merges 7b64805 onto 9fdc5846
RESULT local at `33704404`: closure select `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, the same two scripts; structure `STRUCTURE RATCHET PASSED`, rc 0; architecture score `dS +0.0000 NULL`, rc 0
RESULT four cited jobs at the final head's body: `2bd5e90f` 30:19, `4e5801eb` attempt 1 30:09, `916431ae` 30:07, `4e5801eb` attempt 2 21:31 -- unchanged and exact at 4 of 4
RESULT head checks=every check completed except `Analyze (python)` and `closures`, in progress at write and not red; the only failure is `nightly-status`
RESULT merge-tree=`git merge-tree --write-tree origin/main 33704404` exits 0, no conflicting path; `VERSION` 7.0.2, the manifest version and the `RELEASE_NOTES.md` heading are untouched by the authored diff

## Notes (non-blocking)

- `nightly-status` is red at every head of this review. It grades main: the `slow`
  nightly (run 39387919507, head 0c298f6, 2026-10-20T07:39Z) failed, the check is
  unrequired, and this diff touches nothing it reads. Carry: dismissed:
  main-state red, exempt for this diff; the orchestrator's on main.
- The recarry paragraph in the body names the merge commit it expects; it landed
  as named, so the `## Head` line is the head. Carry: dismissed: verified at the
  final head.
- `mutation` is green in 0.5 min because the branch writes no production Python
  line: the lane draws no mutant and the green is vacuous by design; the
  reviewer's own mutant is the proof. Carry: dismissed: expected for a
  workflow-YAML change.
