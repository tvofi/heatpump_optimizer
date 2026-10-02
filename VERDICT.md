Fix review: blocked a5060e6a61f1d4583cf4d0517e1a13573ef2d29a mutation-vacuous: the restart check pinning lead=None (the bug this PR fixes) goes vacuous at 2026-10-03T06:00Z; also closures red unrepaired, manual-release overclaim, comfort "why" not carried to UX-5
bus-nonce: b19faef0cca54a7981d811ba19f3884b

Round 1. Reviewer: opus fix-review seat, detached worktree at the head. Main was 03ba7f70 (the merge base) for the whole review; `merge-tree` against it is clean. `tools/audit/briefs/` is unchanged between the merge base and main.

## Blocking

1. **mutation-vacuous: the restart pin has a fixed expiry.** `_ux4_released()` defaults `expires="2026-10-03T08:00:00+02:00"`, and the UX-4 block does not freeze the clock. The store's default bound rewrites only instants ahead of `now`, so the check that "found" the `lead=None` bug kills its mutant only until that instant passes.
   - RESULT LEAD_DEFAULT (delete `lead=None,`) at the real clock (2026-10-02 22:46Z): KILLED, 1 of 18 (UX-4 restart).
   - RESULT LEAD_DEFAULT with `dt.freeze(2026-10-03T07:00Z)`: SURVIVED, ALL 18 UX4 PASSED.
   - RESULT the unmutated block under the same freeze: ALL 18 UX4 PASSED (control).
   - Repair: freeze the clock in the block, or derive the expiry from `dt_util.now()` plus a margin.
2. **closures red, autofix did not repair (CI run 37073640871).**
   - `closures`: `UNDER-SCOPED: tests/features.py really reads 2 file(s) the committed closure does not list: blueprints/automation/notifications.yaml, docs/automations.md`. The hand edits put the blueprint in the entities.py and doc_claims.py closures only, and the UX-4 block in features.py reads both files.
   - `closures-autofix`: `skip-classifier-disagrees`. The base's closure.py has no INERT_EXCEPT line for the new blueprint.
   - Owed: a hand-merge of the Linux recording, adding those two paths to `tests/features.py`'s closure, plus a `## Red checks` entry naming UNDER-SCOPED. The body currently says "None on a pushed commit".
3. **claims: "once per channel and override" is stronger than the code.** `_manual` clears its key whenever a solve releases nothing, and `released_*` is re-derived on every solve (`_record_manual_release`).
   - RESULT manual_flicker_same_override (release, no release, release) fires = [1, 0, 1].
   - The body and `docs/automations.md` both state "once per channel and override". Unlike the comfort oscillation, this is not disclosed.
   - Repair: either key the clear on the override ending (manual_plan absent or expiry changed), or state the per-episode behaviour in the docs and the body.
4. **carry-missing: not carried to R9-UX-5.** DESIGN-UX.md UX-4 asks the comfort event to say "why" ("the fuse limit caps heating 02:00–05:00"). The PR ships `peak_guard_suppressing` and defers the rest to UX-5's sub-codes, yet Forward-carry is `none`. The R9-UX-5 roster brief says nothing about extending `EVENT_DATA` or the comfort event. The deviation is honestly stated and acceptable for a first cut, but it must be written into UX-5's brief (finding-propagation.md) or waived by tvofi.

## Verified

- **Mutation, re-driven by hand against the UX-4 block alone** (`ALL 18 UX4 PASSED` unmutated, reproduced):
  - CMP_BOUND 102: `>` KILLED (1 check: at the floor), `<=` KILLED (10).
  - GUARD 130, 197, 221 (dedupe), 234, 252: KILLED.
  - BOOLOP 200, 213, 215, 225, 231: KILLED.
  - RETURN_DEL 155: KILLED.
  - CONST 35: KILLED.
  - CMP 122 (`!= "stale"`): KILLED.
  - GUARD 76 and 99: crash the block, so KILLED by exception.
  - My own 141 (`return None` for an absent manual_plan): KILLED by the restart check.
  - One survivor of my own shape, outside the table's operators: 145 `if isinstance(...)` changed to `if True` (no non-int step is fed). An observation only.
  - The CI mutation lane was still in progress at posting; it is not cited.
- **Once, re-arm, restart:**
  - Every repeat-signal null control reproduces `[[], [], []]`.
  - RESULT restart_far_future_expiry (2099 expiry, real store) fires = [1, 0], so `lead=None` does hold the key across a restart.
  - RESULT comfort_oscillation (18.9 / 19.1 alternating) fires = [1, 0, 1, 0, 1]. This is the disclosed no-hysteresis behaviour, honestly stated and acceptable for a first cut.
- **Quiet hours:** I evaluated the `quiet` template as Python (no jinja2 locally; it uses only and/or and chained comparisons). 22:00–07:00 is quiet at 22:00, 23:30, 00:30 and 06:59, and not at 07:00, 12:00 or 21:59. 01:00–05:00 holds within a single day. Equal start and end turn quiet hours off. The comfort branch alone lacks `not quiet`, so it passes through. The feature check only asserts that the event name is present, so nothing pins this behaviour.
- **Classification:**
  - The INERT_EXCEPT edit is one line and follows the three existing blueprints.
  - `notifier.py` is in exactly the 12 closures holding `frontend.py` plus `__init__.py`.
  - The blueprint is in the same 2 closures as the existing blueprints. That is incomplete per item 2.
  - tests/closure.py is code-owned, so tvofi's review is needed, as the body says.
- **Counts:**
  - 70 modules and 88 package files.
  - 26 module-level homeassistant importers, re-derived with `ast` over top-level statements.
  - I did not re-derive the 43 HA-free figure under the tree's "touching anywhere" rule; my grep definition gives 28, not 27.
  - RESULT harness_headers ALL 94 PASSED; deployment_shape PASSED; structure STRUCTURE RATCHET PASSED; finite_boundary ALL 69 PASSED.
  - entities: ALL 2081 PASSED. A first run showed 22 failures caused by my own untracked runner files in tests/; it is clean with them removed.
- **VERSION, manifest and notes heading:** untouched. **Fixtures:** none moved; no golden or claim file is in the diff.
- **CI at the head:** red closures and closures-autofix (item 2). nightly-status is red, but that is main's; the diff reaches only its own delivery row. fast (3.14), coverage, typing, hassfest and pr-contract are green.

Could not run locally: features.py in full (numpy BLAS; CI's fast lane is green), and the mutation table (CI's lane was still running).
