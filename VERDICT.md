Fix review: merge 6ab7d15ef7dfb69eb55ede687f044297306572de

bus-nonce: 13f2fbdc2ea0f9397e2133a5a0ce170a
pending-ci: gate (merge_train.py classify prints WAIT: pending, gate red: none; head lacks main 6cc15e9b, so a red tests / fast (3.14) combi census or governance / instrument-self-tests is main's old red, cured by the remerge)

## Findings

- Residual: at 10 and 15 min the repair is inert against the base: the dip arm reads the same at both ends in every cell, so the phantom the fix targets stays there at those cadences. It is no worse than the base and removes no real draw; the gain is at 30 min only (3 cells move, all toward truth). Carry: dismissed: no regression, and the gain claim at production cadence is bounded by the 30-min default

## Evidence

- Delta reviewed: 8fe71477..6ab7d15ef7dfb69eb55ede687f044297306572de (round 3, delta of the blocked round 2 at verdict/3444@2a99a2d447f7). Production delta: dhw_learning.py only (ChargeSettle.classify now returns (heated, settling); the fold's charge flag is started_heated or settling instead of heated_interval or settling). No widening beyond that path.
- Block answered. My seq30.py (30 min apart, same sequence as the block): base truth 0.6542 / dip 1.3127 / control 1.3127; old head dip 0.3847; this head truth 0.6542, dip 0.6542, control 1.3127 (ev/seq30_{base,head}.txt). Null control holds.
- Finder-class harness at both ends, my cadence probe over 72 cells (10/15/30/60 min, 3 charges, 6 draw offsets): truth is identical to base in all 72. Dip cells that move against base: only step=15 charge 07:35+15 off+5 (truth 1.2527, base 1.594, head 1.1481), step=30 07:30+10 off+5 (truth 1.6087, base 1.84, head 1.6238) and off+15 (truth 1.9994, base 2.2303, head 2.0143); none is further from truth than base. The block's 15-min cell (07:30+10, off -10; head 0.9868 at the old head, truth 1.8777) now equals the base (ev/cadence_new.txt). The four 30-min cells the old head moved to new under-counts no longer do.
- The fixer's harness r10_dhw_charge_settle_p90.py at 10/15/30 min, both ends (ev/harness_{base,head}.txt): the dip arm never moves away from truth against base; 30-min draw-0735 2.0823 to 1.8629 (truth 1.8512), draw-0745 2.5009 to 2.2759 (truth 2.2703); 10 and 15 min equal the base.
- Mutants run through tests/features.py at the head: reverting the repair (charge=heated_interval or settling) makes the new check "at the learner's production cadences ..." FAIL, and seq30 reads 0.3847 again; R2_ESCROW_DEC_OFF (dhw_draws.py take-back escrow not decremented) and R2_CREDIT_PER_INTERVAL (the credit reset on every charge-affected interval), the two round-2 survivors, now FAIL "a charge's take-back stops at the energy its charge folded and at the dip bound". The unmutated head passes all three charge checks. The one FAIL in a full features.py run at the head is the combi_type_branch census (vendor-name census, line 1208 of ev/features_head.txt), the inherited main red.
- Sub-production cadence: the 5-min arms stay as a sub-cadence check, and the test comment now says so.
- git merge-tree --write-tree origin/main 6ab7d15ef7dfb69eb55ede687f044297306572de exits 0 (tree 00d73351c2715c1f64956e4e40efd5e6a1e64cea). The PR body's code tip and VERSION, manifest and notes heading: not re-read at this delta beyond a diff touching only dhw_learning.py, the harness and tests/features.py, so none of the three is touched.
- Not re-run: the body's named mutant tables and the heavy gate (CI's). owed-reds printed; classify WAIT, gate red: none.
- Harness provenance: the harness is the builder's; probe, cadence and seq scripts are the reviewer's, not in the tree (ev/).
