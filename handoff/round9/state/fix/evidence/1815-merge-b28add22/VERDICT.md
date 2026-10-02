Fix review: merge b28add222acd94ef8f61560d522d197219b91458

Merge delta of 66cc8ccd (verdicted) with main c4f1c263 (#1813).
- The tree of b28add22, 167068f7, equals git merge-tree --write-tree 66cc8ccd c4f1c263.
- Main side since dc6c97e4: tests/entities.py +54 and tests/nightly_status.py. Neither touches closure.py, closures.json or the scoping paths.
- tests/entities.py auto-merge: the branch's +/- lines are byte-identical before and after the merge, and so are main's. The two hunks are disjoint, and main's hunk does not mention closure.
- Cite CI at b28add22.
