deps(tests): the pip group's bumps from Dependabot #3323, re-applied with hashes that install, homeassistant-stubs, zeroconf and cronsim held

Supersedes #3323

Dependabot's branch cannot be edited, so this branch re-applies #3323's version changes (head da3a5cfb8, base 4fe7d5934) to the five test locks. It is cut from main b07627250, and the five files are byte-identical between 4fe7d5934 and that main. This is the same shape as #3088 / #3147. The reds at #3323's head come from two causes:

1. **Stale hashes on five pins.** Dependabot changed the version and kept the previous version's `--hash` lines for coverage 7.17.2 (`requirements-coverage.txt`), and for acme 5.9.0, python-dateutil 4.0.0, sqlalchemy 2.1.8 and uv 0.13.7 (`requirements-typing.txt`). The last four are exactly the typing lock's overrides that the PR moved, the same pattern as #3088's cryptography and uv. pip's hash-checking mode refused the install, which turned `tests / typing` red and `tests / coverage` red. `tests / coverage-ratchet` then had no `coverage-json` artifact. The coverage block is now its header's compile. The typing body is the header's single-package route: this lock as input, those four packages' hash lines deleted, and the override set moved to the new versions.
2. **homeassistant-stubs 2026.10.0.** `tests/typing_ruler.py`'s source-only lock check refuses a lock whose stubs pin disagrees with `tests/typing_budgets.json`'s `ruler`. That was the one failed script in `tests / fast (3.14)`. b9c009a6b held the stubs at 2026.9.3 on purpose: 2026.10.0 is the empty deprecation release, and it changes what the census measures. The stubs therefore stay at 2026.9.3 and no budget moves.

Two of #3323's bumps cannot be compiled under the lock's own rule. homeassistant 2026.10.4 pins `zeroconf==0.151.5` and `cronsim==2.7` exactly, so 0.153.0 and 2.8 are unsatisfiable unless each becomes a new override. Both stay at homeassistant's pin. The override set does not grow, and nothing here needs either version. Every other bump lands as #3323 wrote it: anyio, boto3, botocore, grpcio, mypy-extensions and threadpoolctl in the typing lock, threadpoolctl 3.8.0 in the ci lock, and cython 3.3.1 in the build lock. The ci and build locks are byte-identical to #3323's. py-spy 0.4.3 keeps the nightly-ha lock's documented shape, the two Linux wheels, instead of #3323's nine distributions, so that lock's header stays true.

Text the bump made false is corrected. The typing header names the moved overrides and the held pins. `.github/dependabot.yml` said Dependabot rewrites every hash line of a package it bumps, which was false twice. It now says which pins Dependabot leaves stale and how such a pull request is re-applied.

## Head

a555d52ae875732c290b1847e0b4709826711335

origin/main at b0762725099fefd337fc74ecff161cb487a992bc (`date -u` Tue Nov 10 02:35:05 UTC 2026).

## Mutation proof

- The stale-hash repair: put #3323's `requirements-coverage.txt` back. Then `pip download --require-hashes --no-deps --only-binary=:all: --platform manylinux_2_28_x86_64 ... --python-version 3.13 -r tests/requirements-coverage.txt` exits 1 with `THESE PACKAGES DO NOT MATCH THE HASHES` for `coverage==7.17.2`. The typing lock does the same at 3.14.7 for `acme==5.9.0`: pip stops at the first mismatch, and the per-pin comparison in `## Figures` names all four. This branch's locks exit 0. CI's `tests / coverage` and `tests / typing` logs at da3a5cfb8 show the same refusal, with the same `Got` digest for coverage.
- The stubs hold: put #3323's `requirements-typing.txt` in this tree. Then `python tests/typing_ruler.py` reads `FAIL the typing job's hashed lock installs the recorded pins [homeassistant-stubs==2026.10.0 in the lock, ==2026.9.3 in the budget ...]`, `1 of 11 typing-ruler source checks FAILED`, exit 1. That is CI's `tests / fast (3.14)` failure at da3a5cfb8. Restored, it exits 0.

## Null control

- The census can see an error under this toolchain: append `_HPO_NULL_CONTROL: int = "not an int"` to `const.py` and run `tests/typing_ruler.py --mypy` with this branch's pins. It reads `FAIL errors did not grow [recorded 0, measured 1 (+1)]`, by_code `assignment: 1`. Restored, it reads errors 0.
- The hash comparison can see a correct pin: on #3323's locks the same script reads 127 of 132 pins `OK` and 5 `STALE`. So the zero on this branch comes from correct hashes, not from a comparison that never fires.
- main's typing lock passes the same `pip download --require-hashes` run (exit 0, 111 packages).

## Figures

- Stale hashes, 5 of 132 pins in #3323's five files. For each `name==version` block, the `--hash` set was compared with the sha256 set from `https://pypi.org/pypi/<name>/<version>/json`'s `urls`. coverage 7.17.2: 119 listed, 0 of them PyPI's. acme 5.9.0: 2, 0. python-dateutil 4.0.0: 2, 0. sqlalchemy 2.1.8: 72, 0. uv 0.13.7: 19, 0. Every other pin's set is a subset of PyPI's. At this head the same comparison over all five files reads `STALE pins: 0` (132 pins `OK`).
- `pip download --require-hashes --no-deps --only-binary=:all:` for linux x86_64 (CI's runner platform; PyRIC, sdist-only and unchanged, dropped): the coverage lock on 3.13 and the typing lock on 3.14.7 each exit 0 at this head and exit 1 at #3323's.
- The typing body diff against main (`diff` of the bodies below each header) changes exactly 10 version lines: acme, anyio, boto3, botocore, grpcio, mypy-extensions, python-dateutil, sqlalchemy, threadpoolctl, uv. These are #3323's typing bumps minus homeassistant-stubs, zeroconf and cronsim. The compile was `uv pip compile <lock> --python-version 3.14.7 --python-platform x86_64-manylinux_2_28 --generate-hashes --no-header --no-annotate --override <the 13 overrides the header names>`. With #3323's zeroconf it is unsatisfiable (`homeassistant==2026.10.4 depends on zeroconf==0.151.5`), and the same holds with its cronsim (`depends on cronsim==2.7`).
- Typing census at this head: `tests/typing_ruler.py --mypy --emit <file>`, run by a CPython 3.14.7 venv holding this branch's 112 typing pins (macOS wheels, installed `--no-deps` without hashes, because the lock is Linux-only). Result: exit 0, errors 0, by_code `{}`, environment mypy 2.4.1, homeassistant-stubs 2026.9.3, threadpoolctl 3.8.0. CI's `typing` job, on the hashed Linux install, is the authoritative run.
- `python tests/typing_ruler.py` (source-only): exit 0, `ok the typing job's hashed lock installs the recorded pins`. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `python3 tests/layout.py`: exit 0.
- `python3 tools/audit/archscore/score.py --diff <merge base> HEAD`: `Architecture score: dS +0.0000 NULL`.
- Gate scope, `tests/closure.py select --diff <merge base>`: `MODE: FULL` (`tests/requirements-build.txt changes the gate itself`). The suite is CI's. The ci and build locks are byte-identical to #3323's, and at da3a5cfb8 `tests / fast (3.14)` failed only `typing_ruler.py` (`1 TEST SCRIPT(S) FAILED`). Its `env_drift.py` read `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56 committed fixture(s)`. Both claim files, `VERSION`, the manifest and `RELEASE_NOTES.md` are byte-identical to origin/main.

## Red checks

At this head: none. No check has run, because the pull request is not open. Under `defect-root-cause.md`'s second trigger, this branch answers these reds at #3323's head:
- `tests / coverage`, `tests / coverage-ratchet`, `tests / typing`: stale hashes on a version bump. This is the second instance (#3088 was the first). #3147 dismissed a per-pin PyPI comparison detector: the jobs' own `--require-hashes` install reports the same thing one step later, and only on Dependabot branches, which a seat re-applies either way. That cost test still holds at two instances. A third makes it `root-cause.md`'s (Forward-carry).
- `tests / fast (3.14)`: `typing_ruler.py`'s source-only lock check is already the cheap detector, and it fired as designed.
- `pr-contract / pr-contract` and `gate`: a Dependabot body carries none of the template's headings, and its reds were not answered. That is the reason for this replacement, not a defect.

## Forward-carry

- Dependabot re-proposes homeassistant-stubs 2026.10.0 (#3088, #3323), and zeroconf and cronsim past homeassistant's exact pins, every week. An `ignore:` for those names in `.github/dependabot.yml`'s pip entry would stop the proposals. It is not added here: it changes what Dependabot proposes, and the owner decides it. Carry: #201
- Stale hashes from Dependabot pip bumps, second instance. At a third, `root-cause.md` owes the cost test. Carry: #201

## Friction

none

## Unpinned sites

none: the diff adds no production or tool site.

## Architecture score

dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff <merge base> HEAD`).
