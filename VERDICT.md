Fix review: merge 176eb2e6eb4d16ce8d77e34208de19e6a578a8ad

bus-nonce: 2aabd69d1c17716f0f9f093fca2937cb

Delta review of the main merge since the merge verdict at 143c3767f9178089b7d56b6b1ca002118046a97c (comment 7003010795), under the later-rounds delta-review ruling.

- The PR's three-dot diff at both heads: 118 files, +1868/-34 each time. The two diffs differ only in blob index lines, hunk offsets, and one context line in a tests/features.py hunk header, which #3815 on main inserted ahead of the PR's appended block. No line the PR adds or removes changed. Evidence: ev/diff-old.patch, ev/diff-new.patch, ev/diff-of-diffs.txt.
- Merge 176eb2e6 has parents 143c3767 and 9d65fe80. Running git merge-tree --write-tree on those parents reproduces its tree, bfe7fbbe, exactly. The tests/closures.json merge driver resolved that file as a set. No hunk was resolved by hand. Evidence: ev/remerge.txt, ev/head.txt.
- Checks at the head: every check run finished as success or skipped, and none failed. The required gate check passed, and so did tests/mutation. Evidence: ev/checks.txt, ev/required.txt.
- The prior verdict left no open findings, so none carry forward.
