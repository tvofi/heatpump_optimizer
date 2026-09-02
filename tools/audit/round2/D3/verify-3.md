# D3 verifier seat 3 of 3 — the fix and the sampler

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`. Worktree
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-D3`, left at
the baseline with `git status` showing only `tools/audit/`. Working copy of the
tree under `/tmp/verify-D3-3/`. Interpreter
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python`,
`PYTHONPATH=tests/hastub`, all five BLAS thread variables pinned to `1`, run
from the tree root. No full gate run, no `/tmp/hpo-gate.lock` taken.

Everything below is a count or a ratio of counts (assertion outcomes, kills,
sites, module counts) except the SENSITIVE-projection gaps, which are solver
outputs from a deterministic optimizer — none of it is a timing number, so
none of it is contention-sensitive. `load1` at each measurement is recorded
anyway.

Artefacts written (all under `tools/audit/round2/D3/`):

| File | What it is |
|---|---|
| `verify3-assertions.patch` | the seven assertions, as a patch that `git apply --check`s clean against the baseline |
| `verify3_sensitive_projection.py` | my harness for D3-10's proposed remedy |
| `verify3_sampler_audit.py` | my harness for the sampler's representativeness |
| `verify3_projection_clean.json` | its output on the unmutated baseline |

---

## Part 1 — the seven assertions

Method, identical for all seven. Copy the baseline tree to `/tmp/verify-D3-3/tree`,
write the assertion the finding says is missing into the real test script, and
run that script twice: once with the production files restored from a pristine
copy, once with the mutant patch applied by `patch -p1`. An assertion counts as
proven only if it prints `FAIL` (or the script exits non-zero) with the mutant
and the script exits 0 without it. Driver: `/tmp/verify-D3-3/run_mutant.sh`.

**Metric definition (mine, for all of Part 1):** the number of `R.check`/`check`
assertions in the edited script that report FAIL, and the script's exit code,
with the mutant applied versus with the production file restored.

Baselines before any edit: `features.py` 1557 checks / 1576 `ok` lines rc=0,
`entities.py` 538 rc=0, `open_meteo.py` rc=0. After the edits:
`features.py` 1566 rc=0 (+9), `entities.py` 541 rc=0 (+3), `open_meteo.py`
rc=0 (+1). Nothing else in those scripts moved.

Every killing mutation is a one-line (or one-block) edit in a **production**
file, never in a test file, so none of these assertions measures itself:

| Finding | Mutant | Production file and line |
|---|---|---|
| D3-01 | M31 | `custom_components/heatpump_optimizer/sensor.py:1086` |
| D3-02 | M19 | `custom_components/heatpump_optimizer/dhw_schedule.py:433` |
| D3-03 | M13 | `custom_components/heatpump_optimizer/coordinator.py:1676` |
| D3-04 | M32 | `custom_components/heatpump_optimizer/grid_fee.py:141` |
| D3-05 | M21 | `custom_components/heatpump_optimizer/accuracy.py:382` |
| D3-06 | M30 | `custom_components/heatpump_optimizer/open_meteo.py:194` |
| D3-07 | M15 | `custom_components/heatpump_optimizer/inputs.py:352` |

Each assertion imports and calls the production symbol named in the finding
(`sensor.PredictiveInsightSensor` through the real `async_setup_entry`;
`dhw_schedule.hours_until_next_window`; `Coord._dhw_setpoint_sweep`;
`grid_fee.is_valid_spec` / `grid_fee.parse_rules`;
`AccuracyTracker.from_dict`; `open_meteo._parse_block`;
`InputReader.read`). None re-derives a production formula: the three that
could have (D3-03's ranking, D3-02's countdown, D3-07's age) compare two
production runs or an exact production output instead.

RESULTS TABLE PLACEHOLDER

---
