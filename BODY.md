R10-HOTFIX-STRESS-MEM-PEAK: `tests / fast (3.14)` failed `tests/stress.py`'s "the probed scenarios' memory peaks stay within their recorded budgets" on #3297. The cause is not #3297's diff and not the interpreter version. It is the BLAS thread pin in `optimizer._scoped_minimize`, which built a fresh `threadpoolctl.ThreadpoolController` on every minimize call. The work each build did inside the solve forced CPython to rebuild its interpreter-wide interned-string table in one 1.83 MiB step, and the memory probe's traced window charged that step to whichever scenario's solve crossed the rebuild point. This change builds one controller at import, and the probe now asserts its own precondition: no import inside the traced window.

This repair round answers the three reds at 0f84b0fe8b (`gate`, `tests / mutation`, `tests / replay`).
- It pins the new guard's mutant in the ledger.
- It re-records one replay CPU budget down. The single controller made a replay cycle cheaper, so the old budget could no longer see a doubled cycle.
- It restores a replay null control that the tighter budget had silenced.

A local Linux finding limits what this PR closes. It is under `## Forward-carry`, carried to the two live stages that read a stress red. This round changes no code: it repairs the body against the review verdict at 00d12cad0f (verdict/3349 61a90cfce8).

## Head

`00d12cad0f12bb8eb7da1010a720f7576fd4a552`. Its tree is 6286dfef5e's (`git diff --stat 6286dfef 00d12cad` prints nothing); 6286dfef5e merges origin/main `425b858495432c8dceb89d8d13866550352ba54f` into round 2's 0eb862d2 (giving 4dc05fad, where the scoped gate ran), then `fdc8d21adaa50a7feee534f08ee5edde9bda81ed` (#3338: governance and tools only, no file of this diff). Both merges are clean. No merge this round: `git merge-tree --write-tree origin/main 00d12cad` exits 0 against origin/main 6457496aba (stamped 2026-11-09T02:52Z), so the branch is not re-cut or moved. The merge base stays fdc8d21ada and the scope is unchanged (`MODE: SCOPED -- 27 script(s) run, 6 scoped out`, re-derived at this head).

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

**What interns inside the solve.** `threadpool_limits(limits=1)` constructs `ThreadpoolController()` per call: 8 calls per typical_slab/shoulder solve, 10 per heavy_old/shoulder. On Linux (`_find_libraries_with_linux`, `/proc/self/maps`) each construction opens fresh `ctypes.CDLL` handles. Their symbol names are built at runtime (`f"{prefix}openblas_get_num_threads{suffix}"`, `_get_symbol`), interned by `CDLL.__getattr__`'s `setattr`, and freed with the handle. Off Linux on 3.14, the first call also imports `ctypes.util` (`dllist`) inside the solve. The Linux arm is read from threadpoolctl 3.7.0's source; it was not measured on Linux in this seat. The review's Linux measurement does not confirm it: base and head each ran red 1 of 3 interleaved on one box (`## Forward-carry`), so on Linux the harness does not move under the fix. CI's `fast (3.14)` read green at this head (job 128914863009, `ok python3 tests/stress.py`), which is one more sample of that flake, not a confirmation.

**The claim it reached several PRs is not supported.** Of 300 failed CI runs back to 2026-11-06, the only fast-job failures naming this check are #3297's two. The fast reds on #3181 and #3198, and #3299's earlier heads, were `tests/entities.py` and `tests/env_drift.py`. Their stress.py lines read `ok`.

**Process state: (d), sound under a precondition that changed beneath it.** `_memory_probe_main`'s docstring states the precondition: "A fresh process gives each scenario an honest high-water mark". That holds for RSS. It held for the traced arm only while the solve left interpreter-global tables alone and the import-time interned table sat far from a rebuild point. Nothing asserted it, so a tree landing near the rebuild point read as a scenario regression. Green runs print no memory figures (`run.sh` shows only a failing script's output), so the shrinking margin was invisible until the red. The countermeasure is two checks, and only one reaches Linux. `solve_window_imports` and the stress check that refuses it notice the precondition off Linux only: there the unfixed optimizer imports `ctypes.util` and four `ctypes.macholib` modules inside the window. On Linux it reads `[]` with the unfixed optimizer too (the reviewer's ev/linux-inwindow-imports.txt on verdict/3349: `mutA in-window imports: []`, `wt in-window imports: []`), so it cannot fire there and does not notice this precondition on Linux. The churn shape has no import to observe. On Linux the fix's one guard is the features pin on the shared controller (`_blas_pin_shared_controller`), which the reviewer's mutants A, B and C all fail.

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

- **This round, the ledger's own mutant**: `python3 tests/mutation_table.py --pin-killed --base origin/main` drove `optimizer.py:887 GUARD_OFF` (`if _blas_threads is None:` as `if False:`). It took `tests/features.py` from rc=0 failed=0 to rc=1 failed=2: `pinned custom_components/heatpump_optimizer/optimizer.py:887 GUARD_OFF -- killed by tests/features.py`, `PIN KILLED: 1 pinned, 0 left unpinned`. Its null control (`optimizer.py:552 NULL_COMMENT`) survived every driver.
- **The replay re-record, before and after**: `replay.draw_offenders(replay.cost_draws())` with job 128866186676's rows appended and ref47 still at 3.3424 names that job (`clean cpu_ratio 1.551: budget 3.342 cannot see a 2x cycle`; `cpu arm not over budget`). At 2.7713 it names none.
- **The draws null**: moving job 125051003592 under the ref53 border (into ref47) names nothing at 2.7713. Moved into ref40 it is named (`clean cpu_ratio 1.444: budget 3.987 cannot see a 2x cycle`). Moving 127046649273 over the border into ref53 is still named (`clean cpu_ratio 2.256 over its budget 2.076`).

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

This round, on a 4-core Linux x86_64 container with venv-ci's CPython 3.14.7. Scratch instruments are cited by sha1. Stamped origin/main 425b858495 at 2026-11-08T23:40Z; figures taken before that merge name their head.
- the CI reds: check-runs at 0f84b0fe8b read by `gh api repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs` and job logs by `python3 tools/audit/seat/merge_train.py job-log <job>`. (`tools/audit/seat/failure_logs.sh 3349` exits 2 here: its `gh pr view` is GraphQL, which this container refuses.)
- the pin: `python3 tests/mutation_table.py --pin-killed --base origin/main`. 1 pinned, 0 left unpinned. The ledger file is `tests/mutation_ledger/killed_by/optimizer.py/_scoped_minimize.GUARD_OFF.46e8ecae.json`.
- the replay draw: `python3 tools/audit/seat/replay_draws.py parse --cache <one-run cache>` over run 42523460002's `tests / replay` job 128866186676 gave 5 rows, appended to `tests/replay_cost_draws.tsv`. Synthetic clean cpu_ratio 1.5508, ruler 45.9 (class ref47); every earlier ref47 clean draw reads 2.2558-2.4762.
- the re-derived tables: `replay.derive_cost_classes(replay.cost_draws(), name)` for both fixtures. The only change is synthetic ref47 `cpu_ratio` 3.3424 -> 2.7713. Every band, every other class budget and the flat budgets are unchanged. This is a tightening, not a raise.
- the fix's CPU effect, interleaved on one box: `$S/interleave.sh <out> 4` (sha1 eb0e42e0f467b8cd3a53585e592a9950cbc55504), which drives `$S/one_cost.py <tree>` (sha1 a10189bc35c14f054a83bfe29d446dcb731418ee). That script is `replay.replay_one` on the synthetic fixture, clean. Ruler 27.8-29.5 ms. origin/main cpu_ratio 2.6736 / 2.5756 / 2.758 / 2.5968; this head 2.1811 / 2.1976 / 2.1715 / 2.1389. The control is main's own four readings, interleaved with the head's.
- scope: `python3 tests/closure.py select --diff daf8b349fd...` gives `MODE: SCOPED -- 27 script(s) run, 6 scoped out`.
- the scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` at fa3ab3e+merge gave `2 TEST SCRIPT(S) FAILED`.
  - `tests/entities.py` failed `1 of 2668`: `replay control:cycle_cost:draws`, the null this round re-cut. Re-run at 0eb862d2: `ALL 2668 ENTITY CHECKS PASSED`. The scoped gate at 4dc05fad is the GATE2 line below.
  - `tests/stress.py` failed `1 of 114`, the memory-budget check. See `## Forward-carry`.
  - Every other scoped script read `ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- local stress memory pass (`PYTHONPATH=tests/hastub python3 tests/stress.py`), traced MiB per probed scenario, recorded 3.5 / 3.5 / 3.5 / 3.4 / 3.4 / 1.8, in the order heavy_old/shoulder, winter/cycle, winter/pv+cycle, typical_slab/winter, winter_extreme/1z/dhw, typical_slab/shoulder:
  - origin/main: 3.5 / 3.5 / 3.5 / 5.3 / 5.3 / 2.2. The memory check is red. Its other 7 reds are the self-comparison arms ("origin/main IS this commit").
  - head, first run: 3.3 / 3.4 / 5.2 / 3.3 / 5.1 / 3.9.
  - head, second run: 3.3 / 5.2 / 3.4 / 5.1 / 5.1 / 3.9.
  - head 4dc05fad, inside the scoped gate (GATE2): 5.2 / 5.2 / 5.2 / 3.3 / 3.3 / 3.9. That gate gave `1 TEST SCRIPT(S) FAILED`, this memory check alone (`1 of 114`). `ALL 2668 ENTITY CHECKS PASSED`; every other scoped script read `ok`.
  - All three head runs report `"imported"` empty on every probe.
  - typical_slab/shoulder read 3.9 in 3 of 3 head runs and 2.2 in main's 1 run. The other bumps move between scenarios from run to run.
- the replay lane, synthetic fixture: `PYTHONPATH=tests/hastub python3 tests/replay.py --fixture tests/replay/synthetic-dhw-only.json` at 0eb862d2 gave `1 of 184 replay checks FAILED`.
  - The only failure is `loop_cpu_ratio 0.1574 over its budget 0.1527` on job ruler 26.76 (class ref28). cpu_ratio 1.9433 is inside ref28's band (1.5945, 3.189], and all three doubled arms read over budget.
  - The loop figure is this box's, not the diff's. replay.py's `COST_BUDGETS` comment records that a 4-core box reads it higher at the same code, and the interleave above read main's loop figure 0.1474-0.1672 against the head's 0.1464-0.1778.
- one-scenario probes: `$S/tbprobe.py <tree> <label> 12` (sha1 2e4e334b15b8d2dccdb61dc26fcfbd8191a7c42c) read typical_slab/shoulder at 2.06 with the largest live block 1 KiB. `$S/jumpprobe.py <tree> <label>` (sha1 ca205902471468b1292c1e5f1d8735566dd1bd1e) read winter_extreme/1z/dhw at 3.37 with no jump. Neither reproduced the step.

This round (body-only repair), at 00d12cad0f on a Linux x86_64 container with venv-ci's CPython 3.14.7, origin/main 6457496aba at 2026-11-09T02:52Z:
- merge: `git merge-tree --write-tree origin/main 00d12cad` exit 0.
- scope: `python3 tests/closure.py select --diff fdc8d21ada --workdir <d>` gives `MODE: SCOPED -- 27 script(s) run, 6 scoped out`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, exit 0.
- the pin: `PYTHONPATH=tests/hastub python3 tests/features.py` reads `ok` on both `_blas_pin_shared_controller` arms ("the BLAS thread pin reuses optimizer.py's one ThreadpoolController ..." and "without threadpoolctl the scoped minimize runs unpinned ..."); the reviewer's three mutants fail them (verdict/3349 ev/features-mut*.log), the control.
- class rule: `git grep -n "tracemalloc.start"` returns 9 windows at the head and 9 at fdc8d21ada, the same files as `## Root cause` lists.
- production BLAS-pin sites: `git grep -nE "threadpool_limits|ThreadpoolController" -- custom_components` returns one construction (optimizer.py, the module-level `ThreadpoolController()`) and one comment line; at fdc8d21ada the same rule returns the per-call `_threadpool_limits(limits=1)` in `_scoped_minimize`, the control.
- the Linux in-window import reading and the stress table under `## Forward-carry` are the reviewer's (verdict/3349 61a90cfce8); not re-run here, they are cited by path.

## Red checks

`gate` (jobs 128867413273, 128867544758 at 0f84b0fe8b): it deferred to the code run. Both logs read `FAIL run(s) [42523460002] at this head are still being judged; their gate decides`. Run 42523460002 is the CI run whose `tests / mutation` and `tests / replay` were then red. Each of those is answered below, so `gate` has no cause of its own. No cheaper detector exists: it is the aggregator.

`tests / mutation` (job 128865168606): `ADDED UNPINNED custom_components/heatpump_optimizer/optimizer.py:887 GUARD_OFF: if _blas_threads is None:`. The earlier body's value-check disposition did not reach the ratchet, which reads no body. When this round started, `tests / mutation-pins (1)` (job 128867079096) had not concluded, so the pin was run here: `--pin-killed` killed it with `tests/features.py` and wrote the ledger entry. The cheaper detector is `tools/pr/prepr.sh` step 6d, which predicted this site in round 1. Its standing cost is zero. The miss was answering it in the body instead of the ledger.

`tests / replay` (job 128866186676): `FAIL synthetic-dhw-only.json: cycle_cost [... cpu_ratio 1.551: budget 3.342 cannot see a 2x cycle; re-record 2.193]` and `FAIL ... cycle_cost sees a doubled cycle cpu`. This is the fix's own effect: one controller made each cycle cheaper (ref47 2.26-2.47 -> 1.55; this box 2.58-2.76 -> 2.14-2.20). Answered by the rule's re-record of ref47. A cheaper detector exists: run `replay_one` interleaved on a tree that changes the solve's per-call work before handoff (`$S/interleave.sh`, about 4 minutes). Nothing makes a seat run it, because no scope picks the replay lane for an `optimizer.py` diff.

At 00d12cad0f (this head), three `gate` jobs are red, and every test lane is green (`tests / fast (3.14)` 128914863009, `tests / replay` 128914863112, `tests / mutation` 128913029926, `tests / coverage` 128914863109):
- `gate` 128913688779 and 128917830783: `FAIL run(s) [42539673685, 42540585921] at this head are still being judged; their gate decides` and `FAIL run(s) [42539673685] ...`. Deferrals to the code run; no cause of their own, and no cheaper detector: it is the aggregator.
- `gate` 128928635369: `FAIL codeql / Analyze (python): cancelled (this run)`. That job, 128913029832, ran 00:29:48Z to 01:14:53Z, 45 min 5 s, against the job's `timeout-minutes: 45` in `.github/workflows/codeql.yml`: a timeout cancellation, not a finding. No test reads red, so no cheaper detector exists that could have run it earlier; the remedy is a re-run of that analysis, which is the orchestrator's, since the head is frozen.

## Unpinned sites

- custom_components/heatpump_optimizer/optimizer.py:887 GUARD_OFF: pinned under `killed_by` by `tests/mutation_table.py --pin-killed`, killed by `tests/features.py` (`_blas_pin_shared_controller`'s no-threadpoolctl arm)

## Forward-carry

- On Linux with CPython 3.14, a traced bump of about 1.8 MiB in `tests/stress.py`'s memory pass (the check "the probed scenarios' memory peaks stay within their recorded budgets") is not, alone, evidence against a diff; it is open at both ends, at origin/main and at #3349's fix, and its source is unidentified. This stage's #3299 is blocked on a stress mem-peak red, so its fixer and reviewer read that red under this precondition.
  - The control, the fix reviewer's measurement (its stress summary and six stress logs on the verdict ref verdict/3349 at 61a90cfce8): one 4-core Linux x86_64 container, venv-ci CPython 3.14.7, `PYTHONPATH=tests/hastub python3 tests/stress.py` three times per tree, base fdc8d21ada and head 00d12cad0f run as interleaved parallel pairs. Traced MiB per probe in the order heavy_old/shoulder, winter/cycle, winter/pv+cycle, typical_slab/winter, winter_extreme/1z/dhw, typical_slab/shoulder, recorded 3.5 / 3.5 / 3.5 / 3.4 / 3.4 / 1.8, red above 1.5x the record:
  - head run 1: 5.2 / 3.3 / 3.3 / 3.3 / 3.3 / 2.1, ALL 114 STRESS CHECKS PASSED
  - head run 2: 3.3 / 3.3 / 3.3 / 5.1 / 5.1 / 3.9, 1 of 114 STRESS CHECKS FAILED (typical_slab/shoulder 3.9 against 1.8)
  - head run 3: 5.2 / 5.2 / 3.3 / 5.1 / 3.3 / 2.1, ALL 114 STRESS CHECKS PASSED
  - base run 1: 3.5 / 3.5 / 3.5 / 3.4 / 3.4 / 2.2, ALL 113 STRESS CHECKS PASSED
  - base run 2: 3.5 / 3.5 / 3.5 / 3.4 / 3.4 / 2.2, ALL 113 STRESS CHECKS PASSED
  - base run 3: 5.3 / 3.5 / 5.3 / 3.4 / 3.4 / 2.2, 1 of 113 STRESS CHECKS FAILED
  - Red runs: head 1 of 3, base 1 of 3. Bumped probes (a reading at least 1.5 MiB over its record): head 7 of 18, base 2 of 18. Every bump is +1.7 to 2.1 MiB. The rule that would have separated a diff's own regression from the flake, a red at head with base green beside it on the same box, did not separate here.
  - Re-measure before reading a 3.14 stress memory red against a diff: run `PYTHONPATH=tests/hastub python3 tests/stress.py` three times per tree, the merge base beside the head, on one box, interleaved, and compare red counts and bumped probes. Only a head red count or bumped-probe count above the base's beside it is evidence against the diff; the figures above are snapshots from one box and are not a budget.
  - Carry: R10-GENERIC-HEAT-CURVE
- On Linux with CPython 3.14, a traced bump of about 1.8 MiB in `tests/stress.py`'s memory pass (the check "the probed scenarios' memory peaks stay within their recorded budgets") is not, alone, evidence against a diff; it is open at both ends, at origin/main and at #3349's fix, and its source is unidentified. Destination for the D9 CPU/memory stage: no live group of the round-10 roster (origin/handoff/audit-r10-roster) owns D9 as a stage; this is the one live group whose brief names the D9 target, and its solver CPU measurements are read by the same stress pass.
  - The control, the fix reviewer's measurement (its stress summary and six stress logs on the verdict ref verdict/3349 at 61a90cfce8): one 4-core Linux x86_64 container, venv-ci CPython 3.14.7, `PYTHONPATH=tests/hastub python3 tests/stress.py` three times per tree, base fdc8d21ada and head 00d12cad0f run as interleaved parallel pairs. Traced MiB per probe in the order heavy_old/shoulder, winter/cycle, winter/pv+cycle, typical_slab/winter, winter_extreme/1z/dhw, typical_slab/shoulder, recorded 3.5 / 3.5 / 3.5 / 3.4 / 3.4 / 1.8, red above 1.5x the record:
  - head run 1: 5.2 / 3.3 / 3.3 / 3.3 / 3.3 / 2.1, ALL 114 STRESS CHECKS PASSED
  - head run 2: 3.3 / 3.3 / 3.3 / 5.1 / 5.1 / 3.9, 1 of 114 STRESS CHECKS FAILED (typical_slab/shoulder 3.9 against 1.8)
  - head run 3: 5.2 / 5.2 / 3.3 / 5.1 / 3.3 / 2.1, ALL 114 STRESS CHECKS PASSED
  - base run 1: 3.5 / 3.5 / 3.5 / 3.4 / 3.4 / 2.2, ALL 113 STRESS CHECKS PASSED
  - base run 2: 3.5 / 3.5 / 3.5 / 3.4 / 3.4 / 2.2, ALL 113 STRESS CHECKS PASSED
  - base run 3: 5.3 / 3.5 / 5.3 / 3.4 / 3.4 / 2.2, 1 of 113 STRESS CHECKS FAILED
  - Red runs: head 1 of 3, base 1 of 3. Bumped probes (a reading at least 1.5 MiB over its record): head 7 of 18, base 2 of 18. Every bump is +1.7 to 2.1 MiB. The rule that would have separated a diff's own regression from the flake, a red at head with base green beside it on the same box, did not separate here.
  - Re-measure before reading a 3.14 stress memory red against a diff: run `PYTHONPATH=tests/hastub python3 tests/stress.py` three times per tree, the merge base beside the head, on one box, interleaved, and compare red counts and bumped probes. Only a head red count or bumped-probe count above the base's beside it is evidence against the diff; the figures above are snapshots from one box and are not a budget.
  - Carry: R10-PARTLOAD-RESIDUE
- Disclosed self-correction: the previous body called typical_slab/shoulder's 3.9 MiB on this head stable rather than run-dependent (3 of 3 runs in the fixer's own sample). The reviewer's three head runs read it 2.1 / 3.9 / 2.1, so it is run-dependent like the others; the fixer's readings stay under `## Figures` as recorded. Carry: dismissed: corrected in this body, and the carried precondition above already covers every probe
- The ref47 re-record rests on one post-fix CI draw. The other six synthetic classes hold only pre-fix draws, and the fix cut the cycle by 0.65x on ref47 and 0.82x on this box. A post-fix ref53 draw near 0.65 x 1.45 would fall under that class's floor of 1.038 (2.076 / 2). The next replay job on another class may then need the same rule-driven re-record (append its rows, re-derive). Carry: R10-HOTFIX-STRESS-MEM-PEAK | dismissed: the existing re-record rule in replay.py's `COST_BUDGETS` comment already prescribes that step, so no stage's procedure changes

## Friction

- failure_logs: cost: `tools/audit/seat/failure_logs.sh 3349` exits 2 in a cloud container because its head lookup is `gh pr view`, which uses GraphQL, and the proxy refuses GraphQL. The check-run and job-log steps after it are REST and work. Carry: dismissed: a one-line instrument fix outside this group; the brief forbids extra writes, and the REST path worked by hand.
