The v7.0.2 stamp preparation. Two edits, neither touching production code: `tests/stress_budgets.json` loses the `coverage_floor_override` that R10-PUMP-MODEL-D2 (#2368) left behind, and the `_rca/R10-N-structure-blind` ledger row names the pull request that landed the structure-blind arm. The measurement below is the one the stamp owes: the override lowered the solver-work floor to 18 and the production-call floor to 6 for one branch's diff, and nothing expired it at merge, so every later branch inherited them. The stamp-time items R10-STAMP's roster entry carries from #2445 (the flat-price control ruling and the architecture invariant for the release notes; a measured Pi `process_time` after the stamp) remain in that roster entry and are untouched here.

## Head

478cc27efd03d59d97899cff0d67f2e912ce7918

## Mutation proof

The diff changes no production line, so there is no production line to delete; the mutable artifact is the budget file and the instrument that grades it is `tools/policy/budget_raise_gate.py`. Its self-test holds the pair that separates the two directions:

    $ python3 -I tools/policy/budget_raise_gate.py --self-test | grep override
      ok   stress: the override withdrawn is routine (the literal is stricter)
      ok   stress: an override granted is a raise
      ok   stress: the override lowered is a raise
    budget_raise_gate self-test: 239 checks, 0 failed

Re-adding the override is the mutant and the gate calls it a raise; the committed head removes it and the gate reports zero raises (Figures). The floor instrument reads the same mutation from the other side: `coverage_floors` returns `(18, 6, <cites>)` with the override present and `(40, 15, None)` without it.

## Null control

The unmodified tree — `origin/main` b701723895a1 plus the ledger edit only, head f9bc8028e — run through `python3 tests/stress.py` covers 54 of 54 sweep scenarios and 20 of 20 production-call families against the override's floors (18 and 6). The committed tree, with the override removed, covers the same 54 and 20 against the literal floors (40 and 15). Coverage does not move because this diff changes no production code: the baseline is captured from `origin/main` in the same run and reports `re-planned: []` at both heads. The check that grades coverage is not vacuous: a run whose baseline is refused (HEAD equal to the reference) reds it with `only 0 of 54 scenarios are judged, against a floor of 18`, and the harness's own arms include a planted 2x regression, so a real coverage loss is seen.

The re-check at this head re-derives the floors on the tree the pull request now carries (including #2465): the sweep still holds 54 scenarios and 20 family members and the committed table returns `(40, 15)`, unchanged; the fix review's own re-measurement at this head returned 54/20 as well. The stress script itself is CI's at this head (Red checks).

## Figures

- Stress floors, before (override present), head f9bc8028e09ae5a1572e4da03edfb0878f3e9671, `origin/main` b701723895a1, measured 2026-10-20T10:38Z. Command `PYTHONPATH=tests/hastub GOLDEN_REF=origin/main python3 tests/stress.py`:
  - `solver-work baseline: 54 scenarios from origin/main (b701723895a1), captured in 300 s`
  - `production calls: 20 of 20 family members judged against origin/main (b701723895a1) in 68 s; re-planned: []; new on this branch: []`
  - `whole-solve CPU: median 0.928x of the baseline beside this run over 54 of 54 covered scenarios`
  - `ok   the production-call check covers at least 6 of 20 families`
  - `ok   the solver-work check still covers most of the sweep`
  - floors from the instrument, `PYTHONPATH=tests/hastub python3 -c 'import sys; sys.path.insert(0,"tests"); import stress; print(stress.coverage_floors(stress.load_budget_table(), 20, 54))'` -> `(18, 6, '#201 comment 6240984157 (D2-s2-01 ruling, step 3, mandate 6175172275) ...')`
- Stress floors, after (override removed), head 8947ee76036c2ba75d3377925123ff9bb74852fc, `origin/main` b701723895a1, measured 2026-10-20T10:58Z. Same stress command:
  - `solver-work baseline: 54 scenarios from origin/main (b701723895a1), captured in 282 s`
  - `production calls: 20 of 20 family members judged against origin/main (b701723895a1) in 133 s; re-planned: []; new on this branch: []`
  - `whole-solve CPU: median 0.985x of the baseline beside this run over 54 of 54 covered scenarios`
  - `ok   the production-call check covers at least 15 of 20 families`
  - `ok   the solver-work check still covers most of the sweep`
  - floors from the instrument, `PYTHONPATH=tests/hastub python3 -c 'import sys; sys.path.insert(0,"tests"); import stress; print(stress.coverage_floors({}, 20, 54))'` -> `(40, 15, None)`; `stress.SCENARIO_WORK_MIN_COVERED` is 40
- Floor re-derivation at this head (478cc27e, `origin/main` 76bb4562), command `PYTHONPATH=tests/hastub python3 -c 'import sys; sys.path.insert(0,"tests"); import stress; c=stress.sweep_combinations(); t=stress.load_budget_table(); p=stress.calls_population(c,t); print(len(c), len(p), stress.coverage_floors(t,len(p),len(c))[:2])'` -> `54 20 (40, 15)`. The fix review's stress re-measurement at this head returned 54 scenarios and 20 families as well.
- Budget gate, head 478cc27e, command `python3 -I tools/policy/budget_raise_gate.py --base origin/main --head HEAD --pr 0`:
  - `# merge base 76bb45628745, head HEAD: 7 budget file(s): ... tests/stress_budgets.json ...`
  - `RESULT budget_raises=0 count`
  - `PASS: no budget raise; no owner review is owed`
- Suspension notes, rule `tools/release/stamp.py`'s `restore_suspended` (`SUSPEND_HEAD_RE`, `SUSPEND_TAIL_RE`); only a suspension-note head contains ` suspends `:
  - `git show daca95c5d^:tests/golden/claimed_drift.txt | grep -c " suspends "` -> `19` (the entries v7.0.1's stamp restored, the positive control that the rule fires)
  - `git show HEAD:tests/golden/claimed_drift.txt | grep -c " suspends "` -> `0`
  - `git show HEAD:tests/golden/card_claimed_drift.txt | grep -c " suspends "` -> `0`
- Claim files: `git diff --stat origin/main -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt` -> empty; this branch claims nothing, so the stamp owes no restore here.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`
- Scoped gate at the fix head 8947ee760, `MODE: SCOPED -- 3 script(s) run, 30 scoped out` (`tests/entities.py`, `tests/harness_headers.py`, `tests/stress.py`). `tests/entities.py` -> `ALL 2358 ENTITY CHECKS PASSED`; `tests/closure.py selftest` -> `ALL 124 closure shrink pins PASSED`; `tests/layout.py` -> `layout self-test: ok`; `tests/env_drift.py --claims-only origin/main` -> `claims hygiene: origin/main ok`.

## Red checks

- `pr-contract` is red at both heads. `carry_audit.py check --body` returns `UNROUTED body item 522e1cd9 (## Forward-carry)` because that section began `none.` and then recorded items, a shape its grammar refuses. Answer: the cheaper detector is `carry_audit.py` itself — seconds, local, and already wired into `prepr.sh` — so it exists, was run, and is cheap; the section now reads a genuine `none.` and the #2445 stamp-time items live in the R10-STAMP roster entry (named in the opening paragraph).
- `tests/stress.py`: `shoulder: cheaper than holding the setpoint` (4.67 vs 3.96) is red at both the before and after heads on this arm64 box. `tests/stress.py`: `the probed scenarios' memory peaks stay within their recorded budgets` (`typical_slab/shoulder` attributable RSS 24.5 MiB against a recorded 9.4) is red in the after run only. Neither is this diff: the before head differs from `origin/main` only in the ledger scalar, the diff touches no production code, the memory pass reads only the recorded peaks (not `coverage_floors`), the economics check passed in the archived canonical-environment log `dev/archive/handoff/r9-f2-solver-4/ev/stress_base.log:101`, and `main`'s Tests push run at a25de7a68 concluded success. Both runs were taken on a box at load average 44-56 with two other seats building. The cheaper detector is CI's canonical-environment run, which already executes `stress.py`; the standing cost of a local duplicate is the 15-20 minutes per run this seat paid.
- `tests/harness_headers.py` was left unrun locally: it produced no output within 240 s under the same load. CI runs it on every push, so it is left to CI at this head rather than reported green.
- The scoped scripts and `structure.py` were green at the fix head; `structure.py` was re-run green at this head. The stress run and `harness_headers.py` are left to CI at this head.

## Forward-carry

none.

## Friction

none
