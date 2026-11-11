Builds outside pull request #3436 (Bankaifan, authorship kept on `54f7b20d6c`) under round 10's R10-OUTSIDE-DIAG-REDACT-LOCATION. At main, Download diagnostics rounded `latitude`/`longitude` to one decimal and published the `solar_location` option's coordinate as that rounded cell. The outside commit redacts both outright with Home Assistant's `async_redact_data`, removes `_coarsen`/`_coordinate`/`COORDINATE_PLACES`, and holds `debug.replay` out of both redaction passes. That hold-out published the replay half's `entry.data.solar_location` at `replay_doc`'s two decimals (`{"latitude": 59.33, "longitude": 18.06}`, measured below), where main had coarsened it to one: more location than main, not less. `0437a8168e` replaces the hold-out. `debugger._public`, which already cuts what the replay half reads from the entry, now also drops every `const.LOCATION_KEYS` key at any depth, and `diagnostics.TO_REDACT` is built from the same constant. So the whole download goes through both passes with no section held out, and the replay half carries no location key to trip its own shape check.

Alternatives, and why each lost (`fixer.md` step 17):
- Keep the author's hold-out: it leaks the two-decimal coordinate (`M1-replay-keeps-location` below reproduces exactly that tree), and it is a second, section-specific redaction rule.
- Null the coordinate inside the replay (`latitude: None`): `async_redact_data` still turns the `solar_location` key into `**REDACTED**`, which `replay_doc`'s `text_ok` refuses (`Download diagnostics fills the bundle's replay half ...` goes red). So it needs the hold-out anyway.
- Drop the location in `diagnostics.py` after the bundle is built: a second walk of a sealed document, where the owner of what the replay reads is `debugger.replay_entities`/`_public`.

Cost: a replay half taken from a download carries no solar location, so a replay of it has no Open-Meteo coordinate. `async_bundle`'s only caller is `diagnostics.py`, so this path is the only one that changes. `tools/replay/export.py` (the on-instance export) is untouched and keeps two decimals.

## Head

`0437a8168e997e9ebc5b55897a0a96f7538969cc`, measured on merge base `86953c6d99ecf7aa86c7bc9d57fec9a991daad07` (origin/main at the start, 2026-11-11T06:58Z). origin/main has since moved to `a7628041dc`; `git merge-tree --write-tree origin/main HEAD` reports no conflict, so the base was kept.

## Mutation proof

Spec `mutants.json`, four entries, each `{name, file, old, new}`, run by `python3 tools/audit/seat/mutant_run.py --spec mutants.json --cmd 'bash named.sh <script>'`. debug_collect and features ran in mutant_run's git-archive copy. entities ran `--in-place --root` on a detached worktree at the head, because entities.py needs a git checkout and aborts in an archive. `named.sh <script>` runs `PYTHONPATH=tests/hastub python3 tests/<script>.py` and exits 1 iff one of this group's named checks prints `FAIL` (`the location is redacted`, `a coordinate (nested|that is not)`, `the download's replay half`, `Download diagnostics fills`, `DBG-1 Download diagnostics`, `the value pass searches`), or if no summary line prints. A mutant is therefore killed by a named check, never by an unrelated check that a git-archive or in-place tree fails anyway. That precondition is pinned by `SURVIVED NULL` on each script.

- `M1-replay-keeps-location`: debugger.py `for key, value in node.items() if key not in LOCATION_KEYS}` -> `for key, value in node.items()}`
- `M2-no-location-redaction`: diagnostics.py `TO_REDACT = {CONF_TIBBER_TOKEN, CONF_NAME, *LOCATION_KEYS}` -> `TO_REDACT = {CONF_TIBBER_TOKEN, CONF_NAME}`
- `M3-solar-location-not-a-key`: const.py `frozenset({CONF_SOLAR_LOCATION, "latitude", "longitude"})` -> `frozenset({"latitude", "longitude"})`
- `M4-coordinates-not-keys`: const.py `frozenset({CONF_SOLAR_LOCATION, "latitude", "longitude"})` -> `frozenset({CONF_SOLAR_LOCATION})`

At `0437a8168e`:

```
debug_collect: SURVIVED NULL / KILLED M1-replay-keeps-location / KILLED M2-no-location-redaction / SURVIVED M3-solar-location-not-a-key / KILLED M4-coordinates-not-keys
features:      SURVIVED NULL / SURVIVED M1-replay-keeps-location / KILLED M2-no-location-redaction / SURVIVED M3-solar-location-not-a-key / KILLED M4-coordinates-not-keys
entities:      SURVIVED NULL / SURVIVED M1-replay-keeps-location / KILLED M2-no-location-redaction / KILLED M3-solar-location-not-a-key / KILLED M4-coordinates-not-keys
```

Each mutant is killed by at least one script. M3 survives debug_collect and features because the coordinates inside `solar_location` are still redacted by their own keys there, and only entities' `the location is redacted whole, from data and from options, not coarsened` reads the key's value whole.

Failing test first, with the production side of the arms swapped under the head's tests (const.py at the head in every arm, since it only adds the constant):
- main's `diagnostics.py`+`debugger.py`: entities FAILs `the location is redacted whole ...` `[{'latitude': 59.4, 'longitude': 18.2}]`, `a coordinate nested below the top level, inside a list, is redacted` `[{'latitude': 59.3, 'longitude': 18.1}]`, and `a coordinate that is not a number is redacted too ...`. debug_collect FAILs `the download's replay half carries no part of the home location ...` `[['latitude', 'longitude', 'solar_location'] ... "solar_location": {"latitude": 59.3, "longitude": 18.1}]` and `the value pass searches for a removed value ...`. features FAILs `DBG-1 Download diagnostics carries the bundle through its own redaction ...`.
- the outside commit's `diagnostics.py`+`debugger.py`: those entities and features checks pass, and debug_collect FAILs `the download's replay half carries no part of the home location ...` with `"solar_location": {"latitude": 59.33, "longitude": 18.06}`. That is the hold-out's leak.
- the head: all of those pass.

## Null control

- Mutation: the NULL mutant (no edit) SURVIVED on all three scripts above.
- Every other redacted key is unchanged: `ALL 163 DEBUG COLLECT CHECKS PASSED` at the head, including R10-DIAG-REDACT's token, entry-name and value-pass checks. `the Tibber token never leaves the instance` and `the installation name the user typed never leaves the instance` are among `ALL 2704 ENTITY CHECKS PASSED`.
- The arm runs' one entities failure outside this group, `and main() passes the committed table at its own recorded count (the null control)`, appears in both the main and the author arm. It comes from the arms' modified tracked files and is not a location check. The head, in a clean worktree, passes it (2704 of 2704).
- The replay check's text probe (`59.3`, `18.06`, `18.1` absent from the replay half) passes at the head and fails at main (`59.3`) and at the author arm (`59.33`, `18.06`), so the probe can read each leaked precision.

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED`. Every script its `scope.run` names passed at the head with `PYTHONPATH=tests/hastub`: arch_score_head, debug_collect, deployment_shape, doc_claims, entities, env_drift, features, finite_boundary, golden, harness_headers, structure, typing_ruler. layout and `closure.py selftest` passed too, and `env_drift.py --claims-only <merge base>` exited 0.
- Structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. Its `RESULT` lines at the merge base and the head are identical (`diff struct.base struct.head` exit 0), so no metric moved and no budget changed.
- Architecture score: `python3 tools/audit/archscore/score.py --diff <merge base>` printed `Architecture score: dS +0.0000 NULL`.
- Mutation-ledger entries the outside commit deletes, five, all anchored in diagnostics.py: `@module.CONST.13fdaae9` (`COORDINATE_PLACES = 1`), `_coarsen.GUARD_OFF.c8d051b9`, `_coarsen.GUARD_OFF.de958194`, `_coarsen.RETURN_DEL.d4c9e2a6`, and `_private_values.BOOLOP.0dd41a81` (the `or (under in COORDINATE_KEYS and _coordinate(node) != node)` line). Each pinned code that no longer exists. `git grep -nE "COORDINATE_PLACES|_coarsen|COORDINATE_KEYS and _coordinate|def _coordinate" HEAD -- custom_components/heatpump_optimizer/diagnostics.py` matches nothing at the head, and the same pattern at origin/main matches 7 lines (the control). `_private_values` survives, but its `removed` line now holds no BoolOp, so the BOOLOP site is gone, and no pin was removed for any other reason.
- Location seams (`fixer.md` step 8): enumerator `git grep -nE 'LOCATION_KEYS|CONF_SOLAR_LOCATION|"latitude"|"longitude"|\.latitude|\.longitude' -- custom_components/`, each hit with its disposition:
  - config_flow.py `_default_location` and the `solar_location` field seed the entry's location. It reaches the download through `config_view` (redacted by key: entities' three location checks) and through the replay half (dropped by `_public`: debug_collect's replay check).
  - coordinator.py's options and `hass.config` coordinate reads feed the Open-Meteo client.
  - open_meteo.py's request parameters go to the network, not the download. Its `round(self.latitude, 5)` diagnostics dict sits under `latitude`/`longitude` keys, which are redacted at any depth (`DBG-1` checks it inside a payload snapshot).
  - replay_doc.py `COORDINATE_KEYS` is the replay's own rule, already guarded and no longer reached from the download.
  - const.py, debugger.py and diagnostics.py hold this diff's own constant and its readers.

  `debugger.capped` writes nothing and takes no location: it returns the bundle or its manifest.

## Red checks

none

## Forward-carry

none

## Friction

- r10-outside-diag-redact-location: cost: the outside commit carries `Co-Authored-By:` and `Claude-Session:` trailers, which this seat's brief forbids in any commit it produces. The first build (`defaf622d6`) was pushed to `handoff-wip/r10-outside-diag-redact-location` before the trailer check ran. History was rebuilt as `54f7b20d6c` (same author, trailers stripped, tree identical to `defaf622d6` by `git diff --quiet`). Deleting the stale wip ref was refused with HTTP 403, so that ref still holds the trailer commit until the orchestrator removes it. Carry: dismissed: one-off seat ordering slip, the wip ref is deleted at handoff by the orchestrator
