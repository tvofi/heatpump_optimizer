# BLOCKED: r10-advisor-steady-start, round 6

Question: prepr.sh's pr-body check refuses `tests / fast (3.14)` as red on a commit of origin/main..HEAD and unnamed in `## Red checks`; at the PR head e9b1651a that check is green, and this seat was refused the per-commit check-run read that would find which commit read it red and why. Which commit, and what was its failure, so the body can answer it?

State: the arch-score payment is done and verified, in the tree of this commit (the tree of c3a53241cf2f613e328a4d89f08c9d05a5ed65a4 plus this file), code commits bd7968bde (Rotation for price_tiles.take; whatif.state_for as setdefault) and c3a53241c (five stale pins dropped), both children of the PR head e9b1651a.
- score.py --diff 4aa98689469d: dS +0.0279 IMPROVES, coord_footprint 2505 -> 2503 (e9b1651a: 2505 -> 2513 WORSENS).
- structure.py PASSED, no budget raised; entities.py ALL 2711 PASSED; scoped gate MODE: SCOPED -- 31 script(s) run, all 31 ok (29 in the run, the last five re-run alone after a time limit); finder's harness whatif and steadysign byte-identical at e9b1651a and the head; mutant_run over e9b1651a...HEAD: 16 mutants, 0 survivors; core-line null control KILLED.
- ci_predict.py: no red predicted; 6 unpinned sites (warning).
Open in prepr besides the question: the Unpinned sites line for price_tiles.py:148 must be spelt `:148 CMP_BOUND*2` and `:148 GUARD_OFF` separately, and the Forward-carry item to R10-HOTFIX-LEGACY-CONTROL-DATA (done) needs a live destination. The draft body is in this seat's scratch only.
