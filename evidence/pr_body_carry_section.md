Root-cause record for the recurring "API rate limit exceeded for installation" reds. Round 2.

- **Cause.** The bucket's size is unmeasured. At least about 3,030 calls were served from 08:03:46Z. The 83 % and the 3.2 to 4.6 times the bucket are withdrawn.

## Forward-carry

- Countermeasure M0 to M2 (`governance.yml` `record`, `tools/policy/policy_lint.mjs`); decision O-1 on M3 taken only after M0's measured limit; the M1 + M2 run count (about 5 runs, about 1,850 calls on the 08Z replay) measured by the fixer; HANDOVER item 44's "shared App quota" corrected to the `GITHUB_TOKEN` bucket at that merge (`dev/audit/rca/install-ratelimit.md` sections 4 and 5). Carry: R10-RECORD-API-BUDGET
- `dev/audit/harnesses/record_api_calls.sh` prints `TOTAL 0` with exit 0 when origin is not a github remote (the `subject` enumerator runs, no `curl`), which meets M1's "370 or less"; it should refuse a zero on a non-empty window. Carry: R10-RECORD-API-BUDGET
- `dev/audit/harnesses/record_api_calls.sh` counts a partial abort: it exits only on `curl failed`, so an `HTTP 403 from ...` or `unparseable JSON ...` fetch error ends a mode early and prints the early count as the total (review mutant: 96 instead of 278 per mode, exit 0). Carry: R10-RECORD-API-BUDGET
- An exhausted hourly bucket returns a 403 that is not transient. A retry must wait until the reset time the 403 names, and must never loop. Carry: R10-FLY-GH-READ-RETRY
