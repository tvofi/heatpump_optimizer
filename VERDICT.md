Fix review: merge cecca4391dab34349fe10eb41a6ccfb2c4d3600e

bus-nonce: cb3b8594cc430c84b7c8b53a7023f46f

Round 1 of the fix review (first round: no re-cut is owed). PR #3276, group R10-HOTFIX-GATE-BUSY-DEFER (reopened, fix 2). Reviewed from a detached worktree at cecca4391dab34349fe10eb41a6ccfb2c4d3600e. Merge base 294a880dae608502b62055775e34a5db93217b98 is origin/main. Diff read three-dot. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the role contract is current.

## Evidence

- RESULT head: cecca4391dab34349fe10eb41a6ccfb2c4d3600e, still the PR head at the last read. The body's `## Head` names it, and the authored code head is cc100c27, its parent. The delivery row `dev/programme/delivery/3276.md` is in the diff (ev/HEAD.txt).
- RESULT merge: `git merge-tree --write-tree origin/main <head>` rc=0, tree 9ba7542d, with no conflict (ev/merge-tree.txt).
- RESULT untouched: VERSION, the manifest, RELEASE_NOTES.md, every `*_budgets.json`, tests/closure.py and tests/closures.json are all untouched by the three-dot diff. `tests/structure.py` prints STRUCTURE RATCHET PASSED (ev/structure.txt).
- RESULT classification: the new tracked file `tools/ci/fixtures/gate_busy_defer_runs.json` falls under the GATE_FILES `tools/ci/` prefix (tests/closure.py:501), the same as the existing `tools/ci/fixtures/ruleset/*.json`. It forces FULL, which is deliberate for a gate input. `closure.py select` prints MODE: FULL (ev/closure.txt). `tests/entities.py` cannot run locally because homeassistant is not installed. CI's `tests / closures` is green on the code run.
- RESULT self-tests at the head: `gate self-test: 74 checks, 0 failed` and `prelude self-test: 62 checks, 0 failed` (ev/selftest-head.txt).
- RESULT harness at both ends. I ran `dev/audit/harnesses/r10_gate_defer_race.py` over `git archive` exports at 28482ece, at 294a880d and at the head (ev/harness-base.txt, ev/harness-head.txt):
  - `prelude` scenario: UNDECIDED-RED 1 at both bases, and UNDECIDED-RED 0 DEADLOCK no CYCLE 0 at the head.
  - The other six scenarios are flat (UNDECIDED-RED 0, MASKED 0, DEADLOCK no) at all three trees.
  - `fixture` scenario at 28482ece: all three CI-logged FAILs are reproduced verbatim after 0 s. This null holds: the replay is faithful.
  - `fixture` at 294a880d: 42338396358 FAILs after 0 s, and the #3261 pair reads PASS.
  - `fixture` at the head: 42338396358 FAILs after 720 s (the bound), and the #3261 pair reads PASS after 0 s.
  - Every figure in the body's Figures section re-derives.
  - The roster group names no finder's harness (roster c9bcaca7, ev/roster-group.txt). This group-level instrument is the closest one, and I name it as such.
- RESULT fixture provenance. Cross-checked against the live jobs API for edit run 42338396358: budget-raise-gate ran 04:26:14–04:26:41, arch-score ran 04:26:14–04:27:26, and `pr-contract` is listed under its bare name, completed `skipped`. These match the fixture's attempt-1 record. Code run 42338396871 concluded success at 04:59:04, about 31 min after the edit gate's judge step at 04:27:56, which confirms the body's residual. The fixture is real API data, not re-typed.
- RESULT failing test first. The head's self-test was run over 294a880d's production code (prelude.py plus gate.py above `self_test`). My first attempt used a partial tree and errored on missing files, so it is not cited. The body's figure "74 checks, 9 failed" was not independently re-derived by me. The mutants below kill the same checks, which stands in for it.
- RESULT mutation, the fixer's table: `r10_ci_gate_core.py mutants` gives RESULT mutants=21 survivors=0 (ev/mutants-head.txt).
- RESULT mutation, my own mutants (ev/mutants-own.txt; R0, the unmutated control, gives 0/0 failed):
  - R1 deletes the new `judging` skip: gate 5 failed, harness `prelude` UNDECIDED-RED 2 DEADLOCK yes CYCLE 1. KILLED.
  - R3 widens the skip to any started caller: gate 1 failed. KILLED.
  - R4 restores the at-once bound: gate 6 failed, harness `prelude` UNDECIDED-RED 1. KILLED.
  - R2 survives. It is an equivalent mutant; see Findings.
- RESULT null controls. Each is present and passes at the head:
  - A lone code run still gates (`single`: gate-wait 0 s).
  - A finished sibling still decides, through the C3 re-judge checks.
  - The bound still holds, through the past-bound FAIL check.
- RESULT finding a5837b0c. The body's Forward-carry says plainly that a re-run executes its event base's programs. It claims no re-run cures the old runs, and it advises re-judging only after a fresh event. The live record agrees: this head's own gates all logged `programs restored from 294a880d`, which is pre-fix code.
- RESULT class rule. The body's rule is `grep -n "workset(" ...` with self-test hits excluded, and it returns 4 seams, each dispositioned. I reproduced the seam set from the diff and the files the rule names. I found no seam beyond the four.
- RESULT CI on this head (ev/ci-edit-gates.txt, ev/code-gate.txt, ev/code-run-42342100403.txt, ev/classify.txt). All 60 check-runs fit on one page of 100.
  - Edit runs 42342100330 and 42342851829 each FAILed their gate 3 s into Judge with `FAIL run(s) [42342100403 ...] at this head are still being judged; their gate decides`. Code run 42342100403 was still in progress at the time. This is the brief's GATE DEFERRAL case: #3263's race, at the event-base gate (294a880d, pre-fix), and not a red of this diff.
  - Code run 42342100403's gate (job 128324499249) logged `PASS` at 06:16:47. Its `pr-contract / pr-contract` was green at 06:16:08, after the last red concluded (05:36:27), so that run checked the body. Under fix-review step 11, that green body check is the evidence.
  - By that run's verdict, I judge the head GREEN.
  - `merge_train classify` read RED (`red: gate`, rc=1) before the sweep. The gate-sweep re-runs, at attempt 2 on 294a880d's programs, went as follows. 42342851829's gate passed. 42342100330's gate FAILed once more at 06:20:18, deferring at once to its sibling's re-run gate, still queued: the same pre-fix race this diff removes, now live on this head. A further sweep cleared it.
  - Final: `GREEN cecca4391dab34349fe10eb41a6ccfb2c4d3600e pending: none red: none`, rc=0 at 06:34:27Z (ev/classify-final.txt).
  - `## Red checks` says "none predicted". The edit-gate reds are the brief's GATE DEFERRAL case, at the event base's pre-fix programs, not this diff's. The code run's `pr-contract` was green after the last red, so the body check stands.
- RESULT the code run's conclusion is `cancelled`, because `governance / instrument-self-tests` was cancelled at 30 min. It was in the ci_predict step, just after printing `ci_predict self-test: 0 failed`. The run's gate read that job as non-gating and PASSed.

## Findings

- Residual: on #3263's recorded runs the fixed gate still publishes the deferral red. It now comes past the 720 s bound rather than at 0 s, because that code run took about 34 min against a 12 min bound.
  - Claim: for any code run longer than the bound, the edit gate still goes red until gate-sweep re-judges it, and merge_train reads the head RED until then.
  - Evidence: the harness `fixture` scenario at the head prints FAIL after 720 s. The live code run 42338396871 ended at 04:59:04.
  - Perturbation: R4, the restored at-once bound, moves the wait back to 0 s.
  - The body states this plainly and leaves the bound to the orchestrator. The train recarries waiting on this hotfix will still each show a transient edit-gate red whenever their code run outlasts 12 min, so the orchestrator should expect a sweep re-run, not a clean first pass.
  - Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Follow-up: the new `if jobs.get(u, ("",))[0] == "completed": continue` in `prelude.judging` tests a condition the guard above it already guarantees, so the `== "completed"` part pins nothing.
  - Harness: mutant R2 (`if u in jobs:`) survives both self-tests and the harness.
  - Metric: 0 failed.
  - The body's "fix's own null" (`a caller still running ... still owes its unit`) is held by the earlier all-completed guard at prelude.py:196, not by the new line. Behaviour is correct and the mutant is equivalent, so this is a labelling defect only.
  - Carry: dismissed: equivalent mutant, behaviour correct; the null is held by the pre-existing guard
- Out of scope: `governance / instrument-self-tests` was cancelled at its 30 min limit on this head's code run (job 128315297427), during the ci_predict step after its self-test passed. The run concluded `cancelled` while its gate PASSed.
  - I could not tell whether this diff's FULL scope caused the slowness. I did not re-run it, because CI's heavy runs are cited, not re-run.
  - It is not gating on this head: the gate PASSed with it cancelled.
  - Carry: dismissed: not gating on this head; the gate PASSed with the job cancelled, and its self-test printed 0 failed before the cancel

## Friction

- The frugal inline-search budget refused plain verification commands (a classify run, a sed of merge_train.py) as "search ops", so I had to route CI waits and file reads through subagents. Carry: dismissed: session-local plugin, not a repository mechanism
