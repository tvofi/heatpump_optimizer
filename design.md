# Design: R11-OWNER-FEATURES-SPLIT

Base and code read at `origin/main` ef797d794017c98f7fb2d8a168d7de63d435ef3b (no predecessor; `after` is empty). Brief: `dev/programme/rosters/wave-r11-groups.json` at 97f98df563830e77a4849219f67e866bca18b02c. Owner order: no finder harness, owner report (designer.md). Owning seam: tests/features.py alone; its readers (`tests/run.sh`, `tests/closures.json`, `tests/case_closures.json`, `tests/mutation_table.py` through the ledger, `tools/ci/shards.py`, `.github/workflows/nightly.yml`) only name it. One owner, so no design stop.

## 1. Seam partition (measured at ef797d79)

Unit of the partition: a **section**, every top-level statement from one column-0 `R.section(` call to the next (252 at base; preamble = lines 1-212). The **rule**, applied to every section with no hand placement: the section's seam is the seam holding the most distinct production modules the section references, with `const`, `coordinator` and `__init__` excluded; a tie goes to the seam listed first; a section referencing only those three goes to `cycle`. Module-to-seam table, complete over `custom_components/heatpump_optimizer/*.py`:

- **inputs**: inputs pump_signals pump_mode running_signal flow_meter heat_energy open_meteo external_heat setpoint_check rooms room_history room_record
- **model**: thermal_model sysid accuracy comfort_learning curve_learning dhw_learning defrost learner_progress learning_freeze slab_seed drift flow_lift heat_curve presets batchmath
- **plan**: optimizer tariff price_model price_tiles pv battery grid_fee currency solve_gate plan_slots plan_step whatif early_cutoff comfort_band comfort_floor quiet_windows silent_mode freq_control duty_ledger duty_legs duty_switch wear runs driving_grade process_worker
- **dhw**: dhw_planner dhw_schedule dhw_draws dhw_start disinfection legionella draw_range wood_fuel circulation
- **actuation**: pump_arbiter mixing_valve supply_hold flow_limit power_guard boost away off_restore number_restore slot_drivers pump_schedule manual_plan climate switch datetime
- **surface**: every other module (config_flow entry_config quick_setup topology the prefill trio name_match the entity platforms payload frontend diagnostics diagnosis debugger narrative notifier repairs issues services store snapshots ledger log_latch replay_doc)

A module the table does not name is a refusal of the splitter, not a default. Each seam becomes the script `tests/features_<seam>.py` in source order. Counts are static `R.check` call sites (5737; the run prints `ALL 6272 FEATURE CHECKS PASSED` because loops multiply checks; the fixer reads per-part runtime counts from each part's own run) and D5 units are `text_ledger.units_of(path, text, "D5")`, the counter `check_scopes.py blob_units` calls:

| part | sections | static checks | LOC | D5 units |
|---|---|---|---|---|
| model | 91 | 1885 | 31363 | 1266 |
| plan | 46 | 1122 | 21914 | 884 |
| inputs | 37 | 943 | 14902 | 555 |
| surface | 22 | 852 | 17300 | 683 |
| actuation | 15 | 527 | 10058 | 428 |
| cycle | 31 | 259 | 4950 | 223 |
| dhw | 10 | 148 | 2429 | 99 |
| preamble + between-section comments | - | 1 | - | 11 + 154 |

Sum 4303 = `blob_units` of tests/features.py at base. The 154 are the comment blocks between sections; each travels with the section below it. Every seam spans nearly the whole file (interleaved), so a part is a gather, never a line range.

**Shared helpers.** 108 def/class names are used across seams (237 edges; hubs `_t2_coord` 7 seams, `_Coord`, `_t6_call`, `run` 5 each, `_solve_coord` 4). The rule: a name used in a seam other than its definer's moves, with the transitive closure of top-level names it loads, to one helper module `tests/features_shared.py`, which runs no check. If that closure holds an executed statement other than a definition or import (a check, a patch, a solve), the user section joins the definer's seam instead, and the splitter prints the join.

**D5 scopes.** `dev/audit/config/scopes.json` seat s7's glob `tests/fe*` would still gather every part (4303 of `max_units` 4500). The split re-cuts it: s7 keeps model, dhw, cycle and the helper module (1266+99+223+the helper's share of the 165); s2, at 76 units, takes plan, surface, inputs and actuation (2550). `python3 tools/audit/check_scopes.py --repo . --ref HEAD` must print `ok D5` at the head.

## 2. Migration of generated artifacts (each by script, none by hand)

The splitter is one committed instrument under `dev/audit/harnesses/` (called the splitter below; its closure-or-INERT classification is the fixer's step), deterministic from a features.py text: given the same text it writes the same parts byte for byte. Steps, in order:

1. The splitter's write mode on tests/features.py: writes the seven parts and the helper module, deletes tests/features.py, prints the per-part table above.
2. **Names**: every runner that executes features.py is rewritten to run the parts: `tests/run.sh` line 580 lane; `.github/workflows/nightly.yml` line 543 (the Asia/Kolkata step), which puts `.github/` in the diff, so the push to main runs `full`; the shard table in `tools/ci/shards.py` line 93; the `NOT_A_TEST` set in `tests/closure.py` gains the helper module, as do the helper exclusions in `tests/run.sh` (the `harness.py|profiles.py|worker_deadlines.py` case) and `tests/derive_closures.sh`. Prose references (`git grep -n 'features\.py' -- ':!dev/audit/rounds' ':!tests/mutation_ledger'`) are rewritten only where they name a runner or a fixture string a test reads: `tests/entities.py` census rows near line 4396, `tests/case_closures.json`, the detector string in `dev/audit/config/bugclasses.json`, the `tests/dst_checks.py` and `tests/worker_deadlines.py` headers.
3. **Closures**: `./tests/derive_closures.sh --single tests/features_<seam>.py` for each part, then drop the tests/features.py key and its `recorded` row (`tests/closure.py merge`). Each new script is a test in a measured closure; the helper module is a read path inside them, like `tests/harness.py`. Nothing goes on `INERT`. `tests/entities.py`'s orphan check must print no FULL-suite line.
4. **Mutation ledger**: 4313 of 6137 rows under `tests/mutation_ledger/killed_by` name tests/features.py. `killed_by` is script-granular, and a kill is `failing_count(run) > failing_count(baseline)` over the whole script (`mutation_table.py killed`). Re-key in two passes. (a) Reach: one traced baseline per part (`mutation_table.py`'s `traced_baseline`); a row whose mutated line exactly one part executes gets that part; the rest take the cost-first reaching part as a candidate. (b) Drive: every re-keyed row is driven against its part with baselines taken once per part; `--anchor` alone re-takes the baseline per call, so the fixer adds a batched anchors-file mode to `tests/mutation_table.py` with its self-test, or shards `--anchor` over CI. A row its candidate does not kill is driven against the other reaching parts; a row no part kills is the null control failing, not a survivor to re-triage. The edit rewrites only `killed_by` and appends to `reason`; no row is added or deleted.
5. **Budgets**: no `tests/structure_budgets.json` metric reads tests/ (structure.py scans the package), and `tests/mutation_budgets.json` holds only survivor fractions, which do not move while the killed set is identical. `tests/ci_budgets.json` does grow: `script_runs_per_push` (56) and `script_runs_full_case_pr` (68) count every script once per instrument, so seven scripts for one add six per instrument (the R11-SEAM-tests precedent: one new script took 54 to 56). This is a raise under CLAUDE.md rule 2: **the fixer asks the owner before pushing**, with the payment tried (fewer parts) and its cost (more shared end-of-file appends); no mandate is assumed.

## 3. Null control (both directions, both commands)

- **Test ids**: `PYTHONPATH=tests/hastub python3 tests/features.py | grep -E '^  (ok  |FAIL) ' | sort > before.txt` at base; at the head, the same over `for f in tests/features_*.py; do ...; done` into after.txt; `diff before.txt after.txt` prints nothing, every part prints `ALL N ... PASSED` and the N sum to the base's 6272 (re-measure at the merge base). Perturbation: drop one section from the splitter's output; the diff must print its lines.
- **Pins and kills**: `git diff --name-status $(git merge-base origin/main HEAD)...HEAD -- tests/mutation_ledger` lists only `M`; the same diff filtered `grep '^[-+] ' | grep -v -e '"killed_by"' -e '"reason"'` prints nothing; `grep -rho '"killed_by": *"[^"]*"' tests/mutation_ledger/killed_by | sort | uniq -c` gives the features parts summing to 4313 and every other script's count unchanged; step 4(b)'s drive reports every row killed by its recorded part. Perturbation: re-key one row to a part that never reaches its line; the drive must report it not killed.

## 4. Order and conflict plan

At base 18 of 20 open pull requests edit tests/features.py (`git diff --numstat $(git merge-base origin/main refs/pr/N) refs/pr/N -- tests/features.py` over `list_pull_requests` state open), from 14 to 2307 added lines. The split must not hand each of them a hand merge.

1. The fixer lands the instrument, its tests and the budget question first, then regenerates the split on the newest main immediately before handoff; the orchestrator holds merges touching tests/features.py from the split's final regenerate to its merge (one gate run), and the split merges on the critical path, ahead of the late-round groups.
2. **Port, by the same script**: an open branch merges main's last pre-split commit (old layout, ordinary conflicts it already owns), then the splitter's port mode merges the split commit by regenerating the parts from the branch's own features.py. Because the splitter is deterministic, the branch's parts differ from main's only by its own hunks, which land in the part the rule assigns; a new section the branch appended is classified by the same rule. Its ledger rows naming tests/features.py are re-keyed by step 4. No branch resolves a features.py conflict by hand.
3. After the merge a new test goes into the part the rule names (the splitter's classify mode on the section). End-of-file collisions remain possible within one part; seven ends in place of one is the reduction, not elimination.

## Alternatives

- **Split by line range or by size**: meets the D5 cap but gives a new test no deterministic home, so appends still meet at one end; refused by the brief ("by feature seam, not by size").
- **Split by title tag** (round or issue): titles lead with a round or issue tag (`v` 46, `R10` 18, `W` 18, `R9` 14 sections), so every pull request of a round appends to that round's one file: the conflict is unchanged.
- **A union merge driver on features.py**: no D5 relief, and silently keeps both sides of a non-append edit.

## Notes for the fixer

- Column-0 patches of imported modules assigned once and never textually restored number 53 by a first ast pass and 56 by the partition pass (the difference is unreconciled; the fixer re-derives it) (e.g. `_optmod._multi_start_minimize` set in a model section and read later by surface and plan sections). In separate processes a later part no longer sees them: a check may fail, or pass for a different reason. The test-id diff catches the first case and the mutation drive the second; neither may be waived. Carry: R11-OWNER-FEATURES-SPLIT
- 72 of the 143 multi-seam sections are exact ties decided by seam order; the rule is still deterministic, but a reviewer reading a part's theme will see them. The splitter prints each tie. Carry: R11-OWNER-FEATURES-SPLIT
- At base, D5 seats s6 (4187) and s8 (4042) are also near `max_units`; outside this order. Carry: dismissed: under the cap at base, outside the owner's order
