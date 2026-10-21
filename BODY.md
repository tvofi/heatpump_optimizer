`roster_edit.py --push` could print `pushed <branch> at <sha>` with rc 0 for a commit that never reached origin. This change commits the edit in a detached worktree and pushes that commit as `<sha>:refs/heads/<branch>`. When a rival has moved the branch, the push is rejected; the tool then re-fetches, re-applies the op on the new tip, re-lints and pushes again, up to `PUSH_ATTEMPTS` times. After that it refuses with rc 2. It never force-pushes.

**The cause.** `run()` checks the exit status, and two separate clones racing get a loud rc 2 (the `separate` arm below), so the suspected swallowed exit status is not it. The roster branch was a *named local branch*, and every worktree of one repository shares its local branches. On 2026-10-21 seat C committed b622ec9f1 on `handoff/audit-r10-roster` in worktree `wt-5`. During C's lint gate the orchestrator, from another worktree of the same repository, ran `checkout -B` on that branch, which git 2.38 allows while another worktree has it checked out, and committed 2f37a1cb6. C's `git push origin handoff/audit-r10-roster` then pushed whatever the shared ref held, exited 0, and the tool printed the `head` it had captured before the lint. GitHub's activity log for the branch holds no push of b622ec9f1 and no force push; `af5daaa5b -> 2f37a1cb6` at 09:58:36Z is the only move from af5daaa5b (`gh api repos/tvofi/heatpump_optimizer/activity -f ref=refs/heads/handoff/audit-r10-roster`).

**The fix and the alternatives.**
- Taken: no local branch at all. The worktree is detached, and the push names the commit the run made and linted. A rejected push is classified by re-fetching: if `origin/<branch>` moved off this run's base, the run re-applies its op on the new tip through `apply_op`, the one dispatch every attempt runs; if origin did not move, it refuses at once with git's own message.
- Rejected: keep `checkout -B` and push by sha. That turns the false success into a refusal, but the shared branch can still be reset before the run's commit, and `commit -am` then builds the run's tree on the rival's parent and silently reverts the rival's edit in a fast-forward push. Mutant M5 keeps a named branch and four checks fail.
- Rejected: `--force-with-lease`. The brief forbids forcing, and a lease only turns a lost race into a refusal.
- Rejected: a lock file. It covers seats on one machine and one repository; the race is on the remote ref, whose compare-and-swap on a plain push is the lock.

The reuse guard follows the new model: a `--worktree` whose HEAD is on no `refs/remotes/origin/*` ref (a lint-refused or unpushed edit) is refused, except the run's own commit that lost a race.

**The merge with main (this round).** Main's R10-ROSTER-OPS added `set-after` and `drop-carry` to the inline dispatch in `main()` that this branch had replaced with `apply_op`. The resolution in d729496d9 adds both ops to `apply_op` and passes `a.match` through, so the new ops are re-applied on a lost race like every other op and there is no second dispatch. The self-test's `edit()` takes main's `match=` and this branch's `wt=`; the self-test's local `contextlib`/`io` imports go because main imports both at module level. Mutants M6 and M7 pin the two resolution sites.

No issue is attached, so this body carries no closing keyword. The orchestrator appends the group R10-ROSTER-PUSH-RACE.

## Head

`d729496d9856d6acc8ac30f01149555c85ef49b9` merges origin/main `e9febe6224eaccedbdcd3ffdf3f92a84cb034e9a` into the PR head `5ffbaaaeb827f184ed44abd9ead267ee8e626b08`, resolving the content conflict in `tools/audit/seat/roster_edit.py` as above. Every figure below is measured at d729496d9, merge base e9febe622, with `/opt/hpo/venv-ci/bin/python` (3.14.7). At 2026-10-21T16:03Z origin/main is at 49c222280; `git merge-tree --write-tree --name-only origin/main HEAD` exits 0, and `git diff --name-only e9febe622 origin/main` names none of this diff's five files.

## Mutation proof

Failing test first: commit e19bda54f adds the race checks and only the `PUSH_ATTEMPTS` constant. Re-run there, `python tools/audit/seat/roster_edit.py --self-test` reads `roster_edit self-test: 82 checks, 7 failed`, including `FAIL race: the loser's edit reaches origin (got: solo-2)`, `FAIL race: the sha reported pushed is origin's tip` (a sha printed as pushed that origin does not hold, the 2026-10-21 shape) and `FAIL a non-race push failure refuses at once ... has uncommitted changes`.

Each mutant is an exact one-occurrence replacement in `tools/audit/seat/roster_edit.py` at d729496d9, the self-test run, the file restored byte for byte (the driver's closing `git diff --exit-code` passed):
- M1, race never retried (`if not tip or tip == base_sha:` -> `if True:`): 7 failed, e.g. `FAIL race: rc 0 after re-applying on the rival's tip`, `FAIL race: the loser's edit reaches origin`.
- M2, own lost commit not discardable (`if old != discard and not run(` -> `if not run(`): 7 failed, e.g. `FAIL race: the sha reported pushed is origin's tip`.
- M3, bound off by one (`range(1, PUSH_ATTEMPTS + 1)` -> `+ 2`): 2 failed: `FAIL race on every attempt: refused (rc 2), said loudly`, `FAIL race on every attempt: origin holds every rival, not this edit`.
- M4, reuse guard off (`raise Refuse(` -> `print(` on the unpushed-HEAD guard): 1 failed: `FAIL a worktree holding an unpushed edit is not reused`.
- M5, named branch back (`checkout -q --detach base_sha` -> `checkout -q -B branch base_sha`): 4 failed, e.g. `FAIL race on every attempt: bounded at PUSH_ATTEMPTS rivals (got: ['rival carry 2', 'rival carry 3'])`.
- M6, merge resolution: `drop-carry` dropped from `apply_op` (falls to append-carry): the self-test exits 1 with `AttributeError: 'NoneType' object has no attribute 'startswith'` before its tally.
- M7, merge resolution: `a.match` not passed to `apply_op`: the self-test exits 1 with `TypeError: int() argument must be ... not 'NoneType'` before its tally.

Main's own sweep over the ops this merge routed through `apply_op`, `python tools/audit/seat/r10_roster_ops_mutants.py` at d729496d9: every plant A1-A7, C1-C8, P1-P3 and D1 prints `rc=1` with `fails>=1`; `--null` prints `RESULT mutant=null rc=0 fails=0`; `--self-test` prints `r10_roster_ops_mutants self-test: 63 checks, 0 failed`.

## Null control

- Self-test M0, the unmodified head: `roster_edit self-test: 106 checks, 0 failed`. Its solo arm runs before any race arm: `solo edit: rc 0, one push, no race said` and `solo edit: exactly one commit added, the one reported` pass.
- Harness `solo` arm, one edit and no rival: base and head both `silent_losses=0 false_reports=0 refused_edits=0 pushes=1` on 3 of 3 runs, so the fix adds no push or retry when nothing races.
- Harness `separate` arm at the base: 10 of 10 runs `refused_edits=1` with `silent_losses=0`; separate clones never lose an edit silently, which is why the shared-checkout arm, not a swallowed exit status, explains the field case.

## Figures

The harness is `bash dev/audit/harnesses/r10_roster_push_race.sh <tree> <shared|separate|solo>`, run from the head worktree with `PYTHON=/opt/hpo/venv-ci/bin/python`. `<tree>` is the base, a `git archive e9febe622 tools tests` export, or the head worktree at d729496d9. Counts are its `mode=` summary lines tallied with `sort | uniq -c`, 10 runs per race arm and 3 per solo arm. `silent_losses` counts runs with rc 0 whose edit is not in origin's roster; `false_reports` runs that printed `pushed ... at <sha>` for a sha origin's tip does not contain; `refused_edits` runs with rc not 0; `pushes` commits the branch gained.
- base, shared: 6 of 10 runs `silent_losses=1`; 2 of those 6 also `false_reports=1`, the 2026-10-21 shape. 2 of the 6 are `silent_losses=1 refused_edits=1 pushes=2`: both commits landed, one run was told it failed, and one edit is still missing. The other 4 runs are `refused_edits=1 pushes=1`.
- head, shared: 10 of 10 `silent_losses=0 false_reports=0 refused_edits=0 pushes=2`.
- base, separate: 10 of 10 `silent_losses=0 false_reports=0 refused_edits=1 pushes=1`.
- head, separate: 10 of 10 `silent_losses=0 false_reports=0 refused_edits=0 pushes=2`.
- solo, both trees: 3 of 3 `silent_losses=0 false_reports=0 refused_edits=0 pushes=1`.
- `python tools/audit/seat/roster_edit.py --self-test`: `roster_edit self-test: 106 checks, 0 failed`. The tally prints `passed`, which already counts every check; main's `passed + len(failed)` counted each failure twice. CI's grep `^roster_edit self-test: [1-9][0-9]* checks, 0 failed$` still matches.
- `python3 tests/closure.py select --diff e9febe6224eaccedbdcd3ffdf3f92a84cb034e9a --workdir <dir>`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, naming `RUN tests/entities.py`.
- With `PYTHONPATH=tests/hastub`: `tests/entities.py` printed `ALL 2375 ENTITY CHECKS PASSED`; `tests/env_drift.py --claims-only e9febe6224eaccedbdcd3ffdf3f92a84cb034e9a` printed `claims hygiene: e9febe6224eaccedbdcd3ffdf3f92a84cb034e9a ok`; `tests/closure.py selftest` printed `ALL 124 closure shrink pins PASSED`; `tests/layout.py` exited 0; `tests/harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED`; `tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused, 0 stale allow entries at HEAD`.
- `python tools/audit/seat/ref_privacy.py --self-test`: `ref_privacy self-test: 66 checks, 0 failed`.

The class search: no other pusher reports success on a push it did not make. The rule is `git grep -lE '"push"|git( -C [^ ]+)? push\b' -- tools .claude/workflows .claude/hooks`, then the lines that reset a branch with `-B` (`git grep -nE 'checkout", "-B"|checkout -B' -- tools`, which now returns only two comments in `roster_edit.py`), plus `push.*(\|\| *true|check=False)`. The file set the first command returns at d729496d9 equals the set at the previous round's base 5d433771a (`diff` of the two sorted lists exits 0), so each production site keeps its disposition:
- `tools/audit/seat/body_push.sh` (`$C:refs/heads/$REF`), `tools/audit/seat/bus.sh`, `tools/audit/seat/state_docs.py` and `tools/pr/merge_main_bot.py` push a sha with the exit status checked (`set -e`, `|| REFUSE`, `run()`, a `skip-push-refused` line never counted as pushed). Already guarded.
- `tools/release/stamp.py` `push_via`: `sh(..., check=True)`, pushing `HEAD:main` from the stamp's own checkout. Already guarded.
- `tools/audit/seat/wt_sync.sh`: a deliberate force push of a sha to a per-slug `wip-sync/` ref. Not this class.
- `tools/pr/push.sh`: pushes a branch by name, rc checked; retired by decision 0011.
- `tools/pr/app_push.sh`: pushes `"$br"` by name and reports a `$head` captured earlier, the same shape, guarded by refusing unless `HEAD == refs/heads/$br` just before minting and, on the pull-request path, reading the PR head back against `$head`. Its callers keep the branch in one worktree (`update_pr.sh` refuses `branch $BR checked out elsewhere`; merge_train's `launch` uses a unique `batch/` branch; `remerge_main.sh` runs `--recarry` against the verdict head). A residual check-to-push window stays on `--branch-only`, reachable only by a second worktree running `checkout -B` on that seat's own fix branch. Not changed here.
- `tools/audit/seat/remerge_main.sh`: `|| true` around app_push, then it prints the PR head GitHub reports. Already read back.
- The remaining hits are self-test fixtures, prose, or other words containing "push". None is a production push.

## Red checks

- `pr-contract` (red at aff55f82): `carry_audit.py check` printed `UNROUTED body item b8a36615 (## Forward-carry)` because the explicit-none line carried trailing prose that `NONE_ITEM` in `tools/audit/carry_audit.py` does not accept. A body defect, not this diff, fixed in the body at 5ffbaaae, where `pr-contract` is green; prepr's `red-history` over the branch's commits at d729496d9 now lists only `nightly-status`. The cheaper detector is `tools/pr/prepr.sh`, which runs the same check locally in seconds and was not run on that body edit; none is to build.
- `nightly-status` (red at 5ffbaaae): it reports the last scheduled `Tests` run on main (`tests/nightly_status.py`) and is not a required context. This diff touches none of what it reads (its scripts, `tests.yml`, `governance.yml`, the plan, `HANDOVER.md`, or a row it did not add), so by `defect-root-cause.md` its red is the orchestrator's on main.

## Forward-carry

n/a: the behaviour change for seats is in `tools/audit/seat/INSTRUMENTS.md`'s roster_edit entry, in this diff.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
