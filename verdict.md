Fix review: merge 70461316332c060932e77577e392aeaf40123dbc

bus-nonce: a19316f20483eb9bad7406bded7254f0

## Evidence

- Round 1 review of #3399, measured at head 70461316332c060932e77577e392aeaf40123dbc (still the PR head and the branch tip at verdict time, `git ls-remote`). Merge base b8f67a775137a8032d5c71b34ea64165c1d4613a; `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract read is current.
- Merges with main: `git merge-tree --write-tree origin/main 70461316332c060932e77577e392aeaf40123dbc` exit 0, no conflict.
- CI: `merge_train.py classify 70461316332c060932e77577e392aeaf40123dbc --pr 3399` exit 0, `GREEN 70461316332c060932e77577e392aeaf40123dbc pending: none red: none` (ev/classify-log.txt). No required check went red on this head, so no root-cause answer is owed; the body's "Red checks: none" matches.
- Head self-tests, all exit 0: replan.py (0 failed), roster_lib.py (85 checks), gate_priority.py (15), open_driver.py --self-test (89), plan_page.py (77), merge_train.py (608), orchestrator_tick.py (300), roster_edit.py (270).
- Mutation proof, my own mutants on the production lines, each restored afterwards (ev/mutants-batch1.txt plus the run below):
  - roster_lib.dispatch_rank, outside returns RANK_OTHER: 2 FAIL (the dispatch_rank check).
  - replan.dispatch_tier, the off-path outside arm disabled: self-test 2 failed.
  - replan.build_plan priority re-prefixed with critical-path-first (the #3304 order brought back): fails "within the top tier height orders an outside group and the critical path". This is the PR's stated `top-tier-unordered` claim re-done independently, and it holds.
  - gate_priority, RANK_TOP mapped to HOTFIX_PRIORITY: 7 FAIL.
  - open_driver.default_class, `outside | critical` cut back to `outside`: 9 failed of 89. FENCED 1 -> 0: 1 failed.
  - merge_train.drain_order, outside and critical split back into two keys: 2 failed of 608.
  - roster_edit.op_set_source, SOURCES validation removed: FAIL (refusal check).
  No surviving mutant.
- Null controls in the body re-run inside the self-tests above: a production group with no outside source stays tier 4 and starts after the outside one (replan); a roster with no source field orders as before (open_driver run_pass null, merge_train P420 null, orchestrator_tick null). All pass at the head and are among the checks the mutants turn red.
- VERSION, the manifest, RELEASE_NOTES.md, tests/golden and both claim files are untouched by the three-dot diff. No budget file is touched, so step 14 has no instrument movement to attack.
- Body figures: "Figures: none"; figure_lint at the head reports 0, carry_audit at the head reports 0 finding items. Forward-carry: none, which fits: the change is to the instruments themselves and the roster brief of R10-FLY-REPLAN-TOP-TIER (handoff/audit-r10-roster at 08cd11605b38fab28453f30e22c2b4339af6ce59) already states the new order.
- Finder's harness: none. This is an owner-ordering change, not an audit finding; the per-reader self-test arms are the harness, and I built no instrument of my own beyond the inline string-replace mutants recorded here.
- Not verified: the 2026-11-08 owner statement itself. It appears in the tree only as the orchestrator's restatement, in two wordings (the roster brief: "outside requests and the critical path, all top priority, in no particular order"; replan.py's comment: "landing the outside requests, and landing the critical path ... All of them have top priority ... in no particular order"). Mandate 6715477401 is cited on main (roster_lib.py:375) but the quote has no in-tree primary source I could open. I judged the code against the brief as written; whether the brief reads the owner right is not something this review can establish.
