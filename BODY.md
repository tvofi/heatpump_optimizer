R11-SEAM-store: `store.DOMAINS` is the one schema. Writers and loaders agree with it, and a restored value is tested against it before it is applied. Five findings: D15-s1-04, D15-s1-05 (#3744, class P2), D1-s2-06 and D1-s2-01 (#3757, class P1), and D17-s3-03 (#3758). The class issues stay open, because they hold other groups' findings.

- **D15-s1-04.** `DOMAINS` now declares what the writers actually write. `predicted_cost` on an unpriced accuracy sample is nullable (#2229). Before this, `debugger._kept` dropped every debug row carrying such a sample. An armed `off_restore` entry is declared as the entity beside its value (`async_arm`), and the bare number an earlier release (v7.1.8) wrote is still read. The pre-R10-HOTFIX-COP-UNMEASURED keys `cop_baseline` and `cop_health_cusum` are declared `unread`, derived from `_COP_WATCH`, because 85ee2bfb renamed them without changing their shape. The debug ring's row declarations are now derived from the accuracy sample's, and they declare the row's own rule: `debugger._repair` drops a row whole (`whole=`). An armed entry's entity and value are declared as one pair.
- **D15-s1-05.** A capacity-envelope bucket that only a measured floor raised is stored with count 0 (#1955 fold e). Its loader now keeps it (`_learned_pair(entry, least=0)`), and `DOMAINS` declares the count as `_COUNT`.
- **D1-s2-06.** `boost._restore_settle` now checks `boosted_h` against its declaration (`admitted`) before calling `timedelta()`. The declared ceiling is `_SPAN_MAX_H`, the longest span two datetimes can bound. A sum of runs between stored instants is never longer, and `timedelta` can still hold it with the next run added (the ceiling of `timedelta.max` alone still overflowed in `_boosted_with`). A value past the ceiling reads as unknown, and the rest of the restore still runs.
- **D17-s3-03.** `SnapshotRing.best_restore` refuses a snapshot whose summary carries no bias, such as the first heartbeat's. This covers the service (`undo_target`) and the drift rollback. The bias is read through `const.finite_float`, the one coercion, which also replaces the local `float()` guard. Two restore fixtures in `tests/features.py` (the weekly snapshot after a factory reset, and `_lsl_ring`) took a snapshot with no accuracy evidence. Their subject is the undo point and the load race, so they now carry an in-band bias.
- **Same seam, built here.** `store.in_domain` read any text as the number it spells, so `admitted()` kept `"1.5"` in a number field, such as a debug row's `action_kw` or boost's `boosted_h`. Only a map key is now read as a number, because JSON keys are text. The census confirms no writer stores numeric text in a number field (Arm 6 green under the tightened rule).
- **D1-s2-01** already reads 0 at main: `_poisoned` has refused non-finite values since eab0738368 (R9-F1.6). The judge reproduced it only in a planted copy. Its harness is flat at both ends, and the companion is `tests/finite_boundary.py`'s own "the boundary quarantines nan at every depth" check, `ok` at both ends.
- **Census (P2 rule, fixer step 8).** `tests/finite_boundary.py` Arm 6 is the writer→`DOMAINS`→loader census. Its rich seed now holds an unpriced sample, a count-0 floor, the writer's armed mapping, and two debug rows, one of them unpriced. A new check drives an earlier release's COP-key document and the ring's snapshots of it. The census's debug saver used to re-seed a fresh row whenever the ring loaded empty, which hid every dropped row: that is why Arm 6 missed D15-s1-04. It now seeds only a ring with no start. `tests/entities.py` registers the coverage check and the round-trip check in `_P2_CENSUSES` (`store_domain_declares_writers`, `store_loader_keeps_writers`).

Alternatives not taken:
- Capacity envelope: storing the floor apart from the counted envelope would add a second key and a migration for the same fact. The count's meaning (capping samples) already admits 0.
- Boost: bounding at `timedelta.max` left the overflow in `_boosted_with`. Clamping to the two-hour window would change a stored value instead of reading it.
- Debug rows: keeping the alias and recording 27 new `_A6_CELL_SPENT` entries would have listed as debt the loader's designed whole-row rule.

## Head

`ea5c36ab348672cb9f93438075e40b43cd769292`, measured against merge base `1207ee13b0e439a4acefccabace691785af2ebad` (origin/main at the time of measurement).

## Mutation proof

Each mutant was applied to a detached worktree at the head, and the closure named was run with the driver's in-memory replace restored afterwards. `features_block.py` blocks run with the preludes it emitted (`--emit-prelude`).
- D1-s2-06, the restore read put back to main's `0.0 <= hours < math.inf`: `features_block.py` block `_bt_store = _he_store._tries()` goes red on "a stored boosted sum longer than two datetimes bound reads unknown ... (D1-s2-06)".
- D1-s2-06, the ceiling dropped (`space_settle/boosted_h: _Z0`): the same check goes red.
- D17-s3-03, main's predicate restored (`if bias is not None and abs(bias) > BIAS_BAND_C`): block `# D17-s3-03` goes red on "a snapshot whose accuracy summary carries no bias is no restore point ... (D17-s3-03)", run at `b54a76e0e6`.
- D17-s3-03, the band comparison at `>=` (the CMP_BOUND site `ci_predict` names): the same check goes red at the head (`'edge': (False, False)`). The `edge`/`past` arms were added for it.
- Text read as a number in any value (`if key and` removed): block `# D1-s1-02` goes red on "best_restore skips a non-numeric or out-of-band stored bias ... (R11-SEAM-store)". In `tests/finite_boundary.py`, see the census mutants below.
- Census mutants (`tests/finite_boundary.py`), run at `01a64e68bb`, whose `store.py`, `coordinator.py` and `tests/finite_boundary.py` differ from the head only by one `store.py` comment (`git diff 01a64e68bb b54a76e0e6 -- custom_components/heatpump_optimizer/store.py`):
  - `predicted_cost` back to non-null (D15-s1-04): 5 of 120 FAIL, including "every store the rich seed writes is seeded, and every field it writes is declared ..." and "the healthy rich seed round-trips unchanged ..." (`changed=['debug']`).
  - The envelope loader back to `_learned_pair(entry)` (D15-s1-05): 3 of 120 FAIL, including the round-trip check (`changed=['thermal_learning']`).
  - The envelope count's declaration back to `Domain("int", 1)` (D15-s1-05): 4 of 120 FAIL, including the coverage check (`capacity_envelope/-1/1`).
  - The armed entry's `entity_id`/`value` declarations deleted (D15-s1-04): 2 of 120 FAIL, the coverage check and the #3714 cell-cost check (`off_restore:...`).
  - The legacy COP-key line deleted (D15-s1-04): 1 of 120 FAIL, "an earlier release's COP watch keys ... are declared, and the loader reads none of them (D15-s1-04)" (`off=['cop_baseline~', ...]`).
  - The debug row's `whole=` dropped: 1 of 120 FAIL, the #3714 cell-cost check (`debug:rows/#/...`).
  - Text read as a number in any value (`if key and` removed): 1 of 120 FAIL, "each kind's shape and parse conjuncts decide alone" (`real refuses a value that spells a number`, `int refuses a value that spells an integer`).
- Unmutated blocks: both exit 0 (`none-boost`, `none-snap`).

## Null control

- At main's production code with this head's tests (a worktree at `1207ee13b0` carrying the three test files): `tests/finite_boundary.py` prints `5 of 120 FINITE BOUNDARY CHECKS FAILED`. The failures are the coverage check (`accuracy/samples/1/predicted_cost`, `capacity_envelope/-1/1`, the armed mapping), the legacy COP-key check, the round-trip check (`changed=['debug', 'thermal_learning']`), the out-of-domain probe sweep, and the cell-cost check. At the head it prints `ALL 120 FINITE BOUNDARY CHECKS PASSED`.
- The same worktree's features blocks: the D1-s2-06 check and the D17-s3-03 check FAIL at main and pass at the head. Each block's other check passes at both ends.
- Harness null controls: `capacity_envelope.py --nameplate` prints `fold_written_count_zero=0 lost=0` at main and at the head, so the loss is confined to the count-0 floor. `boost_settle.py`'s `control_restarts_raising=0` (`boosted_h=1.5`) holds at the head. `nan_boundary.py --sub Infinity` prints `leaves_reaching_live=0` at the head.

## Figures

Harnesses run in tree at main (`1207ee13b0`) and at `b54a76e0e6` with `PYTHONPATH=tests/hastub`. Each is cited with its sha1.
- `python3 dev/audit/rounds/round11/D1/s2/boost_settle.py` (sha1 17415b04dd56628fe892bec167881bc3a8f24a57): main `restarts_raising=8 per_cell=[0, 2, 2, 2, 2]`, head `restarts_raising=0 per_cell=[0, 0, 0, 0, 0]`.
- `python3 dev/audit/rounds/round11/D15/s1/domains_drift.py` (sha1 9a26c560e94171cad340cb05861a4f964c68b62a; synthetic arm only, the owner's bundle B is not in this seat): main `sample_none_cost_admitted=0 unit_row_kept=0/1 synthetic_written_rows_kept=0/192`, head `1`, `1/1`, `192/192`.
- `python3 dev/audit/rounds/round11/D15/s1/capacity_envelope.py` (sha1 56f0e94eb80475533fbb8a4443e6ef71d5431191): main `fold_written_count_zero=1 reloaded=0 lost=1 store_off_domain=1`, head `1`, `1`, `0`, `0`.
- `python3 dev/audit/rounds/round11/D17/s3/f03_restore_unevidenced.py` (sha1 8d1c189fca0994303fb3af6790ddf13c926aa4e4): main `restored=1 scale_after=1.0`, head `restored=0 scale_after=1.3` (refused: "No learner snapshot qualifies for restore").
- `python3 dev/audit/rounds/round11/D1/s2/nan_boundary.py --stores accuracy,dhw_profile` (sha1 2cf463c7121ec1cc1d76b5fa4f17496416f99c76): main and head `leaves_reaching_live=0 leaves_making_disk_undecodable=0`, flat at both ends (D1-s2-01 above).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` at the head. A first cut went over by one coordinator-class line, paid back in `_learned_pair`'s docstring.
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=1207ee13b0e439a4acefccabace691785af2ebad ./tests/run.sh` at `b54a76e0e6`: `MODE: SCOPED -- 22 script(s) run, 11 scoped out` (from `tests/closure.py select`), ending `24 TEST SCRIPT(S) PASSED; 10 SCOPED OUT AND NOT RUN`.
- The delta from `b54a76e0e6` to `43312aac55` (the D17-s3-03 edge arms and eight stale-pin deletions) scopes to `tests/doc_claims.py`, `tests/entities.py` and `tests/features.py` (`python3 tests/closure.py select --diff b54a76e0e6`). Each ran alone at `43312aac55`: `ALL 441 checks PASSED`, `ALL 2748 ENTITY CHECKS PASSED` and `ALL 6030 FEATURE CHECKS PASSED`. The head's last commit deletes one more stale pin, and that delta scopes to `tests/entities.py` alone (`python3 tests/closure.py select --diff 43312aac55`): `ALL 2748 ENTITY CHECKS PASSED` at the head.
- `python3 tests/doc_claims.py`: three new comment sentences over 40 words were split to pass it.

Seam enumerations (fixer step 8). Each rule was run on the head, and every seam it returns is dispositioned:
- D15-s1-04, the readers that drop on `DOMAINS`: `grep -n 'admitted(' custom_components/heatpump_optimizer/*.py` returns 9 sites outside its definition. `boost.py:619` is new here. `coordinator.py` 3043, 8281, 8294, 8301 and 8303 cover ledger parts. `debugger.py:166` covers debug rows. `driving_grade.py:120` is the ledger's `operation_drivers`, through the lambda at `coordinator.py:8301`. `snapshots.py:274` covers the snapshot summary. Every store they read is one Arm 6 seeds through its real saver and loader (`len(seeds) == len(LOADERS)`, asserted). The writer-side seams are the Arm 6 coverage check's output: at main it listed the fields above, and at the head it lists none.
- D15-s1-05: `grep -nE "setdefault\([^)]*\[[^]]*, *0\]\)" custom_components/heatpump_optimizer/*.py` returns 3 seams. `coordinator.py:9295` (capacity envelope) is closed here. `freq_control.py:162` is not a seam: the count increments before any save, and its loader accepts `>= 0`. `room_history.py:114` is not a stored `[value, count]` pair, because it persists as a share column (`_share`, `None` at 0 samples).
- D1-s2-06: `grep -nE 'timedelta\((hours|minutes|seconds|days)=' custom_components/heatpump_optimizer/*.py` returns 82 lines. 50 take a literal or a constant (the same grep with `| grep -vE 'timedelta\((hours|minutes|seconds|days)=[0-9.]+\)|=[A-Z_]+\)|=-?[0-9]'` leaves 32). Of those 32, one takes a stored document's number, `boost.py:618`, closed here. The rest take configuration, a constant table (`LEAD_BUCKETS`), a computed elapsed time, or a learner split bounded by its step (`duty_switch.py:540`).
- D17-s3-03: `grep -n 'best_restore\|undo_target' custom_components/heatpump_optimizer/coordinator.py` returns three callers: `coordinator.py:1376`, `:9667` (the drift rollback) and `:9705` (the service, through `undo_target`). All three reach `best_restore`, which this diff closes.

## Architecture score

Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff 1207ee13b0 HEAD`)

## Red checks

- `tests / mutation` (predicted): `ci_predict.py` (prepr step 6d) names the 9 added unpinned sites listed under `## Unpinned sites`. mutation-autofix (`tests/mutation_table.py --pin-killed`) records them on this branch after the push (ci-autofix.md). That job is the cheaper detector, at a standing cost of one bot commit.

## Unpinned sites

`ci_predict.py` (prepr step 6d) names 9 added sites. All are under `custom_components/`, so mutation-autofix's lane measures them after the push:
- custom_components/heatpump_optimizer/coordinator.py:493 CMP_BOUND*2: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:493 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/snapshots.py:229 CMP_BOUND: pinned by mutation-autofix (killed by the D17-s3-03 check's edge arm, measured above)
- custom_components/heatpump_optimizer/snapshots.py:229 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/store.py:247 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/store.py:610 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/store.py:696 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/store.py:696 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/store.py:706 RETURN_DEL: pinned by mutation-autofix

The nine `killed_by` pins whose old lines this diff rewrites are deleted, as `ci_predict.py` instructs: `boost.py` `_restore_settle` CMP_BOUND; `coordinator.py` `_learned_pair` GUARD_OFF; `snapshots.py` `best_restore` GUARD_OFF x2; `store.py` `_declared` BOOLOP and RETURN_DEL, `admitted` RETURN_DEL, and `in_domain` BOOLOP and GUARD_OFF. mutation-autofix pins the edited lines afresh.

## Forward-carry

Part 1 of 2: this pull request is the five built findings. Carry 0 (the late P1 sweep's six loaders that read a stored boolean as a number: `dhw_draws.py`, `tariff.py`, `off_restore.py`, two `coordinator.py` loaders, `legionella.py`) and Carry 1 (the late P2 sweep's three readers of the DHW weekday/weekend windows: `boost.py`, the coordinator's circulation pump, `dhw_learning.py`) are deferred to Part 2 of 2, built as a second part (orchestrator ruling under mandate 6893738184). Carry: dismissed: owed to R11-SEAM-store Part 2 of 2, carries 0 and 1 (orchestrator queues append-carry on the roster, P-R11-84 workaround)

## Friction

none
