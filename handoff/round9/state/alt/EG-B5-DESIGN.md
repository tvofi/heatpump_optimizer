# EG-B5: DHW planner extraction, design spec

**Status and scope.** tvofi opted in on 2026-09-28. The spec covers:
- #1743: the move, R9-EG-B5, and the dedupe that precedes it, R9-EG-B5a;
- #1747: a defect found on the way, R9-EG-B8;
- #1748: a precondition in R9-F10.3.

**Basis.** Measured at origin/main `31394964`. Main has since moved to `686239d2` (#1735), which does not
touch `optimizer.py`, the structure scripts or `mutation_table.py`. Line numbers are at `31394964`;
re-measure at your merge base.

**Provenance.** Two mapping seats (code, roster), one skeptic seat (§10), and the review seat's own probe
for #1747.

## 1. Decision

1. **What moves.** The 19-method DHW planner core moves out of `HeatPumpOptimizer` into one class,
   `DhwPlanner`, in a new module `dhw_planner.py`. That is 1,851 lines by AST span, or 1,852 counting the
   `@staticmethod` line. The planner is built once per solve from explicit inputs, writes no attribute,
   and returns what the optimizer stashes today.
2. **What stays.** `_optimize_with_dhw` (386), `_solve_space` (86) and `_co_optimize` (72) are
   orchestration and stay on the optimizer.
   - Between them they call 12 other optimizer methods, so a moved copy would need a back-reference to
     the optimizer: the `_helper(self, ...)` shape `docs/HANDOVER.md:58` refuses.
   - 37% of `_optimize_with_dhw` matches `_optimize_space_only` line for line (difflib).
3. **The duplicated closures come out first, in R9-EG-B5a.** The `_space_traj` / `objective` /
   `objective_batch` closures are optimizer machinery, duplicated between the two solve paths. B5a replaces
   them with one builder, in the same module. #1738 arm (a), which counts duplication per module, is
   therefore irrelevant to B5.
4. **Before B1.** The planner's inputs already exist per solve. EG-B1 later changes at most the planner's
   construction site.
5. **Refused alternatives:**
   - Moving `_optimize_with_dhw`: it needs the back-reference.
   - A mixin: it keeps one god-class surface.
   - Module functions over the optimizer: refused by `docs/HANDOVER.md:58`.
   - Waiting for B1: it serialises B1 → B6 → B5 → B7 to save about 10 lines of churn.
   - A trailing `requirement` field on `DhwPlan`: it breaks the 14-key contract pin (§3).
   - An `if TYPE_CHECKING:` import: it adds an equivalent GUARD_OFF site, which today's count ratchet
     refuses (§6).

## 2. Boundary

**The 19 methods that move:**

| method | span | method | span |
|---|---|---|---|
| `_dhw_planning_prices` | 2519 (22) | `_dhw_cop_profile` | 5176 (19) |
| `_baseline_dhw_economics` | 3427 (62) | `_plan_dhw_min_cost` | 5196 (211) |
| `_effective_dhw_windows` | 4278 (33) | `_apply_dhw_pins` (staticmethod) | 5409 (20) |
| `_dhw_legionella_due` | 4312 (141) | `_dhw_plan_temps` | 5430 (19) |
| `_dhw_legionella_ceilings` | 4454 (110) | `_repair_dhw_floor` | 5450 (198) |
| `_dhw_legionella_plan` | 4564 (49) | `_clamp_dhw_to_capacity` | 5649 (101) |
| `_dhw_coil_wood_forecast` | 4614 (51) | `_apply_dhw_min_run` | 5751 (103) |
| `_dhw_planner_draws` | 4666 (20) | `_dhw_raise_fits` | 5855 (34) |
| `_dhw_window_floors` | 4687 (135) | `_plan_dhw_cheapest_first` | 5890 (171) |
| `_build_dhw_requirements` | 4823 (352) | | |

Verified by AST (both seats):
- The 19 call no optimizer method outside themselves.
- They write only `_dhw_requirement` and `_dhw_legionella_step` (:5148-5149).
- They read `self.model` in 16 of the 19, `self.config.pv_export_price`, `self._pv_surplus` (:2532) and
  `self._price_known` (via `getattr(self, "_price_known", None)` in `_dhw_legionella_due`).
- They log through `_LOGGER` (:5375, :5379).
- Nothing is mutated through `self.model`.

**Module-level names:**

| name | goes to | why |
|---|---|---|
| `DhwPlan` (1728), `_DhwLegionellaPlan` (1716), `_DHW_MIN_RUN_CHUNK` (516), `_DHW_REFILL_WINDOW_HOURS` (220), `_dhw_windows_at` (176) | `dhw_planner.py` | used only by the core |
| a module logger | `dhw_planner.py` | the two debug lines' logger name changes; cosmetic |
| `_step_humidity` (1057), `_mean_humidity` (1062) | `thermal_model.py` | numpy-only, used by both sides; `thermal_model.py` holds the ambient-humidity fallback and imports nothing that imports `optimizer` (skeptic: confirmed cycle-free) |
| `_pin_is_free` (1052) | `manual_plan.py` | beside `PIN_ON` / `PIN_OFF`; the production module's imports are stdlib only (the `REASON_LEGIONELLA` import is in `tests/manual_plan.py:98`) |
| `_Horizon` | stays in `optimizer.py` | see "The horizon parameter" in §3 |
| `REASON_*`, `classify_dhw_steps`, `_dhw_step_weekdays`, `_dhw_resolved_publish`, `_MANUAL_KEEP_REASONS` | stay | orchestration and coordinator reads |

## 3. Types and interface

**Construction.** `optimize` builds `DhwPlanner(model, pv_export_price, pv_surplus, price_known)` after
`_stash_price_horizon` (:2869).
- It passes the planner down: `_optimize_with_dhw(horizon, planner)` → `_co_optimize(..., planner)`.
- Nothing stores it. It is built inside the worker process, so it is never pickled.
- `pv_surplus` and `price_known` default to None, which is what a fresh optimizer's direct calls see today.
- It exposes `.model`, which the test spies at `tests/features.py` 29502 and 51485 read.

**Six entry sites** become planner calls: `_optimize_with_dhw` :6101, :6118 and :6341; `_co_optimize`
:2422, :2427 and :2432.

**Return values replace the stashes:**
- **`_build_dhw_requirements` returns `(plan, requirement)`.** `requirement` is
  `max(floor, ready, runup_temps)` (:4926). A new `DhwPlan` field is refused: `DhwPlan` is
  `@dataclass(frozen=True)` whose fields are exactly the published keys (#224), and `tests/features.py`
  27408-27411 pins that 14-key tuple.
- **The optimizer keeps `_dhw_requirement`**, assigned from the returned value at exactly the points the
  stash was written today. That preserves last-writer-wins (§9). Its readers, `_publish_breach_reports`
  (:3411) and `_safety_release_steps` (:3839/3841), stay unchanged.
- **`_dhw_legionella_step` is deleted** from `__init__` (:1832-1833), from the resets in `optimize`
  (:2962-2963) and from the build. No production code reads it. The four test reads move to a spy (§5).

**The horizon parameter.** `_dhw_coil_wood_forecast(h)` reads 11 fields of `_Horizon`. Annotate `h` with a
Protocol defined in `dhw_planner.py` that declares those 11 fields as read-only properties.
- It needs no import of `optimizer` and adds no guard.
- `_Horizon`, a frozen dataclass, satisfies it structurally.
- Measure-first: mypy `--strict` accepts `_Horizon` against the Protocol. Run it with `HPO_TYPING_PYTHON`
  before hand-off.

## 4. R9-EG-B5a: the duplicated closures

- **The diffs.** `_space_traj` is byte-identical after dedent (3928-3941 against 6159-6172).
  `objective_batch` (3990 / 6223) and the scalar `objective` differ only by
  `grid_power = space if dhw_plan_power is None else space + dhw_plan_power`.
- **One builder.** An optimizer method builds all three from the horizon and an optional
  `dhw_plan_power`. With None, it is the space-only arithmetic.
- **Measured by simulation** (code-map seat `simulate_dedupe.py`, re-run by the skeptic):
  - `duplication_blocks` falls by 2: the builder's two closures still share one 10-line run;
  - `max_method_loc` falls by 1, because `sysid.identify` becomes the largest method;
  - `_optimize_with_dhw` falls by about 100 lines.

  Re-record, with the reason in the commit message.
- **After R9-F2.4.** F2.4 edits `_optimize_space_only`'s seed list (:4027-4123), so B5a collides with F2.4
  and B5 does not.

## 5. Test migration (no delegating shims)

**`tests/features.py`** (counts confirmed by the skeptic):
- **42 direct calls** (34 core plus 8 on `_baseline_dhw_economics`) move to a test factory's planner. The
  two `_dhw_planning_prices` calls also pass the surplus that :3211 sets today.
  - Every direct `_build_dhw_requirements` call unpacks `(plan, requirement)`.
- **16 class-level monkeypatch assignments and 8 captures** retarget to `DhwPlanner` (blocks 11559-11630,
  11700, 21760, 29568/29754, 51481/51516). `_LgOpt` also constructs optimizers, so it needs a second alias.
- **The 4 `_dhw_legionella_step` reads** (29211, 29226, 29597, 29811) happen after a full `optimize()`, and
  no plan is in the test's hands. Replace them with a planner spy that captures the last build's
  `plan.legionella_step`. `DhwPlan` already has that field.
- **The `_dhw_requirement` read and two writes** stay, because the optimizer still holds it.
- **The imports** of `DhwPlan`, `_DHW_MIN_RUN_CHUNK`, `_step_humidity` and `_mean_humidity` change path.
- **`_P3_FILES` (:50652) gains `dhw_planner.py`.** Without it the humidity-seam rule (#1520) silently stops
  covering the moved code.
- **Unchanged:** the 14-key `DhwPlan` pin (27408), because the tuple return leaves the fields alone, and
  the source-text pin at :33513, which is in `_optimize_with_dhw`.

**Elsewhere:**
- `tests/guard_pins.py:134`: one call.
- `tests/finite_boundary.py`: 0 references. The earlier B5 brief was wrong on this.
- `tools/audit/`: inert.

## 6. Instruments

**Mutation ledger: 9 rows, re-keyed by hand.**
- The rows:
  - 5 `killed_by`: `_apply_dhw_min_run` RETURN_DEL, `_dhw_coil_wood_forecast` RETURN_DEL,
    `_dhw_raise_fits` GUARD_OFF and RETURN_DEL, `_plan_dhw_min_cost` GUARD_OFF;
  - 1 module CONST: `_DHW_MIN_RUN_CHUNK`;
  - 1 `survivor_triage`: `_repair_dhw_floor` CLAMP_DROP;
  - 2 `killed_by` that move to `thermal_model.py`: `_step_humidity` RETURN_DEL `c560cbd8` and
    `_mean_humidity` RETURN_DEL `0696c43c`.
- The anchor is `FILE:SCOPE KIND sha1(old)[:8]`, where `old` includes indentation. Keep the indentation and
  the digest survives; only the path, the scope and the row file's directory
  (`tests/mutation_ledger/<map>/<file>/`) change. The skeptic's simulated move re-keyed all 9 this way, with
  `completeness_problems` falling to 0.
- `--normalize` does not do it: it rewrites only `FILE:LINE KIND` keys
  (`tests/mutation_table.py:1214-1245`).
- Carry the triage row as it is (`ci-autofix.md`: never automate triage). Re-run the re-key at every merge
  from main, because F10.5's nightly writer may add rows.

**Mutation ratchets: two preconditions.**
- **Today's count ratchet** refuses any new unpinned site net. The spec therefore avoids the
  `if TYPE_CHECKING:` guard (§3). The skeptic measured 3593 against 3592 with that guard, even with a
  perfect re-key.
- **R9-F10.3's per-site ratchet** keys a site by file (#1748). A move counts 115 of the 124 moving sites as
  added with today's inventory, 149 with the prototype's. The carry into F10.3 (moved-not-added within
  removed-from and added-to files, same trailing scope) must be in F10.3 before it merges. B5 does not
  start without it.

**Closures.**
- 22 of 27 closures include `optimizer.py`, and a new module makes the gate `MODE: FULL`.
- The closures job reports UNDER-SCOPED, and `closures-autofix` pushes `ci: re-record closures`. Wait for
  it. `tests/entities.py`'s orphan check fails until that commit lands.
- `--single` only if the autofix job goes red.

**Structure budgets.**
- A faithful move changes only `classes_over_300`, from 11 to 12 (`DhwPlanner` is about 1,814 to 1,880
  lines). That needs tvofi's confirmation before the push, unless R9-F10.4 has re-defined the metric
  (#1738 arm (c)).
- `local_imports` is unchanged while the planner import is at module level.
- `DhwPlanner` is itself large. A later split of legionella planning (`_dhw_legionella_due`, `_ceilings`
  and `_plan`, 300 lines) is a candidate, measured after B5.

**Typing.** The whole package is in scope, so the module must be `--strict`-clean with no ignores. This
container cannot run the census; a seat with `HPO_TYPING_PYTHON` runs it before hand-off.

## 7. Sequencing

| group | after | why |
|---|---|---|
| **R9-EG-B8** (#1747) | R9-F2.4 | a behaviour fix to `_co_optimize`, which B5 rewrites; F2.4 is F2's last PR on `optimizer.py` |
| **R9-EG-B5a** | R9-F2.4, R9-F10.4 | edits `_optimize_space_only` after F2.4; a structure writer after the instrument |
| **R9-EG-B5** | R9-EG-B5a, R9-EG-B8, R9-F1.10, R9-F10.4 | R9-F1.10 is the only roster PR planned to edit cluster lines (the P3 floor at :5689 in `_clamp_dhw_to_capacity`; #1741's literal at :4796 in `_dhw_window_floors`); R9-F10.4 comes after R9-F10.3, which must carry #1748 |
| **R9-EG-B1** | adds R9-EG-B5 | |

- No open branch edits cluster lines today (skeptic). F1.10 and F2.4 are not started.
- **Principle 2.** B5a and B5 re-record `tests/structure_budgets.json`, so neither is in flight with
  R9-EG-B1, R9-EG-B7 or each other.
- **The stamp.** B5 does not gate v6.8.0. If it merges first, it ships in it, with its release-note line.
- **The window.** W6, beside F10.5 and F11.4.

## 8. PR slicing and null controls

**Slicing.** B8 (behaviour), B5a (dedupe) and B5 (move) are three PRs. Each fails on its own, never inside
another's diff.

**B5a and B5** run these at the head and after every merge from main:

```
BASE=$(git merge-base origin/main HEAD)
PYTHONPATH=tests/hastub:custom_components python3 tests/env_drift.py --all "$BASE"   # byte-identical: the pure-refactor proof
git diff --stat "$BASE"...HEAD -- tests/golden/                                   # empty: no claims
GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF="$BASE" ./tests/run.sh              # B5: MODE: FULL until the closures bot commit
git checkout -- tools/audit/round4/D6
PYTHONPATH=tests/hastub:custom_components python3 tests/structure.py
```

**B5 additionally owes:**
- **Provenance.** A whole-file comparison showing every moved body identical after the stated substitution
  table: receivers, the stash-to-return edit, the Protocol annotation and import paths. This is #719's
  protocol, plus the three-dot diff at each merge from main (principle 3).
- **No writes.** An AST check that `DhwPlanner`'s methods write no instance attribute.
- **Humidity rule.** `_P3_FILES` includes `dhw_planner.py`. Control: remove it, and the humidity rule stops
  seeing the moved sites.
- **The ratchet carry.** The #1748 carry, demonstrated in F10.3, passes this PR's move.

**B8 follows `fixer.md`:**
- Failing test first: `b8_replan_blocked.py`'s -2.0 arm ships 9.22 kWh as-is and 0 in the control.
- Mutation proof.
- The root-cause section on #1747 (trigger 1).

## 9. Risks and measure-first items

- **#1747 is fixed by B8, before the move.** Reproduced by the review seat at `31394964`; the table is in
  the issue.
- **Last-writer-wins on `_dhw_requirement`.**
  - The second build overwrites it even when the replan is rejected. `wood_coil`'s first and last
    requirement arrays differ by up to 0.030 °C.
  - No published output changed: the breach is 20.939 either way.
  - The goldens never read the stash, so "no mismatch" is vacuous for them.
  - The move preserves this. Returning `requirement` makes any later choice one line at the call site.
  - Not filed: no output differs.
- **The Protocol under `--strict`:** measure-first (§3).
- **The typing census:** not runnable here (§6).

## 10. Skeptic verification

| claim | verdict | correction applied |
|---|---|---|
| F10.3's per-site ratchet counts a cross-file move as added | confirmed | counts 124 / 9 / 115 (today) and 158 / 149 (prototype); the carry is narrowed to removed-from and added-to files and the same scope; #1748 filed |
| the core is self-contained | confirmed | `self.model` in 16 of 19; `_LOGGER` added |
| the helper placement is cycle-free | confirmed | the `manual_plan` import is in the tests, not production |
| add `DhwPlan.requirement` | refuted | tuple return (§3) |
| the `TYPE_CHECKING` import of `_Horizon` | refuted: new equivalent GUARD_OFF | a Protocol (§3) |
| the `_co_optimize` hazard is benign | refuted: real defect | #1747, R9-EG-B8 |
| last-writer-wins: no golden mismatch | refuted (arrays differ; outputs do not) | §9 |
| 7 ledger rows | refuted: 9 | §6 |
| test counts | confirmed; two gaps | the 14-key pin and the legionella-step spy (§5) |
| `classes_over_300` is the only key that moves; B5a gives -2 / -1 | confirmed | — |
| F2.4 may edit `init_base` | speculative | dropped; F2.4 collides with B5a only |
| "must pickle" | moot | dropped |

## 11. Roster changes

- **New R9-EG-B8** (#1747), after R9-F2.4.
- **New R9-EG-B5a** (#1743, part of), after R9-F2.4 and R9-F10.4.
- **R9-EG-B5:**
  - after R9-EG-B5a, R9-EG-B8, R9-F1.10 and R9-F10.4;
  - `owner_gate` records tvofi's opt-in and keeps the `classes_over_300` confirmation;
  - the brief follows this spec.
- **R9-EG-B1:** gains R9-EG-B5.
- **R9-F10.3:** gains the #1748 carry, and #1748 joins its `issues`. The in-tree `carry-1646.json` is
  drafted.
