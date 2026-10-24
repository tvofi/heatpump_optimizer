# D10 — verifier seat 2 of 3

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`. 8-core Apple M1, 8 GB.
Instruments under `tools/audit/round3/D10/verify-2/`. Every metric below is a
count over source, a call count, or a count of mypy output lines — all
contention-immune; taken under `load1` 7.21–32.84 with `thread_factor=1.0`
throughout, and reproduced unchanged across that range.

**Restore verification.** Every file I mutated was restored from a `.bak` under
`verify-2/orig/` and `cmp`-verified at each step; at the end
`diff -rq custom_components <pristine worktree>/custom_components` and the same
over `tests/` report no differing tracked file (only `__pycache__`, since
removed).

**Environment limits, stated rather than left silent.** `tests/entities.py`
cannot run in this export (`FileNotFoundError: RELEASE_NOTES.md`) and
`tests/deployment_shape.py` needs a git repo, which the export is not. "The
gate" below therefore means `ha_contract.py` (51 contracts + 4 conventions),
`config_flow_steps.py` (203 checks), `features.py` (2136 checks) and
`structure.py` — not the full script list.

---

## D10-01 — the register's three stale `todo` rows — **weaken**, severity `low`

### Finder's harness, re-run verbatim

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/qs_register.py`

    rules_checked=52  register_divergences=4
    rules_todo_but_satisfied=3  rules_done_but_unsatisfied=1
    thread_factor=1.0  load1=32.84
    DETAIL todo_but_satisfied: log-when-unavailable, exception-translations, reconfiguration-flow
    DETAIL done_but_unsatisfied: config-flow

Exact reproduction of `value: 4`.

### My own number: **3**

Metric definition (mine): *of the 6 rules `quality_scale.yaml` marks `todo`, the
number whose upstream requirement an independent check finds satisfied, each
check driven on the production path rather than on an isolated helper; the
`done`→unsatisfied direction is excluded because it is another finding's unit.*

Harness: `tools/audit/round3/D10/verify-2/v2_todo_rule.py`.

    v2_todo_rules_satisfied=3  v2_todo_rules_checked=3
    v2_errors_over_5_failed_polls=1  v2_warnings_over_5_failed_polls=0  v2_infos_on_recovery=1
    v2_error_raise_sites=21  v2_raise_sites_untranslated=0  v2_translation_keys_absent_from_strings=0
    v2_async_step_reconfigure_on_configflow=1  v2_reconfigure_terminates=1  v2_reconfigure_successful_string=1

It differs from the finder's in three ways, deliberately. `log-when-unavailable`
is driven through the real `_fetch_tibber_prices` on a coordinator built the way
`async_setup_entry` builds one, counting **every** record on the
`custom_components.heatpump_optimizer` and `heatpump_optimizer` logger trees at
WARNING as well as ERROR — the finder binds the two latch methods to a bare
object, which by construction cannot see a second loud site elsewhere on the
outage path. `exception-translations` additionally requires every
`translation_key` to exist in `strings.json`, not merely to be present at the
raise site. `reconfiguration-flow` additionally requires the branch to
**terminate** — a method on the flow class that both writes the entry back and
aborts with a reason `strings.json` declares — because a defined-but-dead
`async_step_reconfigure` satisfies a grep and not a user.

Two of my own first-pass results were instrument defects and are recorded as
such: attaching the capture handler to `cm._LOGGER` *and* its ancestor
double-counted every record (2 ERRORs for one), and scanning only inside
`async_step_reconfigure` missed the terminator, which lives in
`_async_save_reconfigure` at `config_flow.py:1762`. Both fixed; both would have
produced a false "unsatisfied".

Null controls, one per rule, each moving my metric 3 → 2 and nothing else:

| perturbation | file | result |
|---|---|---|
| `if not self._tibber_outage_cycles:` → `if True:` | `coordinator.py:5703` | `v2_errors_over_5_failed_polls` 1 → 5, rule unsatisfied |
| `async_step_reconfigure` renamed | `config_flow.py:1673` | detected 1 → 0, rule unsatisfied |
| one `translation_key` stripped | `services.py:366` | untranslated 0 → 1, rule unsatisfied |
| one `translation_key` → a key `strings.json` lacks | `services.py:366` | absent-from-strings 0 → 1, rule unsatisfied |

### Attacks

**The value double-counts D10-02.** Executed: `DETAIL done_but_unsatisfied:
config-flow`, and that row's text is *"1 field(s) with no data_description:
['config.reauth_confirm.tibber_token']"* — D10-02 itself. One of the four units
is another finding on this panel, so `value: 4` is not additive with D10-02's
`value: 1`. The `unit` string does disclose the split ("3 todo-but-satisfied +
1 done-but-unsatisfied"), so this is a disclosed overlap rather than a hidden
one, but the per-finding number is **3**.

**"Its totals line is wrong" — refuted as stated.** The file documents its own
enumerator in the comment above the line. Run verbatim it returns

    Counter({'done': 44, 'todo': 6, 'exempt': 4})   over 54 keys

which is exactly what the totals line says (*44 done · 4 exempt · 6 todo*). The
line's own contract is "Counted from this file, not carried", and under that
contract it is correct. What is wrong is the statuses the line counts, not the
count. The compound claim survives only in the weaker reading.

**Grid artefact — present, and it is the finder's header that does not
reproduce.** `qs_register.py` reads `coverage_report.txt`, which the export does
not carry; the committed artefact is `coverage_report_12scripts.txt`. With it
copied to the name the harness reads, `rules_checked` 52 → 54 and
`register_divergences` **4 → 5**, `config-flow-test-coverage` joining the
done-but-unsatisfied set at 98.17% (the register claims 100% over a different
five-script lane set). The harness header's EXPECTED — `rules_checked=54,
register_divergences=4` — reproduces in neither cell. `rules_todo_but_satisfied
= 3` is stable in both; that is the ruler-robust half, and it is my number.

**"Nothing reads the file" — true, but a recorded decision rather than a
discovery.** It is measured with a null *and* a positive control at
`tests/closure.py:662-695` (`NEVER_WIDENED`), asserted at `tests/entities.py:9064`,
and relied on at `tests/deployment_shape.py:257`. My own executed control:
flipping `reconfiguration-flow: todo` → `done` in the shipped register leaves
`tests/ha_contract.py` and `tests/config_flow_steps.py` byte-identical and
`tests/structure.py` green.

**Single-line production mutation the suite misses** (contract §4): any status
line in `custom_components/heatpump_optimizer/quality_scale.yaml` — a file in
the production package, so the gap is real; it is also already documented and
accepted.

**Is the severity earned by consequence?** Nothing reads the file; `manifest.json`
declares no `quality_scale` key; hassfest skips the register for custom
repositories. There is no user-facing surface at all — a wrong register costs a
user nothing. The cost falls on a maintainer or a later audit seat who trusts
it, and it is not nil: three of the six `todo` entries name issues (#216, #217,
#196), so the register doubles as a tracker and a stale `todo` invites redoing
landed work. `low` is earned and nothing more is.

**Vote: weaken** — claim true at 3 of 3 checkable rules under my own harness;
the filed `value: 4` overlaps D10-02 by one unit and the "totals line is wrong"
half is false as written. Severity `low` stands.

---

## D10-02 — `reauth_confirm.tibber_token` has no `data_description` — **verify**, severity `low`

### Finder's harness, re-run verbatim

    config-flow  bronze  done  todo
      config_flow=true; 1 field(s) with no data_description: ['config.reauth_confirm.tibber_token']

### My own number: **1 of 270**, and **3 of 810** across the shipped files

Metric definition (mine): *over every translation file the package ships
(`strings.json` and `translations/*.json`), the number of (file, section, step,
field) tuples where `field` is under a step's `data` map and absent from the same
step's `data_description`, recursing into `sections` blocks.*

Harness: `tools/audit/round3/D10/verify-2/v2_flow_fields.py`.

    v2_translation_files=3  v2_flow_fields_all_files=810
    v2_fields_without_data_description=3  v2_section_blocks=102
    strings.json 270 fields / 1 gap · en.json 270 / 1 · sv.json 270 / 1
    DETAIL gap strings.json:config.reauth_confirm.tibber_token
    DETAIL gap en.json:config.reauth_confirm.tibber_token
    DETAIL gap sv.json:config.reauth_confirm.tibber_token

The finder's rule reads `strings.json` alone and does not recurse into
`sections`. Mine does both. Recursion adds **0**: the 34 section blocks per file
carry `name`/`description` and no `data` of their own, so a one-level walk and a
recursing walk agree at 270. The count is ruler-robust, which is worth saying
explicitly on a project where censuses have come out three different ways.

### Attacks

**Is the rule real?** Fetched
`developers.home-assistant.io/.../rules/config-flow`: *"use `data_description` in
the `strings.json` to give context about the input field"*, with a worked
`strings.json` example carrying both maps. Correctly scoped; not the finder's
invention.

**Is the severity earned by consequence?** Partly mitigated and still real. The
step carries a title and a description ("Tibber refused the configured token.
Enter a valid API token to restore price updates."), so the user is not without
context. What is missing is the per-field pointer: the *setup* step's
`tibber_token` description says *"Create one at developer.tibber.com"*; the
reauth screen — the one screen a user reaches **because** the token stopped
working — says nothing about where a replacement comes from. One missing helper
line on one screen. `low`.

**Grid / contention / stub reachability:** none apply — a count over three JSON
files, identical across runs, no execution path involved.

**Vote: verify**, severity `low`, value 1 (of 270 in `strings.json`; 3 of 810
across all shipped translation files, the same field each time).

---

## D10-03 — strict-typing unmet — **weaken**: the finding is real, the filed value is not

### Finder's harness, re-run verbatim, three times

`MYPY=<mypy 2.3.1> bash tools/audit/round3/D10/strict_typing_rule.sh`

    mypy_exit=1  mypy_error_lines_total=648  integration_errors=578
    code_no_untyped_call=174  code_type_arg=119  code_no_untyped_def=67  py_typed_present=0

Three consecutive runs: identical RESULT lines, and `mypy_strict.txt`
**byte-identical to the finder's committed artefact**, md5
`cc828da8bc753fbc4c85f90974940fa4`. Under its own stated ruler the number is
exactly deterministic. It is **not** invocation noise. What moves is the ruler.

### My own measurement: four rulers, each stated completely

Harness: `tools/audit/round3/D10/verify-2/v2_typing_rulers.py`; raw output in
`verify-2/rulers.json`. Metric definition (mine): *`mypy --strict` error lines
whose path is under `custom_components/heatpump_optimizer/`, split by error code,
under rulers that differ only in the Home Assistant stand-in, the interpreter
target and the missing-import flag, every other variable held.*

- **A — the finder's / the D10 brief's.** mypy 2.3.1 on CPython 3.11.5;
  `--strict --no-color-output --no-error-summary --hide-error-context
  --show-error-codes --cache-dir <fresh> --python-version 3.11
  --ignore-missing-imports`; `MYPYPATH=<root>/tests/hastub`; target
  `custom_components/heatpump_optimizer`; no `homeassistant-stubs`, no
  third-party packages installed.
- **B — the repository's own pinned ruler** (`tests/typing_ruler.py:run_mypy`),
  reproduced on this box. mypy 2.3.1 on CPython **3.13.15**; `--strict
  --warn-unused-ignores --show-error-codes --no-error-summary --no-incremental
  --cache-dir <fresh> --python-version 3.13`; `MYPYPATH` and `PYTHONPATH`
  **stripped from the environment**; installed `homeassistant-stubs 2026.2.3,
  aiohttp 3.13.3, numpy 2.5.3, threadpoolctl 3.6.0, voluptuous 0.15.2` — the
  census `environment` block exactly.
- **C — ruler A with no Home Assistant stand-in at all** (`MYPYPATH` stripped,
  everything else identical to A).
- **D — ruler B's toolchain with ruler A's flags and hastub back on `MYPYPATH`.**

| | A (finder) | C (no stand-in) | B (repo pinned) | D |
|---|---|---|---|---|
| integration errors | **578** | 562 | **187** | 0 |
| total error lines | 648 | 562 | 187 | 1 |
| lines inside `tests/hastub` | 70 | 0 | 0 | — |
| construction guard | **no** | yes | yes | **no** |
| `no-untyped-def` | **67** | **67** | **67** | 0 |
| `no-untyped-call` | 174 | 7 | 7 | 0 |
| `attr-defined` | 102 | 12 | 1 | 0 |
| `type-arg` | 119 | 30 | 41 | 0 |
| `union-attr` | 19 | **362** | 0 | 0 |

Ruler B, run through the repository's own script:

    env -u MYPYPATH -u PYTHONPATH <pinned venv>/bin/python tests/typing_ruler.py --mypy
    ##### 2 number(s) IMPROVED and not yet recorded #####
      errors                 191   187   -4  BETTER
      by_code[no-any-return]  37    33   -4  BETTER
    ALL 25 typing-ruler checks PASSED

Ruler D is a **dead run**, and worth recording because it is the trap:

    <venv>/lib/python3.13/site-packages/numpy/__init__.pyi:737: error:
      Type statement is only supported in Python 3.12 and greater  [syntax]

mypy aborts and a naive counter reads **0 errors on this tree** — exactly the
shape `tests/typing_ruler.py` guard 3 exists to refuse. Ruler C is not a control
either: 362 of its 562 are `union-attr` that neither A nor B produces.

**The ruler-invariant core.** Across all three live rulers only two things hold
still: `no-untyped-def = 67` and `py.typed` absent. Perturbation — annotating
`resolve_currency(hass)` → `(hass: object)` in
`custom_components/heatpump_optimizer/currency.py:15` — moves it 67 → 66 under A,
B and C simultaneously (578→577, 562→561, 187→186), and leaves the dead ruler D
at 0, which is the null control on D.

### Attacks

**The finder's ruler is one the repository explicitly refuses.**
`tests/typing_ruler.py` guard 1 ("the construction guard") requires total
`error:` lines to equal the lines under the package, precisely so that hastub
leakage cannot enter the number. Ruler A emits 648 against 578, with 70 lines
inside `tests/hastub`. The harness *prints* `construction_guard_equal=no` and
`mypy_exit`, and its header says in terms that its number and the census are not
comparable — the disclosure is there. But `findings.json` carries `value: 578`,
which is **3.1×** the repository's own number for the same tree, and the
finding's own title says 67 is *"the ruler-independent size of it"*. The
evidence field and the title name different numbers, and the evidence field is
the one a reader takes. That is what I am weakening.

**The `py.typed` sub-claim: refuted.** The rule text, fetched:

> we recommend fully typing **your library** and making **your library**
> PEP-561 compliant. This means that you need to add a `py.typed` file to
> **your library**.

Independent census of `home-assistant/core` at tag `2026.9.0`, commit
`dfb5a9e690daaf204b542896e4b595e61a11a401`, recursive git tree,
`truncated: false`, 31 470 entries: **exactly one `py.typed`, at
`homeassistant/py.typed`**; **zero** of the **1509** integrations (counted as
`homeassistant/components/<domain>/manifest.json`) carries one — including all
**631** integrations listed in `.strict-typing`. A `py.typed` in
`custom_components/heatpump_optimizer/` would mark nothing: the marker belongs
on the PyPI library the integration depends on, and of this integration's three
declared requirements `numpy` ships one, `scipy` does not and `threadpoolctl` is
a single module — none of which this repository owns or can add one to. What the
rule asks of a **custom** integration is the `mypy --strict` half alone; the
`.strict-typing` half is a file inside core and is structurally unavailable.

**Is the severity earned?** Yes at `low`. The rule is genuinely unmet — 187 > 0
under the repository's own ruler, 67 unannotated defs under every ruler — and
the finder is right that the mechanism already exists: `tests/typing_ruler.py`
ratchets per code and `tests/typing_budgets.json` records the census, so closing
the rule is paying a ratchet down, not building anything.

**Vote: weaken** — finding real, value should be **67** (`no-untyped-def`, stable
under every live ruler) or **187** (the repository's own census, re-measured
here), not 578; the `py.typed` sub-claim is refuted. Severity `low` stands.

---

## D10-04 — the coordinator's missing `config_entry` — **weaken**, `medium` → `low`

### Finder's harness, re-run verbatim

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/coordinator_entry_rule.py`

    super_init_calls=1  calls_passing_config_entry=0
    coordinator_config_entry_is_set=0  coordinator_has_private_entry_attr=1
    stub_names_config_entry=0  stub_signature=(self,*args,**kwargs)
    kwargs_actually_passed=['name', 'update_interval']
    thread_factor=1.0  load1=31.97

Exact reproduction. The divergence itself is real and I do not dispute it: the
integration calls `super().__init__(hass, _LOGGER, name=DOMAIN,
update_interval=…)` at `coordinator.py:1306` and upstream's own example passes
`config_entry=`.

### Half A — "the stub signature makes it undetectable by the whole gate": **refuted**

Harness: `tools/audit/round3/D10/verify-2/v2_coordinator_entry.py`. Metric
definition (mine): *the number of single-line mutations to the `super().__init__`
call that a check writable against the stub **as shipped** cannot tell apart —
i.e. the size of the blind spot attributed to `(self, *args, **kwargs)`.* It is
**zero**.

    arm 1  stub unchanged, production at baseline:
             v2_gate_shaped_check_verdict=FAIL  v2_check_needs_stub_change=0
    arm 2  stub unchanged, config_entry=entry added at coordinator.py:1306:
             v2_calls_passing_config_entry=1
             v2_kwargs_passed=['config_entry','name','update_interval']
             v2_gate_shaped_check_verdict=ok

A check that wraps `DataUpdateCoordinator.__init__` and asserts `config_entry` is
among the keywords is **red at baseline and green after the fix, with the stub
byte-identical throughout**. The finder's own harness is exactly such a check.
`(self, *args, **kwargs)` blocks only a *TypeError*-shaped detection; it does not
block detection. What is missing is an assertion, which is the ordinary
"untested property" situation, not a structural blindness.

I also ran the converse experiment. With the stub given Home Assistant's
2026.9.0 parameter list — `config_entry` keyword-only, `UNDEFINED` default, the
`current_entry` ContextVar fallback — and production untouched:
`ha_contract.py` and `config_flow_steps.py` byte-identical to baseline,
`features.py` at the same verdict (1 of 2136, the same pre-existing failure;
only unrelated DHW log-line ordering moved). So the faithful signature buys no
detection either. One caveat I record because it cuts the other way: my first
pass named the ContextVar publicly and `ha_contract.py` **did** go red —
*"no inventory entry: ['homeassistant.helpers.update_coordinator.current_entry']"*.
The stub's public **surface** is policed; only the constructor's **parameter
set** is not, which is what the finder's mechanism paragraph says about
`tests/ha_contract.py:535`, and that part is correct.

### Half B — user-visible consequence: **zero at every version in the window**

Real `DataUpdateCoordinator.__init__`, fetched from `home-assistant/core`:

```python
if config_entry is UNDEFINED:
    # It is not planned to enforce this for custom integrations.
    frame.report_usage(..., custom_integration_behavior=frame.ReportBehavior.IGNORE)
    self.config_entry = config_entries.current_entry.get()
```

Version survey, 11 releases fetched and parsed:

| version | report? | `custom_integration_behavior` | `breaks_in_ha_version` | ContextVar fallback |
|---|---|---|---|---|
| 2024.12.0 | no | – | – | yes |
| **2025.2.0** (hacs floor) | no | – | – | yes |
| 2025.3.0 / 2025.4.0 / 2025.6.0 | no | – | – | yes |
| 2025.8.0 → 2026.6.0 | yes | `IGNORE` | `2026.8` | yes |
| **2026.8.0 / 2026.9.0** | yes | `IGNORE` | *dropped* | yes |

And `ConfigEntry.async_setup` does `current_entry.set(self)` around the call that
invokes `async_setup_entry` — identical at 2025.2.0 and 2026.9.0. The coordinator
is constructed at `custom_components/heatpump_optimizer/__init__.py:208`, inside
`async_setup_entry`. So in real Home Assistant `coordinator.config_entry` **is**
the entry. Executed confirmation, arm 3:

    v2_faithful_sig_config_entry_set=1      (HA's own signature + ContextVar)
    v2_baseline_stub_config_entry_set=0     (the shipped stub)
    v2_faithful_sig_construction_raised=0

**`coordinator_config_entry_is_set=0` is therefore a stub artefact** — the
contract's own attack, "reachable in real Home Assistant or only through the
test stub", lands on the finding's second observable. A custom integration is
never warned, at any version from the floor to today, by upstream's explicit
decision.

### What survives

**Single-line production mutation the suite misses** (contract §4):
`super().__init__(hass, _LOGGER, name=DOMAIN, …)` at
**`custom_components/heatpump_optimizer/coordinator.py:1306`**. Adding
`config_entry=entry` there leaves `ha_contract.py` and `config_flow_steps.py`
byte-identical (executed). The line is in a production file, so the test gap
stands on its own terms.

Two genuine stub infidelities are worth carrying, neither of them the signature:
the stub **drops** `config_entry` on the floor (`v2_baseline_stub_config_entry_set`
stays 0 even with the production fix applied), and its
`async_config_entry_first_refresh` counts where real HA's
`_async_config_entry_first_refresh` **raises `ConfigEntryError` on
`self.config_entry is None`**. The two cancel in this tree only because upstream's
ContextVar fallback means the real attribute is never None here.

**Is `medium` earned?** No. A style divergence from upstream's current example,
which upstream has decided in its own source not to enforce for custom
integrations; zero user-visible effect at every shipped version in this
integration's supported window; a one-keyword fix. `low`.

**Vote: weaken**, `medium` → `low`. Executed number: `calls_passing_config_entry
= 0 of 1` (the divergence, reproduced), with `v2_check_needs_stub_change = 0`
refuting the stated mechanism and
`v2_faithful_sig_config_entry_set = 1` vs `v2_baseline_stub_config_entry_set = 0`
showing the second observable is a stub artefact.

---

## Read after my numbers were formed: where I differ from seat 1

Seat 1's report was opened only after everything above was written. We agree on
all four votes and on all four severities. Five places where our metrics or our
numbers differ, stated so the judge can compare rather than average.

**1. "Invocation sensitivity" is the wrong name for D10-03's spread.** Seat 1's
table is headed *"Invocation sensitivity, same box, same mypy"*, and each row is
a different flag set. Under the finder's **exact stated ruler** the number is
not sensitive at all: three consecutive runs gave identical RESULT lines and an
`mypy_strict.txt` byte-identical to the finder's committed artefact, md5
`cc828da8bc753fbc4c85f90974940fa4`. The finder's 578 is perfectly reproducible;
it is simply not portable. "Ruler artefact" is right; "invocation sensitivity"
would let a reader conclude the finder's harness is noisy, and it is not.

**2. The repository's pinned census is 187, not 191 — derived, not carried.**
Seat 1 quotes `tests/typing_budgets.json`'s recorded 191. I built that ruler on
this box (CPython 3.13.15 via `uv`, `mypy==2.3.1`, `homeassistant-stubs==2026.2.3`,
`aiohttp`, `numpy`, `threadpoolctl`, `voluptuous` — the census `environment`
block exactly) and ran `tests/typing_ruler.py --mypy`, which prints
`errors 191 → 187 BETTER (lower is better)` and `by_code[no-any-return] 37 → 33`,
with `ALL 25 typing-ruler checks PASSED`. The recorded census is four stale at
this baseline. Per `brief-citations.md`, derive the count rather than carry one;
that applies to a number quoted out of a budget file as much as out of a brief.

**3. Seat 1's 562 row is a third artefact, not a cleaner ruler.** Removing
hastub from `MYPYPATH` with everything else held gives 562 for me too — but
**362 of those 562 are `union-attr`**, a code that is 19 under the finder's
ruler and 0 under the repository's. Dropping the stand-in does not subtract the
stub's noise; it substitutes different noise. Only `no-untyped-def = 67` survives
all three live rulers.

**4. A fourth ruler that neither of us had, and it reports zero.** The pinned
toolchain with the finder's flags (hastub back on `MYPYPATH`, `--python-version
3.11`) makes mypy **die** on `numpy/__init__.pyi:737: Type statement is only
supported in Python 3.12 and greater [syntax]`. One line out, zero lines under
the package: a counter without `tests/typing_ruler.py`'s exit-status and
construction guards reads that as a clean tree. The finder's own harness prints
`mypy_exit` and `construction_guard_equal`, so it is not blind — but the
existence of a plausible ruler that reports 0 on this tree is the strongest
argument for taking `no-untyped-def = 67` as the finding's value.

**5. D10-04: seat 1 verified the gate is blind; I also refute "no gate test
*can* distinguish".** Seat 1's arms show that naming the parameter upstream's way
changes no verdict (34/34), which I reproduce in verdict terms. But the
finding's causal sentence is stronger than that: *"the stub signature names no
parameter, so **no gate test can** distinguish that call"*. That is false, and
the counterexample is the finder's own harness. With the stub **byte-identical
to what ships**, a check that wraps `DataUpdateCoordinator.__init__` and asserts
`config_entry` is among the keywords is **FAIL at baseline and ok after the
one-keyword fix** (`v2_check_needs_stub_change=0`). The gap is "nothing asserts
it", not "nothing could". I also record a detail that cuts against the finder's
"the whole gate is structurally blind": my first faithful stub named the
ContextVar publicly and `tests/ha_contract.py` **did** go red — *"no inventory
entry: ['homeassistant.helpers.update_coordinator.current_entry']"*. The stub's
public surface is policed; only the constructor's parameter set is not.

**One result of seat 1's that I verified and that strengthens the surviving
half.** Seat 1 names `coordinator.py:5732` as the attribute's only consumer and
`tests/entities.py:12727` as the line that supplies it. Both reproduce on my own
read:

    coordinator.py:5732   entry = getattr(self, "config_entry", None)
                          if entry is None ...: return        # reauth never offered
    tests/entities.py:12727   _ra_coord.config_entry = _ra_entry

So the true arm of `_tibber_start_reauth` is reached in the suite only because
the test assigns the attribute production never sets under the stub — the test
supplies its own precondition. That does not change my severity, because in real
Home Assistant the ContextVar fills the attribute and reauth works at every
version in the window. It does change why the one-keyword fix is worth taking:
the user-visible property it protects is *"a refused Tibber token offers
reauthentication"*, and today that property rests on a legacy fallback upstream
is actively reporting against.

**Seat 1's per-def ruler for D10-03 reconciles exactly.** My own AST count,
written independently: `defs_total=1303`, `defs_not_strict_clean=65`, against
67 `[no-untyped-def]` lines over **65 distinct locations**, the two doubled ones
being `optimizer.py:365` and `coordinator.py:2793`; `mypy-only` and `ast-only`
location sets both empty. 65 per def, 67 per error line, same defect set.

**Where seat 1 measured less than it could have, for the record.** Its
`log-when-unavailable` row reads the finder's `log_once_rule.py` transcript
rather than re-measuring. That harness binds the two latch methods to a bare
object; my check drives the real `_fetch_tibber_prices` on a coordinator built
the way `async_setup_entry` builds one and counts WARNING as well as ERROR
across the whole package logger tree. Same answer — 1 loud record per outage —
under the stronger instrument.
