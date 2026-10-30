RESULT R1 rc=1 ['2 of 4622 FEATURE CHECKS FAILED']
  ok   an unresolvable recorded_at FAILS the ratchet, it is not merely noted (#361)
  ok   the ratchet FAILS on an improvement instead of printing a note (#350)
  ok   a pump command that FAILED is not remembered as done
  FAIL the coordinator's cycle inside MIN_OFF of a cut does not turn the switch on  [[('switch', 'turn_on')]]
  FAIL the step tick inside MIN_OFF of an early cut-off writes no turn_on at a step the plan turns on  [{'06:00': ['turn_off'], '06:15': ['turn_on']}]
2 of 4622 FEATURE CHECKS FAILED
