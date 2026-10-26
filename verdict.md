Fix review: merge ac96f4c35659dd3c99f6155b6290cf437ce7742f

bus-nonce: 212a1c44640251bec096b192f77b6627

Round 1 review of #2844 (roster batch 16), measured at head ac96f4c35659dd3c99f6155b6290cf437ce7742f; the head was re-read before return and is unchanged. Roles diff against origin/main is empty, so this contract is current.

## Findings

- The set-stage op 02f265488 (R10-PLAN-ISSUES-CHART queued -> done) cites no merged PR in its commit message, in an op note (set-stage writes none) or in the group's brief, which cites only the owner request of 2026-10-25 that created the group; the PR body does not name it either. The stage is factually earned: #2833 (R10-PLAN-ISSUES-CHART) merged 2026-10-26T01:11:45Z as 63a1c5fe8 on main. Carry: R10-ROSTER | #201 | O1 | dismissed: the fact is verified against a merged PR (#2833), so no roster or brief change is owed for this batch; the citation gap is roster_edit set-stage writing no note, a shape every set-stage op shares, not a defect of this PR.

## Evidence

- RESULT roster-semantic-diff: 195 groups both sides; exactly five groups differ; four carry lists each gain one item and lose none (R10-FLOW-JIDOKA 21->22, R10-FLY-DEPGRAPH-STALE 3->4, R10-ORCH-PLANPAGE 6->7, R10-FLY-LEDGER-SAMPLE 1->2); R10-PLAN-ISSUES-CHART resume.stage queued->done; stage counts done 123->124, queued 11->10. Every '-' line in the textual diff is the same item re-emitted with a trailing comma. No carry is dropped, so no re-route is owed (ev/roster_semantic_diff.txt, ev/figures.txt).
- RESULT citations: e580153ed (JIDOKA) cites #2835 and a main ruling under mandate 6329234399; a1cefa714 (LEDGER-SAMPLE) cites #2840 and the same mandate; 8e61c60c8 (DEPGRAPH-STALE) cites Dependabot #2678, #2811 and the same mandate; d373c351f (PLANPAGE) quotes tvofi 2026-10-26 twice. Mandate 6329234399 is a tvofi comment on #201 (2026-10-21T23:56Z, scope all, until 2026-11-04T18:14Z), in force. #2835 and #2840 are open policy issues; #2811 merged 2026-10-26T01:09:27Z, so the #2678 carry's precondition already holds. set-stage 02f265488: see Findings.
- RESULT delivery-row: dev/programme/delivery/2844.md is present in the three-dot diff (1 line, open).
- RESULT carry_audit: `carry_audit.py check --body` on the PR body, with and without --roster-ref origin/handoff/audit-r10-roster, prints 0 finding items, 0 unrouted, exit 0 (ev/carry_audit.txt). The body's Forward-carry and Friction are none.
- RESULT brief_lint: `node tools/policy/brief_lint.mjs` in a detached worktree at the head (whose tree is the merged tree eed16646, full history and tags) prints TOTAL: 0 error(s) across 48 file(s), exit 0; the ERROR lines in the log are self-test fixtures (ev/brief_lint_head.txt). The body's "10 error(s)" on fresh-init archive extracts I could not re-derive: the same method prints 363 on both origin/main and the head here (ev/brief_lint_noTags.txt). Delta zero holds in both measurements, so the body's conclusion stands; its absolute count is not verified.
- RESULT merge: `git merge-tree --write-tree origin/main ac96f4c35659dd3c99f6155b6290cf437ce7742f` exit 0, tree eed1664666c54a30a9cd5968a3b03af81ead566b, equal to the head tree (origin/main 7d2056970 is already merged in). The authored tip d373c351f merges to e2acc8463d1e..., as the body says; `git diff --stat origin/main e2acc846` reproduces the body's 9 insertions, 5 deletions. Blob hashes 6c8e6f46 (main) and 36ed196b (head) reproduce (ev/merge.txt).
- RESULT version: VERSION, the manifest and RELEASE_NOTES.md are untouched (the diff names two files).
- Mutation proof and finder's harness: n/a; the diff writes roster state and a delivery row, no code line, so no mutant is drawn.
- CI on the head, all concluded: 42 success, 25 skipped, 1 failure (ev/check_runs.tsv). The red is governance / delivery-status: main's backlog of 18 overdue rows for other PRs (#2821 ... #2795); #2844 is not among them and the diff deletes no row, so it is not this PR's. It is not a required context and does not block. pr-contract ran green three times after that red concluded (last 02:34:54Z), which is the evidence for step 11.
- Head check: PR head and refs/heads/fix/audit-r10-roster-pr are ac96f4c35659dd3c99f6155b6290cf437ce7742f at return.
