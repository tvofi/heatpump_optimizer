# D10 round-4 verification — verifier 2 of 3 (panel D10-0)

- **Worktree**: `/Users/timmalmstrom/.zcode/workspace/default/audit-r4-verify-D10-2`,
  detached at `0855277` (branch head of `claude/13-dimension-audit-920935`).
- **Baseline the finder measured**: `7dd68dd`. Between `7dd68dd` and `0855277`
  nothing under `custom_components/` and none of the user docs changed (only
  `tests/`, `docs/HANDOVER.md`, audit registers and plan files). The default-gate
  script set is unchanged apart from a skipped-script rename
  (`record_status.py` → `delivery_status.py`, both skipped). **No number moved.**
- **Interpreter**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  `PYTHONPATH=tests/hastub` from the worktree root, as briefed.
- **Toolchains**: the finder's two scratch venvs the `mypy_arms.sh` header names
  (`/private/tmp/hpo-d10-mypy{,13}/venv`) still exist; I re-used them and
  installed nothing. My own coverage ran in `/private/tmp/hpo-d10-verify02/`.
- `load1` across my runs: 2.88–9.34 (other agents active). Every number below is
  a count, a percentage, or a static type — none is contention-sensitive; no
  timing-based refute is claimed anywhere.
- Per the brief I did not read the other verifiers' reports or the register's
  verdict columns. Three `grep` sweeps over `--include='*.md'` unavoidably
  printed register lines in the terminal; I used none of them as evidence.

## Method

Re-ran every harness exactly as its header says (`qs_rules.py` with **my own**
coverage JSON and **my own** mypy census as inputs; `coverage_measure.sh` fast
then e2e in a fresh work dir; `mypy_arms.sh`; `log_when_unavailable.py`), then
produced independent numbers with my own instruments: my own `coverage`
parse, my own heading grep, my own `reveal_type` probe file, my own
`get_type_hints` runtime probe, and my own register-vs-executed comparison.
Attacked in the contract's order: gate mode (fetched the four rule pages whose
wording decides the contested verdicts, plus the checklist), aggregate,
null control (executed, both directions, for D10-01 and D10-02; perturbation
both arms for D10-03), reachability, severity.

## Re-runs of the finder's harnesses

| harness | finder (7dd68dd) | mine (0855277, own inputs) |
|---|---|---|
| `coverage_measure.sh` fast+e2e | 97.18 % pkg (14948/15381); config_flow.py 97.2 %, 756 stmts, 21 missed; 0/56 below 95 | **identical**: 97.18 % (14948/15381); 97.2 %, 756, 21; 0/56; lowest battery.py 95.0 |
| `qs_rules.py` | rules_total=54, declared_mismatch=3, runtime_data_root_alias_parametrized=False | **identical**: 54 / 3 (same three rows) / False |
| `mypy_arms.sh` | armB=0; armA 542/470/72; probe Any / Coordinator | **identical**, including the by-code table |
| `log_when_unavailable.py` | 1 ERROR / 9 DEBUG / 1 INFO, latch resets | **identical** |

All 20 scripts in my coverage run exited 0 except `golden.py` (exit 1 in strict
mode, the instrument's own documented artefact). `entities.py` exited 0 here
because my worktree has `.git` (the finder's export had none) — a superset, and
the figures came out identical anyway.

## D10-01 — quality_scale.yaml drifted, 3 of 54 rows contradicted — **verify**

My numbers, my instruments:

- Register: 54 rows, Counter{'done': 48, 'exempt': 4, 'todo': 2} — the
  "54" denominator is real, and the fetched checklist is 20+10+21+3 = 54 rules
  with the same names.
- `config_flow.py`: **97.2 %, 756 statements, 21 missed** (my own coverage run,
  my own JSON parse) against the declared "100 % (661 statements, 0 missed)".
  The HA rule page says verbatim "we want to have **100%** test coverage for the
  config flow" — the finder's `>= 100.0` gate is the rule, not an invention.
- `test-coverage`: my run — 0 of 56 modules below 95 %, package 97.18 %; rule
  page: "Above 95% test coverage for all integration modules". The tree's own
  `tests/coverage_budgets.json` (2026-09-11) records the same 97.2 / 0-below.
- `docs-known-limitations`: 0 headings (see D10-02).

**Attacks, in order:**

1. *Wrong gate mode* — fetched the three rule pages; every threshold the
   harness encodes matches the fetched text (100 %, 95 %/module, dedicated
   section, "There are no exceptions to this rule" on all three). The one
   nitpick I can construct — `round(pct,1) >= 100.0` would pass 99.95 — is
   2.75 points away from mattering here. Attack fails.
2. *Aggregate artefact* — not a grid; 54 independent row checks. I re-derived
   the three contested rows with my own code and re-counted the denominator.
   Fails.
3. *Null control* — executed, both directions: correcting only the
   `test-coverage` row (surgical edit, then `git checkout --` restore) moves
   `declared_mismatch` 3 → 2, leaving exactly the other two; flipping the
   agreeing `parallel-updates: done → todo` moves it 3 → 4. The counter is
   live and reads the file. Fails.
4. *Reachability* — `quality_scale.yaml` has no reader: it is pinned INERT by
   `tests/closure.py` (`NEVER_WIDENED`), `tests/entities.py` (the check whose
   message is "hassfest skips it for custom repositories and nothing under
   custom_components/ opens it") and `tests/deployment_shape.py`, with recorded
   byte-identical null-control captures. I attacked the finder's "nothing
   enforces this file" by grepping for readers — the three hits all *pin the
   exclusion*, none validates content. The mechanism claim survives my attack.
   Consequence is register honesty only → severity low (hygiene) is earned.
5. Corroboration of the drift mechanism: the tree's own prior evidence
   `tools/audit/w5-g5-195-coverage/coverage/coverage_report.txt:13` shows
   config_flow.py at 672 statements / 5 missed / 99.3 % — a point between the
   declared 661/0 and today's 756/21. The register's stale comments also check
   out: `docs/automations.md` has 3 ```` ```yaml ```` blocks against the
   comment's "0 automation examples", and my `log_when_unavailable.py` re-run
   (1 ERROR / 9 DEBUG) contradicts the comment's "one ERROR per failed poll".

One instrument defect, noted not voted on: `qs_rules.py`'s header says
`EXPECTED declared_mismatch=2 ... docs-known-limitations, runtime-data`, which
matches neither the committed `qs_rules.out.txt` (3) nor the report (3); run
without `D10_COVERAGE_JSON` the two coverage rows go `unmeasured` and the count
is 1. A stale EXPECTED line, direction-consistent with the finding; the judge
should read the 3 as the number with the env vars set, as the report's re-run
command does.

**Vote: verify. Severity low (hygiene) — earned.** Value 3 of 54 under the
finder's metric; my own metric ("rows whose declared status disagrees with an
independently executed verdict, denominator = rows in the file") gives the same
3, with the three rows re-derived by my own code.

## D10-02 — docs-known-limitations declared done, 0 such headings — **verify**

My own grep, my own metric (heading regex `^#{1,6}` + "known|limitation|caveat",
case-insensitive, over `README.md` + the six user docs):

- headings matching `^#{1,4}.*known limitation`: **0**; the word "limitation"
  anywhere in those files: **0**; total lines: **4075** exactly as claimed.
- Widening the net repo-wide, the only "known limitation" hits are the finder's
  own report and the audit register — not user documentation.
- Null control executed: appending `## Known limitations` to a scratch copy of
  `README.md` moves the count 0 → 1 (and the rule's executed status todo → done).
- Gate mode: fetched the rule page — a dedicated "Known limitations" section is
  required, "There are no exceptions to this rule." The heading-count metric is
  the rule's own shape.
- Counter-evidence re-checked: "Boundaries worth knowing before you pick a
  path:" is at `README.md:174` (the finder cites 176 — a two-line citation
  slip, immaterial: the content exists); caveat paragraphs at `README.md:534`
  and `docs/how-it-works.md:1032` exactly as cited. The finder's framing
  (placement/discoverability, not absence of knowledge) is honest.
- Reachability/severity: documentation-only; no user is blocked. low earned.

**Vote: verify. Severity low (hygiene).** Value 0 under both the finder's
metric and mine.

## D10-03 — root alias is a bare `ConfigEntry`, so `runtime_data` is `Any` in the three entry points — **verify**

Source facts, read directly: `__init__.py:43`
`HeatPumpOptimizerConfigEntry = ConfigEntry` (bare);
`coordinator.py:10451` `= ConfigEntry[HeatPumpOptimizerCoordinator]`; the three
entry points `async_setup_entry` (:248), `async_update_options` (:343),
`async_unload_entry` (:371) all annotate with the root alias; all six platform
modules **and** `services.py` import the alias from `.coordinator` (checked all
seven import lines).

My own probe (`/private/tmp/hpo-d10-verify02/v02_probe.py`, written from
scratch, run with arm B's venv under `--strict`): root alias →
`reveal_type(entry.runtime_data)` = **`Any`**; coordinator alias →
**`custom_components.heatpump_optimizer.coordinator.HeatPumpOptimizerCoordinator`**.
My probe also shows the alias objects themselves: unparametrised
`ConfigEntry[_DataT = Any]` vs parametrised — the PEP 696 default is exactly
why `--strict` stays silent. `mypy_arms.sh` re-run: 0 errors under the real
stub set; the 542 hastub errors reproduce with an identical by-code table
(`no-untyped-call`/`attr-defined`/`type-arg` dominate — stub-shape complaints).

Perturbation, both arms, executed in a copied tree
(`/private/tmp/hpo-d10-verify02/pert`, per the README's root-rule trap):

- naive parametrisation (`TYPE_CHECKING` import + `ConfigEntry["HeatPumpOptimizerCoordinator"]`):
  package-wide `--strict` count stays **0**, my probe on the root alias moves
  `Any` → the coordinator type (the stated direction), and
- `typing.get_type_hints(m.async_setup_entry)`: current tree **OK** (resolves
  `entry` to the bare `ConfigEntry` class); perturbed tree **FAILED: NameError:
  name 'HeatPumpOptimizerCoordinator' is not defined** — the exact runtime
  constraint the in-tree comment above `__init__.py:43` defends, reproduced.

**Attacks, in order:**

1. *Gate mode* — the metric is a static revealed type, not a timing figure; no
   fixture/gate selection involved. The quoted rule text is real: the
   runtime-data page says verbatim "the use of a custom typed
   `MyIntegrationConfigEntry` is required and must be used throughout" (applies
   when following strict-typing, which the register claims is done). Attack
   fails.
2. *Aggregate* — not an aggregate. Fails.
3. *Null control* — the coordinator alias within the same package is the
   built-in control, and my perturbation is the positive control; both move the
   number the stated way. Fails.
4. *Reachability* — nothing is wrong at runtime today; my `get_type_hints` run
   on the current tree succeeds. The consequence is eroded static checking of
   three functions and an over-generous 0 — which is what the finding says.
5. *Severity* — low, and the finder explicitly refuses to inflate it. Earned.

Caveat carried from the finder (still true): arm B uses stubs 2025.4.4 on
Python 3.13.1, not `typing_budgets.json`'s pinned 2026.2.3 / ≥3.13.2, which
this box cannot install. The reveal-type result is insensitive to stub version
(a bare alias defaults its data typevar to `Any` in any PEP-561 stub set), but
the "0 errors" corroboration technically rests on the unpinned pair. This does
not weaken the finding, whose metric is the revealed type.

**Vote: verify. Severity low (hygiene).** Value: `Any` (root) vs
`HeatPumpOptimizerCoordinator` (coordinator), under my own probe as well as the
finder's.

## Deviations and disclosures

- I re-used the finder's mypy venvs (the harness header names them as
  pre-built); installed nothing, as instructed.
- My coverage measurement is the finder's wrapper around the tree's own
  `coverage_tree.sh` — the same instrument the ratchet consumes — but driven
  with my own work dir and parsed with my own code; the three contested
  verdicts were additionally re-derived with instruments I wrote (grep, JSON
  parse, probe files, perturbation copies).
- The `sed` first attempt at the D10-01 perturbation hit both `status: todo`
  rows and self-cancelled (3 → 3); re-done surgically, 3 → 2 and 3 → 4 as
   reported above. The worktree was restored (`git status` clean) afterwards;
   the only file I leave behind is this report, uncommitted, as instructed.
