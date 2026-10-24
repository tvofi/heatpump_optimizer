#2643 landed the tolerant form, and the follow-up after #2636 copied `attribution` into the hooks registration's ignore list (field_coverage.mjs:114) but left it in pending (:122), so the strict form is half done. Remove the pending entry, so an absent key reads DEAD again.

Roster group: `R10-FLY-NO-FOOTERS`. Part of #201.
