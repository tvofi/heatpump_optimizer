# D11 round 9 leads unit — verifier V1 (reproduce)

Box G4-V1. This unit covers the leads findings of dimension D11, read from `origin/handoff/audit-r9-evidence` at 96b89163 in a separate worktree. It was not merged into this output branch.

- Interpreter: `/home/claude/venv/bin/python` (CPython 3.14.0rc2) with `PYTHONPATH=tests/hastub`, and node 22.
- Load: load1 0.95–1.61, thread_factor 1.000. Every metric is a count.
- Only the finders' leads harnesses were re-run, under `tools/audit/round9/<dim>/leads/`. No harness was written, and no production or test file was edited.
- There is no independent (step 2) measurement beyond code reads and greps. That lens belongs to V2.

## D11-s1-71 — verify, low
- **Metric:** Probe rule frontmatters on which rules_sync parse().paths and policy_lint rulePaths() return different lists (JSON-compared)
- **Number:** divergent_cells=2 of 6 (finder same); --perturb eol -> 1 of 6; null wellformed 0 of 3; live rules 0 of 10
- **Method:** Re-ran l3_frontmatter_parsers.mjs baseline and --perturb eol (node 22)
- **Attacks:** Divergent cells are the two named shapes; zero live incidence, capability only -> low

## D11-s1-72 — verify, low
- **Metric:** Probe cells (one new job appended to a workflow file GOV's derivation counts as governance) in which entities.py's GOV pin still passes
- **Number:** escaping_cells=3 of 3, positive control 1 of 1, live_gov_missing=1 (rerun-stale-verdict) (finder same); --perturb all-files -> 0 of 3 (and baseline pin then fails on the live job)
- **Method:** Re-ran l3_gov_pin.py baseline and --perturb all-files
- **Attacks:** Positive control (job added to governance.yml) fails the pin, so the pin is not vacuous; count, contention-immune
