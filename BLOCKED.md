# BLOCKED: r11-pre-new-dimensions (fixer), no code written

Question: Both `After:` predecessors are unmerged at the dispatched head, so the brief's start condition ("the fixer starts on Design review: approve and after both merge") is half met. Re-dispatch this seat once both are on main, or rule that it builds stacked on their handoff heads?

Measured at origin/main e0ad8b2bd32b60a67975039f8573dbba2207757f, 2026-11-15T17:30Z:

- Design review: met. `git show origin/design-verdict/R11-PRE-NEW-DIMENSIONS:verdict.md | head -1` prints `Design review: approve a9377bcf47957e63060733e61a9cb551a8734b1c`.
- Evaluation: met. `eval/r11` tip 9de7c2bdc7, `review.verdict` approve of 02a48db212.
- R11-PRE-FINDER-CONTRACT: not merged. `git merge-base --is-ancestor origin/handoff/r11-pre-finder-contract origin/main` exits 1; pull request #3621 is an open draft. The base copy of `tools/policy/check-wave-script.mjs` that grades this group's `audit-find.js` hunks is therefore the old one.
- R11-PRE-BRIEFS-CENSUS: not merged. The same command on `origin/handoff/r11-pre-briefs-census` exits 1; no pull request is open for it. `tools/audit/enumerate.py` (the `d16-writes` and `d17-features` universes both new briefs cite, carry 1) is absent from main: `git cat-file -e origin/main:tools/audit/enumerate.py` exits 128. Its head also rewrites `scopes.json`, `rotation.json`, `policy_budgets.json` and the D1, D8, D12 briefs this group's territory argument reads.
- Null control: the same ancestor test on `origin/main~1` exits 0.

Why not stacked without a ruling: `fixer.md` cuts the worktree from `origin/main`, and a head stacked on two unreviewed handoff heads is re-cut each time either moves under review.
