Fix review: blocked c766208d486edd8f80323d615af802c08aa5c3ce mutation-vacuous: gate_name_any, report_record_dropped, first_by_input_not_t, named_regex_no_merged, ratchet_rc_ignored, dedup_dropped

bus-nonce: 1338063c72ed67311b29efe738cf8e86

## Block

Round 1. Handoff review of c766208d486edd8f80323d615af802c08aa5c3ce (this is also the body's `## Head`), done before any pull request exists. The body says there is "one mutant per predicate of `scorecard.py`". The self-test's own 22 mutants are all killed (ev/scorecard_selftest.txt). I planted mine with ev/harness/mut.py, running `scorecard.py --self-test --no-mutants` on a temp copy (ev/reviewer_mutants.txt). Six of them survive. Four are predicates of the section-7 rules, and on planted inputs each one changes a printed figure (ev/survivor_wrong_outputs.txt):

- gate_name_any: `if j["name"] == "gate":` -> `if True:`. A_gate goes from 12/16 = 75% to 7/16 = 44%: the line reads whichever job is last in the listing instead of the job named `gate`. This is the rule that separates A_gate from A_run. The self-test's job listings hold only a `gate` job, so a listing that also has a failed job after `gate` would kill this mutant.
- report_record_dropped: in `report()`, `line_ck(runs, rd(record) if record else None)` -> `line_ck(runs, None)`. Through the CLI with `--sweep-record`, K goes from `K 4` to `K unread`. No case calls `report()` with a record. The beat row's test checks only that the flag is passed, not that K reads it.
- first_by_input_not_t: the window of `line_review` is taken in input order instead of sorted by first-verdict time. On the same verdicts shuffled (ev/harness/demo.py, `st7u`), Y_rev goes from 20/50 to 19/50, M_first goes from 18/50 to 19/50, and the printed span runs backwards.
- named_regex_no_merged: `MERGED` dropped from the train-naming regex. Y_train goes from 35/50 = 70% to 3/23 = 13%. Every planted PR is also named on a SKIP, PARK or BATCH line, so the self-test cannot tell what a pull request named only on a `MERGED` line does.
- ratchet_rc_ignored (`json.loads(out) if rc == 0` -> `json.loads(out)`) and dedup_dropped are listed because my driver reported them. I judge both equivalent. `machinery_ratchet.py --measure` prints its JSON and nothing else, and an empty stdout already ends as `ratchet unread`. Removing the de-duplication cannot change any PR's first verdict, which the body already says. Neither needs a new case if the body records it as equivalent.

Same seam, which the re-cut should settle as well: `line_review` takes "first verdict" as the first in file order, not the earliest by `t`. The same verdicts in shuffled order print Y_rev 20/50 against 16/50 when sorted (ev/survivor_wrong_outputs.txt against ev/finder_reference_vs_head.txt seed 7). The study's reference script behaves the same way, so this is inherited. But section 7 defines the line "by first verdict", and neither the docstring nor `instruments/scorecard.py.md` says verdicts.json must be time-ordered. Either sort the verdicts by `t` before de-duplicating, or state the ordering precondition and pin it in a case.

Re-cut: add one case per surviving predicate above, so that each mutant goes into `MUTANTS` and is killed, and handle the ordering point. Then re-run steps 2-8 of `fixer.md`.

## Findings

## Evidence

- RESULT finder harness: I ran the study's reference `scorecard.py` (origin/study/r10-mach-scorecard 4db0564af0, with only its `W` path made an environment variable) and the head's `report` on the same planted state, two seeds (ev/harness/gen.py, cmp.sh). A_gate, A_run, Y_rev, M_first, Y_train, H and E match figure for figure (ev/finder_reference_vs_head.txt). The reference computes neither S nor C, K. I checked those against independent enumerators instead: C and K against a hand count of the planted record (4 recycle lines of the dispatch/triage seats), S below. There is no baseline end: the instrument does not exist at merge base 14f227c5bd. That is flat by construction.
- RESULT one wrong input per figure (ev/plant_one_wrong_input_per_figure.txt, ev/harness/plant.py): each plant moves exactly the line it should. A_gate: one gate conclusion flipped, 75% -> 69%. A_run: 35% -> 40%; A_gate moves with it, as the rule says. Y_rev: 16 -> 17. M_first: 23 -> 24. Y_train: 35 -> 34. H: 20 -> 21. E: outside 10 -> 11 and open 8 -> 9. C: 2 -> 10; A moves too, because the window shifts. K: 4 -> 5. S: a commit adding a 100-line file under `tools/` on a scratch clone's origin/main moves machinery from 182931 to 183031 (+100). The ratchet line stays flat, correctly, because that commit is not a merge (ev/S_head.txt, ev/S_plant.txt).
- RESULT S enumerator: `git grep -c '' origin/main -- tools .github .claude dev/governance | awk -F: '{s+=$NF}'` prints 182931, and the same over `custom_components blueprints` prints 100305. These equal the head's `S machinery 182931 / product 100305 = 1.82`. The ratchet line equals `machinery_ratchet.py --measure --head origin/main` (fc2a7edcf2): 489 per 580, churn 11939.
- RESULT self-tests at head: `scorecard.py --self-test` is ok with mutants, 22 of 22 killed. `beat_jobs.py --self-test` ran 203 checks with 0 failed, and the three scorecard row mutants were killed (ev/beat_selftest.txt).
- Body `## Figures` says none. The scorecard's figures come from out-of-tree inputs, so I re-derived them on planted inputs only. I did not run the live baseline (section 7's 2026-11-11 column) because the session inputs under `S/scorecard/` are not in the tree.
- Null controls: covered by the self-test cases above, re-run on the unmodified tree. H has none, as the study's text says.
- `git merge-tree --write-tree origin/main c766208d48` exits 0 (tree 735b8114fb). Its stderr reports `LEDGER-MERGE: resolved tests/closures.json`, and there is no conflict (ev/merge_tree.txt).
- `tests/structure.py` passes the structure ratchet (ev/structure.txt). I could not run `tests/entities.py` here because it needs `homeassistant`, which this container lacks (ev/entities.txt). CI owes that check.
- `selftest_scope.py select` at merge base..head selects `scorecard`, `beat-job-rows` and `beatd` (ev/selftest_scope_select.txt).
- No pull request exists, so there are no checks, no CI, no review packet and nothing to wait on. No red can be owed (owed-reds set in ev/owed_reds.txt).
- VERSION, the manifest version, RELEASE_NOTES and both claim files are not touched in `git diff 14f227c5bd...c766208d48`.
- Body `## Forward-carry` says none. The `## Friction` line carries `dismissed:` with a reason. The enumeration class is a single instrument, so there is no class to open.
