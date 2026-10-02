# EG-B2 resume note

Stage: round 2, code head 00b27978c930a8a7c7407af9799f06bcb5900c95 (branch handoff/r9-eg-surface-identity): fix 907eedf6, main 777c2318 merged (b8929353), carry-1645.json re-cited for the round-1 briefs block (efe4502a), main c168ec0a merged (00b27978).
prepr.sh: clean at b8929353; re-run at 00b27978 in progress (its closures step outran a 30-min limit once). brief_lint rc 0 and scoped gate as round 1 at 00b27978.
Evidence: /mnt/project-files/audit-r9/fix/evidence/EG-B2-907eedf6/ (identity snapshot script and TSVs, archscore vectors, mutant and gate log tails).
Agreed with the coordinator: EG-B2 deletes last_optimization, next_optimization, solar_radiation and floor_return_temp; F10.4 keeps the rest of the dead members. Whichever merges second takes main in and re-measures structure.
Next: fix review (fix-review.md) at this head. The branch is frozen; only the orchestrator moves it.
Environment: Python 3.13 venv needed (tests/entities.py uses 3.12+ f-strings); keep the venv outside the worktree or prepr's closures step reads it as UNDER-SCOPED.
