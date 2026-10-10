## Summary

Pre-study (R9, seat `r9-closures-scoping-prestudy`): measured decomposition of the `closures` check's cost and an alternatives analysis with a recommendation, per tvofi's request. Study only — no production change, no fix.

- The re-record step is 98.9% of the job: 53 m 35 s of a 54 m 10 s push-to-main run (job `114258919874`); the batch proof measured 54 m 45 s (job `114247906174`). The checking steps after it are 0.2 s and 0.1 s.
- Lane 3 of `tests/derive_closures.sh` is the critical path at 53 m 35 s while lanes 1-2 idle after 15 and 21 minutes; `tests/boost_drift_replay.py` alone is 29 m 26 s — 55% of the wall.
- The CI job is already scoped on PRs; the full arm runs on main pushes (rule 1's detector), workflow_dispatch batch proofs, the nightly, and full-case PRs — 7 main-push runs on 2026-10-10 alone, ~8 full arms/day.
- Today's failure is the check working: PR #2109 took the 16-second skip fast lane, and only main's full arm caught `INERT READS UNDER-APPROXIMATED` (harness_headers.py rglobs `dev/audit/rounds/round*`) 54 minutes after merge.

## Alternatives and verdicts

- (a1) scope the batch/dispatch lane by its three-dot diff, fail-closed to full — preserves rule 1; saves up to 54 min per batch dispatch.
- (a2) make `inert_reads` visible to `affected`'s skip rule — turns today's incident class into a red on the PR in ~4 min; strengthens rule 1.
- (b) content-addressed recording cache — REFUSED: the key must contain the answer before the measurement that produces it; a stale restore is a wrong closure that stays green.
- (c) split the job — this is the current design; its residual costs are exactly a1, a2 and (e).
- (d) nightly full, per-PR static — REFUSED: a wrong closure survives ~5 merges; violates "red within one merge".
- (e) rebalance the derivation lanes — found by this study; same recordings, same checks, only scheduling; ~30-33 min wall instead of 53, ~40-45% off every full arm, zero change to the guarantee.

## Recommendation

(e) first — smallest PR (`tests/derive_closures.sh` lane layout only; acceptance: next push-to-main closures job green with all 33 recordings and re-record wall <= 35 min measured on two runs), then (a2), then (a1). (b) and (d) refused.

The full document, with the cost test, per-script table, provenance for every figure and an explicit unmeasured-box, is `dev/audit/rounds/round9/prestudy/closures-scoping-prestudy.md`.

## Head

- Code head: `177bb01c30` on `handoff/r9-closures-scoping-prestudy` (one commit over origin/main `969c3a5c84`; adds only the pre-study document).
- Baseline: origin/main = `969c3a5c84` (2026-10-10).

_Requested by **tvofi**_
