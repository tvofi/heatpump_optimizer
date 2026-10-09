Fix review: blocked 63e4eba35582afb3899a67d0060429e95ee51350 conflict-resolution: origin/main b2b6acd64 x this head conflicts in tools/pr/ci_predict.py and tools/pr/prepr.sh (step 13, non-claim paths); head has 0 check-runs, so 0 of the 17 required contexts ran and the merged result is not knowable

bus-nonce: be36a6804e1752e80e05dc9435f67749
seat: review-deltas-1015
Evidence: /Users/timmalmstrom/hpo-seats/review-deltas-1015/2073/evidence

Round 3 of this PR, judging a **resolution delta**: the live head moved from `5bcf9d2b201951ff8dfb0e414c633546f1bef453` (the round-2 `merge` verdict, comment 6075945640) to `63e4eba35582afb3899a67d0060429e95ee51350` under an orchestrator push.

## The delta itself is exactly what it claims — that part passes

`git log --first-parent 5bcf9d2b..63e4eba35` is **one commit, not "main merges + one commit"** as my brief was handed it:

- `63e4eba35 tvofi record: the delivery row for #2073` — `dev/programme/delivery/2073.md`, `1 file changed, 1 insertion(+)`. Delta diff stat: 1 file, 1 insertion. `git rev-list --count 5bcf9d2b..63e4eba35` = 1, reverse 0; `origin/main` is **not** an ancestor of this head, so no main merge arrived.
- RESULT the row is one line, anchors #2073 once, and matches main's row shape.
- RESULT nothing else moved: the branch's own three-dot patch (merge base `47b083b0`, unchanged) is **byte-identical once the row file is excluded**; all four branch-owned paths — `dev/audit/rca/R9-RCA-stale-pins.md`, `dev/programme/carries/carry-201.json`, `tools/pr/ci_predict.py`, `tools/pr/prepr.sh` — are blob-identical `5bcf9d2b`→`63e4eba35`. So the round-2 measurement (its plants, the wedge control, the `--perturb` carry) still describes the code, and nothing already verified is invalidated by this delta.
- RESULT claim files byte-identical to `origin/main` at this head (`62bf9eaba2…`, `c683379daf…`).

## Why the verdict is blocked anyway — two things, neither of them this branch's authored work

**1. Step 13: the branch now conflicts with `origin/main`, and not on a claim file.**

`git merge-tree --write-tree origin/main 63e4eba35` → **rc=1**, with conflicts in `tools/pr/ci_predict.py` and `tools/pr/prepr.sh`. There is **no `MERGE-CLAIM` marker in the driver's stderr** for either run, so this is not the `claimnotes` refusal the orchestrator resolves by hand as a matter of routine; it is a content conflict on two paths this branch owns and main has since edited. Step 13 binds here: a conflict on any path other than the two claim files is mine to block on, because I cannot know the merged result is correct.

- RESULT main, not this delta, caused it: the **same** rc=1 conflict, on the same two paths, is present at the round-2 head `5bcf9d2b`, and the row commit touched neither file. `origin/main` advanced (through `b2b6acd64`) into these two scripts after this branch's base `47b083b0`: `git log 47b083b0..origin/main -- tools/pr/prepr.sh tools/pr/ci_predict.py` names #2061's INERT READS arms (`c94842ed9`, `6ae385f29`, `4cdba2ac1`, `0f64774f6`) and #2028's body-check fix (`af5560f81`, `a6984468b`, `3eb8d53a5`) — the same `6d` region this PR edits with its STALE PIN arm. GitHub agrees: `mergeable=false`, `mergeable_state=dirty`, base `47b083b0`.
- RESULT the other two pull requests in this batch show the split: `#2072` (which also edits `prepr.sh`) merges with rc=0 and reads `clean`; `#2069` merges with rc=0 after its main merges. So #2073's conflict is specific to what main changed in `ci_predict.py`/`prepr.sh` — the recarry and step-6d regions — not a batch-wide artifact.

**2. Step 11: the head has never been gated, and absent is not green.**

The commit's own `check-runs` API at `63e4eba35` reports **total_count = 0**. That is the `claim-files.md`/S2 consequence of `DIRTY` in general and of any conflict in particular: GitHub builds no merge commit and no `pull_request` workflow queues, so the PR does not go red — it **cannot run**. Zero of the 17 required status contexts (ruleset 23698884) exist at this head, the governance family (`policy-docs`, `env-matrix`, `wave-script`, `instrument-self-tests`, `record`, `delivery-status`) among them. `orchestrator.md` section 11's first bullet — every gate lane ran — is unmet; no head is green because a lane never ran.

## What unblocks it, and who does it

Merge `origin/main` into the branch **locally**, where the merge drivers run (`claim-files.md`, steward S2), resolve `ci_predict.py` and `prepr.sh` by hand — this is the orchestrator's resolution, not a defect in the authored work and not a fixer re-cut — and push. The resulting head comes back to me as its resolution delta: I will judge the conflict resolution itself (both sides' lines carried, the union of any `prepr.sh` step labels, `bash -n`, and CI's `closures`/`fast` lanes settled at that head) and the step-11 table at it. Until then nothing is owed by the fixer: the round-2 verdict's substance stands on the branch's own lines, which this delta left byte-identical.
