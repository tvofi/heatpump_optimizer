Fix review: merge a0de7d9c2cee4f85edc6b9383fa28f68f7339caa

Round 2. The move from 523fd84a5 is a merge of main (#1891) plus the body re-cut; the four diff files are byte-identical between the two heads (git diff empty), so every round-1 measurement stands: scratch replay (base drops committed inert_reads, head keeps it), union-revert mutant killed (exactly the four #1886 pins), head `--single tests/entities.py` re-run (seconds-only diff), budget raise exact (1416 under 1428 at base; 1469 measured = raised cap; only that key moved; reason in the commit message), one-sentence clause, .mdc regenerated, scope clean.

Re-taken at a0de7d9c2:
- RESULT selftest: rc 0, ALL 32 pins PASSED, four #1886 pins ok.
- RESULT rules_sync --check: ok.
- RESULT body `## Red checks`: now names `budget-raise-gate` (0013 designed pre-approval refusal; clears when the labelled agent approval citing mandate 5951564627 lands — #1843's amendment does count a declared agent approval citing a tvofi MANDATE, verified against #1843 itself), `pr-contract` (named as the consequence of round 1's omission, clearing with this re-take), and `nightly-status` (main's scheduled state).
- RESULT check-runs at head: pr-contract red at 11:40Z (old body) then SUCCESS at 11:52Z with PR-BODY 0 errors — latest run green. budget-raise-gate red, named and answered. nightly-status red, answered. Everything else green (briefs, policy-docs, env-matrix, mutation, typing, closures, coverage-ratchet, hassfest).

Merge on the labelled approval; the gate re-runs green and it merges. Round-1 verdict preserved in evidence/.
