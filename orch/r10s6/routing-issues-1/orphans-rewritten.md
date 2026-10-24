bus.sh orphans treats a handoff whose patch is already on main as stranded, and content_superseded's byte-identical arm misses a file that moved on, so the orphan list carries landed work for days. Classify a handoff whose patch reverse-applies on origin/main as landed-rewritten.

Roster group: `R10-FLY-ORPHANS-REWRITTEN`. Part of #201.
