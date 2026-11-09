Fix review: blocked 9106db4797f1c9b2ab277483977f922982294dd9 defect: bottleneck_check's trip memory is keyed by metric alone, so a breach after an UNREADABLE line for the same metric is masked by the stale line; and merge_train classify reads RED (gate) at this head

bus-nonce: 545f755c666cbcdc9bdaeeafce740724

## Block

1. **defect (patch).** In `tools/audit/seat/bottleneck_check.py`, `remembered` keys its memory by `metric_of(line)`, the line's second word. That word is the same for `BOTTLENECK-UNREADABLE: yield -- ...` and `BOTTLENECK: yield 0.40 ...`. If a metric's source was unreadable on one beat and then really breaches on the next, the run re-prints the stale UNREADABLE line. The breach never reaches the digest, which is the failure the alert exists to prevent. Reproduced at the head (ev/memory_kind_probe_mine.txt): `trip2 (a real breach after UNREADABLE): ['BOTTLENECK-UNREADABLE: yield -- source unreadable']`, MASKED. The reverse direction is the same. The self-test does not cover this. Another run of this seat found it first (commit 981e74722 on this ref, ev/ there), and this run confirmed it independently. Fix: key the memory by (kind, metric), where kind is the line's first word, and add a self-test case for each direction.

2. **ci-red: gate.** `python3 tools/audit/seat/merge_train.py classify 9106db4797f1c9b2ab277483977f922982294dd9 --pr 3350` exited 1 three times (01:45:44Z, 01:46:04Z and 01:47:59Z, ev/classify.txt, ev/classify-2.txt, ev/classify-3.txt): `RED 9106db4797f1c9b2ab277483977f922982294dd9 pending: none red: gate`. The red is not in the patch. Each check suite's latest `gate` is kept and the worst one stands (merge_train.py `latest_runs`/`gate_suites`). Two of those suites at this head carry a deferral `gate` that concluded `failure`:
- job 128917441489 (run 42539681502), 00:51:18Z: `FAIL run(s) [42539680047, 42540557389] at this head are still being judged; their gate decides`;
- job 128920205614 (run 42540557389), 00:59:20Z: `FAIL run(s) [42539680047] at this head are still being judged; their gate decides`.

The code run they defer to, 42539680047, published `gate` job 128932794887 with `success` at 01:40:53Z. Every other completed check at the head is success or skipped. `gate_busy` turns a deferral red into a wait only while a ci.yml run is unfinished, and that run has finished, so the deferrals now read as reds. Nothing in the patch needs to change. The way to clear this is with the orchestrator: re-run the two deferral gate jobs (each should now find run 42539680047 judged), or decide that the classifier's reading is wrong. This block stands apart from block 1: even with a patch fix pushed, the new head needs classify to read GREEN.

## Findings

- Follow-up: a surviving mutant on a line this PR added, `tools/audit/seat/roster_edit.py:1324`, `if a.op in ("set-stage", "set-resume", "mark-carry"):`. Dropping `"mark-carry"` stops `make_edit` from reading the legacy cut-over for a mark, so `close_discharged` gets `{}`. A group whose only unmarked carries are legacy then stays `carries-open` after its last real mark, instead of being written `done`. `roster_edit self-test: 260 checks, 0 failed` under the mutant (ev/mine-legacy-dropped.txt). The harness's `mark-close-*` mutants do not reach this line. The direction is fail-safe: the group is not closed, and `roster_lib.discharged`/replan still read legacy correctly. It still needs one self-test case: a last mark on a carries-open group that also holds a legacy carry is written done. Carry: R10-OUTSIDE-INTAKE

## Evidence

- Head measured: 9106db4797f1c9b2ab277483977f922982294dd9 (ev/HEAD.txt), the head in the PR body and the live PR head at 01:4xZ. Merge base fdc8d21adaa50a7feee534f08ee5edde9bda81ed. `git diff merge-base...origin/main -- dev/governance/roles/` touches only proposal-triage.md, so fix-review.md is current.
- Merge with main: `git merge-tree --write-tree origin/main 9106db4797f1c9b2ab277483977f922982294dd9` at origin/main 6457496ab returned rc=0 and tree 82336c751 (ev/merge-tree.txt). There was no conflict and no claim-file driver call.
- Mutation proof: I re-ran the in-tree `dev/audit/harnesses/r10_outside_intake_p2_mutants.py` at the head (ev/p2_mutants.txt): 22 RESULT mutant lines. M0 printed `rc=0 fails=0 verdict=null`, every other mutant `verdict=killed`, and the run ended `RESULT survived=0`, rc=0.
- My own mutants, outside the harness list:
  - bottleneck_check `remembered` with memory ignored (`now = {metric_of(ln): ln ...}`): killed by "memory: a still-tripped metric re-prints its first line verbatim" (ev/mine-memory-fresh.txt).
  - state_docs `cmd += ["--train-log", a.train_log]` removed: killed by "plan page: --train-log reaches plan_page.py" (ev/mine-statedocs-handon.txt).
  - roster_edit:1324 legacy read dropped: SURVIVED (see Findings).
- `bottleneck_check.py --self-test` at the head: `ok: bottleneck_check self-test`, with all 10 rule mutants killed.
- Replan figures, re-derived at the PR's stated rule: base tree is `git archive` of the merge base fdc8d21ad, not 17e621f08. The head tree is 9106db4797f1c9b2ab277483977f922982294dd9. Roster ref fcc9a1933aa1, `--start 2026-11-08T20:20:00Z --slots 20 --seats 20` (ev/replan-summary.txt, ev/plan-*.json):
  - base: closure 2026-11-15T07:03:00Z, 49 batches, 6075.0 CI minutes, 324 done / 71 open;
  - head: the same closure, 48 batches, 5962.5, 327/68, `groups_discharged` 3. The discharged groups are R10-CI-GRADER-BATCH-STUDY, R10-FRICTION-CI-RED and R10-FRICTION-OTHER-FAMILY.
  - Every figure matches the body. The base arm's tree differs from the body's (main had moved), and the figures reproduce anyway.
- Figures not re-derived: self-test counts (260/72/321/75/185/119/39/34), `selftest_wiring` 125/125, gate scope `2 script(s) run`, entities 2668, harness_headers 112, archscore dS +0.0000. CI's lanes at this head (`tests / closures`, `tests / fast (3.14)`, `governance / instrument-self-tests`, `arch-score`, `tests / mutation`) concluded success and are cited instead, as fix-review.md 11 requires.
- VERSION, RELEASE_NOTES.md, the manifest, golden files, claim files and `*_budgets.json` are all absent from the three-dot diff.
- Red checks (step 11): the body answers the `b99248e2` cancellations and the earlier UNDER-SCOPED `tests / closures`. The two deferral `gate` failures at this head came after the body was set. They are deferrals, not defects. `pr-contract / pr-contract` started at 01:37:08Z, after both, and concluded success.
- Forward-carry: the body states none. Carry 2 is left unmarked on roster `R10-OUTSIDE-INTAKE` (stage `carries-open`, 2 carries on origin/handoff/audit-r10-roster), as the body says.
- Review round: this seat cannot tell. A previous run of this seat ended without pushing a verdict.
- Return ref: `probe/rev-3350-545f755c` already held commit 981e74722bdf1b834f8eb3906b8a753d5ad8f818 (01:45:48Z), a blocked verdict from a run of this same seat that the dispatch did not know about. This verdict is pushed as a fast-forward child of that commit and does not overwrite it. Its first line takes that run's \`defect\` class, which this run reproduced, and adds this run's evidence.
