Fix review: merge eeaa91d5bf60211f38d9a9d9d217a2e976ff8cc7

bus-nonce: b20f36c3942b1030af0eaccce0c18ae4

Round 1 (first review). Measured head eeaa91d5bf60211f38d9a9d9d217a2e976ff8cc7 (merge base 5345766b41), which is still `refs/pull/3540/head` at verdict time. The body names this head and its code head 94e45e7931, which is an ancestor of it.

## Evidence

- RESULT live: `tests / nightly-ha (stable)` job 131755191793 ran the real HA container on the merge of this head into main 8a550692da and printed `ok a4:bridged [bridged: last_update_success=True, price_feed_stale raised, 46 entities available]`, `ok a4:failed [last_update_success=False]`, `ok a4:unavailable [54 unavailable]`, `ok a4:buttons [6 button(s) unavailable]`, `ok a4:no_stale [50 pre-break value(s) gone]`, `ok a4:recovered`, `ALL 66 checks PASSED` (ev/nightly-ha-stable-job131755191793.txt). `nightly-ha (2025.2.0)` job 131755191621 also concluded success, and the lane exits 1 on any FAIL (`nightly_ha.py` `return 1 if checks.failures()`). So the live proof the body says was "not run here" exists at this head: both phases of the #3454 contract (bridged, then failed) are asserted in real Home Assistant with no coordinator poke. The negative end is main's run 43358851739 that the body cites, which has the five FAIL lines; I did not re-fetch it.
- The repair pins the behaviour and does not silence the lane: `a4:failed`, `a4:unavailable`, `a4:buttons` and `a4:no_stale` are unchanged predicates, still asserted, and now reached through the counterparty. The new `a4:bridged` asserts #3454's bridging contract (update successful, `price_feed_stale` in the issue registry, no published entity unavailable). `_async_check_a4` sets neither `last_update_success` nor `_prices`, and entities.py pins `"_prices" not in _a4_walk_src`.
- Product premise re-derived from the head source: `_tibber_fetch_failed` passes `_known_prices_for([plan_step_start(now)])` as `covering` to `issues.note_price_outage`, which bridges only when that is truthy. `_covering_index` ends the last entry one predecessor span after its start. `_hourly_prices(now-3d)` has 72 hourly rows from `floor(now-3d)-2h`, so the last row starts at `floor(now)-3h` and ends at `floor(now)-2h`, before now. That matches the body's "ends 2 h before now". The ended-curve fetch succeeds, so `_tibber_fetch_recovered` resets the outage counter, and the next 500 is cycle 1 with a falsy `covering`, so it raises.
- Mutation proof, re-run (finder's harness = the nightly lane itself; offline pins via `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` in one worktree per mutant; ev/mutants.txt holds each diff and its FAIL line). There are no production lines: the PR changes no `custom_components/` line, by design.
  - M1: dropped `bool(repair_raised)` from `check_a4_bridged`. Killed by `FAIL a4:bridged fails a failed update, a missing repair, ...`.
  - M2: dropped `not gone`. Killed by the same check.
  - M3: dropped `bool(published)`. Killed by the same check.
  - M4: removed `end_price_curve(True)` from the walk. Killed by `FAIL A4 exhausts the published prices at the counterparty, not the coordinator`.
  - M5: `_ENDED_CURVE_AGE = timedelta(hours=1)`. Killed by the same check.
  - M6: the server ignores the ended flag (`_tibber_body(now)`). Killed by the same check.
  - M7: removed `"a4:bridged"` from `A4_INSIDE`. Killed by `FAIL the nightly demands A4 fault-injection checks by name`.
  - Survivors: 0 of 7. M4–M6 are pinned offline by source shape only. Their behavioural kill is the live lane: without the ended curve, phase 2 is bridged and `a4:failed` reads True, which is the body's null control and main's red.
- RESULT entities.py at head: `ALL 2711 ENTITY CHECKS PASSED`, real 9m13s (ev/entities-head.txt; its 60 `FAIL` lines are negative controls printed by passing checks).
- Class: `break_price_source` / `_PRICE_SOURCE_BROKEN` is used only by `_async_check_a4` and `_serve_prices` at this head. This is a one-seam class, and no other nightly check presumes UpdateFailed on a Tibber 500.
- Claims and versions: the three-dot diff touches only `dev/programme/delivery/3540.md`, `tests/entities.py` and `tests/nightly_ha.py`. VERSION, the manifest, RELEASE_NOTES.md, `tests/golden/` and both claim files are untouched. No budget file or closure moves.
- Merge: `git merge-tree --write-tree origin/main eeaa91d5bf` exits 0 (ev/merge-tree.txt).
- CI: `merge_train.py classify eeaa91d5bf --pr 3540` reads `GREEN eeaa91d5bf60211f38d9a9d9d217a2e976ff8cc7 pending: none red: none`, rc 0 (ev/classify.txt).
  - `gate` job 131756457426 concluded failure only as an interim: its log says `FAIL run(s) [43386014142] at this head are still being judged; their gate decides`. The later `gate` 131766981808 is success. No required check went red on content, so no root-cause answer is owed.
  - `governance / instrument-self-tests` 131754828053 is success, so no introduced red.
  - `tests / nightly-status` failure is outside the `owed-reds` set (ev/owed-reds.txt): it grades main, and the body answers it anyway.
  - `pr-contract / pr-contract` 131765528934 is success.
- Review packet re-rendered at verdict time (ev/review-packet.md) refuses `handoff-not-applied: handoff/r10-hotfix-nightly-ha 1dee0df2a4 is not an ancestor of eeaa91d5bf`.
  - Measured: the handoff tip and this head both contain code head 94e45e7931. They differ only in which main merge sits on top (1dee0df2a4 merged main at b5057b0525; the PR branch merged main at 5345766b41 as 61c4191db1, then added the delivery row).
  - The `tests/` patch of each against its own merge base is line-identical (`SAME-TEST-PATCH`).
  - `review_carry.py 1dee0df2a4 eeaa91d5bf` prints FRESH-REVIEW, and this review is that fresh review of the PR head itself.
  - This is a stale dispatch ref, not a defect of the patch. Carry: dismissed: evidence, not a finding
- The body's figures, `ALL 2711 ENTITY CHECKS PASSED` and `prepr.sh` rc=0 at 94e45e7931: I re-derived the first at this head. I did not re-run `prepr.sh` (heavy gate, cited from CI per fix-review step 11). Carry: dismissed: evidence, not a finding
- Forward-carry: the body says none. No finding here changes a later stage.

## Findings

none
