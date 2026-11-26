Fix review: merge f9eff1b832b8a11479d98c5a279f7345d58146c8

bus-nonce: da3ed22088b9c250f2bc63ea56f3e77f
pending-ci: gate

## Round

Re-cut (#3906) of closed #3898 after three blocked verdicts (b15a9f2c, e60d25b9, dbaca057); first review of this PR, scope full (packet `## Review scope: full`). Whole three-dot diff against merge base 3ee06864da reviewed: 12 files, no `custom_components/` path.

## Earlier blocks

- (1) seat key in the `publish_seat` stub: answered. `render` appends `token_ledger.header(...)` to the first line of the stub or the whole prompt. Mutant key-insertion (`text = f"{first} {key}\n{rest}"` -> `text = text`) fails 4 cloud_dispatch self-test arms, the fixer's and reviewer's published-stub arms and the group-seat stub arm (review/3898's case) included. M4 (`if first and ...` -> `if o.get("type") == "user":`) and M5 (`max(d["t"], stamp)` -> `stamp`) each fail one token_ledger arm. The seen guard (`continue` -> `pass`) and `seen.add` removal each fail 3. `inherit_part`'s return -> `return brief` fails 2 cloud_dispatch arms, and its call in `main` -> `pass` fails 1.
- (2) window filter lower bound: answered. In `ledger_unread`, lower bound dropped fails `--round: a seat class whose only row predates the window prints unread`. Whole filter (`win = rows`) fails that arm plus both end-of-window arms.
- (3) upper bound `< b`: answered. The bound dropped (`a <= at(r["t"])`, the earlier D5b survivor) and `<= b` each fail `--round: a seat class whose only row falls at the window's end prints unread` and `--round null: an unkeyed seat row at the window's end is no unread`. Unmutated, the whole `check_scopes.py --repo . --self-test` prints `SELF-TEST passed (every perturbed scope refused)`.

## Evidence

- RESULT: 16 targeted mutants, run by this reviewer from a detached worktree at f9eff1b8 with each file restored after: 16 killed, 0 survived (ev/mutants.txt). The 9 check_scopes mutants were re-run in a second worktree with each failing arm named (ev/mutants-check_scopes.txt, ev/mut-*.txt). The arms named for mutants (2) and (3) match the body's `## Mutation proof` exactly.
- RESULT: beyond the body's set, three `ledger_gaps` window mutants (lower bound dropped, upper bound dropped, `<= b`) each fail `--round null: a seat before or at the window's end, or another seat, is no gap`. The `ledger_unread` unkeyed-count mutant (`unkeyed = 0 * sum(...)`) and the unread-print suppression (`if why:` -> `if False:`) are both killed.
- RESULT: unmutated self-tests at f9eff1b8: `token_ledger self-test: 18 passed, 0 failed`; `cloud_dispatch self-test: 188 checks, 0 failed`; `beat_jobs self-test: 313 checks, 0 failed`; check_scopes `SELF-TEST passed`; `STRUCTURE RATCHET PASSED`, re-run in a clean worktree (ev/structure.txt). The body's `## Figures` are all re-derived.
- RESULT: the body's "11 arms" in the `--round` ledger self-test was counted at the head: 11. "Before the new arms, all 9 ledger arms held under it" describes #3898's head and was not re-run here (not re-derived).
- RESULT: `git merge-tree --write-tree origin/main f9eff1b8` exits 0 (ev/merge-tree.txt). `VERSION`, the manifest, `RELEASE_NOTES.md`, `tests/golden/` and every `*budgets.json` are untouched in the three-dot diff (ev/untouched.txt is empty), so step 4 has no moved fixture or claim. `dev/governance/roles/` is unchanged between the merge base and origin/main.
- RESULT: steps 2 and 3 have no finder's harness (packet: `none named`), because this is an instrument, not a defect fix. The null controls the body names hold unmutated: every-class-keyed, unkeyed-at-`b`, outside-window and absent-ledger.
- RESULT: seat-key rule and residue checked. The body's enumeration rule (`git grep` over event and payload builders) and its stated residue category (a local Agent-tool spawn, printed unread) close the axis. No unenumerated cloud dispatch path was found: `dispatch_group`, `main --publish` and the flag path all reach `render`.
- RESULT: `tests / nightly-status` is red at the head but is not in `merge_train.py owed-reds`, so it is owed no answer. The packet's introduced-red signal was `instrument-self-tests` in progress at render. classify decides (see CI line below).
- RESULT: CI: `merge_train.py classify f9eff1b832b8a11479d98c5a279f7345d58146c8 --pr 3906` polled from 03:25 to 03:55 UTC, every line `WAIT f9eff1b832b8a11479d98c5a279f7345d58146c8 pending: gate red: none` (ev/classify-last.txt). The verdict is returned with `pending-ci: gate` for the relay to post once green.
