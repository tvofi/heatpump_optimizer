_Requested by **tvofi**_

Closes #1740 (R9-EG-B4, the store version seam). Before this, no store could change its version. Snapshots and ledger passed a literal `1`, and `DHW_PROFILE_STORE_VERSION` served three stores (profile, draws, legionella). `QuarantiningStore` had no `_async_migrate_func`, so on a bump Home Assistant's load raised `NotImplementedError`, every loader swallowed it at DEBUG and reset, and `legionella.py` re-stamped its last cycle. R9-F10.1b had already made the stub honour `version`; this PR lands the production seam.

What changed:

- **One version constant per store.** `SNAPSHOT_STORE_VERSION` and `LEDGER_STORE_VERSION` are in `const.py`, `DHW_DRAWS_STORE_VERSION` is in `dhw_learning.py` and `LEGIONELLA_STORE_VERSION` is in `legionella.py`. All values stay at 1, so no stored document is affected.
- **The migration hook.** `QuarantiningStore._async_migrate_func` is Home Assistant's hook, and this default migrates nothing. On a major mismatch it surfaces the mismatch: a WARNING plus a `store_version` repair issue, raised through `setpoint_check.create_issue`, naming the store key. It then raises `NotImplementedError`, the base hook's own answer, so Home Assistant does not re-save the document unmigrated, and a minor-only mismatch is read as stored.
- **Downgrades.** A downgrade (`UnsupportedStorageVersionError`, a document newer than this release) is surfaced the same way and re-raised.
- **Repair-issue text.** The `store_version` issue text is added to `strings.json`, `translations/en.json` and `translations/sv.json`.
- **Ratchet classification.** `tests/structure.py` adds `_async_migrate_func` to `HA_CONVENTION_METHODS`, beside `_async_update_data`: Home Assistant's `Store` calls it, so nothing in the package does. No budget moves.

**Found while proving the mutants: every migration would have deadlocked.** Home Assistant's `_async_load_data` saves a migration's result from inside the load, in the same task. `QuarantiningStore.async_save` waits for the read in flight (D1-s2-52), and that read is the same load. The first mutant that made the hook return data hung for 22 minutes. So the reading task is recorded for the read's duration, and a save from that task does not wait; every other writer still does. Both sides are pinned (Mutation proof, M11 and M12).

**Design choice the checks encode:** the default does not migrate and does not hand back unmigrated data. A store that is bumped must override the hook. `tests/finite_boundary.py` Arm 5 refuses a store read at a version above 1 that does not override it. So a bump without a migration fails in the gate, and the runtime default is the fallback for an override that receives a version it does not know. The loaders' reset on a failed load is unchanged; what changes is that it is no longer silent.

Limit, stated for whoever bumps first: the override is a subclass, and Arm 1 enumerates the bare `QuarantiningStore(...)` call. A subclass construction drops that store out of Arm 1's set, and `every derived boundary is wired to a loader` (13 loaders against 12 boundaries) then fails, so the gap is loud, not silent. That seat extends Arm 1's enumeration to count subclasses.

## Head

`072ff1ee0bee23873e02ec8ca905ed524cb0e771`, on origin/main `03ba7f70f007147bda32ac0fc5dd83b11499bbaf` (fetched 2026-10-02T23:11Z; it is also the merge base).

## Mutation proof

Each mutant was applied to the production file in a detached copy at the head and driven through `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` (scratch runner; M2 and the two late mutants were applied in place after a commit, then restored). M0 is the unedited head and passes all checks.

- M1, the hook's surfacing call replaced by `pass`: 2 FAIL (`every store's version mismatch ... logs a WARNING and raises a repair issue`, `the default hook raises NotImplementedError and surfaces a major mismatch only`).
- M2, the hook predicate replaced by `if True:`: 1 FAIL (`the default hook ... major mismatch only, not a minor-only one`, verdicts `[not-implemented, 1, not-implemented, 1]`). This mutant **survived** the first version of the probe. A shared hass kept one issue per id, so a wrong second surfacing read as the first. The probe now takes a fresh hass per call (commit c78a4603).
- M3, the predicate inverted (`==`): 2 FAIL (the same two as M1).
- M4, `raise NotImplementedError` replaced by `return old_data`: 1 FAIL (`verdicts=['returned', 1, 'returned', 1]`). This is the mutant that hung before the deadlock fix.
- M5, the downgrade surfacing replaced by `pass`: 1 FAIL (the mismatch check, the `@-1` direction).
- M6, `create_issue` replaced by a no-op: 2 FAIL. M7, the WARNING lowered to DEBUG: 1 FAIL.
- M8, legionella constructed with `DHW_PROFILE_STORE_VERSION`: 1 FAIL (`no two stores share a version constant`).
- M9, the snapshot store's version back to the literal `1`: 1 FAIL (`every store's version is a named constant`).
- M10, the brief's scratch bump: `LEGIONELLA_STORE_VERSION = 2` with no migration. 1 FAIL (`a store whose version exceeds 1 overrides the default migration hook`). A bump without a migration fails in the gate.
- M11, the reader exemption removed (every save waits): 1 FAIL (`a store that migrates loads the migrated payload ...`, `got='TimeoutError'`).
- M12, no save waits: it survived both `tests/finite_boundary.py` and `tests/features.py`, because the D1-s2-52 writers wait before they build their payload, so `async_save`'s own wait had no killer even at base. The new check `a save from another task waits for the store's read in flight` kills it: `saves before the read landed=1`.
- RAISE_DEL on the downgrade re-raise: 1 FAIL (`a downgrade leaves the store as UnsupportedStorageVersionError`, `escaped=UnboundLocalError`). Without that check it would survive, because the loaders catch any exception alike.

Sites this diff adds, from `python3 tests/mutation_table.py --scope changed --base 03ba7f70f` (6, unpinned; pinning them is `mutation-autofix`'s job). Each one's killer, measured above:

- `store.py` RAISE_DEL `raise`: the downgrade check.
- GUARD_OFF `if old_major_version != self._major:`: M1.
- RAISE_DEL `raise NotImplementedError`: M4.
- GUARD_OFF `if asyncio.current_task() is not self._reader:`: M12.
- CONST `DHW_DRAWS_STORE_VERSION = 1` and `LEGIONELLA_STORE_VERSION = 1`: doubling either to 2 is M10's case.

No survivor is left on a touched site.

## Null control

The head's `tests/finite_boundary.py` against the merge base's `custom_components/` (tests at the head, production at `03ba7f70f`): 5 FAIL. They are the literal check, the shared-constant check, the mismatch check (`RESULT store_version_unsurfaced=26`: 13 stores times the older and newer directions), the hook-branch check (`AttributeError`, no hook) and the migrating-store check (`TimeoutError`). The control arm, each store read at its own version, surfaces nothing at the base or at the head. The two checks of behaviour the base already had pass at the base: the downgrade escapes as `UnsupportedStorageVersionError` (the stub raises it), and a save from another task waits for the read.

The finder's probe, `m4_store_version.py` from evidence commit a163db90 (sha1 `828afa1f11adc5742a83d760d8849095a8bb510f`), run as `PYTHONPATH=tests/hastub:custom_components python3 m4_store_version.py`:

- At both ends: `saved v1 loaded v2: raised NotImplementedError`, and `v1/v1: returned {'learned': 42}`. Its arms construct a raw `Store`, which this PR rightly leaves alone, so they read flat. F10.1b moved them before this PR.
- `_async_migrate_func overrides in the package`: 0 at the base, 1 at the head.
- The companion that applies the tree's own rule to the same inputs is Arm 5 above. It reads the defect at the base (26 unsurfaced) and not at the head (0).

## Figures

- Store constructions, and how each passes its version: `_version_names()` in `tests/finite_boundary.py`, Arm 1's AST rule (a `Call` whose callee is the bare name `QuarantiningStore`; the version is the second positional argument or `version=`). At the head: 13 constructions, 13 distinct names, 0 literals. At the base: 2 literals, and one name used 3 times.
- Seams of the class (step 8): a stored version that differs from the store's resolves without surfacing. Enumerator: Arm 5's loop over `LOADERS`, which the existing equality check holds to Arm 1's 13 boundaries, each read one version below and one above its own. That gives 26 seams. All 26 are closed in this diff (`RESULT store_version_unsurfaced=0` at the head, 26 at the base); `RESULT raw_store_calls=0`, so no store escapes the set. Two neighbours outside the class, by disposition:
  - `defrost.STORE_VERSION`, a version field inside the thermal-learning payload: already guarded by the `defrost/version` domain in `store.DOMAINS`.
  - `CONFIG_ENTRY_VERSION`: the config entry's own migration in `__init__.py`, which is not a `Store`.
- Lines under `custom_components/`: 67 added and 11 deleted across the `.py` files, plus 12 added in the three string files (`git diff --numstat 03ba7f70f HEAD -- custom_components`).
- Gate scope: `python3 tests/closure.py select --diff 03ba7f70f` prints `MODE: SCOPED -- 25 script(s) run, 3 scoped out` (measured at 4197a323; later commits touch only `store.py` and `tests/finite_boundary.py`, which are already in the set).
- Run locally with Python 3.14 plus numpy and scipy (`~/hpo-seats/R9-F11.4-venv`), `PYTHONPATH=tests/hastub`:
  - At this head: `tests/finite_boundary.py` (ALL 77), `tests/structure.py` (PASSED, no budget moved), `tests/entities.py` (ALL 2081), `tests/harness_headers.py` (ALL 94), `tests/deployment_shape.py` (ALL PASSED), `node .claude/workflows/brief_lint.mjs` (rc 0), `python3 tests/mutation_table.py --normalize` (0 retired keys; no ledger file moved).
  - At 4197a323 or 1ef99a13 (the scope above): `config_flow_steps`, `doc_claims`, `edge`, `env_drift`, `frontend`, `guard_pins`, `manual_plan`, `open_meteo`, `plan_view`, `validate`, `wood_advisor`, `solar_alignment`, `card.mjs` and `card_drift.mjs`, all rc 0.
  - `tests/features.py`: 3651 of 3652. The one FAIL is `R9-F2.1 P3`, which fails on this Mac at main too (BLAS).
- Not run locally, left to CI: `backtest.py`, `golden.py`, `optimality.py`, `stress.py`, `typing_ruler.py`, and features.py's P3 judged on CI.

## Red checks

none: no pull request has run on this head yet.

## Forward-carry

none. The constraints this PR finds bind the seat that first bumps a store's version, and no roster group, carry file or live stage is that seat. They are stated where that seat will look, which is the failing checks themselves:

- Arm 5's `a store whose version exceeds 1 overrides the default migration hook`.
- Arm 1's boundary-and-loader equality, for a subclass construction.
- The hook's docstring in `store.py`.

The deadlock is fixed here, not carried.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
