R10-COP-GATE fixer s10 (nonce f13245d611f85ed8) state

Part 1 (topic r10-cop-gate): worktree wt/, branch work/r10-cop-gate-s10.
- 0b8e0e970 (killed s8 seat's head, two commits past 575ba5f61) + merge of origin/main edd7e0e14 (572ed657a)
  + d3ce1d33f (InstallCapability.cop_electric: fixes entry-config census STRAY in _learning_view that 2c3de4661 introduced).
- Body: body.md (GATE_RESULT placeholder until the scoped gate at d3ce1d33f finishes; ev/gate.txt).
- Evidence: ev/, mutants mut/*.log, drivers tools/cg_block.py, tools/mutant.sh.

Part 2 (topic r10-cop-gate-p2): worktree wt2/, branch work/r10-cop-gate-p2, from d3ce1d33f.
- Uncommitted: carries 13/16 _fold_flow_lift reads heat_energy attribution; features check
  "the flow-bias fold reads the observed dwell ..." (fails before, passes after; mutant p2m1_attr kills it).
  structure.py --record for a class_excess_loc gain pending.
- Still owed in part 2: carries 6, 7, 14 (heat-pump grade hover codes / plain words / envelope_drivers mirror),
  9, 10 (vent latch VERIFY + designer note), 12 (learned top consumer), carry 8's unaligned_meters control.
