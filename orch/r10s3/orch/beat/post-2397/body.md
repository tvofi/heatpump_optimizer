Post-merge beat.

Merged: #2397 (fix/r10-test-orphans, merge f1b21daab, train t7) and #2412 (record/autofix, delivery rows for #2365).

Issues closed: none. #2397 carries "Part of #201" and no closing keyword; nothing to close (state read back: #2220 closed since #2323, #2329 merged).

Roster: #2397 re-applies the R10-PRE-EDIT-HOOK row and the R10-REGISTRY-LEAK early_cutoff detach assertions. Neither has a group of its own beyond those two; R10-PRE-EDIT-HOOK was already `done` (set-stage returned byte-identical, nothing to push), so the roster stays at 789b67eec848.

Leaves #201 open.
