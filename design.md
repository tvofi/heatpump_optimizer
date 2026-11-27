# Design: R11-OWNER-FEATURES-SPLIT (revision 4)

Re-cut of revision 3 (b83de87857, approved d6eff4dca7) after the fixer's stop at section 4's report gate (`handoff-wip/r11-owner-features-split` 6d50d97e2a, BLOCKED.md: sampled re-key extrapolated to 2554253 CPU-s). Base and code read at e84856520dc4de8d70b68d67a206c6f2278351ad; no predecessor handoff. Owner order, no finder harness: owner report. Owning seam: tests/features.py. **Sections 0-3 and 5 and the Alternatives stand as revision 3 states them, with the design verdict's C1-C3 notes; this revision replaces section 4 and section 6 and adds to the Notes.** Orchestrator decision under mandate 6893738184 (15:56Z): the fork drive below is authorised at a hard cap of 150000 CPU-s, on seat hosts only.

**Spike** (never merges; local to the designer seat at `/tmp/hpo-design-features-split-out/spike/`, relayed by the orchestrator if the fixer needs it): `forkdrive.py`, `forkcost.py`, `plancost.py`, `floorcost.py`, `cfloor.py`, over revision 3's `swap_run.py`, `linereach.py` and `parts.json` (dab20b60ec). `## Figures` names the command behind every number.

## 4. Mutation re-key: the fork drive (replaces revision 3's section 4)

4314 rows name tests/features.py: 4132 on a line inside a function body, 181 on a module-level line, 1 reached by no span (`forkcost.py`). C1 holds throughout: a row is re-keyed only to a part whose own run, under the mutant, prints a `FAIL` or raises; a row with no such part is a lost kill, restored in its part (moved, copied or seeded check, verdict C1) and re-driven, never re-keyed blind.

**Why revision 3's drive cost what it did.** A row's plan is its reaching spans plus their `needs` closure, and the closure is nearly the script: median 196 of 252 spans (`plancost.py`). Driving a plan from a fresh process pays that prefix per row and per candidate part. The fork drive pays it once.

**Method.** One server process runs a script span by span, unmutated. Before span s it forks one child per row whose first reaching span is s (reach: `linereach.py record`, LINE events per span). The child:
1. drops the server's solve-worker handle (`_PROCESS_WORKER`, in the module and in every saved swap slot), so it spawns its own worker; without this the child blocks on the server's pipes (found by the spike);
2. replaces `__code__` on every live function (a `gc` scan by file and qualname) whose code the mutant changes, compiled from the mutated source; a changed free-variable set or no live function refuses the row (file-edit drive, below);
3. runs the remaining spans of the row's plan in source order and stops at the first failed check or raised span, attributed by span to its part; the server's own run is the unmutated baseline and must print no `FAIL`.

The prefix before s ran unmutated, which is exact: no span before s executes the mutated line.

**Phase F (find), on the P0-edited monolith under `swap_run.Swapper`** (section 1's swap run, each part on its own state copy): one child per row covers every part at once, so revision 3's candidates-per-row (2.15 measured by the fixer) is never paid; the first `FAIL` names the candidate part. Phase F writes nothing to the ledger.
**Phase C (confirm, the C1 evidence), on the written parts:** one server per part; each row forks in its phase-F part's server at its first reaching span in that part (the parts' own LINE record), fail-fast. Killed: re-key to that part. Not killed: the row's other reaching parts the same way, cheapest first; none: lost kill, as above.

**Module-level rows (181, almost all `CONST`).** The mutated line runs at import, so no fork point shares a prefix. They are driven in phase C only, by a file-edit drive per part (the mutant written into a per-worker git worktree, never a `.git`-less copy, which fails the `recorded_at` check: fixer's baselines.out), `case_select run <part>` with fail-fast, reaching parts cheapest first. The spike's in-process import hook for these rows did not apply its mutant (two `CONST` rows ran the whole script unkilled at identical CPU-s), so it is not used. **They run last**, after every function-body row, and they keep their current key only until driven; nothing is pushed while any row still names tests/features.py, because that key would name a deleted script (the unpinned-site count `tests/mutation_budgets.json` ratchets grows).

**Measured cost** at the base, plan-mode fork drive, 65-row seeded sample (the fixer's 25 plus 40 drawn with seed 27), 6 children on an 8-core host:
- two rows killed, at 7.9 CPU-s (`dhw_schedule.py:_parse_time CMP_BOUND a387ecf9`, same part and span as the fixer's file-edit drive) and 300.9 (`inputs.py:setpoint_and_unit GUARD_OFF 5cd1f888`); two more were past 365.8 and 345.1 when the run was stopped;
- these four are the stratum of 340 function-body rows whose first reaching span is span 2 or earlier: 340 × 254.9 = 86.7k;
- every other row priced at its first reaching span's recorded seconds (the floor; a kill cannot come sooner): 37367 for phase F (`floorcost.py`), and 20060 for phase C at each row's cheapest reaching part (`cfloor.py`);
- **projected total 144k** with those floors as recorded, **111k** with the floors scaled by the one checked kill (7.9 CPU-s measured against 18.7 s recorded). Child CPU only; solve workers added 0-185 CPU-s per child and servers about 1000 CPU-s per pass, both inside the cap below.

**Cap and stop rule.** Hard cap 150000 CPU-s, child plus solve-worker CPU (`wait4` and `RUSAGE_CHILDREN`) plus servers, summed across hosts in the drive's ledger. Seat hosts only (local or cloud seats), never CI runners. Sharding: `--shard K/N` over rows, each shard one server per pass, N chosen so no host exceeds its own seat cap. Order: phase F over every function-body row; then phase C for those rows; then the module-level rows. **Sample first:** the first 200 seeded function-body rows and 20 seeded module-level rows are driven, then the total is extrapolated per kind; above 150000 the drive stops before the rest. **If the running total crosses 150000 at any point, every host stops at its current row, nothing more is re-keyed, and the fixer reports the total, the rows re-keyed and the rows left**; the branch is not pushed until the orchestrator rules.

**Perturbation and nulls.** Revision 3's planted cross-part pair (`planted/planted.py`: part X saves a function's value, part Y checks it): phase C in X must print not killed and the row is a lost kill. Null children patch nothing, at seeded spans, and must run to the end with no `FAIL`. The spike's one identity child ran 312 CPU-s with no `FAIL` before the server stopped, which is a partial null only. A refused patch, a refused fork (a non-main thread alive) and a changed free-variable set are each counted in the body.

## 6. Budgets (restated)

`tests/structure_budgets.json` and `tests/mutation_budgets.json` do not move. `tests/ci_budgets.json` counts each script once per lane in `closures` and `coverage`. At the base that is 35 + 21 = 56, which `tests/entities.py`'s every-script-once check derives, and tests/features.py is in both. Each added script adds 2 to each metric:

| parts | script_runs_per_push | script_runs_full_case_pr |
|---|---|---|
| base (1) | 56 | 68 |
| 7 (step A seams) | 68 | 80 |
| 2 | 58 | 70 |

Payments tried:
- **Fewer parts.** Each merged part pays 2 on each metric, down to 2 parts. That trades away the seam partition the owner's brief asks for ("by feature seam, not by size") and halves the append-conflict relief of aim 1. Aim 2 holds at any part count: D5 s7 holds 4304 units against the 4500 cap at the base.
- **Excluding parts from the coverage `fast` stage.** Refused: it loses per-script production coverage.
- **One runner script running all parts.** Refused: one process brings back the cross-part state the split removes.
- **Deleting or merging other scripts.** Refused: functionality deleted only to fit.

The architecture score's `dS` cannot be measured before the parts exist. The fixer runs `tools/audit/archscore/` before and after at the head and records the `Architecture score: dS` line in `## Raise justification`. The raise is asked before push (CLAUDE.md rule 2, 0013).

## Notes for the fixer

- Fork children must drop the inherited solve-worker handle, swap slots included, or they block on the server's pipes. Carry: R11-OWNER-FEATURES-SPLIT (item fork-worker)
- A `__code__` swap does not reach a generator or frame suspended in the old code, or a closure whose free variables change; refuse those rows to the file-edit drive. Carry: R11-OWNER-FEATURES-SPLIT (item fork-limits)
- Drive trees are git worktrees: a copy without `.git` fails the `recorded_at` check and reads as a kill. Carry: R11-OWNER-FEATURES-SPLIT (item drive-tree)
- LINE reach skips the header, so a row the header executes forks too late; record the header's reach and fork such rows before it. Carry: R11-OWNER-FEATURES-SPLIT (item header-reach)

## Figures

Run from the repository root at the base, `S` revision 3's spike, `F` this one, `PYTHONPATH=tests/hastub:tests SPIKE=$S`, `tests/features_p0.py` the base with `$S/p0.diff` applied:
- reach: `python3 $S/linereach.py record lines.json` (15m27s wall here)
- row kinds and no-fail-fast ceiling: `python3 $F/forkcost.py lines.json $S/parts.json tests/features_p0.py`
- plan sizes and plan ceiling (2413980): `python3 $F/plancost.py lines.json $S/parts.json tests/features_p0.py`
- floors (37367 for the other rows; 37379 for all): `python3 $F/floorcost.py ...`; phase C floor 20060: `python3 $F/cfloor.py ...`
- sample: `OPENBLAS_NUM_THREADS=1 PYTHONHASHSEED=0 python3 $F/forkdrive.py lines.json $S/parts.json tests/features_p0.py out.jsonl --rows rows65.txt --workers 6 --null 3 --seed 11 --plan --twin 4`
- early stratum (340): first reaching span index 2 or earlier among function-body rows, from `forkdrive.rows_for`
