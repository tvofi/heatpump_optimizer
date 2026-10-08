# R9-CI-2: a one-shard pin run reads as `skip-no-measurement`

This is the root-cause seat's analysis of a defect in R9-CI-1's sharded pin chain, which merged
in #2049 (`0c25836e`, 2026-10-08T06:40Z). The seat followed `dev/governance/roles/root-cause.md`.
Measurements were taken at origin/main `dcc77dd0`, and the fix is on this branch.

**Trigger:** the defect turned PRs red (`mutation-autofix`, "THE REPAIR DID NOT HAPPEN") and
cost a hand-applied pin commit (#2025, `c5e00ae3`).

## 1. The defect, reproduced

On #2025 at `de81043a`, shard job 113265218115 printed `PIN KILLED: 4 pinned` and uploaded
`mutation-pins-1` (artifact 11547045879). That artifact holds `status` = `measured`, a
4-entry `pins.json`, and `head` = `de81043a`. Autofix job 113280999308 in the same run
(37763212023) then printed `shards merged: skip-no-measurement`.

The autofix log shows the cause. Exactly one artifact matched `pattern: mutation-pins*`, and
it was extracted to `.../_temp/mutation-pins-shards` itself. `actions/download-artifact` at
the pinned `37930b1c` uses `resolvedPath`, not `path.join(resolvedPath, artifact.name)`,
whenever `isSingleArtifactDownload || inputs.mergeMultiple || artifacts.length === 1`.
(source: `src/download-artifact.ts`, lines 172-182.)

`merge_pin_shards` iterated the subdirectories of `root`. It found only the files `status`,
`pins.json` and `head`, read no shard, and returned `skip-no-measurement`.

The seat replayed the real CI artifacts, flattened the way the action delivers a lone match:

| run | shard status | origin/main `merge_pin_shards` | this branch |
|---|---|---|---|
| 37763212023 (#2025 `de81043a`) | measured, 4 pins | skip-no-measurement | measured, 4 |
| 37769767377 (#2024 `c13216ce`) | measured, 1 pin | skip-no-measurement | measured, 1 |
| 37756428662 (#2024 `8fb1b717`) | skip-nothing-killed | skip-no-measurement | skip-nothing-killed |

## 2. Named cause

`merge_pin_shards` and its `tests/entities.py` fixture both assumed one subdirectory per
shard. `download-artifact` has a single-match exception, and nobody measured that layout.
The fixture built `mutation-pins-1..4` by hand, so it pinned the assumption rather than the
action's behaviour.

## 3. Process state: (c), followed and did not produce the intended result

R9-CI-1 was proof-run on CI over 8 runs on `proof/r9-ci-1-shards*`: 37692017071, 37699948800,
37700521637, 37709945524, 37710478042, 37711053129, 37720269074 and 37723947527. Every one of
those runs had 3, 4 or 10 shards, and none had 1. The proof process existed and was followed.
Its matrix left out the boundary `pin_shard_count` returns most often, which is 1 for up to 6
added sites. The unit test was also written, and its fixture was synthesized. This is not
state (b), because nothing that was owed was skipped. It is not state (d) either: the action's
single-match rule predates #2049.

## 4. How far the class reaches

There is one `download-artifact` with `pattern:` across `.github/workflows/*.yml`, and it is
this one. The other downloads are by `name:`, extract to `path` by design, and are read that
way. The legacy fallback in the autofix step (`SHARDS_DIR + "/mutation-pins-1"`, for a base
without `merge_pin_shards`) has the same blind spot. It cannot be reached any more, because a
pull request's base is the current main, and every main since `0c25836e` carries
`merge_pin_shards`. It is left unchanged.

## 5. Cost test

The seat took every `pull_request` run of tests.yml from #2049's merge to 12:01Z. 9 runs
reached `mutation-autofix` with pins measured:

- 3 had more than one shard: d30236a5 with 7, e4218c25 with 2, 883eed10 with 10. All 3
  autofix jobs succeeded.
- 6 had one shard. All 6 printed `skip-no-measurement`.
  - 3 carried measured pins: #2025 `de81043a` (4), #2025 `0864a8d2` (4) and #2024 `c13216ce`
    (1). At `0864a8d2` the autofix had already checked out `de81043a`, which closures-autofix
    pushed at 10:23Z, so that run would have been `skip-head-moved` even without the defect.
  - 3 were survivors only (#2024 at `e575850b`, `c1cae32d` and `8fb1b717`). They were
    mislabelled, and no pins were lost.

The defect cost 2 lost repairs (5 pins) in 5.3 h. Each cost one hand-pin round plus one CI
round on the new head. #2025's round ran from 11:09Z (the autofix) to 12:02Z (`c5e00ae3`), 52
minutes, before its CI.

P(recurrence) without a fix is about 1 per one-shard pin run, the modal case. The fix has a
standing cost of 0 s per run, plus a millisecond fixture inside `tests/entities.py`. The fix
is built.

## 6. Countermeasure

- **The cause.** `merge_pin_shards` reads a `root` that holds `status` as the one shard. The
  entities check now builds the real one-artifact layout, taken from the CI log above, and
  asserts `measured` with the shard's pins. It failed on origin/main
  (`one-artifact=skip-no-measurement,[]`, 1 of 2212) and passes on the fix. The mutant
  `[r] if False else ...` turns it red again (the PR's Mutation proof).
- **The process (c).** No new rule is proposed. The proof matrix gap was a single run, and the
  fixture is now the barrier at 0 s of standing cost. A policy line such as "proof matrices
  include n=1" would be state-(b) wording for a state-(c) miss. It fails the cost test against
  a fixture that already pins the boundary.
