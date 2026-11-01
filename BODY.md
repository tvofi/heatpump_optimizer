deps(tests): the pip group's bumps from Dependabot #3088, re-applied by the fixer, with homeassistant-stubs held at 2026.9.3

Supersedes #3088

The owner asked for this on 2026-11-01. Dependabot's branch cannot be edited, so this branch re-applies the version changes from #3088 (head bffd45a03, base d052f80f7) to the four test requirement files, cut from main. The four files are byte-identical between d052f80f7 and main. The bumps are #3088's, except one pin held back (below). The reds at #3088's head were bisected to four causes:

1. **Stale hashes on three pins.** Dependabot changed the version of coverage 7.17.0, cryptography 50.0.2 and uv 0.13.6 and kept the previous version's `--hash` lines, so pip's hash-checking mode refused each install. That turned `tests / coverage` red (`coverage-ratchet` then had no `coverage-json` artifact) and `tests / typing` red. Each block now holds every sha256 PyPI publishes for that version. The coverage block is its header's compile; the typing lock body reproduces byte-identically from its header's compile (below).
2. **The ruler's pinned pair.** `tests/typing_ruler.py`'s source-only check in `fast` refuses a lock whose mypy or homeassistant-stubs pin disagrees with `tests/typing_budgets.json`'s `ruler`. That was the one failed script in `tests / fast (3.14)`. `ruler.mypy` moves 2.3.1 -> 2.4.1. **The budget-raise gate reads that key as frozen, so this needs tvofi's approving review** (`## Raise justification`).
3. **homeassistant-stubs 2026.10.0 is held back at 2026.9.3** (Carry below). 2026.10.0 is an empty release that deprecates the package; its PyPI summary is "Deprecated: Home Assistant Core ships its own type information". Under it mypy reads Home Assistant's own py.typed annotations, and the ruler's census goes from 0 to 70 errors. CI never reached that, because the typing install failed first. Moving the ruler off the stubs changes what the census measures, so it is a design change, not a version bump. homeassistant 2026.10.4 still lands, as a lock override, because stubs 2026.9.3 pin homeassistant==2026.9.3.
4. **mypy 2.4.1's `reversed()`.** Its overload returns `Any` for a sequence whose element type holds `Any`. `SnapshotRing.best_restore` returned the loop variable, which made one `no-any-return` error. `learner_progress.snapshot_rates` lost its loop type with no error. Both loop variables are now declared before the loop.

Until a seat's venv-ha is rebuilt from this lock, that seat's `python3 tests/typing_ruler.py` refuses `mypy is pinned at 2.4.1  [found 2.3.1]` (guard 2, measured on this seat's `/opt/hpo/venv-ha`). That is the guard working; `HPO_TYPING_PYTHON` pointed at a venv built from this lock reads `ALL 12 typing-ruler source checks PASSED`.

One break that no CI check covers: `tools/audit/seat/cloud-setup.sh` and `tools/audit/seat/seat_venv.sh` asserted `homeassistant == "2026.9.3"` in the venv-ha they build from the typing lock. Under `set -euo pipefail`, the cloud setup script would exit 1 once the lock moved. Both now read the version from the lock's `homeassistant==` line. **The environment's pasted setup script still holds the literal**, so tvofi re-pastes `tools/audit/seat/cloud-setup.sh` once this merges (Forward-carry).

Header text the bumps made false is corrected. PyYAML 6.0.3 installs from a wheel, so nothing in the ci lock builds from an sdist, and Cython's `<3.0` bound belonged to 6.0.1. The typing overrides are now the set `pip check` lists, and the pyjwt, aiohttp and yarl overrides are gone because homeassistant 2026.10.4 pins those itself. Every other bump in #3088 (numpy 2.5.4, scipy 1.18.1, threadpoolctl 3.7.0, multidict 7.2.1, pyyaml 6.0.3, cython 3.3.0, setuptools 84.2.1 and the rest of the typing lock) needed no change: at #3088's head `tests / fast (3.14)` passed every script but `typing_ruler.py`, `env_drift.py --all` included, with this branch's ci lock byte-for-byte.

## Head

7d56a8934d40b3969eb61e097c4003d445e3ec14

origin/main at c88d552c76f1ae11a879ce7ccb8d8dc29adabf50, merged in (`date -u` Sun Nov  1 19:19:22 UTC 2026). Main moved twice during the work, both times with no conflict: from ca6333333 to 407eb0cb3 (#3049, `tools/audit/seat/` only), then to c88d552c7 (#3051, #3074: the gate lease, prepr, carry_audit, the handover and their tests; none of the files this diff changes or the figures below read). The merge was followed by a second `tools/pr/prepr.sh` run, body check included, and by re-runs of the seat self-tests, the seat mutation, the typing census and the architecture score on the merged tree.

## Mutation proof

- The seat assertion: replace `"$ha_pin"` with the old literal `2026.9.3` in `seat_venv.sh`'s `check()`. Then `bash tools/audit/seat/seat_venv.sh --self-test` reads `FAIL --check accepts a venv-ha at the typing lock's homeassistant pin (2026.10.4)`, `25 checks, 1 failed`. Restored, it reads `25 checks, 0 failed`. The same arm, written before the fix and run on the bumped lock, failed the same way (`23 checks, 1 failed`).
- The `reversed()` declaration: delete `snap: dict[str, Any]` in `snapshots.py`. Then the ruler's mypy invocation under the final lock reads 1 error, `snapshots.py:225: error: Returning Any from function declared to return "dict[str, Any] | None"  [no-any-return]` (measured in the bisect venv, mypy 2.4.1 + stubs 2026.9.3). Restored, it reads 0.
- The stubs hold-back: put homeassistant-stubs back at 2026.10.0. Then `python tests/typing_ruler.py --mypy` reads `FAIL errors did not grow  [recorded 0, measured 70 (+70)]` (69 after the `reversed()` fix).

## Null control

- main's typing toolchain (mypy 2.3.1, stubs 2026.9.3) on main's tree: `/opt/hpo/venv-ha/bin/python tests/typing_ruler.py --mypy` reads `ALL 9 typing-ruler checks PASSED`, `errors did not grow`. main passes typing, so the 70 belong to the bump.
- The bisect's own control: the unmodified re-applied venv (no package swapped) reproduces 70.
- The seat arm's null control: a venv-ha at `0.0.0` is refused by `--check` (`ok --check refuses a venv-ha off the lock's pin (null control)`).
- The lock recipe's control: the same compile with the override set minus `homeassistant==2026.10.4` is unsatisfiable. With the 4 overrides the old header named, it is unsatisfiable too (python-dateutil 3.0.0 against botocore's `<3.0.0`).
- main's coverage lock installs (`pip install --require-hashes --no-deps -r tests/requirements-coverage.txt` at main), and #3088's refuses with `THESE PACKAGES DO NOT MATCH THE HASHES`.

## Figures

- Reds at #3088's head bffd45a03: the check runs of PR #3088 (one page of 55). Concluded `failure`: `tests / fast (3.14)`, `tests / typing`, `tests / coverage`, `tests / coverage-ratchet`, `pr-contract / pr-contract` and `gate` (twice, one per run). That matches the brief's list.
- Stale hashes, 3 of 131 pins in #3088's four files: each `name==version` block's `--hash` set compared with the sha256 set of `https://pypi.org/pypi/<name>/<version>/json`'s `urls`. coverage 7.17.0 lists 92 hashes, 0 of PyPI's 119. cryptography 50.0.2 lists 46, 0 of 59. uv 0.13.6 lists 19, 0 of 19. Every other pin's set equals PyPI's. Reproduced by `pip install --require-hashes --no-deps -r <file at bffd45a03>` (refused for coverage) and by the CI logs of `tests / typing` and `tests / coverage` at that head. At this head the same comparison finds no mismatch in any of the four files, and the `pip install` of each lock exits 0: the ci lock on CPython 3.14.7 with `--build-constraint tests/requirements-build.txt`; the typing lock `--no-deps` on 3.14.7; the coverage lock on 3.13.
- Typing census bisect, the ruler's invocation (`mypy --strict --warn-unused-ignores --show-error-codes --no-error-summary --no-incremental --python-version 3.14 custom_components/heatpump_optimizer`, as `run_mypy` in `tests/typing_ruler.py` builds it), in a copy of the re-applied venv with one group put back at main's pin. None swapped: 70. homeassistant-stubs 2026.9.3: 1. mypy 2.3.1 (with librt 0.15.0, ast-serialize 0.11.2): 69. homeassistant 2026.9.3: 43. Each figure is a count of `error:` lines, and each run printed at least one, so none was a crashed run read as clean.
- Final census at this head: `python tests/typing_ruler.py --mypy --emit <file>` run by a venv built from this branch's typing lock: `ALL 9 typing-ruler checks PASSED`, errors 0, by_code `{}`, environment mypy 2.4.1, homeassistant-stubs 2026.9.3, numpy 2.5.4, scipy-stubs 1.18.1.1.
- `pip check` on that venv lists 12 disagreements. Those are the 12 non-pyopenssl entries the typing header's override paragraph names (pyopenssl is the 13th override, a cap the compile needs), and the header's compile with those 13 overrides reproduces the lock body byte-identically (`diff` exit 0).
- The class seam for item 4: `git grep -n 'reversed(' -- custom_components/` returns 3 sites. `snapshots.py` `best_restore`: closed in this diff. `learner_progress.py` `snapshot_rates`: closed in this diff; `reveal_type(snap)` under mypy 2.4.1 reads `Any` at main and `typing.Mapping[str, Any]` here. `optimizer.py` `reversed(range(n))`: an `int` range carries no `Any`, so it is unaffected.
- `bash tools/audit/seat/seat_venv.sh --self-test`: `25 checks, 0 failed`. `bash tools/audit/seat/cloud-setup.sh --self-test`: `13 checks, 0 failed`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `python3 tools/audit/archscore/score.py --diff <merge base> HEAD`: `Architecture score: dS +0.0000 NULL`.
- Gate scope, `tests/closure.py select --diff <merge base>`: `MODE: FULL` (`tests/requirements-build.txt changes the gate itself`). The suite is CI's; locally this ran the typing ruler (source and census), structure, the two seat self-tests, and on a CPython 3.14.7 venv built from this branch's ci lock with `PYTHONPATH=tests/hastub` and `GOLDEN_MODE=drift`: `tests/features.py`, `tests/entities.py`, `tests/finite_boundary.py` and `tests/deployment_shape.py` (each exit 0; the first two cover `snapshots.py` and `learner_progress.py`), and `tests/env_drift.py --all ca6333333afc1ec7937b9792880458d190f4d4d2`: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56 committed fixture(s)`. That was run against the pre-merge base; the merged delta touches no fixture or production module. Both claim files, `VERSION`, the manifest and `RELEASE_NOTES.md` are byte-identical to origin/main.

## Raise justification

`tests/typing_budgets.json` `ruler.mypy` moves 2.3.1 -> 2.4.1. It is the version the census is measured with, and `ruler.**` is frozen for `tools/policy/budget_raise_gate.py`. No cap moves: `census.errors` stays 0, `by_code` empty, `type_ignores` 0.
Payments tried: none in code. No code payment can satisfy this key. The only alternative is holding mypy at 2.3.1, which drops one of #3088's bumps that lands cleanly (census 0 at 2.4.1 once the `reversed()` loops are declared), and the brief holds back only what cannot land. homeassistant-stubs, which could not land, is held, so its half of the pair does not move.
Architecture score: dS +0.0000 NULL

## Red checks

At this head: none. No check has run, because the pull request is not open and the step ref started no workflow (`list_workflow_runs` for `handoff-wip/r10-deps-pip-bump` returns 0). The reds of #3088 this branch answers, under `defect-root-cause.md`'s second trigger:
- `tests / coverage`, `tests / coverage-ratchet`, `tests / typing`: stale hashes on a version bump. A cheaper detector exists: the per-pin comparison in `## Figures` (one PyPI JSON read per changed pin, seconds per lock), run on a Dependabot pull request before the jobs install. None is in the tree; its standing cost is one network read per changed pin per Dependabot push. Not built here (Forward-carry).
- `tests / fast (3.14)`: `typing_ruler.py`'s source-only lock check is already the cheap detector (0 s, in the source lane); it fired as designed.
- `budget-raise-gate`: red at this head by construction until tvofi's approving review at the head, because `tests/typing_budgets.json` `ruler.mypy` moves 2.3.1 -> 2.4.1, a frozen key (`## Raise justification`). This is not a defect: the gate reads the diff alone and is already the cheapest detector, so none cheaper exists.
- `pr-contract / pr-contract` and `gate`: a Dependabot body carries none of the template's headings. That is the reason for this replacement, not a defect.

## Forward-carry

- homeassistant-stubs held at 2026.9.3, and with it moving the typing ruler off the stubs onto homeassistant's py.typed (69 errors at homeassistant 2026.10.4): `dev/programme/carries/carry-201.json`, last entry (`from` R10-DEPS-PIP-BUMP). Carry: #201
- After merge, tvofi re-pastes `tools/audit/seat/cloud-setup.sh` into the environment's setup script: the pasted copy asserts homeassistant 2026.9.3 and refuses the moved lock. Carry: #201
- A stale-hash detector for Dependabot pip bumps, from the red-check answer above. Not built, by the cost test: it repeats what the jobs' own `--require-hashes` install reports one step later, which only Dependabot branches reach; the fixer replacement route catches it at the same cost. Carry: dismissed: the install step already detects it

## Friction

none

## Unpinned sites

none: `tools/pr/prepr.sh` step 6d lists no site this diff adds.

## Architecture score

dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff <merge base> HEAD`).
