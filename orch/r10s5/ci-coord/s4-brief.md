You are the local P2b COORDINATOR seat for roster group R10-CI-LAYOUT-P2 of tvofi/heatpump_optimizer, round 10, session s4. P2a (#2622, the umbrella engine, inert) merged at a1633381adadcf9e94c477bf651dfe94ba229c5c. Your job is to drive P2b, the cut-over, through its unit pipeline to an open, review-ready PR, exactly as the approved execution plan says.

Binding sources (read them; do not work from memory):
- Plan: `git show 1011d6b2f:plans/ci-layout/EXECUTION.md`. Read all of it, especially sections 1 (units, seats, and where each lands), 2 (every GitHub write and who performs it), 3/3.1 (P2a then P2b, and P2a's interface contract), 4 (order of work: steps 4-12), and the decisions in section 0. The design refs it cites are probe/design-ci-rev4 and probe/design-ci-review5.
- Group entry, all 9 carries included: `git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json | jq '.groups[]|select(.group=="R10-CI-LAYOUT-P2")'`. Carry 8 requires the forgery pin to refuse `statuses: write`, with a planted fixture.
- #2622's PR body: what P2a deferred to P2b.
- dev/governance/roles/orchestrator.md and fixer.md; CLAUDE.md.

Work from /Users/timmalmstrom/hpo-seats/r10s4. Make your own worktree, p2b-coord, off origin/main. Put tools/audit/seat/shims first on PATH. Set PREPR_SKIP_CLOSURES=1 for any prepr.

Your constraints:
1. You cannot call RemoteTrigger. Cloud unit seats are fired by main. For each cloud batch the plan calls for (batch C: U1+U2+U7, U3, U4, U5; batch D: U6, U8, U10, U11; then U9b and U9p; plus any batch-B unit not yet handed off, i.e. U0c, U9a, U9d), first check which unit handoff refs already exist: `git ls-remote origin 'refs/heads/handoff/*ci*' 'refs/heads/ci-probe/*'`. Then write one complete brief per seat under /Users/timmalmstrom/hpo-orch/r10s4/cloud/p2b/<unit>.md. Each brief must say:
   - the unit's scope, verbatim from the plan's section 1 row;
   - its input refs, stacked on P2a's merge;
   - its handoff ref name;
   - PREPR_SKIP_CLOSURES=1;
   - "spare the GitHub API";
   - "no Claude Code footers, Co-Authored-By/Claude-Session trailers or claude.ai session links";
   - the return signal, a handoff/<topic> push.
   Then SendMessage main the line `fire-owed p2b <unit> <absolute brief path> <model>`. Model: sonnet for units the plan marks sonnet, opus otherwise. At most 4 concurrent cloud units, per the plan.
2. Live probe steps (U0 live, step 4; the step 6 and step 8 live runs) are orchestrator-run writes in the plan's section 2. You may run the instruments the plan assigns to the orchestrator: ci_probe.py push/dispatch on probe refs, and sweep_driver --nochain. They act as main's delegate under mandate 6329234399. Cap them at the plan's API budget, and poll no faster than every 60 s.
3. NEVER perform write 20, the ruleset 23698884 PUT (`ruleset_cutover.py --apply`). It is tvofi-only. Prepare its --dry-run output and rollback file for P2b's body instead.
4. Integration (step 10) is yours: cherry-pick unit handoffs onto ci-probe/all, run unitcheck2.py static against current main, then the combined control, then selftest_wiring.py --check (expect N, N, 0).
5. Open P2b (step 11) with tools/audit/seat/open_pr.sh, including the ruleset PUT staging the plan requires in the body. Then SendMessage main "REVIEW 2xxx <head>" so main dispatches the opus reviewer. Do not merge anything; the merge seat and main run the freeze and cut-over (step 12).
6. Report progress to main by SendMessage at each step boundary, one line each. Put decisions you can't make to main as well. Never post issue or PR comments yourself.
7. If you find a defect in P2a's merged code, the fix goes into P2b with a failing test first (fixer.md). Do not open a separate PR.

Start now with step 0: the inventory of which units already have handoff refs and verdicts, and which plan steps are complete. Send it to main, then send the first fire-owed batch. End with RESULT / CHECKS-RUN / UNCERTAINTIES / ESCALATE.
