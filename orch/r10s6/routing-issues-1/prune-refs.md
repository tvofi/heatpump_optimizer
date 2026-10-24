prune_refs.apply_plan makes one REST write per tag and per delete (704 for 352 refs) against the shared budget, and its classifier would delete live claude/* session branches and design/ refs whose tips are in main. Batch the writes through git push and exempt live and design refs, with fixtures through tests/throwaway_git.py.

Roster group: `R10-FLY-PRUNE-REFS`. Part of #201.
