deps(tests): the pip group's bumps from Dependabot #3414, re-applied with hashes that install, homeassistant-stubs, zeroconf and cronsim held

Supersedes pull request 3414. The orchestrator closes it as superseded after the merge; this body carries no closing keyword for it.

Dependabot's branch cannot be edited, so this branch re-applies #3414's version changes (head 4182e75d7, base 32aea942e) to `tests/requirements-typing.txt`, the only file #3414 touches. It is cut from 32aea942e, an ancestor of origin/main d08ed3104. This is the third instance of the class (#3088, #3323 / pull request 3408, now #3414). The reds at #3414's head come from two causes:

1. **A stale hash on the homeassistant pin.** Dependabot moved homeassistant 2026.10.4 to 2026.11.0 and kept the previous version's `--hash` lines. pip's hash-checking mode refuses the install, which turned `tests / typing` red.
2. **homeassistant-stubs 2026.10.0.** `tests/typing_ruler.py`'s source-only lock check refuses a lock whose stubs pin disagrees with `tests/typing_budgets.json`'s `ruler`. The stubs stay at 2026.9.3 (2026.10.0 is the empty deprecation release and changes what the census measures); no budget moves.

Of #3414's seven bumps, boto3 and botocore 1.43.126 and regex 2026.11.7 land as written, and homeassistant 2026.11.0 lands with its own hashes. homeassistant-stubs is held at 2026.9.3. zeroconf and cronsim cannot be compiled under the lock's rule: homeassistant 2026.11.0 pins `zeroconf==0.152.0` and `cronsim==2.7` exactly, so #3414's 0.154.0 and 2.8 stay at homeassistant's pin and the override set does not grow. It shrinks: homeassistant 2026.11.0 stopped pinning cryptography, pillow, hass-nabucasa, orjson, python-slugify, securetar and pyopenssl lower, so the compile resolves without those seven overrides and the header names the six that remain. The lock gains httpcore2, httpx2, pyserial and truststore, which homeassistant 2026.11.0 requires, and loses nothing else. The body is the header's compile from `typing_ruler.py --print-requirements` with the override set above; the pins it resolved are the committed ones (see `## Figures`).

The header's text the bump made false is corrected (override list, the held pins, the generic PyJWT, aiohttp and yarl sentence). `.github/dependabot.yml` is untouched: triage ruled P543 (a Dependabot `ignore:` for homeassistant-stubs, zeroconf and cronsim) REJECT in batch 141, because the ignore would not have made #3088, #3323 or #3414 green (stale hashes in all three), and an ignore of zeroconf would also block the 0.152.0 move homeassistant itself needs.

## Head

f402c1e8a944afd6c702530bd29beceb967ce995

origin/main at d08ed31049cd3636cde4d2fdeb3bd7cd4b3c842a (`date -u` 2026-11-11T01:18:32Z). `git merge-tree --write-tree origin/main HEAD` reports no conflict. The branch carries one commit over its base, authored by the cloud fixer; this seat re-verified it and added no code.

## Mutation proof

- The stale-hash repair: put #3414's `tests/requirements-typing.txt` (4182e75d7) in this tree. Its homeassistant 2026.11.0 block carries 2026.10.4's hash lines, none of them PyPI's for 2026.11.0, so `pip install --require-hashes --no-deps` stops with `THESE PACKAGES DO NOT MATCH THE HASHES` (CI's `tests / typing` log at 4182e75d7 shows the same refusal). This branch's block passes the per-pin PyPI comparison below.
- The comparison itself can see a corrupted pin: change one hex digit in the first homeassistant hash of this branch's body. The comparison then reads `blocks 116 bad 1` with `MISMATCH` on `homeassistant 2026.11.0`. Restored, `bad 0`.

## Null control

- The bot head is the unmodified tree for the hash claim: the same per-pin PyPI comparison on #3414's body reads `blocks 112 bad 1`, the one bad block being `homeassistant 2026.11.0`. So the zero on this branch comes from correct hashes, not from a comparison that never fires.
- main's typing body (base of this branch) reads `blocks 112 bad 0`, so the comparison does not flag good locks.
- The census null control is the ruler's own: its source-only half runs `guard 5` arms (a failing pinned run reddens a check, a passing one does not) and `the lock check refuses a lock that disagrees with the budget`; no production code changes, so no further census control is claimed.

## Figures

- Per-pin hash check, 116 `name==version` blocks in this branch's body: for each block the `--hash` sha256 set was compared with the sha256 set of `https://pypi.org/pypi/<name>/<version>/json`'s `urls`; every block's set is a subset of PyPI's. Result `blocks 116 bad 0`. On #3414's body (112 blocks) `bad 1`, on main's body (112 blocks) `bad 0`. The script is an ad-hoc 20-line `urllib` loop kept in this seat's scratch, not committed (triage P544 rejected a PyPI hash checker as a `tools/` instrument; CI's `--require-hashes` install is the standing detector).
- Reproduction of the body, pin route: take this branch's body, keep only each block's `name==version` line (116 lines), and run `uv pip compile <those lines> --python-version 3.14.7 --python-platform x86_64-manylinux_2_28 --generate-hashes --no-header --no-annotate --override <the six overrides: homeassistant==2026.11.0, uv==0.13.7, astral==3.2, sqlalchemy==2.1.8, acme==5.9.0, python-dateutil==4.0.0>` (uv 0.12.11 on this host). `diff` of the output against the committed body is empty (byte-identical).
- Reproduction of the body, fresh route (`python3 tests/typing_ruler.py --print-requirements` as input, same options): NOT byte-identical today, and it cannot be, because the route re-resolves unpinned names against live PyPI. Differences are exactly: bleak 3.0.2 to 3.1.0, boto3 and botocore 1.43.126 to 1.44.0, josepy 2.2.0 to 2.3.0, regex 2026.11.7 to 2026.11.9 (all released after the fixer's compile, so they are newer than #3414's proposals), and greenlet, httpcore, httpx, pytz and six present in the committed body and absent from the fresh one. The header documents this (`--print-requirements` moves unrelated packages), which is why the pin route is the reproduction claim. The five absent packages are dependencies of the newer josepy / boto3 / bleak resolutions and are not required by anything pinned at this lock; I did not verify that mechanism package by package, so it is stated as the observed difference only.
- Diff of the body against main's body (`diff` below each header): version changes are #3414's boto3, botocore, homeassistant, regex plus the zeroconf move 0.151.5 to 0.152.0 homeassistant pins; added packages are httpcore2, httpx2, pyserial, truststore.
- Typing census at this head: `tests/typing_ruler.py --mypy --emit <file>`, run by a CPython 3.14.7 venv holding this branch's 116 pins (macOS wheels, `uv pip install --no-deps` of the pin lines without hashes, because the lock is Linux-only). Result: exit 0, `ALL 9 typing-ruler checks PASSED`, environment mypy 2.4.1, homeassistant-stubs 2026.9.3. `uv pip check` on that venv lists exactly the header's override set (acme, astral, sqlalchemy, uv, python-dateutil). This host's `venv-ha` holds the old pins (mypy 2.3.1, homeassistant 2026.9.3), so the ruler against it refuses (`mypy is pinned at 2.4.1 [found 2.3.1]`); I did not use it for the claim. CI's `typing` job, on the hashed Linux install, is the authoritative run.
- `python3 tests/typing_ruler.py` source-only half: `ok the typing job's hashed lock installs the recorded pins` (the one FAIL it prints on this host is the venv-ha one above); `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `python3 tests/layout.py`: exit 0.
- `python3 tools/audit/archscore/score.py --diff <merge base> HEAD`: `Architecture score: dS +0.0000 NULL`.
- Gate scope, `python3 tests/closure.py select --diff <merge base>`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` The two are `tests/entities.py` and `tests/typing_ruler.py`.
- VERSION, the manifest version, `RELEASE_NOTES.md` and both claim files are untouched: the diff names one file, `tests/requirements-typing.txt`.

## Red checks

None at this head: no check has run, because the pull request is not open. Under `defect-root-cause.md`'s second trigger, #3414's own reds:
- `tests / typing`: stale hashes on a version bump. Third instance (#3088, #3323, #3414). Triage P544 (batch 141) ruled a PyPI hash checker as a `tools/` instrument REJECT, because CI's `--require-hashes` install already reports it, and it counted 0 re-apply rounds saved across the three. Per #3408's Forward-carry the third instance makes the cost test `root-cause.md`'s; that is the root-cause seat's work and the orchestrator's to dispatch (P544 says so), not built here.
- `tests / fast (3.14)`: `typing_ruler.py`'s source-only lock check, the cheap detector, fired as designed on the stubs pin.
- `pr-contract` and `gate`: a Dependabot body carries none of the template's headings; that is the reason for this replacement.

## Forward-carry

none

## Friction

gate-scoping: cost: the cloud fixer's prepr.sh refused on two environment faults that also fail on a clean origin/main d08ed3104, quoted from its BLOCKED.md: stop-selfcheck.sh --self-test "fatal: bad config line 1 in file /dev/null" (28 passed, 1 failed) and tests/entities.py exit 1, CalledProcessError from tests/throwaway_git.py git init (exit 128); a cloud re-fire would hit the same faults, so a local seat completed the handoff, and on this host the hooks step passes (HOOKS ok: 4 wired hook(s) exist and pass their own --self-test) and the closures step is skipped as non-Linux. Carry: R10-SUITE-ENV-RESIDUE

## Unpinned sites

none: the diff adds no production or tool site.

## Architecture score

dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff <merge base> HEAD`).
