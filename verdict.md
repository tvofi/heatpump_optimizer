Fix review: merge d427c6a8938aa7f0b78f8c6e0dc23cd009df2726

bus-nonce: none-dispatched
pending-ci: gate

## Scope

Round 6. This is a delta review (owner ruling 2026-11-09) from the round-5 merge verdict at `3883d9bb9974e34cae1a2db6ae1b3d0b44c28e79` (verdict/3805 `ba05b1b7bf`). `review_carry.py 3883d9bb d427c6a8` prints `FRESH-REVIEW`. The delta has two parts:
- `88909c98`, the bot's merge of origin/main `3a98735a7e`. Its tree equals the mechanical `git merge-tree --write-tree 3883d9bb 3a98735a7e` (empty diff, `ev/main-merge-resolution.txt`), so it carries no hand resolution.
- The branch's own commits `b638f1ce96` (the move to `dhw_charges.py`), `8d63765ef5` (the `module_excess_loc` re-record) and `9248b8d6f8` (the `TYPE_CHECKING` pin). `d427c6a8` merges `9248b8d6` and has the same tree (`1ff114796b`).

The role contract matches main (`git diff mb...origin/main -- dev/governance/roles/` is empty). No nonce was dispatched to this seat. Its GitHub identity is the owner's (`get_me`: tvofi), which fix-review.md forbids for a verdict, so no hpo-approver comment was posted. The verdict is on a probe ref.

## Evidence

- RESULT the move preserves behaviour. Lines removed from `dhw_planner.py` in `b638f1ce` and `dhw_charges.py` match once blank lines are dropped. The only differences are the new module docstring and imports, the `if TYPE_CHECKING:` import of `DhwPlanner, _DhwPlanContext`, and the rename `_SHORT_K` -> `SHORTFALL_K` (definition plus 3 uses). `dhw_planner.py` adds only the `from .dhw_charges import (...)` block and the renamed use in `_dhw_shortfall`. `optimizer.py` changes one import line and two docstrings. No `_SHORT_K` remains in the tree.
- RESULT finder's harness `dev/audit/harnesses/r11_honest_dhw_runs.py`, all seven arms but `seconds`, at the pre-move tree `88909c98` and at the head: `fixtures`, `stores`, `hysteresis`, `kernel`, `tail` and `combi` are byte-identical, rc 0 at both (`ev/harness-compare.txt`, `ev/h_*`). The head copy's edits read the moved names from `dhw_charges` where the call now resolves them. This is required: an unchanged copy patching `dp.charge_refusal` would no longer see `commit_charges`' lookups. I checked each edit; none changes what is printed.
- RESULT closure-selected scripts at the head, PYTHONPATH=tests/hastub, GOLDEN_MODE=drift against mb `3a98735a7e`: all rc 0 (`ev/t_*.log`).
  - `block_duty` 153 passed; `deployment_shape` passed; `guard_pins` 91; `manual_plan` 132; `plan_view` OK; `solar_alignment` passed; `wood_advisor` 26.
  - `golden`: `NO STALE FIXTURE: 56`.
  - `debug_collect` 164; `typing_ruler` 12; `validate` NO ISSUES; `edge` passed; `backtest` 25; `optimality` 84; `config_flow_steps` 609.
  - `features` `ALL 6069 FEATURE CHECKS PASSED` (`ev/null_features.txt`).
  - Not run here, cited from CI per the 2026-09-30 ruling: `stress`, `entities`, `boost_drift_replay`, `harness_headers`, `finite_boundary`, `card*`, `doc_claims`, `arch_score_head`. CI is pending at this head; see the Notes.
- RESULT `python3 tests/structure.py` at the head: `ok module_excess_loc 21732 <= 21732`, `STRUCTURE RATCHET PASSED`. Against main's budget file (`git diff 3a98735a d427c6a8 -- tests/structure_budgets.json`), only `module_excess_loc` 21779 -> 21732 and `methods_over_200` 7 -> 6 (the latter carried from earlier rounds) change, plus `recorded_at`. No row rises, and no other `*_budgets.json` is touched.
- RESULT step 14, earned: the 21779 -> 21732 drop comes from the move. It takes `dhw_planner.py` from 2580 lines to under the 2000-line threshold's excess by the moved lines. Without the move, `88909c98` measures 22091 (body, `## Red checks`). The move is a real seam: the start condition and commit stage that the planner calls after buying the floor. It is not a re-spelling, and `SHORTFALL_K` is public so it adds no private cross-module crossing.
- RESULT the pin is honest (step 1). Replacing `dhw_charges.py:32` `if TYPE_CHECKING:` with `if False:` (the pin's GUARD_OFF) makes `tests/structure.py` exit rc 1 with `FAIL import_cycle_modules 2 > 0 (+2)`, listing `dhw_charges <-> dhw_planner` (`ev/mut_typecheck_structure.txt`). The unmutated tree passes. At run time the mutant is equivalent, because `TYPE_CHECKING` is False. structure.py's import-graph measurement is the guard's only observable, and it is the check that kills it. The anchor digest `e1433e05` is sha1(`if TYPE_CHECKING:`)[:8].
- RESULT the renamed-line pins were re-measured (the body says the rename was not). With CONST `SHORTFALL_K = 0.1` in `dhw_charges.py`, `tests/features.py` reports `8 of 6069 FEATURE CHECKS FAILED`, rc 1 (`ev/mut_shortfall_const_features.txt`). The null at the head is 6069 passed. The other three renamed-line pins mutate the same comparisons with the identifier renamed. The run-time value and binding are identical, so they carry.
- RESULT claims (step 4): `env_drift.py --all` gives `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56` (`ev/env_drift_all.txt`). The three-dot claim diff is the same `cycling_cost`/`everything_on` claim and suspensions as round 5. `claims-for: 10.1.2` = `VERSION`.
- RESULT versions (step 5): the three-dot diff from mb `3a98735a7e` touches neither `VERSION`, `manifest.json` nor `RELEASE_NOTES.md` (0 lines).
- RESULT merge with main (step 13): `git merge-tree --write-tree origin/main d427c6a8` against `1207ee13b0` gives rc 0. stderr shows `LEDGER-MERGE: resolved tests/closures.json` and no `MERGE-CLAIM` line (`ev/merge-tree.*`).
- RESULT PR body (step 7): `## Head` names `d427c6a8938aa7f0b78f8c6e0dc23cd009df2726`, the head measured here, as the merge of code head `9248b8d6f8`.
  - `## Unpinned sites` names the one site the move added, `dhw_charges.py:32 GUARD_OFF`, as pinned. That matches the ledger file at the head.
  - `## Red checks` answers the reds at `88909c98`: `tests / fast` structure (repaired by this delta), `pr-contract` figure-block and codeql wait.
  - It also names `env-matrix`, `policy-docs` and `briefs` at `3883d9bb`, which settles round 5's `root-cause-unanswered` note.
- RESULT prior findings (round 5):
  - `ci-red` is resolved: the main merge `88909c98` brought the `unloaded_package_imports` row, and the body records `policy-docs` green there.
  - `root-cause-unanswered` is resolved: the body names the three checks.
  - `review-packet` recurs (Notes).
- RESULT CI at this head: `merge_train.py classify d427c6a8 --pr 3805` prints `WAIT d427c6a8938aa7f0b78f8c6e0dc23cd009df2726 pending: gate red: none`, rc 3 (`ev/classify-final.txt`). The PR's check runs show `prelude`, `refresh` and `cancel-superseded` queued since 19:00Z and `arm` skipped.
- RESULT head re-read before return: `refs/pull/3805/head` = `d427c6a8938aa7f0b78f8c6e0dc23cd009df2726` (`ev/head-reread.txt`).

## Findings

- Note: ci-pending: the head's CI has not run (`classify` WAIT, `pending: gate`, runs queued and `arm` skipped, so it is likely held for approval). The heavy scripts this review did not run (`stress`, `entities`, `boost_drift_replay`, `harness_headers`) are uncited until it runs. This `merge` must not be relayed over a non-green head (C8). Carry: dismissed: CI's to run at this head; the relay gates on it
- Note: review-packet: `review_packet.py render --pr 3805 --head d427c6a8 ...` still refuses `UNAVAILABLE: git merge-base --is-ancestor b2ce461c origin/handoff/audit-r11-roster: fatal: Not a valid object name b2ce461c`. This is the fourth round without a packet, and round 5 noted the third instance was owed a root-cause seat. Carry: dismissed: owed to a `root-cause.md` seat dispatched by the orchestrator; instrument state, not this diff
- Note: commit-identity: `9248b8d6f8` is git-authored `tvofi`, while the branch's other commits are `hpo-fixer`. CLAUDE.md's identity rule (0011) reserves writing to the App identities. Paperwork, not a code block. Carry: dismissed: authorship metadata for the orchestrator to confirm; no code effect
- Note: body-title: the PR title reads `Merge remote-tracking branch 'origin/main' into fix/r11-outside-honest-dhw-runs-pr`, a merge subject rather than the group's title. Carry: dismissed: PR metadata for the author App to correct
