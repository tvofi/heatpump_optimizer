# tests.yml CI duration measurement

Source (fetched read-only by `fetch.sh`, the same REST endpoints the GitHub MCP `actions_list` tool wraps): GitHub REST `actions/workflows/tests.yml/runs` and `actions/runs/<id>/jobs?filter=latest`, saved under `raw/`; computed by `measure.py`.
Percentiles are nearest-rank; median is the usual midpoint median. 'executed' = job conclusion is not `skipped` (includes success, failure, cancelled). Skipped jobs count 0 s. Duration stats (median/p90/max) are over executed jobs that concluded success or failure only; cancelled jobs are counted but excluded, since a superseded run's cancel truncates them (some never started: completed_at precedes started_at, clamped to 0 s in jobs.tsv). jobs.tsv holds every job row of every run used in all three sections.
Job names are taken verbatim: a matrix job that was skipped appears under its unexpanded name (`nightly-ha`, `mutation-pins`), an executed one under its expanded name (`nightly-ha (2025.2.0)`, `mutation-pins (1)`); some older runs name the fast lane `fast` instead of `fast (3.14)`.

## Pull-request runs (20 most recent completed)

- runs used: 20 (of 30 listed on the first page; API total_count 2500)
- date range (created_at): 2026-10-18T17:06:56Z .. 2026-10-18T19:19:59Z
- skipped as cancelled-with-no-completed-jobs: 39156531115, 39151682075
- run conclusions: cancelled 2, failure 4, success 14
- per-run wall clock, all runs used incl. cancelled (max job completed_at - run_started_at): median 2059 s (34:19), p90 3861 s (64:21), max 4175 s (69:35)

### Per job name

| job | executed | skipped | conclusions (executed) | median s | p90 s | max s |
|---|---|---|---|---|---|---|
| `briefs` | 20 | 0 | success 20 | 27.5 | 29 | 35 |
| `browser` | 20 | 0 | cancelled 1, success 19 | 241 | 248 | 255 |
| `cancel-superseded` | 7 | 3 | success 7 | 8 | 10 | 10 |
| `ci-ratchet` | 2 | 18 | cancelled 2 | - | - | - |
| `claims-autofix` | 3 | 17 | cancelled 1, success 2 | 15.5 | 17 | 17 |
| `closure-scope` | 20 | 0 | success 20 | 19 | 21 | 21 |
| `closures` | 20 | 0 | cancelled 2, success 18 | 1088 | 1576 | 1601 |
| `closures-autofix` | 2 | 18 | cancelled 2 | - | - | - |
| `composed-proof` | 20 | 0 | cancelled 2, success 18 | 16 | 1220 | 1242 |
| `coverage` | 20 | 0 | success 20 | 969.5 | 1244 | 1349 |
| `coverage-ratchet` | 20 | 0 | success 20 | 9.5 | 11 | 12 |
| `fast (3.14)` | 20 | 0 | cancelled 1, failure 2, success 17 | 1241 | 2661 | 2895 |
| `graders-head-copy` | 20 | 0 | success 20 | 18 | 97 | 122 |
| `lane-proofs` | 20 | 0 | cancelled 1, success 19 | 6 | 8 | 8 |
| `mutation` | 20 | 0 | failure 2, success 18 | 35.5 | 836 | 2140 |
| `mutation-autofix` | 2 | 18 | success 2 | 28 | 36 | 36 |
| `mutation-ledger` | 0 | 20 | - | - | - | - |
| `mutation-ledger-push` | 0 | 20 | - | - | - | - |
| `mutation-nightly` | 0 | 20 | - | - | - | - |
| `mutation-pin-plan` | 2 | 18 | success 2 | 16 | 17 | 17 |
| `mutation-pins` | 0 | 18 | - | - | - | - |
| `mutation-pins (1)` | 2 | 0 | success 2 | 2940 | 3899 | 3899 |
| `nightly-ha` | 0 | 18 | - | - | - | - |
| `nightly-ha (2025.2.0)` | 2 | 0 | success 2 | 145.5 | 156 | 156 |
| `nightly-ha (stable)` | 2 | 0 | success 2 | 173.5 | 175 | 175 |
| `nightly-status` | 20 | 0 | success 20 | 10 | 12 | 13 |
| `recheck-gate` | 0 | 20 | - | - | - | - |
| `record-autofix` | 0 | 20 | - | - | - | - |
| `slow` | 0 | 20 | - | - | - | - |
| `typing` | 20 | 0 | success 20 | 79 | 91 | 94 |

### Runs used

| run id | PR | head sha | attempt | conclusion | created_at | wall s |
|---|---|---|---|---|---|---|
| 39158277850 | 2420 | b0140e47bc | 1 | success | 2026-10-18T19:19:59Z | 1917 |
| 39158231320 | 2415 | 0e238c3042 | 2 | success | 2026-10-18T19:19:22Z | 2314 |
| 39156534701 | 2420 | 0f145d4fae | 1 | cancelled | 2026-10-18T18:57:29Z | 1405 |
| 39155370055 | 2419 | b54a2f2e55 | 1 | success | 2026-10-18T18:42:14Z | 1131 |
| 39154182950 | 2415 | 87c579404d | 1 | success | 2026-10-18T18:26:47Z | 2967 |
| 39153860761 | - | 319769bb4f | 1 | success | 2026-10-18T18:22:26Z | 1218 |
| 39153812016 | - | 8d4e8be01c | 1 | success | 2026-10-18T18:21:49Z | 1453 |
| 39153372062 | 2399 | acf14d8f22 | 2 | success | 2026-10-18T18:16:03Z | 3004 |
| 39153364517 | 2391 | 3aba8f1eb2 | 2 | success | 2026-10-18T18:15:58Z | 4175 |
| 39152091270 | - | 311e9de3e0 | 1 | success | 2026-10-18T17:59:41Z | 2619 |
| 39151687395 | 2420 | 4be8f4cfd0 | 1 | success | 2026-10-18T17:54:05Z | 1802 |
| 39151673429 | 2399 | b931d0f44a | 1 | success | 2026-10-18T17:53:53Z | 2201 |
| 39151671544 | 2406 | d1becac2b3 | 1 | failure | 2026-10-18T17:53:51Z | 3861 |
| 39150747003 | 2368 | c3a25d2ae3 | 1 | failure | 2026-10-18T17:41:29Z | 1858 |
| 39150736179 | 2391 | aa82837c57 | 1 | failure | 2026-10-18T17:41:20Z | 2398 |
| 39150084062 | - | 1450760447 | 1 | success | 2026-10-18T17:32:47Z | 3449 |
| 39148893518 | 2411 | 74d66b3554 | 2 | failure | 2026-10-18T17:17:31Z | 4063 |
| 39148592346 | - | 7bda397d12 | 1 | success | 2026-10-18T17:13:38Z | 962 |
| 39148193627 | 2417 | c83ae12acc | 1 | success | 2026-10-18T17:08:25Z | 360 |
| 39148082068 | 2417 | 6c0218b0d5 | 1 | cancelled | 2026-10-18T17:06:56Z | 115 |

## Push to main (5 most recent completed)

- runs used: 5 (of 5 listed on the first page; API total_count 1504)
- date range (created_at): 2026-10-18T18:51:41Z .. 2026-10-18T19:18:12Z
- skipped as cancelled-with-no-completed-jobs: none
- run conclusions: failure 2, success 3
- per-run wall clock, all runs used incl. cancelled (max job completed_at - run_started_at): median 2963 s (49:23), p90 2988 s (49:48), max 2988 s (49:48)

### Per job name

| job | executed | skipped | conclusions (executed) | median s | p90 s | max s |
|---|---|---|---|---|---|---|
| `briefs` | 5 | 0 | success 5 | 28 | 31 | 31 |
| `browser` | 5 | 0 | success 5 | 236 | 242 | 242 |
| `cancel-superseded` | 0 | 5 | - | - | - | - |
| `ci-ratchet` | 5 | 0 | success 5 | 56 | 62 | 62 |
| `claims-autofix` | 0 | 5 | - | - | - | - |
| `closure-scope` | 0 | 5 | - | - | - | - |
| `closures` | 5 | 0 | success 5 | 1554 | 1713 | 1713 |
| `closures-autofix` | 0 | 5 | - | - | - | - |
| `composed-proof` | 0 | 5 | - | - | - | - |
| `coverage` | 5 | 0 | success 5 | 1018 | 1240 | 1240 |
| `coverage-ratchet` | 5 | 0 | success 5 | 8 | 10 | 10 |
| `fast (3.14)` | 5 | 0 | success 5 | 2893 | 2937 | 2937 |
| `graders-head-copy` | 0 | 5 | - | - | - | - |
| `lane-proofs` | 0 | 5 | - | - | - | - |
| `mutation` | 5 | 0 | success 5 | 35 | 38 | 38 |
| `mutation-autofix` | 0 | 5 | - | - | - | - |
| `mutation-ledger` | 0 | 5 | - | - | - | - |
| `mutation-ledger-push` | 0 | 5 | - | - | - | - |
| `mutation-nightly` | 0 | 5 | - | - | - | - |
| `mutation-pin-plan` | 0 | 5 | - | - | - | - |
| `mutation-pins` | 0 | 5 | - | - | - | - |
| `nightly-ha` | 0 | 5 | - | - | - | - |
| `nightly-status` | 0 | 5 | - | - | - | - |
| `recheck-gate` | 0 | 5 | - | - | - | - |
| `record-autofix` | 5 | 0 | failure 2, success 3 | 119 | 162 | 162 |
| `slow` | 0 | 5 | - | - | - | - |
| `typing` | 5 | 0 | success 5 | 89 | 95 | 95 |

### Runs used

| run id | PR | head sha | attempt | conclusion | created_at | wall s |
|---|---|---|---|---|---|---|
| 39158143952 | - | 07a09406a1 | 1 | success | 2026-10-18T19:18:12Z | 2647 |
| 39156632994 | - | 5756f2b157 | 1 | failure | 2026-10-18T18:58:52Z | 2882 |
| 39156299791 | - | 86010e8cd8 | 1 | success | 2026-10-18T18:54:19Z | 2963 |
| 39156244284 | - | fd64a23e98 | 1 | failure | 2026-10-18T18:53:36Z | 2970 |
| 39156099096 | - | 3d46d694d7 | 1 | success | 2026-10-18T18:51:41Z | 2988 |

## Schedule (5 most recent completed)

- runs used: 5 (of 5 listed on the first page; API total_count 53)
- date range (created_at): 2026-10-14T07:41:52Z .. 2026-10-18T07:15:29Z
- skipped as cancelled-with-no-completed-jobs: none
- run conclusions: failure 1, success 4
- per-run wall clock, all runs used incl. cancelled (max job completed_at - run_started_at): median 13836 s (230:36), p90 14535 s (242:15), max 14535 s (242:15)

### Per job name

| job | executed | skipped | conclusions (executed) | median s | p90 s | max s |
|---|---|---|---|---|---|---|
| `briefs` | 0 | 5 | - | - | - | - |
| `browser` | 0 | 5 | - | - | - | - |
| `ci-ratchet` | 0 | 5 | - | - | - | - |
| `claims-autofix` | 0 | 5 | - | - | - | - |
| `closure-scope` | 0 | 5 | - | - | - | - |
| `closures` | 5 | 0 | success 5 | 1676 | 1701 | 1701 |
| `closures-autofix` | 0 | 5 | - | - | - | - |
| `composed-proof` | 5 | 0 | success 5 | 16 | 21 | 21 |
| `coverage` | 5 | 0 | success 5 | 827 | 1159 | 1159 |
| `coverage-ratchet` | 0 | 5 | - | - | - | - |
| `fast` | 0 | 5 | - | - | - | - |
| `graders-head-copy` | 0 | 5 | - | - | - | - |
| `lane-proofs` | 0 | 5 | - | - | - | - |
| `mutation` | 0 | 5 | - | - | - | - |
| `mutation-autofix` | 0 | 5 | - | - | - | - |
| `mutation-ledger` | 5 | 0 | success 5 | 12585 | 14495 | 14495 |
| `mutation-ledger-push` | 5 | 0 | success 5 | 19 | 31 | 31 |
| `mutation-nightly` | 5 | 0 | success 5 | 6485 | 14152 | 14152 |
| `mutation-pin-plan` | 0 | 5 | - | - | - | - |
| `mutation-pins` | 0 | 5 | - | - | - | - |
| `nightly-ha (2025.2.0)` | 5 | 0 | success 5 | 145 | 169 | 169 |
| `nightly-ha (stable)` | 5 | 0 | success 5 | 171 | 179 | 179 |
| `nightly-status` | 0 | 5 | - | - | - | - |
| `recheck-gate` | 0 | 5 | - | - | - | - |
| `record-autofix` | 5 | 0 | success 5 | 84 | 95 | 95 |
| `slow` | 5 | 0 | failure 1, success 4 | 561 | 735 | 735 |
| `typing` | 0 | 5 | - | - | - | - |

### Runs used

| run id | PR | head sha | attempt | conclusion | created_at | wall s |
|---|---|---|---|---|---|---|
| 39106988523 | - | 994695e06c | 1 | success | 2026-10-18T07:15:29Z | 11053 |
| 39011974246 | - | e3f3b312ff | 1 | success | 2026-10-17T06:59:54Z | 12499 |
| 38866008546 | - | aca6ea4567 | 1 | success | 2026-10-16T07:14:59Z | 14156 |
| 38699166296 | - | 9061fbd3d7 | 1 | success | 2026-10-15T07:30:06Z | 14535 |
| 38530020347 | - | 9111acceb7 | 1 | failure | 2026-10-14T07:41:52Z | 13836 |

## Scheduled-lane jobs only, push/main + schedule runs combined

| job | executed | skipped | conclusions (executed) | median s | p90 s | max s |
|---|---|---|---|---|---|---|
| `composed-proof` | 5 | 5 | success 5 | 16 | 21 | 21 |
| `coverage` | 10 | 0 | success 10 | 973 | 1204 | 1240 |
| `mutation-ledger` | 5 | 5 | success 5 | 12585 | 14495 | 14495 |
| `mutation-nightly` | 5 | 5 | success 5 | 6485 | 14152 | 14152 |
| `nightly-ha` | 0 | 5 | - | - | - | - |
| `nightly-ha (2025.2.0)` | 5 | 0 | success 5 | 145 | 169 | 169 |
| `nightly-ha (stable)` | 5 | 0 | success 5 | 171 | 179 | 179 |
| `record-autofix` | 10 | 0 | failure 2, success 8 | 93.5 | 157 | 162 |
| `slow` | 5 | 5 | failure 1, success 4 | 561 | 735 | 735 |
