R11-SEAM-tests part C (D9-s3-01), the split part the approved design names (design/R11-SEAM-tests at 2d01f6d379cce723f4427314307b74912c9f0e81, §3 C, §7; approved at design-verdict/R11-SEAM-tests 7e60e1ba). It resolves #3825's Forward-carry item 81abd26b.

In check mode, `tests/stress.py`'s memory pass probed six recorded leaders, three per axis. A 2x regression confined to any of the other 48 rows therefore passed, while the detection arithmetic sized every row's budget. Changes:
- `_memory_probe_labels` returns every recorded row. The top-N slice and its cost-order fallback are deleted.
- The new check `the memory pass probes every recorded row` holds the coverage. It replaces the coverage print and the each-axis-maximum check, which every-row coverage implies.
- The probes run on a `concurrent.futures` thread pool with one worker per core. Every verdict is bytes, which contention does not move.
- The room-history timing check moves ahead of the memory pass, so no timing channel runs after it (§3 C "Cost").

Deviation from §3 C, with its reason: the design kept `MEMORY_TOP_N` "only where record mode re-probes the exposed labels". `record_memory_table`'s own rule is that the rows check mode compares get five passes, because a single `ru_maxrss` draw false-reds the first high draw. Check mode now compares every row, so every row gets five passes on the same pool. `MEMORY_TOP_N` and `STRESS_MEMORY_TOP_N` lose their last reader and are deleted. Keeping the top-N re-probe would record 48 compared rows from one draw each.

Harness ports, both under fixer step 3 (a fold deleting a name a harness drives):
- `dev/audit/rounds/round4/D9/h7_memory_gate.py` is live-headered, and `tests/harness_headers.py` executes it. It transcribed the old selector and read `stress.MEMORY_TOP_N`. It now executes stress.py's own nested `_memory_probe_labels`, as the round-11 harness does. Its header moves to probed 54 / never probed 0, and the `memory_top_n` line goes.
- `dev/audit/rounds/round11/D9/s3/mem_confined.py` defaulted `--top-n` to `stress.MEMORY_TOP_N`. It now falls back to `None`, which the every-row selector never reads.

## Head

`8e92c8bb22a55b52ceacb45cd2169ba33640229e` merges the authored code head `d9844d45f59031d1c1f9f1a2e5297c7282467488`.

`5591297f497ac679e61a4fe21605ccce7c8d96f1` merges the authored code head `d9844d45f59031d1c1f9f1a2e5297c7282467488`.

`005a5afd71cfc72fe55942aa478dfb07bfe174d0` merges the authored code head `d9844d45f59031d1c1f9f1a2e5297c7282467488`.

d9844d45f59031d1c1f9f1a2e5297c7282467488 is the head. It is 8d1774b5b0d903a4d335ff49b0fd44857d8cbb32 (the head the review blocked, review/3890 cd7cfdf1, `tests-red`; it is 76827903 plus a merge of origin/main at ae319a5f and the delivery-row commit) plus one commit, d9844d45, which changes `tests/stress_budgets.json` alone: the memory re-record under `## Raise justification`. No code moved, so every figure below still holds at the head except the stress memory verdict, which this commit answers.

Before that: 76827903e91640fd06dcad586eb67e8ac3d861f3, on merge base 7f7e05118feebc6731b854a2a3c7a73b13e4cdd3. The `stress.py` figures below were taken at db56b365b157aa1f60c46926bd5eb05229bd114a. The only commit after it, 76827903, touches the two harnesses alone.

## Mutation proof

Commit b8a5aaee88b5fe99058536596cb13a755e9c1910 is this branch's failing-first commit: the new check over the base's top-N selector. It is also the design's named mutant, the selection restored. Full run `python3 tests/gate_lock.py auto-lease --label r11-seam-tests-c -- python3 -u tests/stress.py` at that tree:
- `FAIL the memory pass probes every recorded row  [48 recorded row(s) not probed, ...]` names each of the 48.
- `2 of 122 STRESS CHECKS FAILED`, exit 1.

The second red at that tree is `its report costs less than one reference solve` (report 25.4 ms vs reference solve 23.5 ms). It is the pre-existing timing check, which at that tree still ran after the memory pass. At db56b365 it runs before the pass and passed.

Same command at db56b365: `ok   the memory pass probes every recorded row`. The diff adds no `.py` line outside `tests/` and `dev/`, so prepr's mutant draw has nothing to take. Per fixer step 5, stress.py mutants are left to CI's required `tests / mutation`.

## Null control

The finder's harness `$EXPORT/dev/audit/rounds/round11/D9/s3/mem_confined.py` (sha1 39310648bc51427e915a78c121722066ecefa8c5, the unported copy) was run with `PYTHONPATH=tests/hastub python3 <harness> --jobs 2 --top-n 6`. At the base, `--top-n 6` equals its default. At the head, the selector reads no `MEMORY_TOP_N`, so the value is inert. Base runs used a detached worktree at 7f7e0511.

| arm | base 7f7e0511 | head db56b365 |
|---|---|---|
| inject (`--ballast-factor` 1.0) | `probed_by_gate` 6, `detected_confined` 6, `blind_confined` 48 | `probed_by_gate` 54, `detected_confined` 54, `blind_confined` 0 |
| null (`--ballast-factor 0`) | `detected_confined` 0, `blind_confined` 11, `flagged_if_probed` 11 | `detected_confined` 11, `blind_confined` 0, `flagged_if_probed` 11 |

The null's 11 flags are a clean tree reading over the record. Every one is traced-side; the attributable RSS of each sits at or under the record. They are the rows the re-record must decide, which `## Raise justification` does at the head. This box reads 11 where the finder read 9. The two extra rows, `summer/2z/space/valve-direct-slab` (x1.506) and `summer/2z/space/wood-two-tank` (x1.527), sit just over the 1.5 factor.

## Figures

- `stress.py` wall time, from the command under Mutation proof, alone on a 4-vCPU Linux box with venv-ci Python and OPENBLAS_CORETYPE Haswell: 323.3 s at b8a5aaee (six probes, serial) and 462.5 s at db56b365 (54 probes on a 4-worker pool), +139 s.
- CI `fast` cost on main: `tests / fast (3.14)` of run 45549222867, at merge base 7f7e0511 (push, GATE_SCOPE full), ran 04:54:08-05:47:42 UTC, 53.6 min against `timeout-minutes: 100` (`.github/workflows/tests.yml`, the `fast` job). Read with `mcp actions_list list_workflow_jobs 45549222867`.
- Projection: 53.6 min + 139 s ≈ 55.9 min, if the runner probes at this box's speed. At twice this box's time the delta is 278 s and the job ≈ 58.2 min. Both are under 100, so §4's rotation fallback is not taken. The design's wall-time precondition is measured on the pull request itself, so the orchestrator reads that job's time in CI.
- Head memory verdict, same command at db56b365: `FAIL the probed scenarios' memory peaks stay within their recorded budgets` on 10 traced rows: flat/1z/space, flat/2z/space, shoulder/1z/space, shoulder/2z/space, summer/2z/space/wood-two-tank, winter/2z/space, winter_extreme/2z/space, winter_mild/1z/space, winter_mild/2z/dhw, winter_mild/2z/space. `1 of 122 STRESS CHECKS FAILED`. Also: `ok   no probed scenario's memory got dramatically cheaper without a re-record`, `ok   every memory-pass scenario has recorded peaks`, and parent RSS growth 0.5 MiB.
- On this box the empty-probe baseline reads 108.4 MiB, and `attributable RSS: 54 of 54 probe(s) read at this platform's import floor`. The RSS arm says nothing here, so only the CI platform can read it.
- `h7_memory_gate.py` at the head: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D9/h7_memory_gate.py` prints `scenarios_memory_probed=54`, `scenarios_never_memory_probed=0`, and every other exact line equals its header.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` reports `MODE: SCOPED -- 6 script(s) run, 28 scoped out`. Each run at the head with `PYTHONPATH=tests/hastub`:
  - doc_claims: `ALL 441 checks PASSED`
  - entities: `ALL 2761 ENTITY CHECKS PASSED`
  - features: `ALL 6116 FEATURE CHECKS PASSED`
  - cycle_lane: `ALL 25 checks PASSED`
  - harness_headers: `ALL 114 HARNESS HEADER CHECKS PASSED` at 76827903 (at db56b365, before the harness ports, 17 checks failed, all on h7_memory_gate.py)
  - stress: the red above
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

- `tests / fast (3.14)` at 8d1774b5 (job 139068952639): `FAILED python3 tests/stress.py`, `1 of 122 STRESS CHECKS FAILED`, on `the probed scenarios' memory peaks stay within their recorded budgets`. It was predicted: the memory pass now probes every row, and 11 rows read over 1.5x their September record on the CI runner. The head re-records those rows, and two at 1.49x, from that job's readings (`## Raise justification`). Cheaper detector: none. The red is the CI platform's all-row reading, which design §7 requires as the source of the record; no check could read it earlier, because before this pull request no run probed those rows.
- `gate` failed on 8d1774b5 because it aggregates `fast`'s red, and the same commit answers it.
- `budget-raise-gate` is red at this head by design: it lists the 13 `traced_peak_mb` raises in `tests/stress_budgets.json` (for example `flat/1z/space.traced_peak_mb: 0.91 -> 1.7`) and stays red until the approving review at the head, here the mandate's (6893738184, scope `all`) under `## Raise justification`. Cheaper detector: none; the gate is the detector, and a raise is meant to stop at it.
- `tests / nightly-status` was red at 8d1774b5. It is not a required check, so it is not owed here.

## Raise justification

The head raises `traced_peak_mb` on 13 rows of `tests/stress_budgets.json`. Each goes to its traced reading on the CI runner (job 139068952639, `tests / fast (3.14)` at 8d1774b5, the clean all-row run) and no higher. 11 rows read over the 1.5x factor and failed the check. Two more, `summer/2z/space` and `summer_negative/2z/space`, read 1.3 MiB against a 0.87 record, 1.49x, which is under the line by less than the log's rounding: the log prints the traced peak to 0.1 MiB, so a true peak between 1.305 and 1.35 MiB prints the same 1.3 and fails, and the next run can trip it on rounding alone. The other 19 rows that read above their record, all under 1.49x, are left at their recorded values, since only a failing row earns a raise (ratchet-budgets.md). No other field moves: `rss_attrib_mb` and `rss_peak_mb` are unchanged, because on this platform every probe reads at the import floor (`attributable RSS: 54 of 54`), which records nothing. Every CPU `ratio` is unchanged too. The 21 rows that read at or under their record are untouched too, since a lowering is a separate re-record. The old records date from 2026-09-28 (9358ef7a, f2766871). Since then the old selector probed only six leaders, so no check read these rows against later production changes.

Deviation from design §7, with its reason: §7 names `stress.py --record-memory`, five passes per row. These figures are the check-mode readings from the CI log, one draw per row, per the orchestrator's brief. `traced_fail_threshold`'s docstring gives the traced peak's run-to-run spread as about 0.1 MiB, against `ru_maxrss`'s 2x spread. The five-pass rule exists for the attributable RSS column, which is not re-recorded here, so one traced draw is the statistic.

| row | record | CI reading (new record) | rise |
|---|---|---|---|
| `flat/1z/space` | 0.91 | 1.7 | 1.87x |
| `flat/2z/space` | 0.93 | 2.2 | 2.37x |
| `shoulder/1z/space` | 0.89 | 1.5 | 1.69x |
| `shoulder/2z/space` | 0.91 | 2.2 | 2.42x |
| `summer/2z/space` | 0.87 | 1.3 | 1.49x |
| `summer/2z/space/valve-direct-slab` | 0.85 | 1.3 | 1.53x |
| `summer/2z/space/wood-two-tank` | 0.91 | 1.4 | 1.54x |
| `summer_negative/2z/space` | 0.87 | 1.3 | 1.49x |
| `winter/2z/space` | 0.92 | 2.0 | 2.17x |
| `winter_extreme/2z/space` | 0.94 | 2.2 | 2.34x |
| `winter_mild/1z/space` | 0.91 | 1.8 | 1.98x |
| `winter_mild/2z/dhw` | 1.82 | 3.3 | 1.81x |
| `winter_mild/2z/space` | 0.91 | 2.2 | 2.42x |

Approval: a raise in `*_budgets.json`. It goes under mandate 6893738184 (scope `all`), by CLAUDE.md rule 2's mandate arm and `budget-raise-gate` (0013). The approving review is the mandate's, after the delta review.
Payments tried: (1) probing only the rows whose record still fits; (2) widening `MEMORY_BUDGET_FACTOR`; (3) keeping the old records and carrying the rise. None of (1)-(3) is an architecture payment: each removes detection (the blind top-N selection this fix deletes, a 2x regression hidden on every row, or a required `fast` red left standing) instead of moving, deleting, sharing or refactoring code, so no tree built from one could score as sounder under `tools/audit/archscore/`, and none was built or scored. (4) lowering the solver's traced working set on these rows is the one real payment. It is a production change outside R11-SEAM-tests (the design reads production files only), so it is carried under `## Forward-carry`, not paid here. The raised values are CI job 139068952639's readings, unpadded.
Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`; measured at the head d9844d45; the diff touches no production file)

## Forward-carry

- The solver's traced working set on the 13 raised stress rows (the 2z/space rows above among them) exceeds their pre-raise `traced_peak_mb` by 1.49x to 2.42x on the CI runner (job 139068952639). Lowering it would let these 13 rows return to their prior budgets. Destination: `dev/programme/rosters/wave-r11-groups.json` (R11-SEAM-cycle-solve's brief). Carry: dismissed: not receivable at roster f520ce03 (R11-SEAM-cycle-solve at carries-open); the orchestrator lands it in R11-SEAM-cycle-solve's roster brief at the next roster landing (ledger CARRY-OWED 3890)

## Friction

none
