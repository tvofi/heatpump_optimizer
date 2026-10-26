# Proposal triage, session s6, batch 33 (P192-)

Proposals from the s6 `proposals.md`. Numbering continues after `s6-batch32.md` (P184-P191). This batch holds 8-10 entries and merges only through the train queue (tvofi, 2026-10-25). Facts read at origin/main b281d0325.

A roster op citing an ACCEPT below resolves only once this file is on the roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P192: the installation rate limit turns required checks red, and a seat classifies and reruns them by hand (S6-V112)
Verdict: REJECT, both arms. The recurrence is not a proposal. It is the recurrence of the class that `dev/audit/rca/install-ratelimit.md` (R10-RCA-INSTALL-RATELIMIT) diagnosed, and it returns to that class's root-cause route (`defect-root-cause.md`). That route is the orchestrator's to dispatch, and this ruling carries nothing.
Source: s6 `proposals.md` `## V112` (orchestrator, 2026-10-26T05:06Z).
Instances: one burst on two PRs, plus one filed instance of another class.
- #2850, run 40269660944. `seat-ledger.md` lines 826-827 in the orchestrator's state directory.
  - At 04:53:08Z, arch-score logged `gh: API rate limit exceeded for installation`.
  - At 04:53:34Z, pr-contract hit the same limit at its body read. Its later jobs fail only because `/tmp/pr-body.md` is missing.
  - The gate exited 3 with `RATE-LIMITED reset_epoch=1792991224`.
  - Train s46 stopped with rc=1 with #2848 and #2825 queued. The merge seat classified the reds and reran with `--failed` after the reset at 05:07:04Z.
- #2843, runs 40271998592 and 40271999135. This is the same window, per V112. Line 832 of the same ledger notes the gate failure at a2a7b9ef (05:01:43Z).
- Not counted: #2845's friction-filer 403 (`seat-ledger.md` line 715). It came from the `record` job on a push to main, not from a required check on a PR. The ledger reads it as a likely secondary limit, and line 733 records that it did not recur.
- The class's earlier burst: three reds on 2026-10-22, at about 06:27Z, 08:40Z and 09:44Z (`install-ratelimit.md:11`). P32 (`s5-batch1.md#P32`) deferred a rerun stagger until "an installation rate-limit red after `97b4fddf2`". The burst above is that red. P32 also asked for the red to be attributable to reruns, and that part is not shown.
- Measured rate: one burst in the about 3.5 days since #2629 (`97b4fddf2`, 2026-10-22). The record's rate before #2629 was 3 a day (`install-ratelimit.md:234`).

Cost of arm (a), the CI re-queue after `reset_epoch`: M. It touches code-owned workflows, so tvofi reviews.
- Every job that went red reads with `GITHUB_TOKEN`: `ci.yml:122`, `:156`, `:300` and `:340`, `arch-score.yml:59`, and `pr-contract.yml:143` to `:335`. The record (section 1.1) shows that this is the bucket that was empty. A `workflow_run` or cron re-queuer with `github.token` and `actions: write` draws on that same bucket. It must list runs, read their logs and POST reruns while the bucket is drained, and on a cron it adds standing calls on every tick.
- Only the gate prints the `RATE-LIMITED` token. pr-contract and arch-score fail on raw `gh` 403 text, so classifying them means a log download per failed job, which is more calls on the same bucket.
- Waiting for `reset_epoch` inside a job holds a runner for up to an hour per job.
- `gate-sweep.yml` already reruns red gates, but only once another gate at that head is green (`tools/ci/sweep.py:4`). By design it reruns nothing after a rate limit (`sweep.py:15`). Arm (a) would be a second rerun path beside it.
- The record states that retrying from every required check "is not the countermeasure" (`install-ratelimit.md:236-240`).

Cost of arm (b), a train WAIT on a `RATE-LIMITED` red: S in `tools/audit/seat/merge_train.py` (5,560 lines, a hot file), and it covers only part of the burst.
- The train pins a `RATE-LIMITED` gate as red (`merge_train.py:338` and self-test `:4218`). A WAIT state would be a new judged outcome, needing its own arms.
- pr-contract and arch-score carry no token the train reads without logs. So at #2850, WAIT would have parked the gate and still stopped on pr-contract.

Measured benefit: about 15 min of merge-seat and dispatch-seat time per burst (V112), plus a train stall that lasts no longer than the reset. At one burst in about 3.5 days, the rest of the round expects about one more.

Binding: the shared `GITHUB_TOKEN` bucket. Both arms spend calls on the bucket whose exhaustion is the defect, or they judge only the gate. Against about 15 min per burst at the measured rate, neither arm clearly pays.

What would change the answer:
- A root-cause seat on this recurrence that attributes the 04:53Z demand. Governance's `record` job prints the bucket's `RATE_LIMIT before:` and `RATE_LIMIT after:` lines (`governance.yml:1290` and `:1399`, M0). If the record's M3 (moving the O(window) reader off the shared bucket) or a load cut does not apply, re-file arm (b) with a measured burst rate. Arm (b) would then also need a log-free rate-limit signal from pr-contract and arch-score.
- More than about one burst a day after #2629, counted from the ledger.

## P193: a train stops because another worktree holds a PR branch (S6-V113)
Verdict: DEFER. Both instances already have owners, and neither is an instance of a missing default.
- Instance (1) is P184(a) (`s6-batch32.md#P184`, ACCEPT, carried to R10-TRAIN-OVERLAP-GRADE).
- Instance (2) is R10-FLY-OPENPR-ATOMIC carry 2 (triage P-D, s4, 2026-10-23, accepted; stage `not-started`). That carry makes `open_pr.sh`'s exit trap detach its PR worktree.
- The filing's first arm, making `--free-holders` the train's default, is REJECTED.
- Its second arm is that owned carry. Per R10-UPDATE-PR-SIGNALS carry 3, the `update_pr.sh` half is owned there.
Source: s6 `proposals.md` `## V113` (orchestrator, 2026-10-26T05:17Z).
Instances: two, today, and they are two different holders.
- (1) The holder was train s43's own `wt/2745`.
  - `seat-ledger.md` line 786 in the orchestrator's state directory (04:34:26Z) shows it held `fix/r10-sav-comfort` at origin's 8d0572dc with "the train's own unfinished merge of main ... with conflict in tests/golden/claimed_drift.txt".
  - The merge seat ran `merge --abort` and then `worktree remove --force`.
  - That worktree was dirty, so `--free-holders` would have refused it: `freeable` requires `status --porcelain` to be empty (`merge_train.py:996-1010`).
  - It is the shape of P184(a): `remerge_main.sh` exits 1 on a conflict without aborting the merge.
- (2) The holder was `open_pr.sh`'s worktree.
  - `seat-ledger.md` lines 842-843 (05:16Z) show s47 stopped at #2848's recarry, holder clean, HEAD equal to the remote 2c7016ce. The train was relaunched as s48 with `--free-holders`.
  - The holder path, `<state>/pr/r10-hotfix-batch-errexit/wt`, is `open_pr.sh`'s `WT=$D/wt` (`open_pr.sh:29`).
  - `update_pr.sh` uses `<state>/pr/upd-<branch>` (`update_pr.sh:30`), so the holder is not `update_pr.sh`'s, which V113 had named.
  - Earlier counts of the same class: P31 (`s5-batch1.md#P31`) counted four `update_pr.sh` holders (#2513, #2544, #2547, #2580).

Cost of arm (a), defaulting `--free-holders`: XS in `train.sh`, but the risk is the binding cost.
- `freeable` tests only that the holder is clean and at origin. It has no liveness test.
- `open_pr.sh` and `update_pr.sh` both hold exactly such a worktree while they run. After `worktree add -B <br> ... origin/<br>` (`update_pr.sh:52`), the tree is clean and at origin until the run's own commit lands.
- A default detach in that window moves the live run's commit off its branch.
- The liveness signal exists, `pr_branch_lock` (`pr_args.sh:66`; `update_pr.sh:34`), but the train does not read it. A default would need that check, which makes arm (a) S in `merge_train.py`, a 5,560-line hot file.
- After the source fixes it would free nothing: the instruments would no longer leave a holder.
- The seat's hand check that V113 prices (no process has the tree open) is the check a default would skip.

Cost of arm (b): owned. R10-FLY-OPENPR-ATOMIC is S, about 10-20 lines in `open_pr.sh` per its carry 2. The carry also fixes a constraint: detach, never remove, under the branch lock.

Binding:
- Arm (a): detaching a live run's clean worktree, for a default that the source fixes make redundant.
- Arm (b): its group already owns it.
- The recurrence is evidence for that group's dispatch, not a new carry. Closure saving: about 5-10 min of critical-path time plus one manual check per instance (V113), so two today.

What would change the answer: a holder that no owned fix covers, a stale clean worktree left by a process other than `open_pr.sh`, `update_pr.sh` or a train's conflicted remerge. Then arm (a), gated on `pr_branch_lock` being free, is the candidate.

For the orchestrator, not a carry: R10-FLY-OPENPR-ATOMIC is `after: [R10-UPDATE-PR-SIGNALS]`, and that group's resume has read `in-progress` since 2026-10-20.

## P194: a hand-rolled POOL.txt removal emptied the pool for a minute (S6-V114)
Verdict: ACCEPT narrowed, as an amendment to an accepted arm -> R10-FLOW-DESIGN-STAGES (stage `not-started`, M).
- Carry 11 of that group (R10-FLY-POOL-INSTRUMENT, folded in; `s6-batch4.md#P55` and `#P60`) builds `tools/audit/seat/pool.py` with a read-back `append`. Carry 12 (`s6-batch24.md#P111`) and P187 (`s6-batch32.md#P187`) amend it. This adds the one write that the arm leaves hand-rolled: `drop`.
- The filing's guard "refuses fewer than N-1 lines or zero bytes" is narrowed to an exact set check, for two reasons:
  - A count misses a write that drops one line and garbles another.
  - Zero bytes is a legitimate result when the last line is dropped.
- The filing names `pubfix.sh` as a possible home. That is REJECTED: it is not in the tree, and an instrument goes in the tree (decision 0013).
Source: s6 `proposals.md` `## V114` (orchestrator, 2026-10-26T06:10Z).
Instances: one of this shape, and four of its class (POOL EMPTY from a pool edit) that other arms own.
- This shape, `seat-ledger.md` line 890 in the orchestrator's state directory.
  - Commit `03990655f` on `dispatch/pool-s6`, "pool: drop dispatch/fixer-r10-heat-meter-closure", took POOL.txt from 16 lines to 0.
  - The cause V114 names is a zsh `${B}:POOL.txt` expansion that read an empty blob. zsh reads `:P` after an unbraced parameter as a path modifier, and this ruling's own count hit that on `$c:POOL.txt` before it was re-run under bash.
  - Fire cse_01AaeWzk returned POOL EMPTY and was refired as cse_01FtqZzm: about 3 min and one fire lost.
- Base rate, measured on the ref:
  - `git log origin/dispatch/pool-s6 -- POOL.txt` shows 132 commits since 2026-10-24T07:50Z. In 13 of them POOL.txt lost lines (`git show <c>^:POOL.txt` against `<c>:POOL.txt`, run under bash).
  - Removal is routine, about 6 a day: done work is pruned by hand or by the relay (`seat-ledger.md` line 561, "fixer pool pruned 42->1 by relay").
  - 1 of the 13 was the defect.
- No code on origin/main 11b7a9d73 writes POOL.txt (`git grep -n POOL.txt origin/main -- tools/` is empty), so every removal so far was out of the tree.
- The same class, owned elsewhere:
  - Line 82, a silent push failure: carry 11's read-back `append`.
  - Line 517, a reviewer line never appended: carry 12.
  - Lines 81 and 615 (V1, V107), stale claims: carry 11 as corrected by P187.

Cost: XS on top of the S arm. `drop` reuses `append`'s write and its ref read-back, plus one set check and two controls. It adds no new file, no API read and no call site beyond `cloud_dispatch.py`'s existing hook.

Binding:
- Without `drop`, the pool instrument guards every write but the one done about 6 times a day, and that write is the one that just failed.
- This round's cost is about 3 min and one fire per failure.
- The arm is owed regardless, so putting the write in the instrument moves a recurring hand-rolled operation into tracked code at almost no marginal cost (tvofi 2026-10-24: mechanise before policy).

Carry text (for `roster_edit.py append-carry R10-FLOW-DESIGN-STAGES`, citing `triage: dev/programme/triage/s6-batch33.md#P194`): "Pool arm (carry 11), drop verb (V114). `pool.py drop <dispatch-ref>...` removes the named lines from POOL.txt on `dispatch/pool-<session>` (and from `dispatch/rpool-<session>` for a reviewer ref). It goes through the same write and ref read-back as `append`. Before the push it refuses unless the new file's line set equals the old line set minus exactly the named lines. Every named line must be present, no other line may change, and an empty result is allowed only when the named lines were the whole file. After the push it reads the ref back and refuses on any mismatch, with git's stderr. It never builds a git path from an interpolated shell string. The 2026-10-26 instance was commit `03990655f`, where a zsh `${B}:POOL.txt` modifier read an empty blob and took POOL.txt from 16 lines to 0, so a refire was lost. Controls: dropping one of 16 lines leaves exactly 15, the other 15 byte-identical, and prints the read-back line; a write whose blob is empty or missing a line that was not named refuses before any push (the 03990655f shape as a fixture); dropping the only line yields an empty pool and passes (null); dropping a line that is absent refuses and changes nothing; one mutant that removes the set check fails the fixture arm."
