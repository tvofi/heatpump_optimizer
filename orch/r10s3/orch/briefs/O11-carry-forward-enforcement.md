FIXER SEAT O11 — make carry-forward mechanical (tvofi request 2026-10-18). Round 10 of tvofi/heatpump_optimizer, part of #201, mandate 6175172275.

WHY: a sweep (/Users/timmalmstrom/hpo-seats/r10s3/finding-sweep/REPORT.md, tool own.py beside it) found 39 of 95 round-10 findings with no owner, although dev/governance/rules/finding-propagation.md already requires every finding to reach an owner. The rule exists; nothing enforces it. Findings leaked from: PR-body "out of scope"/Friction sections, review verdict non-blocking notes, seat reports, RCA countermeasures, SEATS.md notes.

STEP 1 — pre-study (write PRESTUDY.md in your scratch dir, then continue without waiting unless an option needs tvofi): from REPORT.md, tabulate the 39 by WHERE each was recorded and WHY no owner was named. Pick the smallest set of mechanical checks that would have caught >= 90% of them. Count it against the 39 (each row: caught / not caught, by which check).

STEP 2 — build (preferred shape; deviate if the pre-study says so):
a. A destination marker convention: every out-of-scope / non-blocking / friction item written in a PR body or verdict carries `Carry: <GROUP>|#<issue>|O<n>|dismissed: <reason>`. Put the convention in finding-propagation.md (policy file: tvofi approves at merge — say so in the body's Approval section).
b. tools/audit/carry_audit.py (promote own.py into the repo, tests beside it): parses a PR body + its verdict comments; refuses when a finding-shaped item lacks a destination, or names a group/issue/brief that does not exist or is already done/closed.
c. Wire it where it bites: pr-contract (or the closest existing PR-body check) for bodies; merge_train.py pre-flight for verdict notes on the PR being merged; a weekly/at-closure full sweep mode callable from orchestrator_tick.py.
d. Null control: a planted body with an unrouted finding fails; the same body with a Carry: line passes; an invented group name fails. Run it over the last 20 merged round-10 PRs and report the count (expect hits = the sweep's rows from those PRs; compare sets, not totals).

CONSTRAINTS: failing test first; mutation proof; tests/structure.py before push; budgets — if a ci_budgets row is needed, state it (tvofi approves). Conflicts: handoff/r10-tick-drivers (orchestrator_tick.py) and #2386 (prepr.sh) are in flight — do not edit those files; if wiring needs them, write the fold text to /Users/timmalmstrom/hpo-seats/r10s3/O11/fold-<file>.txt instead.

IDENTITY: push refs only via tools/audit/seat/handoff_push.sh (topic r10-carry-enforce) and body via body_push.sh; no GitHub writes. Work in your own worktree from fresh origin/main under /Users/timmalmstrom/hpo-seats/r10s3/O11/. Stop only PIDs you started; never pkill by pattern. prepr cap is 4 concurrent — check the gate lease before running prepr.
REPORT: CODE=<sha> BODY=<sha> plus the pre-study's caught/missed count and the null-control result.
