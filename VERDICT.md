Fix review: merge 249d76dd62bdab432e2c671edba7d5e96313bf80

bus-nonce: 6a7a49cb392d19f87cc47a43f56d4c1a

Round 1 (no earlier verdict ref for #3398). Measured at head `249d76dd62bdab432e2c671edba7d5e96313bf80`, merge base `b8f67a775137a8032d5c71b34ea64165c1d4613a`, origin/main `3aac11dfba2a252f329159af0f1c15b48d79818b`; the head was unchanged at the final read.

## Evidence

- CI: `merge_train.py classify 249d76dd6... --pr 3398` prints `GREEN 249d76dd62bdab432e2c671edba7d5e96313bf80 pending: none red: none`, rc 0, read at the start and again just before this verdict (`ev/classify.txt`). Heavy runs (gate, mutation table) are cited from CI and were not re-run.
- Merge: `git merge-tree --write-tree origin/main 249d76dd6...` rc 0, no conflict (`ev/merge_tree.txt`).
- Roles: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Mutation proof, re-run by the reviewer (`ev/mutants.txt`, `ev/mutants_runner.py`): the PR's mutants M2, M3, M4, M5, M6, M8, M10, M11, M12 and M13 each FAIL the named check under `features_block.py --through "# --- R10-HOTFIX-LEARNER-INPUTS"`. Unmutated, that prefix prints `ALL 1085 FEATURES THROUGH PASSED` (`ev/unmutated_through.txt`). M15 (`if False:`) under `tests/config_flow_steps.py` FAILs `a combi tank without the buffer store (no throttling valve) is refused, not saved (#3225)`. Each file was restored afterwards and `git status` is clean. I used the `--through` prefix in place of the body's relocated block, so the check names match the body but the pass counts do not.
- Reviewer's own mutant M7r (drop `or not self.combi_tank_active` from `legionella_cycle_active`): survives, rc 0, 0 FAIL. See Findings.
- Golden: `env_drift.py --all origin/main` prints `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56` (`ev/env_drift.txt`). The six claims are additive keys, matching `claimed_drift.txt`'s diff.
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched in the three-dot diff.
- Structure: `STRUCTURE RATCHET PASSED`. `class_excess_loc` and `max_class_loc` moved down only. Arch-score: `Architecture score: dS +0.0006 IMPROVES` (`ev/structure.txt`, `ev/archscore.txt`).
- Figures re-derived at head (`ev/figures.txt`): the shortstat `9 files changed, 201 insertions(+), 63 deletions(-)`; the `8a8ad71f2..baac8a0a2` and `d1975b5b7..8a8ad71f2` production diffs are both empty; the vendor grep sums to 2; `ALL 551 checks PASSED`; the harness `exchange` arm prints `exchange_dhw_kwh=22.135`, `null_dhw_kwh=5.327`, `exchange_rounds=3`, `exchange_worst_shortfall_c=-1.455`, `null_worst_shortfall_c=28.767`, all as the body states. The harness sha1 is `e47dc605...`, as stated.
- Not re-derived, cited from CI's green gate: the gate's per-script counts (`ALL 5086 FEATURE CHECKS`, `2707 ENTITY`, `114 STRESS`, `112 HARNESS HEADER`), the `d1975b5b7` red-gate figures and `ci_predict.py`'s line.
- Red checks: none at this head. The inherited `tests / fast (3.14)` and `tests / mutation` reds are named and answered in `## Red checks` (state (b), and "none cheaper" respectively). `pr-contract` is green at this head.
- Class: the legionella raw-flag readers are enumerated by the `combi_legionella_gate` census. A reviewer `grep` of `dhw_legionella_enabled` outside thermal_model.py returns only the diagnostics raw publish (coordinator.py:8011), the payload field declaration and the services schema, and none of these reads behaviour. The preset slug seam is closed by the `combi_type_branch` census.
- Forward-carry: every body carry is dismissed as built or landed here; carry_audit at head reports `6 routed, 0 unrouted`.
- Harness: the finder's harness is `dev/audit/harnesses/r10_combi_tank.py`. It is committed and unchanged since PR A, and its `exchange` arm was re-run above.

## Findings

- Residual: `ThermalParameters.legionella_cycle_active`'s `or not self.combi_tank_active` arm (thermal_model.py:328) is pinned by no check. The mutant that drops it survives the whole `--through` prefix, which holds the PR B block. `ev/m7r_probe.txt` shows it changes behaviour: with the combi switch on, 0 l potable water and no store (`combi_tank_active False`), the head runs the cycle (True) and the mutant would not (False). The production code is correct. The mutant is outside the mutation table's operator set, and it is reachable only when a combi switch is stored over an inactive store, which the building page refuses (M15). A one-line arm in the `legionella_potable` check would pin it. Carry: dismissed: correct production code; reviewer-only mutant outside the mutation table's operators, reachable only past the building page's combi_needs_store refusal; non-blocking test gap recorded here
