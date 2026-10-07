# D10 — verifier seat 1 of 3

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`, standalone export (no
`.git`), 8-core Apple M1, python3 3.11.5, numpy 2.4.6 / scipy 1.17.1 (the
`tests/requirements-ci.txt` pins), mypy 2.3.1 installed into a throwaway venv
outside the tree. `load1` is recorded per measurement below; every metric here
is a count over source or over a pass/fail set, so `thread_factor=1.0` and none
of them is contention-sensitive. Instruments under
`tools/audit/round3/D10/verify-1/`.

**Votes:** D10-01 `weaken` (low), D10-02 `verify` (low), D10-03 `weaken` (low),
D10-04 `weaken` (medium → low).

## Environment caveats that apply to every arm

The export is not a git repository and has no `RELEASE_NOTES.md`. Three checks
fail on that alone, identically in every arm: two handover checks in
`tests/entities.py` (`updated-for:` cannot be resolved without history) and one
`recorded_at = 'unknown'` in `tests/features.py`. `tests/dst_checks.py` needs
`HASTUB_TZ=Europe/Stockholm`, which `tests/run.sh:278` sets and a bare
invocation does not. A placeholder `RELEASE_NOTES.md` was present for every arm
below and removed afterwards.

Because of that, **the metric for every mutation probe is the FAIL-LINE SET,
not the exit status**: a difference between two arms is evidence; an absolute
red is not. `tools/audit/round3/D10/verify-1/run_arm.sh` runs the eight gate
scripts that construct the coordinator or read the stub and diffs their FAIL
lines. One line, `a8:register_once`, names three of a set in nondeterministic
order and is excluded from every set comparison; its count never changed.

---

## D10-04 — the coordinator is built without `config_entry`

### The finder's harness, re-run

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/coordinator_entry_rule.py`
— `super_init_calls=1`, `calls_passing_config_entry=0`,
`coordinator_config_entry_is_set=0`, `stub_names_config_entry=0`,
`stub_signature=(self,*args,**kwargs)`,
`kwargs_actually_passed=['name','update_interval']`. Exact reproduction.
`load1=8.11`, `thread_factor=1.0`.

### The omission is real and reachable

`custom_components/heatpump_optimizer/coordinator.py:1306` passes `hass`,
`_LOGGER`, `name=DOMAIN`, `update_interval=…` and nothing else. **Arm B**
replaced the stub's `__init__` with one where `config_entry` is a *required*
keyword-only parameter: five of the eight scripts — `entities.py`,
`features.py`, `config_flow_steps.py`, `manual_plan.py`, `dst_checks.py` —
die with `TypeError: DataUpdateCoordinator.__init__() missing 1 required
keyword-only argument: 'config_entry'`, every traceback ending at
`coordinator.py:1306`. The call site is on the live path.

### The stated cause is refuted: the permissive signature is not what hides it

The finding's causal claim is that `(self, *args, **kwargs)` "names no
parameter, so no gate test can distinguish that call". **Arm A2** is the honest
tightening: the stub's `__init__` given Home Assistant's *own* parameter list,
transcribed from `homeassistant/helpers/update_coordinator.py` fetched at tags
`2025.2.0` (the `hacs.json` floor) and `2026.9.0` — `config_entry` named,
keyword-only, defaulting to a sentinel that falls back to a `current_entry`
ContextVar, exactly `uc-2025.2.0.py:86-91` and `uc-2026.9.0.py:95-110`.

| arm | stub `__init__` | rc pattern | FAIL lines |
|---|---|---|---|
| arm0 | `(self, *args, **kwargs)` as shipped | 6 green / entities+features red | **34** |
| armA2 | upstream's own named, keyword-only `config_entry` | identical | **34** |
| armB | `config_entry` required (stricter than upstream) | 5 scripts `TypeError` | — |

`diff` of the arm0 and armA2 FAIL sets is empty. **Naming the parameter changes
nothing.** What hides the omission is not the stub's signature; it is that
upstream *permits* the omission and fills the attribute from a ContextVar the
stub has no counterpart for, and that no test asserts
`coordinator.config_entry is entry`. Arm B does turn the suite red, but only by
making the stub stricter than the class it stands in for — the very defect
`tests/ha_contract.py` exists to record.

### The gate-blindness half is verified

**Arm M** applied the finding's own perturbation to production —
`config_entry=entry` added at `coordinator.py:1306` — with the stub as shipped.
The behavioural FAIL set is **identical to arm0**: not one of the 1294 entity
checks, 2136 feature checks, 203 config-flow-step checks or 27 DST checks
changes verdict. The only script that goes red is `tests/structure.py`, and only
on `FAIL coordinator_loc 9605 > 9604 (+1)` and `FAIL max_class_loc 9605 > 9604
(+1)` — a line budget that fires for *any* added line and is not a detector of
this or any other defect.

**The single-line production mutation the suite misses:**
`custom_components/heatpump_optimizer/coordinator.py:1306`, adding or removing
`config_entry=entry` in the `super().__init__` call. Zero behavioural checks
move in either direction.

Per `verifier.md` §4 the killing setup is checked for test-file self-measurement,
and it is exactly that: the only consumer of the attribute is
`coordinator.py:5733` `entry = getattr(self, "config_entry", None)` in
`_tibber_start_reauth`, and the only test that reaches its true arm is
`tests/entities.py:12724`, which writes `_ra_coord.config_entry = _ra_entry`
itself. The test supplies the precondition production never establishes under
the stub. The gap stands.

### Severity is not earned by consequence

`tools/audit/round3/D10/verify-1/real_ha_fallback_rule.py` replays the
integration's own construction call against upstream's `__init__` branch, inside
and outside the ContextVar scope real HA sets:

```
RESULT entry_resolved_inside_setup_scope=1
RESULT reauth_started_inside_setup_scope=1
RESULT entry_resolved_outside_scope=0
RESULT reauth_started_outside_scope=0
```

The coordinator is constructed at `custom_components/heatpump_optimizer/__init__.py:208`,
inside `async_setup_entry`, and `homeassistant/config_entries.py:546` at
`2025.2.0` does `current_entry.set(self)` around that whole call. So in real
Home Assistant `self.config_entry` **is** the entry, and `_tibber_start_reauth`
works. Upstream at `2026.8.0` and `2026.9.0` still carries the fallback, has
*dropped* the `breaks_in_ha_version="2026.8"` argument that `2026.2.0` had, and
reports the omission with `custom_integration_behavior=frame.ReportBehavior.IGNORE`
under the comment *"It is not planned to enforce this for custom
integrations."* A custom integration gets no error, no warning and no
deprecation at any version from the `hacs.json` floor to today.

User-visible consequence at every supported version: **zero**. The real defect
is a test-fidelity one — the reauth path's guard is only ever exercised in its
true arm through a test-assigned attribute — and that is low, not medium.

**Vote `weaken`, severity `low`.** The omission is real (0 of 1 calls), the gate
blindness is real (0 of ~3660 named checks move under the production
mutation), the stated *cause* is refuted (34/34 identical FAIL lines under
upstream's own signature), and the consequence is nil.

---

## D10-01 — the register calls three rules `todo` that the tree satisfies

### The finder's harness, re-run

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/qs_register.py` —
`rules_in_checklist=54`, `rules_checked=52`, `rules_unmeasured=2`,
`register_divergences=4`, `rules_todo_but_satisfied=3`,
`rules_done_but_unsatisfied=1`. Exact reproduction. `load1=7.35`.

### Measured my own way

Each of the three, checked without the finder's harness:

| rule | register's `todo` comment | my check | result |
|---|---|---|---|
| `reconfiguration-flow` | "tracked in issue #196" | `grep -n "async def async_step_reconfigure"` | defined at `config_flow.py:1673` |
| `exception-translations` | "13/13 raise sites untranslated, 0 exceptions sections" | regex over every `raise` of an HA exception class in the package; key resolution in all three string files | 21 raise sites, **21** carry both `translation_domain` and `translation_key`; 21 `exceptions` entries in `strings.json`, `en.json`, `sv.json`; 0 missing keys in either language |
| `log-when-unavailable` | "6 ERRORs per 5 failed polls, latch double-counts" | `log_once_rule.py` transcript | 1 ERROR + 4 DEBUG over 5 failures, INFO on recovery, latch re-arms |

All three `todo`s are stale. That half of the finding is verified.

### Attacks

**The totals line is not wrong.** The claim string asserts *"its totals line
(44 done / 4 exempt / 6 todo) is wrong in the same direction."* The file
documents its own enumerator on line 16-18 and says *"Counted from this file,
not carried."* Running it:

```
rules in file: 54
Counter({'done': 44, 'todo': 6, 'exempt': 4})
```

which is exactly what the line says. The line is an accurate count of the file
it lives in. What is wrong is the statuses it counts — which is the finding's
first sub-claim, not a second one. Presenting it as an additional defect
double-counts.

**The aggregate is a grid artefact of the same kind.** `register_divergences=4`
is 3 todo-but-satisfied plus 1 done-but-unsatisfied, and that 1 *is* D10-02.
Drop the shared cell and D10-01's own number is **3**, not 4.

**"Nothing reads the file" is not a discovery — it is a recorded decision.**
`tests/closure.py:662-695` carries a 34-line block establishing exactly this by
measurement, with a null control (`quality_scale.yaml` edited: `env_drift`
capture and `golden.capture()` over five scenarios byte-identical, sha256s
recorded) and a positive control (`thermal_model.py:2683` perturbed: both
sha256s change). The file is on `INERT` at line 210 and on `NEVER_WIDENED` at
line 695, deliberately. The finding's proposed fix — wire a register check into
`tests/` — runs against that recorded decision and needs to argue with it.

**Suite blindness, executed anyway.** Mutation M1 renamed one rule key to
nonsense and flipped two statuses in
`custom_components/heatpump_optimizer/quality_scale.yaml`; `entities.py`,
`structure.py`, `ha_contract.py` and `config_flow_steps.py` returned an
identical FAIL set. Confirmed blind, as the tree already says.

**Severity by consequence.** The file is shipped to every user's HA install and
read by nothing there; hassfest skips it for custom repositories. It costs a
user nothing. It costs the next agent, who plans finished work. `low` /
`hygiene` is right, and the finder classed it that way.

**Vote `weaken`, severity `low`.** Central claim verified by my own checks;
value corrected 4 → **3**; the totals sub-claim refuted.

---

## D10-02 — `reauth_confirm.tibber_token` has no `data_description`

### Measured my own way

`python3 tools/audit/round3/D10/verify-1/data_description_count.py`. My
counting rule differs from the finder's in two ways: it descends `sections`
sub-maps, and it runs the same count over `translations/en.json` and
`translations/sv.json` as well as `strings.json`.

```
strings_config_steps=13   strings_config_fields=70    without_description=1
strings_options_steps=23  strings_options_fields=200  without_description=0
strings_fields_total=270  strings_fields_without_description=1
strings_missing=['config.reauth_confirm.tibber_token']
en_fields_total=270   en_fields_without_description=1   (same key)
sv_fields_total=270   sv_fields_without_description=1   (same key)
```

**1 of 270**, and the same one key in all three files. Exact agreement with the
finder, under a stricter ruler.

### The rule text

Fetched `developers.home-assistant/docs/core/integration-quality-scale/rules/config-flow.md`:
the Bronze `config-flow` rule says the flow should *"use `data_description` in
the `strings.json` to give context about the input field."* Normative, so the
miss is real, and the register does call `config-flow: done` at
`quality_scale.yaml:28`.

### Attacks

**Consequence, stated properly.** The finder says the label still renders and
the missing line is the one saying where a replacement token comes from. That
understates what *is* there: the step carries its own `description` in all three
files — *"Tibber refused the configured token. Enter a valid API token to
restore price updates."* The user is told what happened and what to do. What is
missing is only the `developer.tibber.com` pointer that the `config.user` step's
`data_description` carries, for a user who has created one of these tokens
before. Real, tiny, correctly classed `low`.

**Does one field flip a Bronze rule to `todo`?** The rule has several clauses
(selectors, validation, `data_description`, data-vs-options split). The finder
flips the whole row to `todo`, which is the strictest available reading; logging
the gap and keeping the row `done` is equally defensible. This is the entire
content of D10-01's fourth divergence, so the choice moves that number too.

**Suite blindness, and the killing mutation is production.** Mutation M2 removed
`config.step.user.data_description.tibber_token` from `strings.json` only: two
new failures, and they are `en.json matches strings.json exactly` and `sv.json
matches strings.json exactly` — **translation parity, not completeness**.
Mutation M2b removed the same key from all three files at once, which is the
exact state `reauth_confirm.tibber_token` is in: the FAIL set is **identical to
arm0** and `config_flow_steps.py` stays green. The single-line production
mutation the suite misses lives in
`custom_components/heatpump_optimizer/strings.json`, and nothing in the gate
compares a step's `data` map against its `data_description` map.

**Vote `verify`, severity `low`.** Value **1 of 270**, measured independently.

---

## D10-03 — `strict-typing` unmet

### The finder's harness, re-run

mypy 2.3.1 installed fresh into `/tmp/d10v1venv`;
`MYPY=/tmp/d10v1venv/bin/mypy bash tools/audit/round3/D10/strict_typing_rule.sh`
— `mypy_error_lines_total=648`, `integration_errors=578`,
`code_no_untyped_call=174`, `code_type_arg=119`, `code_attr_defined=102`,
`code_no_untyped_def=67`, `modules_with_errors=29`, `py_typed_present=0`.
Exact reproduction. `load1=6.52`.

### Measured my own way, with my own counting rule

`python3 tools/audit/round3/D10/verify-1/untyped_defs_ast.py` — no mypy, no
stub, no toolchain.

> **Metric:** `def`/`async def` statements in
> `custom_components/heatpump_optimizer/*.py` with at least one un-annotated
> parameter (`self`/`cls` excluded on methods, `*args`/`**kwargs` **included**,
> because `--strict` requires them) **or** no return annotation.
> **Counting rule:** one per `def` statement, however many mypy lines it
> produces. `tests/` **not** included. Nested `def`s included; lambdas reported
> but not counted.

```
package_py_files=55   defs_total=1303
defs_not_strict_clean=65        (95.01% of defs are strict-clean)
defs_missing_return_annotation=23   defs_missing_a_param_annotation=55
coordinator.py 24 · optimizer.py 21 · binary_sensor.py 5 · button.py 4 · …
```

**65, not 67.** Reconciled to the line: the two sets of source locations are
**identical** (`mset - aset` and `aset - mset` both empty). The difference is
that two defs — `optimizer.py:365` and `coordinator.py:2793` — are missing a
return annotation *and* a parameter annotation, and mypy emits two
`[no-untyped-def]` lines at each. Per-error-line: 67. Per-def: 65. Same defect
set.

### Attacks

**578 is a ruler artefact.** Invocation sensitivity, same box, same mypy:

| invocation | integration errors |
|---|---|
| the finder's (hastub on MYPYPATH, `--python-version 3.11`, `--ignore-missing-imports`) | 578 |
| same, `--python-version 3.13` | 578 |
| same, **without** `--ignore-missing-imports` | 609 |
| same, **without** hastub on MYPYPATH | 562 |
| **the repository's own pinned ruler** (`tests/typing_budgets.json`: mypy 2.3.1 + real homeassistant-stubs 2026.2.3 + Python 3.13.15, no hastub) | **191** |

The headline is three times the repository's canonical figure, and the gap is
the stub: `no-untyped-call` 174 vs 7, `attr-defined` 102 vs 1, `type-arg` 119 vs
41. Those are errors about an untyped Home Assistant stand-in, not about this
integration's typing debt. The harness header does say the two are not
comparable — but `findings.json` puts `"value": 578` forward as the number, and
578 is not a property of the package.

What *is* ruler-stable is the finder's strongest point, and I confirm it from
the repository's own recorded census: `tests/typing_budgets.json`
`census.by_code["no-untyped-def"] == 67`, identical to the hastub ruler and to
my 65 locations.

**`py.typed` is refuted.** The rule page says *"we recommend fully typing your
library and making your library PEP-561 compliant. This means that you need to
add a `py.typed` file to your library."* — the **library** the integration
wraps, not the integration folder. Across the entire `home-assistant/core` tree
at `2026.9.0` (recursive tree API, `truncated: false`) there is exactly **one**
`py.typed`: `homeassistant/py.typed`, at the package root. **Zero** of the
integrations under `homeassistant/components/` carries one — `hue`, `tibber`,
`airly`, `sensibo`, `airzone` all 404. Adding
`custom_components/heatpump_optimizer/py.typed` would make this the only
integration in the ecosystem with that file and would change no type check.

**The rest is already declared and already ratcheted.** The register says
`strict-typing: todo` with issue #197 — this is a divergence the finder's own
`qs_register.py` scores as *agreeing*. `tests/typing_ruler.py` ratchets `errors`
(191) and `by_code` per code under the pinned toolchain in the `typing` CI job
(`.github/workflows/tests.yml:444,457`), with a source-only `type_ignores=0`
guard in the ordinary gate. There is no undetected state here and no new
mechanism owed, as the finder says. What remains is paid-down work.

**Vote `weaken`, severity `low`.** The rule is unmet — that verifies, at **65**
unannotated defs by my ruler, 67 error lines by the finder's, 191 total errors
by the repository's own. The headline 578 is not comparable to anything and
should not be the finding's value; the `py.typed` sub-claim is refuted.

---

## Instruments written for this seat

| file | what it does |
|---|---|
| `verify-1/run_arm.sh` | runs the eight gate scripts that construct the coordinator or read the stub; records rc, wall time and the FAIL-line set per arm |
| `verify-1/stub_armA2_faithful_private.py` | the stub with upstream's own `config_entry` parameter and ContextVar fallback (arm A2) |
| `verify-1/stub_armB_required.py` | the stub with `config_entry` required (arm B) |
| `verify-1/real_ha_fallback_rule.py` | replays the integration's construction call against upstream's `__init__` branch, inside and outside the entry-setup ContextVar scope |
| `verify-1/untyped_defs_ast.py` | my own toolchain-free ruler for D10-03 |
| `verify-1/data_description_count.py` | my own `data`-vs-`data_description` ruler for D10-02, over all three string files |
| `verify-1/uc-*.py`, `ce-2025.2.0.py`, `rule-*.md` | upstream sources and rule pages, fetched, kept for re-reading |

Every file the arms mutated (`coordinator.py`, the stub, `strings.json`,
`translations/en.json`, `translations/sv.json`, `quality_scale.yaml`) was backed
up before the first mutation and restored; all six md5-match their backups, and
the comparator was shown able to report `MISMATCH` on a negative control. The
placeholder `RELEASE_NOTES.md` was removed.
