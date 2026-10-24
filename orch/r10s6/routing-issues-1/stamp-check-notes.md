stamp.py runs rule 4 (notes name every merged pull request) only after rule 1, so a notes omission is found at stamp time. Add --check-notes FILE, which runs rule 4 alone over the window since the last tag and writes nothing.

Roster group: `R10-FLY-STAMP-CHECK-NOTES`. Part of #201.
