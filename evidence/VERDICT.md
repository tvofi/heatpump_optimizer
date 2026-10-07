Fix review: merge 3d1f948910fdb4a054d25a78e2a7e9fd8ea90472

bus-nonce: 8aecbc21890b99cd0081645147205ef6

Round 5. Earlier hpo-approver verdicts on this PR: blocked `3560b696`, merge `edc8fa5d`, merge `78852922`, blocked `2a503e10`. I measured head `3d1f948910fdb4a054d25a78e2a7e9fd8ea90472` from a detached worktree using the 3.14 venv. The head is a merge of `2a503e10` and the code head `3018304403694c070c52ae9c3683dabbfd7cb702`. `git diff HEAD 30183044` is empty. origin/main is `be0cb82134bd3a008e59127da6f2b67fb1c77e98`, which is the merge base.

The 2a503e10 block is answered. The body has been re-cut to the template headings. It no longer narrates `78852922`, `3560b696` or `6132233c`, and it has no figures stamped at `aa1a6615` or `62f604eb`. The mutation proof now names the `tests/block_duty.py` line exactly as written.

RESULT The PR's own production delta is identical at both heads. The `+`/`-` lines of `bcea7488...2a503e10` and `be0cb821...HEAD` over `custom_components/` and `tests/block_duty.py` match. So the only new content to judge is the merge resolution with #2008.
RESULT Resolution: `_arbitrate` passes `_without_block(coord, _share(...), now)` into `desired`, then runs `_write_night_schedule(coord, inp, now)` with no condition. A block does not cause an early return, so the night registers are written while a block holds. My own probe (`probe_resolution.py`, disclosed as mine and not the finder's) stubs the arbiter internals and drives `_arbitrate` in DUTY_CONTROL. It gave 4 of 4: no block commands `both` then writes night; space block commands `dhw` then night; DHW block commands `space` then night; both blocked commands `idle` then night. No test pins "night schedule is written under a block". None of the `_sw4_*` checks in `tests/features.py` sets a block. This is a design statement in the body without a pin. I am not blocking on it.
RESULT Mutant on the resolved line: replacing `desired(coord, inp, _without_block(coord, _share(coord, inp, duty, now), now), now)` with `desired(coord, inp, _share(coord, inp, duty, now), now)`:
  - `tests/block_duty.py` exits 0, as the body says.
  - `tests/features.py` exits 1 with 2 of 3814 failing: `FAIL a space block keeps the lease expiry on hot water, not the baseline's both duties` (writes `Heating + DHW`), plus the known P3 failure.
  - The unmutated head exits 1 with 1 of 3814 failing, P3 only: `shipped 110.4366, seeded with the half-price plan 110.1297`. That is local BLAS drift. CI `fast (3.14)` on this head is success.
  - So the mutant adds exactly the lease-expiry check. Restored.
RESULT `PYTHONPATH=tests/hastub python3 tests/block_duty.py` prints `ALL 46 BLOCK DUTY CHECKS PASSED`, rc 0.
RESULT Power mutant (`action["power"] = 0.0` -> `action["power"] = action["power"]`) exits 1 with 2 of 46 failing, the two named checks. Window mutant (delete ` and _window_open(snap, now)`) exits 1 with 1 of 46 failing, the named check. Both restored.
RESULT `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `tests/entities.py`: `ALL 2198 ENTITY CHECKS PASSED`. `tools/audit/round4/D6/claims.py` rc 0 and leaves no diff in the tree. `tests/closure.py select`: `MODE: FULL`. The diff touches `tests/derive_closures.sh` (adds `rec tests/block_duty.py`).
RESULT The closures command from the body prints `0 True True 82`.
RESULT `tests/deployment_shape.py` docstring figures re-derived from `tests/closures.json` at head: 32 scripts, 106 of 496 pairs at Jaccard >= 0.80, 378 comparable pairs, 89 production files. All match.
RESULT `git merge-tree --write-tree origin/main HEAD` exits 0 with empty stderr; tree `6a863a9447429df4f891888adfaa2564e36af5a0`. The claimnotes driver is installed.
RESULT Claims: `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt` are byte-identical to origin/main (`git diff --quiet` rc 0). Nothing under `tests/golden/` is in the three-dot diff. `env_drift.py --claims-only be0cb821...` prints `claims hygiene: ... ok`. Head `env-matrix` is success. The solver capture was not re-run.
RESULT `VERSION` (6.7.16), the manifest version and the `RELEASE_NOTES.md` heading are not in the diff.
RESULT Finder's harness, both ends: #1926 has no committed harness. Its stated null control is "no block -> no new key, goldens byte-identical, claim files untouched". At this head:
  - claims are untouched and `env-matrix` is green;
  - `block_duty.py` prints `ok no block leaves the action unchanged`;
  - `features.py` passes `with no block set the overlay adds no key and changes no value`.
  At the baseline the feature is absent, so the null control holds there trivially. The release-floor cases were probed on production functions at 2a503e10 (32 of 32, previous verdict). The `boost.py` delta is identical at this head, so those cases carry.
RESULT Red history over `be0cb821..HEAD` (18 commits, 0 API errors), failure conclusions excluding `pr-contract`: `closures`, `closures-autofix`, `delivery-status`, `fast (3.14)`, `mutation`, `mutation-autofix`, `nightly-status`. This matches `## Red checks`, and each has an answer. At head the only reds are `delivery-status` and `nightly-status`, which grade main, plus a cancelled duplicate `budget-raise-gate` beside a success. `closures`, `mutation` (`MUTATION TABLE PASSED`), `coverage` and `fast (3.14)` are success on this head.
RESULT The delivery row is at `dev/programme/delivery/1997.md`. `## Forward-carry` is `none`.

Body note (no figure depends on it): `## Null control` calls `dc2e16f3416cafb371ad21187674c88f5026ccb2` "this head's first parent". It is the first parent of the code head `30183044`. The first parent of `3d1f9489` is `2a503e10`. The orchestrator can correct this without moving the head.

Live head re-read before posting: `3d1f948910fdb4a054d25a78e2a7e9fd8ea90472`.
