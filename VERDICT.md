Fix review: blocked 23d7ac26f4d64451839c64d83565e961428bbac4 census-misclassified: tests / ci-ratchet is called a product check on its name, but it is a push-only, non-required job that reads CI run timings and archscore. The 17 required contexts are never enumerated or classified, so a round-11 seat cannot size a product-only set from this study without redoing it.

bus-nonce: bee3ead43d1d8c47ead530150641d86f

## Block

1. **A check is classified on its name, not on what it reads.** CENSUS.md, "Main-push reds", says the main reds "say nothing about a product-only set, since `tests / ci-ratchet` is a product check in either". That is false on three counts:
   - The job is defined at `.github/workflows/tests.yml:2303`. Its comment at 2301-2302 says it runs only on push to `refs/heads/main` and is not a required context.
   - The `tests/ci_ratchet.py` docstring (lines 1-40) says it measures CI cost and archscore: `script_runs_per_push`, `critical_path_minutes` from Actions run timings, and archscore counts. That makes it a programme instrument.
   - It is absent from the 17 required contexts in `tools/ci/fixtures/ruleset/ruleset_23698884.json`.

   The census uses this misclassification to set aside all 28 main-push rows. Correctly classified, those rows are reds of a programme instrument on main: exactly the class a product-only set is meant to stop grading. (ev/tests_yml_ci_ratchet.txt, ev/ci_ratchet_docstring.txt, ev/required_contexts.txt)
2. **The census does not do what its topic asks.** The study is supposed to sort the required checks into those that protect the product and those that protect the programme's own instruments, to size a product-only required set. CENSUS.md never lists the required set (17 contexts: fast, browser, briefs, closure-scope, closures, typing, hassfest, validate-hacs, policy-docs, wave-script, pr-contract, env-matrix, three CodeQL Analyze, mutation, budget-raise-gate). It never classifies any of them by what it reads. Its only partition is a three-name "B1 drop list" (briefs, policy-docs, wave-script). That list has no source in the tree: no tracked file defines B1 as dropping those checks. Two consequences follow:
   - "CodeQL stays outside B1's drop list" cannot be checked.
   - A round-11 seat would have to redo the whole census. This classification needs no API token, because each check's workflow step is in the tree, so UNREAD does not excuse it.

## Findings

- The body's enumerator for "18 entries over 14 PRs" does not run as written. `python3 -I dev/audit/rca/ci-red/entries.py` with no arguments raises IndexError, because it needs `W.json ci-red` and the window cache is not tracked. The figure is right, but only `tail -1 dev/audit/rca/ci-red/entries_v7.1.2.tsv` reproduces it (`ENTRIES 18 PRS 14`). CENSUS.md's source table and the body's Figures need that enumerator instead. Carry: dismissed: owed by the fixer in the re-cut this block sends back
- "5 `harness_headers.py` reds sit in `tests / fast`" is wrong. `grep -c harness_headers entries_v7.1.2.tsv` prints 4: #3180, #3189, #3208, #3242. Carry: dismissed: owed by the fixer in the re-cut this block sends back
- The six cancelled runs are classed "infrastructure (concurrency cancel)" from the run's conclusion. In every one of them (4036, 4037, 4038, 4040, 4044, 4045) the `tests / ci-ratchet` job itself concluded `failure`, not `cancelled`. The class has to come from the job, and the cause is as UNREAD as for the 8 failed runs. The text "4036-4045" also reads as a ten-run range where six runs are meant. Carry: dismissed: owed by the fixer in the re-cut this block sends back
- "14 PRs of ~560 round-10 delivery rows": the ~560 has no enumerator. `dev/programme/delivery/` holds 1614 files across all rounds. Carry: dismissed: owed by the fixer in the re-cut this block sends back

## Evidence

- Head reviewed: 23d7ac26f4d64451839c64d83565e961428bbac4 (ev/HEAD.txt), from a detached worktree. No pull request exists yet, so there is no review packet and no CI run to read. Red checks: none to answer.
- Merges cleanly: `git merge-tree --write-tree origin/main <head>` gives tree fb3c34b4…, exit 0 (ev/merge-tree.txt).
- Mutation proof: n/a is accepted. The diff adds only CENSUS.md and the read-only `main_reds.py`.
- Re-derived: `main_reds.py | wc -l` gives 28 (14 `tests / ci-ratchet` and 14 `gate`; 8 failure runs and 6 cancelled runs), matching the census (ev/main_reds.tsv).
- Null control re-run: runs 4080, 4107 and 4116 are success and yield 0 rows, matching the census.
- The class table counts real catch 9, infrastructure 7 and grader skew 2. That matches the table as written. The PR/head/red columns match entries_v7.1.2.tsv row for row.
- Not re-derived: `tests/entities.py` classification of the two new files (the import fails here without homeassistant; CI will judge it once the PR opens). The per-head API reads stay UNREAD, as the census says (no token in this seat either).
