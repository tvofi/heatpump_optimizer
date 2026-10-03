Part of #201.

The owner's rulings of 2026-10-03 (tvofi): useful tools belong under `tools/` on `main`, as a permanent repository mechanism, and above all the programme's own instruments (what merges, approves, carries, stamps, gates, watches CI or records state) are tracked, self-tested files. A later ruling the same day: audit instruments are not code-owned; ownership follows decision 0013, unamended. That day a temp cleanup deleted `/private/tmp/audit-7`: the seat venv the `~/hpo-seats/bin` shims ran (no recipe anywhere), the state three tracked seat scripts kept there, and the design note decision 0012 cited.

This pull request does three things.

1. **Lands the instruments and recipes** that lived only in scratch or `~/hpo-seats/bin`: the merge train (`tools/audit/seat/merge_train.py`), the seat venv recipe and its shims, the PR open/update scripts, and the thermal_model parity harness.
2. **Makes the rule permanent**: `fixer.md` step 17 states the obligation and the reusability criterion once; `fix-review.md` step 9 and `orchestrator.md` section 13 point to it. A new check, `tools/audit/seat/tmp_paths.py --check`, refuses a tracked script, workflow or decision record tied to a temp or machine path; it runs with its self-test in `governance.yml`'s `instrument-self-tests` job and in `tools/audit/prepr.sh`. That job grades nothing, which is the only place an unowned, unpinned copy may run (`codeowners_gap.py`, #1515); a red there is still a red at the head that `pr-contract` makes the body answer. Making it a pinned grader in a required job is a two-step follow-up: the base must carry the file before a job can restore it, and pinned `field_coverage.mjs` must declare it. `CODEOWNERS` now owns `tools/release/` (the version stamp, release tooling, not an audit instrument); `tools/audit/seat/` stays unowned.
3. **Fixes the paths it finds**, and makes `app_approve.sh`'s carry run on macOS bash 3.2.

### Inventory

Reusable: a later round or seat reruns it, or a body figure needs it to be reproduced (`fixer.md` step 17). A one-off probe may stay in scratch.

| tool | where it lived | verdict | reason |
|---|---|---|---|
| `ci-watch.sh` state | `/private/tmp/audit-7/ci-watch-state` | fixed | `$HPO_STATE_DIR/ci-watch-state` |
| `handoff_push.sh` | `/Users/...` checkout and worktree, body in `/private/tmp/audit-7/v6612` | fixed | checkout from the git common dir, worktrees beside it, body in the state dir; header names its successors |
| `merge_pr.sh` | state in `/private/tmp/audit-7/orchestrator`, `cd /Users/...` | fixed | state dir, common-dir checkout; header points to the train |
| `remerge_main.sh` | `cd /Users/...` | fixed | toplevel of its own checkout; neutral wording folded in from `remerge.sh` |
| `worktree_gc.sh` keep-dir | `/tmp/hpo-ev` | fixed | cited evidence kept in `$HPO_STATE_DIR/ev`, outside every temp dir; the seats root `/tmp/hpo-orch` stays (scratch meant to die) |
| decision 0012 source | `/private/tmp/audit-7/r8prog/design-rotation-and-D14.md` | fixed | cited at commit `12743bf742e09cbe50b49ae02f8348798b273885`, branch `claude/project-thread-s8rmov` |
| `~/hpo-seats/bin/python`, `python3` | shims to the deleted venv | landed | `tools/audit/seat/shims/seat-python{,3}`, installed by `seat_venv.sh --install-shims <dir>` |
| the seat venv | hand-built in `/private/tmp/audit-7/r9-mac/ha-venv` | landed | `tools/audit/seat/seat_venv.sh` |
| `~/hpo-seats/bin/approve.sh` | `mapfile` shim for bash 3.2 | delete locally | `app_approve.sh` no longer needs it (Figures) |
| `~/hpo-seats/bin/mergewhen.sh` | reads `~/hpo-seats/tools/main`, already gone | superseded | `merge_train.py` with a one-entry queue; its stale-base guard is subsumed by the train's step 4, which refuses a head not containing the `main` it merges into |
| `~/hpo-seats/bin/waitci.sh` | local | folded | `merge_train.py wait-ci <sha>` |
| `~/hpo-seats/bin/openpr.sh`, `updatepr.sh` | local | landed | `tools/audit/seat/open_pr.sh`, `update_pr.sh`, state dir and venv PATH |
| `scratchpad/orch/train3.py` (and `train.py`, `train2.py`) | session scratch | landed | `tools/audit/seat/merge_train.py` |
| `scratchpad/orch/remerge.sh` | session scratch | folded | into `remerge_main.sh`, no duplicate |
| `scratchpad/orch/eta.py`, `demo-b.sh` | session scratch | leave | one session's ETA overlay and one PR's demo push |
| `mypar2.py`, `parity2.py`, `compare.py` | reviewer and fixer scratch (R9-EG-A2) | landed | `tools/audit/harnesses/thermal_parity.py` |
| `mutants_r4b.py`, `mutants3.py` (#1863), `rev_mut.py`, `mutate_pages.py` (#1876), `seat-p11-barrier/mutants.py`, `seat-r-p11/mut/mut.py` | seat scratch | leave | one PR's mutant generators, keyed to that diff |
| HA floor sweep (`seat-rca-hafloor/sweep.py`, `floor_names.py`, `census_fixer.py`) | RCA seat scratch | leave | the RCA seat's own evidence; it lands with that analysis if reused |
| `race_probe.py`, `mutants_r3.py`, `census.py` | deleted | lost | not recoverable from report text at a size worth retyping |

Left in place (fixtures and documented conventions, each named by `tmp_paths.py`'s rules or allow list): `gh_comment.py`, `app_comment.sh`, `app_approve.sh` and `prepr.sh` self-test fixtures, `/tmp/hpo-gate.lock`, a workflow runner's `/tmp`, `/home/user/` in the cloud seat image, `tests/card.mjs`'s legacy plan-data path.

### The merge train

`merge_train.py run <queue.json> [--mandate LABEL] [--approver-role ROLE]` per pull request: recarry through `remerge_main.sh` when the head lacks `origin/main`; wait for every check run (`--ignore-red`, default `nightly-status`); `app_approve.sh --carry`; `origin/main` still in the head; **refuse any policy path** (`policy_lint.mjs --corpus-filter`, sentinel-probed as `preflight.sh` does); approve by the App, or, only when the App refused for code-owned paths and `--mandate` is given and no `*_budgets.json` changed, by `gh pr review` with a body naming the mandate label, role, paths, verdict comment and head; ready, title preflight, merge with `--match-head-commit` (main re-checked before each try), closing-issue read, `worktree_gc.sh`. It stops the queue at the first refusal. Narrower than `train3.py` on one point: a missing-evidence refusal is no longer overridden by a mandate.

### What is not built

A `## Figures` check that a cited script is tracked or marked one-off. `figure_lint.mjs` already refuses an in-tree path that does not resolve and reports an out-of-tree one `unverified`. A "one-off" marker would be the seat's own word on the very judgement the rule asks for, so it adds nothing a reviewer does not already see. `fix-review.md` step 9 now makes it the reviewer's.

## Approval

Approved by the orchestrator under mandate 5951564627, on the owner's instruction, after a `Fix review: merge` verdict at the head. The policy files are `tools/audit/briefs/fixer.md`, `tools/audit/briefs/fix-review.md` and `tools/audit/briefs/orchestrator.md` (POLICY_GLOBS). The code-owned files are `.github/CODEOWNERS`, `.github/workflows/governance.yml` and `docs/decisions/0012-process-diet-and-round-cadence.md`. Each policy file pays for its new lines inside its existing cap, by cutting a motivating anecdote the rule does not need; no cap is raised. `tools/audit/README.md` and `tools/audit/harnesses/README.md` are policy and untouched. `harnesses/README.md` still tables four instruments; `d907_kernel_band.py`, `hpo_ci_container_setup.sh` and now `thermal_parity.py` describe themselves in their headers.

Audit instruments carry no owner (tvofi, 2026-10-03): `tools/audit/seat/` is not added to `CODEOWNERS`, and decision 0013 stands unamended.

## Head

`32251f44c4a443d015bc3b8cef2c9161e919ec3e` is one commit on `1190f1058d95a001e42a98871c28c0e6f24d9e55`: the owner's ownership ruling. That head merges `origin/main` `20f597c6615b10a5d225497cb13b6d1f2e5cce35` (#1875) into `af085331aa76e2f836054ee2b180008f049b8c93`, which merges `origin/main` `1ccd0b1d5e2e2f21260d1b685271ac97fc7cb28f` (#1869) into the authored code head `e3860e5b6d1da81e0a264ec87b18297a9f99a4ac`, one commit on `12dbd3a5d01f48f44e6c6344bff22d3d015baf9d`. Both merges are automatic, with no resolution.

## Mutation proof

- `tools/audit/seat/tmp_paths.py`: ten mutants, each one rule disabled in a copy (every class pattern, the per-process, runner, lease, scope, per-file-allow and stale-entry rules). All ten turn its self-test red, each naming the arm it disables. Example: disabling `private-tmp` fails "a state dir under /private/tmp is refused".
- `tools/audit/seat/merge_train.py`: thirteen mutants, each deleting one stop (policy refusal, filter probe, budget, no-mandate, code-owned-only, CI red, carry, main moved, preflight REFUSE, recarry conflict, superseded red, head moved, queue stop). Twelve fail a named arm. The code-owned-only mutant crashes the self-test (`AttributeError`, rc 1, no tally line), which the governance step's tally grep also refuses.
- `app_approve.sh`: the base is the mutant. Under macOS `/bin/bash` 3.2.57, `app_approve.sh --self-test` at the merge base prints `141 checks, 2 failed`: "refused as a hand-resolved merge" and "refused by the ci: guard". At the head it prints `141 checks, 0 failed`.

## Null control

- `tmp_paths.py --check --ref 1ccd0b1d5` (origin/main at the head's merge) refuses 14 lines: `ci-watch.sh`, `handoff_push.sh` (3), `merge_pr.sh` (2), `remerge_main.sh`, decision 0012 (2), `worktree_gc.sh` (2), the two hastub doc lines and a harness comment; its one stale allow entry there is this checker's own, which that tree lacks. At the head it reports `0 refused, 0 stale allow entries`.
- `thermal_parity.py`: two plain captures of the same tree compare at `base_head_differing=0`, with 0 unequal scalar-vs-batch pairs of 1872. The `--perturb` capture (inter_zone_transfer × (1 + 2⁻⁴⁰)) differs in 1200 arrays, none outside the two-zone cells. A copy with one batch cell moved one ulp reads `base_head_differing=1` and `head_scalar_batch_unequal_pairs=1`.
- `seat_venv.sh` builds a venv whose `pip freeze --all` (less pip) is byte-identical to the hand-built one: 14 packages.
- `merge_train.py`'s null arm: a green, carried, non-policy pull request merges, and the train prints `TRAIN DONE`.

## Figures

- `python3 tools/audit/seat/tmp_paths.py --check --ref 1ccd0b1d5`: 14 refused, 1 stale, rc 1. `python3 tools/audit/seat/tmp_paths.py --check`: 0 refused, rc 0.
- `python3 tools/audit/seat/tmp_paths.py --self-test`: 18 checks, 0 failed.
- `python3 tools/audit/seat/merge_train.py --self-test`: 25 checks, 0 failed.
- `bash tools/audit/app_approve.sh --self-test` on `/bin/bash` 3.2.57: 141 checks, 2 failed at the merge base; 141 checks, 0 failed at the head.
- `bash tools/audit/worktree_gc.sh --self-test`: 66 checks, 0 failed.
- `bash tools/audit/prepr.sh <body>`: every step ok, its own self-test 148 passed, 0 failed.
- `PYTHONPATH=tests/hastub python3 tools/audit/harnesses/thermal_parity.py capture <out.npz>`, twice, then `--perturb`, then `compare`: the null-control numbers above, on the M1 with numpy 2.4.6 and python 3.14.7. `thread_factor` 1.000.
- `bash tools/audit/seat/seat_venv.sh` with `HPO_STATE_DIR` set to a scratch dir: python 3.14.7, numpy 2.4.6, scipy 1.17.1, about 20 s wall.
- `node .claude/workflows/policy_lint.mjs`: `TOTAL: 0 error(s) across 40 policy file(s)`. `node .claude/workflows/field_coverage.mjs`: `FIELD COVERAGE ok`. `python3 -I tools/audit/round6/D11/fix/codeowners_gap.py --check`: `uncovered_files=0`.
- Scoped gate (`python3 tests/closure.py select --diff <merge base>`): `MODE: SCOPED -- 4 script(s) run`, namely `entities.py` (2108 passed), `harness_headers.py` (95 passed), `open_meteo.py` and `solar_alignment.py` (passed); `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

none at handoff; CI has not run. One local note: a single `tests/entities.py` run at this tree failed "the lease has one winner ... run.sh runs unleased" (`run_sh_unleased=False`) at load 8-10; the immediate re-run at the same tree passed all 2104, and the diff touches neither `tests/gate_lock.py` nor `tests/run.sh`.

## Forward-carry

The obligation is carried into the three role contracts this pull request edits: `tools/audit/briefs/fixer.md` step 17, `tools/audit/briefs/fix-review.md` step 9 and `tools/audit/briefs/orchestrator.md` section 13.

## Friction

none
