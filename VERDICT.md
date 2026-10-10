Fix review: merge a9b1b48c493fef74247cfc81511de4956d2bac05

bus-nonce: b71d1c429f91fbab2a3eb62e2cff6c2e

# Fix review — PR #2070 (group R9-live-6), head a9b1b48c493fef74247cfc81511de4956d2bac05

Reviewer seat, detached worktree at the head, own harness. Nothing below is the
fixer's `tools/audit/seat/verify_eight.py`; that harness was not run.

This is my round-6 verdict, re-published as `merge` after the orchestrator pushed
the head I measured and re-cut the body (both were the only grounds of the
`head-moved` block this verdict replaces in `review/2070`'s history). No
measurement changed between the two verdicts: every figure below was taken at
`a9b1b48c…`, and it is now the live pull-request head.

## 1. The kill claims, re-taken by hand (step 1)

Instrument: `miniec.py`, in the evidence directory. It executes the **real bytes**
of `tests/features.py` — the module header, the `import asyncio as _asyncio` /
`_FakeEntry` / `HeatPumpOptimizerCoordinator as _Coord` imports, the pump-arbiter
preamble that defines `_PaNS`/`_PaCoord`/`_PA_TUYA`/`_PA_IDS`/`_pa_aio`, and then
the early cut-off block **verbatim** (50 checks, `R.close` 0 clean) — in a private
worktree at the head. (Same idea as `tools/audit/seat/features_block.py`, plus the
two helper segments that tool's header-only namespace lacks; that tool cannot run
this block alone, it raises `NameError: _PaCoord`.) Each mutant is
`mutation_table.py`'s own canonical `new` text, applied and then **reverted**, with
the clean re-run as the revert-to-green arm.

| site | mutant | verdict | the check that fires |
|---|---|---|---|
| `early_cutoff.py:293 GUARD_OFF` | `if inp.entry_released:` → `if False:` | **KILLED** | `a reading after the entry is released writes no cut` |
| `:266 CMP_BOUND` | `cycle_end - utc < MIN_OFF` → `<=` | **KILLED** | `the min_off guard is a strict < (a cycle exactly MIN_OFF away is not held)` |
| `:275 CMP_BOUND` | `lower_floor < limit - MARGIN_K` → `<=` | **KILLED** | `_second_zone_cold is False at the exact target-margin boundary (strict <)` |
| `:284 CMP_BOUND` (low) | `low <= room <= high` → `low < room <= high` | **KILLED** | `_reading accepts exactly the low plausible bound` |
| `:284 CMP_BOUND` (high) | `… low <= room < high` | **KILLED** | `a room reading exactly at the plausible-range high bound is accepted and cut` |
| `:201 GUARD_OFF` | `if unsub is not None:` → `if False:` | KILLED | `release unsubscribes the room listener and is idempotent` |
| `:215 GUARD_OFF` | `if inp.disinfecting:` → `if False:` | KILLED | `a disinfection hold is never cut, however warm the room` |
| `:259 GUARD_OFF` | switch-state guard → `if False:` | KILLED | `a cut is refused when the switch already reads off` |
| `:273 GUARD_OFF` | two-zone guard → `if False:` | KILLED | `past the plan's own pre-heat + margin it is cut` |
| `:275 RETURN_DEL` | `return …` → `pass` | KILLED | `a cold lower floor in a two-zone house is never cut` (+ the boundary check) |
| `:284 BOOLOP` | `and` → `or` in `_reading` | KILLED | `a room reading above the plausible range is never cut` |
| `:232 RETURN_DEL` | `return None` → `pass` | SURVIVES | — (the fixer's own triaged equivalent) |
| `:268 RETURN_DEL` | `return None` → `pass` | SURVIVES | — (the fixer's own triaged equivalent) |
| `:85 CONST` (control) | `MARGIN_K = 0.5` → `1.0` | KILLED | 8 checks (positive control) |

**Totals: 14 arms, 12 KILLED, 2 SURVIVES.** The two survivors are exactly the two
sites the fixer's own `survivor_triage` rows call equivalent — so the instrument
discriminates, and the "2 triaged equivalents" row of the body is corroborated.
**Every arm's revert re-runs to 0 FAIL.** Clean block: 0 FAIL.

### The `:293` check is a genuine kill, not a tautology
The mutant reddens `a reading after the entry is released writes no cut` and the
revert greens it. The check reaches the guard because it arms **first** (the room
listener registers) and only then sets `_entry_released = True`; under the mutant
the cut is written, so nothing upstream hides it. The fixer's account — that its
first version armed on an already-released entry, which bails inside `arm()` at
line 164 and hid the guard, so it changed the check — is consistent with what I
measure on the final check.

### The three exact-boundary CMPs drive production code, not a re-implemented formula
- `:266`: the check calls production `early_cutoff._cycle_guard` with a production
  `arbiter_inputs()` and a `CutoffState` whose `cycle_end` is exactly `now + MIN_OFF`;
  it asserts `is None`. Clean `None`, mutant `"min_off"`. The public room path cannot
  hit equality (arm/room clock skew), which the check's own comment states; nothing in
  the check restates `< MIN_OFF`.
- `:275`: the check calls production `_second_zone_cold` at `lower == limit - MARGIN_K`;
  clean `False`, mutant `True`. My `275 RETURN_DEL` arm shows the *behavioural* two-zone
  check (lower 18.0) does **not** separate the boundary, so the boundary CMP check is
  load-bearing rather than redundant.
- `:284` low bound: the check calls production `_reading` with a `FakeState("-30.0")`;
  clean `-30.0`, mutant `None`, and the check asserts the value. The low bound is
  observable only there because a below-target room never cuts. Both halves of the
  doubled CMP are separated (low by that check, high by the 60.0-reading check).

## 2. Reproduced vs cited — stated plainly
**Reproduced** (section 1): the four hand-taken sites and six more, all with revert
arms, in my own worktree, my own mutation, my own FAIL-set diff against my own clean
baseline.

**Cited, not reproduced:** the *full-file* claims. A clean `tests/features.py` run is
~3 h on this box (my clean run reached file line 12 785 of 61 823 in 37 min under load),
and my four full-file mutant arms hit a 3000 s timeout — that evidence is void and I do
not carry it. So I did **not** reproduce the full-file FAIL set, the `1 of 3980` count,
or the `R9-F2.1 P3`-only identity locally. For the P3 identity I cite CI's
`fast (3.14)` = success at the live head and the BLAS lane, per tvofi's standing
instruction that heavy scripts run in CI and seats cite check-runs. The block instrument
covers the checks these mutants can move; it would not see a kill from a check outside
the early cut-off section, and I note that limit rather than claim past it.

## 3. The `## Unpinned sites` census — re-derived, composition diffed (not just counted)
`PYTHONPATH=tests/hastub python3 tests/mutation_table.py --base origin/main` at the head:

    MUTATION TABLE REFUSED -- 4655 unpinned site(s) against 4617 at the ratchet base
    7cd5a588cbbbef354c00148040da2d720b8a888c, 38 of them added by this diff.

38 sites over 35 printed lines (three lines are `CMP_BOUND*2`). The body's round-5
`## Unpinned sites` lists 46 entries / **35 distinct `(file, line)` keys**. Diffing the
two key sets, not the counts: every head line maps onto a body key, and the 8 body-only
keys are exactly the sites already disposed in this diff — `139`/`190`/`217`/`288→289`/
coordinator`2416` (pinned: `killed_by`) plus `231→232`/`267→268` (the two triaged
equivalents). The residual count gap (38 vs 35) is `mutation_table.py`'s doubling rule
for a chained `low <= x <= high`, which the body lists once per line. **No composition
drift**; the count matches and so does the composition. (The refusal itself is expected:
`mutation-autofix` owns the pins, and `ci-autofix.md` names it as a repairing job.)

## 4. Step 13 — `merge-tree`
`git merge-tree --write-tree origin/main a9b1b48c…` → **rc=0**, one tree line
(`3ddcb01eec1696f48e76e1fc1efac4f58ec8689f`), no conflict surface, no `MERGE-CLAIM:` line.
`origin/main` (`7cd5a588c`) is an ancestor of the head, so the head already carries main.
For contrast, the head this PR carried before the push (`a9ba0b88…`) exits **1** and
conflicts on six non-claim paths.

## 5. Hygiene
- `VERSION` `6.7.17`, `manifest.json` version `6.7.17`, `RELEASE_NOTES.md` heading
  `## v6.7.17` — untouched by the diff.
- `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt` are
  **byte-identical** to `origin/main`.
- `python3 tests/structure.py` → **`STRUCTURE RATCHET PASSED`**, `max_class_loc 8811 <= 8811`,
  `seam_cut_total 762 <= 762`. The only `*_budgets.json` leaf that moved is
  `max_class_loc`, and it moved **down** (`8818 → 8811`); no leaf moved up.
- New tracked file `tools/audit/seat/verify_eight.py`: `tools/audit/` is on
  `tests/closure.py`'s `INERT` list, so it needs no closure entry, and it is a
  harness (it drives `tests/features.py` in throwaway worktrees) rather than a second
  implementation of the checks. The other new tracked files are classified —
  `dev/audit/harnesses/early_cutoff_closed_loop.py` is named in a recorded closure
  (added to `tests/closures.json` in this diff).
- **Window pins:** the diff adds no window-pin artefact; every added occurrence of
  "window" is prose (a docstring or a comment). I could not find a file, symbol or
  closure of that name in the tree and #2059's file list contains none, so I can
  confirm only that this diff introduces none — I am not carrying a "removed them"
  claim I could not re-derive.

## 6. Step 11 — the head's runs
At the reviewed head `a9b1b48c…` this run had no CI of its own at measurement time; the
runs that exist on the PR's earlier head (`a9ba0b88…`) are a **`workflow_dispatch`** run,
not a `pull_request` one: `mutation` = **failure**, everything else green
(`fast (3.14)` success, `closures` success, `typing` success, `hassfest` success,
`validate-hacs` success, `coverage` success). The `mutation` red is the census refusal
of section 3; the body answers it (`## Red checks`, naming the cheaper detector
`tests/mutation_table.py`), so the red-check trigger of `defect-root-cause.md` is
answered, not silent. Mechanism fact, not a defect in the authored work: those jobs are
gated `github.event_name == 'pull_request'`, so a hand-dispatched run skips
`mutation-pin-plan`/`mutation-pins`/`mutation-autofix` and leaves the refusal unrepaired.
The orchestrator owns the push-triggered run; I did not re-run the gate or the mutation
table (`fix-review.md` step 11).

## 7. Findings — resolved in this publication
- **F1 (head).** *Resolved.* The head this dispatch names is now the live pull-request
  head; my measurements apply to it unchanged (a SHA is content-addressed).
- **F2 (body).** *Resolved.* The body is replaced in the same push with the round-5 body
  naming `a9b1b48c4` (`## Head`, `## Unpinned sites` over all 35 sites, `## Mutation
  proof`); the round-2 body I reviewed is superseded. `fix-review.md` step 7 is met.
- Independently: the fix's own numbers are earned — `max_class_loc` moves down, the
  census composition is intact, and every kill claim I took reproduces with its revert.
