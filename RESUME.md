# R9-F10.5 resume note

- branch: handoff/r9-f10-gate-infra-5 @ f3e2e445bb981eff4fef38242bcb8ac520a7afa6 (code). Draft body on handoff-body/r9-f10-gate-infra-5.
- base: #1838 head 46a70815 (F10.4, not yet merged). WAITING on #1838's merge: then `git merge origin/main`, re-run fixer.md steps 2-8 (entities.py on py3.13, mutants via evidence run_mutants.sh, structure.py, prepr.sh), re-take figures, re-body, hand off to the coordinator.
- done: code, tests, mutation proof (M0 null passes, M1-M8 killed), 40-site drain demo on handoff/r9-f10-gate-infra-5-demo @ f59380e0 (37 pinned, 3 survivors, re-apply skip-unchanged).
- evidence: /mnt/project-files/audit-r9/fix/evidence/F10.5-drain-f3e2e445/
- the remaining prepr refusals at this head are #1838's own red checks (briefs, budget-raise-gate, fast (3.14)) in the range; they leave the range once main carries #1838.
- environment traps: python3 3.11 here (use /tmp venv with 3.13 + tests/requirements-ci.txt); clone was shallow; stress.py timing kills the null control on a contended 4-core box (left out of the demo).
- open: hpo-ledger App + secrets are tvofi's setup.
