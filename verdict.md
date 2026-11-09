Fix review: blocked 1c29e5ab7733d9c72d1773b649c97291b8b5dfb2 ci-pending: classify still WAIT (rc 3) after ~50 min; tests / closures, fast, browser, coverage, typing, arch-instrument jobs still queued on the head

bus-nonce: 75e07da349fe8245825db04e24bba166

## Block

CI on this head never concluded. `merge_train.py classify 1c29e5ab7733d9c72d1773b649c97291b8b5dfb2 --pr 3345` printed `WAIT ... pending: gate red: none` (rc 3) on every poll, about 50 minutes. The runner queue is the cause: `tests / closures`, `tests / fast (3.14)`, `tests / browser`, `tests / coverage`, `tests / typing` and `tests / arch-instrument` were still `queued` at the last read. No gate check was red. This is a hand-back, not a defect finding: I found nothing to block on in the code. Re-dispatch the review, or carry this one, once classify exits 0. The sections below hold what I measured.

## Findings

- Residual: `owner_topic`'s `name.startswith(t + "-")` boundary in tools/audit/seat/topic_grammar.py is not pinned by topic_grammar's own self-test; mutating it to `startswith(t)` leaves that self-test green (rc 0). The caller's `roster_sync.py --self-test` does kill it (1 failed), so the rule is pinned, one module away. Carry: dismissed: pinned by the consumer's self-test; the PR body says the rule moved unchanged.

## Evidence

- Head measured: 1c29e5ab7733d9c72d1773b649c97291b8b5dfb2; PR head re-read at the end of the review and unchanged.
- `git merge-tree --write-tree origin/main 1c29e5ab7733d9c72d1773b649c97291b8b5dfb2` exits 0 (ev/merge-tree.txt); no `MERGE-CLAIM` line, no conflict. `git diff` of dev/governance/roles/ between the merge base and origin/main is empty.
- Self-tests at the head, all pass (ev/selftests.txt): topic_grammar ok; pr_cap 22/0; open_driver 79/0; owed_unactioned 57/0; orchestrator_tick 297/0; ledger 102/0; cloud_relay 385/0; cloud_dispatch 132/0. The cloud_relay count matches the body's 385.
- Mutants on topic_grammar.py, each restored with `git diff --quiet` clean (ev/mutants.txt): prefix match instead of full match: self-test rc 1 (killed). Bare `-<N>` counted as a family member: rc 1 (killed). `owner_topic` prefix without the dash: topic_grammar self-test rc 0 (survives), roster_sync self-test fails 1 row (killed there). The body's claims "bare -<N> fails 2 rows, prefix fails 5" were not re-counted row by row; I confirm only that each is killed.
- I did not re-run the body's tick-level mutants (orchestrator_tick, pr_cap, open_driver, owed_unactioned, cloud_dispatch), the closure INERT_EXCEPT mutation or the `closure.py check` null control. I did not use the diff-mutant run or its 20 survivors; `tests / mutation` was green in CI. The body's remaining figures were not re-derived.
- Packet figure_lint: 18 resolved, 0 not verified, 0 refused. carry_audit: 3 finding items, 3 routed, 0 unrouted. The forward-carry destination R10-FLY-CIPREDICT-RESTORING is present in wave-r10-groups.json on origin/handoff/audit-r10-roster.
- CI at last read: green are `tests / mutation`, `tests / briefs`, `tests / closure-scope`, `tests / nightly-status`, `governance / wave-script`, `governance / instrument-self-tests`, `governance / policy-docs`, `arch-score`, `budget-raise-gate`, `hassfest`, `validate-hacs`. Red: `governance / delivery-status`, repo-wide per the brief and not required. Pending: `governance / env-matrix`, `codeql / Analyze (python)` and the queued tests jobs above. `tests / mutation` green is not proof the baseline was green; I did not read its log.
- Not checked: claim-file drift (`env_drift.py --all`), VERSION/manifest/notes untouched, and step 15 architecture. The diff touches no VERSION file, and no claim file is in the 18-file list (tests/golden/ absent). Step 15 and the `pr-contract` re-run were not completed.
- Round: first review of this head.
