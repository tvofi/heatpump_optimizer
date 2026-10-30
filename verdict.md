Fix review: merge 1381df1f5b25e2e3585035c8fceaec1bce3dcdc2

bus-nonce: bda62683f7b6973c0cc2f7f1ec41da87

## Scope

Fix-review seat (dev/governance/roles/fix-review.md, read at origin/main 043b111d0; `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current). PR #2976, group R10-UX-HEALTH, round 1. Measured head 1381df1f5b25e2e3585035c8fceaec1bce3dcdc2 from a detached worktree. Merge base and origin/main are both 043b111d01c90ecb1220980df1d363c0b50bb37f. Approved design: `design/R10-UX-HEALTH` e6797ca9d. Re-read before publishing: the branch head is still 1381df1f5 and origin/main is still 043b111d0.

## Findings

- Design deviation, arm A backend arm. The design says the `tests/entities.py` arm "runs one cycle on a fully configured stub" and asserts `health.ages()` keys are a subset of the options-flow field set. The PR instead enumerates the read keys statically, from every `InputReader.read*` call site, through an AST walk. Any call keyed some other way is refused. The body describes the mechanism but does not call it a departure. I judged it sounder than the design: it covers every call site rather than the reads one stub cycle happens to reach, and it refuses unseen key shapes. A trace found that `InputHealth.readings` is written only through `InputHealth.record`, which only `InputReader.read`/`read_state` call, and that no read passes its key by keyword. Its null control reproduces: 29 keys unperturbed; fails naming `zz_probe_entity`; fails naming `flow_meter.py:154` for a `k["x"]` key (ev/entities_arm_null_control.txt). Carry: dismissed: static call-site enumeration is a superset of one stub cycle's reads and refuses unseen shapes; no architecture breach.
- Design deviation, arm H refresh cadence. The design calls `debug_collect` status "on Health page entry and after a start". `healthDebugHtml` refreshes from inside the render whenever 60 s have passed since the last call. That makes one `config/entity_registry/get` plus one `debug_collect` call per minute while the Health page is open and redrawing. `healthPageHtml` is drawn only for the active Health page (card line 14624), so it does not poll elsewhere. Carry: dismissed: the cost is two light calls a minute, only while Health is open, and the row then also follows a collection that finishes while the page is open.
- Defect, arm H edge. `host._debugArmed` is never cleared except by the second Start. If a user arms the confirm, leaves, and the collection is later restarted elsewhere and finishes again, the next visit opens straight on the confirm text. Separately, a `debug_start` whose `callService` throws stores `_debug = null`, so the row reads "off" beside a finished collection until the next 60 s refresh. `debugger.async_command("start")` raises on no path, so only a transport failure reaches this. Carry: dismissed: both need an unusual sequence, are cosmetic, discard nothing (the confirm still precedes any discard), and recover within a minute.
- Unverified body figure, null control. The body says the merge base with this branch's `tests/card.mjs` fails 40 checks. At this head's `tests/card.mjs` against 043b111d0 I count 47 (ev/nullcontrol_base_card.txt):
  - 39 UX-HEALTH checks, all of them red;
  - 4 carry-8 null-read checks;
  - "a missing power meter is recommended with an Assign action; insight sensors have a Show action";
  - the census's act-set, press-set and link checks.

  The card JS, strings and translations are identical between the body's base e5ddba1fa and 043b111d0. The 40 was therefore taken against an earlier `tests/card.mjs` than the head's, and I could not re-derive it. The direction holds: every new arm is red at the base, and the two must-hold controls ("a watched COP still reads Normal", "a metered install's learned heat loss still says learned") pass there. Carry: dismissed: a stale count whose conclusion stands at this head; no gate reads it.
- Carry 17 (the P9 grid's `localStorage` reset). The design gives this to this group; it is measured (30 digit-on-digit pairs in `wood_alert`/`wood_lane` at 375 px) and not landed. The body raises it as a new after-edge, because the ink is outside the Health renderer. That follows arm C's own rule for a cause outside the seam. Carry: R10-UX-HEALTH
- Carry 14's "driving scale". The design marks it `decision: orchestrator`, so nothing is built. Carry: R10-UX-HEALTH
- Stale docs: `docs/dashboard-card.md` "The health page" and `docs/img/card/health-light.png` / `health-dark.png` still describe the old page. Both are outside this group's `files`. Carry: R10-ARCH-DOCS
- COP-GATE part 2 has not merged at this base. `copState` step 2 cannot fire in production until `cop_observability`, `cop_refusal` and `measured_cop_at` reach `ModelStatusSensor.cop`. Carry: R10-COP-GATE
- No instrument landed: the fixer's mutant runner is a scratch `mutants.py` that was never committed, and so are mine (ev/mutants.py, ev/nullarm.sh). Each fixer mutant is quoted in the body as one edit, so they reproduce by hand. Carry: dismissed: one-off source edits; no reusable instrument, and decision 0013 lands only reusable ones.

## Evidence

- RESULT head 1381df1f5: `node tests/card.mjs` ALL CARD CHECKS PASSED (rc=0); `python3 tests/entities.py` ALL 2480 ENTITY CHECKS PASSED; `python3 tests/features.py` ALL 4577 FEATURE CHECKS PASSED; `HPO_BROWSER_SCOPE=auto node tests/card_browser.mjs` ALL BROWSER CHECKS PASSED. P9 ran in SCOPED RUN mode: 324 cells, every P9 check ok, UX-HEALTH B and C ok in light and dark at 375 and 1280. `python3 tests/structure.py` STRUCTURE RATCHET PASSED.
- RESULT figures re-derived at the head; each equals the body:
  - archscore dS +0.0403 IMPROVES (`card_clone_copies` 108 -> 105);
  - card_drift: 2 states moved and claimed (health_page, score_open), 43 identical;
  - `env_drift.py --claims-only origin/main`: claims hygiene ok;
  - closure select: `MODE: SCOPED -- 12 script(s) run, 21 scoped out`;
  - sibling greps, base/head: raw-key 1/0, `Number(attrs.` 4/0, COP renderers 20/17, `navigateTo(SETTINGS_PATH)` 1/0;
  - COP-code grep: 13 in accuracy.py, 4 in heat_energy.py;
  - `health.input_*` table: 11 -> 44 keys per language (22 -> 88 lines, en+sv).
- RESULT browser null control at the base (043b111d0 with the head's test files): 6 fail, exactly the body's six: four "UX-HEALTH C: nor after a switch back from a scrolled page" and two "UX-HEALTH B: the input grid spans the page".
- RESULT mutation proofs. These are my own 19 mutants, one production edit each in a fresh worktree, run under `node tests/card.mjs`:
  - 18 of 19 are red: M01 copState step 2, M02 debug read level, M03 another entry's key, M04 confirm, M05 diagnostics fallback, M06 settling day figure, M07 unobservable clause, M08 raw-key label, M09 valve `readNumber`, M10 hover envelope-only, M11 raw unknown code, M12 off renders a row, M14 measured-age, M15 counting without ETA, M16 static learning row, M17 unwatched Normal (5 red), M18 Show to the options page, M19 second Start not starting.
  - M13 (drop `scoreDrivers`' no-drivers guard for non-envelope parts) passes card.mjs but `tests/card_drift.mjs` reads `DRIFT score_open (unclaimed)`: "Typical..." appears under parts that published no drivers. It is killed by a gate script in the same closure (ev/M13_card_drift.txt).
  - Browser mutants: C1 (`saveScroll` reverted) turns all four "C: nor after a switch back" checks red; B1 (`HEALTH_CSS` grid removed) turns both "B: input grid spans the page" checks red. My mutants overlap the fixer's table and extend it with M03, M11, M12, M13, M14, M15, M17, M18, M19, C1 and B1. Every quoted fixer mutant whose edit I reproduced came out red.
- Design trace, arm by arm, against e6797ca9d:
  - A (44 labels per language, per-language marker strip, owning page wins, sv `quick_setup` pair rewritten, raw fallback gone, backend arm): implemented. The backend arm's form differs; see Findings.
  - B (plan and learning above, `repeat(auto-fill, minmax(18em, 1fr))` grid): implemented as designed, page-scoped like `RECEIPT_CSS`.
  - C: measured first in `tests/card_browser.mjs`, then fixed at the design's named alternative site, the dialog's scroll restore.
  - D (`learner_progress` phases; settling without a day figure; off has no row; `scoreReasonText(reasons.overall)`; one `inputAssigned`): implemented. The predicate stays at "no power meter": the design's carry allowed widening only after the demand-overbook harness confirmed it, and that harness has no heat-meter arm.
  - E (one `copState`, precedence alarm > not_measurable/no_electric_meter > watched > reason, `measured_cop_at` age, deleted strings, a string per code): implemented.
  - F (`scoreDrivers`, `health.metric_*` titles, every part in the hover): implemented.
  - G (`show_entities` -> `haLink("entities")`; `fetchWithAuth` download through `navigateTo`'s download mode; fallback to `haLink("options")`; `configEntryId` factored out; settings act and PENDING rows deleted, PENDING now `{}`): implemented.
  - H (`res.response.debug[entryId]`, active/final/off, confirm before discard; `health+debug_final` and `health+debug_off` in FIXTURES; `show_entities`, `diagnostics`, `debug_start` in ACTS): implemented. The refresh cadence differs; see Findings.
  - No backend file changed.
- Class: the design's sibling-site commands are the enumeration rule. Each returns 0 or only the intended remainder at the head (figures above), so no class is left open.
- `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched three-dot.
- Merge: `git merge-tree --write-tree origin/main 1381df1f5` exits 0 (tree 3b77a00e7), so there is no conflict and no claim-file driver call.
- CI on the head (check-runs API, every run concluded): all success or skipped except `tests / nightly-status` (failure). That check reads only the last concluded scheduled run of nightly.yml. This diff touches no workflow and nothing that lane reads, so the red is main's, not this pull request's (defect-root-cause.md). `pr-contract / pr-contract` started at 01:38:13Z, after nightly-status concluded at 00:57:57Z, and is success; `gate` is success. The rendered packet's `red-unanswered` refusal names only that nightly-status check.
- Toolchain: the session-start hook exported venv-ci; `PYTHONPATH=tests/hastub` and `HPO_PLANDATA` were set explicitly for the mutant worktrees. The inline-read budget hook paused this seat twice. I delegated two read-only locate tasks to cheap scouts and re-checked their results against the code myself.
