Fix review: blocked b5c9e5bbae47eb464c081be3202a09ea156ab606 root-cause-unanswered: mutation, fast (3.14) and pr-contract went red, unanswered

bus-nonce: 3f7ad37fa8012a616e533491325954f5

Measured head: b5c9e5bbae47eb464c081be3202a09ea156ab606 (PR #2120, `fix/r9-ux-7`),
merge base 70b50c5730d7, in a detached worktree at that head. `git ls-remote
origin refs/heads/fix/r9-ux-7` was still b5c9e5bba… when this verdict was posted.
Merge conflict measured clean: `git merge-tree --write-tree origin/main <head>`
exits 0, no driver marker.

WHY BLOCKED (contract step 11)
==============================

The body's `## Red checks` opens: "Nothing has been pushed to CI yet, so there
is no pushed-head red." At the measured head that is false. The check-runs API
(read directly, not `gh pr checks`) reports, against b5c9e5bba…:

- `mutation` — completed, FAILURE (job 114248575047, run 38064236516).
- `fast (3.14)` — completed, FAILURE (job 114248575023), after this review's
  local run predicted it (below); the body names neither.
- `pr-contract` — completed, FAILURE, twice (114248586474, 114248516839).
- `mutation-autofix` — completed, FAILURE (114250148730).

Both `mutation` and `pr-contract` are required checks (ruleset 23698884). The
body names neither. `pr-contract`'s own failing step 9 prints the rule:

  ERROR [pr-body] check `mutation` is red and `## Red checks` does not name it.
  Name the failure and answer it: the cheaper detector and its standing cost,
  or the finding that none exists.

`mutation-autofix` failing settles that this is not a "wait for the bot" case:
per ci-autofix.md a red autofix job means there will be no bot commit. Its push
step was SKIPPED and its report step failed — the quiet statuses are `changed`,
`skip-not-allowed`, `skip-not-unpinned`, `skip-nothing-killed`, `skip-head-moved`
(tests/closure.py AUTOFIX_QUIET), so the measured status was one of the
reddening ones (`skip-unchanged`, `skip-measure-failed`, `skip-nothing-drivable`,
`skip-no-measurement`). The branch's own `## Unpinned sites` disposal of the 11
sites is not the answer the contract asks for, and the head did not move, so
`skip-head-moved` is not it.

`fast (3.14)` completed FAILURE while this review ran. My own `env_drift.py
--all` at this head — the command the `fast` job runs, per tests.yml's header
comment — reports, and predicted the red before it landed (evidence/env_drift.txt):

  5 UNCLAIMED DRIFT(S) vs origin/main
    DRIFT coord_all_features/coord_dhw/coord_grid_fee/coord_minimal/
         coord_two_zone: sensors.indoor_temp_predicted and sensors.model_status
         "present on one side only"
  5 COMMITTED FIXTURE(S) ARE STALE — the committed tests/golden/coord_*.json
  carry no model_status / indoor_temp_predicted sensor (verified by reading
  tests/golden/coord_minimal.json's `sensors` dict).

The diff touches neither tests/golden/claimed_drift.txt nor tests/golden/
coord_*.json. `fast` is therefore red on work the branch itself introduced. The tree's own precedent is that this is owed in the same PR:
412b671ba "fix(#1936): claim the advisor's coordinator-capture drift",
63414e06a "fix(R9-UX-9): record the structural keys the code now publishes;
claim them", 965860aa0 "claim the coordinator captures' new horizon_hours key".
The body instead quotes the weaker `env_drift.py` (no `--all`), which printed
"NO STALE FIXTURE" over the 5 sensitive scenarios only. If `fast` lands red on
this, it joins the unanswered list above.

WHAT I VERIFIED GREEN (so the repair round does not re-litigate it)
===================================================================

- RESULT entities head: `PYTHONPATH=tests/hastub python3.13 tests/entities.py`
  at b5c9e5bba… — ALL 2267 ENTITY CHECKS PASSED (matches the body's figure).
  Note the tree needs Python >= 3.12 (pre-existing f-string at entities.py:3935).
- RESULT mutation proof re-run (contract step 1), three mutants, each
  ast.parse-checked, tree restored clean after (evidence/mutants.txt):
  M1 diagnostics `_without_private_ids` str arm -> `2 of 2267 ENTITY CHECKS
  FAILED`, naming both leak checks; M2 sensor COP-alarm guard -> `1 of 2267`,
  naming the status check; M3 coordinator `predicted_next_room_temp` return ->
  `3 of 2267`, naming the three the body names. Not vacuous; figures match the
  body exactly.
- RESULT card_drift: `node tests/card_drift.mjs origin/main` (after
  tests/plan_view.py) — "39 state(s) moved and claimed, 1 identical". Matches.
- RESULT unpinned enumeration: `python3 tools/pr/ci_predict.py --base
  origin/main` prints exactly 11 ADDED UNPINNED sites, the same 11 the body
  dispositions. No seam the rule returns is undispositioned (step 6).
- RESULT learning view: `class LearningView` (payload.py:652) and
  `_learning_view()` (coordinator.py:7454) exist at the merge base and
  `Payload` inherits `LearningView`, so every key the new sensors read
  (cop_health, house_heat_loss_*, lower_floor_loss_*, solar_aperture,
  capacity_envelope, system_identification, internal_gains_profile) is already
  published at the base. All 8 INPUT_KEYS are declared in InputHealthView at
  the base. `last_diagnosis` is absent from main's diagnostics.py as claimed.
- RESULT duplicate check: `learning_model_status`, `indoor_temperature_predicted`,
  `_without_private_ids`, `_published_sections`, `PRIVATE_ENTITY_ID`,
  `def predicted_next_room_temp` each answer 0 files at the merge base; the
  roster/uniqueness checks in entities.py pass at the head. One body figure I
  could NOT re-derive as stated (step 8): the literal
  `git grep -l predicted_next_room_temp <base>` returns 5 files (the private
  method is a substring); the 0-file claim holds only for `def
  predicted_next_room_temp`.
- RESULT enum: `MODEL_STATUS_STATES = (learning, learned, attention)` covers
  every reachable combination; the never-updated case returns None (unknown,
  tested) and the never-learned case maps to `learning` with `samples: 0` in
  the attributes, which the card words as "Still the settings' estimate".
  No missing initial state. State names translated in strings.json/en.json/sv.json.
- RESULT carry (step 10): forward-carry is "none"; the honoured claim verified —
  HEALTH_WAITING is unchanged, the new Health block reads only the
  enabled-by-default `_learning_model_status` sensor and is absent while that
  sensor is unavailable, so it never expects `waiting_for` from an unavailable
  sensor (carry-1795.json third entry).
- RESULT closes-nothing verified: #1795 is closed (2026-10-10T06:37:59Z, by
  #2010's merge); the only closing keyword in the body sits inside a code span
  (does not fire); delivery/2010.md does read `**open**` as the Friction says.
- RESULT version: pr-contract's own prepr step printed "no version edit".
- RESULT structure: `STRUCTURE RATCHET PASSED` at the head, max_class_loc
  8814 <= 8814.

SECONDARY FINDINGS (recorded, not the blocking class)
=====================================================

1. The max_class_loc "payment of 4" is entirely a comment shave. Restoring the
   4-line `# Reports learned=True ... See dev/archive/backlog.md, "Open"`
   comment in HeatPumpOptimizerCoordinator makes structure.py print
   `FAIL max_class_loc 8818 > 8814 (+4)` (evidence/structure_comment_restored.txt).
   The budget edit was not required — at 8818 the old budget 8818 still passes —
   so the -4 is a voluntary tightening bought by deleting a comment in the
   largest class. The comment was stale (the backlog item it cites is marked
   "Status: closed (#110, cca2b115)"), which is why I do not class this
   metric-gamed, but the orchestrator should know the payment buys no
   architecture. The deletion is also the only change in coordinator.py's class
   body, and it removes a caveat about `house_heat_loss_learned` — the very
   flag the new sensor's state rests on.

2. The design of record (handoff/round9/state/alt/design/ux/DESIGN-UX.md, UX-7,
   on origin/handoff/audit-r9-alt — not on main) asks each row for "days of
   evidence against what the learner needs". The implementation publishes
   samples (only solar has a published need, SOLAR_APERTURE_MIN_SAMPLES=30) and
   the heat-loss evidence bar is binary (learned ? 1 : 0). docs/dashboard-card.md
   discloses "The counts are samples, not days", so I read this as a disclosed
   deviation rather than a missing design trace.

Repair path: name and answer `mutation`, `fast (3.14)` and `pr-contract`
under `## Red checks`; the coordinator-capture
drift the two new sensors cause must be claimed in tests/golden/
claimed_drift.txt and the structural keys recorded in the coord_*.json fixtures
on the canonical environment, as 412b671ba / 63414e06a did.

Evidence: /Users/timmalmstrom/hpo-seats/r9rev-2120/ev/ — checkruns.txt,
env_drift.txt, entities_head.log, mutants.txt, card_drift.txt, ci_predict.txt,
structure_head.txt, structure_comment_restored.txt. Each names the head
b5c9e5bbae47eb464c081be3202a09ea156ab606 or was produced in the detached
worktree at it.
