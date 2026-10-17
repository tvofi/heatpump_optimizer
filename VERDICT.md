Fix review: blocked 400df157aae0281b8c7d91de16a8fb02ff37c0c9 head-moved: measured 400df157, head is f97973cc760b126f4fc5507f2f9e24034f757c34

bus-nonce: 15ae054fe480b82ff6e94f77e91bfa61

Round 2. Measured head 400df157aae0281b8c7d91de16a8fb02ff37c0c9 from a detached
worktree at /private/tmp/rev-2346-r2/wt; evidence under
/private/tmp/rev-2346-r2/evidence. The live head is now
f97973cc760b126f4fc5507f2f9e24034f757c34, a single github-actions[bot] commit
`ci: re-record closures` (2026-10-17T14:49:35Z) on top of the head I measured.
Per fix-review.md step 12 that is head-moved. Every number below survives (taken
at 400df157 and re-read there); none re-taken at f97973c: the delta is
tests/closures.json only (it adds translations/en.json, which the new card.mjs
check reads, to a closure, and re-records two `seconds`).

## Round-2 claims, re-derived (all five hold)

- The two sites are deduped: `finiteNum(nowTemp)` at
  heatpump-optimizer-card.js:7071 and `finiteNum(refit.scale)` at :8684
  (`git show 5295fa06a`). The only `typeof … Number.isFinite` spelling in the
  card is the owner `const finiteNum` at :9156; a broader grep for
  `typeof`+`isFinite` and single-quoted `'number'` returns nothing else.
- Finder's enumerator card_shapes.mjs (sha1 677b7542…, as the body names it),
  run by me at three ends: origin/main 81b7aa9ff finite_inline=7 total=31;
  round-1 head 82daaab4 finite_inline=3 total=24; head 400df157
  finite_inline=1 total=22 (evidence/findings/shapes-*.log). The in-tree
  v2_card_lines.mjs: isfinite_lines 7 / 3 / 1, total 34 / 27 / 25. The body's
  `finite_inline=1`, `isfinite_lines=1` and `total=25` hold.
- Mutation proof, my own runner (mutants-mine.py, not the fixer's script;
  evidence/mutants-mine.log, mutants-mine.json), 11 runs of `node tests/card.mjs`
  with this worktree's own plan payload: M0 passes (ALL CARD CHECKS PASSED);
  M1 4 FAIL, M2 11, M3 1, M4 1, M5 1, M6 1, M7 1, M8 1, and M9/M10 (the two
  round-2 sites re-spelled inline) each 1 — `the finite-number test is spelled
  in exactly one place`. M0-M8 unchanged from the fixer's table.
- Step 14, in its own worktree (evidence/step14.log): with the widened regex
  reverted to round-1's `/typeof n === …/` and both sites re-spelled inline
  (M9+M10), the check PASSES and the tree reports ALL CARD CHECKS PASSED
  (rc=0) — removing the widened mechanism returns the missed class, so the
  widening is load-bearing, not cosmetic. With the widened regex in place the
  same two re-spellings FAIL it. The old regex still kills M7, so it is not
  vacuous. card_shapes on the re-spelled card is finite_inline=3 total=24, so
  the 3→1 movement is earned by the dedupe, not by the instrument.
- The `d408fa76a` fallback is now pinned in its truthy branch by `the Configure
  chip names the options page the flow itself names`, which reads STRINGS.en,
  SETUP_CONFIGURE_PAGE and translations/en.json and requires the map's labels
  to equal the flow's; its falsy branch stays unreachable from any drawn
  topology. The body's disposition matches the code.

## Claim files, versions, scope

- tests/golden/card_claimed_drift.txt, tests/golden/claimed_drift.txt and
  tests/golden/config_flow.json are byte-identical to round-1 head 82daaab4;
  `claims-for:` is VERSION 7.0.0. VERSION, the manifest version and the
  RELEASE_NOTES heading move nothing against origin/main.
- `node tests/card_drift.mjs origin/main` -> `39 state(s) moved and claimed, 1
  identical` (evidence/card_drift.log).
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all origin/main` ->
  `NO UNCLAIMED DRIFT: 56` and `NO STALE FIXTURE: 56` (evidence/env_drift.log).
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED` (evidence/
  structure.log). `tests/closure.py select` -> `MODE: SCOPED -- 16 script(s)
  run, 17 scoped out`; scope.run has 16 lines.
- wizard_widgets.py (sha1 66b39055…), both ends: menu_disagree 1 -> 0,
  menu_fallbacks 23 both, golden_equal=1 both; `--bump heat_pump_cop_nominal`
  moves disagree 0 -> 2 at both ends (evidence/findings/wizard-*.log).
- `git merge-tree --write-tree origin/main HEAD` -> rc 0, no conflict.
- Forward-carry destination open and carrying it: wave-r10-groups.json group 13
  (`R10-ARCHSCORE-COVERAGE`), the precondition that its card rows be recorded
  at a base carrying these C1/C4 folds.

## What blocks now

1. **Head moved.** Measured 400df157, live head f97973c. The PR body's `## Head`
   names 400df15 and CI's lint accepts the autofix commit on top, but a merge
   verdict cannot name a head that is not live and the delta file is in the
   branch's own diff, so app_approve.sh --carry would refuse it. Re-dispatch at
   f97973c; the delta is the bot's own re-record and nothing I measured moves.
2. **A red check is unanswered at the live head** (this is not the first-line
   class only because its wait condition is not met yet). `pr-contract` is red
   at f97973c (run 39042398374, 2026-10-17T14:49:42Z):
   `check closures is red and ## Red checks does not name it.` The `closures`
   check is red at 400df157 — the UNDER-SCOPED run whose repair the bot then
   made — and the body's `## Red checks` names only the local P9 grid and the
   local env_drift run. Per fix-review.md step 11 the body must name `closures`
   and answer it; for `UNDER-SCOPED` writing down the autofix chain is the
   answer (ci-autofix.md). The `pr-contract` red is that omission's
   consequence and is answered by the same edit. I did not post
   `root-cause-unanswered`: the head's `closures` runs are still in progress
   and no `pr-contract` run has started after them.

## Instrument note (not a block; step 14)

The widened census keeps round-1's exclusion `^\s*(const finiteNum|\*|\/\/)`,
which is a prefix match, not the owner line. A second owner
`const finiteNum2 = (x) => typeof x === "number" && Number.isFinite(x);` leaves
`node tests/card.mjs` at ALL CARD CHECKS PASSED ("ok the finite-number test is
spelled in exactly one place") while card_shapes reports finite_inline=2
(evidence/second-owner.log). The inline re-spellings the round-1 block named
(M9/M10) are closed; this is a narrower duplicate-owner gap in the check, not
that class, and it is not present in the tree. Anchoring the exclusion to
`const finiteNum = ` closes it. This is an instrument finding under a sound
change, recorded for the seat that owns the card censuses
(R10-ARCHSCORE-COVERAGE's card coverage); I do not block on it.

## Figures (5 sentences, each with its command)

- `node tests/card.mjs` at 400df157 -> `ALL CARD CHECKS PASSED` (M0).
- card_shapes.mjs 677b7542… on the three cards -> the base/head counts above.
- `node dev/audit/rounds/round10/catchup/arch-b/v2_card_lines.mjs <card>` ->
  isfinite_lines 7 / 3 / 1 at base / round-1 / head.
- `node tests/card_drift.mjs origin/main` -> 39 moved and claimed, 1 identical.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all origin/main` ->
  56 checked, 56 still matching.

RESULT round-2 claims 5/5 re-derived (dedupe, widened census, finite_inline=1, M9/M10 kill, fallback note)
RESULT card_shapes base 81b7aa9ff finite_inline=7 total=31; r1 82daaab4 3/24; head 400df157 1/22
RESULT v2_card_lines base isfinite_lines=7 total=34; r1 3/27; head 1/25
RESULT mutation M0 null: 0 FAIL (ALL PASSED); M1 4, M2 11, M3 1, M4 1, M5 1, M6 1, M7 1, M8 1, M9 1, M10 1 FAIL — each mutant killed
RESULT step14 widened-regex + M9+M10: FAIL; old regex + M9+M10: PASS (class returns); old regex + M7: FAIL (control)
RESULT card_shapes on the re-spelled card: finite_inline=3 total=24 (3->1 is earned by the dedupe)
RESULT card_drift 39 state(s) moved and claimed, 1 identical
RESULT env_drift NO UNCLAIMED DRIFT (56), NO STALE FIXTURE (56)
RESULT structure STRUCTURE RATCHET PASSED
RESULT scope MODE: SCOPED -- 16 script(s) run, 17 scoped out
RESULT wizard base menu_disagree=1 -> head 0; menu_fallbacks=23 both; golden_equal=1 both; perturbation disagree 0->2 both
RESULT claims byte-identical to r1 head; claims-for 7.0.0; VERSION/manifest/notes untouched
RESULT head-moved measured 400df157, head f97973c (bot ci: re-record closures; delta tests/closures.json only)
RESULT root-cause closures went red at 400df157 (UNDER-SCOPED) and ## Red checks does not name it; pr-contract red at f97973c (run 39042398374) for that omission
RESULT instrument-note second owner finiteNum2: card.mjs ALL PASSED while card_shapes finite_inline=2
