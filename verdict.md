Fix review: merge 820236749a878893f6217210683b16aefac89657

bus-nonce: d7b21e8499ec9e39fe274c3eb176da76

## Delta

- Round 2. The delta from the reviewed head e3df1f1ca69586ecb91b465cba874ece98a9689b to 820236749a878893f6217210683b16aefac89657 changes `dev/audit/README.md` only, with 10 insertions and 12 deletions, in commit 76aca12e6f. Because it is a policy delta, the scope does not widen (fix-review.md step 12). I did not re-review the Round start section, as the brief says.

## Evidence

- Head measured: 820236749a878893f6217210683b16aefac89657 (`ev/HEAD.txt`). The PR body's `## Head` names the same SHA. Merge base 23cc7b8e1d004279d99bd59f3d2bd2a8f885b426. `git diff <merge-base>...origin/main -- dev/governance/roles/ dev/governance/rules/` is empty, so the contract is current.
- `git merge-tree --write-tree origin/main 820236749a` (origin/main a72ae19952): rc 0, tree 8a799f8471, no conflict.
- Previous block (evidence-cut), constraint 1, is restored. The head README contains "has not refuted it, and says which they could not separate." It reads exactly as at the merge base. `git grep -F` gives 0 hits at e3df1f1c and 1 at the head (`ev/restored.txt`, `ev/body-figures.txt`).
- Constraint 2 is restored. The rotation bullet again states about 150 k for mechanical and relay seats, about 300 k for designers, pre-studies, root-cause and plan seats, and about 500 k for the orchestrator. Fixers, reviewers and standing seats point to `fixer.md:10` (~150 k S/M, ~300 k L/XL), `fix-review.md:8` (~150 k) and `standing.md:39` (about 150k). Those lines state exactly what the base bullet gave those seats, so no seat class from the base bullet is left without a size. The base bullet's example list "(rca, fix, handoff)" is dropped. That list is an illustration, and `fixer.md:10` still carries it.
- Constraint 3 is restored: "A seat re-running a retired one repairs it first." appears at README:274, worded as at the base.
- The re-payment cuts two trap bullets. Each has a surviving copy at the head (`ev/cut-traps-copies.txt`):
  - plan_view/HPO_PLANDATA. `tests/README.md:390-394` covers the per-checkout `/tmp` default, says `card.mjs` alone falls back to an unhashed default with a warning, and says every other Node harness requires the variable. `dev/audit/README.md:193` says the harness sets a private `HPO_PLANDATA`.
  - env_drift. `tests/README.md:298-310` covers the worktree of a reference commit, the refusal of a ref that resolves to `HEAD`, and that refusal's two consequences. The cut bullet also said the worktree is added "in the repository it is run from", and no other text states that, but it follows from the mechanism and binds no seat.
  - Neither cut changes what a seat must do.
- Previous finding, the enumerator-2 literal, is resolved in the group's own seam. The one-liner now reads `roster_lib.FINISHED_STAGES` (= DONE_STAGES + absorbed, `roster_lib.py:89`) plus `refused`. Control in a scratch tree with groups A rca-done, B done, C refused, D fixing: the head line prints only `D fixing`. Mutant, the old literal `('done','absorbed','refused')` put back: prints `A rca-done` and `D fixing`. So the change is what removes the false line. At the head roster it prints 46 lines, rc 0 (`ev/enumerator2.txt`). I did not re-run the body's `deferred`+`absorbed` control separately. My control covers the same set membership.
- Budgets. I ran `node tools/policy/policy_lint.mjs --budgets` at the head (`ev/budgets-head.txt`) and on origin/main merged with the head (`ev/budgets-merged.txt`, tree 229d5d9d49). The touched README, listed as `tools/audit/README.md`, is at 312 lines / 6049 tokens against caps 321/6059 at both. The corpus is ~68947 against 68618 + 500 = 69118. Role record is 7428 and role policy 10014. Both runs exit with rc 0. `policy_lint.mjs` reports `TOTAL: 0 error(s) across 51 policy file(s)`, and `brief_lint.mjs` reports 0 errors. No cap, band or `*_budgets.json` is touched.
- Body figures: each reproduces at the head.
  - Line refs: README:70/71/274/283.
  - The grep counts at e3df1f1c and the head.
  - The role contract caps: designer 877/878, root-cause 998/998, architect-planner 1261/1261, plan-review 304/304. These support the body's reason for keeping the sizes in the playbook.
  - The 312 `wc -l`.
- Mutation: none, because the change is prose. The enumerator mutant above is mine.
- VERSION, the manifest and the notes heading are untouched; the delta touches one file.
- CI: `merge_train.py owed-reds` is in `ev/owed-reds.txt` and the classify polls are in `ev/classify-log.txt`.
- CI: the last classify line is `GREEN 820236749a878893f6217210683b16aefac89657 pending: none red: none` (`ev/classify-log.txt`), and `refs/pull/3600/head` is still 820236749a at that read. The packet's `introduced-red` refusal (instrument-self-tests in_progress) is cleared: that job concluded success at 00:30:36Z. `tests / nightly-status` reads failure, but it is not in `owed-reds` (`ev/owed-reds.txt`), so it is not this PR's red and is owed no answer. The early `gate` failure at 00:12 was superseded, since classify reads the required set GREEN. I re-ran no heavy job.
- RESULT: previous block evidence-cut resolved (3/3 constraints restored); previous finding enumerator-2 resolved (mutant reproduces the false `rca-done` line, the head does not); re-payment cuts 2 bullets, each with a surviving copy; budgets at head and merged with origin/main within caps (312/321 lines, 6049/6059 tokens, corpus 68947/69118).

## Findings

None new. The previous verdict's finding is settled in this PR (see Evidence).
