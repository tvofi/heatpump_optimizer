# Runner R1 report

**Judge runner R1 (shard 1/2):** 23 rows. Shard 1/2 of JUDGE-INPUT.json batch A (46 findings), sorted by id.

## Environment

- **Python version:** 3.11.15 (CPython 3.14 unavailable; using 3.11 from system)
- **venv314:** Created with requirements from RUNNER-NOTES.md
  - numpy: 2.4.6
  - scipy: 1.17.1
  - aiohttp: 3.14.3
  - voluptuous: 0.16.0
  - pyyaml: installed
  - threadpoolctl: 3.6.0
  - orjson: 3.12.0
- **node22:** /opt/node22/bin/node v22.22.2
- **strace:** /usr/bin/strace

## Batch execution

- **Input:** tools/audit/round9/judge/JUDGE-INPUT.json (@7c7ef32)
- **Shard:** 1/2
- **Started:** 2026-09-26T13:45:08Z
- **Finished:** 2026-09-26T14:58:28Z
- **Duration:** ~73 minutes
- **Exit code:** 0 (success)

## Row findings

- **Total rows:** 23 (shard 1/2 of 46)
- **All rows:** produced (no re-takes needed)
- **Load1:** peak 2.31
- **Thread factors:** mostly 1.000, one at 1.003

**Row IDs (shard 1/2):** D0-s1-01, D0-s2-02, D1-s3-02, D1-s3-05, D1-s4-02, D1-s5-02, D10-s1-02, D11-s1-01, D11-s1-03, D11-s2-01, D11-s2-04, D13-s1-03, D14-s4-01, D2-s1-01, D2-s2-03, D2-s4-01, D4-s1-05, D6-s2-05, D8-s2-01, D8-s2-03, D9-s1-01, D9-s1-03, D9-s1-71

## Notes

- Batch A input (46 findings, 23 per shard) confirmed from commit 7c7ef32
- All rows completed successfully
- No mutations run (D3 quiet-window rule: tvofi directive)
- Output files: rows-1.json (17K), rows-1.md (2.8K)
