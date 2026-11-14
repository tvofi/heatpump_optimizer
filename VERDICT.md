Fix review: blocked d9677a53d55bcf114086b15ab97588b7fb429b22 ci-red: instrument-self-tests step introduced at this head (classify RED)

bus-nonce: f22d500815d37b0357c615861e80163d

## Block

`python3 tools/audit/seat/merge_train.py classify d9677a53d55bcf114086b15ab97588b7fb429b22 --pr 3566` exited 1 at 01:44:48Z with `RED d9677a53d55bcf114086b15ab97588b7fb429b22 pending: gate red: none introduced: 1` / `INTRODUCED Show the supervised beat refusing its own fixtures` (`ev/classify.out`, `ev/classify.log`). That step is `governance / instrument-self-tests` (job 132279759403) in the workflow_dispatch run 43540443641 at this head. Its log ends `FAIL wrapper: its UNTRACED list is UNGATED` and `selftest_scope self-test: 117 checks, 2 failed`. Under fix-review.md step 11, an instrument-self-tests step that is red at the head and not at the merge base is the pull request's finding and a block.

Two measurements limit what that red means:
- The same step was green at this same head in the pull_request run 43535827415 (job 132264734198, `success`).
- `python3 -I tools/ci/selftest_scope.py --self-test` prints `117 checks, 0 failed` locally at both the head and the merge base (`ev/selftest_scope.txt`).

So the red does not reproduce from the tree alone. It depends on that run's context, such as the dispatch event or the SELFTEST_TRACE/scope environment. Read the first FAIL line of job 132279759403 and settle it before re-review: either the diff or the dispatch path is the cause (repair it), or the run is re-run green at this head.

The pull_request code run 43535827415 is also red at this head on `tests / fast (3.14)` ("1 TEST SCRIPT(S) FAILED"; the script was not named in the tail I read), `tests / closures` ("1 closure(s) are stale. Re-derive the named script"), `tests / closures-autofix`, `pr-contract / pr-contract` and `gate` (`ev/head_red_jobs.txt`). All five are in the owed-reds set (`ev/owed_reds.txt`). The body's `## Red checks` answers only the earlier `tests / closures` INERT READS red at 1c2963ed0a. The dispatch run re-running fast, closures, coverage and arch-instrument was still in progress at verdict time, so the root-cause trigger is not graded here (step 11: only once the head's workflows have concluded). The repair round answers each red that remains in `## Red checks`.

## Round

First round, full review, at head d9677a53d55bcf114086b15ab97588b7fb429b22 (merge base e23124ff6e45bac1d48b4a775dad555a37965355), from a detached worktree at that head. Apart from CI, the review found no defect in the diff; the measurements below carry to the next round if the head does not move, or by its delta if it does.

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main d9677a53d5` exits 0, tree 82ff1032b2, stderr `LEDGER-MERGE: resolved tests/closures.json`; no conflict.
- RESULT role contracts: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract read is current.
- RESULT enumerator (body's null control, same pathspec): 42 lines in 19 files at the merge base, 1 line at the head (`dev/governance/config/policy_budgets.json:130`, the kept `files_tokens` cap `tools/audit/briefs/nudge.md: 3814`). Matches the body. `ev/HEAD.txt` names the head.
- RESULT VERSION, manifest, RELEASE_NOTES: untouched (three-dot diff names none). Claim files untouched; the diff moves no golden fixture, so `env_drift.py` has nothing to grade.
- RESULT self-tests at head (`ev/head_checks.txt`): postmerge 22/0 failed, budget_raise_gate 280/0, sweep_render 38/0, orchestrator_tick 317/0, roster_edit 294/0; `policy_lint.mjs` TOTAL 0 errors across 50 policy files; `rules_sync.mjs --check` RULES-SYNC ok; `tests/structure.py` STRUCTURE RATCHET PASSED; `tests/layout.py` ok. Locally `tests/doc_claims.py` 348 checks passed, `tests/closure.py selftest` 118 passed, `tests/deployment_shape.py` passed (`ev/local_scripts.txt`).
- RESULT mutation proof, re-run by me (`ev/mutants.txt`), each restored: G1, the `files_tokens` CAPFILE schema line deleted, gives budget_raise_gate 1 failed. P1, `handed()` returning `[]`, gives postmerge 1 failed (null control). P2, `standing-merge.md` made to hand `state_docs.py --push`, gives 1 failed (CARRY 3). P3b, `orchestrator.md` section 11 made to hand `roster_sync.py --apply`, gives 2 failed. My first P3 used `roster_edit.py`, which `steps()` does not run, so 0 failed is correct: an invalid mutant, not a survivor.
- RESULT metric earned (step 14): `corpus_tokens` is re-recorded down from 68618 to 64899. `policy_lint.mjs --budgets` measures 64893 at the head and 68707 at the merge base. With `nudge.md` restored and staged at the head it measures 68701, above cap+band 65399. So the drop comes from the deletion, not the instrument. The other aggregate caps are not moved; their measured values sit inside cap+band.
- RESULT budget-raise-gate at head: success (job 132264727378). G1 kills the grader's production line.
- RESULT forward-carry (step 10): the body's `Carry: R11-INTAKE-R10-RESIDUE` item is in the tree on `handoff/audit-r10-roster` at 07bb98384d3de872c77a8c77baec845a8bef6f37, `dev/programme/rosters/wave-r10-groups.json`, group R11-INTAKE-R10-RESIDUE, carry 80. It states the control (a `files` orphan cap is refused, a `files_tokens` one passes) and a re-measure instruction. The body names the group but not the roster branch SHA. carry_audit: 1 routed, 0 unrouted, rc 0.
- RESULT finder's harness: none named. This is a retirement and re-pointing group from an owner instruction, so there is no finder's harness to run at both ends. The enumerator above is the measurement, run by me at both ends.
- RESULT step 15: the added lines are comments, self-test checks, one schema rule and data edits. No breach found.
- RESULT policy: this is a policy change (CLAUDE.md, gate-scoping.md, policy_budgets.json). It merges only on the owner's approving review or under mandate 6715477401's policy scope; this verdict approves nothing.
