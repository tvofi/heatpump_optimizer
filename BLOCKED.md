# BLOCKED: body_push.sh exit 4, REFUSED CARRY-LANDED

Topic r10-cop-learner-draw-floor, fixer seat.

- Code head: a827c3d985b240fabcc83215e0d35a9692e8fca9, pushed to refs/heads/handoff/r10-cop-learner-draw-floor. It is the first head `tools/pr/prepr.sh` passed clean with the body (rc 0, receipt written for a827c3d985b2).
- Refused body: kept by body_push.sh at refs/heads/handoff-wip/r10-cop-learner-draw-floor-body, 9068dce573080b00ee6bd01d69fef251ee2000f1.
- What blocks: the body's 14 carries are not yet in their groups' briefs or carries. They land on the round's roster branch, which this seat may not write. The relay folds them and re-runs body_push.sh; this seat owes nothing further until then.

Output of `bash tools/audit/seat/body_push.sh r10-cop-learner-draw-floor <BODY.md>`, verbatim:

~~~text
fill-red: `## Red checks` already names mutation; nothing written
figure_block: refreshed 1 block(s) at a827c3d985b2
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-COP-LEARNER-DRAW-FLOOR at a827c3d985b2, 3 live, 3 dispatched carries, 0 refused
CARRY-MISSING R10-COP-LEARNER-DRAW-FLOOR body item 09c5aa75: not in its brief or carries: '- Departure 1, where the release runs (behind the freeze gate in `_fold_measured_cop`, not in `_lear'
CARRY-MISSING R10-COP-LEARNER-DRAW-FLOOR body item 5b2b2810: not in its brief or carries: '- Departure 2, a replay does not feed the capacity envelope: a held departure asked at or above 0.95'
CARRY-MISSING R10-COP-LEARNER-DRAW-FLOOR body item ade1b168: not in its brief or carries: '- Note n2, the one-cycle scale move: the instrument is the harness row `true_0.6_max_cycle_move` (`#'
CARRY-MISSING R10-COP-LEARNER-DRAW-FLOOR body item 870278d1: not in its brief or carries: "- Design decision, owner: where the evidence is unobtainable a departure keeps base's rule (built he"
CARRY-MISSING R10-COP-LEARNER-DRAW-FLOOR body item 28d8e538: not in its brief or carries: '- Design decision, owner: the cap reads run-asked draws only, so an install with an overstated minim'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item bb796039: not in its brief or carries: '- Residual, measured and not built (no finding in the brief asks for it): before the evidence exists'
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS body item fe86c735: not in its brief or carries: '- Design decision, orchestrator: group C of design/R11-OUTSIDE-HONEST-STARTS-RUNS (0c692c86d2), the '
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item f2abf2d0: not in its brief or carries: '- Carry 2, the band measurement, stays open on named owner data: a diagnostics download with the wee'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item e97e01d8: not in its brief or carries: '- Note n4, checked: a diagnostics download publishes no running-draw window rows (`draw_range.diagno'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 1e3849ec: not in its brief or carries: '- Note n9: when fix 3 adds a `COP_REFUSED_*` literal, the same pull request owes its `health.cop_rea'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 40807f25: not in its brief or carries: '- Four harnesses stop with a traceback on origin/main 9fdba3b8547f, before this diff, each run as `P'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item cf9d2161: not in its brief or carries: 'designer.md: unenforced: the approved note reuses `_fold_cop_evidence` for the replay and calls `rel'
CARRY-MISSING R10-COP-LEARNER-DRAW-FLOOR body item b4659e0c: not in its brief or carries: 'fixer.md: contradiction: step 17 has the architect note followed and a departure raised, not made; s'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 837668dc: not in its brief or carries: 'figure_block.py: cost: the `scope-line` block renders `MODE: FULL` for a branch whose merge base pre'
CARRY-LANDED: 14 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
fatal: expected 'acknowledgments', received 'packfile'
warning: push negotiation failed; proceeding anyway with push
remote: 
remote: Create a pull request for 'handoff-wip/r10-cop-learner-draw-floor-body' on GitHub by visiting:        
remote:      https://github.com/tvofi/heatpump_optimizer/pull/new/handoff-wip/r10-cop-learner-draw-floor-body        
remote: 
body_push: refused body kept at handoff-wip/r10-cop-learner-draw-floor-body 9068dce573080b00ee6bd01d69fef251ee2000f1
~~~
