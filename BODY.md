Why this change, and what it measures.

The R10-N-log-flood barrier (`tests/entities.py` `_R10_LOG_ALLOWED_BY_REASON`) carried eight unlatched WARNING/ERROR sites under "OWED", each reached every cycle or solve and triggered by a persisting condition. This PR latches each through the existing transition latch, moved from `coordinator.py` to a new leaf module `log_latch.py` so the pump arbiter and the input reader can import it without closing an import cycle, demotes the optimizer's three redundant per-solve reports to DEBUG, deletes each OWED entry, and adds the owed runtime probe arms.

- `coordinator._apply_action` (stale-plan hold), `_command_valve_target` (three sites), `_note_solve_failure`, `pump_arbiter._space_target` and `inputs._age_gate` route through `log_latch._log_held`.
- The latch owner is whatever outlives the call: the coordinator for its own sites, and `hass` for the arbiter and the reader. `ArbiterInputs` is rebuilt every pass and `InputReader` every read, so a latch keyed on either would warn every time; `hass` is stable per install, exactly as the outage latches are (`_space_target` reads `inp.hass`, `_age_gate` reads `self.hass`). Round 2 corrected the first head here: it threaded the coordinator into `_space_target` for this owner, which charged that function's logic statements to `coord_footprint` and reddened `arch-score`; `hass` was already a field of the snapshot, so the function keeps its signature.
- `optimizer.optimize` / `_solve_space` / `_optimize_space_only` are demoted to DEBUG: a failed solve already surfaces once through the coordinator's latched `_note_solve_failure` (the `failed (...)` status), and a released manual plan through its `manual_plan_released` notification. The optimizer cannot latch on the coordinator -- it runs in a worker process with a fresh optimizer per solve -- and importing `coordinator` would add HA glue to the pure solver (fixer.md step 17), so the duplicate is dropped to DEBUG rather than latched in place.
- The five killed-pin rows move with the function to `mutation_ledger/killed_by/log_latch.py/`, keeping the digest each row's mutant line carries (`mutation_table.py --normalize` wrote them in canonical form).
- Round 2 follows the new leaf through the tree's counts: the selection-cost note (`tests/deployment_shape.py`, #1218), the D6 module census (`dev/audit/rounds/round4/D6/`, 77 -> 78), the `#2226` probe in `tests/features.py` (its log handler is now rooted at the package, so the latch's child logger is read), and `class_excess_loc` (recorded 18468 -> 18459 in its own commit).

## Head

fc9d9186dfd9195992bd87a83dc5eb543e509cf8

## Mutation proof

Revert the latch in `coordinator._note_solve_failure` to a bare `_LOGGER.error`, and the barrier's enumerator reopens the seam (the OWED entry is gone, so the site would be refused):

```
PYTHONPATH=tests/hastub python3 - <<'PY'
import ast, re
from collections import Counter
from pathlib import Path
def unlatched(sources):
    found = Counter()
    for name, source in sources.items():
        tree = ast.parse(source)
        def walk(node, chain, fn):
            for child in ast.iter_child_nodes(node):
                inner = child if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) else fn
                if (isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute)
                        and child.func.attr in ('warning','error')
                        and ast.unparse(child.func.value) == '_LOGGER'):
                    latched = False
                    for test in chain:
                        text = ast.unparse(test.test)
                        if re.compile(r'(warn|logged|report|latch|announc|_failed|notified|seen)', re.I).search(text) or (
                                isinstance(test.test, ast.Compare) and any(isinstance(o, ast.NotIn) for o in test.test.ops)
                                and f'{ast.unparse(test.test.comparators[0])}.add(' in ast.unparse(fn)):
                            latched = True
                    if not latched:
                        found[(name, fn.name if fn else '<module>')] += 1
                walk(child, chain + [child] if isinstance(child, ast.If) else chain, inner)
        walk(tree, [], None)
    return found
pkg = Path('custom_components/heatpump_optimizer')
src = {p.name: p.read_text() for p in sorted(pkg.glob('*.py'))}
mut = dict(src)
mut['coordinator.py'] = mut['coordinator.py'].replace(
    '_log_held(coord, "solve_failure", True, "Optimization failed: %s", err)',
    '_LOGGER.error("Optimization failed: %s", err, exc_info=True)')
print('FIXED  _note_solve_failure unlatched:', unlatched(src).get(('coordinator.py','_note_solve_failure'), 0))
print('MUTANT _note_solve_failure unlatched:', unlatched(mut).get(('coordinator.py','_note_solve_failure'), 0))
PY
```
FIXED  _note_solve_failure unlatched: 0
MUTANT _note_solve_failure unlatched: 1

## Null control

The unmodified tree at `origin/main` (`81b7aa9ff976413ec98592045930647c0e0bac73`, the base the gate merges) reads the eight OWED sites as seams; the barrier's own planted latched fixture is not a site, and the runtime probe's `control` arm reads `floods=0`.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/structure.py` — STRUCTURE RATCHET PASSED; every row `ok`, including `import_cycle_modules 0 <= 0`, `max_class_loc 8635 <= 8635`, `seam_cut_total 752 <= 752`; after recording `class_excess_loc 18468 -> 18459` (`coordinator_private_reach` and `seam_cut_total` flat).
- `PYTHONPATH=tests/hastub python3 tests/entities.py` — `ALL 2346 ENTITY CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/features.py` — `ALL 4152 FEATURE CHECKS PASSED`, including both `#2226` arms (the transition probe and the four-cycle flood count).
- `PYTHONPATH=tests/hastub python3 tests/arch_score.py` — `ALL 204 ARCHITECTURE SCORE CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/solar_alignment.py` — `ALL SOLAR ALIGNMENT CHECKS PASSED` (it is the driver the re-keyed `log_latch` pins name).
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` — `arch_modules_on_disk=78`, `arch_map_listed=78`, and the run leaves `claims.json`/`claims.md` byte-identical (`git status --porcelain dev/audit/rounds/round4/D6` empty).
- `python3 -I tools/audit/archscore/gate.py --base 81b7aa9ff976413ec98592045930647c0e0bac73 --head fc9d9186dfd9195992bd87a83dc5eb543e509cf8 --body <this body>` — `Architecture score: dS +0.0000 NULL`, `PASS: no gate metric rose`.
- `python3 dev/audit/rounds/round10/D14/log_flood/enumerate.py custom_components/heatpump_optimizer` — `sites=70 latched=6 seams=64` at the head; the same command over `git archive 81b7aa9ff976413ec98592045930647c0e0bac73` prints `sites=80 latched=6 seams=74` and lists `_apply_action`, `_command_valve_target` (3), `_note_solve_failure`, `_space_target`, `_age_gate`, `optimize`, `_solve_space`, `_optimize_space_only` as SEAM. The 64 returning seams are the class's pre-existing dispositions in `dev/audit/rounds/round10/sweep-N-log-flood.md`; the eight above are closed in this diff.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/log_flood/probe.py` — every arm reads `floods=0`: `control`, `no_weather_entity`, `weather_fetch_fails`, `open_meteo_no_coord`, `open_meteo_bad_coord`, `no_prices`, `bad_peak_months`, `bad_peak_hours`, `solve_failure`, `stale_plan`, `valve_mistyped`, `space_target_misdeclared`, `future_stamp`.
- `python3 tests/mutation_table.py --scope changed --base origin/main --max 0 --jobs 1` — `4343 unpinned site(s) of 6128 candidate sites, 4343 at the ratchet base 81b7aa9ff976413ec98592045930647c0e0bac73; the ledger agrees with the deterministic inventory` and `MUTATION TABLE PASSED` (the prechecks; the mutant pool itself is CI's `mutation` job).
- `node tools/policy/policy_lint.mjs --pr-body <this body> --head fc9d9186dfd9195992bd87a83dc5eb543e509cf8 --title "record(mutation): re-key _log_held's killed pins to log_latch.py" --author app/hpo-author --paths-file <git diff --name-only 81b7aa9ff...HEAD> --existing-file <git diff --name-only --diff-filter=a 81b7aa9ff...HEAD> --red arch-score --red "fast (3.14)" --red mutation --red pr-contract` — `PR-BODY: 0 error(s)` (no token here, so its red-history walk skips rather than reads: `--red` names each check this handoff answers).

## Red checks

- `arch-score` — red at `83bf0770c`: `coord_footprint 2547 -> 2552` (dS -0.0028). The first head threaded the coordinator through `pump_arbiter._space_target` only to give the latch an owner; `coord_footprint` charges every module-level function handed the coordinator, so that function's five logic statements arrived in the metric. Cheaper detector: the gate's own static vector, `python3 -I tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`, runs locally with no runner and no queue; measured standing cost 65 s on this seat. No cheaper check exists that is not that same computation, so the answer is the standing cost and the fix: the owner is `inp.hass`, already in the snapshot, and `_space_target` keeps its signature. The gate now reads `dS +0.0000 NULL`.
- `fast (3.14)` — red at `83bf0770c` on four scripts, every one a count the new leaf moved: `tests/entities.py` (the #1218 selection-cost note pinned 95 production files; `log_latch.py` makes 96, and its `mutation_table --anchor` arm drove the non-canonical ledger), `tests/features.py` (the `#2226` probe attached its log handler to the coordinator module's logger, so the latch's child logger went unread and it counted zero floods), `tests/structure.py` (`class_excess_loc 18468 -> 18459` was an unrecorded improvement), and `tests/harness_headers.py` (the D6 census header said 77 modules; the executed harness printed 78 and rewrote `claims.json`/`claims.md`). Cheaper detector: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`, the scoped gate, selects and runs exactly these scripts locally (its `MODE: SCOPED` line names the set); its standing cost is the scripts' own minutes, and the machine's gate lease serialises `stress.py`. The counts are self-invalidating figures about the tree that carries them, and each owning check already refuses a stale one -- none was missing, they were not run at the pushed head. The countermeasure is the scoped gate run this round, not a new check.
- `mutation` — red at `83bf0770c`: `MUTATION TABLE REFUSED -- the ledger is not in canonical form`, on the five re-keyed `log_latch.py` rows. The rows were written by hand (one-space JSON indentation); `row_text` writes two-space, sorted keys. Cheaper detector: that refusal is the first seconds of `python3 tests/mutation_table.py` itself, the command CI runs, and no baseline is paid before it -- the local run reaches it in 35 s including the whole-tree inventory. Countermeasure taken: `python3 tests/mutation_table.py --normalize` rewrote the rows to canonical bytes; the same command now reports the ledger agrees with the deterministic inventory.
- `pr-contract` — red at `83bf0770c`: `red-history` derives every failure conclusion across the branch's committed heads and refuses a body whose `## Red checks` does not name each (it named only an unrelated `gate_lock` flake). Cheaper detector: `tools/pr/prepr.sh` step 7c passes every red the pushed commits carry to the same `policy_lint.mjs --pr-body`, so the omission is refused locally; the body-check portion is seconds. Its standing limit is stated in the script: it reads pushed commits only, so the first handoff push cannot see its own reds -- this body names them, and re-running prepr after the reds appear is the answer, not a new check.

## Forward-carry

none

## Friction

none
