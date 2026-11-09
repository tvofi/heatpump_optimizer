Fix review: blocked 54f76620231dab81bc2111b87bebacfaf78992cc main-conflict: dev/audit/harnesses/r10_codescan_wait_race.py conflicts with origin/main 7bdc8aa2e

bus-nonce: 1c0c05730b9cb9e0abe0785af6966c17

## Block

`git merge-tree --write-tree origin/main 54f76620231dab81bc2111b87bebacfaf78992cc` exits 1 with `CONFLICT (content): Merge conflict in dev/audit/harnesses/r10_codescan_wait_race.py` (`tests/closures.json` resolved by LEDGER-MERGE; no claim file refused). The conflict is off the claim files, so it is the author's. Main commit d23377e1d (landed after this head's base f365ce7) changed the same file: `pages()` region and a new per-attempt read for a run whose `filter=all` listing 502s. That is a third design of the retry in the carry 5 file, overlapping this PR's `MAX_ITEMS` bound and its 14 self-test checks. The author must re-merge main, reconcile the paging designs, and re-take the carry 5 mutation proof and null controls on the merged file. I did not run mutants on the unmergeable head.

## Evidence

- CI at this head: `merge_train.py classify` printed `GREEN 54f76620231dab81bc2111b87bebacfaf78992cc pending: none red: none`, rc 0.
- `merge_train.py owed-reds` is not invocable with a head or --pr (takes only --repo, --min-runs); its output lists tests/coverage-ratchet, tests/fast (3.14), tests/mutation, tests/typing, validate/validate-hacs. None is red at this head, so no red-check answer is owed.
- `review_packet.py render` was UNAVAILABLE (`Not a valid object name 42454528717` in the roster ancestry check), so no packet; live checks were re-read directly.
- Not examined (stopped at the block): mutation re-run, finder-harness measures, claim-file drift, forward-carry open. Round: first review by this seat.
