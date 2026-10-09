R9-CI-2b, PR 2 of 2 (tvofi's decisions on the pre-study, 2026-10-08: build the carry rule and the merge-main bot as well as #2057's layout; the carry also covers remerge_main.sh / merge_train main merges). The problem it answers is the one in #2057: when a head moves after a verdict or a body was written, it costs a full review round even when nothing moved but a bot or an automatic main merge. In the bus refs (review/*), #2024 and #2010 lost `merge` verdicts that way, and only a bot's ledger commit stood between each verdict and its live head.

Closes #2023

**1. The carry (`tools/pr/app_approve.sh carry()`).** A commit under a bot subject may now change main's merge-driver files and that bot's own paths, and nothing else:

| subject | own paths |
|---|---|
| `ci: pin killed mutants` | the mutation ledger |
| `ci: re-record closures` | `tests/closures.json` |
| `ci: drop inherited claims` | the claim files |
| remerge_main.sh's `claims: drop the claims main already carries after the main merge` | the claim files (the owner's Q3) |

Round 2 adds two rules for a bot subject:
- the commit's author must be that subject's writer: `github-actions[bot]` for the `ci:` subjects, the orchestrator's `tvofi` noreply address for remerge_main.sh's;
- a claim-file subject may only remove lines.

What those commits wrote is left out of the branch's own-diff comparison. A `ci:` commit that touches main's driver files alone keeps #1667's rule unchanged.

**Disclosure.** Author and subject are git metadata anyone who can push may write. A seat that forges the bot's identity can still carry a `killed_by` entry no run measured under `ci: pin killed mutants`. That is the same reach a seat's own ledger edit has, and `policy_lint.mjs` says the same of pr-contract's acceptance. Seats commit as `tvofi`, so the `claims:` subject's author check binds nothing against a seat. Its remove-only rule is what prevents a forged one from adding a claim.

**2. The merge-main bot (`tools/pr/merge_main_bot.py`, `.github/workflows/merge-main.yml`).** It runs on each push to main. A pull request gets `ci: merge main` only when all of these hold:
- GitHub reports it unmergeable;
- its head does not contain that main;
- git's text merge (every driver replaced by `git merge-file`, which is GitHub's view) conflicts only on `.gitattributes` driver files;
- main's drivers resolve every one of them, with no `refused`.

Other properties of the bot:
- **Pushes.** At most one push per pull request per main push. The push is never forced, and a head that moved since the read is skipped.
- **Code it runs.** Only main's code runs: `git merge-tree` in main's checkout, then `commit-tree <tree> -p <head> -p <main>`.
- **Loop guard.** It triggers on a push to main and pushes only to pull-request branches. The head it leaves contains main, so a second run does nothing.
- **Held runs.** Each push is dispatched, then approved as the Actions-only App, as claims-autofix does; this is fail-soft.
- **Testing.** It has a dry run (`workflow_dispatch`, `dry_run` defaults to true) and `--self-test`, which governance.yml now runs.
- **Branch names.** A branch name outside `[A-Za-z0-9._/-]` is skipped, because the pull request chose it.

**3. pr-contract accepts the bot's merge, and only that merge (round 2).** `checkPrBody` accepted only single-parent autofix commits on the named head, so every bot merge would have turned the contract red. `AUTOFIX_BOT_COMMITS` gains `ci: merge main`, a two-parent commit, and it is accepted only when all of these hold:
- its second parent is on `origin/main` (round 2);
- its tree is git's own merge of its parents outside the driver files, the #1667 rule;
- those driver files are read from `origin/main`'s `.gitattributes`, never from the parent's (round 2).

The walk then continues down the first parent. pr-contract's checkout uses `fetch-depth: 0`, so `origin/main` is there. A clone without it refuses, and never assumes.

**4. Policy** (owner approval through the orchestrator's mandate). Each change is paid in the same file, so every cap holds:
- `fixer.md` step 6: the head is frozen except to the orchestrator, the merge-main bot or a commit `--carry` passes (round 2 names the bot). `ci-autofix.md`'s section heading now says what the section permits, and `merge-main.yml`'s concurrency comment is corrected: a queued run is replaced by the next push's.
- `fixer.md` step 7: a head that `--carry` reaches needs no body re-take, but the bot reds must be named.
- `fixer.md` step 5: run run.sh's `run_always` lines too (the #2051 entry of #2039).
- `fix-review.md` step 7: the body's SHA may `--carry` to the measured head.
- `ci-autofix.md` and `claim-files.md` permit exactly this bot, and no second one.

## Head

`b630c9e1e122e20374cc5951ad2e6a1c9f011668` merges origin/main `f84d891e1` into the previous head `afe9cfd87649cfc1de24608267fab4fdcf33ce6a` (a by-hand merge by a seat; `afe9cfd8` is the head that carried the approval). Conflicts: `tests/closures.json`, resolved with `tools/merge/ledger_merge.py --resolve tests/closures.json`; `dev/governance/roles/fixer.md`, where main's step 17 (#2064) is kept as main has it and this PR's step 5, handoff and step 7 edits are re-applied, trimmed to hold the 315-line / 5216-token cap (`policy_lint.mjs --budgets`: 315 / 5215).

`0ac45f6417399f2316ba8e03668345a842835c42` is the code head (round 2), measured 2026-10-08.

## Mutation proof

The ledger is `/Users/timmalmstrom/hpo-seats/r9-ci-2b/mutation2.txt`. Each mutant was applied in its own worktree, then restored.

- P1 (pin subject unmapped in `bot_paths`): `app_approve.sh --self-test` FAILs "CARRY: mutation-autofix's ledger commit, inside its own paths (R9-CI-2b)" and "CARRY: a merge from main, then the ledger commit it set off (#2024's shape)".
- P2 (the ci: guard ignores bot paths) and P3 (the own-diff comparison keeps bot paths): those two FAIL, plus "CARRY: remerge_main.sh's inherited-claims commit".
- P4 (pr-contract's automatic-merge test deleted): `tests/entities.py` FAILs "and refuses every chain that is not purely the bot's own repair" (`merge_main_hand` accepted).
- B1–B6 (`merge_main_bot.py --self-test`):
  - B1, other-file conflicts allowed: the null control "a code conflict beside the ledger one is left for a human" FAILs.
  - B2, clean heads not skipped: FAIL.
  - B3, containment not checked: FAIL.
  - B4, driver refusal ignored: FAIL.
  - B5, GitHub's view computed with the drivers: "a ledger-only conflict the driver resolves is planned for a merge" FAILs.
  - B6, parents reversed: FAIL.
- Round 2:
  - P5 (pr-contract's main-ancestry check deleted): `tests/entities.py` FAILs "and refuses every chain that is not purely the bot's own repair" (`merge_main_offmain` accepted).
  - P6 (carry's author check deleted): FAILs "NO CARRY: the ledger commit under the bot's subject but a seat's author".
  - P7 (claims remove-only deleted): FAILs "NO CARRY: the same subject adding a claim line". The ledger keeps a first P7 run whose replacement never applied, so it measured nothing; it is marked as such there, beside the re-run.
  - Reading `.gitattributes` at the parent instead of at main is not separately killed. With the parent required to be on main, the two differ only when main changed `.gitattributes` after that parent. I say so rather than count it.
- M0, unmutated, at `0ac45f64`: `app_approve self-test: 153 checks, 0 failed`, `merge_main_bot self-test: 24 checks, 0 failed`, `tests/entities.py` ALL 2213 PASSED.

Failing first:
- Round 2: the review's two forgeries in the entities fixture, under the round-1 `policy_lint.mjs`, read `merge_main_offmain` accepted (rc=0) (`/Users/timmalmstrom/hpo-seats/r9-ci-2b/failing-first-pr2-r2.txt`).
- Before the carry code, the three new carry cases read `got '1', want '0'` (`/Users/timmalmstrom/hpo-seats/r9-ci-2b/failing-first-pr2.txt`).
- The new entities fixture under main's `policy_lint.mjs` FAILs "pr-contract accepts the merge-main bot's automatic `ci: merge main`" (F0 in the ledger).

## Null control

Each of these runs on real heads, against main's unmodified copy as the control:

- The carry on the two lost verdicts:
  - `app_approve.sh --carry 65f5e914 8fb1b717` (#2024) and `--carry dc4e3f13 b78e5810` (#2010) print `CARRY: yes` at this head.
  - The same calls with main's copy print `CARRY: no ... is a ci: commit that changes files outside main's merge-driver files`.
  - #2025 (`0662bd8e -> 95b08306`) stays `no`, because it merges `b21ed75e`, which is not on main. That refusal is correct.
- The bot's merge on #2010's head against origin/main, built with `plan_one` + `commit_merge` (`fe9425e2`):
  - `--carry dc4e3f13 fe9425e2` gives `CARRY: yes`; main's copy gives `no`.
  - `policy_lint.mjs --pr-body <body naming the PR head> --head <bot merge>` prints `accepted autofix commit(s) on top of it: ... (ci: merge main)`; main's copy refuses it as "not an autofix message".
- The bot's decision on the live DIRTY heads against origin/main (`plan_one`, real drivers): #2053 and #2010 give `merge`; #2054 and #2025 give `skip-no-text-conflict` (main had moved).

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 2 script(s) run` (`tests/entities.py`, `tests/harness_headers.py`). `merge-main.yml` was recorded in both of their closures by hand, the two that read every workflow.
- Run locally on venv-ci 3.14 (round 2 at `0ac45f64`; the bot's self-test is 24 checks): `tests/entities.py`, `tests/harness_headers.py`, `tests/layout.py`, `tests/env_drift.py --claims-only origin/main`, `tests/closure.py selftest`, `tests/structure.py`, `bash tools/pr/app_approve.sh --self-test`, `python3 tools/pr/merge_main_bot.py --self-test`. Each result is in `/Users/timmalmstrom/hpo-seats/r9-ci-2b/gate2/`. The rest is CI's.
- `node tools/policy/policy_lint.mjs --budgets`: every changed policy file is at or under its cap. `policy_lint.mjs` prints `TOTAL: 0 error(s)`, and `rules_sync.mjs --check` passes. No cap was raised.
- The lost-verdict count (two of three post-verdict losses were the ledger commit alone) is the bus refs' VERDICT.md first lines, read as in `/Users/timmalmstrom/hpo-seats/r9-ci-2b/PRESTUDY.md` section 4.

## Red checks

Measured at `9e44f73c`, the previous head:

- `CodeQL` (check run 113314033968): alert #35, `py/overly-permissive-file` (high), at `tools/pr/merge_main_bot.py:247`, where the self-test's stand-in driver was chmodded `0o755`. Fixed to `0o700` in `154c9139`, so the alert does not stand at the new head. Cheaper detector: none on a seat. CodeQL needs its CLI and runs on every pull request; the cost was one head move.
- `pr-contract` (run 37777939476): it refused the round-1 body for the unnamed `delivery-status` and `nightly-status` below. The body now names them. The cheaper detector is `prepr.sh`'s ancestry-reds step, which reads them only after CI has posted them; it did refuse the first body update.
- `delivery-status`: OVERDUE, because rows for merges already on `main` are unread (`#1998`, `#1992`, `#1991`, `#1989`). The diff touches `.github/workflows/governance.yml`, a reporter input, which voids the main-state exemption. It only adds one self-test step there, though, and the only row it adds is its own. Clearing the red is the orchestrator's, on `main`.
- `nightly-status`: `main`'s scheduled run 37595831734 failed `mutation-ledger`, `mutation-nightly` and `record-autofix`. Those are lanes this diff does not touch, and the nightly reports its own state, so none is owed.

## Forward-carry

none. The friction dispositions below are the owner's fold into R9-CI-2b. The two that need a seat of their own are named for the orchestrator, not carried to a brief by this pull request.

## Friction

none

## Approval

Policy plus a new workflow: `dev/governance/roles/fixer.md`, `fix-review.md`, `dev/governance/rules/ci-autofix.md`, `claim-files.md` (and their generated `.claude/rules`, `.cursor/rules`), `.github/workflows/merge-main.yml`, `.github/workflows/governance.yml`. tvofi decided this on the R9-CI-2b pre-study (2026-10-08), relayed by the orchestrator: build the carry rule and the merge-main bot, and amend `ci-autofix.md` to permit exactly that bot. Owner approval of the merge is the orchestrator's, under the mandate.

## Friction-issue dispositions (owner's fold, 2026-10-08)

Each is keyed on the merged bodies and verdicts in `v6.7.16..origin/main`. The verdict instances come from the review/* bus refs.

- #2023 `head-moved`: closed here. The instance (#2010, head moved by `ci: pin killed mutants`) now carries (null control above). The carry also covers the bot merge, and `fix-review.md` step 12's carry clause now reaches it.
- #2020 `conflict`: no keyword. The instances (#1987 twice, #2025) conflicted on code, README, `docs/architecture.md` and the D6 claims artefacts, none of them driver files, so `fix-review.md` step 13 blocks them by design. #2057 and this pull request remove the driver-only share. The D6 claims artefacts are a generated-file conflict of their own, and that is the orchestrator's to route. Suggest closing: the residue is by design.
- #2028 `root-cause-unanswered`: no keyword. There are 10 distinct pull requests in the window, which is past the recurrence trigger, so it is owed to `dev/governance/roles/root-cause.md`, not to this fix. A third of them (closures #2007, #2018, #2053; mutation #1987, #2025) were reds a bot answered, which `ci-autofix.md` already lets a body answer by naming. The class itself is reds that land after a body is written.
- #2034 `harness`: no keyword. Seven pull requests were blocked for an open class or a missing harness. That is the review working as `fix-review.md` step 6 intends, not friction this change touches. Route to D13 (process yield) if its rate is the question.
- #2019 `other`: no keyword. The instances (#1997 re-cut, #2010 typing and screenshot, #2013 RCA count) share no cause. `other` is the verdict grammar's catch-all, so the fix is vocabulary in `.claude/workflows/web-fix-wave.js`'s classes. That is out of scope here.
- #2039 `fixer.md`: no keyword. The #2051 entry (step 5 omits `run_always`) is fixed here, and #2030's step-2 contradiction was already resolved: step 2 now defers to `ci-autofix.md`. The remaining entries are #2041 (a test left `time.monotonic` patched: the D3/D14 test-gap class, not `fixer.md`) and #2026, #1975 and #1974 (environment costs: CI-only replay, Darwin `features.py`, prepr self-test under the venv shim). Suggest closing.
- #2046 `ratchet-budgets.md`: no keyword. All three entries (#2044, #1958, #1942) record cap pressure that the rule prices on purpose, and each was paid or raised by its own pull request. There is no defect; suggest closing.
- #2052 `ci-autofix.md`: no keyword. All three entries were fixed by the merged pull request they name. #2049 (R9-CI-1) made INERT READS the bot's, and #2018 fixed the log the stale sentence described. #1987's `skip-failed-recording` on an unrelated script was also fixed by #2049: the base `closure.py` now leaves a failed recording of a script the check did not name out of the merge (`apply_under_scoped_recordings`). Suggest closing.

