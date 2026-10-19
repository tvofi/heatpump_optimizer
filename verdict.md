Fix review: merge 8f3e72f46da197b64a923c73054c450c8ccf699d

bus-nonce: 7187588c51a236847e5a757959cdb84c

Round 1: no earlier `Fix review:` comment on #2456. Contract: fix-review.md read from origin/main; `git diff 5b9c33d58...origin/main -- dev/governance/roles/` is empty, so it is current.
Measured head: 8f3e72f46da197b64a923c73054c450c8ccf699d (ev/HEAD), merge base 5b9c33d58, origin/main f118e2644. The PR API reported this head again before posting.

## RESULT lines

- RESULT stamp_self_test=pass at head (ev/selftest_head.txt)
- RESULT stcov=pass at head; RESULT stcov=fail with origin/main's stamp.py, naming the same twelve MAY-DRIFT UNCOVERED names the v7.0.1 refusal printed (ev/stcov_block.py, my own copy of the new entities block run alone)
- RESULT deleted=41 restored=12 stale=7, verbatim_blocks=19/19, first_lines_equal=True 19/19 against `git show v7.0.0:tests/golden/claimed_drift.txt` (ev/verbatim.py, ev/verbatim.txt)
- Stale notes: each of the 7 dropped notes (valve_storage_smart_write, wood_two_tank, wood_two_tank_smart_write, wood_coil, valve_upper_direct_slab, winter_two_zone_no_dhw, valve_storage) has a live `# may-drift:` entry whose line equals the note's tail. Nothing is lost, and a note is dropped only when its live entry exists. Mutant M2 below shows this.
- Simulated stamp: a scratch bare origin whose main is origin/main plus a `--no-ff` merge of this head; notes listing all 178 first-parent PR numbers since v7.0.0; `stamp.py --bump patch --title simulated --allow-red --allow-rowless`, needed because the scratch head has no CI run and its merge has no row. Output: `41 claim(s) deleted`, `12 suspended may-drift entries restored verbatim`, `7 stale suspension note(s) dropped`, `claims self-check: claims hygiene: HEAD^1 ok`, `RESULT stamped=v7.0.1 tag_pushed=false`, exit 0. On the stamp commit, `env_drift.py --claims-only HEAD^1` gives `claims hygiene: HEAD^1 ok`, exit 0 (ev/sim_stamp.txt, ev/sim_claims_only.txt). The stamp commit's claim file equals my offline rewrite apart from the title.
- `env_drift.py --claims-only origin/main` at head: ok, exit 0. tests/golden/, VERSION, the manifest and RELEASE_NOTES.md are byte-identical to the merge base (step 5).
- `git merge-tree --write-tree origin/main 8f3e72f4`: exit 0, tree 395086d9, no conflict. main since the base touches neither stamp.py nor the claim files.

## Mutation proof (steps 1 and 14; ev/mutants.py, ev/mutants.txt)

| mutant | self-test | new entities check |
|---|---|---|
| M1 the PR's own: `restore_suspended` call in `rewrite_claims` -> `pass` | fail, exactly the 3 checks the body names | fail, MAY-DRIFT UNCOVERED, 12 names |
| M2 stale notes restored too (no live check) | fail, 2 checks | pass |
| M3 missing tail tolerated | crash, rc 1 (AttributeError on None) | pass |
| M4 two notes for one name tolerated | fail ("two notes") | pass |
| M5 head/tail name mismatch tolerated (`if not tail:`) | **pass, survives** | pass |
| M6 entry not verbatim | fail, 2 checks | pass |
| M7 continuation line dropped | fail, 3 checks | fail |

The CI mutation lane drew no mutant: `MUTATION TABLE -- scope changed: no production code line added or modified`. So the table above is the only mutation evidence.

## Body figures (steps 7 and 8)

I re-derived each figure at this head:
- 19 notes, 7 live, the 12 names: confirmed.
- 41 claims, all deleted: confirmed.
- 39 card claims deleted: confirmed.
- The three self-test names under M1: confirmed.
- `blocks checked 19 all verbatim`: confirmed under my own block definition. A block is a first line plus the comment lines that follow it, up to the next entry, a note, or a bare `#`. The fixer's scratch script is not in the tree, so I did not run it.
- The body's head SHA: matches.

## Checks (step 11)

The check-runs API on this head shows no red check (ev/check_runs.tsv). `fast (3.14)` is SCOPED and ran tests/entities.py; both `stamp.py's --self-test passes` and the new `...covers every allowed may-drift name` check are `ok`. Red checks: none, so nothing needs a root-cause answer. At 18:37:50 UTC there were 46 runs. All are success, skipped or neutral except `closures` (job 118230804141, started 18:25:59), which was still in progress. coverage succeeded at 18:25:55 and Analyze (python) at 18:35:21. `closures` is a heavy CI lane, which I cite and do not re-run. The orchestrator should confirm it is green before merging.

The second `merge-tree` was against origin/main at 8b14bcecc, after main moved by three record commits. It exits 0, tree 18a9e083, with no conflict (ev/merge_tree.txt).

## No check weakened

The diff only adds to stamp.py. Its 3 deleted lines are a docstring sentence and one call, which moved into a `try` that converts a `ValueError` to `Refuse("claims")`. entities.py gains one check. No env_drift rule changed.

## Observations (none blocks)

1. M5 survives. The `tail.group("name") != name` arm of the refusal has no test. If a hand-edited note's head and tail named different fixtures, the code would still restore the tail's entry under the head's name. The stamp's own claims self-check would still refuse afterwards, because the head's name stays uncovered. So this is a gap in the self-test, not a hole a stamp can pass through. One `_bad` case would pin it.
2. The stamped claim file keeps the 24-line R10-PUMP-MODEL reason paragraph, which says the entries are "suspended above for this release". main's stamp would have deleted it as reason-block text. The head ends the reason block at the restored flat_prices entry, as its docstring says it does. The R10-RATIO-SITES and R10-SAV-BASELINE paragraphs below the claims survive under both stamps, which is existing behaviour. No check reads this prose, but after v7.0.1 it is stale record text in the claim file. A later branch should tidy it; that is not this PR's.
3. The 12 restored entries come back at their suspension positions, not in v7.0.0's order. Each block is verbatim, and nothing depends on order.
4. Roster R10-STAMP's second carry (R10-ROSTER-FASTPATH: restart the state-docs beat after #2406) is not dispositioned in the body. It is an orchestration step, not this diff's. carry-201's remeasure line still tells the stamping seat to restore suspended entries by hand before stamping. The body dismisses that line as superseded, but the text stays in dev/programme/carries/carry-201.json for the orchestrator to update.
