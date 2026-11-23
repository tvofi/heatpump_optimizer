Fix review: blocked 0b1994a331b7a3a46a49b0c8ed718cb338243860 mutation-vacuous: roster_lib.round_literal_hits ROUND_RECORDS file half survives (key loosened to constant name only, 124 checks 0 failed)

bus-nonce: 3dac3e7b40d4f37723406a6b163b7966

Round 1 (full review, no earlier reviewed head).

## Block

- The barrier's exemption is stated as keyed on (file, constant): the body says "`ROUND_RECORDS` keyed on (file, constant)", and the code comment says the key "does not reach another constant". The self-test pins only the constant half (`a ROUND_RECORDS key admits its own constant and no other`). Mutant M7 rewrites `x.isupper() and (rel, x) not in ROUND_RECORDS` to `x.isupper() and x not in {k for _, k in ROUND_RECORDS}`, so a record's constant name is exempt in every file. `roster_lib.py --self-test` then prints `124 checks, 0 failed`. Witness: `round_literal_hits("tools/x/other.py", 'SEARCH = "dev/audit/rounds/round11/D11"\n')` returns `['tools/x/other.py:1: module constant: round11']` at the head and `[]` under the mutant (ev/mutants.txt). `SEARCH` is a generic name, so a new module constant with that name that names a live round would get past the barrier the ruling asks for. The repair is one null arm: the same record constant planted under another file path is refused.

## Evidence

- RESULT head: 0b1994a331b7a3a46a49b0c8ed718cb338243860 is the PR head (ev/HEAD.txt), and the review ran from a detached worktree at that commit. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- RESULT merge: `git merge-tree --write-tree origin/main 0b1994a331` gives tree 8417c20907 with no conflict. Merge base 3153a635b4 equals origin/main.
- RESULT self-tests at head: roster_lib 124 checks 0 failed, roster_queue 69/0, closeout 41/0, replan `self-test: 0 failed` rc 0, including `ok self-test fails when roster-ref-default is deleted` (ev/selftests-head.txt, ev/replan-selftest-head.txt).
- RESULT mutants (ev/mutants.txt). Each of these is killed:
  - M1: `roster_at` default set to the wave-r10 literal fails `a later round's roster is the one a ref carries`, 69/1.
  - M2: `readback` default set to the literal crashes the self-test, rc 1, `group N not in the roster`.
  - M3: `readback_text` gives the same crash, rc 1.
  - M4: the closeout default restored to the round10 literal crashes in `json.load`, rc 1, as the body says.
  - M5: the replan literal fallback, committed in a scratch worktree, makes roster_lib fail `no tools/ default at this checkout's HEAD names a round` (got `replan.py:166: parameter fallback: audit-r10`).
  - M6: deleting the or-fallback hit gives 124/1.
  - M8: dropping the argparse `help` shape gives 124/1.
- RESULT M7 survives, as the block above describes.
- RESULT barrier figures re-derived: `round_literal_defaults` at e3cb5c019b gives 5 hits, the same five the body lists. At HEAD it gives 0 (ev/lint-base-head.txt).
- RESULT class check: I ran an AST census of every round literal in tools/**/*.py outside self-test functions and round<N>/ directories at the head. It finds 50 constants, and each one is a fixture function (`cases`, `_plant`, `_fixture`, `*_checks`), a docstring example, or a ROUND_RECORDS record (ev/py-literal-census.txt). None is in a default shape. Every non-.py hit of the body's census grep sits in a self-test section: body_patch.sh, bus.sh, prepr.sh, brief_lint.mjs and check-wave-script.mjs. No module imports the removed `roster_queue.ROSTER_REL`.
- RESULT symptom (ev/symptom.txt): with no --roster-ref, base reads origin/handoff/audit-r10-roster (116 groups, none of the three named groups). Head reads origin/handoff/audit-r11-roster (131 groups at today's r11 tip a124adacb4, all three present). At the body's r11 commit a45c0c450f the head plans 126 groups, matching the body's figure. The 131 is later roster growth, not a discrepancy.
- RESULT untouched: VERSION, manifest, RELEASE_NOTES.md and tests/golden/ show no diff over the three-dot range (ev/untouched.txt).
- RESULT CI: `merge_train.py classify` printed WAIT (`pending: gate red: none`) up to 02:57:48Z (ev/classify.log). I did not wait for green, because the block does not turn on CI. Not re-derived: the archscore dS and structure.py figures, which are cited for CI to re-prove.
