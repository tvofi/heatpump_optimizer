Fix review: merge 846f2dc07b4503522909bf953b91e502f168f2af

bus-nonce: d8e3d48acd9cc28629d822cd942eecce
pending-ci: gate

Round 5 is a delta re-review of 0740542f38..846f2dc07b. I measured head 846f2dc07b4503522909bf953b91e502f168f2af from a detached worktree. The branch's own change in this range is the one commit baaf0064: eight added lines, one self-test arm in tools/plan/size_durations.py. Everything else in the range arrives from origin/main through the merge 3b29e4e31. The three-dot diff against the merge base differs from round 4's only by those eight lines (ev/branch-delta.txt). Unchanged code was not re-reviewed.

## Findings

- Follow-up: the body's `## Mutation proof` says deleting the new arm's `check(...)` call is KILLED. Deleting the whole two-line call SURVIVES at this head (`arm-check-del`, ev/mutants-arm.txt). A deleted assertion cannot fail, and the body's own `## Unpinned sites` puts single-line check deletions in that class. So the KILLED figure most likely came from a one-line deletion that left a syntax error, which kills nothing real. The figure is wrong, but no production line is unpinned by it. Carry: dismissed: test-side, a deleted assertion is inherently unkillable; the misstated figure is recorded here
- Follow-up: the stub `reads={"rest": lambda o, s_: 1 / 0}` behind the arm's "no read made" can be swapped for one that returns `[]`, and that SURVIVES (`arm-stub-noraise`). It is equivalent: a run that ignored the cache would read 0 PRs with `replayed=False` and fail the same `endswith` check, and `read-noreplay` and `run-cache-none` are KILLED. Carry: dismissed: equivalent test-side mutant, the cache path is pinned by production mutants
- Follow-up: the body's `## Mutation proof` has an unclosed backtick (`` `## Unpinned sites ``) and repeats the full `## Unpinned sites` text inside its last bullet, so the section appears twice. This is cosmetic and changes no figure. Carry: dismissed: body formatting only
- Follow-up: the test-side mutant `replan-cap` survives, as rounds 3 and 4 recorded. Carry: dismissed: test-side only, the production defaults are pinned, as rounds 3 and 4 dismissed it

## Evidence

- RESULT round-4 block answered. `note-replayed` (`input_note(via, since, len(prs), replayed)` changed to `..., False)` in `size_durations.run`) is now KILLED through tools/audit/seat/mutant_run.py (ev/spec-r5.json, ev/mutants-r5.txt). NULL SURVIVED. Applied by hand, it prints `FAIL run --prs-cache: sizes_provenance ends naming the replay, no read made` and `size_durations self-test: 1 failed` (ev/note-replayed-fail.txt). That matches the body's `1 failed`.
- RESULT my extra production mutants on the replay path are all KILLED: `note-replayed-true` (always True; the null `cache=None` arms kill it, which confirms the null control), `run-cache-none` (run passes `cache=None` to read_prs), `read-noreplay` (read_prs ignores an existing cache), `read-replay-false` (read_prs returns False on replay), `note-replay-text` (the replay suffix is dropped) and `note-cond-inv` (the condition is inverted).
- RESULT the new arm's statements (ev/spec-arm.json, ev/mutants-arm.txt): deleting the roster write is KILLED, deleting the cache write is KILLED, and flipping the expected flag from True to False is KILLED. These match the body. Deleting the check, and swapping the raising stub, SURVIVE (see Findings).
- RESULT self-tests at the head, unmutated (ev/selftests.txt): `size_durations self-test: 0 failed`, `plan_page self-test: 93 checks, 0 failed`, and replan `self-test: 0 failed`.
- The earlier survivors `note-run`, `run-via` and `replan-via` sit on code that this range does not change. Round 4 killed them, and I did not re-run them. The hot-* mutants likewise sit on unchanged code.
- Step 13: `git merge-tree --write-tree origin/main 846f2dc07b` exits rc=0 with no conflict (ev/merge-tree.txt).
- Step 5 and step 14: the branch delta touches no VERSION, manifest, release-notes heading, budget, claim, golden or closures file. Those files appear in the range only through the main merge.
- The round-4 `pr-contract` red (`roster_lib.carry_receivable` missing) is answered by the merge of origin/main, which carries that function.
- I did not re-run diff mode, so the body's survivor counts (8 / 11 / 3) are not re-derived here. `durations.json` was not re-measured, as the body says.
- Finder's harness: none. This is an instrument group fed by roster carries, as rounds 3 and 4 recorded.
- CI: polled with `merge_train.py classify` (ev/classify-poll.txt). owed-reds: ev/owed-reds.txt.
