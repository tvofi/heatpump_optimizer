<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: Dependabot reports PyJWT 2.13.0 advisories on `main`. The only PyJWT pin in the tree is `tests/requirements-typing.txt`, the `typing` job's hash lock, where it arrives transitively because homeassistant 2026.9.3 pins `PyJWT==2.13.0`.

After: the lock pins PyJWT 2.15.0, and the header's regenerate recipe lists `pyjwt==2.15.0` in `<overrides>` beside the existing cryptography and pyopenssl overrides, so a regeneration does not reinstate 2.13.0. CI already installs this file with `--no-deps`, so homeassistant's exact pin does not refuse the install.

How: the new body is the header's own `uv pip compile` recipe with the extra override, constrained to `main`'s other pins; it differs from `main` in the PyJWT block alone. This supersedes the Dependabot PR #1827, which carries the same version and hashes but leaves the recipe producing 2.13.0; #1827 can be closed once this merges.

Reachability: no tracked module imports `jwt`; `custom_components/heatpump_optimizer/manifest.json` requires only numpy, scipy and threadpoolctl; the typing job runs mypy, which does not execute homeassistant. No alert reaches the integration's runtime code. At a user's install, PyJWT is Home Assistant core's dependency, not this integration's.

Dismissal advice (for tvofi; nothing was dismissed): GHSA-gvp8-978c-rx2q (PYSEC-2026-4146, `decode()` mutates a caller's `options` dict) has no fixed PyJWT release, so this bump cannot close it. Dismiss it as "Vulnerable code is not actually used": the package is a typing-toolchain dependency and nothing calls `jwt.decode`. The other PyJWT advisories are fixed in 2.14.0 or 2.15.0 and close on merge: GHSA-w6j9-cwv2-h6wq, GHSA-2gx3-rcp4-g85q, GHSA-w2cx-738m-mc7w, GHSA-hxm8-2xgr-2p9m, GHSA-9v7f-9g4p-ffgj, GHSA-ffc3-869f-jxw9, GHSA-r6x4-923q-g947, GHSA-p4g4-x82p-q773, GHSA-8wjv-2p76-3863, GHSA-9j54-fg26-wv3r, GHSA-jwrc-g2q2-pq5p, GHSA-42vr-xj54-vc7v. `tests/pwlane/package-lock.json` (the other manifest Dependabot scans) returned no advisories from the npm bulk-advisory endpoint.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_015KAQ8EpXbQntbLLFWmuiUT

## Head

4516c3695d95d805b1bad44a9526bf698b2f5db3

## Mutation proof

n/a: the diff changes a hash lock and its comment; there is no production predicate to delete. The load-bearing claim is that the recipe now yields 2.15.0, and the control for it is under Null control: the same recipe without the new override reproduces `main`'s body exactly, PyJWT 2.13.0 included.

## Null control

The header's recipe with `<overrides>` holding only cryptography==50.0.1 and pyopenssl==26.4.0, constrained to `main`'s other pins, reproduces the body of `tests/requirements-typing.txt` at merge base d536fb4d64a9a4c27cd49bf63328f9bf8d2e0262 byte-for-byte (pyjwt==2.13.0). Adding pyjwt==2.15.0 to `<overrides>` reproduces this head's body byte-for-byte; the only differing block is PyJWT's. Measured 2026-10-01T20:17Z against origin/main d536fb4d.

## Figures

- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED`, running `tests/entities.py` and `tests/typing_ruler.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` (Python 3.13 venv from `tests/requirements-ci.txt`): rc=0, its final line `ALL ... ENTITY CHECKS PASSED`.
- `python3 tests/typing_ruler.py`: rc=0, every source check passed, including the lock check against `tests/typing_budgets.json`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- The PyJWT hashes: `pip download --no-deps --require-hashes` of the PyJWT block downloaded and verified both files.

Not run here: the mypy census (`HPO_TYPING_PYTHON`) and real-HA `tests/ha_contract.py`. Both need Python >= 3.14.2 for homeassistant 2026.9.3, and this cloud container has 3.14.0rc2 at most, with no 3.14.7 download available. `ha_contract.py` is outside the measured scope; CI's `typing` job is the authority for the census and installs this exact lock.

## Red checks

none

## Forward-carry

none

## Friction

none
