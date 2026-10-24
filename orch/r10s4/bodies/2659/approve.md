Approved under mandate 6329234399 (scope all) at head 5c091c198bb3d4663df171b918ecc80eb415428b.

Fix review: merge at this head (review/2659 ba10e553, verdict d4b4639d). The red-first commit, a mutant of the flag check, a plant with rc 1 without the flag and rc 0 with it, and a null control (unflagged runs still grade all nine harnesses) all check out. The flag is set only by closure.py's recording path, and the fast lane runs harness_headers.py without it. `git merge-tree` against main a6620c3 is clean. The one finding was dismissed in the verdict.
