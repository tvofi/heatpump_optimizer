rca: R10-RCA-HARNESS-FRICTION, the root-cause record for the friction keys `harness` (#2331), `class-open` (#2353) and `mutation-vacuous` (#2409), routing `mutation (family)` (#2410) to its owner. One cause: a step in a contract that defines a block class does not teach the word `VERDICT_CLASSES` has for it. Step 6 of `fix-review.md` taught `harness: class-open` (#1414), and step 1 taught no word, so one obligation was keyed under several words and the cron filed it twice. Process state (c). The fix teaches both words (policy). The detector that was held while #2390 edited the same file is now in `check-wave-script.mjs`. The branch also carries the orchestrator's fold of #2423 into section 11 of `orchestrator.md` (policy). Part of #201.

Closes #2331

#2353 and #2409 are disposed by the record, and the orchestrator closes them by hand after the merge. #2410 leaves this group for R10-POLICY-LINT-FAMILY. #2428, #2429, #2436, #2437 and #2438 stay open (Forward-carry).

## Head

`f7802ee36aa86ec0cbf6e25d60ad33a9b129ad6c` merges origin/main `57f0c9c77cfd5958e0a2443e158bea8326bedae2` into the reviewed head `1019d18de448a9569c65a704410c331046cbe868`. It is a merge, not a rebase. Round 2 answers fix review 6315535889 (`blocked 1019d18de carry-missing`). Among the files this branch authors (`git diff --name-only $(git merge-base origin/main 1019d18de)...1019d18de`), `git diff 1019d18de f7802ee36` changes only `dev/governance/roles/orchestrator.md`. That file takes main's edits plus the resolution below.

Every figure below was taken at `f7802ee36` with origin/main at `57f0c9c77`, 2026-10-21T20:33Z to 21:10Z, except the window figures. Those are pinned to `v7.0.0..df6ca4bc6858f2796f694035e6f53e46e237e33b` and were re-taken in this pass from a worktree at that SHA. `git merge-tree --write-tree origin/main HEAD` exits 0.

**Merge resolution.** One file conflicted. In `dev/governance/roles/orchestrator.md` section 4, main rewrote the roster-text sentence ("Roster text applies too: a seat will paraphrase it into its own body — a third-hand path, and it has occurred."), and this branch had rewritten the same sentence to pay for the section-11 line. The merge takes main's sentence and re-applies this branch's payment: it cuts the narrative tail "— a third-hand path, and it has occurred". Main's sentence whole, without that cut, is over the cap: `policy_lint.mjs` printed `about 4517 tokens across its lines exceeds its cap of 4513`. `git diff origin/main -- dev/governance/roles/orchestrator.md` now shows only that cut and the section-11 line. `dev/audit/config/bugclasses.json` merged clean this time.

## Approval

Owed: tvofi's approval at merge, under mandate 6175172275, for the two policy files. These are `dev/governance/roles/fix-review.md` steps 1, 6 and 8 and `dev/governance/roles/orchestrator.md` sections 4 and 11. It has not been given, and nothing here claims it.

What changes what a seat must do:
- In step 1, a reviewer blocking on a surviving mutant writes `blocked <sha> mutation-vacuous: <mutant>`.
- In step 6, a reviewer blocking on an undispositioned seam writes `blocked <sha> class-open: <seam>`, not `harness: class-open <seam>`.
- In section 11, a direct merge passes no custom `--subject`.

Step 8 and section 4 only cut words: step 8's "rather than reporting a number as confirmed" restated its bold lead, and section 4's tail was narrative.

## Mutation proof

Re-taken at `f7802ee36`. Each mutant was applied with `sed`, run with `node tools/policy/check-wave-script.mjs`, and restored with `git checkout --`. `git status --short` was empty after each. `git diff --stat` showed the edit landed before each run.
- **M1, step 6 put back to the #1414 spelling** `harness: class-open <seam>`: rc=1, 202 passed, 1 failed. `FAIL fix-review.md teaches "class-open" as a reason under another class: blocked <sha> harness: class-open <seam>`.
- **M2, the shadow predicate's body replaced by `return null`**: rc=1, 201 passed, 1 failed. `FAIL the shadow predicate fires on the #1414 spelling (negative control)`.
- **M3, step 1's word misspelt `mutation-vacous`**: rc=1, 201 passed, 1 failed. `FAIL fix-review.md teaches block class "mutation-vacous", and VERDICT_CLASSES carries it`. This is the existing taught-word arm.
- **M4, step 1 put back to main's prose**: rc=0, 200 passed. No arm pins that step 1 is present. The record's section 8 refuses a presence arm.
- **M5, M1 plus the detector's loop line (`if (w) t(...)`) deleted**: rc=0, 202 passed. So that loop is the line that kills M1.

The script's `FAIL (probe, expected) threw: deliberate` line is a self-probe that prints on every run. It is not counted above.

## Null control

- `check-wave-script.mjs` with the head's detector, run on main's `fix-review.md` (`git show origin/main:dev/governance/roles/fix-review.md` copied into the head worktree): rc=1, 200 passed, 1 failed. The one failure is step 6's example. At this head: rc=0, 202 passed. The predicate's own null control, `harness: class-rule-missing`, is in the script.
- The class-reach census of the record's section 4. It reads `VERDICT_CLASSES` from `.claude/workflows/web-fix-wave.js` and every backticked `blocked <sha> <w>:` example under `dev/governance/roles/` and `dev/governance/dimensions/`. It is a one-off scratch probe. Its shadow arm is the in-tree detector above. At origin/main `57f0c9c77` it reads `classes 17 taught 6 shadows 1` (fix-review.md step 6). At this head it reads `classes 17 taught 8 shadows 0`. The 9 untaught words are the same as the record's section 4.
- `fold_ledger.py check` with this entry's `in_tree_home` pointed at a missing file prints `DANGLING: _rca[R10-RCA-HARNESS-FRICTION].in_tree_home ... is not a file under dev/audit/rca` and `1 violation(s)`. At this head it prints `0 violation(s)`.
- `gh api --paginate .../pulls/N/files --jq '.[].filename' | grep -c '^custom_components/'` returns 4 on #2365 and #2391, so the rule can return non-zero. It returns 0 on the other ten.
- The carry route. A carry file was planted at `dev/programme/carries/carry-2428.json` and then removed. `node tools/policy/brief_lint.mjs` (no-arg, the CI path) printed `-- 0 error(s)` for it and `TOTAL: 0 error(s)`, rc=0. A live group, R10-RCA-FRICTION, lists #2428 in `dev/programme/rosters/wave-r10-groups.json`, so this is a second destination that should have been refused. See Friction.

## Figures

The window is `v7.0.0..df6ca4bc6858f2796f694035e6f53e46e237e33b`. It was re-taken in this pass from a worktree at that SHA. The window is fixed, so these figures do not move with main. Re-derive them with the commands below rather than carrying the numbers.
- `git log --first-parent --format=%s v7.0.0..df6ca4bc...`, subjects `Merge pull request #N`, gives 229. The re-take matches the committed `dev/audit/rca/harness-friction/window_prs.txt` (`diff` exits 0).
- A per-PR fetch of `gh api --paginate .../issues/N/comments` and `.../pulls/N/reviews` (first line of each body, per `rounds.py`'s docstring) printed `PRS 229 FAILURES 0`. `python3 dev/audit/rca/harness-friction/rounds.py <dir>` gives 102 blocked verdicts. Sorted, they are identical to the committed `blocked_rounds.tsv` (`diff` exits 0). `SUM class-open 26 entries 7148 min`.
- `GITHUB_TOKEN=$(gh auth token) node tools/policy/policy_lint.mjs --stats --since v7.0.0`. Its window always ends at `origin/main`, whatever the checkout. So it was run in a local `--shared` clone whose `refs/remotes/origin/main` is set to `df6ca4bc`: rc=0, 394 s. Apart from the committed file's trailing `rc=0 secs=434` line, its output is identical to `dev/audit/rca/harness-friction/stats_v7.0.0.txt` (`diff` prints only that line). That is 234 merged PRs, of which 116 carry a parsable verdict. Counted as distinct PRs / entries: harness 15/23, class-open 5/7, mutation-vacuous 5/6, mutation (family) 7/8, carry-missing 12/15, root-cause-unanswered 5/7.
- The same command in a worktree at `df6ca4bc` but with the shared `origin/main` at `57f0c9c77` measured `v7.0.0..57f0c9c77` instead: 263 merged PRs, 131 with a verdict, harness 16/24, root-cause-unanswered 6/8. class-open (5/7), mutation-vacuous (5/6) and mutation (family) (7/8) are unchanged. This is the instrument's sliding window, not a change in the record's window.
- The mutation obligation is the union of the class words `mutation-vacuous`, `test-vacuous`, `vacuous-test`, `vacuous-check`, `mutant-survives`, `mutation-survivor` and `mutation`, read from the class column of the re-taken `blocked_rounds.tsv`. It covers 12 distinct PRs. 10 of them change no `custom_components/` file (Null control).
- `node tools/policy/policy_lint.mjs --budgets`: fix-review.md 140/140 lines and ~2443/2451 tokens (main ~2451). orchestrator.md 317/319 and ~4506/4513 (main 317 and ~4502). Corpus ~61138 (main ~61142). No cap moved, because no `*_budgets.json` is in the diff.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`, rc=0.
- `node tools/policy/policy_lint_mutants.mjs`: `MUTANTS ok`. `node tools/policy/rules_sync.mjs --check`: rc=0.
- `node tools/policy/check-wave-script.mjs`: rc=0, 202 passed, 0 failed.
- Detector cost: two rounds of five runs of `check-wave-script.mjs` per tree. At origin/main the means were 0.233 s and 0.164 s. At this head they were 0.211 s and 0.170 s. The difference between trees is inside the spread between rounds on one tree.
- `python3 tools/audit/fold_ledger.py check`: `0 violation(s)`, with 114 rca entries.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `HPO_STATE_DIR=/opt/hpo PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body> 2331`: rc=0, `PRE-PR: f7802ee36aa86ec0cbf6e25d60ad33a9b129ad6c ...`. The closure step was skipped by the variable, so the scoped gate above stands in for it.
- `python3 -I tools/audit/archscore/gate.py --base 57f0c9c77cfd5958e0a2443e158bea8326bedae2 --head HEAD --body <this body>`: `PASS: dS +0.0000 NULL, no gate metric rose`.
- `python3 tools/audit/carry_audit.py check --body <this body>` (the roster in the head's tree): `CARRY-AUDIT: 14 finding item(s): 14 routed, 0 unrouted, 0 bad destination(s)`, rc=0. The same with `--roster-ref origin/handoff/audit-r10-roster`: the same line, rc=0. Control: the previous body, checked by CI's pr-contract run 119230480706 at `1019d18de`, gave `6 bad destination(s)`. That tree's roster has no group listing #2428, #2429, #2436, #2437 or #2438 (`git show 1019d18de:dev/programme/rosters/wave-r10-groups.json`).
- **Gate scope.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. The script is `tests/entities.py`. Under `PYTHONPATH=tests/hastub` with the CI venv's Python 3.14 (`/opt/hpo/venv-ci`) it prints `ALL 2382 ENTITY CHECKS PASSED`, rc=0. Its `FAIL` lines are its own planted probes. The `run_always` lines (`env_drift.py --claims-only origin/main`, `closure.py selftest`, `layout.py`, `harness_headers.py`): each rc=0. The claim files are not in the diff.
- **The class's seams** (fixer.md step 8). The rule is the detector itself, a walk over every contract verdict example, plus the census above. The detector returns one seam, step 6, which is closed in this diff. The census returns step 1, also closed in this diff, and 9 untaught `VERDICT_CLASSES` words. Their dispositions are in the record's section 4: the two `root-cause-*` words are R10-BRIEFS-FOLD's carry, and the rest are blocks that no window split took above threshold.

## Red checks

Read from `gh api .../commits/1019d18de.../check-runs` for the reviewed head. This new head has not run CI yet.
- `pr-contract` (119209550896, 119230480706): the carry_audit step failed with `6 bad destination(s)`. This PR's diff did not cause it. That head's roster lacked the R10-RCA-FRICTION group, which reached main afterwards through the roster branch. The merge brings it in, and carry_audit passes at this head (Figures). Cheaper detector: carry_audit already runs locally in under a second, and the fixer can run it with `--roster-ref origin/handoff/audit-r10-roster`. The round-1 body ran it against the roster ref and passed, but CI reads the tree's roster. The cheaper detector is to run carry_audit without `--roster-ref` before handoff. That costs one extra sub-second run. No new check is owed: `prepr.sh` and pr-contract already run the tree-roster form. The miss was this seat not running the form CI runs.
- `nightly-status` (119210180269): `NIGHTLY FAILED: mutation-nightly, slow failed last night`, scheduled run 39563978649 at `c77f89d`. This grades `main`, and this diff touches none of what it reads: its scripts, `tests.yml`, `governance.yml`, the plan, `HANDOVER.md`, or a delivery row other than its own `2561.md`. Per `defect-root-cause.md` it is the orchestrator's on main.

Every other check on `1019d18de` concluded success or skipped.

## Forward-carry

- The detector in `tools/policy/check-wave-script.mjs` lands in this PR. That spends the R10-BRIEFS-FOLD roster carry, "The first group to edit tools/policy/check-wave-script.mjs after #2390 ... lands it". The BRIEFS-FOLD fixer re-reads `fix-review.md` steps 1 and 6 at its merge base. Any new verdict example it writes for step 11 (`root-cause-detectable:`, `root-cause-unrecorded:`) must put the word first, because the detector now refuses a taught word in the reason position. Carry: R10-BRIEFS-FOLD
- The refused unconditional `fixer.md` step 8 (record section 8) is already item 11 of that group's brief, and the tooling-mutant substance of #2409 is its item 1. Re-measure both at that group's merge base with `rounds.py`, not from this record's numbers. Carry: R10-POLICY-FIXER-MD
- #2410's family arm reads 7/8: `mutation-vacuous`'s 5 PRs plus #2390 (`mutation`) and #2444 (`mutation-survivor`). The member `mutation-vacuous` fired its own line in the same window, so 5 occasions are filed twice. The family's member list also misses `test-vacuous`, `vacuous-test`, `vacuous-check` and `mutant-survives` (record section 5). Control: the distinct-PR list in `dev/audit/rca/harness-friction/blocked_rounds.tsv`. Carry: R10-POLICY-LINT-FAMILY
- #2428 (`carry-missing`), #2436 (`other`) and #2437 (`root-cause-unanswered`) are in this group's roster issues, but this record neither measures their cause nor disposes them. `blocked_rounds.tsv` reproduces their `--stats` counts (12/15, 3/3, 5/7). The three `other` blocks are literal `other:` verdicts (#2294, #2404, #2406), not words split away from a taught one. Carry: #2428
- The same applies to #2436, which the line above measures. Carry: #2436
- The same applies to #2437. Its 7 blocks name 4 different checks, and none recurs across 3 PRs (`pr-contract` #2404 #2485, `wave-script` #2404 #2406, `fast` #2347, `arch-score` #2444). Carry: #2437
- #2429 (`.claude/rules/ci-autofix.md`) and #2438 (`.claude/rules/finding-propagation.md`) are friction rule ids read from PR bodies' `## Friction` sections, which this record's verdict enumeration does not read. Carry: #2429
- The same applies to #2438. Carry: #2438
- **Ownership after this merge.** These five issues resolve to a live owner only through R10-RCA-FRICTION, the group this PR delivers. The round-2 brief offered a `dev/programme/carries/carry-<N>.json` per issue, and that route was not taken. `finding-propagation.md` refuses a carry file at an issue a live group covers ("so no stage has two destinations"), and R10-RCA-FRICTION covers all five in `dev/programme/rosters/wave-r10-groups.json` at this head. When the orchestrator sets this group's `resume.stage` to `done`, `python3 tools/audit/carry_audit.py check --body <this body>` will report the five as `has no owner` again. So that roster edit must also re-home them, in a new or existing group or one carry file each. Roster edits are frozen while PR-A is under review, so this seat made none. Control: carry_audit at this head gives `0 bad destination(s)`. With the group's stage set to `done` in a scratch worktree's roster, that worktree's `carry_audit.py` prints `6 bad destination(s)`, rc=1, naming exactly these five issues (#2437 twice). Carry: #201
- Roster carry "Source: #2452 Friction", about the cost of `tests/card.mjs`. It records a priced, deliberate cost (fresh render per drive) and does not touch this record's cause. Carry: dismissed: a cost the source itself justifies, with no obligation or instance count for this group to dispose
- Roster carry from R10-RCA-NIGHTLY-PYSPY, which says a red-check answer has no cross-run count. Over this window, the `root-cause-unanswered` blocks name no check on 3 or more PRs (the #2437 line above), so no instance count clears the bar the carry itself sets. Carry: #2437

## Friction

brief_lint: unenforced: `tools/policy/brief_lint.mjs`'s `rosterIssues()` and its no-arg roster list read only `.claude/workflows/wave-*-groups.json` and the carries directory. They never read `dev/programme/rosters/`. So the `briefs` CI job neither lints round 10's roster briefs nor refuses a carry file at an issue a round-10 group covers. Measured: the no-arg run lists `.claude/workflows/wave-3l-groups.json` as its only roster. A planted `carry-2428.json`, whose issue R10-RCA-FRICTION lists, gave `0 error(s)`, rc=0 (Null control). `finding-propagation.md` and `brief-citations.md` both state that brief_lint reads the round's roster. Carry: #201

ledger_merge: unenforced: the `ledgermerge` driver routes `dev/audit/config/bugclasses.json` (`.gitattributes`) but can never merge it. `_format()` accepts only `json.dumps(...) + "\n"`, and `fold_ledger.py`, the file's writer, writes no trailing newline. `ledger_merge._format(<origin/main's bugclasses.json>)` returns `None`, and the same text plus `"\n"` returns `{'indent': 2}`. So every `_rca` conflict is refused with "a side is not in its writer's own JSON format" and is resolved by hand. The self-test misses this because it builds its sides with `+ "\n"`. Carry: #201

prepr: unclear: in a cloud seat whose environment provisions the CI venv at `/opt/hpo/venv-ci`, `tools/pr/prepr.sh` looks for `$HPO_STATE_DIR/venv-ci/bin/python3` under its default state directory. Its `closures` step and five `6b` self-tests therefore refused with "no interpreter that parses the tree was found". The same run under `HPO_STATE_DIR=/opt/hpo` was clean, with rc=0. Nothing in the seat brief names the variable. Carry: #201

🤖 Generated with [Claude Code](https://claude.com/claude-code) · https://claude.ai/code/session_01EKuEDAWj345nexzL3YvFAA
