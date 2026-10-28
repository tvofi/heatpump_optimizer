Fix review: blocked 2d4a45e59841a37c52ff89e3d7c69599a07e317b carry-missing: carry [6] stamp flush (stamp dispatches record-autofix and waits for its merge before tagging) not built; deferred to R10-FLOW-POSTMERGE, which owns neither stamp.py nor web-stamp.js

bus-nonce: 65884187d240bbd0bee2c5281515a6a3

Round 1 (first review of the fixer's handoff). Measured head: 2d4a45e59841a37c52ff89e3d7c69599a07e317b, detached worktree. Base/merge base: f3ffb1c63 (= origin/main at review). Roles diff merge-base...origin/main: empty (contract current).

## Block

Carry [6] (roster, R10-FLOW-RECORD-PITCH) states: "The stamp step dispatches `record-autofix` and waits for its merge before tagging, because tools/release/stamp.py's rule 5 refuses rowless merges." The diff does not build it (changed files: ev/changed_files.txt; neither tools/release/stamp.py nor .claude/workflows/web-stamp.js nor web-fragments.md changes). The body defers it ("The stamp flush ... Carry: R10-FLOW-POSTMERGE") because stampPrompt in web-fragments.md sits under its policy token cap (2427, confirmed present at dev/governance/config/policy_budgets.json:102; the "shortest wording read 2497" I did not re-derive).

Why this is carry-missing rather than a settled deferral:
- The batch this PR adds is exactly what makes the stamp refuse: on a push, up to 7 rowless merges (and any count below the age arm) now wait, so a stamp run after a wave's last merges meets rule 5's refusal until someone hand-dispatches nightly.yml twice (open, then merge). The carry was written to prevent that regression and this PR ships the regression without it.
- The named destination does not own it: R10-FLOW-POSTMERGE's roster files are merge_pr.sh, merge_train.py and INSTRUMENTS.md, and none of its carries at origin/main mentions the stamp flush. A carry to a stage that owns no stamp file is not a carry to the stage that must act (finding-propagation.md).
- The only route weighed was the capped policy fragment. A code route (tools/release/stamp.py, or the web-stamp.js script outside the fragment) was not examined in the body's alternatives, and where every route needs a cap raise, CLAUDE.md rule 2 asks the owner before pushing, not after.

To clear: build the stamp flush in this PR by a route that needs no budget raise, or obtain the owner's ruling (cap raise or explicit waiver of this clause of carry [6]) and record it in the body, with the carry written into the brief of the group that owns the stamp.

## Findings

- Stamp flush of carry [6] is unbuilt (the Block above). Carry: R10-FLOW-RECORD-PITCH
- Directive [7] "record PRs never merge under a running train": the head keeps the beat's own merge outside a train (behind the unchanged train hold and the new pitch) and reads the directive as covering a running train only; the stricter reading (beat never merges, only the --bot-prs sweep) needs the owner's ruling, as the body says. Carry: R10-FLOW-RECORD-PITCH
- CLI exit mapping of --batch-due / --pitch-check (`return 0 if why else WAIT_RC`, and the inverse) is pinned by no mutant: tests/entities.py's batch wiring check greps the job text and the step harness stubs record_row.py. The body's triage ("a failed git read proceeds, never a stranded row") is true of the git reads but not of a swapped exit, which would make every due batch wait (including schedule/dispatch flushes) and strand rows until OVERDUE. One self-test or entities case driving main() over a plan file both ways closes it. Carry: R10-FLOW-RECORD-PITCH
- The STALE_AFTER_COMMITS = 12 margin (check f) holds at the p90 only: floor/age arm 8 plus wait_c p90 3 = 11 < 12, but wait_c max is 10 (round 10), so the tail can still read OVERDUE. The body states the p90 basis; the after-merge measurement should report the overdue count, not only the record-merge rate. Carry: R10-FLOW-RECORD-PITCH

## Evidence

- Merge with origin/main: `git merge-tree --write-tree origin/main 2d4a45e59841a37c52ff89e3d7c69599a07e317b` exit 0, no conflict (ev/merge_tree.txt).
- VERSION, manifest, RELEASE_NOTES and both claim files untouched (ev/version_claims_untouched.txt). No fixture moved, so step 4 has nothing to compare.
- record_row.py --self-test at head: "record_row self-test: all checks passed", gh_read 122 checks 0 failed (ev/record_row_selftest.txt).
- Mutation proof re-run with the seat-selftest harness: RESULT survivors=0; record_row-1 KILLED (chain), record_row-2 KILLED (batch: a dispatch with 1 row flushes; the carry's "drop the event check" mutant), record_row-3 KILLED (pitch), S19 baseline KILLED (ev/seat_mutants.txt). Mutant ids are per-file and inside the record_row.py block (carry [3a]).
- The entities.py mutants in the body's table (classify's record_class arm, the pitch arm, the event in the batch gate) were not re-run: a full entities run is a heavy run, cited from CI, which had not concluded.
- CLI driven end to end at head over real main merges (ev/batch_due_cli.txt): 3 fresh rows on push -> BATCH WAIT rc=4; same on schedule and workflow_dispatch -> DUE rc=0; 2 rows whose oldest is 13 commits old on push -> DUE rc=0. Controls of carry [6]/[7] (7 wait / 8 open / dispatch 1 opens / count 2 at age 8 opens / young-record pitch overridden at 8 commits) present as self-test arms and pass.
- Body figures re-derived with the PR's own harness (record_batch_measure.py, sha1 6e1490fcbbcc matches the body) over db71fe47a..dfcd8d9be: record merges 174; rows median 3 p90 5 max 21; wait_c median 1 p90 3 max 10; wait_s median 2629 p90 6129; age median 3 p90 7 max 20; chain 170/173; conflicts 0/174; moved 73/174; 2026-10-24: 21 of 56 (ev/record_batch_measure_dfcd8d9be.txt). All match. Null control (empty range) prints record merges 0 (ev/record_batch_measure_null.txt). This harness is the fixer's own (disclosed); the group has no finder harness beyond the roster's git rule, which it implements.
- Not re-derived: the merge-wait-by-size buckets (ad hoc, uncommitted, as the body says), the 122-reads API estimate, the ledger figures (146/147 rowed), the chain plans at 102f74975/ce3a77c5f (uncommitted plan_at.py), and the 2497-token stampPrompt wording.
- Check (b): the beat now caps the plan at BATCH_CEILING_ROWS = 27 (title bound, pinned by the ceiling self-test arm); there was no per-run row cap at base. The API argument cites no figure from R10-RECORD-API-BUDGET beyond "W + 3P"; the batch reduces pushes to main and so Governance record-job runs.
- Check (d): the automerge path's review gate and merge pin (_raf_review_gated, _raf_merge_pinned) are unchanged and still required by _raf_job_ok; the pitch only adds a skip, so no-review admission is not widened.
- Check (e)/carry [5]: plan_merges skips a record-class merge (self-test chain arm with its null control), classify rows a record_class merge (entities check with null control); both use stamp.merge_is_record_class, called not copied.
- Carry [0]/[4]: not applicable (MQ probe infeasible, #2826 closed). Carry [1]: pitch at 3600 s, two-pitch override, in nightly.yml's automerge step after the train hold; controls present. Carry [2]: one row per merge preserved. Carry [3]: no new git repos or push sites; Red checks section present.
- CI on this head: at review time only prelude/cancel-superseded/refresh jobs, mostly queued, none concluded red; the red-check step (11) cannot be judged yet and is not part of this block.
- Code-owned workflow (.github/workflows/nightly.yml): a later merge verdict still needs tvofi's review under the mandate.
