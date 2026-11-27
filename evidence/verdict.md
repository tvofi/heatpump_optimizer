Fix review: blocked aeb563a713aa0b9d3587604c51dc7fb64397ec6a harness-broken: removing adoption_decision(config) and slab_mode_identifiability(config) breaks three in-tree round-11 finder harnesses that pass at the base and TypeError at the head
bus-nonce: 2e5ddc7cd3a40ac3744d7e2a7be05bcf

Round: 1 (full review; no prior reviewed head).

Findings:
1. harness-broken. `dev/audit/rounds/round11/D2/s3/m5_sysid.py` and `dev/audit/rounds/round11/D7/s2/m2_sysid_plant.py` call `adoption_decision(res, declared, config)`, and `dev/audit/rounds/round11/D3/s1/probe_46021727.py` calls `slab_mode_identifiability(params, config)`. Run with PYTHONPATH=tests/hastub, each gives rc 0 with RESULT lines at 190ffb10 and rc 1 with a TypeError at aeb563a7 (ev/r11_harnesses_base_head.txt). The body migrates the round-3 D2 harnesses and r10_cop_gate_vent.py and names r10_heat_meter.py and r10_thermal_power_option.py as archived, but it does not mention these three, which import the working tree. Repair: drop the third argument at each call site, the same treatment the round-3 harnesses got. `sweep/P5/D14/sweep-P5/enumerate.py` already fails at the base (SysIdConfig has no `enabled`), so it is out of this diff. Carry: R11-SEAM-dead-state
2. Note: harness-drift. `dev/audit/rounds/round11/D3/s1/fl183_nonfinite.py:77` and `probe_3885e472.py:70` still pass a return temperature as the second positional argument of `observe_temps`. That value now binds to `heat_output_kw`. Both RESULT sets are the same at base and head, because neither reads the slot. Carry: R11-SEAM-dead-state

Verified: mutation driver r11_dead_state_mutants.sh rc 0 at the head; my own mutant on flow_meter.py temps[0]->temps[1] is killed (block 9). The merge-tree against origin/main is clean. VERSION, the manifest and the notes are untouched. The roles have not changed since the merge base. The archscore perturb scripts edit the pinned tree, so the `_observe_frequency(now)` anchors are unaffected. The live red `tests / nightly-status` is outside the owed set and is answered in the body.
RESULT harnesses_broken_by_diff=3 count
RESULT targeted_mutant_killed=1 count
