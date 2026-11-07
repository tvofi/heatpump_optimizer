Fix review: blocked e3094246142cdfa6028f8c92bf9a42b0d548f2c7 claim-refuted: #3219 is filed under group A (no check failed on the diff) but tests / mutation concluded failure on an unpinned site added by its diff 14 min before the blocked verdict

bus-nonce: e057f3bf9c9f26950851c70981db8d7a

## Block

Round 1. Measured head `e3094246142cdfa6028f8c92bf9a42b0d548f2c7`, merge base `4b5d771bdf8feb1f83d7d9443e5117b771a0ab76`.

`R10-RCA-CI-RED.md` section 3 defines group A as "Run cancelled or gate deferral, no check failed on the diff: 8 entries, 8 PRs" and lists #3219 in it. The check runs at #3219's blocked head `aca500910` (read with `filter=all`, every page) show `tests / mutation` concluded `failure` at 2026-11-05T04:18:12Z (job 127045678304), before the `ci-red` verdict at 04:32:06Z. Its log, line 6869: `MUTATION TABLE REFUSED -- 3175 unpinned site(s) against 3174 at the ratchet base 78a2be77c..., 1 of them added by this diff.` That is a red on the diff, the same mechanism as #3195's third entry, which the record files under D. `tests / replay` also failed at 04:38:35Z, after the verdict.

So the 8 / 4 / 4 / 2 split, group A's 110 min mean (769 over 7), P_A = 8 / 93, and section 4's "A is state (d)" over all eight entries do not re-derive under the record's own rule. The cheap fix: move #3219 to D (or to C, if its body's Red checks omitted the mutation red, as its verdict suggests stale Red checks), then re-take the section 3 counts and the section 5 table. It changes no conclusion about B, which is the record's one built-later countermeasure.

## Findings

- #3219 (`aca500910`) is misclassified into group A; tests / mutation failed on an unpinned site its own diff added (job 127045678304, log line 6869) before the verdict, so group A's count, mean and P, and group D's (or C's) count, are wrong. Carry: R10-FRICTION-CI-RED

## Evidence

- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Count re-derived: `node tools/policy/policy_lint.mjs --stats --since v7.1.2 --window-cache W.json` at the head, origin/main `364353e67` (main moved by #3280 after the base): `STATS: 94 merged pull request(s)`, row `14 / 18 ci-red`, the same as the record's (93 PRs, because the window then ended at `4b5d771bd`). `ev/stats_review.txt`.
- `entries.py W.json ci-red` reproduces `entries_v7.1.2.tsv` byte for byte (`diff` empty, `ev/entries_review.tsv`). `ci-redd` gives `ENTRIES 0 PRS 0`. Null control: I rewrote #3189's `ci-red` verdict to `ci-redx` in a copy of the cache, and the output moved to `ENTRIES 17 PRS 13` (`ev/null_control.txt`).
- Check runs for all 18 heads, `filter=all`, every page fetched explicitly: `ev/checkruns_all/`, summary in `summary.txt`. The default `filter=latest` view, in `ev/checkruns/`, hides cancelled-then-rerun runs, e.g. #3181's and #3217's codeql cancellations. Apart from #3219, every row's named red appears there: the codeql cancellations at #3181, #3217 and #3244 first; the prelude/gate cancellations at #3167 second and #3204; nothing but gate at #3240; full cancellation at #3211; fast at #3180, #3189, #3208 and #3242; typing at #3195 first; CodeQL at #3244 second; instrument-self-tests and fast at #3227.
- inline_scan re-timed: `0` in 0.659 s (`ev/inline_scan.txt`), against the record's 0.55 s. The order-of-1000 cost argument for B holds. The `prepr.sh:436` comment deferring `harness_headers.py` to CI is present.
- Policy: the record changes neither the keying rule nor the gate. The vocabulary change (C) is stated as policy awaiting the owner, and nothing of it is applied. The cancellation and D refusals are recorded. All three forward-carries name #3156, which the body says is not to close on this record.
- Body: `Disposes #3156` with no closing keyword. The delivery row `dev/programme/delivery/3295.md` is in the diff. VERSION, manifest and RELEASE_NOTES.md are untouched (three-dot diff is the 5 listed files). `## Head` names `e3094246` with code head `809d97772`; the only later commit adds the delivery row.
- Merge: `git merge-tree --write-tree origin/main HEAD` exits 0 (tree `a8268e493`).
- CI: `merge_train.py classify e3094246... --pr 3295` gives `GREEN e3094246142cdfa6028f8c92bf9a42b0d548f2c7 pending: none red: none`, rc 0 (`ev/classify1.txt`). The packet's `tests / nightly-status` failure is not this PR's: the diff does not reach what it reads. So `## Red checks: none` stands.
- Mutation proof is n/a: no production line changes. The body's prepr run is the fixer's; I did not re-run the gate (rule 11).
