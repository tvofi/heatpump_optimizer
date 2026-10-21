Fix review: merge 8f026328dd45d8113e05c51c64038fa47a3a4b67

This is the third review in this head series. 38ec7c60 was blocked ci-red and 044edcc2 was blocked carry-missing. I measured head 8f026328dd45d8113e05c51c64038fa47a3a4b67 (ev/HEAD.txt). I re-read it at 18:47Z and it was still the PR head (ev/head_recheck.txt). My contract is current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty. Seat: a Linux cloud container with bash 5.2, CPython 3.11.17 and node 22.

## Both earlier blockers are resolved

- ci-red (38ec7c60). The check that fired fails before the fix and passes after it, and it was not weakened. Before: at 38ec7c60 it prints `71 self-testing, 70 wired, 1 unwired` (UNWIRED tools/pr/gate_priority.py), rc=1. At the head it prints `72 self-testing, 72 wired, 0 unwired`, rc=0. `selftest_wiring.py` has the same blob at 38ec7c60, 044edcc2 and the head (292dc67d). My mutants on the fix line:
  - M-del (the gate_priority line deleted): 72/71/1, rc=1.
  - M-comment (the line commented out): 72/71/1, rc=1.
  - Restored: 72/72/0, rc=0, and the tree is clean.
  - The harness's W1-W3 are KILLED as well.
- carry-missing (044edcc2). The carry is now in the tree. Both R10-CI-LAYOUT-P1 and R10-CI-LAYOUT-P2 hold the line on handoff/audit-r10-roster: at the body's a6e0530d49965ed5be440590425aaaa44b71577a, at f424d993d, and at the current tip 23ef06dc6 (ev/roster_carry.txt). Both groups are not-started. The line states its control as a precondition: `N self-testing, N wired, 0 unwired` with rc 0 after every main merge, and deleting a wired line turns it rc 1. The body routes it with `Carry: R10-CI-LAYOUT-P1 and R10-CI-LAYOUT-P2 ... roster SHA a6e0530d...`. `carry_audit.py check --body` reads `8 routed, 0 unrouted, 0 bad destination(s)` against both the roster ref and main. CI's pr-contract at the head prints the same line.

## Round-2 conflict resolution (dev/audit/harnesses/r10_seat_selftests_mutants.py)

- `git merge-tree --write-tree 7752acbf 49c22228` reproduces the single content conflict in the harness (ev/merges.txt).
- Main's mutants are kept exactly. I parsed the AST of main's harness and of the head's. All 31 of main's MUTANTS tuples are present byte-equal at the head: `missing []`. The tick_loop mutants S31-S34 are among them. At 7752acbf the same parse prints `missing ['S31','S32','S33','S34']` (ev/resolution_parse.txt).
- This PR's four mutants are renumbered consistently:
  - Each of S31->S35, S32->S36, S33->S37 and S34->S38 has identical text (`True` x4).
  - There are 39 ids with no duplicates.
  - The docstring now reads `S01..S38` and `S35-S37 ... S38`.
  - The WRAPPERS block equals the PR side's (S08 re-targeted).
- I diffed the PR-vs-base diff at 044edcc2 against the same diff at the head (ev/authored_delta_044edcc2_to_head.diffdiff). The only authored change between the two rounds is this renumbering, plus hunk offsets.
- No other file names this PR's ids:
  - INSTRUMENTS.md names no S-id.
  - `git grep` for S31-S38 outside the harness and the ledger hits only round-9 D3 artefacts and `tests/finite_boundary.py`'s unrelated `GUARD_OFF S34` (ev/id_refs_head.txt).
- 8f026328's own merge is clean. Recomputing `merge-tree 28cc73dd f2fb1b0e9` gives tree be628a73, which equals the head's tree, with the driver line `LEDGER-MERGE: resolved tests/closures.json`. 28cc73dd's tree equals bfcdece3's.

## Finder's harness, run at the head in its own worktrees (never the fixer's instruments)

RESULT finder_harness(head copy) M0_red=0 killed=42 not_run=0 survivors=0 rc=0 tree_clean=yes   (ev/harness_head_version.txt)
RESULT finder_harness(main copy, unedited, at head) killed=37 survivors=1 rc=1 -- the 1 is S08 `NOT RUN | PATTERN FOUND 0 TIMES`   (ev/harness_main_version_at_head.txt)

- The head copy's lines match the body word for word:
  - S31 `8 checks, 4 failed`, S32 `3 failed`, S33 `1 failed`, S34 `4 failed`.
  - S35, S36 and S37 each `handoff_push self-test: 2 checks, 1 failed`.
  - S38 `merge_pr self-test: 16 checks, 2 failed`.
- Main's copy gives the same S08 result the round-2 reviewer judged harness maintenance. This PR rewrote the wrapper, and the head's copy re-targets S08 to the new dispatch line, where it is KILLED. A pattern that no longer matches is not a surviving mutant.

## Other mutants (mine)

RESULT mutant restore_pathspec (wave-script's 'tests/delivery_status.py' line deleted): `13 closure file(s), 12 covered ..., 1 missing` rc=1; restored 0 missing rc=0   (ev/mutants_restore_precise.txt)
RESULT mutant restore_precondition (`if restore_check(root, reader):` -> `if False:`): `agreement_py self-test: 7 checks, 1 failed` rc=1; restored 0 failed   (ev/mutant_restore_precondition.txt)

The body lists the delivery_status pathspec mutant as not re-taken. I ran it: it is killed.

## Body figures re-taken at this head (ev/figures_head.txt)

All of these reproduce:
- selftest_wiring: 72/72/0.
- offline_spy: 2 files, 0 refused, network=0 remote_git=0 for both.
- handoff_push self-test: 2 checks, 0 failed. merge_pr self-test: 16 checks, 0 failed.
- gate_priority self-test: 12 checks, 0 failed.
- agreement_py --restore: 13/13/0. agreement_py --self-test: 7/0.
- STRUCTURE RATCHET PASSED.
- layout --guard: 0 refusal(s).
- tmp_paths: 0 refused, 0 stale.
- policy_lint: 0 error(s) across 41 policy file(s).
- ci_predict: no closures or fast red predicted.
- row_files_replay --self-test: ok.
- The program count is 14, matching the body. I did not re-derive it this round; the round-2 reviewer did.
- grep -c KILLED gives 42, which matches the body.

How these were taken:
- The body's figures were taken on the bfcdece3 tree with origin/main at 49c22228. I re-took them on the 8f026328 tree, where the merge base is f2fb1b0e9 (layout --base f2fb1b0e9), and they hold there.
- Not re-run by me: prepr.sh's `FIGURES: 14 resolved, 1 not verified`. CI's pr-contract at the head prints that same line.
- Not re-run by me: the agreement.mjs --py-json null.

## Merge, versions, claims

RESULT merge_tree origin/main=f2fb1b0e9 rc=0 tree=be628a73 (equals the head's tree)   (ev/merge_tree.txt)
RESULT merge_tree origin/main=57f0c9c77 (main moved during the review) rc=0 tree=b146576c; on that merged tree selftest_wiring 72/72/0 rc=0, agreement_py --restore 13/13/0 rc=0   (ev/merge_tree_newmain.txt)
RESULT version_manifest_notes_claims_budgets untouched (origin/main...head)   (ev/carry_version.txt)

## CI at this head (commit check-runs API, ev/check_runs_head.tsv)

- Every non-skipped run is complete and green except nightly-status (119372325177). That includes:
  - the FULL gate: fast (3.14) 119372927800, and closures 119387589787 (closures-autofix skipped);
  - instrument-self-tests 119372325390, wave-script, policy-docs and both pr-contract runs;
  - coverage, composed-proof, mutation, arch-score, budget-raise-gate, delivery-status and CodeQL.
- nightly-status fails on its step "Report the last scheduled run's conclusion". It grades main's scheduled run. The diff touches neither tests.yml nor the mutation or slow lanes, so it is not this PR's red. The body names it and answers it.
- Red-check answers (step 11). pr-contract at the head prints `record red-history ... 19 commit(s) ...: instrument-self-tests, nightly-status, policy-docs`. The body's `## Red checks` names and answers each of those three, plus pr-contract's BAD-DEST at 7752acbf. Every red check across the range is named and answered, each with a cheaper detector or the statement that none exists.

## Not verified / disclosed

- I did not re-run the gate or the mutation table: they are CI's runs.
- Instruments I built myself:
  - the AST parse of MUTANTS (ev/resolution_parse.txt);
  - the diff-of-diffs (ev/authored_delta_044edcc2_to_head.diffdiff);
  - the in-place mutants listed above.
- No numbers moved under step 14 beyond tests/closures.json. Its entries for merge_train.py, queue_pre_flight.py, tmp_paths.py and selftest_wiring.py, and its entities.py seconds (670.4 -> 2033.6), come from 2fd3fd459's recording, which this round did not change. I did not re-record closures. CI's closures lane is green at this head.

bus-nonce: 6a90cc3dbdedf45b14fd822bc8d7958d
