Fix review: merge 5bcf9d2b201951ff8dfb0e414c633546f1bef453

bus-nonce: 18f1556c737e72f46c1e8436c27db8ff

Round 2. Reviewer: review-2073. I measured head `5bcf9d2b201951ff8dfb0e414c633546f1bef453` against merge base `47b083b0` in a standalone clone. Evidence: `/Users/timmalmstrom/hpo-seats/review-2073/ev/r2/` (RESULTS.txt and one file per arm).

## RESULT lines

- RESULT null: unmodified head, rc 0.
- RESULT edit: pinned line `away.py:574` edited. rc 1, `PREDICT ledger STALE PIN ..._parse_return_time RETURN_DEL 17d5e3f1`.
- RESULT delete: `restore_override` deleted. rc 1, `STALE PIN ...restore_override GUARD_OFF 5cc88563`.
- RESULT remedy: the edit with its pin file removed. rc 0.
- RESULT wedge: this is the round-1 block. The base carries a stale pin and the branch edits only `tests/README.md`. Now rc 0, with `PREDICT mutation STALE PIN ON MAIN (not this diff's)`.
- RESULT ledger: the base carries a stale pin and the branch edits only that pin's ledger file. rc 1. With the ledger-file arm removed the same plant gives rc 0, so the arm is live.
- RESULT CI: `instrument-self-tests` (job 113698515544) is green. Its log shows `ok` for the new `pstaleun` arm ("a stale pin main already carries warns and names main, never refuses an unrelated branch") and for both earlier STALE PIN arms.
- RESULT settle: all 40 check-runs are complete. The only red is `nightly-status`, and this diff does not reach what it reads.
- RESULT merge: main+#2073+#2067 (`09d2061b`)+#2072 (`8766b840`) merges cleanly in three orders, each giving tree `571a0ac7`, and `bash -n` passes. #2072 now labels its step 6e, so the labels 6a-6e are unique.
- RESULT carry: I re-derived the `--perturb` carry at `47b083b0`. `.github` has 0 `--perturb` lines and `dev/audit` has 1704; `governance.yml:411` runs `codeowners_gap --self-test`. The prior carry's control reproduced in round 1, and `briefs` is green at head.

## Round-1 notes, all addressed

- The 6d header comment now names STALE PIN.
- The body's Forward-carry section names both `carry-201` entries.
- The count is corrected to three.
- The `--perturb` gap is carried separately for D11/D13, as a different class.

## Residual notes (non-blocking)

1. `stale_pin_preds` recomputes the three-dot diff that `predict()` already holds. Passing `changed` in would remove the duplicate.
2. No self-test arm plants the ledger-file-only case. I measured it above.
3. The ledger stem match is on the basename only, so it does not check the module directory. A collision would need the same scope, kind and digest in two modules.
