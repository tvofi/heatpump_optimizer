Fix review: merge 7ff8d4848a3ebeb46f5ed1135ee4a45d9b8d725d

bus-nonce: a2874ff7b42e51cc4c2007a91a2e39cc

## Scope

This is the fifth fix-review dispatch on PR 3299 and the third delta round. The earlier verdicts were: blocked at `f00e035b5` (code round 1); merge at `85ba6cda8` (round 2); blocked at `e2254515` (ci-red, stress); and blocked at `83b0be72` (ci-red, `tests / mutation` refused on a stale `_prefill_errors RETURN_DEL 7451af7c` pin). As the owner's scope ruling requires, I reviewed only `git diff 83b0be72a116b3c09872c37deb0ca122a9922bb2 7ff8d4848a3ebeb46f5ed1135ee4a45d9b8d725d`. The branch has two authored commits since then, `d6e73c472` (deletes the stale pin) and `14c31e564` (German strings). It also has three merges of main: `f31e6be86`, `5fc731c63` and `7ff8d4848`. `review_carry.py 83b0be72 7ff8d4848` prints `FRESH-REVIEW`, so I reviewed the delta directly.

The production delta comes almost entirely from main. Main's changes come mainly from R10-WATER-SETPOINT-LIFT (#3372) in `pump_arbiter.py`, `topology.py`, `thermal_model.py`, `const.py` and `config_flow.py`, plus R10-I18N-DE (`translations/de.json`). The branch's own production lines in the delta are only `de.json` and the card's `de` dictionary (`14c31e564`).

I did not widen the review. Main's #3372 adds no new key that the optimizer writes an entity for. It adds a `return` unit and the `flow_min_lift_k` / `flow_heat_c` numbers on the same `space_setpoint_entity` key. So the branch's `_written_entity_collision` over `_WRITTEN_ENTITY_KEYS` still covers every written entity. The branch's own modules, `heat_curve.py` and `off_restore.py`, import nothing that #3372 changed. `config_flow.py` and `const.py` auto-merged in disjoint hunks.

`git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.

## Evidence

- Head measured: `7ff8d4848a3ebeb46f5ed1135ee4a45d9b8d725d` (ev/HEAD.txt). At verdict time, `refs/pull/3299/head` is still this SHA. The body's `## Head` names this head.
- Main merge: `git merge-tree --write-tree origin/main 7ff8d4848` exits 0. Its merge base equals origin/main `2f6d699e5`, so the head is level with main (ev/merge-tree.txt).
- Previous finding (block at `83b0be72`) resolved: `tests/mutation_ledger/killed_by/config_flow.py/_prefill_errors.RETURN_DEL.7451af7c.json` is gone at this head, and `_prefill_errors.RETURN_DEL.66f7970d` remains. `python3 tests/mutation_table.py --scope changed --base origin/main --max 0 --jobs 1` returns rc=0 with `2700 unpinned site(s) of 6995 candidate sites, 2703 at the ratchet base 2f6d699e5...; the ledger agrees with the deterministic inventory` (ev/mutation_table_max0.txt). Mutant: restoring the deleted file (from `d6e73c472^`) gives rc=1 and `MUTATION TABLE REFUSED ... _prefill_errors RETURN_DEL 7451af7c: disposition names no site the inventory generates` (ev/mutant_stale_pin_restored.txt). I removed the file again afterwards, and `git status` was clean. CI `tests / mutation` (job 129354170896) concluded success at this head.
- Previous stress red (`tests / fast (3.14)`, from the e2254515 and 83b0be72 rounds): main's #3349 fix `53f4a051b` is in this head's ancestry. `tests / fast (3.14)` (job 129354517102) concluded success at this head.
- Merge resolutions, each checked against the automatic `git merge-tree` of its parents:
  - `f31e6be86`: the only hand change is `tests/golden/claimed_drift.txt` (`MERGE-CLAIM` refused, `CONFLICTING CLAIMS` on `config_flow`). The resolution keeps this branch's line and drops R10-WATER-SETPOINT-LIFT's line, which is main's own and already in the merge base. That is correct under claim-files.md.
  - `5fc731c63`: hand changes are `claimed_drift.txt` (this branch's line kept under main's emptied 7.1.9 list) and `tests/deployment_shape.py` (three count hunks resolved to the sum of both sides). The package count of 107 matches `git ls-files custom_components/heatpump_optimizer/ | wc -l` = 107 at this head. The pair count goes 145 to 146 as the body says. The other `deployment_shape.py` checks pass.
  - `7ff8d4848`: its tree equals the automatic merge-tree, so it carries no hand resolution.
- Claim files: `git diff origin/main 7ff8d4848 -- tests/golden/claimed_drift.txt` is the single added `config_flow # R10-GENERIC-HEAT-CURVE` line. `card_claimed_drift.txt` is identical to main's. `env_drift.py --all 2f6d699e5` returns rc=0, `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56 committed fixture(s)` (ev/env_drift_all.txt). `env_drift.py --claims-only origin/main` returns `claims hygiene: origin/main ok` (ev/claims_only.txt).
- `VERSION`, `manifest.json` and the `RELEASE_NOTES.md` heading do not differ from origin/main.
- Mutation proof for `14c31e564`, run in a separate detached worktree at this head:
  - Card mutant: I deleted `"health.input_heat_curve_displace_entity"` from the card's `de` dictionary. `node tests/card.mjs` returns rc=1 with `3 CARD CHECK(S) FAILED`: key-for-key parity, its null-control line, and `UX-HEALTH A: the card's de input labels are the options flow's`. KILLED (ev/mutant_card_key.txt).
  - de.json mutant: I deleted `options.error.heat_curve_not_offset` from `translations/de.json`. `dev/audit/rounds/round4/D6/claims.py` rewrites C112 to FALSE with `missing={'de': 1, ...}`. KILLED (ev/mutant_de_key_claims.txt). This is the claims register that prepr refuses on, and the body's account names it.
  - I restored both files, and `git status` was clean.
  - Unmutated: `card.mjs` gives ALL CARD CHECKS PASSED (ev/card_unmutated_wt2.txt, after `tests/plan_view.py`). The `card rc=1` in ev/card.txt is a run in the other worktree that skipped `plan_view.py`'s payload precondition (`plan payload ... not found`), not a check failure.
- Unmutated at this head:
  - `tests/entities.py`: ALL 2707 ENTITY CHECKS PASSED, which includes the de.json key-parity check (ev/entities_tail.txt).
  - `tests/config_flow_steps.py`: ALL 561 checks PASSED.
  - `tests/deployment_shape.py`: ALL DEPLOYMENT SHAPE CHECKS PASSED.
  - `tests/structure.py`: STRUCTURE RATCHET PASSED.
  
  Each of these numbers matches the body's figures for `14c31e564` and `5fc731c63`.
- CI at this head: `merge_train.py classify 7ff8d4848a3ebeb46f5ed1135ee4a45d9b8d725d --pr 3299`, re-run every 60 s, read WAIT from 18:47Z, then exited 0 at 19:29Z with `GREEN 7ff8d4848a3ebeb46f5ed1135ee4a45d9b8d725d pending: none red: none` (ev/classify.log, ev/classify_final.txt). I read all 43 check runs live. Every context `merge_train.py owed-reds` lists (ev/owed-reds.txt) concluded success or skipped: `gate`, `pr-contract / pr-contract` (finished 19:28:49Z, after every other run), `tests / mutation`, `tests / fast (3.14)`, `tests / closures`, `tests / coverage`, `tests / coverage-ratchet`, `codeql / Analyze (python)` and the rest.
- The one red at this head is `tests / replay` (job 129354517194, failure). It is not in the owed-reds set, so under the owner's 2026-11-09 red-check ruling it owes no `## Red checks` answer and cannot block. I name it here only.
- The `## Red checks` answer for `83b0be72`'s `tests / mutation` red is present in the body. It names the cheaper detector (the source-only `completeness_problems`, which the `merge-main.yml` bot merge does not run) and routes it to the root-cause seat. That satisfies step 11's trigger. `pr-contract` is green after the last red.
- Figures I did not re-derive: the body's prepr run times, its order-preservation script output (`existing order preserved: True`), and the sampled `--max 10` mutant run it marks `unmeasured`.

## Findings

None.
