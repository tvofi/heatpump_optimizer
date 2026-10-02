Fix review: merge 52d488ba542c8b290b6ab49e46693a93b7710bc8

PR #1837, R9-F10.9d, round 3, a delta review. The earlier verdicts on this branch are blocked 39fda423 (round 1) and merge 851237fc (round 2).

## The delta, 851237fc..c590bbaf
The code change is one tests/closures.json row, `inert_reads["tests/entities.py"] = ["LICENSE"]`. It is needed because round 2's entities check runs a Python child under --exec-record that reads LICENSE, and CI `closures` (Tests run 36949999009) went red at 851237fc with INERT READS UNDER-APPROXIMATED. My round-2 review missed this too: like the fixer, I never ran a record-then-check of the script whose test code changed.
The body (8045f383) names the red check and answers it with a cause, a cheaper detector and its cost (about 7.5 minutes), process state (b), and a recorded decision to build no countermeasure. That satisfies step 11.

## Carry, c590bbaf..52d488ba
- Main moved to f7f6c1d1 (#1836, UX-2). The merge base is 3bd6f122.
- No file changed on both sides; the intersection of the two name-only diffs is empty.
- 52d488ba's tree equals merge-tree(c590bbaf, f7f6c1d1) exactly, with an empty diff (tree 3f174e8a).
- Main's side touches claims.json and docs/dashboard-card.md, which harness_headers.py could read. So I re-measured on the merged tree rather than trusting the textual carry.

## RESULT, on tree 3f174e8a (the same as 52d488ba), Python 3.13, requirements-ci, Linux with strace (rec3.log)
- `closure.py record tests/entities.py`: rc 0, ALL 2055 ENTITY CHECKS PASSED, inert_reads = [LICENSE].
- `closure.py record tests/harness_headers.py`: rc 0, ALL 94 HARNESS HEADER CHECKS PASSED, inert_reads = the five committed files. #1836's claims change adds no read.
- `closure.py check --in-dir rec3 --partial`: rc 0, "committed closures cover every file this run touched". I did not record every script; CI's closures job does that.
- Round 2's mutant results stand, because the code is unchanged since 851237fc apart from a data row.

## CI at 52d488ba when I wrote this
Every completed check is green. `closures`, `fast (3.14)`, `coverage` and CodeQL `Analyze (python)` are still running. The merge seat merges only once those are green.
