# Verifier 3 of 3 — panel D10-0, audit round 4

- **Worktree**: `../audit-r4-verify-D10-3`, detached at `0855277` (branch head
  `claude/13-dimension-audit-920935`). The finder measured the baseline
  `7dd68dd`; the head adds `tests/entities.py` (rewritten), `tests/run.sh`,
  `tests/closure.py`, `docs/` plan/register files, `manifest.json` and the card
  bundle — **none of `quality_scale.yaml`, `__init__.py`, `coordinator.py`,
  `config_flow.py`, `README.md` or the six user docs changed**, and every
  number below came out identical to the finder's. No number moved.
- **Interpreter**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  `PYTHONPATH=tests/hastub` from the worktree root. Nothing installed; the
  finder's two scratch venvs under `/private/tmp/hpo-d10-mypy*` were reused
  for the mypy arms only.
- **Box**: 8-core Apple M1. `load1` during my runs ranged **2.47 – 8.34**
  (another verifier was running the identical coverage instrument in a
  neighbouring worktree for part of it). Every number in this report is a
  count, a percentage or a revealed type — `thread_factor=n/a` for all of
  them; no timing evidence is relied on anywhere.
- My own harnesses: `tools/audit/round4/D10/verify3/probe_alias_v3.sh` (D10-03
  consequence probe) and `tools/audit/round4/D10/verify3/cov_config_flow_v3.sh`
  (D10-01 five-script coverage arm), both uncommitted in this worktree.

## Re-runs of the finder's harnesses

| harness | my result | finder's |
|---|---|---|
| `qs_rules.py` (no toolchain JSONs) | mismatch=1 (docs-known-limitations), 2 rows unmeasured | — |
| `qs_rules.py` + coverage.json + census.json | `declared_mismatch=3`, same three rows and directions | 3 |
| `coverage_measure.sh fast` then `e2e` | package **97.18 %** (14948/15381), **56** modules, **0** below 95 %, lowest `battery.py` 95.0; `config_flow.py` **97.2 %, 756 stmts, 21 missed** | identical |
| `mypy_arms.sh` | arm B (real stubs) **0** errors; arm A 542/470/72, same by-code table; probe root=`Any`, coordinator=`…HeatPumpOptimizerCoordinator` | identical |
| `log_when_unavailable.py` | 1 ERROR + 9 DEBUG over 10 failed polls, 1 INFO recovery, latch resets | identical |

Exit-code differences from the finder's export run, all benign and none
figure-affecting: in this worktree (`git` present, `round3/` present)
`entities.py`, `deployment_shape.py` and `harness_headers.py` exit **0**
(finder's export: 1); `golden.py` exits 1 in both, in strict mode against
other-machine fixtures, exactly as the instrument's header documents.

One discrepancy inside the finder's own material, recorded because a later
reader will hit it: `qs_rules.py`'s header EXPECTED block says
`declared_mismatch=2 … -- docs-known-limitations, runtime-data`, which matches
neither the committed `qs_rules.out.txt` (3) nor the report (3) nor the
unmeasured run (1); `runtime-data` is done/done and is deliberately excluded
(the code says so at the `runtime-data` rule). Stale header line in the
harness, not a defect in the number.

## D10-01 — register drift, 3 of 54 rows contradicted when executed — **verify**

**My number**: `declared_mismatch=3` of 54 (config-flow-test-coverage
executed todo / declared done; test-coverage executed done / declared todo;
docs-known-limitations executed todo / declared done).

**My own metric and collection** (independent of the finder's): the decisive
row is `config-flow-test-coverage`, whose register comment itself names the
script set it claims — *"over config_flow_steps, entities, golden, features
and deployment_shape"*. `verify3/cov_config_flow_v3.sh` is my own runner (own
coveragerc, own sitecustomize, own private `HPO_PLANDATA` and data dir) over
exactly those five scripts:

```
RESULT cf_cov_five_scripts=97.2% stmts=756 missed=21
RESULT cf_missing_lines_five=[451, 1110, 1115, 1223, 1671, 1711, 1712, 1728,
  1729, 1731, 1732, 1733, 1734, 2546, 2549, 2550, 2556, 2640, 2641, 2642, 2919]
```

The 21 lines are the finder's 21 lines. So even under the register's **own**
script set, all three quoted figures are contradicted: 100 % → 97.2 %,
661 statements → 756, 0 missed → 21. The five-script union equals the
20-script figure, which also independently confirms the finder's "the failing
script cannot confound it" control: the other 15 gate scripts add **zero**
config_flow.py coverage.

**Attacks, in the contract's order**

1. *Wrong gate mode* — no. I fetched both rule pages today:
   config-flow-test-coverage demands "100 % test coverage for the config
   flow" including reconfigure/reauth/options flows, so `pct >= 100.0` is the
   right gate; test-coverage demands "Above 95 % test coverage for **all**
   integration modules", so the per-module row (0 of 56 below) is the
   deciding aggregate, not the package percent. Both gates match the rule
   text.
2. *Aggregate artefact* — no grid to drop cells from; each of the three rows
   rests on its own number. Sensitivity noted: `test-coverage`'s executed
   `done` has zero headroom (`battery.py` at exactly 95.0); were it 94.9 the
   row would agree with the declaration and the count would be 2. The
   measured value stands and the tree's own `tests/coverage_budgets.json`
   (recorded 2026-09-11) independently records 97.2 % and
   `modules_below_bar=0` — the ratchet agrees with the execution and only the
   register was left behind.
3. *Null control / perturbation* — executed, both directions: correcting the
   `test-coverage` row in `quality_scale.yaml` moves `declared_mismatch`
   3 → 2; flipping an agreeing row (`parallel-updates: done → todo`) moves it
   3 → 4. File restored afterwards (`git status` clean).
4. *Reachability* — the register is a shipped artefact a user can read, and
   the mechanism claim ("no check executes against this file") is corroborated
   by the tree itself: `tests/closure.py:234` classifies it as read by no gate
   script, and `tests/entities.py` (~:9239) asserts byte-identical golden and
   env_drift captures across an edit of it.
5. *Severity earned* — yes: three stale rows (two of them self-invalidating
   coverage figures) in a non-enforced register; no user meets anything.
   `low` is right, and the finder's two extra stale-comment rows
   (`docs-examples` "0 automation examples" vs 3 ```yaml blocks in
   `docs/automations.md`; `log-when-unavailable` "one ERROR per failed poll"
   vs the measured 1+9 latch) both reproduce, status still correct.

One nuance for the judge: not all three rows "drifted" the same way. The two
coverage rows rotted (the file grew under true figures). `docs-known-limitations`
was **born wrong**: `git log -S "Known limitations"` over `README.md`/`docs/`
returns only the register-adding commit `998d354` — the heading never existed
in any user doc. Same number, sharper cause.

**Vote**: verify. Value 3 of 54. Severity low (hygiene).

## D10-02 — `docs-known-limitations` declared done, 0 headings across 4075 lines — **verify**

**My number**: **0** headings matching `^#{1,6}.*known limitation`
(case-insensitive) — and I widened the finder's scope to **all** repository
markdown, not just README + the six user docs: still 0. The word "limitation"
occurs in no user doc at all; repo-wide it appears only in the audit register,
one `battery.py` code comment, and the register row itself. Line count
confirmed: 878 + 3197 = 4075.

**Attacks**

1. *Wrong gate mode* — n/a (a grep count); the rule text is fetched, not
   recalled: the page requires a `## Known limitations` section and says
   "There are no exceptions to this rule."
2. *Aggregate artefact* — no; one regex over named files.
3. *Null control / perturbation* — executed: appending `## Known limitations`
   to a temp copy of README moves my count 0 → 1.
4. *Reachability* — could the section live somewhere the finder missed? My
   all-markdown grep answers no. The counter-evidence is real and I confirmed
   it: README:176's "Boundaries worth knowing before you pick a path" list,
   caveats at README:534 and how-it-works.md:1032 — limitation content
   without the section, exactly the finder's "placement, not knowledge"
   framing, which is what makes `low` earned rather than inflated.
5. *Severity* — documentation discoverability only; no capability changes.

**Vote**: verify. Value 0. Severity low (hygiene).

## D10-03 — bare `ConfigEntry` re-bind at the package root; `runtime_data` is `Any` in the three entry points while strict reports 0 — **verify**

**My numbers**: `mypy_arms.sh` re-run over **my** tree: arm B (real
homeassistant-stubs 2025.4.4, py3.13.1, mypy 2.3.1 `--strict
--warn-unused-ignores`) = **0** errors; probe reveals `Any` through
`__init__.py`'s alias and `…coordinator.HeatPumpOptimizerCoordinator` through
`coordinator.py`'s. Both alias definitions confirmed in my tree
(`__init__.py:43` bare, used at :249/:344/:372 — `async_setup_entry`,
`async_update_options`, `async_unload_entry`, the functions HA calls;
`coordinator.py:10451` parametrized).

**My own consequence probe** (`verify3/probe_alias_v3.sh`, independent of the
finder's reveal_type echo): the same bogus call
`entry.runtime_data.no_such_attribute_anywhere()` made through each alias —
``0`` mypy errors through the root alias, ``1`` `[attr-defined]`` error
through the coordinator alias. That is the lost checking demonstrated, not
just labelled: the "0 errors" census is true *because* three functions'
attribute access is `Any`.

**Attacks**

1. *Wrong gate mode* — n/a.
2. *Aggregate artefact* — no; a per-alias probe plus a per-alias error count.
   The coordinator alias is the null control: same stub, same run, concrete
   type.
3. *Reachability* — the defect is static-only, and the finding says so
   ("nothing is wrong at runtime today"); `get_type_hints` on
   `async_setup_entry` resolves cleanly in the current tree. The in-tree
   comment's defense is real and I reproduced both halves of the finder's
   perturbation transcript in a copied tree (`/private/tmp/hpo-d10-v3perturb`):
   naive parametrization keeps `mypy --strict` at **0** errors over the whole
   package (with `TYPE_CHECKING` imported — the finder's snippet omitted the
   import; with it the count is 0), and `get_type_hints` then raises
   `NameError: name 'HeatPumpOptimizerCoordinator' is not defined`. So the fix
   is genuinely not a one-liner; a compliant shape exists (runtime binding or
   annotation-only alias) and the rule wording — fetched — is "the use of a
   custom typed `MyIntegrationConfigEntry` is required and must be used
   throughout".
4. *Severity* — earned: three functions escape strict checking and the
   Platinum 0 becomes partly vacuous; no runtime behaviour changes. `low`.

**Vote**: verify. Value `Any` (root) vs `HeatPumpOptimizerCoordinator`
(coordinator alias); 0 vs 1 errors on the consequence probe. Severity low
(hygiene).

## Nothing left unresolved

No timing evidence was used by finder or by me; every refute avenue closed on
executed counts. All three findings verify at `low`.
