Fix review: merge 6f6aa4e48d6871cf5cb926c9ac53a521468ae58a

bus-nonce: 9735ee20c9fdc156d52d86515647a580

Review round 3. This is a carry of round 2's merge at `98d33ce032e8958419accb7fa91fa9661b494521`. The measured evidence is round 2's, by reference: `/Users/timmalmstrom/hpo-seats/r10s3/review-2379/evidence-r2` and `seat/VERDICT-r2.md`.

Delta 98d33ce03..6f6aa4e48 is one commit, the github-actions[bot] `ci: pin killed mutants`. It adds three files, all under `tests/mutation_ledger/killed_by/`: climate `current_temperature GUARD_OFF d1cf25b6`, `payload_number GUARD_OFF 6821a53f` and `_gap_energy_rate CMP_BOUND 6c88eaac`. Round 2 confirmed each was killed by my own mutant runs and by CI's pin job (`3 pinned, 0 left unpinned`). The commit touches no other path.

All 72 check-runs at 6f6aa4e48 concluded success or skipped. Both `mutation` runs (117635958778, 117635972463) are green, with no `ADDED UNPINNED` site.
