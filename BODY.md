R10-HOTFIX-STRESS-MEM-PEAK: `tests / fast (3.14)` failed `tests/stress.py`'s "the probed scenarios' memory peaks stay within their recorded budgets" on #3297. The cause is not #3297's diff and not the interpreter version. It is the BLAS thread pin in `optimizer._scoped_minimize`. That pin built a fresh `threadpoolctl.ThreadpoolController` on every minimize call, and the work each build did inside the solve forced CPython to rebuild its interpreter-wide interned-string table in one 1.83 MiB step. The memory probe's traced window charged that step to whichever scenario's solve crossed the rebuild point. This change builds one controller at import, and the probe now asserts its own precondition (no import inside the traced window). No budget is re-recorded: the record was right and the window was not.

## Head

17bb738485d01c7a1ed9c26319fcc22547c48294 (base bb7dfb9bd6; `git merge-tree --write-tree origin/main HEAD` clean against origin/main 8a4974d152 at 2026-11-08T15:59Z)

## Root cause

**Reproduction.** The red is CI job 128711769266, #3297 head 7fe24f9f61, CPython 3.14.10 on an AMD EPYC 7763. It traced heavy_old/shoulder and winter/pv+cycle at 5.3 MiB against a 3.46 record. A second run at the same SHA (job 128751219984, CPython 3.14.10 on a Xeon 8370C) traced those two at 3.5. On that run typical_slab/winter read 5.3 (record 3.4) and typical_slab/shoulder 4.0 (record 1.8). Same tree, different scenarios bumped, each bump about +1.8 to 2.2 MiB.

**Not the interpreter, not the hardware.**
- Main's own full runs on CPython 3.14.10 passed stress.py on every runner CPU class in the sample after #3274 merged, including 4fe7d5934b (#3297's main parent) on an EPYC 7763 and 72940b7954 on a Xeon 8370C.
- Locally on 3.14.7, stress.py's own `--memory-probe` at origin/main reads 3.47 on heavy_old/shoulder, winter/pv+cycle and winter/cycle (3 of 3 each). At the #3297 head it reads 5.31 on all three (2 of 2 each).
- On 3.12.14, origin/main reads 3.49 and 3.50.

**Mechanism.**
- On 3.14 a process's first `ThreadpoolController()` traces 199 KiB at main and 2076 KiB at #3297, after identical imports. Interning 100 throwaway strings before tracemalloc starts takes #3297's figure back to 199 KiB.
- The traced 1888 KiB sits in 93 blocks allocated under `marshal.loads` of a tiny stdlib module (`ctypes.macholib.dyld`, imported by `ctypes.util`). That is a global table being rebuilt at that moment, not the module.
- A churn harness (intern a fresh attribute name, then free it) shows the step directly: 1.83 MiB at intervals on both 3.14 and 3.12. With a constant name the peak is 0.002 MiB.
- So #3297 changed no solve. Its added strings moved the import-time table to just under a rebuild point, and the solve's own interning crossed it.

**What interns inside the solve.** `threadpool_limits(limits=1)` constructs `ThreadpoolController()` per call: 8 calls per typical_slab/shoulder solve, 10 per heavy_old/shoulder. On Linux (`_find_libraries_with_linux`, `/proc/self/maps`) each construction opens fresh `ctypes.CDLL` handles. Their symbol names are built at runtime (`f"{prefix}openblas_get_num_threads{suffix}"`, `_get_symbol`), interned by `CDLL.__getattr__`'s `setattr`, and freed with the handle. Off Linux on 3.14, the first call also imports `ctypes.util` (`dllist`) inside the solve. The Linux arm is read from threadpoolctl 3.7.0's source and is consistent with the CI figures; no Linux box was available to run it. CI's `fast (3.14)` on this head is the measurement.

**The claim it reached several PRs is not supported.** Of 300 failed CI runs back to 2026-11-06, the only fast-job failures naming this check are #3297's two. The fast reds on #3181 and #3198, and #3299's earlier heads, were `tests/entities.py` and `tests/env_drift.py`. Their stress.py lines read `ok`.

**Process state: (d), sound under a precondition that changed beneath it.** `_memory_probe_main`'s docstring states the precondition: "A fresh process gives each scenario an honest high-water mark". That holds for RSS. It held for the traced arm only while the solve left interpreter-global tables alone and the import-time interned table sat far from a rebuild point. Nothing asserted it, so a tree landing near the rebuild point read as a scenario regression. Green runs print no memory figures (`run.sh` shows only a failing script's output), so the shrinking margin was invisible until the red. The countermeasure makes the probe notice its own precondition: `solve_window_imports` and the check that refuses it. The churn shape has no import to observe, so its one known source is pinned in features.py.

**Class reach.** The rule is `git grep -n "tracemalloc.start"`. It returns 9 windows:
- `tests/stress.py`: closed here.
- `tests/replay.py`: memory cycles are the odd cycles after cycle 0 has already solved, so first-call setup is paid before any traced window. Already guarded.
- The seven `dev/audit/rounds/*/D9/*` harnesses, including `round4/D9/h7_memory_gate.py`, which `harness_headers.py` executes: all trace a solve after importing optimizer.py, so this change removes the per-call controller from their windows too. They are evidence records, and their thresholds are not touched.

**Cost test.**
- Defect: one production PR (#3297) blocked on both of its runs, plus this fixer and an RCA seat.
- P(recurrence): the step recurs at every rebuild point the tree's growth passes. In the churn harness they sit about 7 000 and 50 000 interned names apart on 3.14, about 14 500 and 58 000 on 3.12. Any diff can land near one.
- Countermeasure: one set difference per probe and a three-call features check. Passes.

## Mutation proof

- **Delete the production fix** (the stress.py change applied to main's unfixed optimizer.py; mutant worktree at bb7dfb9bd6+wt): the probe's `imported` field reads `["ctypes.macholib", "ctypes.macholib.dyld", "ctypes.macholib.dylib", "ctypes.macholib.framework", "ctypes.util"]` on typical_slab/shoulder (traced 2.06 MiB). The new memory-pass check "no probed solve imports a module inside the traced window (first-call setup is the import's cost, not the scenario's)" fails on it. The full stress.py run per mutant is left to CI's mutation check (`fixer.md` step 5).
- **The features pin, driven against the same mutant**: `FAIL the BLAS thread pin reuses optimizer.py's one ThreadpoolController ... | constructions=4 (want 1: the null control's alone), _blas_threads=NoneType`.
- **A second mutant that keeps `_blas_threads` but calls `threadpoolctl.threadpool_limits(limits=1)` again**: `FAIL ... constructions=4 ..., _blas_threads=ThreadpoolController`.
- **GUARD_OFF on the new guard** (`if _blas_threads is None:` made `if False:`, a copy of the head's custom_components): `FAIL without threadpoolctl the scoped minimize runs unpinned and still solves (x -> 0 on the bowl) | error=AttributeError("'NoneType' object has no attribute 'limit'") x=None`.
- **At the head**: both arms `ok`.

## Null control

At origin/main the traced peaks match the record (3.47 against 3.46 on heavy_old/shoulder), and only a tree near the rebuild point bumps. With the fix, #3297's tree and main read the same: typical_slab/shoulder 1.87 / 1.87, heavy_old/shoulder 3.29 / 3.29, winter/pv+cycle 3.29 / 3.29. Both report `"imported": []`. The 3.29 against a 3.46 record is 0.95x, inside the stale rule. The 0.18 MiB fall is the in-window `ctypes` import that this Mac no longer pays; on Linux, which has no such import, a fall is not expected. In the churn harness a constant (already interned) name peaks at 0.002 MiB against 1.83 MiB steps for fresh names. In the pin, the counter sees a direct construction (1), so a 0 cannot come from a dead counter.

## Figures

Local runs: macOS arm64, uv CPython 3.14.7 and 3.12.14 venvs with `tests/requirements-ci.txt` installed `--no-deps`. Scratch instruments are cited by sha1 (`$S` = this seat's scratch directory).
- traced peaks per tree: `$S/probe1.sh <repo> <python> <label>...` (sha1 1aedffce5a465ce6fa27a35936cf5916f8c77e11), which runs `python3 tests/stress.py --memory-probe <spec>`. Main 3.47; #3297 5.31; main+fix and #3297+fix 1.87 / 3.29 / 3.29; mutant 2.06 with five ctypes modules imported.
- repetition at main and #3297: `$S/memprobe.py <repo> <n> <labels>` (sha1 e3457e990305a17dd798b80980749ec079321a40). Main 3.14.7: [3.47, 3.47, 3.47] / [3.47, 3.47, 3.48] / [3.47, 3.47, 3.47]. #3297 3.14.7: [5.31, 5.31] / [5.3, 5.31] / [5.31, 5.31]. Main 3.12.14: [3.49, 3.49] / [3.5, 3.49].
- first-controller trace and the 100-string padding: `$S/importpeak.py <repo> controller <pad>` (sha1 d1d62b5d929fa50e3dd650ce79ff5114e8363627). 199 / 2076 / 922 / 922 KiB; #3297 at pad 100 gives 199.
- allocation site: `$S/tbdiag.py` (sha1 d3fdab1a419f144015bb2f38023d05e759551c9d). 1888 KiB in 93 blocks under `_compile_bytecode` (`marshal.loads`) of `ctypes.macholib.dyld`, reached through `threadpool_limits` and `_load_libraries`.
- in-window imports and hash-seed independence: `$S/impdiag.py` (sha1 ec9be2b1d49047cbfdf7dd8f70612d692c481f2f). Seeds 1 and 2 both read 3.88 at #3297; main reads 2.05.
- no cyclic garbage in a solve (refutes a GC-timing cause): `$S/gcdiag.py <repo> <label> saveall` (sha1 7f8f62811489bbd7a7a7b9c92ae6adfb89f91d93). `unreachable: 0`.
- the rebuild step: `$S/churn.py` (sha1 b9a3037a4d12d53fc84702d221541245e438c5ea). 1.83 MiB at 7 000 / 57 000 (3.14.7) and 14 500 / 72 500 (3.12.14); null control 0.002 MiB.
- per-call CPU: `$S/tpbench.py` (sha1 6938d9ca4852064d1c3f0a82e42f3fb08fd4366a). Fresh `threadpool_limits` costs 1.141 ms (3.14.7) and 1.838 ms (3.12.14) per call; shared `controller.limit` 0.002 ms. This box's controller finds 0 BLAS libraries (Accelerate), so the Linux figure is not measured here.
- minimize calls per solve: `$S/countcalls.py` (sha1 f862208f468f895120f79fb810bfd06abef6f3da). 8 (typical_slab/shoulder) and 10 (heavy_old/shoulder).
- pin and mutants: `$S/pin1.py` (sha1 c08e52b9a419b780b01a57cb46a86a9742fb062b).
- CI census: `gh run list --workflow CI -L 300 --status failure`, then the failed `fast` jobs' logs grepped for `FAIL the probed scenarios' memory peaks`. 9 failed fast jobs, 0 hits; #3297's job 128711769266 was in progress during the census and carries the hit.
- scope: `python3 tests/closure.py select --diff bb7dfb9bd6...` gives `MODE: SCOPED -- 27 script(s) run, 6 scoped out`.
- `tests/structure.py`: exit 0. `tests/typing_ruler.py`: exit 0. `GOLDEN_MODE=drift tests/golden.py`: exit 0, "NO UNCLAIMED DRIFT: 56 scenario(s)". `tests/features.py`: "ALL 4968 FEATURE CHECKS PASSED" at 17bb738485, both arms of `_blas_pin_shared_controller` `ok`.
- `tests/optimality.py`: 1 of 84 failed, `one|summer_negative|shoulder` (a claimed gap at 0.0000%). The same single failure appears with main's optimizer.py (mutant worktree), so it belongs to this platform's BLAS, not the diff.
- Left to CI: the other scoped scripts, stress.py's full run included, which is the Linux measurement of this fix.

## Red checks

`mutation` (predicted by `prepr.sh` step 6d: `custom_components/heatpump_optimizer/optimizer.py:871 GUARD_OFF`, a site this diff adds): pinned by a value check in this diff, the no-threadpoolctl arm of `tests/features.py::_blas_pin_shared_controller`, which kills it (Mutation proof). Its cheaper detector is that arm itself, in the fast suite.

`tests / fast (3.14)` on #3297 (jobs 128711769266, 128751219984): stress.py's memory-budget check. A cheaper detector exists and lands here: the features.py pin `_blas_pin_shared_controller` (three minimize calls, milliseconds) catches the per-call controller that produced the churn, in the fast suite, on any platform. The probe-side `solve_window_imports` check costs one set difference per probe. A detector for the general shape (any interning churn inside a traced window) was not found: the interned table is not observable from Python. That is stated in `solve_window_imports`'s docstring.

## Unpinned sites

- custom_components/heatpump_optimizer/optimizer.py:871 GUARD_OFF: pinned by a value check, `tests/features.py::_blas_pin_shared_controller` (the no-threadpoolctl arm), which fails with AttributeError under the mutant

## Forward-carry

`none`

## Friction

`none`
