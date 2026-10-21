# Summary

`open_pr.sh` opens a PR with its first push, commits the PR's own delivery row, and pushes a second time. On 2026-10-21 that second push was refused on #2547 and #2548 (and #2549 is left without a row too; repairing the three rows is the orchestrator's follow-up, by rerunning `update_pr.sh` on each, which adds the row when the head lacks it), so `bus.sh dispatch` refused their reviewers. The refusal is `app_push.sh`'s head check: `worktree HEAD (41fd99b0...) is not the committed tip of 'fix/r10-replay-cap' (daac94b4...)`.

**Cause (measured with git, not the error text).** The error text suggests a stale local branch. The reflogs and lock files say the writer of that state was `update_pr.sh`:

- #2548: the PR worktree's reflog has `commit: record: the delivery row for #2548` at 12:15:36 on the branch, then `checkout: moving from fix/r10-replay-cap to HEAD` (a detach) at 12:26:31. `upd-fix-r10-replay-cap.lock` was written at 12:26:29, two seconds before.
- #2547: row commit 11:58:53, detach 12:05:21, `upd-fix-r10-tick-owed-level.lock` written 12:05:19.
- The detach is `update_pr.sh`'s line that detaches every clean worktree under the state root holding the branch, then `git worktree add -B <branch> <its own worktree> origin/<branch>`, which moves the local branch to origin's head (or to the update's own row commit, `90bab078d` on #2547). The PR worktree's HEAD is then a detached commit that is not the branch tip, so the row's push is refused.
- `open_pr.sh` held no lock; `update_pr.sh` took `upd-<branch>.lock` for its own worktree only. `cloud_relay.sh` runs `update_pr.sh` when a handoff is ahead of its PR, which is how it ran minutes after the PR opened.
- #2549 shows no detach (its worktree is on the branch with the row commit as tip); its `p2.log` stops in the middle of prepr, so its original stop is not established here. This fix addresses the two instances whose evidence names the cause.

**Fix (two layers).**
1. `open_pr.sh` takes the same per-branch lock as `update_pr.sh` (`upd-<branch>.lock`), from before its worktree until it returns, so an `update_pr.sh` that starts in between exits 75 BUSY and changes nothing (`cloud_relay.sh` already retries 75 on its next pass). The lock code moved out of `update_pr.sh` into `pr_args.sh`'s `pr_branch_lock` (both scripts source it), so there is one copy.
2. `update_pr.sh` no longer detaches a worktree whose HEAD origin lacks: it refuses, naming the worktree. Before, the detach plus `-B` silently dropped any unpushed commit a sibling instrument held. A clean worktree whose HEAD is on origin is detached as before.
3. `ref_privacy.py`'s `PUSHERS` names `tools/audit/seat/pr_args.sh` as a `fixture`: its self-test's stub `app_push.sh` pushes only into the self-test's scratch origin.

This pass adds no code. Its delta over the reviewed head `085a4caf` is one merge of `origin/main` `3688cf259`; the authored diff is unchanged. The class sweep below now dispositions every line its rule returns, `tools/audit/seat/ci_predict_replay.sh` included, and every figure is re-taken at the head named below.

No `VERSION`, claim file or budget is touched.

## Head

`2108fcb09ef16a53119dedb8b731bd89f0fea0ad` merges the authored code head `e958d53bc15002f4fb64a7dca93bd018235f9dc1` and then merges origin/main `22615537a` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`d901186ff4073a104b999ad8318875a422ebf8e3`, the code head pushed to `handoff/r10-openpr-row-push`: PR #2560's head `085a4cafa84022120460fd23701a21883321536f` merged with `origin/main` `3688cf25977ca71b4406be942df9592577d9b42e`, clean, no resolution. Every figure below was taken at a tree byte-identical to it (`git rev-parse d901186ff^{tree}` equals the tree the figures ran on), at 2026-10-21T12:55Z with `origin/main` at `3688cf259`.

## Mutation proof

The self-test (`bash tools/audit/seat/open_pr.sh --self-test`, which runs `pr_args.sh`'s after `delivery_row.sh`'s) builds a scratch origin and a stub `app_push.sh` that makes the same head check the real one makes. Its race arm holds `open_pr.sh` inside its second push, starts `update_pr.sh` on the same branch, then lets the push go. Each new arm sits beside a mutant that deletes its predicate line (`# mut:<name>`) and must fail it; the self-test runs the mutants itself, so its tally at the head covers them:

- `open_pr: an update_pr.sh on its branch during its second push is BUSY, and the PR's row reaches origin`.
- `mutant mut:oplock`: with `open_pr.sh`'s lock line deleted `update_pr.sh` is no longer BUSY, but the row still reaches origin because layer 2 refuses the detach.
- `mutants mut:oplock and mut:unpushed (both deleted)`: the stub prints `app_push: REFUSE: worktree HEAD is not the committed tip of 'fix/r'`, `open_pr` fails with `the push failed`, and the row is not on origin. This is the production defect, reproduced.
- `update_pr: a worktree holding the branch with a commit origin lacks is refused and stays on its branch`, and `mutant mut:unpushed` (the worktree is detached under its commit).
- The existing lock arms (`mut:lock`, `mut:unlock`, `mut:watch`, `mut:stop`) still pass; their lines now live in `pr_branch_lock`.

Registry entry, re-taken at the head: deleting `PUSHERS`' two `pr_args.sh` lines (`ref_privacy.py`, the `"tools/audit/seat/pr_args.sh": ("fixture", ...)` entry) makes `python3 -I tools/audit/seat/ref_privacy.py --check` exit 1 with `ref_privacy: REFUSE tools/audit/seat/pr_args.sh:353: a push site in a file PUSHERS does not name` and `1 refused`; restored, `git diff --quiet` passes and it prints `0 refused`. No rule, scope or pattern changed; only the file is named with its reason, as `app_approve.sh` and `r9_rc_bus_fetchhead.sh` are.

## Null control

`origin/main` `3688cf259` in a detached worktree with only the head's `pr_args.sh` copied over it, so the new arms run against the old scripts: `pr_args self-test: 62 checks, 4 failed`. The four `FAIL` lines: `update_pr: a branch whose update is in flight refuses BUSY (75) and leaves that run's worktree in place` (its text changed), `open_pr: an update_pr.sh on its branch during its second push is BUSY, and the PR's row reaches origin`, `mutant mut:oplock (its line deleted): update_pr.sh takes the branch (not BUSY); the unpushed-work refusal alone keeps the row`, `update_pr: a worktree holding the branch with a commit origin lacks is refused and stays on its branch`. At the head: `pr_args self-test: 62 checks, 0 failed`.

`ci_predict_replay.sh` probe (scratch, below): its own two worktree lines, lifted verbatim, run beside a sibling worktree `W` holding branch `b` with a commit origin lacks and a dirty file, leave every ref, `W`'s branch and `W`'s files unchanged. The null control aims the same `worktree remove --force` at `W` itself and the probe reports `CHANGED (W removed: yes ...)`, so the probe can see the change it reports absent.

## Figures

- `bash tools/audit/seat/open_pr.sh --self-test` at the head: rc 0, `delivery_row self-test: 5 checks, 0 failed`, `pr_args self-test: 62 checks, 0 failed`. The same command in a detached worktree of `origin/main` `3688cf259`: `pr_args self-test: 56 checks, 0 failed` (the 6 added arms are this diff's).
- `python3 -I tools/audit/seat/ref_privacy.py --check` at the head: rc 0, `ref_privacy --check at HEAD: 19 file(s) with a push site, 9 guarded, 113 line(s) added since 3688cf25977c judged, 0 refused` (the "added since" count is measured from the merge base, so it moves with `origin/main`). `python3 -I tools/audit/seat/ref_privacy.py --self-test`: `ref_privacy self-test: 66 checks, 0 failed`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD`: `Architecture score: dS +0.0000 NULL`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`; `scope.run` names `tests/entities.py`. Run under a Python 3.13 venv built from `tests/requirements-ci.txt` with `PYTHONPATH=tests/hastub` (the seat venv recipe `tools/audit/seat/seat_venv.sh` refused here: `No download found for request: cpython-3.14.7-linux-x86_64-gnu`): `ALL 2375 ENTITY CHECKS PASSED`. `tests/run.sh`'s `run_always` lines: `tests/env_drift.py --claims-only 3688cf259...` `claims hygiene: ... ok`; `tests/closure.py selftest` `ALL 124 closure shrink pins PASSED`; `tests/layout.py` `layout self-test: ok`; `tests/harness_headers.py` `ALL 109 HARNESS HEADER CHECKS PASSED`.
- Class search. Rule: every site that detaches, hard-resets, `-B`-recreates or force-removes a worktree or deletes a branch in the seat and PR instruments: `grep -nE "checkout -q --detach|reset -q --hard|worktree add -q -B|worktree remove --force|branch -D" tools/audit/seat/*.sh tools/audit/seat/*.py tools/pr/*.sh`. At the head it returns 43 lines (`ci_predict_replay.sh` 1, `cloud_relay.sh` 2, `handoff_push.sh` 2, `pr_args.sh` 6, `remerge_main.sh` 1, `update_pr.sh` 3, `app_approve.sh` 24, `app_push.sh` 1, `prepr.sh` 3). Dispositions, every line:
  - `update_pr.sh:40` (detach of every clean worktree holding the branch) and `:44` (`worktree add -q -B`): closed in this diff (the lock, and the refusal of a worktree whose HEAD origin lacks).
  - `update_pr.sh:43` (`worktree remove --force $WT`): `$WT` is `update_pr.sh`'s own `upd-<branch>` worktree, removed under the branch lock this diff makes `open_pr.sh` take too, after `:42` refuses when the branch is checked out anywhere else. Already guarded.
  - `ci_predict_replay.sh:47` (`worktree remove --force "$wt"`): a self-created scratch worktree, outside the class. `$wt` is `$scratch/wt-$sha` (`:38`), where `$scratch` is the directory its caller names and `$sha` a full 40-hex PR commit sha from the API; `:39` adds it with `worktree add -q --detach`, so it holds no branch, and nothing in it commits (`ci_predict.py` only predicts). No other instrument writes a `wt-<40-hex sha>` path (`grep -rn 'wt-\$\|/wt-' tools dev .claude` finds only `dev/audit/rounds/round10/intake/quiet.sh`'s `$OUT/wt-$id`, where `$id` is a mutant id like `M35`, and two prose mentions). `git worktree remove` moves no ref, so it cannot leave a worktree HEAD off its branch tip, the defect's state. Probe: the null control above (refs, `W`'s branch and files unchanged; aimed at `W`, `W` is removed and branch `b` still carries its commit `unpushed`).
  - `handoff_push.sh:63` (`reset --hard origin/$BR`) and `:79` (`worktree remove --force "$WT"; branch -D "$BR"`): its worktree is `${HPO_WT_ROOT:-$(dirname "$M")}/fix-<topic>`, outside `$HPO_STATE_DIR/pr`, so `update_pr.sh`'s detach (filtered to `^$P/`) never reaches it, and it resets or removes only its own worktree and branch (`:79` runs on a refused earlier attempt with no PR). Legacy path (`INSTRUMENTS.md`: new work uses `open_pr.sh`/`update_pr.sh`); not the defect.
  - `remerge_main.sh:17` (`reset --hard origin/$BR` in the worktree the merge train passes it): the train owns that worktree and holds no unpushed work in it by contract (its header: the worktree may be detached). Not the defect.
  - `cloud_relay.sh:395`, `:400`: inside `self_test()` (`:245`-`:440`), on its scratch repositories. Fixture.
  - `pr_args.sh:116`, `:281`, `:286`, `:328`, `:382`, `:406`: inside `pr_args_self_test()` (`:102`-`:430`), on its `mktemp -d` origin and worktrees. Fixture.
  - `app_approve.sh:591`, `:597`-`:601`, `:606`, `:616`, `:618`, `:620`, `:625`, `:657`, `:659`, `:663`, `:667`, `:673`, `:686`, `:688`, `:690`, `:692`, `:698`, `:1092`, `:1100`, `:1118` (24 lines): past `:488`, where a call without `--self-test` runs `approve` and exits, so only the self-test reaches them, in its temp clone `$W/clone` and `$W/reloc`. Fixture.
  - `app_push.sh:827`: past `:464`'s same split, in the self-test's `$R/wt`. Fixture.
  - `prepr.sh:1877`, `:1984`, `:2098`: inside the `--self-test` block (`:1282`-`:2484`), each in a `throwaway_git_clone` under its own `mktemp -d`. Fixture.

  An un-dispositioned line would be an open seam; none is.

## Red checks

- `instrument-self-tests` (step "Refuse a push that names the host, and an unregistered pusher"), red on an earlier head of this PR: the race arm's stub `app_push.sh` heredoc in `pr_args.sh` is a push site `ref_privacy --check` did not know. Cheaper detector: `python3 -I tools/audit/seat/ref_privacy.py --check`, seconds, run before the push. `tools/pr/prepr.sh` does not run it (`grep -n ref_privacy tools/pr/prepr.sh` finds nothing), and a fixer has no rule naming it, so a diff that adds `git push` text under `tools/` is caught only by CI. Standing cost of wiring it into prepr: one more step on every run; not built here, since the process moratorium (decision 0012) bars new checks and the class has one instance. Named for the root-cause seat if it recurs. Fixed by the registry entry.
- `pr-contract` (`carry_audit.py check --body`: two `## Forward-carry` items unrouted), red on an earlier head: the two items were notes, not findings for a later stage. Cheaper detector: `python3 tools/audit/carry_audit.py check --body <body>`, instant; `prepr.sh` does not run it either (`grep -n carry_audit tools/pr/prepr.sh` finds nothing). Fixed: the rows follow-up moved into the Summary, the other item dropped, and `## Forward-carry` is `none`.
- `nightly-status` grades `main`, not this diff.

## Forward-carry

none

## Friction

none

