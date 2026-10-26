R10-FLY-OPENPR-ATOMIC (#2719, part of #201), round 10. Part of #2719: the roster lists it in this group's `issues` and not its `fixes`, so this body closes nothing.

`open_pr.sh` stopped trains and left PRs rowless at one seam. Its worktree stayed checked out on the PR branch after every run. A STOPPED or refused open left it there, and the merge train reads a branch checked out elsewhere as busy (train s47, 05:15:57Z). A row push that prepr refused left the row commit unpushed on that branch, and `update_pr.sh` then refused the worktree as unpushed work (#2625, #2629). This change does four things:

- The row push asks for `--row-only` (P53). An open now runs one full prepr, not two, and its row lands seconds after the PR. Before, it landed a prepr later, by which time CI on p1 could report a red the body had never been asked to answer.
- A refused row push resets the worktree to the pushed head and prints `open_pr: ROWLESS: #N is open ...`. `update_pr.sh`'s `ensure_row` then adds the row.
- `pr_release_wt` (`pr_args.sh`) is the run's last act on every exit. `pr_exit_trap` runs it in a new `PR_TIDY` slot, after the reap and while the branch lock is still held. It detaches a worktree whose HEAD is the sha the run pushed. It removes, with its local branch, a worktree whose branch origin never had. It keeps and names (`KEPT <wt> on <br>: <why>`) a worktree that is dirty or whose branch origin holds (P-D, P64, P72). `handoff_push.sh` calls it after its last push and re-attaches with `checkout -B` on its update path.
- `pr_tools_fresh` refuses `STALE CHECKOUT` tools (P-P). `ci_predict.py --rekey-body` re-keys `## Unpinned sites` lines that a main merge only shifted (P70, P125).

## Head

`0ce0c6f8b4110acd3426e97f7d2e17397daefdb2`, on origin/main `ed1c9045e140b14e6a98fdb642942b6fa39aca71` (the dispatch base; 0 commits behind at `date -u` 2026-10-26T07:24:24Z). The shell figures below were taken at `f2f569d4c`. That is this head's parent, and the only change after it is in `tools/pr/ci_predict.py`'s `rekey_self_test`, which now builds its scratch repository through `throwaway_git_init` (prepr's raw-git self-test refused the raw `git init`). The `ci_predict.py` figures and the throwaway-git check were re-taken at this head. Figures that name `334ef2413` (the failing-test-first commit) or the base were taken there.

What the brief asked me to reproduce, and what I could reproduce: the s47 train log and the orchestrator's state worktree live on the orchestrator's machine, and this cloud seat cannot read them. Instead I reproduced the class in the `pr_args.sh` fixture, against the unchanged scripts at `334ef2413`. There a refused open, a TERMed open and a successful open each leave the worktree on its branch. A refused row push strands the row commit, and `update_pr.sh` refuses it with `(unpushed work` (the `mut:rowreset` arm reads exactly that at base). The P184(a) remerge stop (train s43) is R10-TRAIN-OVERLAP-GRADE's, and this change does not touch it.

## Mutation proof

Each `# mut:<name>` line is deleted by `pr_args.sh --self-test` itself, and its arm must then fail. At the head, all 144 checks pass, the mutant arms included:

- `mut:release` (the detach in `pr_release_wt`): `open_pr: a successful open leaves its worktree detached at the pushed head` goes red. Its arm reads `opened PR's worktree still holds its branch`.
- `mut:reltidy` (the worktree removal): the refused open's worktree still holds its branch.
- `mut:reldirty`: the dirty worktree is not named as dirty.
- `mut:relorigin`: the worktree of a branch that origin holds is removed.
- `mut:oprowonly`: the row push runs the full prepr. Its argv has no `--row-only`.
- `mut:rowreset`: the row commit stays unpushed on the branch, `update_pr.sh` refuses `(unpushed work`, and no row reaches origin. This is the #2625 defect.
- `mut:stale`: stale tools open and reach the push.
- `mut:freshpaths`: a `docs/`-only difference refuses.

The other mutations were done by hand, each restored afterwards:

- `handoff_push.sh`, `mut:hprelease` line deleted: `FAIL the open path leaves its worktree detached at the row's pushed head (P64)`.
- `handoff_push.sh`, `checkout -q --force -B "$BR" "origin/$BR"` reverted to `reset -q --hard "origin/$BR"`: `FAIL an update on the detached worktree a previous run left still pushes once`.
- `ci_predict.py`'s `rekey_self_test`, the in-hunk `return None` in `moved_line` deleted (also with the text comparison deleted): `FAIL rekey: a key whose line text changed is kept (null control)`.
- The duplicate-text guard deleted: `FAIL rekey: a key whose text is on two lines at HEAD is kept` and `FAIL rekey: exactly one key is re-keyed`.
- The inventory-kind guard deleted: `FAIL rekey: a key the inventory holds no such kind for at the new line is kept` and `FAIL rekey: exactly one key is re-keyed`.

Failing test first: the arms were committed first as `334ef2413`, with no production change. Run against the unchanged scripts, that commit gives `pr_args self-test: 144 checks, 12 failed`. The 12 FAIL lines:

- the refused open's worktree and branch are left (P72)
- the dirty null control is not named
- the origin-held null control is not named
- `mut:relorigin`
- tools/audit/seat staleness is not refused
- `mut:freshpaths`
- the `HPO_ALLOW_STALE_TOOLS` notice
- update_pr staleness is not refused
- the TERMed open leaves its worktree
- the successful open is not detached
- the row push does not pass `--row-only`
- the rowless repair fails

## Null control

- A successful open whose push is BUSY-raced by `update_pr.sh` still exits 0 with its row on origin. This is the existing `racerun -` arm, unchanged.
- The code push (p1) never passes `--row-only`.
- A refused open keeps its worktree when the worktree is dirty, or when origin holds its branch. In both cases the run names it.
- A `docs/`-only commit on origin/main is no staleness refusal, and the run reaches its push.
- A fresh checkout opens, as the existing null-control arm does.
- An unmoved main rewrites no key: `--rekey-body` from HEAD over a body naming `away.py:175 GUARD_OFF` printed `REKEY: 0 re-keyed, 0 kept` and left the file unchanged. A key outside `## Unpinned sites` is never touched.
- `update_pr.sh`'s own worktree still detaches through its lock holder (the existing `mut:detach` arm, green).

## Figures

- `bash tools/audit/seat/pr_args.sh --self-test` at base `ed1c9045`: 125 checks, 0 failed. At `334ef2413`: 144 checks, 12 failed (listed above). At the head: 144 checks, 0 failed. The +19 checks are this change's arms, counted as the difference between the two tallies.
- `bash tools/audit/seat/handoff_push.sh --self-test` at the head: 6 checks, 0 failed (3 at base: the 3 new arms are the open-path detach, the update-path detach and the re-attach on a detached worktree).
- `python3 -I tools/pr/ci_predict.py --self-test` at the head: `ci_predict self-test: 0 failed`, including its 6 `rekey:` rows.
- `python3 -I tests/throwaway_git.py --check` at the head: `0 raw git init or clone site(s) refused`. At `f2f569d4c` it refused 1, `tools/pr/ci_predict.py` (the rekey self-test's raw init, fixed in `0ce0c6f8b`).
- Rekey on a real production file: in a scratch worktree at the head, I committed one line inserted at the top of `custom_components/heatpump_optimizer/away.py`. Then `python3 tools/pr/ci_predict.py --rekey-body <body> --from HEAD~1` printed `REKEY custom_components/heatpump_optimizer/away.py:175 GUARD_OFF -> custom_components/heatpump_optimizer/away.py:176 GUARD_OFF` and `REKEY KEPT ...away.py:176 GUARD_OFF: its text is on 4 lines at HEAD`, then wrote one `## Head` note. The null control, from HEAD with no move, printed `REKEY: 0 re-keyed, 0 kept`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. The 5 changed files are in no script's measured closure. `tests/run.sh`'s run_always lines ran green: env_drift claims-only, closure selftest, layout, harness_headers.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `bash tools/pr/prepr.sh <this body>` at the head refuses one step, `closures`: `failed while being recorded: tests/entities.py (exit 1)`. `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `2 of 2451 ENTITY CHECKS FAILED` at this head and identically at base `ed1c9045` in a detached worktree of origin/main in this container. The same two rows fail in both runs: `gate-sweep.yml: on CI's completion ...` and `graders-head-copy's delivery_status step ...`. Both drive workflow step scripts that this diff does not touch, so the red belongs to this cloud container's environment and not to the diff. CI's own run decides the check. Every other prepr step passed.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: no closures, fast, wave-script or instrument red predicted against `ed1c9045e140`, and no unpinned site added (the diff is `tools/` only).
- Carry 6's gate, measured with real git in a scratch repo: a worktree detached at the branch tip reads `HEAD=4f6f27f tip=4f6f27f`, which passes app_push.sh's committed-tip comparison. After a commit planted on the detached HEAD, it reads `HEAD=06663dd tip=4f6f27f`: refused.

### The class's seams

The rule that enumerates them: `bash tools/audit/seat/pr_args.sh --pushers`. It is the census of every tracked `tools/` script naming `app_push.sh`, and the seams it returns are the pushers. Its `runner` entries that leave a PR branch checked out in a worktree of their own:

- `open_pr.sh`: closed in this diff (`pr_release_wt` via `PR_TIDY`).
- `handoff_push.sh`: closed in this diff (after its last push).
- `update_pr.sh`: already guarded. Its lock holder detaches `$WT` (`mut:detach`), and its `OWN` sweep detaches clean sibling worktrees.
- `remerge_main.sh`: runs in a caller's detached worktree (its self-test fixture adds it `--detach`). It is the merge train's, and no branch is held.
- `app_push.sh`: pushes from the caller's worktree and creates none; app_push.sh is untouched (carry 4).
- `merge_train.py` (runner-py): owns `--free-holders` for the recarry. It is unchanged here.

## Carries

1. Atomic open (#2625, #2629): **implemented.** The row push (p2) is `--row-only`, so it lands seconds after p1, before CI on p1 can report a red. A refused p2 resets to the pushed head, prints ROWLESS and releases the worktree. Control: the `rowless` arm. Its p2 is refused, and then `update_pr.sh fix/r -` exits 0 with `dev/programme/delivery/5.md` on origin and no stranded worktree. Under `mut:rowreset` it is refused as unpushed work (the defect).
2. P-D, the exit trap detaches on success and on STOPPED: **implemented** as `PR_TIDY`, run after the reap and under the branch lock. The holder is let go only afterwards. Controls: the successful-open and TERMed-open arms.
3. P-P, `pr_tools_fresh`: **implemented** in `pr_args.sh` as its own function, called after each script's fetch of origin/main. Its rows cover stale (refuse), docs-only (pass) and fresh (pass), plus the escape notice and update_pr's refusal. Mutants: `mut:freshpaths` and `mut:stale`. The paths are top-relative (`:/`). The first cut used bare paths under `git -C <tools dir>`, which read below that directory and counted 0. Its first run caught that. Grepping main for R10-FLY-RELAY-REVIEW-FF's tick_loop path-scoped count finds no such count yet, so this is the first definition.
4. P53, p2 passes `--row-only`: **implemented.** The argv row and `mut:oprowonly` cover it. app_push.sh is untouched.
5. P64, a shared detach after the last push: **implemented** for `open_pr.sh` and `handoff_push.sh`. `handoff_push.sh`'s update path now re-attaches the branch with `checkout -q --force -B`, because the old `reset --hard` would have moved a detached HEAD and left the branch behind. `update_pr.sh` is already guarded by its lock holder's detach, and a second detach would duplicate it. Measured: open_pr's worktree (`$HPO_STATE_DIR/pr/<topic>/wt`) is inside update_pr's sweep, and handoff_push's (`$HPO_WT_ROOT/fix-<topic>`) is outside it. Each pushes twice in one worktree on the open path. Control: the dirty and origin-held arms stay on their branch.
6. A detached HEAD passes the committed-tip gate: **addressed by placement**. The detach is the run's last act and runs from the exit trap, so no push of the same run can follow it. The planted-commit refusal is measured under `## Figures`. No app_push.sh self-test row was added, because that self-test stubs git, and carry 4 asks for app_push.sh to be left untouched.
7. P70, `ci_predict.py --rekey-body BODY --from <code-sha>`: **implemented** and called by both scripts after their main merge, with one `## Head` note. Its `rekey:` rows cover a moved key (re-keyed), changed text (kept), duplicate text (kept), a kind the inventory lacks at the new line (kept) and a key outside the section (untouched). A site the body never listed is never written, so 7d still refuses it. Mutants: the hand mutations above.
8. P71, defaulting the Closes list to the group's `fixes`: **dismissed: the trailing issue arguments decide nothing since #2838.** `app_push.sh` forwards them only to `prepr.sh`, whose `preflight_body` ignores and names them and derives the intended list as pr-contract does. Defaulting them changes no push and no refusal. The Closes list is the body's own text, and this group's own roster entry (`fixes: []`, `issues: [2719]`) shows why a default would only print a list nothing reads.
9. P72, a REFUSE or STOPPED exit removes a clean, origin-absent worktree and its branch: **implemented.** The null controls (an uncommitted file; a branch on origin) are kept and named. Mutants: `mut:reltidy`, `mut:reldirty` and `mut:relorigin`.
10. P125, re-key line-shifted sites after the main merge: **implemented** by the same `--rekey-body` as carry 7. Carries 7 and 10 describe one mechanism, and building it twice would duplicate it. prepr inside the push is the one rerun of 7d.
11. V64, auto-open on handoff in `cloud_relay.sh`: **not built here.** The carry says it is built on this group's atomic open, so it can only be built once that is merged. It also edits the handoff arm of `cloud_relay.sh`, whose update arm is R10-FLOW-BODY-ONLY's. Its controls (one PR per topic, the second concurrent pass exits 75, handoff-to-open latency before and after) need this head as their "before". Carry: R10-FLOW-BODY-ONLY

## Red checks

none

## Forward-carry

- Auto-open on handoff (carry 11, V64), built on `open_pr.sh` at this head: `cloud_relay.sh`'s handoff arm runs `open_pr.sh` for a `handoff-no-pr` topic with a body ref, under `pr_branch_lock`. Carry: R10-FLOW-BODY-ONLY

## Friction

none
