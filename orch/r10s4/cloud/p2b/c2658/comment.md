Closed unmerged: folded into P2b (R10-CI-LAYOUT-P2), because the cut-over now runs in a ruleset-off window.

The cut-over order is now: freeze, `ruleset_cutover.py --disable`, merge P2b, `--enable`, then main's push `gate`. After the merge, main carries P2b's own graders, so main's base-pinned copies never judge P2b's tree under an enforced ruleset. That makes (a), the `cutoverDrift` reader on main, and (b), `governance_pin`, unnecessary here. No SHARED_GRAMMARS arm was built.

Where the rest went (assembly `ci-probe/all`, branch p2b-assembly):
- (c), the ghapi GET 5xx retry, a P2a defect: 3585c7feb (red test) and 81900c11a (fix), cherry-picked from f17e09d63 and 54c60b5ac.
- Review finding, the surviving `cutoverDrift` mutant (contexts-only comparison): e4a209d7e adds an acceptance row whose `pre_cutover` differs from the post-PUT record in `rulesets`. With the mutant it reads `FIXTURE VACUOUS ... 6 finding(s)`; at head it reads `FIXTURE ok`.
- Review findings on (b), the "6 failed" figure and the entities crash after the stale-`_GOV_FILES` pin: they lapse with (b).
- Review finding, the two `pr-contract` reds on this head (jobs 120336368847 and 120336562671): the `carry_audit` UNROUTED item in `## Forward-carry`, fixed by body_patch at 09:17:50Z. `python3 -I tools/audit/carry_audit.py check --body <body>` reproduces it locally before a push. That RCA answer is recorded in P2b's body.
