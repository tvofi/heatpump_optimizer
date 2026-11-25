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

76827903e91640fd06dcad586eb67e8ac3d861f3, on merge base 7f7e05118feebc6731b854a2a3c7a73b13e4cdd3. origin/main was at dc2b2bab316419ced8f919c256908275a2cc3e25 at 2026-11-25 06:23 UTC; `git merge-tree --write-tree origin/main HEAD` reports no conflict. The `stress.py` figures below were taken at db56b365b157aa1f60c46926bd5eb05229bd114a. The only commit after it, 76827903, touches the two harnesses alone.

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

The null's 11 flags are a clean tree reading over the record. Every one is traced-side; the attributable RSS of each sits at or under the record. They are the rows the re-record must decide (Forward-carry). This box reads 11 where the finder read 9. The two extra rows, `summer/2z/space/valve-direct-slab` (x1.506) and `summer/2z/space/wood-two-tank` (x1.527), sit just over the 1.5 factor.

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

`tests / fast (3.14)` is predicted red at this head. The stress lane fails `the probed scenarios' memory peaks stay within their recorded budgets` on the rows over their record, which the Figures list from this box. Cheaper detector: none. The red is the measurement the design's §7 owner-gated step needs, because only the CI platform's clean all-row run may set which rows rise. A row recorded from this box would be a non-CI number, which the brief refuses.

## Raise justification

No budget row moves at this head: `tests/stress_budgets.json` is untouched. The memory-half re-record is owed in this pull request, by the producing group, after its CI run (design §7, CLAUDE.md rule 2, budget-raise-gate 0013). The CI `tests / fast (3.14)` stress log is the clean all-row reading, and each row it fails on `memory peaks stay within their recorded budgets` is a raise. This box's candidates are the null's 11: flat/1z/space, flat/2z/space, shoulder/1z/space, shoulder/2z/space, summer/2z/space/valve-direct-slab, summer/2z/space/wood-two-tank, winter/2z/space, winter_extreme/2z/space, winter_mild/1z/space, winter_mild/2z/dhw, winter_mild/2z/space. Their RSS side is unread here. The record comes from `stress.py --record-memory` on the CI platform (five passes per row at this head), and the raise merges only on the owner's or the mandate's raise review.
Payments tried: (1) probing only the rows whose record still fits, refused because it is the blind selection this fix removes; (2) widening `MEMORY_BUDGET_FACTOR`, refused because it would blind every row's 2x detection, which the detection check holds under `DETECTION_TARGET`; (3) lowering the traced peak in production, outside this group's seam, since the design reads production files only.
Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff 7f7e05118feebc6731b854a2a3c7a73b13e4cdd3 HEAD`; diff mode scores `custom_components/` only, and this diff touches no production file).

## Forward-carry

none

## Friction

none
