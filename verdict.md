Fix review: blocked 755a94316f90a8fcbc441c867ea53fa4a7427410 main-conflict: pump_arbiter.py and docs/architecture.md conflict with origin/main b0a4ae22de (#3883 flow_anchor), whose ArbiterState.served field must move into arbiter_record.py

bus-nonce: 2a86f7a0ddf4e4ebacd0404167dfe0d9

## Block

- `git merge-tree --write-tree origin/main 755a94316f` (origin/main b0a4ae22de) reports CONFLICT (content) in `custom_components/heatpump_optimizer/pump_arbiter.py` (4 hunks) and `docs/architecture.md` (1 hunk); the ledger drivers resolve `tests/structure_budgets.json`, `tests/closures.json` and the round-4 D6 register. Hunks: `ev/conflict-pump_arbiter.txt`, `ev/conflict-architecture.txt`.
- The pump_arbiter conflict is semantic, not textual. Main's #3883 (R11-OWNER-STEP-KICK) adds `flow_anchor` to the module import, adds `served: flow_anchor.Served | None = None` ("never persisted") to `ArbiterState`, and threads `settle=` through the flow target. This PR moves `ArbiterState` and `FeedbackRun` into `arbiter_record.py`. Resolving it means porting the `served` field into `arbiter_record.ArbiterState`, keeping it out of `persist_record`/`load_record` because main marks it never persisted, and importing both `arbiter_record` and `flow_anchor`. That is a change to production code, so it moves the head. The fixer re-runs steps 2–8 after that merge (fixer.md), and the next round reviews the delta.
- docs/architecture.md: both sides add a module-map row at the same place (`flow_anchor.py` from main, `arbiter_record.py` here). Keep both rows.

## Red checks

`merge_train.py classify 755a94316f --pr 3897` prints `RED 755a94316f90a8fcbc441c867ea53fa4a7427410 pending: none red: gate` (exit 1). `gate` is in the `owed-reds` set (`ev/owed-reds.txt`). The gate job (run 46179041619) fails on these lines:
- `tests / fast (3.14, 3/4)`: `tests/doc_claims.py` comment ratchet `REFUSE tests/features.py: long units 465 -> 466` (a sentence over 40 words, starting "The cycle and the duty toggle (N-solve-recompute) share their write tail (``_actuate_plan``), ..."), scope total 2294 -> 2295.
- `tests / fast (3.14, 1/4)`: `tests/entities.py` features freeze: `tests/features.py has span 'R11 seam actuation writes — the added write rails, each driven at its own branch', which tests/features_frozen_budgets.json does not list` (252 listed, 253 live). main froze `tests/features.py`, and this PR's span (present since the reviewed head 765414af) has to move to its seam's features script.
- `budget-raise-gate`: `RAISE class_excess_loc 17191 -> 17205`, `RAISE max_class_loc 7753 -> 7766`, `REFUSED: no decisive review by tvofi`. The owner's approval of a raise comes after the verdict. This line is not a block.
The first two reds are this PR's test placement and comment length. Both re-run on the head that resolves the conflict. A local `prepr.sh` run against current main would have caught both before push (defect-root-cause.md), so the fixer owes a root-cause answer for each at that head unless they are fixed before it.

## Evidence

- RESULT head=755a94316f90a8fcbc441c867ea53fa4a7427410 reviewed-head=765414af4e6ad2bc24aa7f491267e205b8410d9b scope=delta
- RESULT merge-tree=CONFLICT files=2 (ev/merge-tree.txt, main at ev/main.txt)
- RESULT classify=RED red=gate (ev/classify.txt)
- review_packet.py render printed `REFUSE structure: ... head does not merge cleanly with origin/main` and `REFUSE required-red: gate`. The merge conflict blocks the delta review: no mutation or harness re-run was done at this head, because the head has to move to merge with main. The next round reviews the previous verdict's findings and the delta.
