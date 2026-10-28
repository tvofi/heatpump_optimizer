# fix-2873-s10 state (round-5 repair of #2873, R10-DIAG-AGES), stopped at the 2 h wall 2026-10-28T10:27Z
- worktree: wt/ (branch fix2873-s10, locked), code head 060c9bef5c4b77adc5ee77d50f21bd5c06393fb8 on PR head d00790305
  - d05d521ff tests only (card.mjs reads PROBLEM_WORDS keys + per-table en/sv checks; debug_collect census holds PROBLEM_WORDS == published)
  - 060c9bef5 fix: PROBLEM_WORDS gains "stale" (no output moves)
- wt2/: detached clean copy at 060c9bef5 where prepr runs
- DONE, all green at 060c9bef5: card.mjs (needs NODE_OPTIONS=--max-old-space-size=8192 on this host, else OOM rc 134), debug_collect 158/158,
  structure.py, ci_predict (no red), closure select SCOPED 27, archscore dS +0.0012 vs base / NULL vs d00790305, landed harness identical.
  Failing first at d05d521ff: card census FAIL (stale), dc 1 of 158. Mutants K1-K4 all killed (mut-results.txt), round-4 N-set re-taken (mut4-results.txt, mut4-n5-features.txt).
- body: body-r5.md (assemble: cat part-intro part-r5-top part-r5-mid part-r5-fig part-arch part-r5-red part-tail); only PREPR_LINE in part-r5-red.md left to fill.
- prepr DONE: no refusal, rc 0, 3728 s; PREPR_LINE filled, body-r5.md assembled and ready.
- REMAINING: fill PREPR_LINE from prepr.log; reassemble body; from wt: git push origin 060c9bef5:refs/heads/handoff/r10-diag-ages;
  bash /Users/timmalmstrom/hpo-seats/r10s6/orch-wt/tools/audit/seat/body_push.sh r10-diag-ages /Users/timmalmstrom/hpo-seats/r10s6/fix-2873-s10/body-r5.md /Users/timmalmstrom/hpo-seats/r10s6/fix-2873-s10/RESUME.md;
  then (venv-ci python first on PATH, no timeout wrapper) bash /Users/timmalmstrom/hpo-seats/r10s6/orch-wt/tools/audit/seat/update_pr.sh fix/r10-diag-ages 060c9bef5c4b77adc5ee77d50f21bd5c06393fb8 /Users/timmalmstrom/hpo-seats/r10s6/fix-2873-s10/body-r5.md;
  verify git merge-base --is-ancestor 060c9bef5 origin/fix/r10-diag-ages.
