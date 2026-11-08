Fix review: merge 4818616cd0ee1a41dc73e0fae3db2797f27dc382

bus-nonce: 5bc1fbc4af39fccc588f085164ce4280

Delta review only (scope per brief); prior verdict was merge at e5a600c1e28b5cfd11b6218fad8b39b01724f50c.

## Findings

None.

## Evidence

- Delta claim re-measured from a detached worktree at 4818616cd0ee1a41dc73e0fae3db2797f27dc382. Diff of the PR against its merge base at each head (new 48af0864..4818616c, old aaaec212..e5a600c1), keeping only added and removed lines (excluding file headers): 261 lines each, `diff` prints nothing. RESULT: IDENTICAL (ev/old.lines, ev/new.lines, ev/ident.txt).
- nightly.yml: the PR's hunks (run-name, `lanes` input, `inputs.lanes != 'beat'` on mutation-nightly, mutation-ledger, the ledger-publish job, slow and nightly-ha) are unchanged. The neighbouring context in main's new text ("started_at and completed_at). The 60 minutes left cover the runs in flight, each under its scaled timeout") sits above the mutation-ledger `if:` and doesn't mention or contradict the beat gating. It reads correctly.
- CI at 4818616cd0ee1a41dc73e0fae3db2797f27dc382: all check-runs read across all pages via the commits check-runs API (ev/checks.txt). Every one is success or skipped, none pending or red, including tests / mutation, tests / nightly-status, pr-contract, budget-raise-gate and gate. merge_train.py classify: GREEN 4818616cd0ee1a41dc73e0fae3db2797f27dc382 pending: none red: none, exit 0.
- Merge with origin/main: `git merge-tree --write-tree origin/main HEAD` is clean.
