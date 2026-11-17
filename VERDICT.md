Fix review: merge aaf3c780f126b2268e009a00734d2cc9976ef70f

bus-nonce: f83e0825d3c7d17f40e7133ddc85acf6
pending-ci: governance / instrument-self-tests, governance / policy-docs, governance / wave-script, arch-score / arch-score, codeql / Analyze (python), tests / fast (3.14), tests / closures, tests / browser, tests / coverage, tests / typing, tests / arch-instrument

Round 1 (first review; no --reviewed-head). Scope: full three-dot diff at `aaf3c780f1` against merge base `2d7161a4b7`: an RCA document (`dev/audit/rca/R11-RCA-SELFTEST-TABLE-DRIFT.md`), its measurement harness (`dev/audit/harnesses/r11_selftest_static_edge.py`), one `inert_reads` entry in `tests/closures.json` and the delivery row. No `custom_components/`, tool, policy or workflow line changes.

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main aaf3c780f1` exits 0 against origin/main `38bf516bdd` (re-run at return; head unchanged at `aaf3c780f1` per `git ls-remote`) (ev/merge-tree.txt); no conflict, no claim-file driver invoked.
- RESULT roles current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- RESULT step 1 (mutation): no production line is named or changed; the diff draws no mutant (`tests / mutation` success at this head). The harness is measurement, so its mutation proof is a perturbation instead: disabling its Python-import scan (`if path.endswith(".py")` set to `if False`) moves the C1 figure from 14 to 11 true flags and from 333 to 325 unique flags. So the harness moves under its own perturbation.
- RESULT truth set re-derived: added (step, kind, path) triples from the table at `e352724335` to the table at `142926ec66` = 67 (45 files, 13 dirs, 9 probes) across 20 steps, 0 removed (ev/truth.py, ev/truth_67.json). Matches the body and the RCA §1 and §5 ("20 drifting steps").
- RESULT C1 re-run: the committed harness, run per merge over `git rev-list --first-parent 5aaf9c112f..e352724335` (15 merges, confirmed), each against its own table: 412 per-merge lines, 333 unique flags, 14 of them in the truth set, maximum 119 at `367c3b9cac` = #3641 (ev/c1_flags_per_merge.txt). All four RCA figures reproduce exactly.
- RESULT attribution (§1): under the RCA's stated rule (`git log --first-parent --diff-filter=A 82e301585d..e352724335 -- PATH`): #3622 14, #3644 8, #3625 7, #3627 3, #3641 2, #3651 none. #3640 gives 8 under the literal rule because the pre-existing directory `tests` (a `dirs` and a `probes` entry of `gantt-and-verdict-audit`) matches any file added under it. Exclude those two, which the tree already had, and #3640 is 6, the total attributed 40 and older 27, as stated.
- RESULT merge rate: 77 first-parent merges on origin/main from 2026-11-14T15:40Z to 2026-11-16T15:44Z, as stated. #3622 merged `56ce2f695b` at 04:16:31Z and #3652 `5aaf9c112f` at 04:20:41Z (RCA says :42, the GitHub merge-time rounding; four minutes holds).
- RESULT cause citation: `governance.yml` at `e352724335` line 313 sets `SELFTEST_TRACE` only for `github.event_name == 'push'`; line 1592 gates on it, as the RCA says (the drift step's `if:`).
- RESULT null control (step 3), proxy: run 43884631892's artifact was not downloaded (no `gh run download` in this seat). Using `142926ec66`'s table as the artifact proxy (the RCA §6 states that commit is that artifact committed): `selftest_scope.drift` with the table at `e352724335` gives 27 refusals, and with `142926ec66`'s table gives 0. Dropping one file from the proxy-matched table gives 1, so the control moves. The artifact-exact run is the fixer's.
- RESULT step 4/5: no golden, claim file, `VERSION`, manifest or notes heading in the diff.
- RESULT step 14: the only moved instrument number is one `tests/closures.json` `inert_reads["tests/harness_headers.py"]` entry naming the new harness. That is the harness-header lint's read of a new file under `dev/audit/harnesses/`, so the entry is earned by adding the file and goes away with it. `tests / closure-scope` is success at this head. Locally `tests/harness_headers.py` cannot import here (`homeassistant` is absent in this seat), so CI is the record.
- RESULT step 7 / 12: the PR body's `## Head` names `af67d6a221`; the head is `aaf3c780f1`, a `ci: merge main` on top. `review_carry.py af67d6a221 aaf3c780f1` prints `CARRY` (0 of 1 branch-only commits are non-merge) (ev/review_carry.txt). So the body head is carried to this head.
- RESULT step 6 (class): this PR is an RCA and opens no fix seam; the class it names (additions to the self-test read table) is routed to C5 below, not settled here.
- RESULT owed reds: `merge_train.py owed-reds` read; no owed check is red at this head as read (see CI line).
- Not re-derived: the 54-of-55 drift-step conclusions over 80 push runs, the hotfix open times (62/64/105/129/152 min), the job wall times (18.9-23.8 min untraced, 38.5-71.7 min traced), and the directory-listing variant's 384 flags. That variant has no committed harness. My own reading of its stated rule ("a file the diff adds under a directory the step lists") gives the same recall, 8 of 45 file reads, but 4011 unique flags, not 384. Its flag count rests on an uncommitted definition, which does not change the verdict (refused either way).
- CI: `merge_train.py classify aaf3c780f1 --pr 3684` printed `WAIT aaf3c780f126b2268e009a00734d2cc9976ef70f pending: gate red: none` on every poll from 00:25 to 00:53Z (ev/classify.log). No check run at this head is red. Completed success at return: tests / mutation, tests / closure-scope, tests / briefs, governance / env-matrix, budget-raise-gate, hassfest, validate-hacs, codeql (actions, javascript-typescript), and on the earlier run of the same head arch-score and governance / policy-docs. Still queued or running: the `pending-ci:` set above. The relay posts this verdict only once those are green.

## Findings

- Follow-up: paperwork: the RCA's owed follow-ups (the `bugclasses.json` entry for the additions class beside `R10-SELFTEST-TABLE-SHRINK`, and C5's red-then-green demonstration with its green-push null control) are routed to proposal P-R11-41, which is not in the tree; the body's `## Forward-carry` says none. They belong to the group that builds C5, the unbuilt half of R11-PRE-SHARED-FILES's countermeasure A. Carry: R11-PRE-SHARED-FILES
- Note: figure: "about 22 flags per merge" is unique flags over 15 merges (333/15); per-merge lines average 27.5 (412/15). It is a wording point in a refused detector's cost and does not change the verdict. Carry: R11-PRE-SHARED-FILES | dismissed: wording only, verdict unaffected
- Note: harness-missing: the directory-listing variant (8 of 45, 384 flags) has no committed harness; its flag count could not be re-derived (my reading gives 4011). Carry: R11-PRE-SHARED-FILES | dismissed: refused detector, verdict unaffected

## Friction

none
