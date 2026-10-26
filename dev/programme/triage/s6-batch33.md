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
