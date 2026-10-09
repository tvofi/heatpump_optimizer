Fix review: merge 9b39bb7c68ff6a0cf5914c27c7cb93293400a9f3

bus-nonce: 5acf1e2dce6f553b0765e1f333f03868
seat: review-2065-r5, round 5 (resolution delta only)
measured at: `9b39bb7c68ff6a0cf5914c27c7cb93293400a9f3` — my detached worktree
`/Users/timmalmstrom/hpo-seats/review-2065-r5/wt5`. The PR carried `debe97613` when
I opened; I waited for the fixer's push, and `gh pr view 2065 --json headRefOid` names
`9b39bb7c6` both before I measured and now as I post (step 12). `mergeStateStatus:
CLEAN`, `merge-tree origin/main HEAD` exits 0 (only `LEDGER-MERGE: resolved
tests/closures.json`, no conflict path). Body `## Head` names `9b39bb7c6` (step 7).
Contract current: `git diff $(git merge-base origin/main HEAD)...origin/main --
dev/governance/roles/` empty (read before this review). CI settled at this head, all
17 required contexts green.
Evidence: /Users/timmalmstrom/hpo-seats/review-2065-r5/evidence/ (head.txt,
claims_head.txt, rederive_merged.txt, fourtree.txt, mergetree_markers.txt,
both_touched.txt, rederive_summary.txt)
Instruments I re-ran (step 2/8, all the finder's/committed ones — I wrote no production
harness): claims.py (D6), entities.py's `_d308_pairs` over the merged closures.json,
closure.py selftest, structure.py, the four mutation_table source-only validators,
ci_predict.py, unpinned_sites, and `git merge-tree`.

This is the round-4 `merge` carrying (decision 0013 / step 12) over the resolution merge
of main `d8a4bd36f` (#2024 flow_meter, #2059). I judged ONLY the delta: three content
conflicts resolved and a false agreement caught. I did not re-review the branch's own code.

## Re-derived vs claimed — every figure reproduced

RESULT arch_modules_on_disk=75     claimed 75  MERGED TREE TRUE (75 .py on disk)
RESULT arch_map_listed=75          claimed 75  TRUE (C33 missing=0 phantom=0)
RESULT arch_map_missing=0          claimed 0   TRUE
RESULT ha_module_level_importers=27 claimed 27  TRUE (C34 documented=27 measured=27)
RESULT config_defaults_compared=89 claimed 89  TRUE
RESULT config_ranges_compared=91   claimed 91  TRUE
RESULT claims_extracted/true/false/stale/unverifiable = 125/123/0/0/2  claimed same  TRUE
  - the committed claims.json/claims.md byte-equal this run (git status clean after the
    run); the claims.py docstring header RESULT assertion lines match the run exactly, so
    harness_headers.py's executing assertion will pass. NOT stale against its instrument.
  - C32 reads `(\d+) modules, of which` = 75; architecture.md's "other 47 modules" =
    75-27-1 = 47, arithmetic correct; draw_range/flow_meter/entry_config all present on
    disk and in the module map.

RESULT deployment_shape prod_files=93  claimed 93  MERGED closures.json + on-disk both 93
RESULT deployment_shape pairs>=0.80=123 claimed 123  TRUE (528 total = 33 choose 2)
RESULT deployment_shape comparable=406  claimed 406  TRUE
RESULT deployment_shape at_1.00=18     claimed "Eighteen"  TRUE
  - every per-pair shared count in the prose reproduced: arch_score_head/deployment_shape
    93, golden/env_drift 91, {doc_claims,entities,harness_headers} pairwise 83,
    {finite_boundary,structure,typing_ruler} pairwise 75, card.mjs/card_drift 58,
    {boost_drift_replay,plan_view,solar_alignment} pairwise 57,
    optimality/validate/edge/backtest six pairs 21.
  - four-tree control re-derived: base 91/120/18, branch-head 92/120/18, main 92/120/18,
    merged 93/123/18. The merged 123 exceeds a union of the two 120s, and 93 = 92+1, so
    these were MEASURED, not unioned. (NOTE for routing: the dispatch shorthand's third
    column "20/21" is not the at-1.00 figure — measurement gives 18 at all four trees,
    which is what the head prose states; the authoritative targets 93/123/406/18 all match.)

## features.py union (item 4)
Top-level names: branch adds 52 (`_dr*/_DR*/_Dr*`), main adds 25 (`_fm*/_fb*/_Fm*/_Fb*/
_FB_KEYS`); COLLISION = NONE (prefixes disjoint, no shared name or import alias); merged
superset of the union = YES, merged-only extras = NONE. Check-count delta: branch +41,
main +19, merged +60 = 41+19 exactly — both sides' checks present, none dropped, none
double-counted. Whole-file run is CI's: `fast (3.14)` **success** at this head; I did not
reproduce the macOS Accelerate arm (R9-F2.1 P3, the disclosed `1 of 3930` that also fails
at main) — CI's canonical Linux run is the authority (heavy lanes are CI's).

## Nothing reverted by the merge (item 5)
Evil-merge set = exactly the 9 both-touched files. `closure.py selftest` -> ALL 57 closure
shrink pins PASSED. Committed closures.json blob 8756c5b7 == `git merge-tree(debe97613,
d8a4bd36f)` driver output 8756c5b7 (stderr `LEDGER-MERGE: resolved`); it came from main's
driver, not a hand union. merge-tree conflict set = claims.py, deployment_shape.py,
features.py (three); coordinator.py/thermal_model.py/architecture.md auto-merged clean.
Branch-added-line survival (base->head vs merged): coordinator.py 38/0 lost,
thermal_model.py 8/0, closures.json 28/0, features.py 369/0. The census files' only lost
branch lines are the OLD wrong numbers (74->75, 92->93, 82->83, 46->47), each replaced by
the re-derived value confirmed true above; every descriptive contribution survives
(draw_range attribution in claims.py/deployment_shape, the module-map entry in
architecture.md). 49 head-only files match the branch head (0 reverts); 51 main-only files
match main (0 drops). Correct union.

## Budget / structure / ledger (item 6)
structure.py -> STRUCTURE RATCHET PASSED; max_class_loc 8818<=8818, seam_cut_total
762<=762, coordinator_attrs 153<=153 (at cap, zero headroom, none raised). Both budget
files byte-identical to main. Source-only validators (load_budgets + inventory, 5943 sites):
triage_problems / ledger_form_problems / layout_problems / cap_problems /
completeness_problems ALL CLEAN.

## Unpinned (item 7)
`ci_predict.py --base d8a4bd36f` -> "no closures or fast red predicted" (no ADDED
UNPINNED line). `unpinned_sites`: 4620 of 5943 (matches the pin-lane inventory claim);
**0 unpinned on draw_range.py** — every draw_range site is disposed in the ledger.

## Files / claims identity (item 8)
VERSION, RELEASE_NOTES.md, hacs.json, package manifest.json, and BOTH claim files byte-
identical to main. `mergeStateStatus: CLEAN`. All 17 required contexts present (none
ABSENT) and green at the head; nightly-ha/nightly-status skipped/success; all autofix jobs
skipped (nothing owed to the bot). No check went red in the range 90b9e87f7..9b39bb7c6, so
there is no unanswered `## Red checks` for this delta (step 11 trigger not fired).

## Friction — assessed plainly (for routing, not a block)
The `## Friction` claim that "the merge-main bot could union two identically-wrong census
numbers and ship a false pair silently" is NOT true of the bot as landed.
`tools/pr/merge_main_bot.py` pushes a resolution ONLY when every conflicting path is a
`.gitattributes` driver file (claimed_drift.txt, card_claimed_drift.txt,
mutation_budgets.json, structure_budgets.json, closures.json, bugclasses.json) that its
driver resolves. Census figures live in claims.py / architecture.md / deployment_shape.py —
none is driver-routed — so any conflict on them is `skip-other-conflict` and the bot
refuses to push. A clean false-agreement merge (both sides identically wrong, e.g.
architecture.md's naive merge-tree line 8 = "74") is NOT a conflict, so the bot never fires
on it; that hazard is plain git three-way merge, present with or without the bot. The bot
neither can nor does union two census numbers.
The hazard the fixer is really pointing at is broader and pre-existing: a clean merge of two
identical-but-wrong figures ships silently, and it is caught only where an instrument reads
the prose. claims.py's arch counts are such an assertion (harness_headers.py executes the
header every PR, REGISTER_DIRS includes D6), and entities.py pins deployment_shape.py's
THREE headline numbers to the closures derivation — so a wrong number in those goes red in
CI. The genuinely uninstrumented figures are deployment_shape.py's at-1.00 COUNT and each
per-pair shared-file count (entities checks only the three headline numbers): a wrong one
would ship with no test. That is an instrument-scope gap in the D6 / deployment_shape note,
NOT a property of R9-CI-2b / the merge-main bot. Do not file it against the bot; if filed,
it belongs to the census-lane brief.
