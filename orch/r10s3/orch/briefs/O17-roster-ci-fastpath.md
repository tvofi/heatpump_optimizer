# O17 — make roster changes cheap to land (tvofi 2026-10-18)

tvofi asked: keep the roster and state docs from costing CI. The state docs are already off main (`tools/audit/seat/state_docs.py` writes the orphan ref `handoff/audit-r10-plan`). The roster (`dev/programme/rosters/wave-r10-groups.json`) is on main for three reasons:
- `finding-propagation.md` requires a carry to be in the tree before the producing PR merges. Measured case: #2373 waits on roster PR #2384.
- CI runs `brief_lint.mjs` over it.
- main is the durable record (`orchestrator.md` §5b).

Seats and tools already read `handoff/audit-r10-roster` live, so only landing on main costs a PR.

## Phase 0 — PRE-STUDY FIRST (report, no code), about 1 hour

For each item below, answer: feasible? mechanism? files touched? policy or code-owned paths (tvofi approval at merge)? what enforcement is lost, and how it is kept? cost estimate? recommendation (do / do differently / don't)? Measure, don't argue. For example: what a roster-only PR runs today (its check-runs; #2384 and #2380 are examples), its wall-clock to green, and how many roster PRs round 10 has merged.

1. **Batch roster merges.** The orchestrator lands the roster on main only when a carry must be in the tree, or at a stamp. Is any instrument or check assuming the roster on main is current, and does it go stale under batching? Candidates: the tick, `state_docs.py` defaults, `roster_lib.py` default ref, `delivery_status.py`, `queue_pre_flight.py`, `open_pr.sh` preflight.
2. **Fast-path roster-only PRs.** A PR touching only `dev/programme/rosters/` runs just the gates that read it (brief_lint, the policy and record checks, pr-contract) and merges without a fix review, like a `record:` PR. This needs workflow path filters and a required-checks or ruleset question: a skipped required check must still report. Find the existing pattern (record-autofix, `record_row.py --automerge-check`) and say whether to extend it.
3. **Carries read from the roster ref.** The carry checks (brief_lint carry check, `fix-review.md` step 10, `prepr.sh` carry destinations) read carries from `handoff/audit-r<N>-roster` rather than main, so a producing PR stops waiting on a roster merge. State exactly how the "in the tree" guarantee survives a session ending, for example by landing the roster at each stamp or closure. This rewords `finding-propagation.md`, so it is policy.

Reply PRESTUDY=<absolute path of report> with a per-item recommendation, then STOP and wait. The orchestrator decides which items to build.

## Phase 1 (only after go-ahead)
Build the approved items as one group (or one PR per item if the files are disjoint): failing test first, mutation proof, self-tests, `fixer.md` throughout. Hand off as `handoff/r10-roster-fastpath` plus `handoff-body/r10-roster-fastpath`.

Identity: push refs only (`tools/audit/seat/body_push.sh`, `git push` of handoff refs); never open a PR or post. Scratch and worktree: /Users/timmalmstrom/hpo-seats/r10s3/O17/ (absolute). Seat venv shims go first on PATH. Load is high: no full gate locally; cite CI check-runs. Stop only PIDs you started.
