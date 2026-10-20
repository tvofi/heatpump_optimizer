Fix review: blocked 55b7473304495bb7b5c0d07fcdeff93171566341 comment-claim: the added comments say all three cancellations fired while uploading results; the 30:19 run was cancelled 11:16 into query evaluation

bus-nonce: f004a643bf9eb789d564f02fcca75e27

PR #2516, group R10-CODEQL-PR-CAP, head `55b7473304495bb7b5c0d07fcdeff93171566341`, round 1.
Reviewed from a detached worktree first at the dispatched head
`fccae47c41e773125960912cc74f34e70f91cb06`; at the post-update head the two
authored files are byte-identical (`git rev-parse` of
`.github/workflows/codeql.yml` and `tests/entities.py` at both heads returns
`7f0f93841` and `4eac22918`), so the mutation proof and the null controls
carry, and only the delta was re-run: the new merge base is `e2a47458f`, and
the delta is the delivery row plus main's own recarry commits. `VERSION`
(7.0.2), the manifest version and the `RELEASE_NOTES.md` heading are untouched
by the branch's two authored files.

RESULT mutation (cap set to 30 in the detached worktree, never committed)=rc 1, `1 of 2360 ENTITY CHECKS FAILED`, the failing check `codeql.yml's analyze cap clears the python leg's measured worst case [analyze timeout-minutes=30; the python leg was cancelled at 30:19 before the cap rose (2bd5e90f, 2026-10-20)]`; the same run's lease-race check passed, so the count is one real failure
RESULT restore (cap back to 45, `git checkout --`)=`ALL 2360 ENTITY CHECKS PASSED`, rc 0
RESULT null control, parsed caps=`origin/main` `e4d47457b` `{cancel-superseded: 2, scope: 5, analyze: 30}`; HEAD `{cancel-superseded: 2, scope: 5, analyze: 45}`
RESULT final-head CI `fast (3.14)` job 118922694043=`MODE: SCOPED -- 2 script(s) run, 31 scoped out`; `RUN tests/entities.py` and `RUN tests/harness_headers.py`; `ALL 2360 ENTITY CHECKS PASSED`; `ALL 109 HARNESS HEADER CHECKS PASSED`
RESULT local closure select at 55b74733 against e2a47458=`MODE: SCOPED -- 2 script(s) run, 31 scoped out`, the same two scripts
RESULT structure at 55b74733=`STRUCTURE RATCHET PASSED`, rc 0
RESULT architecture score at 55b74733 (`--diff origin/main`)=`Architecture score: dS +0.0000 NULL`, rc 0
RESULT harness headers, uncontended at fccae47c=`ALL 109 HARNESS HEADER CHECKS PASSED`, rc 0 (an earlier run begun at load1 ~130 read `13 of 109 ... FAILED`, every failure under `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py` hitting its own 900 s wall cap; the clean run is the number)
RESULT the four cited jobs, Actions API: `2bd5e90f` job 118675172846 14:09:00Z->14:39:19Z cancelled 30:19; `4e5801eb` attempt 1 job 118679535262 14:17:24Z->14:47:33Z cancelled 30:09; `916431ae` job 118688693484 14:34:41Z->15:04:48Z cancelled 30:07; `4e5801eb` attempt 2 job 118701134345 14:58:02Z->15:19:33Z success 21:31 -- 4 of 4 exact, each at the run the body names
RESULT phase at cancellation, from each job's own log (download URL `.../actions/jobs/<id>/logs`): `4e5801eb` attempt 1 uploaded its results SARIF at 14:46:11Z and was cancelled 14:47:28Z while `Analysis upload status is pending`; `916431ae` uploaded at 15:02:39Z and was cancelled 15:04:44Z pending; `2bd5e90f` never uploaded a results SARIF -- `Running queries for python` opened 14:27:49Z and `Perform CodeQL Analysis` was cancelled 14:39:05Z, 11:16 later, the only upload in its log being the post-cancellation failed-run SARIF at 14:39:09Z
RESULT class: no other required context runs near its cap at the head -- largest ratio `browser` 3.8/20 min, then `Analyze (python)` 27:17 against the old 30-minute cap
RESULT head checks at 55b74733=every check completed except `coverage` and `Analyze (python)`, both in progress at write and not red; the only failure is `nightly-status` (main-state, exempt, below)
RESULT body at 55b74733 names 55b74733 under `## Head` and its own row; it does not state that `.github/workflows/` is code-owned and needs tvofi's approving review (CODEOWNERS `/.github/workflows/ @tvofi`)

## Why blocked

The two added comments -- `.github/workflows/codeql.yml` lines 185-188 and
`tests/entities.py` lines 20311-20314 -- assert that all three cancellations
fired "while uploading results rather than hung". Two of the three were in the
upload-processing wait; the 30:19 run was not: it was cancelled during query
evaluation, and the "Uploading results" at the tail of its log is the runner's
post-cancellation failed-run SARIF, not the cause. The claim is the paragraph's
only account of where the time went, it is the durable justification attached
to the 45, and one of its own three cited runs disproves it. The cap, the guard
and the remedy are unaffected -- hence a comment correction, not a redesign.
Suggested wording: "two were waiting on CodeQL's analysis processing when the
cap fired; the third was still evaluating queries".

## Notes (non-blocking)

- `nightly-status` is red at this head and at the previous one. Its failure is
  main's `slow` nightly (run 39387919507, head 0c298f6, 2026-10-20T07:39Z); the
  check is unrequired and this diff touches nothing it reads. Carry: dismissed:
  main-state red, exempt for this diff; the orchestrator's on main.
- `PREPR_SKIP_CLOSURES=1` on the local re-push cannot be re-derived from the
  tree; what can be is that it concealed nothing: the pre-update head's
  `closures` job (39482206355) concluded success and the final head's
  `closure-scope` is green, so the closures lane ran at both heads in CI.
  Carry: dismissed: process claim, CI re-ran the lane.
- The body's recarry note names `7f5269fb`, a head superseded by 55b74733 in
  the same push. Accurate but stale; worth trimming when the correction above
  is made. Carry: dismissed: cosmetic, the `## Head` line names the live head.
- `mutation` is green at this head in 0.5 min: the branch writes no production
  Python line, so the lane draws no mutant and the green is vacuous by design.
  The real proof is the mutation result above. Carry: dismissed: expected lane
  behaviour for a workflow-YAML change; the reviewer's own mutant is the proof.
