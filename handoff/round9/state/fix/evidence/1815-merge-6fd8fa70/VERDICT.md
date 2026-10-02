Fix review: merge 6fd8fa7084a0ad56a7e43cc32410471a87a508a3

Merge delta of 4c098c15 (verdicted) with main 90335cbd (F10.8, #1811).
- The tree of 6fd8fa70, 709da606, equals git merge-tree --write-tree 4c098c15 90335cbd.
- Main side: 8 files. Of the files this PR changed, only tests/entities.py is among them.
- tests/entities.py auto-merge: the branch's changed lines and main's changed lines are each byte-identical before and after the merge.
- None of main's added lines in entities.py touches _closure, closures.json, select, affected, not_run or DRIVEN_BY_OTHERS.
- Cite CI at 6fd8fa70.
