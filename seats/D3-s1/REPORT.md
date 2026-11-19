# D3-s1 round 11, box D3-u1c slice (baseline 92d38ecb)

x

## Coverage

- D3.M1: universe 1260, examined 1260; enumerator `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py --unpinned`
- D3.M2: universe 1260, examined 340; enumerator `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py --unpinned`
  - not reached: custom_components/heatpump_optimizer/coordinator.py: 269 unpinned sites not pre-screened here (lines 467-11214); assigned to box D3-u1a, D3-u1b or D3-u1d (key outside [8206a42b98c8dd86, c0ecc8e0b6b66ded))
  - not reached: custom_components/heatpump_optimizer/defrost.py: 31 unpinned sites not pre-screened here (lines 111-804); assigned to box D3-u1a, D3-u1b or D3-u1d (key outside [8206a42b98c8dd86, c0ecc8e0b6b66ded))
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py: 90 unpinned sites not pre-screened here (lines 91-2307); assigned to box D3-u1a, D3-u1b or D3-u1d (key outside [8206a42b98c8dd86, c0ecc8e0b6b66ded))
  - not reached: custom_components/heatpump_optimizer/flow_lift.py: 3 unpinned sites not pre-screened here (lines 51-244); assigned to box D3-u1a, D3-u1b or D3-u1d (key outside [8206a42b98c8dd86, c0ecc8e0b6b66ded))
  - not reached: custom_components/heatpump_optimizer/grid_fee.py: 16 unpinned sites not pre-screened here (lines 187-488); assigned to box D3-u1a, D3-u1b or D3-u1d (key outside [8206a42b98c8dd86, c0ecc8e0b6b66ded))
  - not reached: custom_components/heatpump_optimizer/optimizer.py: 198 unpinned sites not pre-screened here (lines 1320-6661); assigned to box D3-u1a, D3-u1b or D3-u1d (key outside [8206a42b98c8dd86, c0ecc8e0b6b66ded))
  - not reached: custom_components/heatpump_optimizer/price_model.py: 44 unpinned sites not pre-screened here (lines 57-896); assigned to box D3-u1a, D3-u1b or D3-u1d (key outside [8206a42b98c8dd86, c0ecc8e0b6b66ded))
  - not reached: custom_components/heatpump_optimizer/sysid.py: 105 unpinned sites not pre-screened here (lines 129-2411); assigned to box D3-u1a, D3-u1b or D3-u1d (key outside [8206a42b98c8dd86, c0ecc8e0b6b66ded))
  - not reached: custom_components/heatpump_optimizer/tariff.py: 47 unpinned sites not pre-screened here (lines 77-1227); assigned to box D3-u1a, D3-u1b or D3-u1d (key outside [8206a42b98c8dd86, c0ecc8e0b6b66ded))
  - not reached: custom_components/heatpump_optimizer/thermal_model.py: 117 unpinned sites not pre-screened here (lines 270-5045); assigned to box D3-u1a, D3-u1b or D3-u1d (key outside [8206a42b98c8dd86, c0ecc8e0b6b66ded))
- D3.M3: universe 280, examined 84; enumerator `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tabulate.py --tsv | grep -P '\tSURVIVED\t'`
  - not reached: custom_components/heatpump_optimizer/optimizer.py:4033 CMP_BOUND 6e5e1a9f; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:10561 CMP_BOUND 45c379dc; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/price_model.py:198 GUARD_OFF ed095cbf; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:3387 CLAMP_DROP 9e45afd9; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:2144 CMP_BOUND 8d209fd1; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:846 CMP_BOUND 32465940; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/tariff.py:391 CMP_BOUND ea09d31b; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:4610 CMP_BOUND d9b2b8a5; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/price_model.py:201 GUARD_OFF 3dbd4039; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:784 CMP_BOUND fe16bdce; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:4751 CLAMP_DROP 5f84740b#2; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:2581 CLAMP_DROP 4cc7cd0a; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:4851 BOOLOP 4d085ae8; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:473 GUARD_OFF 54e620e3; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/sysid.py:643 CMP_BOUND 72abb7dd; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:6093 CMP_BOUND cf0ef9fc; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:1798 RETURN_DEL 3367669c; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:1708 CMP_BOUND 9330e956; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:1606 RETURN_DEL 90660fdb; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:687 GUARD_OFF d02b7542; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/optimizer.py:5211 CMP_BOUND f6038118; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:6097 CMP_BOUND c05d6fd2; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:5271 CMP_BOUND 32915bf0; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:4460 GUARD_OFF 4cb5c458; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/defrost.py:181 CMP_BOUND 7b9d8278; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/defrost.py:540 CMP_BOUND ef60f0b9; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:835 CMP_BOUND 855229b8; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:1715 CMP_BOUND 628390f0; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/price_model.py:342 CMP_BOUND cb6981eb; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:2376 CLAMP_DROP 73b72613; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:5654 CMP_BOUND dcf818be; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:677 GUARD_OFF f4619cef; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/optimizer.py:4828 CMP_BOUND 934404a3; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:6379 CMP_BOUND a306f8ef; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:5674 CMP_BOUND 8256b8db; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:5229 CMP_BOUND 9384ba6e; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:9440 CMP_BOUND 9f0fd699; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:1018 CLAMP_DROP 152250ba; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:2126 CMP_BOUND 036bc6d8; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:807 CMP_BOUND b8ab8111; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:1528 CLAMP_DROP 16576d0c; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/price_model.py:825 BOOLOP 44f0178f; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/tariff.py:801 CMP_BOUND ba43bf7e; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:1538 CLAMP_DROP f0477740; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/defrost.py:106 CONST d4d92013; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/price_model.py:207 CMP_BOUND c00e502c; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:3168 CMP_BOUND e6d706d3; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:11271 BOOLOP 67eac7b8; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:1343 CLAMP_DROP 051a1593; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/price_model.py:90 CONST f47f8e99; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:2010 CLAMP_DROP bea40588; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/grid_fee.py:310 RETURN_DEL 7e53edad; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:5083 CLAMP_DROP 61545c3f; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:1342 CMP_BOUND d209e002; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:467 CMP_BOUND 713016cb; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:7549 CLAMP_DROP 7b17a55a; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/price_model.py:535 CMP_BOUND 4b53a999; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:4234 CLAMP_DROP 85664bbe; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/tariff.py:1109 CMP_BOUND c58ef9ab; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:643 CMP_BOUND 72abb7dd; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:2598 CMP_BOUND 549bb130; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:549 CONST 745545cd; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/grid_fee.py:173 GUARD_OFF f8c4994a; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/sysid.py:1083 CMP_BOUND 7e1c5191; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:2375 CLAMP_DROP 6ca2df8a; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:3102 CLAMP_DROP 5d60b655; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:6648 CMP_BOUND 83c9652a; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:3073 CMP_BOUND e46c5e3e; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:5701 CLAMP_DROP cb686f74; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:2573 CLAMP_DROP 11808d14; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:2583 CMP_BOUND 01f70545; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:2539 CMP_BOUND 78b040fc; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:3073 CMP_BOUND e46c5e3e; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:470 CMP_BOUND 6e5e1a9f; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:1549 CMP_BOUND 9f414fb5; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:6091 RETURN_DEL 35c20d2b; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/defrost.py:683 BOOLOP 1299c7b8; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:1343 CLAMP_DROP 051a1593; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:5016 CLAMP_DROP c634563f; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:852 CMP_BOUND 5bc864cc; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:677 CMP_BOUND f4619cef; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/tariff.py:64 GUARD_OFF 39ff0db0; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/defrost.py:802 BOOLOP ea64107d; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:677 CLAMP_DROP 581f45bc; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:6602 CMP_BOUND b8bcfb6f; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:5222 CMP_BOUND 1a159a14; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:2946 CLAMP_DROP 351c0e21; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:10192 CMP_BOUND 8a040c32; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:9360 CMP_BOUND a1c68d69; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/grid_fee.py:360 CMP_BOUND 23a3a01d; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:5250 CMP_BOUND 2f71906b; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:5945 CLAMP_DROP 8d062eb9; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:1800 CMP_BOUND c97627da; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:2903 CMP_BOUND 5dfd3ad3; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:539 GUARD_OFF 23752846; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/optimizer.py:4272 CLAMP_DROP 86078a63; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:3651 CMP_BOUND a01b8479; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/defrost.py:808 BOOLOP d8122347; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:1942 CMP_BOUND 3e0642e4; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:1708 CMP_BOUND 9330e956; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:2037 CLAMP_DROP 79ab3a2f; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:10445 CMP_BOUND 8635e542; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:169 GUARD_OFF 4893b0a8; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/sysid.py:1785 RETURN_DEL b2994929#2; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:6360 RETURN_DEL 440ee7e3; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:75 GUARD_OFF b551ee16; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:2232 CLAMP_DROP f29a02b3; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:5674 CMP_BOUND 8256b8db; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:2086 CLAMP_DROP f3416292; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/flow_lift.py:183 GUARD_OFF 336a6ca0; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/coordinator.py:9365 CMP_BOUND a84c93c2; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:773 GUARD_OFF dacd4cc6; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/sysid.py:1212 CMP_BOUND 950dc213; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:9153 CMP_BOUND 789d92ca; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:1593 CMP_BOUND 3896349a; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:2075 CMP_BOUND 0d9190a8; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:892 CMP_BOUND ebe7af8b; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:2140 CMP_BOUND 655157d4; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:1782 CLAMP_DROP 81525776; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/price_model.py:72 CONST 90ecade5; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/price_model.py:510 CMP_BOUND b4032e2b; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:8785 CMP_BOUND ff55e496; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:5225 CMP_BOUND 60d71c27; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:900 CMP_BOUND ad0739c1; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:3402 CMP_BOUND 055feb1c; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:6573 CMP_BOUND 6d711f71; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:11091 CLAMP_DROP b4fd5e0d; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:10231 CMP_BOUND 8a040c32; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:3328 CLAMP_DROP 2723239c; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/grid_fee.py:496 RETURN_DEL d7923b87#3; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:10445 CMP_BOUND 8635e542; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:11002 CMP_BOUND 3036d119; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:4463 BOOLOP 66b15be8; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:1913 CMP_BOUND 8acc76b0; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:5145 CMP_BOUND d629fd84; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/tariff.py:824 CMP_BOUND b17b660c; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:9107 BOOLOP 2f74d22d; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:539 BOOLOP 23752846; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:5108 CMP_BOUND 9f0fd699; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:9051 CMP_BOUND 936e7a6e; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:677 CMP_BOUND f4619cef; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:4578 BOOLOP afe9dcd9; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/flow_lift.py:47 CONST 17af2c12; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/sysid.py:610 GUARD_OFF 72abb7dd; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:1527 CLAMP_DROP 0a81eaf0; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:10564 CMP_BOUND 842b328c; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:4668 CLAMP_DROP b186b210; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:1073 CMP_BOUND 501fd0e7; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:2038 BOOLOP f030484a; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:1994 CMP_BOUND f33dcd5d; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:875 CMP_BOUND 9cd2a896; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:6752 BOOLOP 9f6c1950; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:3013 CMP_BOUND 9a9af603; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:270 GUARD_OFF 55e7d0fb; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/optimizer.py:5271 CMP_BOUND 32915bf0; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:1545 CMP_BOUND 442ad6d1; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:3177 CMP_BOUND ddd90b1f; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:643 CMP_BOUND 72abb7dd; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:3328 CLAMP_DROP 1a5e5be6; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/grid_fee.py:355 CMP_BOUND 4a974762; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:1778 CLAMP_DROP 07b8a4e6; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:4720 CMP_BOUND 164830ff; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:9038 CMP_BOUND 8274eedf; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:4679 CLAMP_DROP 2d9d455e; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/tariff.py:806 CLAMP_DROP e202a9d1; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/price_model.py:141 CMP_BOUND de1a0615; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:2038 CMP_BOUND f030484a; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:9023 CLAMP_DROP bc68892f; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:3569 CLAMP_DROP c141a98b; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:548 CMP_BOUND d8dd626d; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:2208 CMP_BOUND 9174794d; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:659 CLAMP_DROP 29c2028d; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:4893 CMP_BOUND c3e4b79c; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/defrost.py:559 GUARD_OFF 7b8dda16; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/optimizer.py:2126 CMP_BOUND fc7a9935; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/optimizer.py:3969 CMP_BOUND 674746fd; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/sysid.py:2237 CMP_BOUND 9b28838f; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:3479 CMP_BOUND 5eed5b5e; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/coordinator.py:1643 CONST 7e415eaa; this box's slice, NOT DRIVEN
  - not reached: custom_components/heatpump_optimizer/price_model.py:337 R10C2 M25; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/tariff.py:744 R10C2 M31; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/sysid.py:1549 R10C2 M26; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/price_model.py:252 R10C2 M34; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/price_model.py:532 R10C2 M33; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/flow_lift.py:188 R10C2 M35; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/sysid.py:2246 R10C2 M27; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/sysid.py:1593 R10C2 M28; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/tariff.py:64 R10C2 M29; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/defrost.py:783 R10C2 M32; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/grid_fee.py:355 R10C2 M36; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/coordinator.py:8806 R10C2 M04; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:835 R10C2 M03; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/tariff.py:595 R10C2 M22; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/dhw_planner.py:1559 R10C2 M19; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/thermal_model.py:2593 R10C2 M07; carried survivor outside D3-u1c's slice, assigned to another box of the split
  - not reached: custom_components/heatpump_optimizer/grid_fee.py:383 R10C2 M21; carried survivor outside D3-u1c's slice, assigned to another box of the split
- D3.M4: universe 280, examined 280; enumerator `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tabulate.py --tsv | grep -P '\tSURVIVED\t'`
- D3.M5: universe 27, examined 23; enumerator `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py --scripts`
  - not reached: tests/card.mjs (assigned to box D3-m5)
  - not reached: tests/card_drift.mjs (assigned to box D3-m5)
  - not reached: tests/golden.py (assigned to box D3-m5)
  - not reached: tests/stress.py (assigned to box D3-m5)

## Slice tally (slice_u1c.py)

```
RESULT keys=309
RESULT driven=309
RESULT not_driven=0
RESULT pre_killed=64
RESULT pre_survived=245
RESULT pre_timeout=0
RESULT first_kill[tests/typing_ruler.py]=26
RESULT first_kill[tests/env_drift.py]=11
RESULT first_kill[tests/plan_view.py]=7
RESULT first_kill[tests/solar_alignment.py]=6
RESULT first_kill[tests/manual_plan.py]=6
RESULT first_kill[tests/structure.py]=4
RESULT first_kill[tests/finite_boundary.py]=2
RESULT first_kill[tests/doc_claims.py]=1
RESULT first_kill[tests/block_duty.py]=1
RESULT mutants_no_driver_ran=0
RESULT driver_runs_skipped_by_reach=1595
RESULT driver_runs_relaxed_skipped=152
RESULT driver_runs_red_unparsed=3
RESULT full_net_driven=82
RESULT full_net_killed=28
RESULT full_net_survived=54
RESULT full_net_timeout=0
RESULT full_net_kill[tests/features.py]=26
RESULT full_net_kill[tests/entities.py]=3
RESULT full_net_kill[tests/harness_headers.py]=1
RESULT pre_wall_sum=80252 s (provisional)
```

## Full-net survivors (finding candidates for the D3-top6 full gate)

key | file:line | symbol | kind | old -> new | verdict | drivers executing the line (should have failed)
---|---|---|---|---|---|---
8297234e122897ff | defrost.py:802 | DefrostWindow.peek | GUARD_OFF | `if self._state and self._since is not None:` -> `if False:` | full:SURVIVED | boost_drift_replay.py,config_flow_steps.py,entities.py,features.py
8365c2592bae9886 | optimizer.py:2796 | OptimizationConfig._comfort_pair | GUARD_OFF | `if self.day_end_hour_weekend is not None:` -> `if False:` | full:SURVIVED | boost_drift_replay.py,entities.py,features.py
884d2aba2bbd5409 | thermal_model.py:2598 | _valve_two_zone_delivery | GUARD_OFF | `elif available <= 0.0:` -> `elif False:` | full:SURVIVED | entities.py,env_drift.py,features.py,validate.py
88a992e9013ee436 | dhw_planner.py:2236 | DhwPlanner._plan_dhw_cheapest_first | GUARD_OFF | `if not candidates:` -> `if False:` | full:SURVIVED | block_duty.py,doc_claims.py,entities.py,env_drift.py,features.py,manual_plan.py,optimality.py,plan_view.py,validate.py
894b4e70a336f8fa | coordinator.py:10188 | HeatPumpOptimizerCoordinator._file_dhw_lead_predictions | GUARD_OFF | `if not trajectory:` -> `if False:` | full:SURVIVED | config_flow_steps.py,entities.py,features.py
89a3d25e2425b8e0 | coordinator.py:9386 | HeatPumpOptimizerCoordinator._fold_solar_aperture | GUARD_OFF | `if capacity <= 1e-6 or dt_h <= 1e-6:` -> `if False:` | full:SURVIVED | features.py
8ac9888c3d5fed52 | optimizer.py:5059 | HeatPumpOptimizer._derive_hold_schedule | GUARD_OFF | `if not bool(expensive.any()) or not bool(charging.any()):` -> `if False:` | full:SURVIVED | env_drift.py,features.py
8b4f4adbf55981bc | coordinator.py:9931 | HeatPumpOptimizerCoordinator._current_humidity | GUARD_OFF | `if not self._weather_forecast:` -> `if False:` | full:SURVIVED | block_duty.py,boost_drift_replay.py,config_flow_steps.py,entities.py,env_drift.py,features.py,finite_boundary.py,manual_plan.py,solar_alignment.py
8fd14c249b86abf7 | optimizer.py:5234 | HeatPumpOptimizer._safety_release_steps | GUARD_OFF | `if pinned_off:` -> `if False:` | full:SURVIVED | features.py,manual_plan.py,optimality.py
905a40b5ecea024f | optimizer.py:5044 | HeatPumpOptimizer._derive_hold_schedule | GUARD_OFF | `if n == 0 or len(prices) != n:` -> `if False:` | full:SURVIVED | env_drift.py,features.py
9297f123a6265555 | grid_fee.py:483 | apply_catalog | GUARD_OFF | `if not product_id or product_id == DSO_PRODUCT_NONE:` -> `if False:` | full:SURVIVED | config_flow_steps.py,entities.py,features.py
92e6a72a53dd339f | optimizer.py:1996 | _multi_start_minimize | GUARD_OFF | `if best is None:` -> `if False:` | full:SURVIVED | block_duty.py,boost_drift_replay.py,config_flow_steps.py,doc_claims.py,entities.py,env_drift.py,features.py,manual_plan.py,optimality.py,plan_view.py,validate.py
936bcb2da6441e86 | dhw_planner.py:1893 | DhwPlanner._repair_dhw_floor | GUARD_OFF | `if np.array_equal(plan, before):` -> `if False:` | full:SURVIVED | block_duty.py,doc_claims.py,entities.py,env_drift.py,features.py,manual_plan.py,optimality.py,plan_view.py,validate.py
94285425a1bc856a | coordinator.py:6615 | HeatPumpOptimizerCoordinator.async_shutdown | GUARD_OFF | `if pending:` -> `if False:` | full:SURVIVED | config_flow_steps.py,entities.py,features.py
94c2cc27ea61db25 | dhw_planner.py:1346 | DhwPlanner._build_dhw_requirements | GUARD_OFF | `if legionella_step is not None:` -> `if False:` | full:SURVIVED | env_drift.py,features.py
953a106a1aa39cee | coordinator.py:5658 | HeatPumpOptimizerCoordinator._async_learn_buffer_cooling | GUARD_OFF | `if buffer_temp > previous_temp:` -> `if False:` | full:SURVIVED | features.py
96fe4cecaa16f997 | coordinator.py:9390 | HeatPumpOptimizerCoordinator._fold_solar_aperture | GUARD_OFF | `if x <= 1e-6 or not np.isfinite(y):` -> `if False:` | full:SURVIVED | features.py
97628f4b14aec1b9 | coordinator.py:4497 | HeatPumpOptimizerCoordinator._async_drive_pumps | GUARD_OFF | `if not vvc_entity and not space_entity:` -> `if False:` | full:SURVIVED | config_flow_steps.py,entities.py,features.py
977021e3b3964277 | optimizer.py:2782 | OptimizationConfig._comfort_pair | GUARD_OFF | `if self.holiday_comfort_night is not None:` -> `if False:` | full:SURVIVED | entities.py,features.py
97bd985754f1099b | thermal_model.py:4140 | ThermalModel.simulate_step | GUARD_OFF | `if n_sub == 1:` -> `if False:` | full:SURVIVED | block_duty.py,boost_drift_replay.py,config_flow_steps.py,doc_claims.py,entities.py,env_drift.py,features.py,manual_plan.py,optimality.py,plan_view.py,validate.py
9aa50bd32847b4dd | optimizer.py:1948 | _multi_start_minimize | GUARD_OFF | `if not scored:` -> `if False:` | full:SURVIVED | block_duty.py,boost_drift_replay.py,config_flow_steps.py,doc_claims.py,entities.py,env_drift.py,features.py,manual_plan.py,optimality.py,plan_view.py,validate.py
9b72b944ac12fa25 | coordinator.py:8842 | HeatPumpOptimizerCoordinator._guard_floor_hold | GUARD_OFF | `if params.two_zone_enabled:` -> `if False:` | full:SURVIVED | features.py
9b890e4f1fdfcd41 | dhw_planner.py:556 | DhwPlanner._effective_dhw_windows | GUARD_OFF | `if hour == prev + 1:` -> `if False:` | full:SURVIVED | env_drift.py,features.py
9bfc2c6d1bfe66bd | optimizer.py:5120 | HeatPumpOptimizer._tighten_buffer_caps | GUARD_OFF | `if refused is None:` -> `if False:` | full:SURVIVED | env_drift.py,features.py,validate.py
9d16dbc0d3aba164 | tariff.py:904 | _peak_excess | GUARD_OFF | `if house.size == 0:` -> `if False:` | full:SURVIVED | env_drift.py,features.py
a2a1d3802ceff60d | thermal_model.py:404 | ThermalParameters.topology_layout | GUARD_OFF | `if cached is not None and cached[0] == key:` -> `if False:` | full:SURVIVED | block_duty.py,boost_drift_replay.py,config_flow_steps.py,doc_claims.py,entities.py,env_drift.py,features.py,finite_boundary.py,guard_pins.py,manual_plan.py,optimality.py,plan_view.py,solar_alignment.py,validate.py
a33188790c5affad | coordinator.py:6454 | HeatPumpOptimizerCoordinator.async_run_optimization | GUARD_OFF | `if self._solve_failures >= SOLVE_FAILURE_ISSUE_COUNT:` -> `if False:` | full:SURVIVED | config_flow_steps.py,entities.py,features.py
a581feadd69c6c42 | optimizer.py:6606 | HeatPumpOptimizer.get_current_action | GUARD_OFF | `elif p_norm < 0.9:` -> `elif False:` | full:SURVIVED | config_flow_steps.py,entities.py,features.py
a7dd3153718e531b | coordinator.py:9153 | HeatPumpOptimizerCoordinator._confidence_margins | GUARD_OFF | `if damp <= 1e-9:` -> `if False:` | full:SURVIVED | config_flow_steps.py,features.py
aa338654e7801916 | optimizer.py:6070 | HeatPumpOptimizer._buffer_charge_ceiling | GUARD_OFF | `if hi <= lo:` -> `if False:` | full:SURVIVED | env_drift.py,features.py,validate.py
aa6b718c979bf831 | coordinator.py:7118 | HeatPumpOptimizerCoordinator._weather_fetch_failed | GUARD_OFF | `if not self._weather_outage_cycles:` -> `if False:` | full:SURVIVED | config_flow_steps.py,entities.py,features.py,manual_plan.py
ab65584805229d1c | sysid.py:892 | _slab_refusal | GUARD_OFF | `if not (-0.5 <= gains_kw <= 2.0):` -> `if False:` | full:SURVIVED | entities.py,features.py
ab918806fc8b4af6 | coordinator.py:10331 | HeatPumpOptimizerCoordinator._accumulate_energy | GUARD_OFF | `if energy <= 0:` -> `if False:` | full:SURVIVED | boost_drift_replay.py,entities.py,features.py
ac6bedc70bb82ff7 | coordinator.py:8265 | HeatPumpOptimizerCoordinator._build_data_dict | GUARD_OFF | `if manual_state is not None:` -> `if False:` | full:SURVIVED | config_flow_steps.py,entities.py,env_drift.py,features.py,finite_boundary.py,manual_plan.py
ad01ae06d7ea84ec | optimizer.py:5054 | HeatPumpOptimizer._derive_hold_schedule | GUARD_OFF | `if p85 <= p25 * 1.05:` -> `if False:` | full:SURVIVED | env_drift.py,features.py
ad8a02e5c07428ab | coordinator.py:4538 | HeatPumpOptimizerCoordinator._async_drive_pumps | GUARD_OFF | `if params.two_zone_enabled:` -> `if False:` | full:SURVIVED | config_flow_steps.py,features.py
b020c93535a7f9e6 | defrost.py:795 | DefrostWindow.peek | GUARD_OFF | `if self._opened is None:` -> `if False:` | full:SURVIVED | boost_drift_replay.py,config_flow_steps.py,entities.py,features.py
b028ad9d6c702965 | coordinator.py:2360 | _warm_seeded | GUARD_OFF | `if result is not None:` -> `if False:` | full:SURVIVED | config_flow_steps.py,entities.py,features.py
b098598faf0d87dc | thermal_model.py:835 | ThermalParameters.seasonal_inlet_temp | GUARD_OFF | `if swing <= 0.0:` -> `if False:` | full:SURVIVED | block_duty.py,boost_drift_replay.py,config_flow_steps.py,entities.py,features.py,finite_boundary.py,manual_plan.py,solar_alignment.py
b143b01c4ea02159 | optimizer.py:6604 | HeatPumpOptimizer.get_current_action | GUARD_OFF | `elif p_norm < 0.7:` -> `elif False:` | full:SURVIVED | config_flow_steps.py,entities.py,features.py
b25e80c59b31c20d | dhw_planner.py:1184 | DhwPlanner._build_dhw_requirements | GUARD_OFF | `if dhw_pins is not None:` -> `if False:` | full:SURVIVED | block_duty.py,doc_claims.py,entities.py,env_drift.py,features.py,manual_plan.py,optimality.py,plan_view.py,validate.py
b341873adae0cf3c | thermal_model.py:2587 | _valve_two_zone_delivery | GUARD_OFF | `elif delivered <= 0.0:` -> `elif False:` | full:SURVIVED | env_drift.py,features.py
b413c17079bb8176 | sysid.py:1922 | SystemIdentification.identify | GUARD_OFF | `if dt_h <= 1e-3 or dt_h > 2.0:` -> `if False:` | full:SURVIVED | features.py
b546d5e705722bb5 | coordinator.py:5382 | HeatPumpOptimizerCoordinator._fold_cop_evidence | GUARD_OFF | `if modelled_cop <= 0.1:` -> `if False:` | full:SURVIVED | boost_drift_replay.py,features.py
b5d57e4a1fc22d96 | optimizer.py:3177 | stored_heat_survival | GUARD_OFF | `if span <= 0.0:` -> `if False:` | full:SURVIVED | env_drift.py,features.py,validate.py
b61d1402aad5a055 | sysid.py:1545 | SystemIdentification.conditions_met | GUARD_OFF | `if cfg.start_hour <= cfg.end_hour:` -> `if False:` | full:SURVIVED | features.py
b6ac2d53028d45a3 | coordinator.py:5049 | HeatPumpOptimizerCoordinator._interval_space_power | GUARD_OFF | `if self._pump_signals.mode_observed and not self._pump_signals.space_heat:` -> `if False:` | full:SURVIVED | boost_drift_replay.py,entities.py,features.py
b8d5ec03e8eba5c7 | sysid.py:1942 | SystemIdentification.identify | GUARD_OFF | `if len(rows) < 5:` -> `if False:` | full:SURVIVED | features.py
b94f040a7b0aed92 | optimizer.py:2494 | _mark_manual_reasons | GUARD_OFF | `if _pin_is_free(pin) or pin < 0.5:` -> `if False:` | full:SURVIVED | block_duty.py,features.py,manual_plan.py,optimality.py
b9b6cf1d15a84248 | price_model.py:337 | PriceShapeModel.expected_daily_min | GUARD_OFF | `if not day_types or not np.isfinite(level) or level <= 0.0:` -> `if False:` | full:SURVIVED | features.py
b9bbb3ac364893f7 | thermal_model.py:698 | ThermalParameters.wood_tank_heat_loss_coefficient | GUARD_OFF | `if cached is not None and cached[0] == key:` -> `if False:` | full:SURVIVED | env_drift.py,features.py
ba9f6b92f678ab10 | price_model.py:303 | PriceShapeModel.quarter_factor | GUARD_OFF | `if trust <= 0.0:` -> `if False:` | full:SURVIVED | entities.py,features.py
bcf290164a0edeeb | coordinator.py:5157 | HeatPumpOptimizerCoordinator._external_heat_override | GUARD_OFF | `if probe.stale:` -> `if False:` | full:SURVIVED | block_duty.py,boost_drift_replay.py,config_flow_steps.py,entities.py,features.py,finite_boundary.py,manual_plan.py,solar_alignment.py
be95c184bf4746ff | optimizer.py:4211 | HeatPumpOptimizer._analyze_forecast_trajectory | GUARD_OFF | `if n == 0:` -> `if False:` | full:SURVIVED | block_duty.py,boost_drift_replay.py,config_flow_steps.py,doc_claims.py,entities.py,env_drift.py,features.py,manual_plan.py,optimality.py,plan_view.py,validate.py

## Findings

None from this slice: survivors are candidates (D3.md step 3); only the D3-top6 full gate turns them into findings.

## Non-findings


## Harnesses

- dev/audit/rounds/round11/D3/s1/enumerate.py
- dev/audit/rounds/round11/D3/s1/prescreen.py
- dev/audit/rounds/round11/D3/s1/tabulate.py
- dev/audit/rounds/round11/D3/s1/slice_u1c.py
- dev/audit/rounds/round11/D3/s1/build_u1c.py

## Unfinished

- none

## Exposure

x
