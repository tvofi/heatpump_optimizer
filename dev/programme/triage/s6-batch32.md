# Proposal triage, session s6, batch 32 (P184-)

Proposals from the s6 `proposals.md`. Numbering continues after `s6-batch31.md` (P176-P183). This batch holds 8-10 entries and merges only through the train queue (tvofi, 2026-10-25). Facts read at origin/main c9cbe6b45.

A roster op citing an ACCEPT below resolves only once this file is on the roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P184: a conflicted recarry leaves its worktree holding the branch, and `--free-holders` refuses a holder that is only behind (S6-V104)
Verdict: ACCEPT narrowed -> R10-TRAIN-OVERLAP-GRADE (queued, M; it owns the train's admission in `tools/audit/seat/merge_train.py`, with P129 and P164). The files gain `tools/audit/seat/remerge_main.sh`. The filing's candidate countermeasure is REJECTED. Freeing any clean worktree under a prior train's `train/s*/wt/*` keys on a path pattern, not on the cause. `--free-holders` already frees a clean holder anywhere: s40's own log shows it freeing the relay's update worktree for this same branch. The two causes are below.
Source: s6 `proposals.md` `## V104` (merge seat w16, 2026-10-25, slip).
Instances: one. The train state logs (`train/s40/train.log` and `train/s41/train.log` in the orchestrator's state directory) show it in order:
1. s40 recarried #2753 (branch `fix/r10-thermal-power-option-pr`), and the merge of main conflicted: `SKIP #2753 recarry: main does not merge without a resolution`.
2. At s40's close, `release_worktrees` (`merge_train.py:1805-1816`, never forced) logged `NOT released .../s40/wt/2753 (rc=128: ... contains modified or untracked files)`. `remerge_main.sh:21` runs `git merge --no-edit -q origin/main` and on failure prints `MERGE CONFLICT` and exits 1 without `git merge --abort`. So the train's own worktree kept the conflicted merge and kept holding the branch.
3. The fixer then pushed the resolution, and origin moved to 8a133f39 (`ci: merge main`).
4. s41 ran with `--free-holders`, and the holder's status was clean by then. `freeable` (`merge_train.py:996-1010`) still refused it: `not freed: its HEAD 45d08312 is not origin/fix/r10-thermal-power-option-pr 8a133f39 (unpushed work)`.
5. 45d08312 is an ancestor of 8a133f39 (`git merge-base --is-ancestor`), so nothing was unpushed. The holder was behind the remote, and the equality test reads behind as unpushed.
6. The train does not retry a skipped entry within a batch, so critical-path #2753 lost a whole batch.

Cost: XS + XS.
- (a) `remerge_main.sh`: on a failed merge, run `git -C "$W" merge --abort`, falling back to `git reset -q --hard` to the branch's tip, before exiting 1. The train's own worktree is then clean, and `release_worktrees` removes it at the train's close.
- (b) `freeable`: a clean holder whose HEAD is an ancestor of `origin/<br>` is freeable. Equal stays freeable. A HEAD that is not an ancestor still refuses, now with the reason "has commits origin does not". Nothing is forced in either case.

Binding: both are the train's own seam. Each fix closes a separate arm of the same loss, and neither widens what is freed beyond "nothing is lost". Closure saving: about 0.5 h. Basis: one critical-path batch, about 0.5 h, avoided per recurrence; conflicted recarries recur whenever main moves under a critical-path head.

Carry text (for `roster_edit.py append-carry R10-TRAIN-OVERLAP-GRADE`, citing `triage: dev/programme/triage/s6-batch32.md#P184`): "Stale train holders (V104 slip, #2753, s40 -> s41). (a) `tools/audit/seat/remerge_main.sh` line 21: when `git merge --no-edit -q origin/main` fails, run `git merge --abort` in the worktree (fallback: `git reset -q --hard origin/<branch>`) before printing MERGE CONFLICT and exiting 1, so the train's own recarry worktree is clean and `release_worktrees` (`merge_train.py` 1805-1816) removes it at the close. On 2026-10-25 s40 logged `NOT released .../wt/2753 ... contains modified or untracked files`. (b) `freeable` (`merge_train.py` 996-1010): a clean holder whose HEAD is an ancestor of origin/<branch> is freeable, so nothing is lost. Only a HEAD with commits origin lacks refuses, with that reason. s41 refused 45d08312, an ancestor of origin's 8a133f39, as 'unpushed work'. Do not key on a train-dir path pattern. Controls: a fixture recarry whose merge conflicts leaves a clean worktree and a `released` line (a mutant without the abort leaves `NOT released`); a clean holder behind origin is freed and logged; one ahead of origin refuses with 'commits origin does not have'; an equal holder is freed as today (null)."
