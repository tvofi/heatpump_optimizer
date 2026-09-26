# D6 round 9 leads unit — verifier V1 (reproduce)

Box G4-V1. This unit covers the leads findings of dimension D6, read from `origin/handoff/audit-r9-evidence` at 96b89163 in a separate worktree. It was not merged into this output branch.

- Interpreter: `/home/claude/venv/bin/python` (CPython 3.14.0rc2) with `PYTHONPATH=tests/hastub`, and node 22.
- Load: load1 0.95–1.61, thread_factor 1.000. Every metric is a count.
- Only the finders' leads harnesses were re-run, under `tools/audit/round9/<dim>/leads/`. No harness was written, and no production or test file was edited.
- There is no independent (step 2) measurement beyond code reads and greps. That lens belongs to V2.

## D6-s1-81 — verify, low
- **Metric:** HA core versions for which resolve_currency on core's own Config.currency default returns FALLBACK_CURRENCY
- **Number:** fallback_reached=0 of 2 (HA 2025.2.0 and 2026.2.3 both default 'EUR') (finder same); --perturb -> 2 of 2; null stub_resolves_to=SEK
- **Method:** pip download of both wheels to a mktemp dir, then l4_currency_fallback.py --wheels baseline and --perturb; spot-checked both wheels' core_config.py hardcode 'EUR'; README.md:450 claim live
- **Attacks:** Null isolates SEK to FakeHass; doc-claim mismatch, money still labelled correctly -> low
- **Note:** The HA wheels were fetched with `pip download --no-deps` into a mktemp dir (pypi is reachable here) and deleted after use.
