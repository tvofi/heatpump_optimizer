R10-FRICTION-REGRESSION: the root-cause record for the recurring-friction key `regression` (#2860). The record is `dev/audit/rca/R10-RCA-FRICTION-REGRESSION.md`, registered in `bugclasses.json`'s `_rca`. It lands one sentence in `fixer.md` step 5 and no production code.

Disposes #2860. `prepr.sh`'s preflight refuses a closing keyword for #2860, because #2860 is not on the group's intended (`fixes`) list at this roster. For #2860 to close on merge, the orchestrator must move it into R10-FRICTION-REGRESSION's `fixes`.

## Root cause

- **Count.** 3 PRs / 3 entries in `v7.0.4..origin/main` at `507a9ec26` (`policy_lint.mjs --stats --since v7.0.4`, 319 merged PRs). The three PRs are #2698, #2825 and #2841, found by an independent rescan of every window PR's `Fix review:` comments. Time from each block to the next verdict: 728, 96 and 153 min (upper bound).
- **No single cause.** `regression` is an untaught word that names an outcome, not a mechanism. Each of the three blocks has its own mechanism:
  - **#2841, state (c).** `fixer.md` step 5's "leaving the rest to CI" was followed: the scope was `MODE: SCOPED -- 24 script(s) run`. `card_browser.mjs` is `NOT_A_TEST`, so no scope ever selects it. Its first run is CI's, after the handoff, so its red always costs a review round.
  - **#2698, state (b), inside the `class-open` residue's standing refusal.** The body's "Clamp means reset, consistently" was an "every" claim. It was measured on the ratio's clamp branch only, and the scale's mirror branch was open at `3383fb2a`.
  - **#2825, no process failure.** A revision's arm drove a pid kill, and a group kill escaped. The fix review is the designed detector and caught it in one 96-min round.
- **Cost test.** Countermeasure: "**No scope selects `card_browser.mjs`**, which CI runs past the handoff: run it on a `GRID_SURFACE` diff". Standing cost: 268 s per card-surface diff × 7 card PRs in the window = 31 min, or 63 min with every PR run twice. Benefit: 153 min (1 red-lane block in 7 card PRs). **Built.** The basis is one instance in one window, and the record says so.
- **Refused.** A `closure.py select` browser line: it duplicates `GRID_SURFACE` into Python, puts a `MODE: FULL` gate file in the diff, and reaches the same single instance. A CI hold until `tests / browser` concludes: the red still arrives after the handoff, so it saves no round.
- **Policy approval.** `fixer.md` is policy. The edit is approved under the orchestrator's mandate (scope `all`), as the brief states.

## Approval

`dev/governance/roles/fixer.md` (budgeted as `tools/audit/briefs/fixer.md`) is a policy file. Editing it is the countermeasure this root-cause seat was dispatched to land. The dispatch brief approves it under the orchestrator's mandate in force (scope `all`): "A countermeasure that edits a policy file is approved under the orchestrator's mandate (scope all); no step waits on tvofi." The edit changes what a fixer seat must do: a diff on `card_browser.mjs`'s `GRID_SURFACE` now runs that lane locally before the handoff. It addresses process state (c). No budget file moves, so `budget-raise-gate` does not apply.

## Head

`91d0fde2d` (this branch), on merge base `507a9ec264eb373b132248d752259254d8a9fa4d`, which was also `origin/main` when measured on 2026-10-30.

## Mutation proof

n/a: no check and no production line. The countermeasure is an instruction. Its demonstration is the run it instructs (record section 7), which is red on the defect and green at the defect's other two ends:

- `2cfb8b96` (#2841's blocked head): rc=1, `2 BROWSER CHECK(S) FAILED`. The two `FAIL` lines are `P9 grid: every cell mounted and every driver step found its target` and `P9 grid: no pop-up leaves the viewport or its chart`, the two the review named.
- `5261ba84` (merge base): rc=0, `ALL BROWSER CHECKS PASSED`.
- `59c744f4c` (the repair): rc=0, `ALL BROWSER CHECKS PASSED`.

## Null control

- At `2cfb8b96`, `python3 tests/closure.py select --diff 5261ba84` prints `MODE: SCOPED -- 24 script(s) run, 9 scoped out`, and `scope.run` holds no `card_browser.mjs`. The unmodified step 5 therefore never runs the lane. With no defect present, the same lane run reads green at the base and at the repair (above).
- The budget edit: `policy_lint.mjs --budgets` puts the row `tools/audit/briefs/fixer.md` at 5216 / 5216 tokens and 314 / 315 lines at this head. The cap is unchanged.

## Figures

- `node tools/policy/policy_lint.mjs --stats --since v7.0.4` → `319 merged pull request(s)`, `3 / 3     regression   <- at or over threshold` (`dev/audit/rca/regression/stats_v7.0.4.txt`).
- `gh api repos/tvofi/heatpump_optimizer/issues/<pr>/comments --paginate` over the 319 window PRs, keeping first lines matching `^Fix review:.*\bregression\b` → #2698, #2825, #2841. Block-to-next-verdict minutes are `created_at` differences: 728, 96 and 153 (`dev/audit/rca/regression/items.tsv`).
- `git log --first-parent --format=%h v7.0.4..507a9ec26 -- custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js | wc -l` → 7.
- `NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs`, after `PYTHONPATH=tests/hastub python3 tests/plan_view.py`, in a detached worktree at each SHA → rc 1 / 0 / 0 in 268 / 249 / 272 s (head / base / repair).
- `gh api repos/tvofi/heatpump_optimizer/check-runs/121335806091` → `tests / browser`, `failure`, completed 2026-10-26T00:28:19Z. PR #2841 was created 2026-10-25T23:57:28Z (`gh api repos/tvofi/heatpump_optimizer/pulls/2841 --jq .created_at`).
- `node tools/policy/policy_lint.mjs --budgets` → `tools/audit/briefs/fixer.md 314 315 5216 5216`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` at this head → `MODE: SCOPED -- 1 script(s) run, 32 scoped out` (`tests/entities.py`).
- `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` → rc=0, `ALL 2484 ENTITY CHECKS PASSED`, `5 TEST SCRIPT(S) PASSED; 30 SCOPED OUT AND NOT RUN`.
- `node tools/policy/policy_lint.mjs` → `TOTAL: 0 error(s) across 50 policy file(s)`.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/fold_ledger.py check` → `131 rca entries`, `0 violation(s)`.

## Red checks

none

## Forward-carry

- The browser-lane finding changes how every later fixer works. It lands in that stage's own contract: `dev/governance/roles/fixer.md` step 5, in this diff. Carry: dismissed: landed in this pull request's own contract edit

## Roster carries

The dispatch brief (`PROMPT.md` on `dispatch/fixer-r10-friction-regression`) scopes this seat to #2860 alone. It omits the group's three roster carries. This seat therefore landed none of them. Each is named here and returned to the orchestrator.

- **Carry 1** (P259: absorb #2840, #2835, #2895 and #2907, five records, one `Closes` line each, merge on tvofi's review): **not done here.** This PR lands the #2860 record only. Records for the other four keys are already present at the base by name: `R10-RCA-MUTATION-SURVIVOR.md`, `R10-FRICTION-GATE-SCOPING.md`, `R10-RCA-FIXER-MD-KEY.md` and `R10-RCA-FRICTION-CLAIM-FALSE.md` (#2956). Their sufficiency was not judged here. The carry's "merges only on tvofi's approving review" contradicts the brief's "no step waits on tvofi". The orchestrator decides which binds. The group's `fixes` is `[]`, so no `Closes` line passes `prepr.sh`'s preflight. Carry: dismissed: outside this dispatch brief, returned to the orchestrator
- **Carry 2** (#2875 `root-cause-detectable` and #2950 `class-open`): **not done here.** Neither key is in this seat's brief. Carry: dismissed: outside this dispatch brief, returned to the orchestrator
- **Carry 3** (land R10-RCA-FRICTION-RESIDUE's approved tooling countermeasures for #2436, #2437 and #2429): **not done here.** These are policy-tooling changes to `policy_lint.mjs` and `ci-autofix.md`, with demonstrations of their own, and none is in this seat's brief. This record reuses none of them (record section 4). Carry: dismissed: outside this dispatch brief, returned to the orchestrator

## Friction

fixer.md: stale: the dispatch brief for R10-FRICTION-REGRESSION omits its three roster carries, the omission #2841's body reported for R10-CARD-VOICE; review_packet's brief-carries refusal surfaced them at the handoff. Carry: dismissed: a dispatch-rendering note for the orchestrator, carried in this body
