# BLOCKED: R11-OWNER-FEATURES-SPLIT, fixer, at the C2 sample-and-report gate

Question: the C2 sample extrapolates the design note's mutation re-key drive (section 4 rules 1 and 2) to at least 2554253 CPU-s, above the note's 100000 CPU-s report gate (at 32 cores, 8 four-core runners, about 22 h wall; on this 4-core seat about 177 h). Is the full drive authorised at that cost, sharded `--shard K/N` on N = 8 four-core runners once the parts are written, or does the orchestrator narrow or re-scope the re-key? C1 rules out re-keying any row without a drive, because a lost kill is only found by driving the row. Separately, and owed before any push in either case, section 6's `tests/ci_budgets.json` raise (`script_runs_per_push`, `script_runs_full_case_pr`, one per added script) needs the owner's confirmation under CLAUDE.md rule 2.

Base: e84856520dc4de8d70b68d67a206c6f2278351ad (the brief's head). Measured 2026-11-27, stamped 2026-11-27T14:20:11Z. No code branch is pushed; nothing in `tests/` or production is changed.

## What was run

Design note b83de87857 section 4, with the spike at dab20b60ec (`linereach.py`, `swap_run.py`, `parts.json`: step A's partition, 7 parts).

1. **Line reach recorded at the base**: `PYTHONPATH=tests/hastub:tests python3 $S/linereach.py record lines.json`. Exit 0, `@@END rc=0`, 0 `FAIL` lines, 253 `@@SPAN` markers, 19m52.7s wall.
2. **The note's cost model re-measured at this base**: `HEAD_S=6.9 linereach.py cost lines.json`.
   - 4314 rows name tests/features.py; the note's base had 4313.
   - Rows by reaching parts: 748 one, 3565 several, 1 none.
   - Rule-1 ceiling: 87032 CPU-s (mean 116.4, max 399.5).
   - Rule 2: 100948 CPU-s if the first candidate kills every row, 2166480 if every candidate is driven.
   - Rule 3: 1071 CPU-s.
3. **Seeded sample**:
   - Command: `dev/audit/harnesses/r11_owner_features_split/sample_drive.py lines.json sample.jsonl --n 200 --seed 11 --workers 4`, with `NO_BASELINE=1`.
   - The draw is `random.Random(11).sample` over rule-1 and rule-2 rows: 45 rule-1 and 155 rule-2.
   - The sample was stopped at 25 rows driven, 14704 CPU-s measured. The extrapolation already sat more than an order of magnitude past the gate, and the remaining 175 rows were about 15 h on this seat.
   - Driven: 5 rule-1 rows and 20 rule-2 rows.
4. **Extrapolation** (`extrapolate.py sample.jsonl 748 3565`; per-rule mean CPU-s per row times the rule's row count; sha1 e9b4491e of `evidence/extrapolate.out`):
   - Rule 1: 5 sampled, 4 killed. Mean 466 CPU-s per row (min 180, max 737), giving 348374.
   - Rule 2: 20 sampled, 20 killed, first candidate killed 7. 2.15 drives per row. Mean 619 CPU-s per row (min 16, max 2083), giving 2205879.
   - Total: **2554253 CPU-s**.

## How the drive emulates a part, and its limits

The parts are not written yet, so a part is emulated on the monolith:

- The plan is the part's reaching spans plus their **whole** `needs` closure. A needed span of another part stands for the binding or seed the split copies into the part's header.
- A kill is a `FAIL`, or an uncaught exception, inside the driven part's spans or the header. `@@SPAN` markers attribute each one to its span.

The note's in-part-only closure cannot run on the monolith: a row's in-part plan raised `NameError: name 'NOW' is not defined`, a T4 binding from another part. Two consequences follow:

- **Cost**: the whole-closure plan is larger than a written part's drive will be (one row: 145 spans, recorded 488.1 s, against the note's in-part plan of 57 spans, 158.3 s). The rule-1 figure overstates by that factor.
- **Rule 2 is a floor**: 6 of the 20 rule-2 kills stopped at a false kill (below), so their remaining candidates were never driven.

On either reading, the floor of the note's own model with fail-fast (rule-1 ceiling 87032 plus rule-2 floor 100948) is 187980 CPU-s, above the gate.

## Null controls

- **Drive, positive and null**: `sysid.py:SystemIdentification.identify GUARD_OFF 7025e9c1`, part `model`. The unmutated plan prints 0 in-part FAILs and completes. The mutant is killed in `sysid settle power, comfort-bounded step sizing, settle window (W2-G5)` (FAIL #779).
- **Baseline of 4 seeded killed plans, unmutated** (`baselines.py lines.json sample.jsonl --n 4 --seed 11`, sha1 8f42f992 of `evidence/baselines.out`): **1 of 4 prints an in-part FAIL**. It is `#369/#370/#1738` check "the path that proceeds still stamps a resolvable recorded_at (#363)", in part `cycle`. The cause is that the worker trees are copies without `.git`, which `fixer.md` step 2 names as failing that check.
  - 6 of the sample's 20 rule-2 kills are that check (all part `cycle`), so they are not kills.
  - Rule-2 kills confirmed: 14 of 20.
  - The full drive needs worker trees with a `.git` (worktrees).
  - A second baseline (`dhw_schedule.py:_parse_time CMP_BOUND a387ecf9`, part `actuation`, 194 spans) ends without completing, on an exception outside the part. So the whole-closure emulation is not clean on every plan.
- **Tree hygiene**: an aborted run left its in-flight mutant in each worker tree, and the first 25-row sample was driven over it. That sample is void and is not used above. The driver now rewrites every production file from the base at start and refuses a tree that still differs. A planted stale edit in one tree was removed at start. Commit e2ebade36d on this ref.

## C1 candidate

- Row: `custom_components/heatpump_optimizer/sysid.py:probe_step_hours GUARD_OFF dc9c2ceb`. Rule 1, reaching part `model`.
- In the clean sample it is not killed: 736.7 CPU-s, 192-span plan, no in-part event, 2 events outside the part, run not completed.
- That is inconclusive under this emulation, because the run ended in another part's needs span. It is the first row the written parts' drive must settle under C1.

## Not done

Nothing past C2: no splitter, no parts, no reference rewrite. The heartbeat loop reached the harness's 2 h background limit and was not restarted; checkpoints were beaten by hand after it.
