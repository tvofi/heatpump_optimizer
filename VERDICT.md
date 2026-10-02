Fix review: merge 9efd4dd4065492efd48d389ffe1827b1fe5b4a2b

bus-nonce: ac92fcf9655784ca8358014bd23063e0

Round 5. PR #1852 (R9-EG-B3a, Part of #1737). Measured head `9efd4dd4065492efd48d389ffe1827b1fe5b4a2b`, which was still the live head when this verdict was posted. No `ci:` commit followed it: `closures-autofix` and `mutation-autofix` were both skipped. The evidence directory names the head.

## The resolution delta (9efd4dd4 = e78ac301 + origin/main 68b8cb97d, which brings in #1858 `dhw_planner.py`)

`git merge-tree --write-tree e78ac3016 68b8cb97d` conflicts in exactly `tests/deployment_shape.py` and `tools/audit/round4/D6/claims.py`. The `closures.json` ledger driver resolved that file as a set. I compared the head against the automatic merge tree `070b39acd152` (`evidence/resolution_vs_mergetree.diff`). Five paths differ, and each is either a conflict or a count that the merge left stale:

- **`docs/architecture.md`** auto-merged to 68 modules and 42 HA-free, and was corrected by hand to 69 and 43. I re-derived these: 69 `*.py` files in the package, 25 importing `homeassistant` at module level, and 43 free of it. The module map lists both `payload.py` and `dhw_planner.py`.
- **`tests/deployment_shape.py`**: neither side was taken. The note now says 87 files, matching the 87 `git ls-files` entries under the package and the 87 production files in `deployment_shape.py`'s closure. The history parenthetical is in the right order: main went 85→86 with `dhw_planner.py`, then this PR went 86→87. I recomputed every pair count from the head's `closures.json`: entities/harness_headers 77, structure/typing_ruler 69, finite_boundary pairs 69 each, plan_view/solar_alignment 52, golden/env_drift 85, card/card_drift 53, and the optimality four 16. All are Jaccard 1.00 and match the note.
- **`tools/audit/round4/D6/claims.py`**: the header now reads 69 with both module steps in its history. `claims.json` and `claims.md` change only on the two 68→69 result lines. CI's `harness_headers.py` (inside `fast`, green) is what proves the regenerated output matches. I could not run `claims.py` locally, because it imports numpy.

**The PR's own diff is otherwise unchanged.** For each of the 20 files in the PR's three-dot diff, I compared the sorted added and removed lines against round 4's diff. 15 are identical, including all 5 production files, `entities.py`, the hastub edit, `closures.json`, the 5 ledger pins and `qs_rules.py`. The 5 that differ are exactly the count files above. The body's statement that `closures.json` needed no edit holds: CI's `closures` check is green on the combined table.

## CI at 9efd4dd4 (`evidence/check_runs_9efd4dd4.tsv`)

All required lanes are green: `fast (3.14)`, `mutation`, `typing`, `closures`, `coverage`, `coverage-ratchet`, `env-matrix`, `pr-contract`, `budget-raise-gate`, `delivery-status`, `policy-docs`, `hassfest`, `validate-hacs` and CodeQL. The one `cancelled` run each of `pr-contract` and `budget-raise-gate` was superseded, and a `success` sits beside each.

**The only red is `nightly-status`:** "NIGHTLY ABSENT: mutation-ledger, mutation-ledger-push did not run in that scheduled run". This is main's red. Under `fix-review.md` step 11 the diff reaches nothing that check reads, and the check is not required. The body names it all the same.

## Red checks across the range (step 11; `evidence/range_reds.txt`)

`pr-contract` printed `skip red-history` because no token was available, so the body check left every earlier head unchecked. I read each head myself:

- **2261e2a4** (round 1): `closures`, `closures-autofix`, `fast (3.14)`, `mutation`. These are the same four checks with the same causes (payload.py unclassified, the stale `_data` pin) as at 29b763d7. The body answers them under 29b763d7, and the answer covers both heads.
- **29b763d7**: the same four, answered in full with a root cause. Its `pr-contract` failure printed "red checks the body must answer: closures, closures-autofix, fast (3.14), mutation". That was the body check reporting those four as unanswered at the time. They are answered now, and `pr-contract` is green at this head.
- **0135f1ac**: `fast (3.14)`, which was main's `always()` red fixed by #1859; `mutation`; and `mutation-autofix`, which was inconclusive because of that red. All are named.
- **6cbc5661**: `mutation`, the 5 killed unpinned sites, which the `mutation-autofix` carry e78ac301 repaired; and `nightly-status`, which is main's. Both are named.
- **e78ac301**: no red.

## Carried, no production change since round 2

- **Contract:** census 0 errors (CI `typing` green). My probe inverts as designed. 0 golden type mismatches. EG-B3 reads 173 published = 173 declared, and its null control fails against round 1's `payload.py`. The M1 and M2 mutants give 2 errors each.
- **Owed to R9-EG-B3b, recorded in its brief by the orchestrator:** the enumeration check misses `setdefault`, `|=`, `update(kw=)` and constant-name keys; the `handover` store; the 23 `dict[str, object]` keys and 6 nested fields; and the overstated `untyped_payload_keys` figure.
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden/` are untouched (three-dot).

## Non-blocking body note

`## Head` opens with "`9efd4dd4…` merges the authored code head `9efd4dd4…` and then merges origin/main `68b8cb97d`, with no hand resolution". That sentence is self-referential, and "no hand resolution" is false. The next paragraph discloses the two conflicts and how they were re-derived, accurately and in full. Correcting it is a body edit only and moves no head.

Round 5. The orchestrator should confirm the `BUS` line for this head and nonce.
