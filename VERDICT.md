Fix review: merge a95b50b17ab10277b578de0e2d93602d31a87005

bus-nonce: e5c37caa634c964206047ce10dac1c3d

Round 1 review of PR #2595 at head a95b50b17ab10277b578de0e2d93602d31a87005 (fixer's a8f339d9a + merge of main 07fcbee2e + delivery row). Measured from a detached worktree at that head; head re-read before posting, unchanged. Contract copy current (`git diff merge-base...origin/main -- dev/governance/roles/` empty).

RESULT policy_lint head a95b50b17: TOTAL 0 error(s) across 43 policy file(s)
RESULT policy_lint origin/main 07fcbee2e (clean worktree): TOTAL 1 error(s), the [budgets] orchestrator.md 4515 > 4513 files_tokens line
RESULT mutant (main's orchestrator.md restored at head): TOTAL 1, same [budgets] error; restored, tree clean
RESULT bytes/tokens: 93e6a63d2 18009/4502, 6077bf70e^1 18025/4506, 6077bf70e^2 18045/4511, 6077bf70e 18061/4515, 07fcbee2e 18061/4515, head 17924/4481; --budgets row: 316 lines (cap 319), ~4481 tokens (cap 4513)
RESULT budgets: no *_budgets.json or policy_budgets.json touched; VERSION/manifest/notes untouched (diff = orchestrator.md + delivery/2595.md)
RESULT carry_audit check --body: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)
RESULT merge-tree --write-tree origin/main head: clean (rc 0, tree 295267445)
RESULT rules_sync --check: ok
RESULT closure select (workdir out of tree): MODE: SCOPED -- 1 script(s) run, 32 scoped out (tests/entities.py)
RESULT run_always local: env_drift --claims-only rc 0, closure.py selftest rc 0, layout.py rc 0; harness_headers.py not re-derived locally (seat venv-ci lacks homeassistant) -- cited from CI fast (3.14) success
RESULT check-runs at head (API, 48 runs): 31 success, 16 skipped, 1 failure = nightly-status (grades main; the diff reaches nothing it reads; not this PR's per fix-review.md step 11). policy-docs, env-matrix, instrument-self-tests, fast (3.14), pr-contract: success.

Obligations (each changed sentence vs main; evidence/obligations.md): s0 still binds follow-not-relay of every rule and contract; s2 keeps the independence rationale and the "dispatch it" bullets untouched -- drops only main's self-contradictory "must then review" gloss; s10 keeps "a comment, including yours on #201, is not propagation", cuts a motive clause; s14 keeps "yours to make and to state", "not to skip" was emphasis already implied by "make". No obligation dropped or weakened.

Step 14: the only moved number (file size) is earned by the cut -- the mutant restores 4515/red. Cap left at 4513 with 32 headroom, not re-recorded to zero.
Step 11: the red on main (policy-docs, env-matrix, instrument-self-tests, fast) is named and answered in "Red checks" with a cheaper detector (policy_lint --budgets on the merge result; merge_train batch proves only batches). Root cause routed to R10-POLICY-LINT-FAMILY; judged the PR, not the RCA.

Body figures not reproduced (non-blocking, body-only; no stage changes):
- "wc -c ... 17925 at the head": measured 17924 at a8f339d9a and at the head (token figure 4481 holds either way).
- Null control "Only orchestrator.md differs (git diff --stat origin/main...HEAD)": at this head delivery/2595.md also differs (true at a8f339d9a only).
- "## Head" still carries a superseded paragraph for d0f9c95b8 (a replaced row commit, not an ancestor of the head) beside the correct a95b50b17 one.
Carry: none -- the three notes above are this PR body's own wording; they change no later stage.
Carry: R10-POLICY-LINT-FAMILY -- unchanged from the body's own carry (root cause of the semantic-merge red); no new finding added by this review.

Evidence: ~/hpo-seats/r10s4/rev2595-ev (HEAD.txt, policy_lint.txt, obligations.md, check-runs.tsv, body.md)
