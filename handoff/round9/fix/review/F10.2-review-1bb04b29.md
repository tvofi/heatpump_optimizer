Fix review: merge 1bb04b29a8b17f23919d4184c15d843512919553

Round 2, PR #1803. Head 1bb04b29 is the live PR head as posted. It is a fast-forward over b0a69c90 (the bot's closures re-record) and b4a0f75e (reviewed in round 1). Transport commits 6b73f2dd, 250da41c, cd03f38b and 75a751bb sit above it, not in its ancestry. The b4a0f75e..1bb04b29 delta touches four files: tests/closures.json (bot), tests/replay.py, tests/stress.py (comment only) and tools/audit/bugclasses.json (barrier text).

Round-1 remedies
1. loop_cpu_ratio is now 0.426. That is sqrt(2) x sqrt(0.2642 x 0.3433) = sqrt(2) x 0.3012 = 0.4259, from the six cloud runs the comment lists, so the floor is 0.213. The comment cites its source runs and corrects the clean range. Re-taken at this head on this box with threads pinned: clean 0.3267, inside (0.213, 0.426] and 23% above the floor. The doubled-loop arm read 0.6923, over the cap. The arm check fires on loop_cpu_ratio itself (replay.py:1275-1276 keys on that figure's own "over its budget"), so a loop arm whose cpu_ratio also goes over cannot pass it by proxy. ALL 77 replay checks PASSED. Answered.
2. The SCENARIO_CALLS_GROWTH comment and N-solve-recompute's barrier text now say a #1711-style firing passes for that one pull request on tvofi's approving review on the red channel, and that the constant is never raised for a single firing. Answered.

Budget values, final assessment
- loop_cpu_ratio 0.426: honestly measured, centred in its band, and the right design (card B1). It still records the fixer's runs and mine, not the nightly runner's. replay.py runs only nightly, so the first nightly on main is its first runner read. Scaled from the nightly's cpu_ratio, it should land about 0.24-0.30, inside the band.
- Valve rows 1.54, 9.15 and 7.64: new caps, not raises. They are the right design: the plant-axis check needs a row for every plant the sweep builds, and the two-zone choices are forced by topology.py:270-282. They are now runner-verified. PR CI fast (3.14) at b4a0f75e (job 110260309965) ran tests/stress.py in scoped mode: "ALL 98 STRESS CHECKS PASSED", which judges every row against (budget/2, budget]. stress.py's change since then is comment text only.

Unchanged from round 1: the 5% allowance re-derivation (the fixer's figures, not re-run here), the D9-s2-03 harness flat by design, and README's sweep count 51 -> 54.

CI: the b4a0f75e run was green on fast (3.14), mutation, budget-raise-gate, pr-contract, policy-docs and briefs. closures at b4a0f75e was answered by the bot's re-record in b0a69c90, and the body names it. CI at 1bb04b29 started 07:45Z and was still running at posting. The merge seat merges only on CI green at this head. Owed before merge: tvofi's approving review (code-owned tests/stress.py, policy tests/README.md, the new budget entries).
