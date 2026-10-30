Fix review: merge 9cb4919101475766b2c92ec38e51a2d1c0a8a867

bus-nonce: 4d40e7da4ba5a70c6f1d3984549f3552

## Round

Round 1: the first review of this head, measured from a detached checkout at 9cb4919101475766b2c92ec38e51a2d1c0a8a867. The merge base is d99cadb1235a5e40e250466e656c41c7ce88e641, which is origin/main now. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the role files are current. Before writing, `git ls-remote` gave 9cb4919101475766b2c92ec38e51a2d1c0a8a867 for both refs/pull/3000/head and fix/r10-friction-regression. The diff holds no production code. It adds one root-cause record with its evidence, one bugclasses `_rca` entry, the delivery row, and a two-sentence edit to `fixer.md` steps 5 and 13.

## Findings

- `dev/audit/rca/regression/stats_v7.0.4.txt` is not a clean capture of `policy_lint.mjs --stats`. Its first 29 lines are a directory listing of `dev/audit/rca/{claim-false,harness-friction,headmoved}` plus three unrelated `git log` lines (5f3a5dd61, 15abe48e5, 8db235793). It ends with a transcript marker, `[exited with code 0]`. It also lacks the `INFO [stats]` lines that the 218-PR snapshot `harness-friction/stats_v7.0.4.txt` carries (that file's line 236 is the `would open ... regression` line). So the "would open" absence that record section 1 calls unestablished is plausibly an artefact of the capture, not of the tool. The two figures the record cites from it (319 merged PRs; `3 / 3 regression`) are present. Severity: minor. Carry: dismissed: evidence hygiene only; no count the record draws from the file is affected, and section 1 already declines to rely on the missing line
- The block-to-next-verdict figure for #2698 is 728 min, but its own items.tsv timestamps (13:32:03Z to 01:40:57Z) give 728.9 min. The other two rows are rounded (#2825 95.6 → 96, #2841 152.7 → 153), so this row should read 729 and the sum 978. Severity: minor. Carry: dismissed: a one-minute rounding slip that leaves the median (153) and the cost test (31/63 min < 153 min) unchanged
- `dev/governance/roles/fixer.md` is policy and code-owned. The body records its approval under the orchestrator's mandate (scope `all`). CLAUDE.md requires the owner's approving review through `main-protect-checks`'s code-owner rule, and tvofi is the requested reviewer. Whether the mandate settles that is not this review's to decide. Carry: dismissed: enforced at merge by main-protect-checks' code-owner rule, and the merge train holds it there

## Evidence

- **Mutation proof (step 1).** The body says n/a: no check and no production line. Confirmed. My mutant deleted the new step-5 sentence ("**No scope selects `card_browser.mjs`** ... #2841)"). `policy_lint.mjs` still read `TOTAL: 0 error(s) across 50 policy file(s)` and `rules_sync.mjs --check` read ok (ev/mutant_sentence.txt), so no check pins the sentence. That is expected for an instruction-shaped countermeasure. The tree was restored and verified clean.
- **The countermeasure's demonstration, re-run by me** (record section 7; ev/browser-*.log). In detached worktrees I ran `PYTHONPATH=tests/hastub python3 tests/plan_view.py`, then `NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs`:
  - RESULT browser 2cfb8b96 rc=1 s=307, `2 BROWSER CHECK(S) FAILED`: `FAIL P9 grid: every cell mounted and every driver step found its target` and `FAIL P9 grid: no pop-up leaves the viewport or its chart`. These are the two failures the #2841 review named.
  - RESULT browser 5261ba84 rc=0 s=267, `ALL BROWSER CHECKS PASSED`.
  - My wall-clock times (307 / 267 s) differ from the body's (268 / 249 s), which is machine variance. The cost test stands either way: 7 × 307 s = 36 min < 153 min.
  - I did not re-run the repair 59c744f4c. The #2841 round-2 and round-3 verdicts record it green at 11e8075d and c32202c9.
- **Null control.** The body says no scope selects the lane. Confirmed in the tree at this head:
  - `tests/closure.py:116-118` excludes card_browser.mjs ("It runs in its own job").
  - `tests/run.sh:448` reads `card_browser.mjs) continue ;;`.
  - `tests.yml:472-487` gates the browser job on closure-scope, not on GATE_SCOPE.
  - `GRID_SURFACE` sits at `tests/card_browser.mjs:1063`.
  - `web-fragments.md:68-70` carries the recipe.
  - `VERDICT_CLASSES` sits at `web-fix-wave.js:175`.
  - `tests/README.md:442-445` and `tests.yml:1270-1276` (nightly-ha) are as cited.
- **Mechanisms re-derived at the blocked heads.**
  - #2698 at 3383fb2ac: in `_reanchor_house_heat_loss_scale`, the `if not HOUSE_HEAT_LOSS_SCALE_MIN <= new_scale <= HOUSE_HEAT_LOSS_SCALE_MAX` branch resets new_scale and the house samples. The function then still calls `self._apply_lower_floor_loss_ratio(new_ratio)` with the jointly solved ratio.
  - #2825: `pr_args.sh:249` at ab80907a reads `dog = os.fork()`, and its line 1123 is the pid-kill arm. Line 1178 at 3e936f0c is the group-kill arm. All as the record states.
- **Figures I re-derived.**
  - `git log --first-parent --format=%h v7.0.4..507a9ec26 -- …/heatpump-optimizer-card.js | wc -l` gives 7, and the same range without the path gives 332 commits.
  - `policy_lint.mjs --budgets` puts `tools/audit/briefs/fixer.md` at 314 / 315 lines and 5216 / 5216 tokens, at both this head and the base. The cap did not move, and no budget file is in the diff.
  - `closure.py select --diff <mb>` gives `MODE: SCOPED -- 1 script(s) run, 32 scoped out`.
  - `PYTHONPATH=tests/hastub python3 tests/entities.py` gives `ALL 2488 ENTITY CHECKS PASSED`. I ran the script alone, and the body's 2484 came through `run.sh`, so I did not re-derive that figure.
  - `policy_lint.mjs` gives `TOTAL: 0 error(s)`, `structure.py` gives `STRUCTURE RATCHET PASSED`, and `fold_ledger.py check` gives `131 rca entries` and `0 violation(s)`.
  - The window controls are as stated: stats_v7.0.0 shows `1 / 1 regression`, stats_v7.0.5 (59 PRs) has no regression row, and the 218-PR snapshot printed the would-open line.
  - #2841's minutes from the live comments: the block at 2026-10-26T01:01:44Z and the next verdict at 03:34:24Z give 152.7 → 153. The lane went red at 00:28:19Z, 33 min before the block, as stated.
- **Figures I could not re-derive:**
  - the 319-PR `--stats` run itself (this seat has no `gh` binary);
  - the 319-PR comment rescan that yields exactly #2698, #2825 and #2841;
  - the #2698 and #2825 comment timestamps, which I took from items.tsv;
  - the reviewers' 128.3 / 201.2 W/K and 11-process figures (the record also does not re-run these);
  - the "five other blocks quote tests / browser" count;
  - the body's `run.sh` line `5 TEST SCRIPT(S) PASSED`.
- **Class (step 6).** The record's section 5 states the enumeration: every lane CI runs that no local scope selects (NOT_A_TEST plus run.sh's unwired list). That returns `card_browser.mjs` and `nightly_ha.py`. The second is dispositioned: it needs Docker, it is left to its own key's record, and it runs only in the unrequired nightly-ha job. No undispositioned seam.
- **Forward carry (step 10).** The browser-lane finding lands in `fixer.md` step 5 in this diff, which is the later stage's own contract. carry_audit reads `2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`.
- **Metrics (step 14).** No budget, closure, golden, claim, ledger or archscore file moves. The token cap held by deleting the step-13 fidelity-vocabulary list ("faithful, divergent, simplified, unverified, or a holder"), which `tests/ha_contract.py` records itself. That is sound: it drops a copy, not information.
- **Version (step 5).** VERSION, the manifest and RELEASE_NOTES.md are absent from the three-dot diff (ev/tree.txt).
- **Merge (step 13).** `git merge-tree --write-tree origin/main 9cb4919101475766b2c92ec38e51a2d1c0a8a867` exits 0, tree 93ea2c00c4633830e58031724fbb755258d8c1b6. No claim file is touched.
- **CI at this head (step 11).** I read the PR's check-runs API: 40 runs, all completed, every one success or skipped. `governance / instrument-self-tests`, the last to conclude, ended success at 15:49:57Z. No red, so the body's `## Red checks: none` stands. No `pr-contract` or `gate` run appears at this draft head, so the body check is still CI's to run.
- **Head (steps 7, 12).** The body names 9cb4919101475766b2c92ec38e51a2d1c0a8a867 as the head, and that is the head I measured. The head did not move.
