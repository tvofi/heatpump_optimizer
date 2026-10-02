# R9-F10.5 resume note

- branch: handoff/r9-f10-gate-infra-5 @ f3e2e445bb981eff4fef38242bcb8ac520a7afa6
- base: #1838 head 46a708150f35534344039ef0ada7f12c81c77af6 (F10.4, not yet merged); merge origin/main once it lands, then re-run fixer.md steps 2-8.
- done: --drain mode + push half in tests/mutation_table.py; mutation-ledger / mutation-ledger-push jobs in tests.yml; REQUIRED_LANES gains mutation-ledger; 0011 amendment; entities.py checks (2060 pass on py3.13); mutation proof M0-M8 all killed (M3 after the seed check was fixed).
- running: a 40-site drain demo (seed 20261002) on a scratch worktree at f3e2e445.
- next: apply the demo's pins on a scratch ref, re-run the ratchet, show idempotency; scoped gate; prepr.sh; body.
- environment traps: python3 is 3.11 here, entities.py needs 3.12+ (use a 3.13 venv with tests/requirements-ci.txt); the clone was shallow (git fetch --unshallow origin main).
- open: the ledger-writer App (hpo-ledger) and its secrets are tvofi's setup; push job is fail-soft until then.
