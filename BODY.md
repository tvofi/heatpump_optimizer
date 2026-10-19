_Requested by **tvofi**_

policy: O17 items 1 and 3, the policy half, from the roster-cost pre-study the orchestrator accepted on 2026-10-18 (tvofi asked to keep the roster and state docs from costing CI). Part of #201. No roster group lists an issue for this work, so this body closes none. The tooling halves are `handoff/r10-roster-fastpath` (readers default to the roster branch, the beat watches it) and `handoff/r10-codeql-lang-skip`. The tick's line for unlanded roster commits is the coordinator's own, in the tick seat.

**Owner gate.** This is policy: `dev/governance/rules/finding-propagation.md` and `dev/governance/roles/{orchestrator,fix-review}.md` are in `POLICY_GLOBS` and code-owned, so tvofi approves this before it merges.

**Why.** A producing PR waited on a roster PR because the rule said the carry must be "in the tree", meaning on main. #2373 waited on roster PR #2384. Yet no check reads a roster carry's content from main:
- `policy_lint.mjs --pr-body` tests only that a `## Forward-carry` path exists, and the roster path always does. `brief_lint.mjs` documents this as cases 3 and 4, existence and not authorship.
- What enforced the wait was this text and `fix-review.md` step 10.

The pre-study measured the cost of that wait: 14 roster-only PRs merged in round 10 (median 49 min open to merge), and 54.1 runner-min on #2380's head. These figures come from the pre-study, outside the tree. This body does not re-derive them.

**The change.**
- **`finding-propagation` (canon `dev/governance/rules/`, both generated copies via `rules_sync.mjs`).**
  - Enforcement: a carry to the round's roster is in the tree once it is on that roster's branch `handoff/audit-r<N>-roster`. That branch lands on main at each stamp and before branch cleanup, and stays while `git diff origin/main...<branch> -- dev/programme/rosters/` prints anything. That is the durability guard: the carry survives a session because the ref outlives it, and cleanup may not delete it unlanded. The body names the branch SHA. A carry to any other destination still has to be on main.
  - **Two roster homes, both named and both bound.** "Where it goes" names a live group's `brief` in its roster: the round's roster under `dev/programme/rosters/` (`roster_lib.roster_path`), or a web-fix-wave `groupsFile` under `.claude/workflows/`. `paths:` keeps `.claude/workflows/*.json`, which main has, and adds `dev/programme/rosters/*.json` and `dev/programme/carries/*.json`. So the rule loads for a seat editing any live roster or carry.
- **`policy_lint.mjs` rule-binding, a new arm.** Every tracked roster file (`wave-*-groups.json`) or carry file (`carry-<N>.json`) outside `dev/archive/` and `tools/policy/fixtures/` is a live carry destination, and `.claude/rules/finding-propagation.md` must bind it. The arm finds these files by walking the tree, not by reading the rule's own globs. The previous head of this PR dropped `.claude/workflows/*.json` and every existing check stayed green, because the globs it kept still matched files. `brief_lint.mjs` exports `ROSTER_FILE_RE` so both linters use one filename rule. The acceptance gains a model of the #2408 shape, and its clean model now holds a bound roster, an archived roster and a fixture carry.
- **`orchestrator.md` section 10.** Land the roster on main only when the tree needs it: when a PR names a carry, when a `Closes` needs a `fixes` edit (pr-contract derives the allowed closes from the PR's tree), at each stamp, and before branch cleanup. Cleanup keeps the roster branch while it differs from main.
- **`fix-review.md` step 10.** Open a roster carry at the body's roster-branch SHA.
- **Paid in-file, no cap raised.** All three files were at zero headroom. The words paid were incident detail, a duplicate pointer, and rewording:
  - commit shas beside issue numbers;
  - "it has happened twice";
  - `Your other reusable scripts land too, by fixer.md step 18.`, which section 13's preceding sentence already states;
  - a lane-without-roster example;
  - in finding-propagation, shorter wording of the re-derivation sentence, the sibling-seam sentence, the two-copies sentence and the scratch-copy sentence. This paid for the two added globs and the second roster home.

  `policy_lint`'s `duplicates` entry for orchestrator.md drops from 8 to 6 and is re-recorded.
- **Out-of-scope fix, folded.** `node tools/policy/policy_lint.mjs --record-known-bad` crashed with `TypeError: at is not a function`: in `cmdRecord`, a local `const at = recordedAtSha()` shadowed the module's `at(path)`. Every re-record since then has needed a hand edit. The local is renamed `sha`. I did not re-derive which commit introduced the shadowing, and nothing here depends on it.

**Alternatives considered.**
1. Make CI read carries from the roster ref. Refused: a PR check that reads a mutable, unreviewed branch is not reproducible at a fixed head, and no CI check reads carry content anyway.
2. Keep "in the tree" as main and batch roster PRs only. Refused: the producing PR still waits on a roster PR's full CI.
3. Raise the three caps. Refused: each was payable in-file.
4. Make `dev/programme/rosters/` the only roster home and archive `.claude/workflows/wave-3l-groups.json`. Refused: `3L-G6` is `blocked`, not done, and `web-fix-wave.js` still requires a committed `groupsFile` under `.claude/workflows/`. Moving web-fix-wave's home is a tooling change outside this group.

## Head

`0fd1f3e4f217ff1e20ddc491428747afdf2fdf44` is this PR's code head. It is a merge of origin/main `06c6f3cf2589cd37fa9fe56cc5ebeef709dc8d3b` (read 2026-10-19T02:17Z) into the previous handoff head `357fe0fca9d484a761c75cd7e09ab8a0f01e7cf4`. The merge was automatic: no conflict, no resolution, and no file this PR authored changed. The red PR head `928a672753558ca6f88f45f806d9aa9b04440c36` was the orchestrator's earlier merge of an older main into `357fe0fca`; this head supersedes it.

`357fe0fca` is the authored code head, two commits on `e3a6f0729dbb5053bd92a5fb8168b3e74edbaa65`: the roster-home fix with its policy_lint arm, and the change that makes the arm judge each file at the path `locate()` reads. `git merge-tree --write-tree origin/main HEAD` (origin/main `06c6f3cf2`, 2026-10-19T02:17Z) exits 0 with tree `40fb19fd78d7`.

## Approval

Owed: tvofi's approval of this policy change before it merges (`CLAUDE.md`; the coordinator listed this PR as policy for tvofi at merge). It has not been given yet, and nothing here claims it.

## Mutation proof

Each mutant was applied to the head tree `0fd1f3e4f`, run, and restored with `git checkout` (`git status --short` empty after each). All four were re-run at this head after the merge, because `policy_lint.mjs` changed on main (#2423). The new check runs as `node tools/policy/policy_lint.mjs`.
- **M1, the `.claude/workflows/*.json` glob deleted from the head's globs** (the dropped glob that first-head review caught): rc=1, `TOTAL: 2 error(s)`. The arm names `.claude/workflows/wave-3l-groups.json` and `.claude/workflows/carry-1921.json`. So the test fails on the old code.
- **M2, the two added globs deleted** (`dev/programme/rosters/*.json` and `dev/programme/carries/*.json`; origin/main's globs): rc=1, `TOTAL: 10 error(s)`. These are `dev/programme/rosters/wave-r9-groups.json`, `wave-r10-groups.json` and the 8 carries under `dev/programme/carries/`. Main never bound the round roster or the carries directory. The arm judges the path `locate()` reads, so the 4 carries that `trackedFiles()` spells at their pre-move `.claude/workflows/` names are read at `dev/programme/carries/`.
- **M3, the arm's predicate made dead** (`continue` added after the binding test): `TOTAL: 0 error(s)` and `FIXTURE VACUOUS: the rule-binding 'unbound carry home' arm produced []`, rc=1. Killed by the acceptance fixture.
- **M4, the archive and fixture exclusion deleted:** `FIXTURE OVER-FIRES: rule-binding produced 2 finding(s)`, and on the real tree `TOTAL: 47 error(s)` (5 archived rosters, 37 archived carries and 5 linter fixtures), rc=1. Killed.
- **Caps.** The first draft of the round-1 head, the rule text added with nothing paid, measured `.claude/rules/finding-propagation.md 104 lines / ~1408 tokens` against caps 101 and 1336 (`node tools/policy/policy_lint.mjs --budgets`). The same draft measured orchestrator.md at 322 and ~4576 against 319 and 4513, and fix-review.md at 141 and ~2460 against 140 and 2451. In this round, the second roster home and the two globs with no rewording paid measured 100 lines / ~1338 tokens against 1336. That figure is the second iteration, after three of the four rewordings.
- **Citations.** A round-1 draft that named `dev/programme/rosters/wave-r<N>-groups.json` was refused by `policy_lint.mjs`: `[citations] .claude/rules/finding-propagation.md:57: path groups.json: not in the tree`. The head names the directory.
- **Generated copy.** Restoring origin/main's `.cursor/rules/finding-propagation.mdc` over the head's makes `node tools/policy/rules_sync.mjs --check` print `RULES-SYNC: 1 file(s) out of date`. Restored.
- **Known-bad.** Before the re-record, `policy_lint.mjs` printed `[known-bad] ... 6 occurrence(s) left of 8 recorded: duplicates|tools/audit/briefs/orchestrator.md`, and `--record-known-bad` crashed with `TypeError: at is not a function`. After the rename it printed `recorded 7 entr(ies), 13 occurrence(s) ... ~ 8 -> 6`, and the lint printed `TOTAL: 0 error(s)`.

## Null control

At origin/main `63816b857`, the unmodified tree's `policy_lint.mjs --budgets` reads 100/1329 (finding-propagation), 319/4513 (orchestrator.md) and 140/2451 (fix-review.md).

These lines change what the policy requires:
- finding-propagation's `## Enforcement` paragraph.
- orchestrator.md section 10's "Land the roster on main only when the tree needs it".
- fix-review.md step 10's roster-branch SHA.
- The two added globs. With them the rule also loads on `dev/programme/rosters/*.json` and `dev/programme/carries/*.json`.
- The rule-binding arm, a new refusal.

The second roster home in "Where it goes" restores the destination main already names, `.claude/workflows/`, and adds the round's roster beside it. Every other changed line in the three policy files rewords a sentence without changing what it requires, or removes an incident detail or a duplicate pointer, as listed above.

The arm's control is M1 and M2 above: the arm reads 10 errors on each set of globs it exists to refuse, and 0 at the head.

**`.claude/workflows/audit-verify.js`'s draft roster `.claude/workflows/wave-r${round}-groups.json`.** This path is unchanged, and it now sits in a home the rule binds and names again. `brief_lint.mjs`'s default scan lints any `wave-*-groups.json` there, and the new arm refuses an unbound one. Round 10's record shows the draft is a staging file: `f32a3924e` wrote the draft roster to `.claude/workflows/`, `4c584d2c6` dropped it from the record, and `db71fe47a` wrote the round roster under `dev/programme/rosters/`. Whether audit-verify should draft straight into `dev/programme/rosters/` is a tooling question for that driver. This rule is now true for both answers.

## Figures

All figures are at head `0fd1f3e4f217ff1e20ddc491428747afdf2fdf44`, re-taken after the merge of origin/main `06c6f3cf2`, unless a line says otherwise.
- `node tools/policy/policy_lint.mjs --budgets`: finding-propagation 100 lines (cap 101) and ~1336 tokens (cap 1336); orchestrator.md 319/319 and ~4513/4513; fix-review.md 140/140 and ~2451/2451; corpus ~61137 (cap 61026 plus band 500).
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`, then `FIXTURE ok: 92 error(s) hold 246 pins across 12 check classes`, rc=0.
- `node tools/policy/policy_lint_mutants.mjs`: `MUTANTS ok`, and `ruleBindingOverTree` is in its corpus list, rc=0.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `node tools/policy/brief_lint.mjs`: rc=0, `CARRY ok`.
- `python3 -I tools/policy/agreement_py.py --out J; node tools/policy/agreement.mjs --py-json J`: `RESULT divergent=0 unregistered=0 dead=0 refused=0`, rc=0.
- `node tools/policy/field_coverage.mjs`: `RESULT ... blind=0 dead=0 refused=0`, `FIELD COVERAGE ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2349 ENTITY CHECKS PASSED`, rc=0.
- **Gate scope.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out` (`tests/entities.py`, run above).
- **The class's seams.** The rule that lists them is `git ls-files | grep -E '(^|/)(wave-[^/]*-groups|carry-[0-9]+)\.json$'`, which is the arm's own walk. At the head it returns 59 files. Their dispositions:
  - 3 rosters and 9 carries are live: `.claude/workflows/` holds 1 of each, `dev/programme/rosters/` holds 2 and `dev/programme/carries/` holds 8. All are bound in this diff, and the arm reads 0.
  - 5 rosters and 37 carries are frozen under `dev/archive/`. They are excluded, not destinations.
  - 5 files under `tools/policy/fixtures/` are linter fixtures. They are excluded.

## Unpinned sites

- `policy_lint.mjs`'s `cmdRecord` write path: no fixture drives `--record-known-bad`, which is how a crash on every call went unseen. Triage: the run above is its one exercise. A pin belongs in `policy_lint_mutants.mjs`'s fixture drive. It is owed and stays open: that file is outside this group, so the orchestrator dispatches it (out-of-scope findings get fixed).
- The arm's use of `locate()`. No acceptance model holds a moved file, so reverting to the old spelling is caught only on the real tree, by M2's count (10, against 6 for the both-spellings version). Triage: the real-tree run is a value check that holds while main's move map spells 4 carries at `.claude/workflows/`. A synthetic moved-file model needs a move-map fixture, which `rule-binding`'s driver does not take today. That work is owed with the `cmdRecord` pin above.

## Red checks

These are the reds on the PR head `928a672753558ca6f88f45f806d9aa9b04440c36`, read from the check-runs API (`failure_logs.sh 2408`). Exactly two were red there, `wave-script` and `delivery-status`. `pr-contract` was green at that head, so no pr-contract red is owed an answer. Both reds are inherited from main and cleared by the main merge in this head:
- **`wave-script`** (run 39164766859, the agreement lane). `merge-subject-pr` read `divergent=2` on main's merges `Merge pull request #2401 (R10-ARCHSCORE-COVERAGE p5)` and `Merge pull request #2379 (R10-SENSOR-PAYLOAD)`: `stamp.py` and `delivery_status.py` read the PR number, and `policy_lint.mjs`'s `resolvePrFromCommit` read null. Cause: main's merge subject shape outran one reader. Cleared by main's #2423 (one merge-subject grammar across readers) and #2424 (the guard), both merged into this head. At this head `python3 -I tools/policy/agreement_py.py --out J; node tools/policy/agreement.mjs --py-json J` prints `RESULT divergent=0 unregistered=0 dead=0 refused=0`, rc=0. This diff touches none of those readers. The detector is the agreement lane itself, which went red on main's first push carrying the shape; no cheaper one exists.
- **`delivery-status`** (not a required context). It read `DELIVERY STATUS OVERDUE — 126 rowed, 8 pending, 3 overdue` against main `07a09406a`: rows for #2413, #2412 and #2407 sat 14 to 17 commits behind. Cause: main's row backlog, not this diff, whose only delivery file is its own row `2408.md`. Cleared by main's later record merges (`record: delivery rows` #2425 and the rows for #2420, #2423, #2424). At this head `python -I -S tests/delivery_status.py --check` prints `DELIVERY STATUS OK — 138 rowed, 2 pending, 0 overdue`. The two pending, #2425 and #2390, are the ordinary batch state.

Whether CI at this head is green is read after the orchestrator remerges; this body claims only the two local re-runs above.

## Forward-carry

none. This change is itself the rule text the next round's orchestrator reads.

## Friction

finding-propagation: stale: the rule named only `.claude/workflows/wave-*-groups.json` as a roster's home. The round's roster lives under `dev/programme/rosters/` (`roster_lib.py`), and no glob bound it or `dev/programme/carries/`. No check measured whether every live roster or carry is bound, and this PR's own first head dropped a live home with every check green.

