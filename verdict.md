Fix review: merge 5a5b2c4fca00886ffa425268ee9b604fcaf58045

bus-nonce: c7571fb57dc0bf8718c94e69e931c78c

Round 1 of this review. Measured head 5a5b2c4fca00886ffa425268ee9b604fcaf58045, still the PR head when written. Review packet UNAVAILABLE (carry-landed check read a run id as a commit); reviewed without it.

## Findings

- Follow-up: the pr-contract.yml wiring of gh_read_run.py (7 reads, base-restore pathspec, dropping both `pending` keys in field_coverage.mjs) is not in this diff and is owed after the merge; body forward-carries it. Carry: #2731
- Follow-up: the other 17 workflow `gh api` reads, the stale EQUIVALENT entry in r10_gh_read_retry_mutants.py, app_push.sh's push retry, outside_intake.py plan_live and the lagging-red decision are open class seams, each dispositioned in the body's Forward-carry. Carry: #2731

## Evidence

- merge-tree with origin/main: rc 0, clean (LEDGER-MERGE resolved tests/closures.json). ev/mergetree.txt
- merge_train classify at this head: GREEN, pending none, red none (ev/classify1.txt). The body's red `gate` (edit run, deferral to the code run) is answered in the body; its later attempt and the code run are green.
- Self-tests at head: gh_read_run 13 checks 0 failed; stamp RESULT stamp_self_test=pass; r10_codescan_wait_race selftest 14 checks 0 failed; r10_red_list_lag 5 checks 0 failed; record_row gh_read 138 checks 0 failed; field_coverage ok; structure ratchet passed; archscore dS +0.0000 NULL.
- Mutants (mine): deleting the fallback break lines in pages(): selftest 3 failed [fallback, over50, many1760], matching the body. Reverting the item bound to MAX_PAGES: 1 failed [many1760], matching the body. Dropping NON_JSON from gh_transient: gh_read_run 4 failed, gh_read 138-check self-test 3 failed. Replacing get_gh's retry with one read: stamp RESULT stamp_self_test=fail. All restored. ev/m1..m4.txt
- Enumerators re-run: `git grep -n 'gh api' -- .github/workflows` gives 24 (body: 24 at its base); `git grep -nE "urlopen\(" HEAD -- tools` gives the same 5 lines as the body.
- VERSION, manifest and RELEASE_NOTES untouched; no golden or claim file in the diff; roles dir unchanged against main.
- Not re-derived: the 44-minute live red-list lag count (1 in 379), the live 502 null controls, the 118-mutant diff run and the 7m57s sweep figure (heavy or live-API; cited, not re-run).
