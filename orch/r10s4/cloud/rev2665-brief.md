Fix reviewer for PR #2665, P2b-pre2 of R10-CI-LAYOUT-P2 (CRITICAL PATH: it gates the P2b ruleset cut-over). Branch fix/r10-ci-layout-p2b-pre2, head 29b08d042f6e0e125079e95a6d907a724d8e73d9, base main 4c31eb16e. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. Your ev/ MUST contain ev/HEAD.txt holding the full 40-hex head, or the relay refuses the verdict.

Context (owner-mandate ruling (a) on #2662's round-2 Block 1): main's ci-ratchet is red on critical_path_minutes, 57.65 against a budget of 54.825. Its path is `fast (3.14)` at 40-56 min, about 41 of them the architecture-score pair. This PR ports U5b's split (1ae2cf9ff) into main's current tests.yml, so main's push gate can go green before the cut-over window. Commits:
- 509ac38ad: a tests/entities.py pin that the new `arch-instrument` job takes `fast`'s scope by exact copies of fast's two scope steps;
- b759eaadd: tests/run.sh gains RUN_PART=fast|arch, tests.yml gains the arch-instrument job, and lane-proofs needs both;
- 29b08d042: the delivery row.

Verify adversarially:
(1) Three-dot diff `git diff $(git merge-base origin/main HEAD)...HEAD`: only tests.yml, tests/run.sh, tests/entities.py (plus fixtures), and dev/programme/delivery/2665.md.
(2) The required contexts are unchanged. Extract every job name and check name that main's ruleset 23698884 requires (read the ruleset once) and confirm each is still produced by name at this head. A rename or drop of a required context blocks.
(3) Coverage parity: the union of what fast and arch-instrument run at the head equals what fast ran on main. No script is dropped and none runs twice in a way that changes a verdict. Show it by RUN_PART listing at the head against main's run.sh listing. Scope parity: the pin's two step copies equal fast's steps byte for byte. Mutants: change only one copy (the pin must go red), drop arch from lane-proofs `needs` (show what catches it, or carry it), and make RUN_PART=arch run nothing (show what catches it).
(4) The critical-path claim: read this head's own CI run, with one bulk check-runs call plus the run's job timings. Report fast's and arch-instrument's durations and the run's critical path, against the 54.825 budget. If the run has not completed, record that figure as not measured under ## Evidence; that does not block. Check every figure in the body at this head.
(5) ci-ratchet itself: at this head, does the ratchet read PR runs or only push runs? State which median moves after the merge, and how many fast pushes it takes before it goes under 54.825, from main's last 8 push-run critical paths (read them once).
(6) `git merge-tree --write-tree` against origin/main is clean. VERSION is untouched. No commit carries a footer or Co-Authored-By (git log --format=%B). Record the scoped-gate MODE line.
Rules: PREPR_SKIP_CLOSURES=1; spare the GitHub API (bulk calls, stop on a 403); no Claude footers.
