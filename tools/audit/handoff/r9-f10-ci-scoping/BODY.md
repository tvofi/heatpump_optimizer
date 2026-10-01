<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi** · [project thread](https://claude.ai/code/project/chan_01EL5jLi4rokGBbkaevYXSJV?thread=cmsg_01EL5jLi4rokGBbkaevYXSJVYKatV7FXxQxAPuXRz23zkw)_

Round-9 fix PR F10.9 (roster group R9-F10.9): part 1 of #1812, the PR-gate scoping waste the CI scoping audit measured over the last 20 successful PR runs (#1799 to #1810). Part of #1812; R9-F10.9b (coverage on reachable scripts, the holistic pass including #983 and mutation baseline speed) closes it.

Before: a pull request that touched `tests/closures.json` ran every `fast` script; a change reaching `tests/dst_checks.py` re-recorded every closure in the `closures` job; and a scoped gate's NOT RUN block said `tests/harness_headers.py` and `tests/layout.py` "did NOT run" on every gate that ran them.

After: a `tests/closures.json` change runs the scripts whose own entry moved (grown, shrunk or new) plus the scripts that read the table, plus the normal selection for the rest of the diff; a change reaching `features.py` re-derives `features.py` and `dst_checks.py` only; and the NOT RUN block lists only what did not run, with run_always scripts printed as "ran anyway".

- **closures.json** (`tests/closure.py` `select`, `base_closures`): an entry is compared with the merge base's committed table. An unchanged entry makes the skip claim main already makes for this diff; a shrunken entry is a changed entry, so the only way to hide a dependency runs the script. With no merge base it is still a gate file and runs FULL. The `closures` job keeps re-deriving in full on a closures.json change (`affected` is unchanged there). Main's push stays FULL and unscoped.
- **The table is now a measured dependency.** `_rel` excluded both `tests/closure.py` and `tests/closures.json` from every recording, which was harmless while the table forced FULL. `tests/entities.py` pins `select` and `affected` against the committed table, so its answer depends on it; `_rel` now excludes only `closure.py`, and `entities.py` was re-recorded `--single` under strace and lists the table. `deployment_shape.py` (imports closure) was re-recorded too and does not read it.
- **dst_checks** (`affected`, `check --partial`, `derive_closures.sh --single`): the `DRIVEN_BY_OTHERS` full-forcing rule in `affected` is replaced by a scoped re-derive of the driver plus the child. The map itself stays: it is what makes `dst_checks.py` unselectable and folds it into `features.py`. `--single tests/dst_checks.py` now sets `HASTUB_TZ=Europe/Stockholm`, as its lane does, and `check --partial` folds the child's recording into its driver's comparison, as `merge --partial` already did.
- **NOT RUN block** (`tests/run.sh`, `closure.py not-run`): reads the lane manifests, not only the plan. A planned skip is printed as run only on a manifest line that ran the script and none that skipped it, so `env_drift.py`'s run_always `--claims-only` line never stands in for its skipped capture.
- `tests/entities.py`: four new pins and one rewritten. The `_af5` restore pin used a driven child recorded alone as its route to a successful merge with a still-failing check; that route is now a repair, pinned as such, and the restore is driven by a check that fails on its second call.
- `docs/delivery/1812.md`: the #1812 row the coordinator's brief gives verbatim. `docs/delivery/1815.md`: this pull request's own row. `tests/README.md`: the closures.json paragraph.

## Head

74988886082e337428c6df7c346d0ce550bd3303

## Mutation proof

Each mutant is one in-memory edit to `tests/closure.py` in a worktree at e4eda221 (this head less `docs/delivery/1815.md`), then `PYTHONPATH=tests/hastub python tests/entities.py` (driver `mut.py`, sha1 in Figures). Head and M0 (a comment edit, the null mutant) print `ALL 2013 ENTITY CHECKS PASSED`. Every other mutant prints `1 of 2013 ENTITY CHECKS FAILED`:

- M1, closures.json back to a gate file whenever a base exists (`if is_gate_file(f):`): FAIL `a closures.json change runs the scripts whose entry moved, either way` (the grown case runs all 28).
- M2, moved entries no longer selected (`if hits:`): FAIL the same check (`grew=['tests/entities.py'] shrank=['tests/entities.py']`).
- M3, the driven child dropped from the re-derive (`rederive = suite_order(why)`): FAIL `a change to a subprocess-driven script re-derives its driver and itself` (`rederive=['tests/features.py']`).
- M4, the child fold in `check --partial` off (`if False:`): FAIL `a driven child's recording repairs its driver's closure (R9-F10.9)` (`status=skip-still-fails`).
- M5, the manifest's skip no longer outranks a run line (`if any(`): FAIL `the NOT RUN block lists what did not run, and only that (R9-F10.9)` (`env_drift.py` read as ran anyway).
- M6, the table excluded from recordings again: FAIL `the recorder measures the table as a dependency, never the instrument`.

No production `.py` file changes, so `tests/mutation_table.py` has no site to pin and `--pin-killed` has nothing to do.

## Null control

- **NOT RUN block.** The same docs-only diff (one blank line on `DISCLAIMER.md`, INERT) gated with `GATE_SCOPE=auto GATE_SCOPE_BASE=HEAD GOLDEN_MODE=drift GOLDEN_REF=HEAD ./tests/run.sh`. At main dc6c97e4 it runs 4 scripts (harness_headers.py 151 s, layout.py 4 s) and prints both as `did NOT run`, then `4 TEST SCRIPT(S) PASSED; 28 SCOPED OUT AND NOT RUN`. At head it runs the same 4 and prints `26 SCOPED OUT AND NOT RUN`, with harness_headers.py and layout.py on `ran anyway` lines.
- **closures.json selection.** With the merge base's table identical to head's, a closures.json-only diff runs exactly the table's readers (today `tests/entities.py`), pinned in entities.py. With no base it runs FULL, as before.
- **strace proof.** At main dc6c97e4 (F10.3's strace union merged), `./tests/derive_closures.sh --single tests/features.py --record-only` records 121 files; the lane recording `HASTUB_TZ=Europe/Stockholm python tests/closure.py record tests/dst_checks.py` records 104 real, non-INERT files, and 0 of them are missing from the features.py recording. Null control: the audit-hook-only recording of features.py (`closure.py --exec-record`, no strace) misses 4 of the 104 (`custom_components/heatpump_optimizer/binary_sensor.py`, `tests/hastub/homeassistant/components/binary_sensor.py`, `tests/replay.py`, `tests/replay/synthetic-dhw-only.json`), so the comparison can fail. 0 of the 104 are missing from main's committed features.py closure either.

## Figures

Evidence directory (cloud): `/mnt/project-files/audit-r9/fix/evidence/F10.9/`. Python 3.13 venv with `tests/requirements-ci.txt`, `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`, Linux with strace.

- strace proof: recordings `strace_features_dc6c97e4.json` (sha1 cc89057b), `lane_dst_checks_dc6c97e4.json` (6bd10fbd), `hookonly_features_dc6c97e4.json` (2a9a5b48); the subset is `set(real(B)) - set(A)`, with `real` = `closure._is_real_file` and not `closure.is_inert`.
- Replay of the audit's closures.json cases, the PR's own selection against this branch's `select` at the PR's merge (`replay_select.sh`, sha1 987577cc, output `replay_select.out`): #1803 f720ee90 FULL 28 to SCOPED 5 (1 entry moved); #1800 fc16a761 FULL 28 to SCOPED 20 (1 moved); #1799 65814159 FULL 28 to SCOPED 22 (16 moved). Each line also lists the scripts the old selection ran and the new one skips. These tables predate entities.py listing the table, so entities.py is selected there only through its own closure.
- NOT RUN: `notrun_main_docsonly.log` and `notrun_head_docsonly.log` (the command under Null control).
- Mutants: the driver mut.py (sha1 3ed2d8af) and each run's last lines, entities_<M>.tail.txt, in the evidence directory's mutants folder.
- Re-record: `./tests/derive_closures.sh --single tests/entities.py` then `--single tests/deployment_shape.py` (strace present): entities.py rc 0, 194 files, lists `tests/closures.json`; deployment_shape.py rc 0, does not.
- At the code head: `python tests/closure.py selftest` `ALL 23 closure shrink pins PASSED`; `python tests/structure.py` `STRUCTURE RATCHET PASSED`; `python tests/closure.py no-copies` rc 0; `node .claude/workflows/brief_lint.mjs` rc 0; `node .claude/workflows/policy_lint.mjs` rc 0; `node .claude/workflows/rules_sync.mjs --check` rc 0; `tests/entities.py` `ALL 2013 ENTITY CHECKS PASSED`.
- Scope: this diff touches gate files (`tests/closure.py`, `tests/run.sh`, `tests/derive_closures.sh`), so `select` prints `MODE: FULL` and CI runs the whole suite; the scripts that can move here (entities.py, the closure selftest, run.sh's NOT RUN path) were run locally as above, and the rest is left to CI's FULL run.
- Not run here: `mypy --strict` (no production module changed); Python 3.14.2 typing and real-HA `ha_contract` (no production module changed; neither box has the pins); `tests/stress.py` and the full suite (CI's FULL gate).

## Red checks

none

## Forward-carry

none. One note for R9-F10.9b goes to its roster brief through the coordinator, not this tree: with `tests/closures.json` in `entities.py`'s closure, every `ci: re-record closures` autofix commit now selects `entities.py` (about four minutes) on its re-check, and nothing else unless an entry moved.

## Friction

none

## Approval

tvofi's approving review is owed: this changes code-owned gate files and `tests/README.md`.
