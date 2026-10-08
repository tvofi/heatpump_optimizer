Fix review: merge 539d300b8d4d1037fc3ed98503e6f49224e125a0
bus-nonce: 334a1cb7b35d7e7ffb23f1e94f66a1be

PR #2062 (#2028 RCA + fix), round 1. Measured at 539d300b8d4d1037fc3ed98503e6f49224e125a0 (live head re-read at posting: unchanged). Detached worktree; roles/ three-dot vs origin/main empty (contract current).

## 1. Is the named cause the real one? Partly -- and the RCA says so with counts.
- Bus re-derived independently (35 review refs now; RCA's 34): RESULT 104 verdicts / 54 blocked / 19 root-cause-unanswered. The 6 extra verdicts are all after 14:00Z, past the RCA's 13:29Z window; the RCA's 98/52/19 set is an exact subset (comm: 0 only-theirs).
- The dispatch's examples map onto the RCA's classes: #2053 6ddb8c4c = D (the token defect); #2058 aa88452d = A (the contract had already refused it at +0); #2058 e8701d2e = C (no pull_request contract run at that head); #2059 9e44f73c = A; #2051 811846b5 = B (the verdict came before the workflow settled). The RCA does not claim the token explains all 19: A 7, B 5, D 1, C 6. It keeps #1985's (c) for A and B and proposes the dispatch-timing lever (section 6, item 3) for the owner without landing it. The partial cause is stated with counts, as owed.

## 2. The fix
- CI at this head runs the new step with the token. Both pr-contract jobs (113370311952, 113370497626) print `record red-history 3 commit(s) ... delivery-status, nightly-status` and `PR-BODY: 0 error(s)`. Before the fix, 35/35 logs printed skip; spot-checked 112484565476 and 113220546508 (#2053), both `skip red-history`.
- Replays use my own standalone clone, the program at the base as CI restores it, the bodies from GraphQL userContentEdits, and the paths and existing lists from three-dot:
  RESULT #2053 body@08:19Z, no token: skip, rc 0 | token: record 6 commits, ERROR closures unnamed, rc 1  (refused at push, as the RCA states)
  RESULT #2053 body@10:55Z (null), token: record, rc 0
  RESULT #2058 aa88452d body@12:28Z (class A), no token: rc 1 (delivery-status) | token: rc 1 (delivery-status, closures, nightly-status)
  So the token moves only class D to push time. A was already refused, and B cannot be caught at push. That matches the RCA's own split, so it is not a defect.
- Security: the trigger is `pull_request`, not `_target`. The job's permissions are contents, checks and pull-requests, all read. The step runs only the base-restored policy_lint; no pull-request program runs before it in the job. Three earlier steps in the same job already hold GH_TOKEN, so no new exposure. A fork pull request gets a read-only token anyway. pr-contract's own reds are excluded from the history (failingCheckNames skips PR_CONTRACT_CHECK). The rerun workflow's job attaches to main, not to the branch commits.
- Pin mutation, full tests/entities.py in the CI venv (Python 3.14.7):
  RESULT head: ALL 2214 PASSED | M0 delete env line: 1 of 2214 FAILED (the pin) | M1 comment it out: 1 of 2214 FAILED (the pin). Null control ok in all three.
  I extracted the predicate verbatim and drove it over planted variants (my own harness, evidence/pin_mutants.py). The pin kills: moved to the next step, empty value, a token only in the run block, the wrong secret. It accepts `GITHUB_TOKEN:`. It REFUSES the equivalent `${{ github.token }}`, which is over-strict but safe. Not blocking.
- Class-open (step 6): I grepped every GITHUB_TOKEN/GH_TOKEN/ghCredential reader in tools, .claude/workflows and tests. The other policy_lint ghGet callers (fetchPullsBySha, fetchWindow) belong to --record and --stats, which refuse loudly through requireToken and never run in --pr-body mode. That agrees with RCA section 5: one silent skip.

## 3. Cost test, re-derived from my bus read
- RESULT the 7 body-only repairs, block to the next merge verdict: 13, 173, 27, 92, 81, 76, 112 = 574 min, median 81. #2049 is counted from its second root-cause block at 07:18Z. By class: A 249, B 92, D 112, C 121, and A+B 341. All match.
- RESULT 65 revisions of the step from a07dd57d3^ to the merge base, 0 holding a token. Matches.
- The 5 s standing cost is the RCA's own figure; I did not re-time it.

## 4. Closes #2028 sits on its own line in prose. It is the only closing keyword.

## 5. CI at the head, read through the API
- Every required check is completed and green except two reds. delivery-status (113370313070) and nightly-status (113370311445) are main's reporters. The diff (pr-contract.yml, entities.py, dev/audit/rca/**) reaches neither. The contract's reporter exemption passed the body with both listed, and step 11 says they are not this pull request's red. coverage was still in progress at posting; it is not a required check (coordinator).
- merge-tree against origin/main 0b89f781 gives rc 0. origin/main equals the merge base.
- VERSION, the manifest version, the notes heading and both claim files are untouched. No budget file is touched.

## Not blocking, for the orchestrator
(a) The red-history walk now costs about 1 + N_commits GITHUB_TOKEN calls on every contract run, including each body edit. The repo-wide GITHUB_TOKEN limit is about 1000/h, and a failed read fails the contract closed (`could not be derived`). The RCA's cost test names only time.
(b) RCA §6 item 3 changes fix-review.md step 11 and orchestrator.md. Today it lives only in the RCA. It needs surfacing to tvofi on #201 or in the HANDOVER owed-work, or it will not reach a decision.
(c) The workflow is code-owned, so the approving review is the orchestrator's or tvofi's, not this verdict.

Evidence: /Users/timmalmstrom/hpo-seats/review-2062/evidence
