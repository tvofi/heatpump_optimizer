Fixer seat r10s6 fix-2887-s8, PR #2887 (R10-BUFFER-STORE).
Code head a5f40d84c407c90fbaf51cf6de6b14c8e062b765 on handoff/r10-buffer-store: merge of origin/main e8cb7e683 into fc841f51d (driver-resolved structure_budgets + closures), fold of the duplicated 35 L fallback, dT_cap line split, three equivalent survivor triages, class_excess_loc re-record.
Owed: update_pr.sh fix/r10-buffer-store-pr a5f40d84c <BODY.md> 2500 (runs prepr), mark ready, approve held runs; tests/mutation stays red on one site (thermal_model.py:1756 CLAMP_DROP, killed by features.py) until mutation-autofix pins it.
Not run to completion locally: entities, guard_pins, finite_boundary, golden drift, features (seat time bound).
