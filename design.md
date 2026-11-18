# Design: R11-SEAM-tests (round 11, size L)

Architect note, extended (`dev/governance/roles/designer.md`). Plan of record
`plan/r11` at 819aa2e354b4e5baaf824b8568fd72bea8168a75 (`PLAN.md`; move: adr
none, dS 0). Base 8751943e17ef4d3ec699e7859ae829b4528d8ce7 (`origin/main`);
no `after` edge, so no predecessor head. Resumed from the blocked checkpoint
`handoff-wip/design-R11-SEAM-tests` 92fa49675c (its inputs re-read here, none
reused unread). No production code on this ref. Harnesses are under
`dev/audit/rounds/round11/` on `plan/r11`; each was run at the base from a
worktree with those directories copied in, venv-ci Python, OPENBLAS_CORETYPE
Haswell.

## 1. What each finding reads at the base

| finding | harness, RESULT | finder | base | live |
|---|---|---|---|---|
| D10-s1-05 | `D10/s1/cfg_recovery.py` `unrecovered_triples` of `error_triples` | 51 of 53 | 52 of 54 (config 16, options 34, reconfigure 2); `never_stepped_past` 49; `--perturb` 48 | yes |
| D10-s1-06 | CI `tests / coverage-ratchet` on main 7938522854 (job 134841972572) | 34 modules < 95 % on an export where most traced scripts exited non-zero | `every module >= 95.0 % (0 below)`, package 99.02 %, `config_flow.py` 100.00 % | **no** |
| D9-s3-01 | `D9/s3/mem_confined.py --jobs 2` `blind_confined` | 48 | 48 (`probed_by_gate` 6 of 54, `flagged_if_probed` 54; traced 1.538-3.290×); null `--ballast-factor 0`: `detected_confined` 0, `flagged_if_probed` 9, all unprobed (traced up to 2.323× clean) | yes |
| D9-s3-02 | `D9/s3/percycle.py`; `D9/s3/reach.py` | gate dev 0.0000; `coordinator_executed` 0 | clean 2.00 solves, 88180 B, 8094 B/cycle retained, 422 yields; each arm moves its own metric (4.00; 175804 B; 210628 B/cycle; 0 yields), gate deviations 0.0000 on counts, traced at most 0.0005; `coordinator_executed` 0 of 836, `files_blind` 81 of 97 | yes |

D10-s1-06 is not live on a full tree. The judge already ruled it "not shown
false on a full tree" (`JUDGE.json`). The register row is keyed to the recorded
floors by `tests/entities.py:1894-1927` (`_qs_budgets`). `tests/coverage_ratchet.py` grades
those floors against a fresh `coverage.json` on every push to `main`, and on
each pull request that `tests/lane_skip.py` does not skip for the coverage lane
(`tests.yml` `coverage` then `coverage-ratchet`; `modules_below`,
`coverage_ratchet.py:177`), so a module under 95 % turns the ratchet red. The
recorded floor is therefore a fresh measurement at one remove. **No edit**:
§3 B gives the fixer's proof that the existing detector detects.

## 2. Owning seam

`outside the package`: test suite and ratchets, `tests/` (`COMPONENTS.md`).
`tests/seam_map.json` maps coordinator methods only and has no tests entry.
Each concern has one owner inside the seam:
- `tests/config_flow_steps.py` for A.
- `tests/coverage_ratchet.py` for B (no edit).
- The memory pass of `tests/stress.py` for C.
- A new cycle-lane script under `tests/` for D.

The changes only read `config_flow.py`, `coordinator.py` and `optimizer.py`.
D monkeypatches three of their symbols inside the test process, as
`percycle.py` does: `_run_in_process` (`coordinator.py:2052`),
`_multi_start_minimize` (`optimizer.py:1891`) and `_time_mod`. No concern needs
two owners.

## 3. Shape

**A. Every rendered flow error is driven to its recovery (D10-s1-05).**

*Tracker.* `tests/config_flow_steps.py` gains a tracker owned by `Ledger` (:471).
Every flow the script builds registers with it. Today the script builds flows
at seven sites (§5), and `fresh_flow` (:428) and `fresh_options` (:1515) cover
most of them. Per instance, the tracker wraps `async_show_form` and
`async_show_menu` and records `(kind, step_id, error value)` for each non-empty
`errors`. It also wraps `async_create_entry` and `async_abort` and records
whether that instance finished.

*Finished* means the same instance did one of:
- created an entry (config, or a saved options page);
- aborted with `reauth_successful` or `reconfigure_successful`.

This is the finder's metric definition.

*Recovery.* A helper, `recover(flow, step, fixed, rest)`, resubmits the
corrected answer on the same instance through `submit` (:437). It then walks
the remaining steps to a finished result. Every error check ends in
`recover(...)` on the flow that rendered the error, not on a fresh flow.

*Closing check.* The script's last check asserts that the rendered triples
minus the finished triples is empty. On failure it prints each residual triple.
This is the I1 barrier: a new error branch with no recovery fails
`config_flow_steps.py`, not an audit.

**B. Coverage register row (D10-s1-06).** No edit. The fixer runs the existing
detector twice and puts both runs in the body:
- Detection: `tests/coverage_ratchet.py --coverage` on main's coverage artifact,
  with one module's `executed_lines` trimmed under 95 %. It must print
  `module(s) below` and exit 1.
- Null: the same file untrimmed. It must print `COVERAGE RATCHET PASSED`.

**C. The memory pass probes every recorded row (D9-s3-01).**

*Selection.* In check mode, `_memory_probe_labels` (:5321) returns every label
of the budget table that the sweep runs. The top-N slice and its fallback
(:5352) go. `MEMORY_TOP_N` and `STRESS_MEMORY_TOP_N` (:635) are left only where
record mode re-probes the exposed labels (:1745).

*Cost.* At :5376 the probes run serially, one subprocess each. They move to a
`concurrent.futures` pool of `os.cpu_count()` workers. The verdicts are bytes
(traced peak, and attributable RSS against the same child's empty-probe
baseline), so they do not depend on contention. The pool starts only after every timing
channel of the script has finished; if a timing section runs after the memory
pass today, the memory pass moves behind it.

*Coverage check.* A new check asserts that the set probed equals the set of
recorded rows. The detection-sizing check (:5761-5768) then holds over every
row, and the corollary in the finding (records never re-read) closes.

*Expected cost.* The memory pass costs 207.0 s of child CPU for six probes
(comment at :5298-5303), about 34.5 s per probe. All rows
(`python3 -c "import json;print(len(json.load(open('tests/stress_budgets.json'))))"`)
come to about 1860 s of CPU. On a 4-way pool that is about 470 s of wall time,
against about 207 s now. Measured at the base: `mem_confined.py --jobs 2`,
which runs the gate's own `_run_memory_probe` for every scenario, took 359 s
wall on a 4-vCPU Linux box (load1 1.92), so the estimate is an upper bound. The `fast` job's limit is `timeout-minutes: 100`
(`.github/workflows/tests.yml:217` "timeout-minutes: 100").

**D. A cycle lane (D9-s3-02).** A new `tests/` script, run by `tests/run.sh` as
its own lane. Its channels are counts and bytes, so it runs with the parallel
lanes, not in the alone-on-the-box tail.

*Coordinator.* For each of a fixed set of sweep labels, the lane builds a
coordinator the way `percycle.py` does:
- `tests/harness.py` `FakeHass`, `FakeEntry` and `FakeState`;
- prices and forecast set on the coordinator;
- the three fetchers replaced by no-ops;
- `_run_in_process` swapped for an inline call.

The fixed set is the five labels `percycle.py` drives, taken from
`stress.sweep_combinations` by name. The lane then runs `_async_update_data`
for one warm-up cycle plus four measured cycles.

*Readings per scenario and cycle:*

| channel | how | fails when |
|---|---|---|
| solves per cycle | entries to `_multi_start_minimize`, counted by a wrapper | above the record (integer, deterministic) |
| payload bytes | `len(json.dumps(data, default=str).encode())` of the dict the cycle returns | above 1.5 × record |
| retained bytes per cycle | `tracemalloc` current after `gc.collect()`, mean of consecutive differences after warm-up | above a floor the null sets (§6): arms that do not touch retention read 3830-8406 B/cycle at the base, so 1.5 × record alone would flap |
| yields per cycle | `sleep` calls the optimizer makes while it holds the GIL (all four sites, §5) | below record / 1.5 |
| loop-side calls per cycle | Python calls in `coordinator.py` frames, counted by `sys.setprofile` with the solve excluded | above 1.5 × record |

Loop-side calls stand in for `loop_thread_work`. With the in-process swap,
everything runs on the loop thread, so thread CPU cannot separate the solve.
A call count is contention-immune and moves with the coordinator's own work.
`gil_hold` is read through the yields.

*Records and modes.* Records go in a new budgets file beside
`tests/stress_budgets.json`, keyed by label, written by a `--record` mode.
Check mode reads it. A label with no row fails the run.

*Flow, before and after:*

```
before: run.sh -> stress.py -> build_case -> HeatPumpOptimizer.optimize      (coordinator: 0 functions)
after:  run.sh -> cycle lane -> coordinator._async_update_data x5
                               -> optimize_in_process (inline) -> _build_data_dict
                               -> readings vs the lane's budgets file
```

*Invariants kept.* No production file changes. `tests/golden/` and both claim
files stay byte-identical. The stress solve, CPU and work channels are
unchanged. No budget row anywhere loosens without §7's owner step.

## 4. Alternatives (lost on the code)

- **A, a recovery test per triple on its own flow.** This repeats the
  mechanism that the finding names: the error is rendered on one instance and
  recovered on another. It also doubles the flow constructions.
- **A, the finder's tracker kept as an audit harness only.** No gate reads it,
  so the next unrecovered branch merges green.
- **C, a SHA-keyed rotating subset on pull requests, with the full set on a
  push to `main`.** A 2× regression confined to an unrotated row merges green,
  and the pull request is the cheaper detector. This is the fallback if the
  measured wall time breaks the `fast` limit (§7).
- **C, making the detection check count only probed rows** (the finding's
  second option). The check becomes truthful, but 48 rows stay blind.
- **C, raising `STRESS_MEMORY_TOP_N` in the workflow env.** Same coverage as
  C, but serial: about 1860 s on the tail, with no pool.
- **D, a section inside `tests/stress.py`.** That script is 6250 lines (`wc -l`)
  and runs alone on the box for its timing channels. The lane needs no
  isolation, and placing it there would add its cost to the serial tail.
- **D, extending the cycle tests in `tests/features.py`** (:1203). That script
  pins behaviour and has no record mode. A budget there mixes a ratchet into
  behaviour checks.
- **D, driving the real process worker.** That brings back the IPC timing, and
  the payload pickling is measured nowhere else. The inline swap is the
  finder's harness and keeps every channel a count or bytes.

## 5. Sibling sites (commands, at the base)

| command | hits | disposition |
|---|---|---|
| `grep -nE 'HeatPumpOptimizer(Config\|Options)Flow\(' tests/config_flow_steps.py` | 7 (:430, :1396, :3391, :4346, :4942, :5466, :7754) | all register with A's tracker |
| `git grep -nE 'async_show_form\|async_show_menu' -- custom_components/heatpump_optimizer/ ':!*config_flow.py'` | 1, `repairs.py:37` | `DhwSetpointRepairFlow` renders no `errors` (`git grep -c 'errors\[' -- custom_components/heatpump_optimizer/repairs.py` 0): out of scope |
| `git grep -nE 'MEMORY_TOP_N\|_by_cost\[' -- tests/stress.py` | 6 | :5323, :5352 go (C); :635, :1745 record mode, kept; :5298, :5516 comments rewritten |
| `grep -nE 'sleep\(' custom_components/heatpump_optimizer/optimizer.py` | 4 (:1858, :1888, :1962, :5832) | all counted by D's yields; :5832 is a local `import time` (see notes) |
| `git grep -n 'coverage_budgets' -- tests/entities.py` | the register keying | B: unchanged |

## 6. Evidence plan

**Failing tests first**, each red at the base:
- A's closing check, red with the 52 residual triples.
- C's probed-equals-recorded check, red at 6 of the recorded rows.
- D's lane: run against the base with `percycle.py`'s four injected arms. Each
  arm's own channel must go red: `solves2x` on solves, `payload2x` on payload,
  `retain` on retained bytes, `noyield` on yields.

**Finder's harnesses at both ends**, with the predicted readings after:
- `cfg_recovery.py`: `unrecovered_triples` 0. Null: the reauth triples are
  finished before and after.
- `mem_confined.py --jobs 2`: `blind_confined` 0 and `detected_confined` equal
  to `probed_by_gate`. Null `--ballast-factor 0`: `detected_confined` 0.
- `percycle.py`: unchanged (it reads `build_case`). The lane's readings per arm
  go in the body instead.
- `reach.py`: re-run with the lane's script added to its channel list. The
  coordinator functions it executes must be above 0.

**Null controls.**
- D's clean arm run five times must stay inside every threshold. Its maximum
  sets the retained-bytes floor.
- C's clean all-row check run on the CI platform (below).

**Goldens.** None move. `tests/golden/claimed_drift.txt` and
`card_claimed_drift.txt` stay byte-identical.

**Mutation targets.**
- A: the tracker's finished predicate, and one deleted `recover` call (each
  must redden the closing check).
- C: restoring the `[:MEMORY_TOP_N]` slice (:5352).
- D: each channel's comparison operator and the 1.5 factor.
- B: no code, so the detector proof is §3 B.

## 7. Hot files, serial position, carries

- **Order on shared files.** In the `PLAN.md` hot-file order, this group
  follows plant-model and config on `config_flow.py`. It only reads that file.
  After either of those merges, the fixer re-runs A's closing check at the
  rebased head, because any error branch they add must be recovered. The
  check makes that land on whoever merges second.
- **`quality_scale.yaml`.** This design does not edit it, so the group leaves
  that row (tests, then cycle-reporting).
- **Other hot files.** `tests/stress.py` and `tests/stress_budgets.json` are
  this group's alone. No `after` edge.
- **Owner-gated part, C's re-record.** At the base, the `mem_confined.py` null
  flags 9 unprobed rows on a clean tree (traced up to 2.323× record), the finder's
  same 9 `*/space` and `winter_mild` rows. Probing all rows will be red on a clean
  tree here, so a re-record is expected; the CI-platform run decides which rows rise. If
  the all-row check is red on a clean CI run, the memory half needs a
  re-record on the CI platform. Any row that rises is a raise under
  `budget-raise-gate` (0013), and the owner's confirmation is needed before
  the push (rule 2). A and D do not wait on it: cut C into its own pull
  request, so the owner step blocks only C.
- **D's new budgets file.** `budget_raise_gate.py` reads a budgets file
  present only at the head. Under its `file_raises`, a new leaf is not a raise unless
  its kind is `MAX0` (:358-384). The fixer runs the gate locally before the
  push; a refusal is the owner's step, as above.
- **C's wall-time precondition.** C keeps every row only if the `fast` job,
  measured on the pull request, stays under its limit. If it does not, take
  §4's rotation fallback and record the measurement that refused C.
- **New files.** Classify the lane script and its budgets file in a measured
  closure, or `tests/entities.py` forces FULL (`gate-scoping.md`; derive on
  Linux only).
- **Carries.** No pinned grader in a restoring job registers these files, so
  no p1/p2 split beyond C's cut. No carry is received.

## Notes for the fixer

- `custom_components/heatpump_optimizer/optimizer.py:5832` "time.sleep(0.002)" sleeps through a function-local `import time`. A shim on
  `_time_mod` alone does not count it, and `percycle.py`'s `noyield` arm does
  not remove it, so the lane must count `time.sleep` from optimizer frames.
  Carry: R11-SEAM-tests (item yield-local-time)
- The base renders 54 triples where the finder rendered 53. Take the residual
  list from the closing check at the head, not from the finding.
  Carry: R11-SEAM-tests (item triple-count-moved)
- `percycle.py`'s payload reading counts characters. Encode before taking
  `len`, or a non-ASCII label under-reads.
  Carry: R11-SEAM-tests (item payload-bytes)
- The register rows' `tests/entities.py` keying stays. The D10-s1-06 proposal
  to key the rows to a fresh run duplicates `coverage_ratchet.py`'s grade.
  Carry: dismissed: the ratchet already grades the floors fresh on every push (item register-rekey)
