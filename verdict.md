Fix review: merge 6a18dda78921c90404e51171639e49f3588982b8

bus-nonce: 44c31e2a541ab30acac64780324f2c02

## Summary

Round 1 review of #3052 (R10-HOTFIX-AWAY-PRESENCE). I measured head 6a18dda78921c90404e51171639e49f3588982b8 from detached worktrees at the head and at the merge base c3a47e5656ef858674a1fd011c0e2f039c4ed838. The roles diff from the merge base to origin/main is empty, so this contract is current. At verdict time the branch head is still 6a18dda7 (`git ls-remote`). The fix does what the brief asks. A listener on `away_presence_entity` and on `holiday_calendar_entity` requests the coordinator's debounced refresh only when the interpreted reading changes. Every mutant of the fix that I ran turns a named check red. The deleted `_unsub_timer` was dead code.

## Findings

none

## Evidence

- RESULT companion `dev/audit/harnesses/r10_away_presence_listener.py` (sha1 2f7665bb), base with the harness copied in: 7 flip arms `listeners=0 refreshes=0 wait_min=30.0`, and `reload_handover next_solve_in_min=20.0 plan_age_min=10.0`. Head: 7 flip arms `listeners=1 refreshes=1 wait_min=0.0`, 6 hold arms `listeners=1 refreshes=0`, `unconfigured listeners=0`, and `reload_handover next_solve_in_min=0.0 plan_age_min=10.0`. The base is red and the head is green, as the brief requires (ev/companion_base.txt, ev/companion_head.txt).
- RESULT finder's harness `dev/audit/harnesses/r10_live_away_heating.py` (sha1 822ccca2, the probe aa6e5db30's harness, run as the probe states): 13 RESULT/VERDICT lines, byte-identical at the base and at the head. It is flat by design, because the fix does not touch the solve: flat, not regressed (ev/finder_base.txt, ev/finder_head.txt).
- Null control, re-run: at the head, the six hold changes request 0 refreshes and each still has its listener (count 1). So the control is not vacuous. The handover plan-age control reads 10 min at both ends.
- Mutation proof, `PYTHONPATH=tests/hastub python3 tests/features.py` per mutant. The head itself reads ALL 4666 PASSED. Diffs are in ev/mutant_*.diff, outputs in ev/features_*.txt.
  - m1, coordinator registration line deleted: 3 of 4666 failed (the flip check, the null control and the registration check).
  - m2, `_watch` comparison replaced by `if True:`: 1 failed (the null control).
  - m3, the handover's `next_optimization` line deleted: 1 failed (the handover check, 20 min ahead).
  - m4, the holiday entry dropped from `reads`: 3 failed.
  - mis (my own mutant), `is True` dropped from `_away_of` so that None and False differ: 1 failed (the null control's `unavailable -> home` hold).
- away.py:596 `holiday_dates` RETURN_DEL, measured by me rather than predicted: `return _holiday_days(...)` replaced by `pass`. features.py crashes with TypeError at the W5-G8 c holiday check (line 51113, `sorted(None)`), rc=1. CI's `tests / mutation` lane (job 124660774212) also prints `away.py:596 RETURN_DEL -- killed by tests/features.py`.
- `_unsub_timer` deletion: at the base, `grep -rn _unsub_timer` finds only the `None` init (coordinator.py:3348) and the shutdown branch (6300-6302). Nothing else assigns it, and `git log -S` traces it to ec45dc4d5 (v1.0.0). At the head, the grep returns nothing.
  - I restored the attribute and its branch (munsub). features.py stays ALL 4666 PASSED, so behaviour is unchanged.
  - With the restore, `tests/structure.py` fails `class_excess_loc 17657 > 17653`, `coordinator_attrs 142 > 141`, `coordinator_multiassigned_attrs 109 > 108` and `max_class_loc 8061 > 8057`. So the ratchet's movement is earned by the deletion and not by the instrument. Every row moved down and no budget was raised. The reason is in commit fddb9a1bf's message.
  - `python3 tests/structure.py` at the head prints STRUCTURE RATCHET PASSED. It has no `summary` argument, so I ran it plain.
- Holiday-calendar extension, judged as built: it is sound. It reuses `holiday_dates`'s own reading through the extracted `_holiday_days`, so the listener and the solve read the calendar identically.
  - It has its own flip arms (off→on, and on→on with a span one day longer) and its own null arms (on→on with the same span, and off→off with a new span). It failed first at the base (4 checks red) and m4 kills it.
  - It widens the blast radius only by one listener per configured calendar, which the entry's unload drops (checked).
  - If the same calendar is configured in both slots, the dict keys collide and one listener with the holiday reader remains. This loses no refresh, because an on/off flip always changes `_holiday_days`: "on" yields at least one day. I read this from the code; I did not test it.
- The reload-window carry: the handover's `next_optimization` is now the current time, consumed once (`self._reload_handover` is set to None). The card's `healthPlanHtml` and the `next_optimization` sensor read "due now". The window's two bounds are the existing pins the body cites; I did not re-derive them beyond reading the code path.
- Class (step 6): I re-ran the body's census rule at the head. It returns exactly the two seams (`holiday_dates(` in `_solve_hubs` and `_entity_state(config.presence_entity)` in `_resolve_away`), and both are in the diff.
  - My own wider grep of `states.get(`/`_entity_state(` in coordinator.py finds only price, weather and power readings, none a band switch (ev/class_census.txt).
- Local-only gate failures, now green in CI: in `tests / fast (3.14)` (job 124660741780), `ok node tests/card.mjs (109s)` and `ok python3 tests/entities.py (514s)` both pass.
  - That job prints `ALL 2493 ENTITY CHECKS PASSED` and `ALL CARD CHECKS PASSED`, and its `hb:positive_control` lines show that the heartbeat-sampler block ran there.
  - The job's MODE line is `MODE: SCOPED -- 22 script(s) run, 11 scoped out.` and the job ends `23 TEST SCRIPT(S) PASSED; 10 SCOPED OUT AND NOT RUN` (ev/ci_fast_lane.txt).
- CI state at 6a18dda7: I read all 133 check runs (3 pages of the commit check-runs API; ev/check_runs_6a18dda7.jsonl). The latest run of each of 46 names is success, skipped or neutral, including `gate`, `pr-contract / pr-contract`, `tests / mutation` (MUTATION TABLE PASSED, with 6 pins from the bot's commit) and `budget-raise-gate`.
  - `merge_train.py classify` exited 2 (unreadable) twice (ev/classify_*.txt). Its `gh api --paginate` follows a `repositories/{id}` next link, which this container's proxy refuses with HTTP 403. The green state above therefore comes from my own paged read, not from the classifier.
- Red checks at this head: two earlier `pr-contract / pr-contract` failures (124660742790, 124660737501). The body's `## Red checks` names them and answers them (the body's wording, with `body_patch.sh` as the cheaper detector). The later run 124661812756 is green, so it is the evidence.
  - The body also names `tests / mutation` red at fddb9a1bf as red by construction, and the bot's pins answer it. The pins record kills measured by `mutation_table.py --pin-killed` (rc 0 to rc 1), and my m596/mis/m2 runs reproduce the behaviour they pin.
- Merge: `git merge-tree --write-tree origin/main 6a18dda7` (main f3c9144b) exits 0. There are no claim-driver lines, because no claim file conflicts (ev/merge_tree.txt).
- Claim files: in the three-dot diff, `claimed_drift.txt` and `card_claimed_drift.txt` are untouched. `VERSION`, `RELEASE_NOTES.md` and `manifest.json` are identical to origin/main.
- Delivery row: `dev/programme/delivery/3052.md` is in the three-dot diff.
- Head named in the body: 6a18dda78921c90404e51171639e49f3588982b8, the head I measured. The body's figure `4666 FEATURE CHECKS` matches my local run. CI's synthetic merge reads 4667, because main added checks since the merge base.
- Figures I did not re-derive: the body's local gate MODE line against 14ed1355 (I cite CI's MODE line instead), and its M5/M6 scratch probes (CI's mutation lane reports away.py:244 and :262 killed, and pins :265 as `_watch.RETURN_DEL`).
