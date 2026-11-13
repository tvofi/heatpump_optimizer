Fix review: merge b724dc370defeff285ff74b5022ef7c2d1bfd3da

bus-nonce: 36acbb580a67043d0676c6d6ac0453ad

## Scope

Round 1 (first review, full scope). Measured head b724dc370defeff285ff74b5022ef7c2d1bfd3da, merge base 3150fe5e305ca4dfb0cbad54eb40bda6cf9a67bc. Checked against what the bumped packages actually require (wheel METADATA from PyPI), not only against the tree's pins.

## Evidence

- RESULT upstream-pins: the homeassistant-2026.11.0 wheel's METADATA pins `cronsim==2.7`, `httpx2==2.14.0`, `truststore==0.10.4` and `zeroconf==0.152.0` exactly, and does not list bleak. Two body claims are confirmed: homeassistant refuses #3483's httpx2, truststore and zeroconf bumps, and cronsim belongs to the same class.
- RESULT httpcore2: homeassistant does not pin httpcore2. The `httpx2==2.14.0` wheel does (`httpcore2==2.14.0`), so holding httpcore2 is right, but the pinning package is httpx2. The header comment groups it under "a package homeassistant 2026.11.0 pins exactly", which is imprecise wording only.
- RESULT bleak 3.1.0: its wheel requires `dbus-fast>=4.0.0` on linux, and the lock has dbus-fast 5.2.0. habluetooth 7.1.2 and bleak-retry-connector 4.7.1 both require `bleak>=3.0.2`. Nothing in the lock caps bleak below 3.1.0.
- RESULT hash parity: the bleak and regex blocks at the head are byte-identical to the ones in Dependabot #3483's commit 43f71cf41c (diff empty, ev/checks.txt context).
- RESULT install: a fresh venv ran `pip install --require-hashes --no-deps --build-constraint tests/requirements-build.txt -r tests/requirements-typing.txt` at the head and got install-rc=0 (ev/install-head.txt). That is the same install CI's typing job does. `pip check` then lists exactly the header's documented override set (homeassistant via the stubs, astral, sqlalchemy, uv, acme, python-dateutil) and nothing else. bleak 3.1.0 and regex 2026.11.9 add no new conflict (ev/pipcheck-head.txt).
- RESULT ruler at head: `python3 tests/typing_ruler.py` gives `ok mypy is pinned at 2.4.1` and `ok homeassistant-stubs is pinned at 2026.9.3`; ALL 9 and ALL 12 checks PASSED (ev/ruler-head.txt).
- RESULT mutation M1: replacing the lock with #3483's verbatim gives `FAIL the typing job's hashed lock installs the recorded pins [homeassistant-stubs==2026.10.0 in the lock, ==2026.9.3 in the budget...]` and `1 of 12 typing-ruler source checks FAILED` (ev/mut-M1.txt). This reproduces the body's mutation proof.
- RESULT entities: `env -u BASH_ENV python3 tests/entities.py` (venv-ci, PYTHONPATH=tests/hastub as tests/run.sh sets it) on mutant M2 gives ALL 2709 ENTITY CHECKS PASSED (ev/entities-M2.txt). At the head: ALL 2709 ENTITY CHECKS PASSED, rc=0 (ev/entities-head.txt).
- RESULT figures: `git diff -U0 b5057b05 HEAD -- tests/requirements-typing.txt | grep -E '^[-+][a-zA-Z0-9_.-]+=='` prints only the bleak and regex pins (ev/checks.txt). The body's figure is re-derived.
- RESULT dependabot.yml: the `ignore` entries for homeassistant-stubs and mypy sit under the single pip `/tests` entry, which is the directory #3483 bumped. The only `name==` pins of either package under tests/ are the typing lock's (`mypy==2.4.1`, `homeassistant-stubs==2026.9.3`), so the ignore removes no other manifest's updates.
- RESULT untouched: VERSION, manifest.json, RELEASE_NOTES.md and both claim files have an empty three-dot diff. No golden fixture or claim is involved, so `env_drift.py --all` is not applicable.
- RESULT merge: `git merge-tree --write-tree origin/main b724dc37` exits 0, both against 9fa98b0076 (tree 2454f0047a) and against main after it moved to 0723540391 (tree f888c5862a).
- RESULT head re-read before return: `git ls-remote` shows refs/pull/3543/head and the branch both at b724dc370defeff285ff74b5022ef7c2d1bfd3da (ev/head-recheck.txt).
- RESULT CI: `merge_train.py classify b724dc370defeff285ff74b5022ef7c2d1bfd3da --pr 3543` printed `GREEN b724dc370defeff285ff74b5022ef7c2d1bfd3da pending: none red: none` (rc 0, ev/classify-1.txt). The packet's `tests / nightly-status` failure grades main and is outside owed-reds. The body's `## Red checks: none` agrees.
- RESULT head: the body names b724dc370defeff285ff74b5022ef7c2d1bfd3da, which is the head measured here. The delivery-row commit and main-merge commit on top of b86aed6c34 change no code.
- RESULT harness: no finder's harness is named. The finding is a red Dependabot pull request, and its committed detector is `tests/typing_ruler.py`, which was run at both ends above (M1 is red, the head is green).

## Findings

- The new ignore stops homeassistant-stubs and mypy, but nothing enforces the header's hold on the five exact-pin packages (cronsim, zeroconf, httpx2, httpcore2, truststore). Measured with mutant M2: #3483's lock with only the homeassistant-stubs block restored, so the cronsim 2.8, zeroconf 0.154.0, httpx2/httpcore2 2.16.0 and truststore 0.10.5 bumps are taken. On M2, `tests/typing_ruler.py` passes all 9 and all 12 checks (ev/mut-M2.txt) and `tests/entities.py` passes all 2709 (ev/entities-M2.txt). No workflow runs `pip check` on the lock, and the typing job installs it with `--no-deps`. Dependabot keeps proposing these five weekly until homeassistant moves its pins. Before this PR, such a pull request went red on the stubs pin and a compat seat re-applied it with the holds. After it, the same group pull request can go green and `dependabot-automerge.yml` lands the patch/minor bumps, putting the lock past homeassistant's exact pins as undocumented overrides. mypy executes none of these packages, so no measured number moves. The cost is the header's resolution contract, not the census. Countermeasure owed to the next seat touching Dependabot or the typing lock: either (a) `ignore` entries with `versions` above homeassistant's pin for each held name, or (b) a ruler check that `pip check` on the lock lists only the header's override set. Control for either: mutant M2 must turn red, and the head must stay green. Carry: #201

## Friction

none
