k3 A 56a214c8bd8f72dfc4839234dc749cc53ec6813c rc=0 ALL 4987 FEATURE CHECKS PASSED
k3 B 02954c6aa76b64f0bbf904f233f954c5d0cbb168 rc=0 ALL 4987 FEATURE CHECKS PASSED
q7 A ce4cdb2271c3a3883c422e228f55d526d93827e2 rc=0 ALL 4988 FEATURE CHECKS PASSED
q7 B bb2ab4b3b54485ba07ad4fb4ae5f7faf58a7bbd2 rc=1 3 of 4988 FEATURE CHECKS FAILED
m2 A a942da87b28a2ec60cf29717754c6a663c9f4efe rc=0 ALL 4984 FEATURE CHECKS PASSED
m2 B 19dff27fe599c934aa0441ae5c5f98035fc30914 rc=143 no summary line (killed by me at 90 min elapsed, past the 60 min allowance; the first attempt was lost to a container restart, the rerun's log stopped growing at "and the credited plan still clears dhw_min_temp inside every demand window" while the process stayed at ~99% CPU)

q7 B FAIL lines:
FAIL #2499: the slab rises with the metered draw, below the commanded trajectory while the pump draws less than 4 kW  [slab off/1kW/4kW=22.840/22.840/22.840]
FAIL R10-COP-GATE-E: a switch back from hot water to heating advances the slab by the dwell's space share of the draw, not the whole draw as space heat  [slab switch-back/half-draw/heating=23.5050/22.8400/22.8400]
FAIL R10-COP-GATE-E: a switch from heating to hot water books the dwell's space share of the draw, not 0 kW  [slab switch-out/half-draw/dhw-only=23.5050/22.8400/22.8400]
