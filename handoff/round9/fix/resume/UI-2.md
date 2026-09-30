# UI-2 resume note (2026-09-30T22:20Z)

Stage: code head complete and pushed; awaiting the Mac's draft PR and review.
Code head: 0723471d0e5554d7c938ab5b7fb90398c3eb224b on handoff/r9-ui-2 (same commit on handoff/r9-ui-2-i38q58), base main 59c2543b.
Body: handoff/round9/fix/resume/UI-2-body.md. Not run here: tests/ha_contract.py against the real pinned HA (not installed in this container; the change touches no Python module), mutation table (docs-only diff draws no mutant), full gate (scoped MODE: SCOPED names entities, doc_claims, layout, md_tables; all green).
Regenerate figures: HPO_FONTS=<dir> NODE_PATH=<global node_modules> python3 docs/img/readme/make_readme_figures.py.
