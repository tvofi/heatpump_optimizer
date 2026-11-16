# R11-OUTSIDE-SELF-SETTING-PUMP: fixer blocked before code

Question: which clamp remedy does the owner rule for the D4 design, A (re-seed at a clamp, the design's recommendation) or B (a stated residual: an install already walked to COP_SCALE_MIN or COP_SCALE_MAX stays there under flat asks until a manual scale reset)?

The approved design (design/R11-OUTSIDE-SELF-SETTING-PUMP at b31718e618, design-verdict at c875d70e1a, "Design review: approve b31718e618") routes this to the owner as "decision: owner" and tells the fixer to implement only the remedy the owner rules (fixer note c4e81d27). Under B, invariant (s) and the re-seed mutant are dropped. The rows the verdict shows for this decision are `true_0.45_flat_4kw_from0.5`, the persisted-0.500 heat-led 0.68 row and the persisted-0.500 self-setting rows, in the design's evidence plan.

Where I looked and found no ruling: dev/programme/RULINGS.md and dev/programme/HANDOVER.md at origin/main f9b680fee4; `git grep -i self-setting origin/main -- dev/programme`; #3394 comments from 2026-11-14T17:25Z to 2026-11-16T05:19Z; issue and pull-request search for "self-setting"; the dispatch payload at 28a9b47ea0.

The same verdict also routes these, which the ruling can confirm alongside:
- owner: carry 3, a release is not bounded per cycle (`true_0.6_max_cycle_move`).
- owner: carry 4, the overstated-minimum floor is unchanged (`min3_running_warm_own`, `fixed3_duty50_warm_own`, `fixed3_duty70_warm_own`).
- orchestrator: departure 1 (release and restore behind the freeze gate) and departure 2 (a replay does not feed the capacity envelope).

Once the ruling is in the dispatch brief, a fixer can start from origin/main; no code was written in this pass.
