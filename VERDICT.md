Fix review: merge 708927198d91ca8cfbc79d1843cf401904782d6d

bus-nonce: a7f748b64d36d03677e8c6487ff5cf32

Round 1 of this reviewer seat on PR #2531 (R10-CI-RATCHET-RED). I measured head `708927198d91ca8cfbc79d1843cf401904782d6d` (ev/HEAD.txt) from a detached worktree. The merge base is `289426c1f`. The roles diff from the merge base to origin/main is empty, so the contract I followed is current.

## RESULT lines
- RESULT mutation M0 (none): `--self-test` rc 0, `15 checks, 0 failed` (ev/selftest_M0.txt)
- RESULT mutation M1 (0-byte guard deleted): rc 1, 1 FAIL, the named empty-response arm. Run under tests/entities.py, `1 of 2381` failed, exactly the named `window parser refuses an empty artifacts response` check (ev/entities_M1.txt)
- RESULT mutation M2 (FETCH_ATTEMPTS=1): rc 1, 2 FAIL, as the body states
- RESULT mutation M3 (expired skip removed): rc 1, 1 FAIL
- RESULT mutation M4 (null-first created_at key): rc 1, 5 FAIL, as the body states
- RESULT mutation M6 (this-run exclusion removed, my own): rc 1, 4 FAIL
- RESULT mutation M7 (the (run,name) order before the cut removed, my own): rc 1, 4 FAIL
- RESULT mutation M8 (dedup removed, my own): rc 1, 5 FAIL
- RESULT mutation M5 (fetch_window's explicit rc-0/0-byte branch removed, my own): rc 0, 0 FAIL. This is an equivalent mutant. window_entries already refuses an empty body, so the retry still happens through the SystemExit path and only the message text differs. The branch is redundant rather than untested. Not blocking.
- RESULT wiring: replacing tests.yml with the base's makes tests/entities.py fail exactly its 2 wiring pins, `2 of 2381` (ev/entities_baseyml.txt)
- RESULT entities at head: `ALL 2381 ENTITY CHECKS PASSED` (3.13 venv from tests/requirements-ci.txt), which matches the body
- RESULT null control, base: the base heredoc extracted verbatim and run on a 0-byte window.json gives rc 1 and a bare `JSONDecodeError`. The head's window_entries on the same file gives rc 1 with `the artifacts fetch returned 0 bytes for run 39548715713 …` (ev/nullcontrol_empty_base_vs_head.txt)
- RESULT null control, good body: I fetched a live artifacts list and ran the base's jq program through standalone jq against head window_entries. With run=0: 37 vs 37, `identical=True`. With run=39594588752 (an id present in the list, which exercises the exclusion): 34 vs 34, `identical=True`. Dropping one entry flips both to False (ev/nullcontrol_jq_vs_head.txt). My own first fetch for this came back rc≠0, 0 bytes, `unexpected end of JSON input`, which reproduces the failure class the body names.
- RESULT seam rule (the body's grep, run on git-archive trees, line numbers stripped): 25 sites at head and 26 at the merge base. The only difference is the closed ci-ratchet `… > window.json || true` (ev/seam_*.txt). I spot-checked the dispositions for tests.yml:2570/2908/4005/4301 and governance.yml:195/1029/1122 at a5dede8e and they hold. In particular, 2570's empty ID takes an explicit fail-closed re-record. The class is closed.
- RESULT structure.py: `STRUCTURE RATCHET PASSED`. Claims: `claims hygiene: 289426c1f… ok`. No claim file, budget, VERSION, manifest or notes heading is in the three-dot diff.
- RESULT merge: `git merge-tree --write-tree origin/main 708927198d91ca8cfbc79d1843cf401904782d6d` rc 0 with no conflicts. Re-checked at verdict time against origin/main `5d433771aa88bbfd49b8868a9b53ea1241ab85a3`.
- RESULT CI on head, from the check-runs API with all 51 runs concluded (ev/check_runs.tsv): everything is success, skipped or neutral except `nightly-status`. That failure grades main's scheduled run 39563978649 (`slow`, `mutation-nightly`). This diff's tests.yml hunks touch only the ci-ratchet job, so it does not reach what that check reads and the red is not this PR's. The body answers `nightly-status` and the earlier `pr-contract` reds under ## Red checks. `pr-contract` is green twice on this head.

## Steps
- 1 (mutation proof): confirmed for M1–M4, plus three of my own mutants that also redden. Details above.
- 2 (finder harness): the group brief names no committed finder harness. Its control is "ci-ratchet green on the fix head and on main after merge; a planted extra script run turns it red". ci-ratchet runs only on push to main, so that control cannot be measured on a PR head. The finder's reproduction in the roster's resume note is the 0-byte fetch→JSONDecodeError path, and I re-ran it at both ends (base heredoc against head module). Per step 9, this has no committed harness. The self-test plus entities pins now serve as that harness, and the instruments I built (the jq-vs-module compare and the heredoc extraction) are my own.
- 3 (null control): re-run as above, both ends.
- 4: no fixture moved and no claim files were touched.
- 5: VERSION, manifest and notes are untouched.
- 6: the class is opened with the body's named seam rule, and every returned seam is in the diff or dispositioned.
- 7: the body's ## Head names `708927198d91ca8cfbc79d1843cf401904782d6d`, and its merge parents (a5dede8e, 289426c1f, delivery-row commit) match `git log`.
- 8: re-derived: 15 self-test checks, 2381 entity checks, 25/26 seams, `identical=True`. I could not re-derive the body's tally of 15 main push runs (2 passed, 8 Gather, 5 Grade) because I did not re-take that run listing. I am not verifying those figures. They do not bear on the fix.
- 10: ## Forward-carry is `none`. The remaining critical_path red is already owned by R10-CI-LAYOUT in the roster, as the body states. The body says main's ci-ratchet stays red at Grade after merge until R10-CI-LAYOUT lands, so the brief's "green on main after merge" control cannot be met by this PR alone. That is disclosed and routed, not hidden.
- 11: covered under CI on head above.
- 12: the head was still `708927198d91ca8cfbc79d1843cf401904782d6d` at verdict time (ls-remote refs/pull/2531/head).
- 14: no budget or instrument number moves.
- 15: the added lines move a heredoc decision into a tested module (decision 0013 shape), with no architecture breach.
