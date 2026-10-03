Fix review: blocked e17006c704d38cb72f2ba3b1c0e42e4779f6aedd other: store.py imports UnsupportedStorageVersionError from homeassistant.helpers.storage, absent from HA 2025.2.0 (the declared floor) through 2026.2.x, so the integration fails to import on every supported release before 2026.3

bus-nonce: bd6c8423bf7654b41e15f36bf685b43a

Round 1. Measured at e17006c704d38cb72f2ba3b1c0e42e4779f6aedd, from a detached worktree, against merge base 03ba7f70f. The live head is now ef37a5ba1d9652769ac099227fa2379f3ebe8f71: `github-actions[bot]` "ci: pin killed mutants", adding 6 `killed_by` JSON files and nothing else. No production or test line moved, so every figure below also holds at ef37a5ba.

## Blocker: the import fails at the floor

`hacs.json` and the README declare Home Assistant 2025.2.0 as the floor, and `nightly-ha` runs the `2025.2.0` image. The PR adds `from homeassistant.helpers.storage import Store, UnsupportedStorageVersionError` to `store.py`.

- I checked upstream `homeassistant/helpers/storage.py` at each tag. `UnsupportedStorageVersionError` occurs 0 times at 2025.2.0, 2025.3.0, 2025.6.0, 2025.9.0 to 2025.12.0, 2026.1.0, 2026.2.0 and 2026.2.3. It occurs 2 times at 2026.3.0, 2026.6.0 and 2026.9.0, where it is re-exported from `homeassistant.exceptions`. It is also absent from `homeassistant/exceptions.py` at 2025.2.0.
- The stub's own inventory already says so. `tests/ha_contract.py` reads: "the class is in HA releases after the 2025.2.0 floor".
- Reviewer's probe: `tests/hastub` with the class renamed away, which is what 2025.2.0 looks like.
  - `RESULT floor_import(e17006c70)=ImportError: cannot import name 'UnsupportedStorageVersionError' from 'homeassistant.helpers.storage'`
  - `RESULT floor_import(03ba7f70f)=ok`, the null control at the base.
- Effect: `store.py` is imported by every module that persists anything, so the integration fails to set up on 2025.2.0 through 2026.2.x. No gate script sees this. The stub defines the class, and the local real installs are 2026.9.3. Only the nightly `2025.2.0` arm would see it, after the merge.
- Downgrade semantics at the floor also differ from the stub. 2025.2.0's `_async_load_data` (evidence: `ha_2025.2.0_storage_L270-425.py`) has no downgrade refusal and hands a newer document to `_async_migrate_func`. There the hook's `!=` branch surfaces it, which is correct, and the load escapes as `NotImplementedError`, not `UnsupportedStorageVersionError`.
  - Arm 5's check `a downgrade leaves the store as UnsupportedStorageVersionError` therefore pins 2026.3+ behaviour only.
  - My mutant V2, `old_major_version < self._major`, **survives all 77 checks**. At the floor it would leave every downgrade unsurfaced. That survivor exists because the stub models only the post-floor path.
- Repair: guard the import, for example `try/except ImportError` with a local placeholder class, or catch by `getattr(storage, "UnsupportedStorageVersionError", ())`. Then add a check that kills V2, for example by driving the hook directly with `old_major_version > self._major` and asserting it surfaces. Either the stub models the floor's downgrade path, or the PR body states the divergence.
- The cheaper detector the class lacks is a gate check that every `homeassistant` name production imports exists at the 2025.2.0 floor. Whether to build it is root-cause.md's question, not this review's.

## Item 1: the deadlock fix, raced (reviewer's probe `race_probe.py`)

The probe wraps the stub with upstream 2025.2.0's `async_load` dedupe (`_load_future`) and an executor-style yield.

- `RESULT other_task_save_first_event=load-done disk={"x": 99}` at the head. A save from another task waits for the migrating read and lands after it. At the base the same scenario deadlocks: `TimeoutError`.
- `RESULT spawned_save_order=['load', 'save']`. A task spawned by the reader is a different task, so it waits.
- **A residual seam:** `RESULT two_concurrent_loaders=TimeoutError (deadlock)` at the head.
  - Cause: a second `async_load` in another task overwrites `_reader` and `_reading`. Upstream then parks it on the first call's `_load_future`, and the first call's migration write-back waits on the second call's `_reading`, which never resolves.
  - It is latent today: no store migrates, so no write-back happens. It becomes live at the first bump if any store can be loaded twice concurrently. Holding readers in a set, or not re-arming while a read is in flight, closes it.
  - My mutant V4, never clearing `_reader`, also survives all 77 checks. Nothing pins the clear.
  - Repair, or disposition in the body.

## Item 2: the repair issue fires once, in both languages (`once_probe.py`)

I counted raw `create_issue` calls per load, not registry entries, because the registry dedupes by id.

```
RESULT issue_calls[same] create_issue_calls=0
RESULT issue_calls[older(bump)] escaped=NotImplementedError create_issue_calls=1
RESULT issue_calls[newer(downgrade,2026.3+)] escaped=UnsupportedStorageVersionError create_issue_calls=1
RESULT issue_calls[newer(downgrade,floor)] escaped=NotImplementedError create_issue_calls=1
```

`issues.store_version` exists in `strings.json`, `en.json` and `sv.json` with the same placeholders, `{store}` and `{detail}`. One non-blocking note: `{detail}` is English prose, so the Swedish notice carries an English clause. The same pattern already exists in `pump_write_ignored`.

## Item 3: downgrade

Correct on 2026.3+: surfaced once, then re-raised (RAISE_DEL is killed). On the floor, downgrades are only handled through the hook, as described in the blocker.

## Item 4: `HA_CONVENTION_METHODS`

The classification is legitimate. Upstream calls `self._async_migrate_func` from `_async_load_data` (2025.2.0, lines 408-413), the same convention as `_async_update_data`.

```
RESULT dead_methods=0 with the entry
RESULT dead_methods=1 without it (FAIL dead_methods 1 > 0)
```

The one member it keeps alive is the hook itself. `_surface_version` is also reached from `async_load`. No budget moved.

## Item 5: mutants (`tests/finite_boundary.py`, venv 3.14, detached worktree at the head)

Of the fixer's mutants, I re-ran 5 plus a null:

| mutant | result |
|---|---|
| R0 null | `ALL 77 PASSED` |
| M2 | killed, 1 FAIL |
| M4 | killed, 1 FAIL |
| M11 | killed (`TimeoutError`) |
| M12 | killed |
| RAISE_DEL | killed (`UnboundLocalError`) |

My own, around the version-compare branches and the reader:

| mutant | result |
|---|---|
| V1 `>` | killed, 2 FAIL |
| **V2 `<`** | **SURVIVED, ALL 77 PASSED** |
| V3 `_major = 1` | killed |
| **V4 `_reader` never cleared** | **SURVIVED** |
| V5 `_reader` never recorded | killed (`TimeoutError`) |

CI's `mutation` lane refused 6 unpinned sites, then pinned all 6 as killed by `tests/finite_boundary.py` (`PIN KILLED: 6 pinned, 0 left unpinned`). That is the bot commit ef37a5ba.

## Item 6: the fixer's two decisions

- **(a) Loaders still reset to defaults, which is surfaced, not prevented.** Not a blocker. The brief's item (2) asks for surfacing, and the reset is base behaviour.
  - It is a forward-carry, not a non-finding. On a downgrade the reset loader's next save overwrites the newer document within one cycle, and legionella re-stamps `last_cycle`. The repair text's "reinstall the newer one before the data is overwritten" promises a window that is minutes long.
  - It belongs to whichever stage owns store-load failure handling. The body's "Forward-carry: none" should name that destination or state the decision.
- **(b) A bump needs a subclass, and Arm 1 counts bare constructions.** Not a blocker, and the body's "loud, not silent" holds. My V6, legionella built through `type("_LegionellaStore", (QuarantiningStore,), {})(...)`, gives `FAIL every derived boundary is wired to a loader in the reach sweep [boundaries=12 loaders=13]`. The failing check is the carrier.

## Other contract steps

- Finder's harness `m4_store_version.py` (sha1 828afa1f) at both ends:
  - overrides 0 at the base, 1 at the head;
  - the bump arm reads `NotImplementedError` at both ends (raw `Store`, flat by design), matching the body.
- `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched (three-dot).
- `git merge-tree --write-tree origin/main HEAD` returns rc 0.
- CI at e17006c7 (`waitci.sh`: total=35):
  - `mutation`: failure. This PR's; answered by the autofix pin commit, but the body must name it.
  - `pr-contract`: failure, `REFUSE 'Closes #1740' closes #1740; not in the intended list`. This PR's, and unanswered.
  - `nightly-status`: failure. main's, and exempt: the diff reaches none of its inputs.
  - The body's `## Red checks: none` is stale against two of this PR's own reds (step 11).
- Not run by me: `features.py`, the goldens, `optimality`, `stress`. CI's heavy runs are cited, not re-run.
