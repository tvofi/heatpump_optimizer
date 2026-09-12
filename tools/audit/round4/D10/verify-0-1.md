# D10 verify — seat 1 of 3 (round 4)

- **Worktree**: `/Users/timmalmstrom/.zcode/workspace/default/audit-r4-verify-D10-1`, detached at **0855277** (branch head). Baseline was **7dd68dd**.
- **Tree movement**: none in the measured surface. `git diff --stat 7dd68dd..0855277` over `custom_components/heatpump_optimizer/`, `README.md`, the six user docs, `tests/coverage_budgets.json` and the coverage instrument is empty; the 25 commits are audit bookkeeping. Every baseline number below therefore stands unchanged at the head (and all of them reproduced exactly).
- **Box / contention**: 8-core Apple M1. `load1` during my session ran 2.85–8.60 (other agents active). Every number here is a count, a ratio, a percentage or a type name — no timing or memory RESULT is gated, so nothing below is contention-sensitive; no refute rests on a timing mismatch.
- **Toolchain**: python3 = 3.11.5 (`/Library/Frameworks/.../3.11/bin/python3`), coverage 7.16.0, PyYAML present. `mypy` is **not** on the system interpreter, but the finder's two scratch venvs (`/private/tmp/hpo-d10-mypy{,13}/venv`, mypy 2.3.1 in both, arm B = homeassistant-stubs 2025.4.4 on Python 3.13.1) still exist, so `mypy_arms.sh` was re-runnable as its header requires. Nothing was installed.

## Re-runs of the finder's harnesses (per their headers)

| harness | command | my output vs baseline |
|---|---|---|
| `qs_rules.py` (plain, no env) | `PYTHONPATH=tests/hastub python3 tools/audit/round4/D10/qs_rules.py` | `rules_total=54`, `declared_mismatch=1` (only `docs-known-limitations`; the two coverage rules are `unmeasured` without the JSONs and excluded by the code). **The header's EXPECTED block is stale**: it says `declared_mismatch=2 -- docs-known-limitations, runtime-data`; `runtime-data` is done/done in every run and never a mismatch. Minor harness-doc defect, reported below; does not touch the finding. |
| `qs_rules.py` (full) | as above plus `D10_COVERAGE_JSON=<my fast+e2e coverage.json> D10_MYPY_JSON=<my re-run census.json>` | **Byte-identical to the committed `qs_rules.out.txt`** (diff empty after dropping the `load1` line): `declared_mismatch=3`, the same three rows, tier counts 19/1 · 10 · 15/4/2 · 3. |
| `coverage_measure.sh` | `D10_WORK=$(mktemp -d /private/tmp/hpo-v-D10-ownXXXX) tools/audit/round4/D10/coverage_measure.sh fast` then `e2e` | fast: package 97.17 % (14945/15381), `config_flow.py` 97.2 %, **756 stmts, 21 missed**; fast+e2e: package **97.18 % (14948/15381)**, 0 of 56 modules below 95 %, lowest `battery.py` 95.0 — all exactly the finder's numbers. My worktree has `.git`, so `entities.py` and `deployment_shape.py` exit 0 here (exit 1 in the finder's export); no figure moved. `golden.py` exit 1 in `GOLDEN_MODE=strict`, as the instrument documents. |
| `mypy_arms.sh` | `tools/audit/round4/D10/mypy_arms.sh` | `real_stub_errors=0`, `hastub_total=542 / in_pkg 470 / in_stub 72`, identical by-code table; `runtime_data_revealed_root=Any`, `..._coordinator=…HeatPumpOptimizerCoordinator`. The re-written `census.json` is **byte-identical** to the one the finder left in the scratch dir. |
| `log_when_unavailable.py` | `PYTHONPATH=tests/hastub python3 tools/audit/round4/D10/log_when_unavailable.py` | 10 failures → **1 ERROR + 9 DEBUG**; recovery → **1 INFO**; next 10 failures → **1 ERROR** again (latch resets). VERDICT done. Matches. |

## Own harnesses (this seat)

Beside the finder's, uncommitted: `d10_own_D10-01.sh` + `d10_own_D10-01.py`, `d10_own_D10-02.py`, `d10_own_D10-03.py`. Outputs:

```
# d10_own_D10-01.py --executed <my re-run table> --own5 <own 5-script coverage> --full <my fast+e2e> --perturb
RESULT own_declared_rows=54 rows
RESULT own_declared_mismatch_vs_rerun=3 rows: [config-flow-test-coverage, docs-known-limitations, test-coverage]
RESULT own_config_flow_test_coverage=own:todo/declared:done [CONTRADICTED]
    -- own five-script run (the row's claimed basis): 97.2%, 756 stmts, 21 missed
RESULT own_test_coverage=own:done/declared:todo [CONTRADICTED]
    -- own full-gate re-run: 97.18% package (14948/15381), 0 of 56 modules below 95%
RESULT own_docs_known_limitations=own:todo/declared:done [CONTRADICTED] -- own regex: 0 headings
RESULT own_contradicted=3 rows
RESULT own_perturb_fix_one=2 rows   (was 3; direction down, as declared)
RESULT own_perturb_flip_one=4 rows  (was 3; direction up, as declared)

# d10_own_D10-02.py  (README.md + ALL of docs/*.md — 15 files, broader than the finder's six)
RESULT six_set_headings_known_limitation=0 headings        (finder's file set)
RESULT six_set_word_limitation=0 occurrences
RESULT full_set_headings_known_limitation=0 headings       (my broader set: the attack)
RESULT full_set_word_limitation=4 occurrences              (all in docs/audit-2026-09.md, the audit register)
RESULT full_set_files=15 markdown files, 12705 lines

# d10_own_D10-03.py
RESULT root_alias_bindings=1: ['ConfigEntry']                     (bare)
RESULT coordinator_alias_bindings=1: ['ConfigEntry[HeatPumpOptimizerCoordinator]']
RESULT entry_points_found=3 of 3                                 (async_setup_entry / async_update_options / async_unload_entry)
RESULT entry_points_annotated_with_root_alias=3 of 3
RESULT runtime_data_uses_in_entry_points=2 direct attr accesses (+1 via getattr in async_update_options)
RESULT stub_configentry_decl=class ConfigEntry[_DataT = Any]:     (read out of homeassistant-stubs 2025.4.4)
RESULT stub_runtime_data_decl=runtime_data: _DataT
RESULT probe_root_runtime_data=Any
RESULT probe_root_effective_config=Any
```

The `d10_own_D10-01.sh` five-script coverage run is the seat's sharpest own instrument for D10-01: the register row's own comment names its basis — *"100% statement coverage (661 statements, 0 missed) over config_flow_steps, entities, golden, features and deployment_shape"* — so I ran coverage over exactly those five scripts with my own coveragerc/combine. Result: **97.2 %, 756 statements, 21 missed**. The row is falsified on its own claimed basis, not only under the finder's 20-script superset (under which, by monotonicity of coverage, missed under the subset is ≥ missed under the superset — both are 21; no gate script touches those statements at all).

## Attacks run, and their outcomes

1. **Contention** — no timing RESULT gates anything; `load1` 2.85–8.60 quoted, ignored by design.
2. **Wrong script set / gate mode (D10-01's coverage half)** — attacked two ways: (a) my independent five-script run reproduces the same `config_flow.py` figure as the 20-script instrument, so the 21 missed is not a script-selection artefact; (b) the instrument's known silent drop (`closure.py selftest`) is measured harmless in its own header. The e2e stage moves the package figure by +0.01 pp (14945→14948), confirming the finder's own statement.
3. **Aggregate artefact** — n/a (row counts, not grids).
4. **Null control / perturbation** — D10-01: both directions executed on temp copies of the yaml (fix one row 3→2; flip agreeing `parallel-updates` 3→4). D10-03: the parametrized coordinator alias is the same-run control — same probe, same mypy invocation reveals the concrete class there and `Any` at the root.
5. **Scoping attack (D10-02)** — could a "Known limitations" section hide where the finder did not grep? My harness scans **all 15** markdown files under `README.md` + `docs/` (the finder's six plus HANDOVER, backlog, both audit registers and the four plan files): **0** "known limitation" headings anywhere; the 4 word-hits are the audit register describing this very finding. No synonym heading exists in user docs either.
6. **Rule-text attack (D10-02, D10-03)** — fetched both rule pages live. `docs-known-limitations`: "There are no exceptions to this rule." — confirmed. `strict-typing`: the actual sentence is *"If the integration implements `runtime-data`, the use of a custom typed `MyIntegrationConfigEntry` is required and must be used throughout."* The finder paraphrased the condition as "implements strict-typing"; the real condition is implementing `runtime-data`, which this integration does (1 write, 11 reads) — the requirement applies a fortiori. Conclusion unchanged; the paraphrase is worth a note, not a weaken.
7. **Reachability / real HA (D10-03)** — the bare binding is *deliberate*: the comment above `__init__.py:43` documents that binding through the lazy-import helper broke `get_type_hints` on the event loop (real HA 2026 behaviour) and inflated the measured closure. The finding already prices this in ("the fix is not a one-liner"); severity `low` ("nothing is wrong at runtime today") is honest. Corroborated, not refuted.
8. **Stale-artefact attack (D10-01)** — is the row maybe true and the harness wrong? No: the tree's own committed instrument `tools/audit/w5-g5-195-coverage/coverage/coverage_report.txt` records `config_flow.py 672 / 5 missed / 99.3 %` — the register's own cited control point — and the file has since grown to 756 statements. The row was true once and rotted; the mechanism (nothing machine-enforces the file, per its own header) is real.
9. **Numbers moved from baseline?** None. Production surface identical between 7dd68dd and 0855277; every re-run reproduced the baseline figure exactly (the mypy census byte-identical, the full qs_rules table byte-identical modulo `load1`).

## Instrument defects noticed while verifying (for the record, none finding-blocking)

- `qs_rules.py` header EXPECTED block is stale (`declared_mismatch=2 -- docs-known-limitations, runtime-data`): the plain run yields 1, the full run 3, and `runtime-data` is never a mismatch. The committed `qs_rules.out.txt` and the FINDER report both say 3, so only the docstring rotted.
- `d10_own_D10-01.py`'s five-script `golden.py` arm exits 1 under `GOLDEN_MODE=strict` on this box (fixtures recorded on another BLAS build, as `tools/audit/README.md` documents); coverage is still recorded, and my number matches the 20-script instrument's, so the arm is sound.

## Votes

| id | vote | my number | metric definition (one line) |
|---|---|---|---|
| D10-01 | **verify** (low) | 3 of 54 contradicted; perturb 3→2 / 3→4 | rows of `quality_scale.yaml` whose declared status differs from an executed verdict, where the three suspect rows were re-derived by this seat's own commands (five-script coverage run, full-gate re-run, own regex) |
| D10-02 | **verify** (low) | 0 headings over 15 files / 12705 lines | count of ATX headings matching /known limitation/i over README.md + every docs/*.md |
| D10-03 | **verify** (low) | root alias bare (`ConfigEntry`), used by 3/3 entry points, probe reveals `Any`/`Any`; stub declares `_DataT = Any` | the type `mypy --strict` reveals for `entry.runtime_data` (and `.effective_config`) under the alias exported from the package root, at the three HA entry-point signatures |

All three severities `low` are earned: a rotted hand-maintained register, a missing user-docs section (content exists in prose, discoverability lost), and a deliberate-but-lossy typing binding that costs checking of three functions while runtime behaviour is correct. None is met by a user.
