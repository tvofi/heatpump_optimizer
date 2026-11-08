Fix review: blocked 41a196a242f20636f9e354ad98c5a401445831d9 ci-red: required gate red in edit run 42525599444, never re-judged after code run 42525600582 went green

bus-nonce: 2613f0884bf668cb45a0d24992b1c990

Delta review, round 2. This judges only the points in the blocked verdict `verdict/3341` (`32681b6b8`, head `81741e448`), at head `41a196a242f20636f9e354ad98c5a401445831d9`, from a detached worktree.

## Block

- Required context `gate` is red at this head. `merge_train.py classify 41a196a242f20636f9e354ad98c5a401445831d9 --pr 3341` printed `RED 41a196a242f20636f9e354ad98c5a401445831d9 pending: none red: gate`, rc 1, at 22:40Z. I re-ran it at 22:41Z and it printed the same (`ev/classify.txt`). The red `gate` (job 128876728348) belongs to the edit-kind run 42525599444, attempt 2, which completed at 22:04:58Z. Its log ends `FAIL run(s) [42525600582] at this head are still being judged; their gate decides` (`ev/gate-failed-run-42525599444.txt`). The code run 42525600582 then concluded success at 22:33:16Z, with its own `gate` (job 128883057965) green and every lane green. Nothing re-ran the edit run's `gate` afterwards, so the train still reads that suite's red. `latest_runs` keeps the worst gate per suite, and `infra_rerun` skips a run at attempt 2. This is not a defect in the diff. The cure is a re-run of run 42525599444's failed `gate` job, followed by a fresh `classify`. With that red gone, every point of the previous verdict is closed (Evidence) and this review reads as a merge. The fixer owes no code change. Carry: R10-REVIEW-ENUMERATE

## Findings

- Follow-up: two narrower mutants of the same lookbehind at `tools/audit/seat/survivor_list.py:77` survive the self-test at this head. Dropping `.` from the class `(?<![\w./-])` gives rc 0, and so does dropping `-` (`ev/mutants-head.txt`). Neither is equivalent. With `.` dropped, a verdict naming `a.setup.py:3` lists survivor `setup.py:3`. With `-` dropped, a verdict naming `my-setup.py:3` lists it. The new arm pins only `/`. They are not the previous reviewer's mutants, and this delta review judges only those, so they do not block. A two-arm addition to the self-test (`a.setup.py:3` and `my-setup.py:3` against survivor `setup.py:3`) would kill both. Carry: R10-REVIEW-ENUMERATE

## Evidence

- Previous Block item, survivor `tools/audit/seat/survivor_list.py:77` (left-boundary lookbehind removed): **closed**. I repeated the previous reviewer's full mutant set at this head (`ev/mutants-head.txt`). `token_lookbehind_off` now gives rc 1 KILLED, by `FAIL a key is a whole token: tools/setup.py:3 does not list setup.py:3`. I also ran `lookbehind_word_only` (class reduced to `\w`), which is KILLED. The other mutants are KILLED again: diff_rx_off, spec_null_kept, lives_off, pinkilled_off, triaged_off, token_lookahead_off, class_off, rc1_to_0, unreadable_rc0 and rglob_top. Null control: `NULL rc=0 SURVIVED`. `class_anchor` still survives. The previous verdict judged it equivalent, and the body's `## Repair` records that, with `Carry: dismissed`. I agree: `re.match` already anchors at the start. The checkout was confirmed clean after each mutant (`git status --porcelain` empty).
- Previous Finding, stale scope figure: **closed**. At this head, `closure.py select --diff <merge base>` printed `MODE: SCOPED -- 3 script(s) run, 30 scoped out`. `closure.py select --files <three-dot files>` printed `MODE: FULL`, with the reason `tests/closures.json changes the gate itself`. Both match the body's re-taken figures, and the old figure is withdrawn (`ev/closure-select.txt`).
- Diff outside the repair: `git diff 81741e448..41a196a24` touches 23 files. All but `tools/audit/seat/survivor_list.py` (+2 lines, `c7b72252c`) come from origin/main merges. The three-dot diff against merge base `daf8b349f` has the same 8 files as before. Its only change since the blocked head is that self-test arm. `VERSION`, the manifest, `RELEASE_NOTES.md` and every `*_budgets.json` are untouched (`ev/untouched.txt`).
- `survivor_list.py --self-test` printed `20 checks, 0 failed`, matching the body (`ev/survivor-selftest.txt`). `bus.sh --self-test` printed `162 checks, 0 failed`, rc 0, matching the body (`ev/bus-selftest-head.txt`).
- `PYTHONPATH=tests/hastub python3 tests/entities.py` ran plainly at this head, with no BASH_ENV or PREPR_SKIP_CLOSURES workaround. It passed clean: `ALL 2668 ENTITY CHECKS PASSED`, rc 0 (`ev/entities-head.txt`). `tests/structure.py` printed `STRUCTURE RATCHET PASSED` (`ev/structure.txt`).
- Merge with main: `git merge-tree --write-tree origin/main HEAD` rc 0, no conflict (`ev/merge-tree.txt`).
- Body: `## Head` names `41a196a24` and accounts for the chain from `81741e448`. The delivery row `dev/programme/delivery/3341.md` is in the diff and reads open. `## Red checks` says none. When the packet was rendered, the `gate` run was cancelled (`id=128869794912`, superseded) and later re-ran. See the CI line for its final state.
- CI, every check-run on the one page (55 runs, total_count 55): no concluded failure except `gate` job 128876728348 (edit run, in the Block). Its required siblings in the code run are all success: gate, pr-contract, closures, fast (3.14), coverage, mutation, browser, typing, briefs, instrument-self-tests, policy-docs, env-matrix, arch-score and budget-raise-gate. The body's `## Red checks: none` was written before CI ran. `pr-contract / pr-contract` (job 128881868349) started at 22:27:28Z, after the red at 22:04:58Z, and concluded success.
- Not re-derived: the brief's motivating `review_strength.py` counts. They read live refs, and the body does not quote them.

## Friction

- The brief names `tools/audit/seat/carry_audit.py`, but that path does not exist. I used `tools/audit/carry_audit.py check`.
