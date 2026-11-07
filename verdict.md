Fix review: merge 37d64edf2f82f78288999663cee629842aabef88

bus-nonce: 147226123463d2111b1ec347acc36127

Round 1 (first-round adversarial fix review) of PR #3269, R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT, measured at head 37d64edf2f82f78288999663cee629842aabef88 in a detached worktree. Merge base 80016a71f567d936450d8708abcbb79d9e8071d7. Roster read at origin/handoff/audit-r10-roster 149b326a0. I checked the role file against current main: `dev/governance/roles/` differs from the merge base only in nudge.md, so fix-review.md is current.

## Evidence

- RESULT mutation proof, run with `PYTHONPATH=tests/hastub python3 tests/entities.py`, one worktree per mutant (diffs in ev/mutants.diff, summaries in ev/entities_*.summary.txt):
  - The head reads `ALL 2641 ENTITY CHECKS PASSED`.
  - m1, which drops `drive_pool`'s `and not (free and free(m, s))`, gives `1 of 2641 FAILED`, the admission check. Killed.
  - m2, which drops the same filter in `drive_pin_pool`, gives `1 of 2641 FAILED`, the same check. Killed.
  - m3, which drops `main()`'s `free=reach_free`, gives `1 of 2641 FAILED`, the same check. It is killed by the textual `"free=reach_free)" in _MUT_BODY` clause only.
  - m6, which reverts the seed to the date, gives `1 of 2641 FAILED`, with `missing=['--seed "${{ github.run_id }}"']`. Killed.
  - m7, which reverts the budget to 240, gives `2 of 2641 FAILED`: the mutation-ledger write-grant check and the budget-pass check. Killed.
  - m4 and m5 are two unnamed changed lines in `reach_free`. Both survive (see Findings).
- RESULT null control: the new check's own null (a `free` that frees nothing) closes both schedules at once on every mutant above, since its assertion clauses [2] and [3] hold under m1–m3. The m1–m3 failure output shows the freeing arm move while the null arm stays `SKIP-BUDGET`. The harness therefore moves under its own perturbation.
- RESULT breakdown, re-derived with the PR's `dev/audit/harnesses/nightly_drain_breakdown.py` over the eight shard logs, fetched by `gh api .../actions/jobs/<id>/logs` (ev/breakdown_sched.txt, ev/breakdown_dispatch.txt):
  - Run 42139479636 gives drawn 320, killed 90, killed new 20, lives 44, split 0, timed out 1, not run 185.
  - Per-shard slack is 55, 16, 80 and 37 minutes.
  - Dispatch 42135552492 gives drawn 320, killed 104, killed new 104, lives 66, split 1, timed out 1, not run 148.
  - Every figure matches the body exactly.
- RESULT duplicate-draw mechanism: all eight `DRAIN SHARD` headers read `of 3091 unpinned site(s) ... --seed 20261106`. The dispatch started at 00:15:55Z and the schedule at 00:48:25Z, 32.5 minutes apart; the body's "33" is that figure rounded. Ledger commits b346319a6 (20 files) and 5d75a576f (104 files) match `killed new`.
- RESULT 37%/13%: I ran the PR's `drain_admission_probe.py` myself on a 785c2b604 tree with `--scope full --drain DIR --max 320 --jobs 4 --seed 20261106`, then `--summary` (ev/admission_summary.txt, ev/admission_probe.log):
  - mutants 320; shared pairs 6028, reach-free 2234 (37%). This is identical to the body.
  - Admission charge is 126.5 h, of which 15.4 h is reach-free (**12%**, against the body's 13%). Median charge is 22.9 / 19.7 min, against the body's 23.8 / 20.2.
  - The pair counts are structural and reproduce exactly. The hour share depends on the machine's baseline seconds, as the body itself states ("the shares are the figure and the hours are not"). The charge share is 12–13% across two machines.
  - The probe is the fixer's own instrument, disclosed as such. The group has no finder's harness, because the owner's request is the finding.
- RESULT wall clock (ev/jobs_42139479636.txt): shard 2 ran 00:54:49Z–04:39:03Z, 224.2 minutes. The body's "225 minutes of timeout-minutes: 330" is that figure rounded up. 785c2b604's nightly.yml shows `timeout-minutes: 330`.
- RESULT killers (ev/killers.txt): tests/features.py has 130 of 194 kills, matching the body.
- Not re-derived: the body's runner core count, "`nproc` 4". Neither ledger shard log states a core count, only `--jobs 4`.
- RESULT checks: `python3 tests/structure.py` gives STRUCTURE RATCHET PASSED. The diff moves no `*_budgets.json`. VERSION, the manifest and RELEASE_NOTES.md are untouched in the three-dot diff. dev/programme/delivery/3269.md is in the diff. Both new harnesses are classified in tests/closures.json.
- RESULT merge: `git merge-tree --write-tree origin/main <head>` exits 0 against main 28d46c49 (ev/merge_tree.txt). Only closures.json needed the ledger driver, with `LEDGER-MERGE: resolved`. Main has not touched mutation_table.py, nightly.yml or the role files since the base.
- RESULT CI: all check-run pages at the head (68 runs, ev/check_runs.txt) show no concluded run other than success, skipped or neutral. `merge_train.py classify` exits 0 with `GREEN 37d64edf2f82f78288999663cee629842aabef88 pending: none red: none` (ev/classify.txt). `## Red checks: none` is accurate.
- `## Head` names 37d64edf2f82f78288999663cee629842aabef88, the head I measured. The branch was still at that head when this verdict was written.
- Behaviour check of the admission change:
  - `reach_free` reads `reaches.get(s)`, which is None for a lazy or deferred driver, so `reach_skip` returns False and `drive()` keeps its own check.
  - EXCLUSIVE drivers are still charged in full.
  - `drive_pin_pool._resolve` reads `shared0`, which now excludes freed pairs, so a kill does not wait on a pair that never runs. That is consistent.
  - A freed pair could not have killed: its trace never executed the line. Kills and pins are therefore unchanged per admitted mutant; only admission widens.
  - Survivor triage is untouched and stays manual.
- Side effect, report-only. `reach_free` is evaluated for every pool mutant before admission, including ones later cut `SKIP-BUDGET`. So the `REACH SKIP` tally now counts their pairs, and `pin_reverification` in mutation-nightly reads `PIN NOT REPRODUCED` rather than "not re-verified" for a budget-cut pinned site whose pinned killer's trace never reaches its line. That reading is true from the trace whatever the budget. I record it here and do not treat it as a defect.

## Findings

- Survivor: the mutants deleting `reach_free`'s `reach_skipped.append((triage_key(mut), s))` (m4) and its `outcomes[(id(mut), s)] = False` (m5) each read `ALL 2641 ENTITY CHECKS PASSED`. No check pins the bookkeeping that the docstring claims ("recorded as reach-skipped before the schedule queues it"). Without m4's line the `REACH SKIP` tally under-reports freed pairs. Without m5's line `pin_reverification` misreports a freed pinned pair as "no longer drives this file". The change still needs a check that runs `main()`'s path, or a fixture over `reach_free`, asserting both. Carry: R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT
- Defect, stale comment: `.github/workflows/nightly.yml:101` (mutation-nightly) still says "The seed rotates by date, as mutation-ledger's does (R9-F10.13)". This PR made that false. It updated the four other date-seed comments it touched but missed this one, which is the class's remaining site. It is comment-only and changes no behaviour. Carry: R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT
- Follow-up: the group brief requires before-and-after pins-per-night on a workflow_dispatch nightly. The after-figure can only be taken after merge, because `mutation-ledger` runs only on refs/heads/main. It is owed by the seat that lands this PR: `nightly.yml` dispatched on main, then `nightly_drain_breakdown.py` over its four shard logs, with `--prior` naming any run that pushed during it. The body's `## Forward-carry` reads `none`, yet its Friction dismissal says the after-run "is named under Forward-carry". That is a body inconsistency; this bullet carries the obligation instead. Carry: R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT

## Friction

- The frugal-routing inline-search guard refused ordinary evidence commands (`grep` over my own result files) twice mid-review. I resumed only after delegating an unrelated lookup. This cost time on a critical-path review without saving any reading. Carry: dismissed: session-plugin tooling outside this repository's seams
