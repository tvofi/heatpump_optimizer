Fix review: merge 82443a023ac7187e6cc580d0c8b5e752cbd6c583

bus-nonce: dcfdca5f5af75362491a9caa47d74e1a

Round 1. Reviewer r10-raise-reviewer, from a detached worktree at 82443a023ac7187e6cc580d0c8b5e752cbd6c583; contract `dev/governance/roles/` current at the merge base (three-dot diff to origin/main empty).

- Policy text: CLAUDE.md rule 2, ratchet-budgets.md and the 0013 amendment state an agent raise only under a mandate in force scoped `budget-raise` or `all`, and only after no payment (move/delete/share/refactor) that arch_score does not read as worse and judgement finds sounder; the body owes `## Raise justification` with `Payments tried:` and score.py's `Architecture score: dS <n> <verdict>` line. Outside a mandate the owner's own review is unchanged. Nothing wider found; the change narrows the 2026-10-02 mandate amendment. The prose-cap extension (step 1's cuts count as payments) adds payments, not raise permission.
- RESULT budget_raise_gate self-test at head: 235 checks, 0 failed (python 3.14.7).
- Perturbations, all refused by the self-test arms I ran: expired mandate (`justification: an expired mandate is refused`), edited mandate (`a mandate edited before/after the review fails`), no mandate, missing score line, missing payment line, figures outside the section, heading as substring, empty body, failed body read (fail closed, unit and e2e).
- My own probes of `justification()`: a `###` heading, a score line without score.py's verdict word, and figures without payments all refused; a bulleted valid section passes. The regex matches score.py:95's own format.
- Mutation proof (my mutants): justify skipped -> 8 failed; justification always true -> 8 failed; score regex loosened -> 1 failed; section boundary removed -> 1 failed; decide passes no justify -> 8 failed. All killed.
- The gate fires on `pull_request: edited`, so a body edit re-grades. merge_train's policy reader passes no justify; raises remain graded by the required budget-raise-gate check.
- CI check-runs at the head (commits API): all concluded success/skipped/neutral except `nightly-status` (failure: "slow failed last night"; not a required context, and this diff does not reach the slow lane). No red check owed an answer.
- merge-tree against origin/main: clean, exit 0. rules_sync --check: ok. VERSION, manifest, notes and claim files untouched.
- Delivery row dev/programme/delivery/2211.md: correct pre-merge row, carrying record_row.py's OPEN_ROW_TITLE, as #2206/#2207 do; delivery-status green.
- Not verified: the body's mutant counts (M1 13 failed etc.) were measured by the fixer's own scripts; my mutants differ in form, so the counts are not re-derived, only that each class is killed.
