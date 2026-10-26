R10-FLOW-JIDOKA: error-proofing in `tools/pr/prepr.sh` before handoff. The pull request has three parts. Closes #2428.

- **Step 7e, the carry check.** The new function `carry_line` runs pr-contract's own checker, `python3 -I tools/audit/carry_audit.py --roster-ref <round ref> check --body <body>`. It runs on the body in full prepr (step 7) and in `--body-check`, which is the call `body_push.sh` makes at every handoff. No rule is added (decision 0012). Revision 8 sets the ref: `roster_lib.round_ref` names it (`origin/handoff/audit-r<N>-roster`), and the step fetches it before reading. With `--roster-ref`, carry_audit reads groups and carry files at that ref and nowhere else. That is where fix-review step 10 looks, so a group that exists only in the worktree's roster, or only in a stale mirror, is refused. If the ref cannot be named or fetched, the step refuses rather than reading the mirror. A design choice the reviewer should see: a group that is on main but not yet on the round branch is refused here, while pr-contract would pass it, because pr-contract reads the tree's roster as well. Prepr's step 6d still predicts pr-contract's own reading offline (`ci_predict.py --body`). Step 7e adds the reviewer's reading.
- **Step 7c, the red-check arm: why it did not fire, and the gate fix.** The answer is under Figures (census), and it has three parts. The gate defect: 7c skipped whenever 7b's local mirror of the pull request's head ref was absent ("no $UPREF yet"). 7b never fetches, by design. A fixer pushes `handoff/<topic>` and never fetches the `fix/<topic>` head that `handoff_push.sh` opens, so the arm read nothing on revision rounds, even when earlier pushed heads already carried reds. 7c reads check runs over the network anyway, so it now gates on `reds_head_sha`, which fetches the ref first. An unfetchable ref is a skip, like every other unread 7c input. The other two parts are not this gate's to fix. Most cited reds first appeared at the blocked head itself, which no pre-push read can see. The pr-contract reds are excluded from 7c by design, and step 7e now catches the carry refusals among them.
- **Heavy steps die with the prepr** (carried from #2528, R10-PREPR-CAP). Before this change, steps 3 to 3h ran their programs in the foreground. A TERM to the prepr was deferred until the program exited, and a KILL left it running. That included the 3h self-test (about 5 min) and the 3a mutants drive. A new helper, `heavy_run`, wraps 6b's existing recorder pattern: the program runs in its own process group (`set -m`), the prepr `wait`s on it, and a watchdog reaps the group once `$$` is gone. Every program in steps 3 to 3h now runs through it, and so does 6b's recorder, which keeps one copy of the pattern.
- The ledger cites the class's second RCA. `dev/audit/config/bugclasses.json` gains the `_rca` entry `R10-RCA-BODY-CHECK-PARITY`, as that RCA's `## Forward-carry` asked, and `N-body-lint-bounce` now lists it with a wider barrier text. `dev/governance/roles/fixer.md` step 5 and an `app_push.sh` comment no longer say that prepr omits the carry check.

Alternatives considered:
- (a) Without `--roster-ref`, carry_audit unions the tree's roster with the round mirror. That is the offline read revision 8 names as the defect: the "worktree roster only" fixture passes it (see Null control).
- (b) Make 7b fetch too. 7b's header argues "NO NETWORK, EVER" for a check that would otherwise be run as `|| true`. Only 7c reads the network, so only 7c fetches.
- (c) Background each heavy step by hand, copying the recorder's watchdog. That would be twelve copies of one pattern. `heavy_run` is the one owner, and 6b now calls it too.

## Head

`2b0eb9d853c6f319bf2c61acee24baeae7b945ce`. Its merge base is `da12aa37dee15b9e9567bd6c848493436f2592dd`, which was origin/main's tip when read at 2026-10-25T17:50Z. Three commits sit over the merge base:
- `1b9a86266`, the change itself.
- `d4bce566f`, which cuts the step 5 sentence in `fixer.md` back under `tools/audit/briefs/fixer.md`'s `files_tokens` cap. The first wording had put the file 13 tokens over.
- `2b0eb9d85`, which re-keys four rewritten lines so they no longer name a `/tmp/` or a retired path. These are the two pinned-grader planters, the foreground-step row, and the agreement step's fallback, which now sits on one line. It also drops the `tmp_paths.py` allow entry that the old planter text needed. The full prepr at `d4bce566f` refused the layout guard and temp paths on those lines.

The mutant drive and the census were taken at `1b9a86266`. Neither moves under the later two commits: they touch no mutated line, and no line or row that a mutant's kill depends on. The self-test count, prepr and every other figure were taken at `2b0eb9d85`.

## Approval

`dev/governance/roles/fixer.md` is policy, and this pull request changes one sentence of its step 5. Before, the sentence said the body must also pass `carry_audit.py check --body`, "which prepr omits". Now it says prepr's step 7e is the carry check. This is a correction to match the new step, and it adds no obligation to a seat, but the owner's approving review is still owed before the merge. `tools/pr/prepr.sh` and `tools/audit/seat/tmp_paths.py` are code-owned paths too.

## Mutation proof

Each mutant was applied to `tools/pr/prepr.sh` in a detached worktree at the head, and the full `bash tools/pr/prepr.sh --self-test` was run once per mutant before the file was restored. The driver is the scratch harness `$S/mutants.py` plus `$S/mutants.sh`, not in the tree. M1 to M8 ran at `1b9a86266`, whose M0 (unmutated) gave 377 passed, 0 failed. M9 is quoted from its re-run at `2b0eb9d85`, the head whose re-keyed row it is killed by. Each mutant fails the rows named:

- M1, the step 7e call deleted from the main flow: 1 failed, "the body step runs carry_line on the body and refuses on its rc".
- M2, the `carry_line` call in `--body-check` replaced by a pass: 1 failed, "and refuses a body whose Forward-carry the lint passes and carry_audit reads as unrouted, pushing nothing". This is the body_push arm.
- M3, `--roster-ref "$ref"` dropped: 2 failed, "and carry_line refuses it: the round branch, where fix-review step 10 looks, lacks the group" and the BAD-DEST line row.
- M4, the round-branch fetch replaced by `if false`: 3 failed, "the same carry passes once carry_line fetches the round branch", the ok-line row, and "and the refusal says why".
- M5, `heavy_run` run in the foreground: 12 failed. Among them are the 6b reap arms ("a KILL to the prepr leaves no recorder ... running", got `gone:alive:alive`) and the 6b recording rows.
- M6, the `heavy_run` watchdog dropped: 6 failed. These are the three 6b reap arms and the three new heavy-step reap arms, each `gone:alive:alive`.
- M7, step 7c gated on 7b's `UPSHA` again: 1 failed, "and step 7c gates on it, not on 7b's UPSHA".
- M8, `reds_head_sha` without its fetch: 2 failed, "reds_head_sha finds a pushed head the mirror lacked" (got 3) and "and returns the origin's sha for it".
- M9, the 3h self-test line in the main flow back in the foreground: 2 failed, "no step from 3 to 3h runs a program in the foreground" and "and 3h's self-test, the heaviest, runs through heavy_run".

Result: 9 planted, 9 killed.

## Null control

- **Self-test count.** At the merge base `da12aa37d`, `bash tools/pr/prepr.sh --self-test` prints `352 passed, 0 failed`. At the head it prints `377 passed, 0 failed`. The difference is 25, and the head adds exactly 25 `st` arms:
  - 8 in block (9): 3 reap arms, 2 foreground null controls and 3 call-site rows.
  - 11 in block (10), the carry rows.
  - 5 in block (11), the 7c rows.
  - 1 body_push row.
  - No row of the base's was removed or renamed. The sorted ok-name sets differ only by the 25 new names: `diff` of the base and head name lists shows 25 `>` lines and 0 `<` lines once the 11 pinned-grader planters were re-keyed. Those 11 rows key on step 3e's text, and the planter is updated to the new `heavy_run` form; their names are unchanged.
- **Worktree-only carry.** In the block (10) fixture, `carry_audit.py check --body` without `--roster-ref` passes a carry to a group that exists only in the worktree's roster (rc 0). That is the defect. `carry_line` refuses the same body with carry_audit's own `BAD-DEST ... R10-LOCAL` line.
- **Stale mirror.** carry_audit with `--roster-ref` at the unfetched mirror refuses a carry to a group that only the origin's round branch holds (rc 1). `carry_line` fetches the branch, and the same body then passes.
- **Unrouted, then routed.** The unrouted Forward-carry fixture is refused with an `UNROUTED` line. The same item with `Carry: R10-ROUND` passes.
- **7c.** The fixture clone has no mirror of the origin's `fix` (`rev-parse` rc 1, which is what 7b reads). `reds_head_sha origin/fix` returns the origin's sha. A branch the origin lacks returns rc 3.
- **Foreground.** The same sleeper run in the foreground outlives a KILL to the prepr (`gone:alive:alive`), and a TERM leaves the prepr itself waiting (`alive:alive:alive`). Through `heavy_run`, all three arms read `gone:gone:gone`.
- **The RCA's four recorded instances** (R10-RCA-BODY-CHECK-PARITY section 1). This tree's `carry_line` was run on each `BODY.md`. Each passed the old `--body-check`, which had no carry step:
  - `21af14bd` (#2643): rc 1, 2 unrouted.
  - `888ce1e0` (#2658): rc 1, UNROUTED `bd4b6c1e`.
  - `99940d99` (#2664): rc 1, UNROUTED `97ab79eb`. That is the id CI's pr-contract job 120428691732 printed.
  - `66f506fc` (#2666): rc 1, UNROUTED `ac72ee0e`.
  - The null is the current `handoff-body/r10-flow-autotrain-r5` tip `560d24c09`: rc 0, `5 routed, 0 unrouted`. The RCA's suggested null, `b3b67b1b`, no longer passes against today's roster branch (5 unrouted), so it was not used.

## Figures

- `bash tools/pr/prepr.sh --self-test`: `352 passed, 0 failed` at the merge base, and `377 passed, 0 failed` at `1b9a86266` (M0). Full prepr's step 3h at `2b0eb9d85` gave `377 passed, 0 failed`. Wall time by `time` on this box: 4 min 55 s at the base and 5 min 15 s at `1b9a86266`.
- Mutants: 9 planted and 9 killed, by the kill rule "the self-test's summary reports one or more failures". The driver printed no `PATTERN NOT FOUND` for the run counted (M9's first pattern matched twice and was re-keyed to the flow line).
- The census of why 7c did not fire is `$S/reds_census.sh`, a scratch script that is not in the tree. Its rule:
  - Input: every `Fix review: blocked <sha> (root-cause-unanswered|ci-red)` issue comment created on or after 2026-10-12, read through `repos/tvofi/heatpump_optimizer/issues/comments?since=2026-10-12T00:00:00Z`. That window includes 17 verdicts.
  - Classification: each check name that the verdict line cites, and that failed at the head or on any earlier commit of the PR, gets one class. PR-CONTRACT is pr-contract itself, which 7c's `REDS_JQ` excludes. RED-AT-EARLIER means the check failed on a PR commit listed before the blocked head. HEAD-ONLY means it failed only at the blocked head.
  - Result: 24 cited reds. 11 are HEAD-ONLY, 7 PR-CONTRACT and 6 RED-AT-EARLIER.
  - The HEAD-ONLY reds did not exist when the body was linted, so no pre-push read can see them. That is the job of step 6d's prediction, and the roster's fast (3.14) and instrument-self-tests carries are where it continues.
  - 5 of the 7 PR-CONTRACT verdicts cite carry_audit (#2404 at `b419463b1` and `519bb4db9`, #2469, #2485, #2560). Step 7e is their pre-push twin.
  - The 6 RED-AT-EARLIER reds were readable by 7c with a fetched head ref: #2368 fast (3.14), #2424 and #2529 instrument-self-tests, #2444 arch-score, #2527 and #2140 mutation. The gate fix addresses these.
  - Null control: the first pass cut each verdict line at its first `(` and matched nothing in 5 verdicts (`fast (3.14)` was cut). The rule above matches the whole line.
- `carry_line` wall time on a 5-item body: 908, 704 and 699 ms over 3 runs, mostly the fetch. The checker alone measured about 0.1 s in the RCA.
- `bash tools/pr/prepr.sh <this body> 2428` at `2b0eb9d85`, 30 min 52 s wall: every step is `ok` or `skip` except `closures` (below). The new step's line is `ok carry CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s), at origin/handoff/audit-r10-roster 32ffe43c0`. Step 7c skips with `no origin/fix/r10-flow-jidoka on the remote, fetched now`, because no pull request exists yet.
- prepr's `closures` step refuses locally: `failed while being recorded: tests/entities.py (exit 1)`. `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `2 of 2445 ENTITY CHECKS FAILED` at the head and at the merge base, and the FAIL-line names, sorted with their bracketed detail stripped, are identical (`diff base head && echo IDENTICAL-FAIL-NAMES` printed it). The FAIL lines include the `hb:positive_control` py-spy check at its third try, which this container cannot satisfy. Which two lines the count tallies was not separated. So the recording truncates the same way at the base. It is this box's, not this diff's, and CI's `closures` job records on its own runner.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)` from `d4bce566f` on. At `1b9a86266` it printed `ERROR [budgets] tools/audit/briefs/fixer.md: about 5229 tokens ... exceeds its cap of 5216 tokens`, which is what `d4bce566f` repairs.
- Live, outside the self-test: `bash tools/pr/prepr.sh` was started at `d4bce566f`. Its 3h nested `bash tools/pr/prepr.sh --self-test` appeared after 385 s, and 5 s later the top prepr's pid alone received a TERM. The top prepr exited 143, no nested self-test process was left within 1 s, and `pgrep` then found no prepr, `derive_closures` or `sleep 300` process. An earlier attempt is not counted, because it signalled the watchdog's pid as well.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out` and `RUN tests/entities.py`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff da12aa37dee15b9e9567bd6c848493436f2592dd HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/audit/fold_ledger.py check`: `0 violation(s)`, `122 rca entries`.
- `python3 -I tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused`. The new fixtures use `throwaway_git_init` and `throwaway_git_clone`.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: `0 refused`. The one push the diff adds is inside the self-test's fixture origin.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.

## Red checks

- `governance / record`, red on main's tip `da12aa37d` (job 121219438293). `friction_issues.mjs` refuses there because "the census summary declares 67 key(s) and 66 row(s) parsed". This diff touches neither `friction_issues.mjs` nor the census, so the red is main's. The detector that grades it is that job, on main.
- `tests / nightly-status`, if red on main's ancestry. It grades main's nightly lane, not this head, and this diff did not turn it red.
- `tests / ci-ratchet`, which may be red on main's push runs: GitHub's repo-wide artifacts listing returns 0 bytes, and a hotfix is in flight. It is not this branch's red, and this diff does not touch `tests/ci_ratchet.py`.

## Forward-carry

- The rest of this group's roster carries are not built in this pull request. They are: the parity test (G1, G2), one grammar owner for `## Forward-carry` (G3), the P-N body-check extensions, the base-pinned replay (P3), ref_privacy and figure_lint at body push, quiet output, `--fill-red`, the wave-script trigger glob (P75), the claims.py byte-identity check, and predicting fast (3.14) and instrument-self-tests. They remain on `R10-FLOW-JIDOKA` in `dev/programme/rosters/wave-r10-groups.json` on the roster branch. This pull request was scoped by the dispatch brief, and the S size cap (about 400 lines) cannot hold them. Carry: R10-FLOW-JIDOKA
- The census's HEAD-ONLY class (11 of 24 cited reds) needs a predicting detector, not a reading one. Step 7c can only read reds on commits already pushed. Carry: R10-FLOW-JIDOKA

## Friction

none
