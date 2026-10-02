Fix review: merge d2f05c97c6e457039f7724c9d93ad4b7a9703481

PR #1831, round 1. Head d2f05c97 = code 4516c369 + docs/delivery/1831.md (one row, orchestrator's own, PROC-3). Live head re-read at posting: d2f05c97. origin/main d536fb4d = merge base; merge-tree clean (rc 0).

RESULT regen-null: uv 0.8.17 `uv pip compile` of `typing_ruler.py --print-requirements`, the header recipe flags, overrides cryptography==50.0.1 + pyopenssl==26.4.0, constrained to main's other 111 pins -> byte-identical to main's lock body (pyjwt==2.13.0).
RESULT regen-fix: same plus pyjwt==2.15.0 -> byte-identical to the head's lock body. The two differ only in the 3-line PyJWT block (regen_null_vs_fix.diff). No new transitive packages.
RESULT hashes: PyPI JSON for pyjwt 2.15.0 gives wheel 7a3742de... and sdist b11c5f97..., matching the lock; `pip download --no-deps --require-hashes` of the block verified.
RESULT imports: `git grep -nE '(^|\s)(import|from)\s+jwt\b'` returns nothing (rc 1); "pyjwt" appears only in tests/requirements-typing.txt. The other "jwt" hits are shell-built App JWTs in tools/audit/*.sh and tests.yml, not PyJWT.
RESULT install: tests.yml `typing` job installs the lock with --require-hashes --no-deps, so homeassistant's PyJWT==2.13.0 pin cannot refuse it.
RESULT checks (Python 3.13 venv from tests/requirements-ci.txt, at 4516c369): entities.py rc 0 "ALL 2031 ENTITY CHECKS PASSED"; typing_ruler.py rc 0 "ALL 11 typing-ruler source checks PASSED" (census not checked locally); structure.py "STRUCTURE RATCHET PASSED"; prepr.sh rc 0, MODE: SCOPED, claim files byte-identical, no version edit. With no venv, prepr refuses closures only because voluptuous is missing (environment, not the diff).
RESULT CI at d2f05c97 when posted: pr-contract, policy-docs, delivery-status, env-matrix, instrument-self-tests, wave-script, budget-raise-gate, hassfest, validate-hacs green. The cancelled pr-contract/budget-raise-gate runs were superseded by green re-runs. CodeQL python was still running. The `tests` workflow (fast/gate/typing) had not reported, so the mypy census against this lock is unverified until CI's typing job goes green. The Mac's green-CI precondition covers it.

Not verified by me: the mypy census and real-HA ha_contract (no Python >= 3.14.2 here, same as the fixer). Whether the 12 named GHSAs close on merge is the body's claim from the advisory data; I did not re-fetch each advisory.

Non-blocking: the tests.yml comment beside --no-deps still names only the cryptography override; it is still true, just incomplete. No budget raise, no forward-carry, no red check to answer.
