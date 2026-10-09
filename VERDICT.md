Fix review: blocked 3637f1c780ae030ba19bcd0818a7e19ee18ee9f2 architecture-unsound: the STALE PIN arm is whole-tree, so a stale pin main carries refuses an unrelated branch (measured rc 1 on a tests/README.md-only diff); every other refusing 6d arm is diff-scoped and has a main-state null control

bus-nonce: 4e7628e8564146c85ec735d666a479ca

Round 1. Reviewer: review-2073. I measured head `3637f1c780ae030ba19bcd0818a7e19ee18ee9f2` against merge base `47b083b0` in a standalone clone, and I used the base copy of `ci_predict.py` as the "before" predictor. Evidence: `/Users/timmalmstrom/hpo-seats/review-2073/ev/` (RESULTS.txt and one file per arm).

## RESULT lines

- RESULT null: unmodified tree, rc 0.
- RESULT edit: pinned line `away.py:574` edited. New predictor rc 1, `STALE PIN ..._parse_return_time RETURN_DEL 17d5e3f1`. Base predictor rc 0.
- RESULT delete: `restore_override` deleted. New predictor rc 1, `STALE PIN ...restore_override GUARD_OFF 5cc88563`. Base predictor rc 0.
- RESULT remedy: the edit with its pin file removed. rc 0, with only the ADDED UNPINNED warning.
- RESULT shift: 14 comment lines prepended to `away.py`. rc 0, no STALE PIN, because a pure move stays valid.
- RESULT wedge: the base commit carries a stale pin and the branch edits only `tests/README.md`. rc 1, STALE PIN.
- RESULT cost: `completeness_problems` takes 3.4, 4.3 and 7.4 ms over 5891 sites and 1250 pins. The predictor's wall time at head (4.4-5.7 s) is the same as at the base (5.7-7.7 s) within noise. The claim of 0.01 s holds as an upper bound.

## The blocking finding

`unpinned()` adds `completeness_problems(budgets, sites)` over the whole tree with no diff filter. The new code comment says "a pin whose site the diff edited, moved or deleted", but the check is broader than that claim. Every other refusing arm of 6d is diff-scoped:
- UNCLASSIFIED: `if f in changed`
- NO RECORDING: `s in changed or lanes_changed`
- ADDED UNPINNED: `diff_sides`

The self-test pins that property with "6d charges no branch with an unrecorded script main already carries (null control)". The new arm has no such control.

The state is reachable. `mutation` is required in ruleset 23698884, but `strict_required_status_checks_policy` is false. So if PR A's autofix pins a line and PR B edits that line, both merge green and main carries the stale pin. From then on, prepr refuses every seat's push with "repair before the handoff" until some unrelated PR deletes main's ledger file.

Repair:
- Refuse only a stale pin whose anchor file, or whose ledger file under `tests/mutation_ledger/`, is in the diff's changed paths.
- Print any other stale pin as a WARN that says main carries it.
- Add a self-test arm built like `pinh`/`pmainred`.

The filter still catches all three cases in the RCA: #2065, where the branch adds the pin and also changes the file; #2066 and #2070, where the anchor file is changed.

## Checked and passing (not blocking)

- **Process state (c).** It matches `root-cause.md`'s own wording: the check existed in CI and in no local path. The class search is honest. Of the arms `ci_predict.py` models, the ledger was the only half-ported pair.
- **Carry.** `briefs` is green at head, and I reproduced the carry's control: a 14-line prepend makes the fixture VACUOUS with rc 1, a 1-line prepend gives rc 0. The carry is well formed.
- **Merge simulation.** main+#2073+#2067+#2072 merges cleanly in three orders, each giving tree `85031e98`, and `bash -n` passes. The duplicate `# --- 6d.` label comes from #2072 alone (its layout guard) against main's existing 6d. `6e` is unused, and #2073 adds no label.
- **Red checks.** None except `nightly-status`, and this diff does not reach what that check reads.
- **Untouched.** `VERSION`, the manifest and the claim files.

## Notes for the re-push (non-blocking)

1. The 6d header comment in `prepr.sh` (around lines 394-403) lists what refuses. It should name STALE PIN too.
2. The body says "Forward-carry: none", but the PR adds an entry to `carry-201.json`. Name it there.
3. "Four occurrences": the RCA's own list has three stale-pin PRs. The fourth item, the pr-contract observation, is not a pin red. The cost verdict is unchanged.
4. The #2070 observation, that CI never runs a round's `--perturb` arms, is a separate class: an instrument CI never exercises, so its breakage turns nothing red. It does not belong to this RCA's class, a local predictor that ports half of a CI refusal. It belongs to D11/D13 or its own carry.
