Fix review: merge 928a672753558ca6f88f45f806d9aa9b04440c36

bus-nonce: 6666813bbe71d0ca22fbf790e968274c

Round 2. Round 1 was `blocked e3a6f0729 null-control-false` (comment 6253163400).
This is a repair, not a re-cut. Measured head 928a672753558ca6f88f45f806d9aa9b04440c36,
and `git ls-remote` still showed it as refs/pull/2408/head just before I wrote this.
Merge base and origin/main: 07a09406a. The contract is current:
`git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.

## Round-1 blocker: resolved

- `paths:` keeps `.claude/workflows/*.json` and adds `dev/programme/rosters/*.json`
  and `dev/programme/carries/*.json`.
- "Where it goes" names both roster homes: the round's roster under
  `dev/programme/rosters/`, and a web-fix-wave `groupsFile` under `.claude/workflows/`.
- `audit-verify.js:252` still drafts to `.claude/workflows/wave-r${round}-groups.json`.
  That is now a bound home, and the body dispositions it.
- The new policy_lint rule-binding arm walks the tree, so the round-1 shape can no longer pass green.

## Head = clean merge (resolution delta)

928a67275 merges origin/main 07a09406a into 0b09c4ab4. Its tree is 3d846f25284c.
`git merge-tree --write-tree 07a09406a 357fe0fca` gives the same tree, so the
resolution delta is empty. `git merge-tree --write-tree origin/main 928a67275`
exits 0 with tree 3d846f25284c, no conflict and no MERGE-CLAIM line. Evidence: `ev/merge_tree.txt`.

## RESULT lines (at the head unless stated)

- RESULT policy_lint: `TOTAL: 0 error(s) across 41 policy file(s)`, `FIXTURE ok: 92 error(s) hold 244 pins across 12 check classes`, rc=0. At base 07a09406a: TOTAL 0, rc=0. `ev/lint_head.txt`, `ev/lint_base.txt`
- RESULT budgets: finding-propagation 100/101 lines and 1336/1336 tokens; orchestrator.md 319/319 and 4513/4513; fix-review.md 140/140 and 2451/2451; corpus ~61137. Base: 100/1329, 319/4513, 140/2451, corpus ~61130. These match the body. No cap is raised. `ev/budgets_*.txt`
- RESULT rules_sync --check: `RULES-SYNC ok`. brief_lint: `CARRY ok`, rc=0. policy_lint_mutants: `MUTANTS ok` with `ruleBindingOverTree` in the corpus list, rc=0. structure.py: `STRUCTURE RATCHET PASSED`.
- RESULT closure select: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. This matches the body. `ev/closure_select.txt`
- RESULT entities.py (`env -u BASH_ENV PYTHONPATH=tests/hastub`): `ALL 2349 ENTITY CHECKS PASSED`, rc=0. The body's 2346 was taken at the code head 357fe0fca, before the main merge brought in 3 checks. That difference is not a discrepancy. `ev/entities_head.txt`
- RESULT mutation proof, the arm (`ev/mutation_arm.txt`), with my own mutants:
  - M1, the previous head's globs: rc=1, TOTAL 10. It names `.claude/workflows/wave-3l-groups.json`, `.claude/workflows/carry-1921.json` and 8 carries under `dev/programme/carries/`. Matches the body.
  - M2, main's globs: rc=1, TOTAL 10. It names `wave-r9`, `wave-r10` and 8 carries. Matches the body.
  - M3, the arm's predicate made dead: `FIXTURE VACUOUS: ... 'unbound carry home' arm produced []`, rc=1. Killed.
  - M4, the exclusion deleted: TOTAL 47 (37 archived carries, 5 archived rosters, 5 fixtures) and `FIXTURE OVER-FIRES`, rc=1. Killed, and the count matches the body.
  - M5, mine: `locate()` replaced by raw `tracked`. TOTAL 5 on the real tree: the old spellings `.claude/workflows/fixtures/carry-99000{1..4}.json` and `roster-probe/wave-probe-groups.json` fire. This adds a real-tree witness that `locate()` is load-bearing beyond the body's M2 claim. The acceptance fixture still has no moved-file model, and the body discloses that under Unpinned sites.
- RESULT cmdRecord fix: `--record-known-bad` at the head prints `recorded 7 entr(ies), 13 occurrence(s) ... +0 -0 ~0`. Only `recorded_at` moves, to the new merge base. Restoring the shadowing `const at` gives `TypeError: at is not a function`, so it is killed by manual drive only (no pin, as the body discloses). Restoring the known-bad count 6 to 8 gives `[known-bad] ... 6 occurrence(s) left of 8 recorded`, TOTAL 1, so the re-record is earned by the deleted duplicate. `ev/mutation_record.txt`
- RESULT class seams: the body's rule `git ls-files | grep -E '(^|/)(wave-[^/]*-groups|carry-[0-9]+)\.json$'` returns 59 files. 2 are in `.claude/workflows`, 2 in `dev/programme/rosters`, 8 in `dev/programme/carries`, 42 under `dev/archive`, and 5 under `tools/policy/fixtures`. This matches the body's dispositions, and no open seam remains. `ev/class_seams.txt`
- RESULT VERSION, RELEASE_NOTES.md, manifest and tests/golden: untouched (three-dot, empty diff). `ev/version_untouched.txt`

## CI on the head (check-runs API, every run) and step 11

`ev/check_runs.txt` holds these reds:
- **wave-script** failure (job 117785286969). The agreement lane printed `merge-subject-pr ... 2 divergent` on `Merge pull request #2401 (R10-ARCHSCORE-COVERAGE p5)` and `#2379 (R10-SENSOR-PAYLOAD)`, where the policy_lint readers read null. The same job is red on main 07a09406a (run 39158144006, job 117765552837). This is main's red, and the body's `## Red checks` names it and answers it: no cheaper detector.
- **delivery-status** failure: `OVERDUE` on rows #2413, #2412 and #2407 (main's records). The diff adds only its own `2408.md` row, so this red is not this PR's (fix-review step 11).
- **pr-contract** failures at 20:45 and 20:49. Both are `[pr-body] check wave-script is red and ## Red checks does not name it`, against the body as it stood then. The latest pr-contract job, 117794455376 (started 21:26:30 after the body edit), is **success**. It printed `record red-history ... delivery-status, wave-script` and `PR-BODY: 0 error(s)`.
- Every other check run is success or skipped.

## Steps without a harness, and figures not re-derived

- Steps 2, 3 and 9: this is a policy PR from an owner-accepted pre-study, and it has no finder's harness. The instruments are the policy lints, run at both ends above.
- The pre-study figures (14 roster-only PRs, median 49 min, 54.1 runner-min on #2380) are quoted from outside the tree. They are not re-derived, as the body says.
- Step 10: the forward-carry is `none`, which is consistent, because the PR is itself the rule text.
- Step 14: no budget moved. The known-bad 8 to 6 change is earned (mutant above).

## Advisory (not blocking)

- Repeated from round 1: fix-review.md step 10 still fuses "carrying the control" and "stated as a precondition" into "confirm it states its control as a precondition". finding-propagation keeps these as two separate checks. The owner may want them split when headroom allows.
- The cmdRecord fix and the arm's `locate()` path have no fixture pin. Both are disclosed as owed under the body's Unpinned sites.
- Owner gate: this is policy. tvofi approval at merge is owed (the orchestrator's, under mandate), and the body says so.
