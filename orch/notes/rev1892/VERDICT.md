Fix review: merge c16d751e2b8df1ebc9f106c85e9a747687b50816

Round 2 (the round-1 block was honored with a re-post, not a repair on a moved branch). All round-1 scope re-measured at head c16d751e2 / base origin/main 283eb22f0 (the r9-fr-2 merge, which edits policy_lint.mjs, so both ends sit on the merged tree), 2026-10-04T13:2x-14:05Z, finder's commands; evidence/ on this box carries the outputs.

1. Byte-identity holds at the new ends: `--stats --since v6.7.16` whole output IDENTICAL base vs head; `--since v6.7.14` exact-id rows and every `CENSUS\tverdict class`/`CENSUS\tfriction rule id` line IDENTICAL (my own diff); the only deltas are the two additive family rows, CENSUS 30 -> 32 key(s), and the one new would-open. RESULT: byte-identity confirmed.
2. Figures reproduce at the new windows: s14 base quiet on the family, head `4 / 5 mutation (family) <- at or over threshold`, exactly one new would-open, WOULD OPEN 5 -> 6; s13 head `5 / 6 environment (family) <- at or over threshold` beside `mutation (family) 6/7`, base prints zero family lines. RESULT: figures confirmed.
3. Mutation arm 2 re-run at the new head (union -> first-member count): rc=1, the three family pins red; restored rc=0, `FIXTURE ok: 92 error(s) hold 238 pins across 12 check classes`. RESULT: mutation proof confirmed.
4. Consumer harness re-runs green at the head with the mkdtemp fix: 6 ok lines including the control refusing `declares 5 key(s) and 7 row(s) parsed`, exit 0; `friction_issues.mjs --self-test` 100 passed; acceptance FIXTURE ok. RESULT: consumer confirmed.
5. Scope unchanged: policy_lint.mjs + friction-families.json + the harness only; no VERSION/claims; merge-tree --write-tree vs origin/main rc=0. RESULT: scope confirmed.
6. Red checks now complete, checked against the check-runs API, not the body: CodeQL green at this head (the mkdtemp fix, named with the finding and the cheaper-detector answer), pr-contract's latest run green at 11:57Z and names this head (its 11:49Z red was the body mid re-take, superseded), nightly-status named with run 37108891698 and exempt — the diff touches none of what it grades. RESULT: red-check trigger answered.
7. Head verified c16d751e2 immediately before posting; nothing moved under the review.

Evidence: /Users/timmalmstrom/hpo-seats/review-1892/evidence/ (r2_base_s{13,14,16}.txt, r2_head_s{13,14,16}.txt, README.md).
