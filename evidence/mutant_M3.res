RESULT M3 rc=1 ['3 of 4617 FEATURE CHECKS FAILED']
  ok   an unresolvable recorded_at FAILS the ratchet, it is not merely noted (#361)
  ok   the ratchet FAILS on an improvement instead of printing a note (#350)
  ok   a pump command that FAILED is not remembered as done
  FAIL the step tick writes the switch at the boundary of each step whose command changes  [[(14, 'turn_on'), (15, 'turn_off'), (30, 'turn_on'), (44, 'turn_on'), (45, 'turn_on'), (60, 'turn_off'), (74, 'turn_off'), (75, 'turn_off'), (90, 'turn_on'), (104, 'turn_on'), (105, 'turn_off'), (120, 'turn_on'), (134, 'turn_on'), (135, 'turn_off'), (150, 'turn_off'), (164, 'turn_off'), (165, 'turn_off'), (180, 'turn_on'), (194, 'turn_on'), (195, 'turn_on'), (210, 'turn_off'), (224, 'turn_off'), (225, 'turn_on')]]
  FAIL an early cut-off holds across a step boundary the plan keeps on  [[(0, 'turn_on'), (15, 'turn_off'), (30, 'turn_on'), (34, 'turn_off'), (45, 'turn_on'), (60, 'turn_off'), (75, 'turn_off'), (90, 'turn_on'), (105, 'turn_off'), (120, 'turn_on'), (135, 'turn_off'), (150, 'turn_off'), (165, 'turn_off'), (180, 'turn_on'), (195, 'turn_on'), (210, 'turn_off'), (225, 'turn_on'), (240, 'turn_on')]]
  FAIL the step tick writes nothing at a boundary under a live boost across a boundary whose plan step is off  [(['turn_on'], True, False)]
3 of 4617 FEATURE CHECKS FAILED
