Fix review: blocked 1131843cf418a2bc0bb81c28bac1be45ea7d1def mutation-vacuous: X-nosort, X-namefilter, X-nobatch survive at this head

bus-nonce: 1a9f4edd44647d818ea5c5c4eabaaf5e

## Block

Round 2 (re-review of the block at bdf48d98). The block's survivors M4, M5 and M8 are now killed, and each dies on the check written for it (ev/why_mt.txt, ev/why_ot.txt). The reviewer's own mutants on the same added lines still leave three survivors. Driver: `tools/audit/seat/mutant_run.py --spec ev/spec_*.json` at the head, NULL SURVIVED first in every spec.

- SURVIVED X-nosort (`tools/audit/seat/merge_train.py`, `one_job_pulse`): `key=lambda r: r.get("completed_at") or ""` replaced by `key=lambda r: 0`. The fixture `hist` already lists runs in completion order, so the completed_at sort never changes the result. Under the mutant, a listing whose runs come back in API order (newest first) builds the BASELINE_JOBS window from the wrong end. To kill it, shuffle or reverse `hist` in the pulse check.
- SURVIVED X-namefilter (`one_job_pulse`): `r.get("name") == name and` dropped from the baseline filter. The only foreign completed run in the fixture, `tests` (0-60 s), is the oldest, so the 6-run window drops it and the printed p50 and max do not change. To kill it, give the foreign run a recent completed_at, or use a window larger than the history.
- SURVIVED X-nobatch (`tools/audit/seat/orchestrator_tick.py`, `HELD_TOPIC`): `-\S*batch\S*` widened to `-\S*`. Every held fixture ref is a batch ref and every live one is `r10-live-*`. No test shows that a non-batch `triage-*` or `record-*` topic stays unheld. No such topic is on the bus today (git ls-remote), but the predicate's `batch` qualifier is untested. To kill it, add a non-batch `triage-x` or `record-x` ref to the live set.

## Evidence

- Head 1131843cf418a2bc0bb81c28bac1be45ea7d1def is still the handoff tip at verdict time (git ls-remote refs/heads/handoff/r10-tick-residue-p2). The body's `## Head` names the same SHA. Measured from a detached worktree.
- Mutation proof (ev/mutants_mt.txt, ev/mutants_ot.txt, ev/mutants_ou.txt). These mutants are KILLED: M1, M4, M5, M5b, M6, M7, M8, M9, M10, M11, plus the reviewer's own X-p50, X-notstarted and X-sortrev. These SURVIVED: X-nosort, X-namefilter, X-nobatch.
- Why each named mutant dies:
  - M4 fails only "wait_ci logs the one-job pulse right after its beat".
  - M5 fails the window check and the over-max check.
  - M5b fails the window check.
  - M8 fails "25 stranded with 14 held: all 11 others print within the cap".
  - M10 fails the held-last and cap-count checks.
- Null controls hold: every spec's NULL SURVIVED, and the body's three named null checks pass inside the green self-tests.
- Figures re-derived at the head:
  - `orchestrator_tick.py --self-test`: 315 checks, 0 failed.
  - `PYTHONPATH=tests/hastub merge_train.py --self-test`: 614 checks, 0 failed (ev/mt_selftest.txt).
  - `owed_unactioned.py --self-test`: 60 checks, 0 failed. The body gives no number for this one.
  - `tests/closure.py select --diff <merge-base>`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`.
  - (ev/checks.txt)
- `tests/structure.py`: STRUCTURE RATCHET PASSED. VERSION, the manifest, RELEASE_NOTES.md and both claim files are untouched in the three-dot diff. The new file `dev/programme/delivery/3471.md` is the delivery row.
- `git merge-tree --write-tree origin/main 1131843c` exits 0 (tree af0036853298). The head is behind origin/main 0e28afd38b35 but merges cleanly.
- The rebinding `hang = [...]` in merge_train's self-test matches the base's `hang[0]` mutation (name "fast", started_at "1", now completed). The later proof-wait test is not weakened.
- CI:
  - No review packet was provided, and the brief says there is no CI to wait on before the PR opens.
  - The PR's listed check-runs belong to the earlier head. Their only reds are `tests / nightly-status` and `governance / instrument-self-tests`. Neither is in `merge_train.py owed-reds` (ev/owed_reds.txt), so neither is owed an answer.
  - Re-check CI at 1131843c once it is pushed.
- Forward-carry: the body has none. Carry 1 (CI-PULSE-ONE-JOB-BASELINE) is built in this diff as `one_job_pulse`. I did not open the roster at a `handoff/audit-r10-roster` SHA, so I have not verified that no other carry is assigned to this group.

## Findings

none
