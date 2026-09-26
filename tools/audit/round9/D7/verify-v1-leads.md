# D7 round 9 leads unit — verifier V1 (reproduce)

Box G4-V1. This unit covers the leads findings of dimension D7, read from `origin/handoff/audit-r9-evidence` at 96b89163 in a separate worktree. It was not merged into this output branch.

- Interpreter: `/home/claude/venv/bin/python` (CPython 3.14.0rc2) with `PYTHONPATH=tests/hastub`, and node 22.
- Load: load1 0.95–1.61, thread_factor 1.000. Every metric is a count.
- Only the finders' leads harnesses were re-run, under `tools/audit/round9/<dim>/leads/`. No harness was written, and no production or test file was edited.
- There is no independent (step 2) measurement beyond code reads and greps. That lens belongs to V2.

## D7-s3-51 — verify, low
- **Metric:** Of 2 arms (CancelledError, KeyboardInterrupt from the first refresh, recovery refresh raising), arms where _async_check_a4 returns instead of propagating; plus SyntaxWarnings on compile
- **Number:** swallowed=2 of 2, control_swallowed=0 of 2, syntax_warnings=1 (finder same); --fixed -> 0 / 0
- **Method:** Re-ran nightly_finally_return.py baseline and --fixed (on Python 3.11.15, not 3.14; number identical); read tests/nightly_ha.py:1266-1281
- **Attacks:** Null control (recovery succeeds) 0 of 2; mechanism confirmed by reading; nightly-lane code, rare window -> low
- **Note:** Ran on system Python 3.11.15 rather than 3.14. The SyntaxWarning and both counts were identical, so the interpreter did not move the number.

## D7-s1-71 — verify, low
- **Metric:** Of 5 production sites resolving a cold-water inlet default, those whose delivered value does not move when const.DEFAULT_DHW_INLET_TEMP is moved 10.0 -> 12.5
- **Number:** sites_not_following=3 of 5 (finder same); --no-move 0 of 5; --perturb literal -> 1 of 5
- **Method:** Re-ran l3_cold_water_default.py in all three modes
- **Attacks:** Per-site values show three spellings of the default; null shows no live divergence today -> hygiene low

## D7-s3-72 — verify, low
- **Metric:** ThermalModel _step_* members with >=1 production write and 0 reads from production functions that never write that member, over four golden solves
- **Number:** write_only_members=4 of 5 (finder same); live control _step_buffer_refused 97344 consumer reads; --perturb reader -> 3 of 5
- **Method:** Re-ran l3_write_only_scratch.py baseline and --perturb reader over the four golden scenarios
- **Attacks:** Live control proves the read instrumentation detects real consumers; 4 scenarios (<5, leave-one-out not owed), each with large write counts
