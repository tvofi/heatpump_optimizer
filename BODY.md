A stopped pusher must not leave its work running, and no pusher may join the tree without the same guarantee.

A shell does not forward TERM, INT or HUP to a foreground child. So a stopped pusher exited, and its subtree was reparented to launchd and kept burning CPU. On 2026-10-20 six survivors were swept up, aged 26 to 62 minutes, on a box at load 77 on eight cores. The previous head fixed three pushers it named. The review of `c071fa5f` found a fourth (`handoff_push.sh`) that no rule had enumerated. This head closes the class: it adds the rule that enumerates every pusher, and it treats every seam that rule returns.

**The rule (the census).** `tools/audit/seat/pr_args.sh --pushers [<rev>]` defines a pusher as every tracked `tools/` script (`*.sh`, `*.py`, `*.mjs`, `*.js`) that names `app_push.sh` or `push.sh`. The test is the `git grep -lE '(^|[^A-Za-z0-9_])(app_)?push\.sh'` it runs. Every path the grep returns needs exactly one disposition in `PR_PUSHERS`:
- `runner`: the script installs `pr_exit_trap`, and every line running `"$_push"` or `"$prepr"` runs it asynchronously.
- `runner-py`: the script TERMs its tool rather than SIGKILLing it, and its entry calls `stop_on_signal()`.
- `retired`: `push.sh`.
- `mention`: the script names a pusher but runs none, and the entry gives the reason.

The census prints `OPEN` and exits 1 in three cases: a returned path with no entry, an entry the grep no longer returns, or a runner that lacks either property. `pr_args.sh --self-test` runs the census on the tree, and CI runs that self-test on every governance run (`open_pr.sh` / `update_pr.sh --self-test` steps). So a new pusher cannot land undispositioned.

**The mechanism is one EXIT trap.** `pr_exit_trap [<command>]` sets `trap "<command>; pr_reap" EXIT`. bash runs the EXIT trap when TERM, INT or HUP ends the shell, as well as on every other exit. The TERM/INT/HUP signal traps of `c071fa5f` (`pr_signal_traps`, `pr_signal_exit`) are deleted. They only duplicated the EXIT trap, which is why that review found their mutants survived. Each push runs asynchronously, and the shell `wait`s on it. The reason is INT: an untrapped INT waits for a foreground child, while all three signals interrupt `wait`. `pr_reap` now ignores further TERM/INT/HUP while it runs (`# mut:sigign`), so a second stop cannot end the shell before the KILL that follows the grace period (`# mut:grace`).

Seams treated in this diff:
- `handoff_push.sh`: the one the review found.
- `remerge_main.sh`: the census also returned it. It ran `app_push.sh --recarry` in a foreground command substitution.
- `merge_train.py`: the census also returned it. `Train._run` used `subprocess.run`, whose own handler SIGKILLs the child, and an untrapped TERM ended the train with its tool still running. `Train._run` now TERMs the tool and waits for that tool's own trap to reap the tree. `stop_on_signal()` turns TERM and HUP into `SystemExit`, so a stop unwinds through that handler.
- `cloud_relay.sh`: the level-2 caller the review named (it runs `update_pr.sh`).
- The previous three, `open_pr.sh`, `update_pr.sh` and `app_push.sh`, are moved onto the one mechanism. `app_push.sh` installs it once, beside `cleanup`, which is now a no-op until `$PRIV` exists.

Every signal still goes to a numeric pid the walk returned: never a pattern, never a group.

SIGKILL stays out of scope, because no trap runs. The KILL arm of `update_pr.sh` asserts only that the lock does not go stale.

## Head

`b5b91be95a2dd08a1d8daab07c406c07a8509e97` is the code head, and everything below was measured there. It merges origin/main `5226fd2d` into `6945363d7f67cae739baafc7ac3f4601068a9d28`, my last commit. Origin/main's tip was read at 2026-10-21T15:40:08Z. The merge touched none of the eight files this PR changes (`git diff --quiet 6945363d7 b5b91be95 -- <the eight>` exit 0), and it needed no hand resolution. `6945363d7` itself sits on PR head `c071fa5f37abdac0da2284547b9282549eb4d607` and merges origin/main `e7c66485`. `prepr` runs with `PREPR_SKIP_CLOSURES=1` (the owner's ruling), so the scoped gate was derived separately and is in `## Figures`.

## Mutation proof

Every mutant was applied to the committed head and restored with `git checkout -- <file>`, and `git status --short` was empty afterwards. The runner is a scratch `mut.sh` that applies one exact-match replacement, runs the named self-test, and prints its `FAIL` lines.

- **M0, the null run:** no change to any line. `pr_args self-test: 74 checks, 0 failed`.
- **M1 `handoff_push.sh`, `pr_exit_trap` dropped from its source line:** 4 failed.
  - `handoff_push: TERM reaps the whole descendant tree, and the pusher is gone`
  - `the pusher census: the rule returns exactly the dispositioned paths, and every runner reaps`
  - `the census on the scratch copy passes as it does on the tree`
  - `a runner whose push runs in the foreground is refused`. This arm fails because the no-trap OPEN fires first.
- **M2 `handoff_push.sh`, `hp_push` run in the foreground:** 2 failed, the two census arms.
  - The census flags it as `a push runs in the foreground`. The first M2 run, before `6945363d7`, survived: the census read `2>&1` as a background `&`. The check now strips redirections, and a self-test arm pins exactly that shape.
- **M3 `remerge_main.sh`, `pr_exit_trap` dropped:** 3 failed: `remerge_main: TERM reaps the whole descendant tree, and the pusher is gone` and the two census arms.
- **M4 `open_pr.sh`, the first push back in the foreground:** 3 failed: `open_pr: INT reaps the tree too -- the push runs asynchronously, so the INT does not wait behind it` and the two census arms.
- **M5 `cloud_relay.sh`, `pr_exit_trap` dropped:** `cloud_relay self-test: 75 checks, 1 failed`, `a relay TERMed mid-update leaves none of the update's tree alive (R10-PUSHER-REAP)`.
- **M6 `app_push.sh`, `pr_exit_trap cleanup` dropped:** `app_push self-test: 139 checks, 11 failed`. The failures include `and leaves none of prepr's tree alive (R10-PUSHER-REAP) (got '3', want '0')`, and ten token-revoke and private-directory arms.
- **M7 `merge_train.py`, `p.terminate()` turned into `p.kill()`:** `merge_train self-test: 200 checks, 1 failed`, `a TERMed train exits 143 and leaves none of its tool's tree alive (R10-PUSHER-REAP)`.
- **M8 `merge_train.py`, `main`'s `stop_on_signal()` call deleted:** the census prints `OPEN tools/audit/seat/merge_train.py runner-py: a stop SIGKILLs or orphans its tool`.
- **M9 `merge_train.py`, the handler's `raise SystemExit(128 + signum)` turned into `return None`:** 1 failed, the same arm as M7.
- **Built-in mutants.** `pr_args.sh`'s self-test runs each one on copies of the scripts, and each arm passes only because its mutant shows the defect:
  - `mut:exitreap` (`pr_exit_trap`'s trap line): the open_pr, handoff_push and remerge_main survivor arms.
  - `mut:grace` (the KILL line): a TERM-proof child survives.
  - `mut:sigign`: a second TERM ends the host mid-reap, and the child survives.
  - `mut:stop` (`pr_kill`'s kill): the open_pr and update_pr survivor arms.
  - `mut:unlock` and `mut:watch` are unchanged.

  The review found four survivors at `c071fa5f`: the signal-trap call, app_push's EXIT reap, the KILL escalation, and both EXIT backstops. Each is now either gone (the signal traps) or killed: M6, `mut:grace`, and `mut:exitreap` with M1/M3.

**Failing test first.** At this head, the new arms ran against `c071fa5f`'s `handoff_push.sh` and `remerge_main.sh`, the two files copied in with `git checkout c071fa5f --`. `pr_args self-test` printed `74 checks, 5 failed`:
- `handoff_push: TERM reaps the whole descendant tree, and the pusher is gone`
- `remerge_main: TERM reaps the whole descendant tree, and the pusher is gone`
- the two census arms
- `a runner whose push runs in the foreground is refused`

The new arms for `cloud_relay.sh`, `app_push.sh` and `merge_train.py` live inside those files, so their red runs are M5, M6 and M7/M9.

## Null control

- **The bystander.** An unrelated sleeper, started outside any pusher's tree, survives every TERM arm and the successful-run arm. The reap goes by pid only.
- **The merge_train arm** runs its own control: the same driver without `stop_on_signal()`. In it the train dies and all 3 pids of its tool's tree survive (`null control: without stop_on_signal the train dies and its tool's tree survives`), so the arm can see the defect it pins.
- **The census.**
  - On a scratch tree holding copies of every entry, the census passes. Planting `tools/audit/seat/new_pusher.sh` running `app_push.sh` makes it refuse `undispositioned`. Deleting `handoff_push.sh`'s `pr_exit_trap` makes it refuse `no pr_exit_trap`, and dropping its `&` makes it refuse `a push runs in the foreground`. These are self-test arms.
  - An enumeration that returns nothing cannot pass. Run from a path outside the repository (`bash <(git show …)`), the grep returned nothing, and the census printed 16 `stale` OPEN lines and exited 1.
- **No vacuous arm.** Every reap verdict first requires that the push's tree started (4 recorded pids, `treen`). Before that guard, one handoff_push arm passed with nothing to reap: a branch collision stopped the run short of its push. Now such a run fails the arm.

## Figures

Measured at `b5b91be95a2dd08a1d8daab07c406c07a8509e97`. origin/main `5226fd2d11b71deddd359c328f7ec1805e22b752` was read at 2026-10-21T15:40:08Z.

- **The class's seams.** Rule: `bash tools/audit/seat/pr_args.sh --pushers <rev>`, the git grep above with the dispositions in `PR_PUSHERS`. It returns 16 paths at the merge base `e7c66485`, at `c071fa5f` and at this head.

  | seat | disposition | base `e7c66485` | `c071fa5f` | this head |
  |---|---|---|---|---|
  | `tools/audit/seat/handoff_push.sh` | runner, closed in this diff | OPEN | OPEN | ok |
  | `tools/audit/seat/remerge_main.sh` | runner, closed in this diff | OPEN | OPEN | ok |
  | `tools/audit/seat/merge_train.py` | runner-py, closed in this diff | OPEN | OPEN | ok |
  | `tools/audit/seat/open_pr.sh` | runner, closed in this diff | OPEN | OPEN* | ok |
  | `tools/audit/seat/update_pr.sh` | runner, closed in this diff | OPEN | OPEN* | ok |
  | `tools/pr/app_push.sh` | runner, closed in this diff | OPEN | OPEN* | ok |
  | `tools/pr/push.sh` | retired: decision 0011's retired author path, which no runner executes (the level-2 rule below returns no caller) | ok | ok | ok |
  | 9 `mention` paths, each with its reason in `PR_PUSHERS` | mention | ok | ok | ok |

  The 9 mention paths are `pr_args.sh`, `handover_prompt.py`, `ref_privacy.py`, `app_approve.sh`, `approve_held_runs.sh`, `head_note.py`, `check-wave-script.mjs`, `friction_issues.mjs` and `policy_lint.mjs`. Census exit status: 1 at the base, 1 at `c071fa5f`, 0 at this head.

  \* At `c071fa5f` these three did reap, through `pr_signal_traps`. The census keys on `pr_exit_trap`, the mechanism this head replaces them with, so this reading of that commit is name-keyed. The review measured those three as reaping.
- **Level 2: who executes a runner.** Rule: `git grep -nE '(bash|exec)[^#|;]*(handoff_push|open_pr|update_pr|remerge_main)\.sh|tool\("(remerge_main|app_push)"\)' HEAD -- 'tools/*.sh' 'tools/*.py'`. Each returned line and its disposition:
  - `cloud_relay.sh` (update_pr): closed in this diff, with its own arm.
  - `merge_train.py` (remerge_main, and app_push `--branch-only`): closed in this diff (runner-py).
  - `pr_args.sh`, five lines: its self-test fixtures.
  - `r9_rc_bus_fetchhead.sh`: a round-9 measurement harness that runs `handoff_push.sh` in a scratch fixture.
  - `tmp_paths.py`: a self-test string.

  Callers above level 2 (`train.sh` runs `merge_train.py`; `tick_loop.sh` runs `cloud_relay.sh`) stop a child that now reaps its own tree.
- **Self-tests at this head:**

  | command | result |
  |---|---|
  | `bash tools/audit/seat/open_pr.sh --self-test` | `delivery_row self-test: 5 checks, 0 failed`; `pr_args self-test: 74 checks, 0 failed` |
  | `bash tools/audit/seat/update_pr.sh --self-test` | the same two lines |
  | `bash tools/audit/seat/handoff_push.sh --self-test` | `delivery_row self-test: 5 checks, 0 failed` |
  | `bash tools/pr/app_push.sh --self-test` | `app_push self-test: 139 checks, 0 failed` |
  | `bash tools/audit/seat/cloud_relay.sh --self-test` | `cloud_relay self-test: 75 checks, 0 failed` |
  | `python3 tools/audit/seat/merge_train.py --self-test` | `merge_train self-test: 200 checks, 0 failed` |
- **The scoped gate:** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` names `tests/entities.py`. `PYTHONPATH=tests/hastub python tests/entities.py` (python 3.13 with `tests/requirements-ci.txt`) printed `ALL 2375 ENTITY CHECKS PASSED`.
- **Checks before push:**
  - `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
  - `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD` printed `Architecture score: dS +0.0000 NULL`.
  - `python3 -I tools/audit/seat/tmp_paths.py --check` printed `tmp_paths: 0 refused, 0 stale allow entries at HEAD`.
- **Anchors still unique:** every anchor that `dev/audit/harnesses/r10_seat_selftests_mutants.py` (landed on main in this merge) plants in a file this PR changes occurs exactly once at this head. I ran its tables' `text.count(old) == 1` over the files under `tools/`, and nothing came back.
- **Rule 3 / rule 4:** `git diff --name-only $(git merge-base origin/main HEAD)...HEAD` names no `VERSION`, manifest, `RELEASE_NOTES.md` or claim file.

## Red checks

- **`pr-contract` at `c071fa5f`.** `carry_audit.py` refused 3 unrouted body items: the `## Forward-carry` "none -- …" sentence and both `## Friction` lines. The body caused it, not the code, and this body is written fresh: `## Forward-carry` and `## Friction` are each a bare `none`. A cheaper detector already exists, `carry_audit.py`'s own check, which `prepr.sh` runs before the push. The previous body went out without that run's refusal being acted on. I am naming the trigger here; its analysis belongs to `root-cause.md`'s seat.
- **`nightly-status`** grades `main`. This diff (eight `tools/` scripts) does not reach anything it reads.

## Forward-carry

none

## Friction

none
