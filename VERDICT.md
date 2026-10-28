Fix review: merge cc0510ee2a25444363251df640509b3034bca4f6

bus-nonce: ff2ea98c4e75a1315ce4b96f65b2656c

## Round

First fix review of #2912 (R10-CONFIGFLOW-PAGES arm A + A3'). Measured head `cc0510ee2a25444363251df640509b3034bca4f6`; merge base `eab04d0ebf8c45667099b668ab0d8bf976d5f99a` (= origin/main at review). `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Findings

- Surviving mutant on an added line: in `HeatPumpOptimizerOptionsFlow._entities_errors`, `view = {**current, **submit}` -> `view = dict(submit)` leaves `tests/config_flow_steps.py` at `ALL 531 checks PASSED` (ev/mutants.txt, R6). It is equivalent in production: the options form always submits the required `price_source` select, and `_clear_absent` puts a cleared `price_entity` in the submit as `None`, so `current` never supplies either key to `view`. The A3' behaviour the body names is pinned by A3'-M1/M2 and by my R5, which all die. Carry: dismissed: equivalent mutant under Home Assistant's form semantics, the `current` merge is defensive only
- PR body hygiene: lines 69-116 of the body repeat `## Mutation proof` and `## Unpinned sites` under a broken heading (`## Null control\` and \`## Figures\` was measured ...`), a copy-paste remnant. `--body-check` does not catch it (the packet's figure_lint and carry_audit pass), but a reader sees two copies of each section. The orchestrator should remove the duplicate block before merge. Carry: R10-CONFIGFLOW-PAGES
- Owed after this verdict: the head moved during the review to `4fc6a4c51ad990b04f7911807c83b245df3a2141` (`ci: pin killed mutants`, github-actions[bot]). It adds 32 `tests/mutation_ledger/killed_by/config_flow.py/` rows and nothing else. At my last read its CI run was `queued` (a GITHUB_TOKEN head is held `action_required`, ci-autofix.md). The `tests / mutation` job log at `cc0510ee` could not be read here (the Actions log blob host returned 403 through the proxy), so I cannot tell whether every predicted site was killed or some survivor is left. Before merging, the orchestrator must see `gate` and `tests / mutation` green at `4fc6a4c51`, and re-check the body's `## Red checks` `mutation` line, which the pin stales (ci-autofix.md). Carry: R10-CONFIGFLOW-PAGES

## Evidence

- Merge with main: `git merge-tree --write-tree origin/main cc0510ee` exits 0 with tree `df2b246668cb131c4cebfb0b5bc316f441a9e51c`, no conflict (ev/merge-tree.txt).
- Suite at head (Python 3.14.7, /opt/hpo/venv-ci): `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` gives `ALL 531 checks PASSED`, rc 0 (ev/head_config_flow_steps.txt). The head's tests over merge-base `config_flow.py` give `6 of 531 checks FAILED`, rc 1: the five `a rejected <page> submit re-renders each cleared stored entity empty` checks (entities 9, entities_metering 9, comfort 1, hot_water 1, building 7) and `clearing the stored price entity under an entity source is price_entity_required` (ev/base_cf_headtests.txt). The body's `6 of 530` was taken before the wood-block check was added; the same six fail.
- The body's ported harness `dev/audit/harnesses/r10_configflow_pages.py` (the fixer's own instrument, disclosed as such), run by me at both ends (ev/harness_both_ends.txt):
  - base `RESULT pages=9 rejected=9 stored_rows=30 stale_slots=27`; head `stale_slots=0`
  - `--null`: `rejected=7 stored_rows=30 shown_stored=19` on both trees
  - `--clear-required`: base `type=menu errors=None stored_price_entity=None`; head `type=form errors=price_entity_required stored_price_entity='sensor.price'`
  - `--clear-required --null`: `stored_price_entity='sensor.other'` on both trees
  - `--accepted`: `cases=11 exceptions=1 digest=071e7ad04eb0` on both trees. The exception line matches the body at each end.
  All figures match the body.
- Finder's harness (step 2): `bash dev/audit/rounds/round10/D7/arch-s2/run_findings.sh 08_page` at its pinned base `554e2ecfa` gives `RESULT delta_S=+1.1717`, `admissible=1`, `duplication_copies=68->62`, `perturbed_delta_S=+0.0000`, `perturbed_vector_equals_baseline=1` (ev/finder_08_page.txt), the same as the body and #2238. The harness only applies its patch to its hardcoded base and cannot score a tree that already has the patch, so the head side is the archscore diff: `python3 tools/audit/archscore/score.py --diff eab04d0eb` at head gives `Architecture score: dS +2.3483 IMPROVES`, `duplication_copies 35 -> 29` (ev/archscore_head_vs_mb.txt), the same as the body.
- Mutation proof (step 1), my own mutants on head `config_flow.py`, each in a fresh `git archive` copy (ev/mutants.txt):
  - R1 dropping `current = {**current, **cleaned}`: 7 of 531 FAILED (all seven re-render checks)
  - R2 `_clear_absent(..., current)` (body M6): 1 of 531 FAILED, the wood-block check
  - R3 `finish(cleaned, current)`, not in the body: 1 of 531 FAILED, the wood-block check
  - R4 `if check is not None:` -> `if False:`: 39 of 524 FAILED
  - R5 `check(flat, current)` (body M2): 3 of 531 FAILED, the three the body names
  - R6: survives, see Findings
- Class (step 6): the body's rule is `grep -n 'when='` plus the harness's nine-page enumeration. I also grepped every `{**current, **user_input|flat|submit}` re-render basis (ev/class_rule_grep.txt). The one remaining is `_try_thermal_model_save` (line 3327). The thermal_model pages carry no `_STORED` row (0 matches), so they have no clear to lose. The `_STORED` pages outside the nine (entities_pump, hot_water_pumps, solar_pv, away) have no `check`, so they never re-render a submit. No open seam.
- Claims and versions (steps 4 and 5): `VERSION`, `RELEASE_NOTES.md`, the manifest and both claim files are untouched three-dot (count 0). Golden drift is not re-run here: no claim moved, the body's `GOLDEN_MODE=drift` run was at a commit with this head's `config_flow.py`, and CI's heavy runs are cited, not re-run.
- Numbers moved (step 14): `class_excess_loc` re-recorded 18038 -> 17992. `tests/structure.py` measures 18038 at the merge base and 17992 at head, and prints `STRUCTURE RATCHET PASSED` (ev/structure_head.txt, ev/structure_mb_class_excess.txt). This is a tightening that the fold earned, not a raise. `tests/closures.json` adds the new harness to `INERT`. `tests/entities.py` re-points one disposition from `async_step_building` to `_building_wood_flag`, where the guarded code moved. `PYTHONPATH=tests/hastub python3 tests/entities.py` at head prints `ALL 2467 ENTITY CHECKS PASSED`, rc 0 (ev/entities_head.txt). The six re-keyed ledger rows follow their guards. My R1, R4 and R5 kill `_page` and `_entities_errors` sites.
- Figures re-derived: `ci_predict.py --base origin/main` at head lists 24 ADDED UNPINNED sites in config_flow.py, as the body says (ev/ci_predict_head.txt). The three-dot diffstat at `cc0510ee` is 21 files, +751/-305: the body's 20 files, +750/-305 at `9d043f78`, plus the delivery row.
- CI at `cc0510ee` (step 11, read from the check-runs API; ev/checks_at_render.tsv, ev/checks_live.tsv, ev/workflow_runs.tsv):
  - `tests / mutation` concluded failure. The body's `## Red checks` names it and answers it: ci_predict's 24 predicted unpinned sites, with the cheaper detector `ci_predict.py` already run at handoff. That is the documented `mutation-autofix` path, and the bot's pin commit followed.
  - Every other completed check succeeded, was skipped or was neutral.
  - At my last read, `prelude` (the edit run) and `tests / mutation-pins (1)` were still in progress.
  - No `pr-contract` check run is listed on this head, so I cite none.
- Head moved during the review (step 12): the PR head is now `4fc6a4c51ad990b04f7911807c83b245df3a2141` (bot pin). The carry predicate holds (ev/carry_predicate.txt):
  - the 32 files it adds share none of the branch's own three-dot file list (overlap 0)
  - both claim files at `4fc6a4c51` equal origin/main's
  - the commit holds no reviewer-turn content
  So this `merge` verdict on `cc0510ee` carries to `4fc6a4c51` by `orchestrator.md` section 11, subject to the gate at that head (see Findings).
- Behaviour change (A3'): disclosed in the body as user-visible. It uses the existing `price_entity_required` key, so no strings move.
- Body head SHA (step 7): `## Head` names `cc0510ee`, the head I measured.
