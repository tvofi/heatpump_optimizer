Fix review: blocked 7033a7e40a3af1d1b8f06ebaf060b073748b561c census-misclassified: the previous round's block stands unresolved because CENSUS.md and main_reds.py are byte-identical to 23d7ac26, and the only delta is a clean main merge plus the delivery row. tests / ci-ratchet is still called a product check, and the 17 required contexts are still neither enumerated nor classified.

bus-nonce: ed76e4c5ba59e7e5de90616afe613839

## Block

This is the second round, a delta over the reviewed head 23d7ac26f4d64451839c64d83565e961428bbac4. `git diff 23d7ac26 7033a7e4 -- dev/audit/rounds/round10/protection-census/` is empty (ev/own_delta.txt). The re-cut the previous block sent back was never made, and both of its items still hold at this head:

1. **`tests / ci-ratchet` is classified on its name.** CENSUS.md lines 23-24 still say it is "a product check in either". `.github/workflows/tests.yml` at this head still defines it as push-only, `github.event_name == 'push'`, with the comment "Not a required context" (ev/tests_yml_ci_ratchet.txt). It is also absent from the 17 contexts in `tools/ci/fixtures/ruleset/ruleset_23698884.json` (ev/required_contexts.txt). The census still uses this misclassification to set aside all 28 main-push rows.
2. **The required set is still neither enumerated nor classified.** None of the 17 contexts is classified by what it reads. The only partition is still the three-name "B1 drop list" (CENSUS.md lines 58-61), and that list has no source in the tree. This classification needs no API token, so UNREAD does not excuse it.

## Findings

- The PR body's Figures still cite `python3 -I dev/audit/rca/ci-red/entries.py` as printing "ENTRIES 18 PRS 14". Run with no arguments at this head, it raises IndexError. Only `tail -1 dev/audit/rca/ci-red/entries_v7.1.2.tsv` prints `ENTRIES 18 PRS 14` (ev/entries_rerun.txt). Carry: dismissed: owed by the fixer in the re-cut this block sends back
- CENSUS.md line 52 still says "5 `harness_headers.py` reds", but the ledger holds 4 such rows (ev/entries_rerun.txt). Carry: dismissed: owed by the fixer in the re-cut this block sends back
- CENSUS.md line 19 still classes the six cancelled runs from the run's conclusion, as "cancelled runs 4036-4045". The previous verdict found the `tests / ci-ratchet` job concluded `failure` in each of them, and the range spelling still reads as ten runs. Carry: dismissed: owed by the fixer in the re-cut this block sends back
- CENSUS.md line 68 still has "~560 round-10 delivery rows" with no enumerator. Carry: dismissed: owed by the fixer in the re-cut this block sends back

## Evidence

- Head measured: 7033a7e40a3af1d1b8f06ebaf060b073748b561c (ev/HEAD.txt). It is the same as the PR's live head and the head the body names.
- Delta: the main merge 2c80348407 has parents 23d7ac26 and fc2a7edc. Its tree fb3c34b4 equals `git merge-tree --write-tree` of those parents, so it was resolved mechanically. Commit 7033a7e4 adds only `dev/programme/delivery/3503.md`. The `custom_components/` lines in the delta are main's own and come from no resolution in this branch, so the review is not widened (ev/merge.txt).
- Merge with origin/main 5365b184: `git merge-tree --write-tree` exits 0, no conflict (ev/merge.txt).
- CI: `merge_train.py classify 7033a7e4 --pr 3503` gives `WAIT ... pending: gate red: none`, rc=3 (ev/classify.txt). No red is owed an answer. The block rests on the census content, which no CI outcome changes, so I did not wait for green.
- Mutation proof: not applicable. The branch diff against the merge base is CENSUS.md, the read-only `main_reds.py` and the delivery row, with no production line.
- The previous round's re-derivations were not re-run, because the files are unchanged: 28 main-push rows and a null control of 0 rows. carry_audit at head: 1 routed, 0 unrouted (packet).
