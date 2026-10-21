`roster_edit.py --push` could print `pushed <branch> at <sha>` with rc 0 for a commit that never reached origin. This change commits the edit in a detached worktree and pushes that commit as `<sha>:refs/heads/<branch>`. When a rival has moved the branch, the push is rejected; the tool then re-fetches, re-applies the op on the new tip, re-lints and pushes again, up to `PUSH_ATTEMPTS` times. After that it refuses with rc 2. It never force-pushes.

**The suspected mechanism was wrong.** `run()` does check the exit status (`if r.returncode != 0: raise Refuse(...)`). With two separate clones, the losing push is rejected loudly with rc 2 (the `separate` arm below). The real cause is that the roster branch was a *named local branch*, and every worktree of one repository shares its local branches:

1. Seat C ran the 2026-10-21 carry loop from one repository's worktree `wt-5`. It ran `checkout -B handoff/audit-r10-roster` and committed b622ec9f1.
2. While C's lint gate ran, the orchestrator ran `set-stage R10-ADVISOR` from orch-wt, a worktree of the same repository. Its own `checkout -B handoff/audit-r10-roster` reset that shared branch to af5daaa5b. Git 2.38 lets `checkout -B` move a branch that another worktree has checked out (measured in a scratch repository: `rc=0`, branch moved). The orchestrator then committed 2f37a1cb6 on it.
3. C ran `git push origin handoff/audit-r10-roster`, which pushes whatever the shared ref points at. That was not b622ec9f1. The push exited 0, and the tool printed the `head` it had captured before the lint: `pushed handoff/audit-r10-roster at b622ec9f1...`.

GitHub's activity log for the branch has no push of b622ec9f1 and no force push. The entry `af5daaa5b -> 2f37a1cb6` at 09:58:36Z is the only move from af5daaa5b (`gh api repos/tvofi/heatpump_optimizer/activity -f ref=refs/heads/handoff/audit-r10-roster`). C's try 2 failed with `wt-5 has uncommitted changes`, which this cause also explains: wt-5's HEAD followed the moved branch, while its index still held b622ec9f1's tree.

At the baseline, the shared branch scrambles more than the push. The self-test and harness runs below also show a run that exits rc 2 although its edit landed, and a commit whose message says it is one seat's edit but whose content is the other seat's.

**The fix and the alternatives.**
- Taken: no local branch at all. The worktree is detached, and the push names the commit the run made and linted. A rejected push is classified by re-fetching. If `origin/<branch>` moved off this run's base, that is a race, and the run re-applies its op on the new tip (`apply_op` is now one function, so each attempt runs the same op). If origin did not move, the run refuses at once and prints git's own message.
- Rejected: keep `checkout -B` and push by sha only. That turns the false success into a loud refusal, but the shared branch can still be reset under a run *before* its commit. `commit -am` then builds the run's tree on the rival's parent and silently reverts the rival's edit in a fast-forward push. Mutant M5 below keeps a named branch while still pushing by sha, and four checks still fail.
- Rejected: `--force-with-lease`. The brief forbids forcing, and a lease only turns a lost race into a refusal.
- Rejected: a lock file around the edit. A lock covers only seats that share one machine and one repository, while the race is on the remote ref. The remote's own compare-and-swap on a plain push is the lock.

The reuse guard follows the new model. A `--worktree` whose HEAD is on no `refs/remotes/origin/*` ref, which means a lint-refused or unpushed edit, is refused rather than dropped. The old guard keyed on a local branch, which no longer exists. The only exception is the run's own commit that lost a race. The self-test's lint-refused and stale-lint arms now use their own worktrees, and a new check pins the refusal.

No issue is attached, so this body carries no closing keyword. The orchestrator appends the group R10-ROSTER-PUSH-RACE.

## Head

5091d7b865f7208580847ead995d65a7fe414cbe, at merge base 6961f06637964001a2ed544e495ea0312eeefa37. At 2026-10-21T13:01Z origin/main is at dbea71db76f1. Since the base, main has touched only one of this diff's files: `tools/audit/seat/INSTRUMENTS.md`, in a91a9a185 and 5d477d6e9, whose hunks are the WIP-cap entries and not the roster_edit entry. `git merge-tree --write-tree HEAD origin/main` merges without a conflict. The head is not merged with main: the orchestrator merges it.

## Mutation proof

Failing test first: commit e19bda54f adds the race checks and only the `PUSH_ATTEMPTS` constant. On the baseline code the self-test reads `roster_edit self-test: 82 checks, 7 failed` (the old tally counted each failure twice; it was 75 checks), including:
- `FAIL race: the loser's edit reaches origin (got: solo-2)`
- `FAIL race: the sha reported pushed is origin's tip (got: (['f8acd469b3c2...'], '7af32704b090...'))`: the 2026-10-21 shape, a sha printed as pushed that origin does not hold
- `FAIL a non-race push failure refuses at once ... has uncommitted changes; refusing to reuse it`: the shape of C's try 2

Each mutant was applied at 35cc73a03 (roster_edit.py is byte-identical at the head: `git diff --quiet 35cc73a03 5091d7b86 -- tools/audit/seat/roster_edit.py` exits 0) by an exact one-site replacement and reverted with `git checkout -- tools/audit/seat/roster_edit.py`. Each run is `python3 tools/audit/seat/roster_edit.py --self-test`:
- M1, race never retried (`if not tip or tip == base_sha:` -> `if True:`): 7 failed, e.g. `FAIL race: rc 0 after re-applying on the rival's tip`, `FAIL race: the loser's edit reaches origin`.
- M2, own lost commit not discardable (`if old != discard and not run(` -> `if not run(`): 7 failed, e.g. `FAIL race: the sha reported pushed is origin's tip`.
- M3, bound off by one (`range(1, PUSH_ATTEMPTS + 1)` -> `+ 2`): 2 failed: `FAIL race on every attempt: refused (rc 2), said loudly`, `FAIL race on every attempt: origin holds every rival, not this edit`.
- M4, reuse guard off (`raise Refuse(` -> `print(` on the unpushed-HEAD guard): 1 failed: `FAIL a worktree holding an unpushed edit is not reused`.
- M5, named branch back (`checkout -q --detach base_sha` -> `checkout -q -B branch base_sha`): 4 failed, e.g. `FAIL race on every attempt: bounded at PUSH_ATTEMPTS rivals (got: ['rival carry 2', 'rival carry 3'])`.

## Null control

- In the self-test, the null control runs before any race arm. A solo edit gives `solo edit: rc 0, one push, no race said` and `solo edit: exactly one commit added, the one reported`, and both pass at the head. The unmodified head (M0) reads `roster_edit self-test: 76 checks, 0 failed`.
- In the harness, the `solo` arm runs one edit with no rival. Base and head agree on every run: `silent_losses=0 refused_edits=0 pushes=1`, so the fix adds no push and no retry when nothing races.
- In the harness, the `separate` arm uses two clones. At the base it never loses an edit silently: it refuses loudly (`refused_edits=1`) on all 10 runs. That is why the mechanism the brief suspected (a swallowed exit status) does not explain the field case, and the shared-checkout arm does.

## Figures

The harness is `bash dev/audit/harnesses/r10_roster_push_race.sh <tree> <shared|separate|solo>` with `PYTHON` set to the seat venv python. `<tree>` is either the base, a `git archive` export of 6961f0663's `tools` and `tests` (an earlier detached base worktree was collected mid-run), or the head worktree at 5091d7b86. It prints one summary line per run. The counts below are tallied with `sort | uniq -c` over 10 runs per race arm and 3 per solo arm. `silent_losses` counts runs with rc 0 whose edit is not in origin's roster. `refused_edits` counts runs with rc not 0. `pushes` counts commits the branch gained.
- base, shared: 6 of 10 runs `silent_losses=1`. 3 of those 6 also have `false_reports=1`: a run printed `pushed ... at <sha>` for a sha that origin's tip does not contain, which is the 2026-10-21 shape. One of the 3 had both runs exit rc 0. In the other 4 runs one edit was refused loudly, and in 1 of those 4 both edits landed anyway, while one run had been told it failed (`refused_edits=1 pushes=2`).
- head, shared: 10 of 10 `silent_losses=0 false_reports=0 refused_edits=0 pushes=2`.
- base, separate: 10 of 10 `silent_losses=0 false_reports=0 refused_edits=1 pushes=1`.
- head, separate: 10 of 10 `silent_losses=0 false_reports=0 refused_edits=0 pushes=2`.
- solo, both trees: 3 of 3 `silent_losses=0 false_reports=0 refused_edits=0 pushes=1`.
- An earlier set, taken with the harness before its throwaway-git rewrite, also showed a fourth shape: both runs exit 0, the branch gains two commits, and one edit is still missing. The second commit was built on the rival's parent but carried the pre-rival tree, so it reverted the rival's edit in a fast-forward push. That set is not counted above.
- `python3 tools/audit/seat/roster_edit.py --self-test`: `roster_edit self-test: 76 checks, 0 failed` at the head. The tally now prints `passed`, which already counted every check; the old `passed + len(failed)` counted each failure twice. CI's grep `^roster_edit self-test: [1-9][0-9]* checks, 0 failed$` still matches.
- `python3 tests/closure.py select --diff 6961f06637964001a2ed544e495ea0312eeefa37 --workdir <dir>` at the head: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, naming `tests/entities.py`, which printed `ALL 2375 ENTITY CHECKS PASSED`.
- The `run_always` lines and the step-5 gate, each at the head with `PYTHONPATH=tests/hastub`: `tests/env_drift.py --claims-only 6961f066...` printed `claims hygiene: ... ok`; `tests/closure.py selftest` printed `ALL 124 closure shrink pins PASSED`; `tests/layout.py` exited 0; `tests/harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED`; `tests/structure.py` printed `STRUCTURE RATCHET PASSED`; `tests/entities.py` printed `ALL 2375 ENTITY CHECKS PASSED`.
- `tests/layout.py` exited 1 at 35cc73a03, with `new-reference: dev/audit/harnesses/r10_roster_push_race.sh cites retired path .claude/workflows/brief_lint.mjs`. 85f9f827f points the harness's lint stub at `tools/policy/brief_lint.mjs`. The control on the same command: the base tree exits 0.
- prepr at 85f9f827f refused twice. First, `throwaway git` refused the harness's bare `git init`; bed7018dc builds its repositories with `tests/throwaway_git.sh`, and the figures above were re-taken after that change. Second, `ci predict` reported `closures INERT READS tests/harness_headers.py: dev/audit/harnesses/r10_roster_push_race.sh`; `python3 tools/pr/ci_predict.py --base origin/main --apply-inert` wrote that one `tests/closures.json` entry at e6c9580c3. The scope at the head is now `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, with `RUN tests/entities.py`. Then 46a043272 sources the helper from the repository root, after `tests/harness_headers.py` refused the `dirname`/`..` walk as a depth seam, and 5091d7b86 prints the setup edit's own output on failure.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused, 0 stale allow entries at HEAD`.
- `python3 tools/audit/seat/ref_privacy.py --self-test`: `66 checks, 0 failed`.

The class search finds no other pusher that reports success on a push it did not make. The rule: `git grep -nE '"push"|git( -C [^ ]+)? push\b'` over `tools .claude/workflows .claude/hooks`, then the lines that reset a branch with `-B`, plus `push.*(\|\| *true|check=False)`. Each returned production site and its disposition:
- `tools/audit/seat/body_push.sh` (`$C:refs/heads/$REF`), `tools/audit/seat/bus.sh:266`, `tools/audit/seat/state_docs.py` and `tools/pr/merge_main_bot.py` all push a sha. Their exit status is checked: by `set -e`, `|| REFUSE`, `run()`, and a `skip-push-refused` line that is never counted as pushed. Already guarded.
- `tools/release/stamp.py` `push_via`: `sh(..., check=True)` raises, and the push is `HEAD:main` from the stamp's own checkout. Already guarded.
- `tools/audit/seat/wt_sync.sh`: a deliberate force push of a sha to a per-slug `wip-sync/` ref, gated by `&& echo`. Not this class.
- `tools/pr/push.sh`: pushes a branch by name, rc checked. Retired by decision 0011.
- `tools/pr/app_push.sh`: pushes `"$br"` by name and reports a `$head` it captured earlier. That is the same shape as this defect, but it is guarded. It refuses unless `HEAD == refs/heads/$br` just before minting, and on the pull-request path it reads the PR head back against `$head`. Its callers keep the branch to one worktree: `update_pr.sh` refuses `branch $BR checked out elsewhere`, merge_train's `launch` uses a unique `batch/` branch per train, and `remerge_main.sh` runs `--recarry` against the verdict head. A residual window stays between the check and the push on `--branch-only`. A second worktree of the same repository would have to `checkout -B` that seat's own fix branch inside it. Not changed here.
- `tools/audit/seat/remerge_main.sh:25`: `|| true` around app_push. It relays the `RECARRY|REFUSE|PUSHED` lines and then prints the PR head that GitHub reports, so its rc does not report a push by itself. Already read back.
- The remaining hits are self-test fixtures, prose, or other words containing "push" (`pushState`, event names). None is a production push.

## Red checks

none at handoff: no pull request is open yet.

## Forward-carry

none. The behaviour change for seats is in `tools/audit/seat/INSTRUMENTS.md`'s roster_edit entry, which is in this diff. Several seats may now run roster edits from one `--checkout` at the same time. Making a fresh `--worktree` per edit stays the safe habit, because a worktree that holds an unpushed edit is refused.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
