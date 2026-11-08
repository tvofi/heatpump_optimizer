# r10-hotfix-codeql-headroom: prepr.sh refuses in this container

Change is done (head below): `.github/workflows/codeql.yml` sets
`timeout-minutes: ${{ matrix.language == 'python' && 60 || 45 }}` and
`tests/entities.py`'s cap check resolves it per leg.

Measured on main's ci.yml push runs, 58 completed `Analyze (python)` jobs:
p50 41.7 min, p90 45.0, 8 cancelled at the 45-minute cap (censored, so p99 is
not measurable, >= 45.1). 60 = cap plus the ~15 min margin the 45 had.

`tools/pr/prepr.sh` step `closures` REFUSEs: `tests/entities.py` exits 1 here
with 3 of 2665 checks failed (coverage-job reuse, release ZIP, Pages
workflow). The same 3 fail on a clean worktree of origin/main 6188936a, so they
come from this container, not the diff. The codeql cap check passes. Every
other prepr step printed ok. Mutants/wall time: not run to completion
(prepr was stopped at its time limit).

Question: hand off from a container where entities.py is green, or accept this
head as is?
