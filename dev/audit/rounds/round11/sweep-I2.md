# Class sweep I2, round 11

Class I2 (bugclasses.json, status `barriered`): a measured closure or scope diverges from the real dependency graph. Findings: D0-s3-01 (verified), D3-s2-01 (weakened, hygiene), D5-s2-07 (verified).

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep-I2/enum_i2.py <repo> [--no-c] [--keep-extra PATH]`, built from the three findings' seam rules:

- **A strip-keep.** It copies `strip_earlier_rounds`' keep set from `prepare_baseline.sh` (closures.json plus `tests/` literals). It then lists every literal earlier-round path in tracked `tools/`, `dev/audit/config/`, `dev/governance/` and `.claude/workflows/` files that the strip removes.
- **B select granularity.** `tests/closure.py select` is file-level. That is one seam.
- **C plant scope.** For each D5/D6 seat, it plants `text_ledger.plant` into the seat's `files[0]` and counts the new units under that dimension.

At 28b864af6d it returns 1676 seams: A 1673, B 1, C 2.

## Controls

- **Positive:** it re-finds all three findings. A lists `dev/audit/config/bundles.json` line 16 (D0-s3-01). B is D3-s2-01. C lists `run_check[D5-s2]` with a plant into README.md that yields 0 units (D5-s2-07).
- **Null:** on a clean fixture (a git repo with an empty closures.json, one round9 file and one tools file that does not reference it) it prints A=0 and C not run. Only the constant B line remains.
- **Perturbation:**
  - Adding one line to the fixture's `tools/a.py` that opens the round9 file moves A from 0 to 1.
  - On the real tree, `--keep-extra dev/audit/rounds/round10/D15/s1/intake.py` (the finder's `keep_bundles`) moves the bundles.json seam from 1 to 0.

## Dispositions

| seam | count | disposition |
|---|---|---|
| A bundles.json:16 | 1 | **instance**, finding site D0-s3-01 |
| A tools/audit/seat/review_strength.py:722, :1237 | 1 (two reads) | **instance**, beyond the findings. Its self-test reads round10/D13/yield-probe.md, which the strip removes, so `--self-test` raises FileNotFoundError in a finder tree |
| A tools/ci/selftest_closures.json | 1598 lines | not applicable. It is a recorded closure listing compared by the CI self-test on the unstripped repository and never read in a finder tree |
| A dev/governance/config/corpus_excluded.json | 53 | not applicable. It is an exclusion list, so an absent path is excluded all the same |
| A dev/audit/config/bugclasses.json, rotation.json | 15 | not applicable. These are provenance strings and are never opened as files |
| A tools/audit/seat/codeql-triage-poll.sh:3 | 3 | not applicable. The paths filter code-scanning alerts on origin, not local files |
| A tools/audit/seat/roster_lib.py:10, :17 | 2 | not applicable. The paths appear in a docstring |
| B tests/closure.py select | 1 | **instance**, finding site D3-s2-01. It over-scopes, which is the accepted direction (RCA-BULK-2), and the strace recorder (`closure.py check`, UNDER-SCOPED) guards under-scope |
| C text_ledger run_check[D5-s2] | 1 | **instance**, finding site D5-s2-07 |
| C text_ledger run_check[D5-s1] | 1 | **instance**, beyond the findings. `files[0]` is also README.md and the plant yields 0 D5 units, so this seat's null control can never pass either |
| C other D5/D6 seats | - | guarded. The plant yields at least one unit (the enumerator's own check) |

**Beyond-finding instances: 2.** The class barrier (the strace recorder) covers only test closures. Families A and C are scopes that seat tools compute and that no barrier measures. The proposed barrier is twofold:

- `prepare_baseline.sh` should keep every round path that a tracked file outside the round directories opens (family A run as a check).
- `text_ledger.py --plant` should choose the first seat file whose plant yields units, and refuse when none does.
