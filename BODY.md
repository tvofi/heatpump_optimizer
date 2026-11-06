Owner ruling (tvofi, 2026-11-01): a review-strength guardrail trip dispatches the planted-defect audit it names, one per tripped arm and cut, never twice for the same line; nothing for `ok` or `insufficient`; the guardrail still sets no exit code and blocks nothing; P0 = 0.28, ALPHA = 0.05 adopted. Built as a new beat job row `audit-dispatch` in `tools/audit/seat/beat_jobs.py` (job table `beatd.jobs.json`, interval 1800 s), which runs `review_strength.py --fetch --guardrail` and writes `DISPATCH: planted-defect-audit arm=<arm> cut=<first..last verdict>` once per (arm, cut), remembered in `state/audit-dispatch.json`. `carry-201.json`'s R10-FLY-YIELD-GUARD entry records the ruling. Carry 1 (stranded 13, DISPATCH-REG), Carry 2 (stranded 48, BEATD) and Carry 3 (stranded 50, BEATD) are answered together: each asks for this one dispatch, folded into R10-ORCH-LEDGER's beat job table, with the same control (a `would-trip` arm line dispatches once per arm and cut, a repeat none, `ok`/`insufficient` none), and the ruling that held them is made. `standing-dispatch.md` is unchanged. Alternative not taken: a new standalone script; the row reuses the digest, fold and memory the other rows share, so one owner holds the job table.

## Head

0bfec38fa3a35f7dcf01d8999724c67b60a13875 (merge base b88684a218923f85de66f1e8fb1833e31a76a154; origin/main had not moved at the `tools/pr/prepr.sh` run, so no second run).

## Mutation proof

Four mutants of the new row in `beat_jobs_selftest.py` MUTANTS, each killed by its named case: `audit_trip_any_arm` (ok lines trip), `audit_no_memory` (repeat re-dispatches), `audit_key_arm_only` (cut dropped from key), `audit_rc_ignored` (failed run read as a result). `python3 -I tools/audit/seat/beat_jobs.py --self-test` prints `beat_jobs self-test: 116 checks, 0 failed`.

## Null control

Cases `audit-dispatch null: a repeat of the same arm line dispatches nothing and writes no byte` and `audit-dispatch null: only ok and insufficient arm lines write no job, no digest, no memory`. Live: the bus at 2026-11-06 reads the all, cloud, local and two model arms `ok`, one model arm insufficient, and `model:sonnet` `would-trip`; so a live pass would dispatch exactly that one arm.

## Figures

- `python3 -I tools/audit/seat/beat_jobs.py --self-test`: 116 checks, 0 failed (107 at the merge base).
- `python3 -I tools/audit/seat/review_strength.py --self-test`: 116 checks, 0 failed.
- `python3 -I tools/audit/seat/beatd.py --self-test`: 119 checks, 0 failed.
- `python3 -I tools/audit/seat/review_strength.py --fetch --window X=2026-10-01T00:00Z..2026-11-06T12:00Z --guardrail`: arms as under Null control (snapshot of the bus at fetch).
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2632 ENTITY CHECKS PASSED.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `bash tools/pr/prepr.sh`: clean run, scoped gate runs `tests/entities.py` only.

The dispatch is a digest line the orchestrator's wake reads, like the other rows; no row launches a seat. A cut is keyed by the arm line's printed first..last verdict span (no year): a repeat of that span a year later would be read as the same cut.

## Red checks

none

## Forward-carry

none

## Friction

none
