Fix review: merge c200ad654edad312d1493e0edd41cb2bd7e2897e
bus-nonce: 0066f0b0366fb38b94d58583e568094f
pending-ci: required checks at the head (tests/fast, closures, coverage, browser, env-matrix, instrument-self-tests, prelude) were still running at review time; 17 pass, 0 red apart from the aggregate `gate` job, whose log says only "run(s) at this head are still being judged". Cheap checks (briefs, mutation, typing, policy-docs, closure-scope, arch-score, budget-raise-gate, hassfest, validate-hacs) pass.

Round 1 (full scope). Record-only PR; no production code, so no mutation proof, harness or null control applies (body says n/a, correct: diff touches only dev/ paths).

Verified (evidence in ev/):
- Roster: reconstructed merge base 89acffb1ab, main, branch (80c1fb32c7); `git merge-file` auto-merge conflicts in exactly 3 hunks; head differs from the auto-merge only at those hunks (ev/auto_vs_head.diff). Taken: branch's resume stage/commit for R10-PROCESS-SLIM (note keeps archive/ form) and R10-COP-LEARNER-DRAW-FLOOR (stage carries-open, commit b046b22d6e, branch archive/ form). Absent: main's `stage: in-progress`, `commit: null` (stale, #3593 merged) and the branch's unarchived `handoff/...` spellings; both sound. Parses; brief_lint rc 0 at head, same error counts as main.
- Delivery rows: all six merge shas equal the API's (ev/merges.txt); 3590 row is byte-equal to record_row.row_line(3590, live title, merge sha, None) and matches the group-less shape of existing merged rows (3589). 3608 own row is the open form.
- CLOSEOUT-REPORT.md: ref_privacy body-lines rc 0, no host path/account grep hits; under INERT prefix dev/audit/.
- HANDOVER: updated-for a39627da59 reachable from head; merge shas, open PR list (#3598 #3602 #3551 #3566 #3420 #3529 plus this PR), hacs/default 14201 open all match gh/git; no stale open-state sentence on those PRs survives (grep).
- VERSION, manifest, RELEASE_NOTES, both claim files untouched; merge-tree of head onto main clean (rc 0); carry_audit with the body: 0 findings.

Note: handover-volatility: HANDOVER.md line ~338 "A new orchestrator session took round 11's single-writer lock" is running-session state that writing-for-agents.md keeps on #3394; drop it. Carry: R11-INTAKE-R10-RESIDUE
Note: unverified-quote: the 2026-11-15 owner ruling quoted verbatim in HANDOVER.md (instrument triage) I could not re-derive from git or gh; the orchestrator should confirm the wording against the sweep log. Carry: R11-INTAKE-R10-RESIDUE
Note: body-figure: "25 merges" from `record_row.py --enumerate --since ee9e23372c^` not re-run (needs API attribution); the five derived rows are consistent with git log first-parent. Carry: R11-INTAKE-R10-RESIDUE
