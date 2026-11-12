# BLOCKED: r10-mach-scorecard

Question: The ten scorecard lines (A_gate, A_run, Y_rev, M_first, Y_train, H, S, E, C, K), each with its rule and null control, are defined in "the study plan's section 7" and in a 62-line reference script. Neither is in the tree or in any ref I could reach (carry SCORECARD-LANDS-AS-BEAT-ROW, wave-r10-groups.json; triage s6-batch218.md P664 says the scorecard lives only in a session directory outside the tree). Where can the section-7 rules, null controls and the reference script be read (a path or a ref)? Without them I would be inventing the rules, so I have written no code.

Searched: git grep A_gate/M_first/Y_rev/scorecard/FAMILY over origin/main and git history; only OpenSSF standards scorecards match.
