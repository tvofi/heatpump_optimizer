`tests/stress.py`'s memory pass went red on main (`tests / fast (3.14)`, job 129554889319, main pushes 96346fdec3 and 3aac11dfba): typical_slab/shoulder traced 3.9 MiB against a 1.8 MiB record (x1.5 ceiling 2.73). In the same pass three of six probes read about 1.8 MiB above the others: 5.1 against 3.3. Not a memory regression, and not a budget to move. The cause is a measurement fault. Each probed solve interns three fresh strings. When a probe process's import fill leaves the interpreter's interned-string table fewer free slots than that, the solve rebuilds the table inside the traced window and is charged the whole new table: 1.83 MiB on CI, 3.67 MiB on the cloud seat's image. Where the fill lands moves by a few slots from one process to the next on an unchanged tree. On a tree that sits that close to the rebuild, the same scenario reads 2.1 MiB in one run and 3.9 MiB in the next. This is the class 17bb738485 (R10-HOTFIX-STRESS-MEM-PEAK) fixed one source of: per-call churn. That fix left the fill itself in charge.

The fix is a measurement fix (brief: prefer it to a budget move). Before tracemalloc starts, both `--memory-probe` and the empty probe `--memory-baseline` call `give_interned_table_headroom()`. It interns fresh strings until the rebuild is seen, dropping each one as soon as it is interned. A freed key leaves a dummy, so the slot stays spent and the memory is reused. The table is then freshly rebuilt with ~43,700 free slots against the solve's three. The empty probe pays the same step, so the transient table appears in both RSS watermarks.

A new pair of checks in the memory pass puts a probe on the edge every gate run. `intern_fill_readings` takes the cheapest probed scenario by recorded work ratio and fills its table to `INTERN_FILL_SHORT` (1) slot short of the rebuild. The slots are counted in a forked child that shares the probe's exact table. A second process cannot do this count: it lands its own fill 43669-43674 slots from the rebuild over ten processes, more than a solve consumes. The checks then require that:
- the filled probe reads within `INTERN_FILL_TOLERANCE_MIB` (0.5) of the clean probe;
- the same fill with the headroom step skipped (`--no-intern-headroom`) reads over `INTERN_REBUILD_STEP_BYTES` (512 KiB) above it. This is the check's own null control: it proves the fill lands.

No budget changes. `tests/stress_budgets.json` is untouched.

Alternatives and why each lost:
- **Re-record typical_slab/shoulder's `traced_peak_mb` upward.** This is a raise, and it measures the runner. It would also leave the three 5.1 MiB readings at 0.07 MiB under their 5.19 ceiling, and widen every traced budget by a table's size.
- **A warm-up solve before the traced one.** It doubles every probe's cost. It also leaves the trace at the mercy of any churn that reaches the rebuild.
- **Keep the headroom strings alive.** This was this branch's second commit, b0861c69b. It held ~11 MiB under the probe's RSS watermark: attributable read 0.7-0.9 MiB against 8.6-8.9 at the base, which blinded the RSS arm. 1b7a633a3 churns the strings instead.

## Head

c0c3609dbc647815fdbd809e61f5f192801fc580, merge base 9b1bb58db713a8a13148f98148fa8eb4fd796980 (origin/main at the time of measuring).

## Mutation proof

Deleted the probe's headroom call (the two lines `if "--no-intern-headroom" not in argv:` / `give_interned_table_headroom()` in `_memory_probe_main`). The check went red in 3 of 3 runs. `a probe's traced peak does not depend on where the runner's import fill left the interned-string table` read filled 6.96/6.97/6.96 MiB vs 3.30 clean (tolerance 0.5). The perturbation check stayed ok (bare 6.97/6.97/6.96). Restored. Driven through the check's own `intern_fill_readings` on typical_slab/winter, not by a full `stress.py` run per mutant (`fixer.md` step 5).

The failing-check-first commit a2a6cd9b4 carries the check before any fix. It used the first, two-process form of the fill and read red there: typical_slab/winter 6.97 MiB filled against 3.30 clean.

The empty probe's headroom call (`_memory_baseline_main`) is a value site with no gate check that reads it. In this repository's gate context every probe's attributable RSS reads 0.0 at both ends: the empty probe sits at 104.7 MiB at the base and 105.6 MiB at the head, and CI reads 117.2 MiB. Measured directly on three scenarios, deleting it reads attributable 10.3-10.7 MiB and keeping it reads 6.8-7.4, against 8.6 at the base. It is kept because the budget's rule is the probe minus everything the probe pays before build_case. The site is named here as unpinned.

## Null control

At the merge base, with the harness filling the table before the tree's own pre-trace steps: 1 slot short reads 5.72 MiB on typical_slab/shoulder; 50 slots short reads 2.05. At the head: 2.05 at 1 short, 2.04 at 50 short. Unperturbed, the base and the head read the same on all seven probed scenarios over five probes each (Figures). The fix changes no reading on a process whose fill is not at the edge.

## Figures

All measured on the cloud seat's image (venv-ci, Python 3.14.7, x86_64), base 9b1bb58db7 and head c0c3609db.

- CI's red pass: typical_slab/shoulder 3.9 MiB vs recorded 1.8; typical_slab/winter and winter_extreme/1z/dhw 5.1; heavy_old/shoulder, winter/cycle and winter/pv+cycle 3.3; empty probe 117.2 MiB, attributable 0.0 on all six. Source: `get_job_logs` job 129554889319, the `tests/stress.py` memory-pass lines.
- Edge perturbation, typical_slab/shoulder: base 5.72 (1 short), 2.05 (50 short); head 2.05 (1 short), 2.04 (50 short). Command: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_stress_intern_fill.py edge <tree> typical_slab/shoulder <short>`.
- Slots one untraced solve consumes: 3 on each of the seven probed scenarios (typical_slab/shoulder, heavy_old/shoulder, winter/cycle, winter/pv+cycle, typical_slab/winter, winter_extreme/1z/dhw, winter_extreme/2z/dhw), base. Command: `... r10_stress_intern_fill.py count <base> <label>`. Traced, filled 1/2/3 short, typical_slab/winter crossed in 9 of 9 forked runs; 4 or 6 short, in 0 of 4.
- Per-process spread of the fill: 43669-43674 interns to the rebuild over ten `--intern-count` processes of one tree; 43669-43673 over four with `PYTHONHASHSEED=0`. Measured with the two-process `--intern-count` of a2a6cd9b4 (`python3 tests/stress.py --memory-probe '{"season": "winter", "building": "typical_slab", "dhw": true}' --intern-count`, `PYTHONPATH=tests/hastub:custom_components`).
- Table step: 3.67 MiB on this image (`_intern_until_rebuild`'s jump); 1.83 MiB on CI (17bb738485's measurement; CI's 5.1 vs 3.3 here).
- Headroom step: 43,670 interns in 0.071 s; afterwards, the next rebuild came after 43,696 more interns. Command: `give_interned_table_headroom()` then `_intern_until_rebuild('next')`, in-process at the head.
- Repeated probes, 5 each, base vs head: typical_slab/shoulder 2.06-2.07 vs 2.06-2.07; heavy_old/shoulder 3.33 vs 3.33; winter/cycle 3.34-3.35 vs 3.34-3.35; winter/pv+cycle 3.34-3.35 vs 3.34-3.35; typical_slab/winter 3.30 vs 3.30; winter_extreme/1z/dhw 3.30 vs 3.30; winter_extreme/2z/dhw 3.34 vs 3.34 (MiB). Command: `... r10_stress_intern_fill.py probes <tree> 5 <seven labels>`.
- RSS arm, direct probes (not the gate context): empty probe 88.6 vs 92.2 MiB; attributable typical_slab/winter 8.5 vs 7.3, winter_extreme/1z/dhw 8.6 vs 7.0, heavy_old/shoulder 8.6 vs 7.2, typical_slab/shoulder 6.7 vs 5.7 (base vs head; records 13.7/11.7/12.7/9.4, so the head's readings are within 2.0x of each, under the 3.5x `SCENARIO_STALE_FACTOR`). Command: `... r10_stress_intern_fill.py rss <tree> typical_slab/winter winter_extreme/1z/dhw heavy_old/shoulder typical_slab/shoulder`.
- Scoped gate at 1b7a633a3 (the code of this head less one comment and the harness), `GATE_SCOPE=auto PYTHONPATH=tests/hastub bash tests/run.sh`: EXIT 0, `MODE: SCOPED -- 5 script(s) run`; `tests/stress.py` ok (327 s). Its memory pass: typical_slab/shoulder traced 2.1 MiB; fill check on winter_extreme/1z/dhw: 3.30 filled, 6.97 bare, 3.30 clean; both new checks `ok`. The same command at this head c0c3609db: EXIT 0, `MODE: SCOPED -- 5 script(s) run`; `tests/stress.py` ok (319 s), `tests/harness_headers.py` ok (163 s); typical_slab/shoulder traced 2.1 MiB; fill check 3.30 filled, 6.96 bare, 3.30 clean.
- The same `tests/stress.py` at the base, `PYTHONPATH=tests/hastub`: empty probe 104.7 MiB, attributable 0.0 on every probe. The RSS arm's blindness in the gate context predates this change.
- `dev/audit/rounds/round4/D9/h7_memory_gate.py` at both ends: identical RESULT lines, including `inject2x_traced_rule_fires=True`, `clean_traced_rule_fires=False` and `scenarios_where_2x_traced_fails=54`. A doubled peak still fails through the head's probe.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `python3 tools/audit/archscore/score.py --diff 9b1bb58db7`: `Architecture score: dS +0.0000 NULL`.
- Class seams: `git grep -n "tracemalloc.start" -- tests dev/audit`, each against its disposition.
  - `tests/stress.py` `_memory_probe_main`: closed in this diff.
  - `tests/stress.py` `_intern_until_rebuild`: the instrument itself.
  - `tests/replay.py` `run_fixture` (memory cycles): already safe, measured. Every memory cycle consumes 0 slots: synthetic-dhw-only 24 of 24 cycles at both ends; owner-2026-10-30-away 8 of 8 at the base. Base, filled to 1 slot short before every memory cycle, synthetic's max traced peak stays 1.89 MiB with 0 of 24 over 2.5. All of a replay run's ~14,440 slots are spent in cycle 0, which is untraced. Command: `... r10_stress_intern_fill.py replay <tree> tests/replay/<fixture>`.
  - `dev/audit/rounds/round4/D9/h7_memory_gate.py`, `dev/audit/rounds/round4/D9/d9_own_d9_06.py`: these drive stress's own `--memory-probe` (via `_run_memory_probe` or the CLI), so the fix closes them too.
  - `dev/audit/rounds/round3/D9/h3_memory.py`, `dev/audit/rounds/round4/D9/h4_retained.py`, `dev/audit/rounds/round4/D9/h8_leak_attrib.py`, `dev/audit/rounds/round4/D9/verify3_h7_mmap.py`, `dev/audit/rounds/round8/evidence/D9/s2_cycle.py`, `dev/audit/rounds/round10/D9/s2/retained.py`: frozen round evidence, not a gate (`tests/harness_headers.py`: "finder harnesses are FROZEN EVIDENCE"). Not touched.

## Red checks

none

## Forward-carry

none

## Friction

none
