# D3-g23 per-key probe notes (provisional class pending each key's full gate)

Probes run from a scratch baseline worktree ($HOME/probe-base at 92d38ecb), never the gate's tree.
Class applies only if the key's gate is SURVIVED or RED-AS-NULL; a KILLED gate makes it a non-finding.

| key | line | probe number (baseline -> mutant) | through optimize() | provisional class |
|---|---|---|---|---|
| c6679b9b114e5732 | 5228 | short space_pins: ([],[]) -> IndexError | 0 of 3 short-pin solves differ; reach 0 of 11 release calls (_normalise_pins pads) | equivalent-candidate (unreachable through production) |
| 8ef1027c9e221b64 | 5229 | 0.5 pin at floor+0.1: ([],[]) -> ([0],[]) | 5 of 55 solves with 0.5 pins differ | candidate |
| ce686724ef107650 | 5229 | on-pin at floor+0.1: ([],[]) -> ([0],[]) | 3 of 36 on-block solves differ | candidate |
| 8fd14c249b86abf7 | 5234 | off step at floor+0.1: ([0],[]) -> ([],[]) | 11 of 55 off-block solves differ | candidate |
| 0120a5a672990611 | 5235 | off step at floor+0.15 tie: ([0],[]) -> ([],[]) | tie only (solver float) | candidate (boundary) |
| 0ecb763c4bcb0828 | 5237 | free step at floor-0.25 tie: ([],[]) -> ([0],[]) | tie only | candidate (boundary) |
| f2894b5754c254fe | 5248 | short DHW requirement: ([],[]) -> IndexError | reach 0 of 11 | equivalent-candidate (unreachable) |
| bc3a42f14c903439 | 5250 | tank at req-0.5 tie: ([],[]) -> ([],[0]) | tie only | candidate (boundary) |
| 856aa341a89a6ab0 | 5211 | optimize released [0] -> [] (16.9 C, step 0 off) | moves | candidate |
| 7303435ec1ab7701 | 5212 | short pins, breach past end: ([0],[]) -> IndexError | 0 of 3; reach 0 of 11 | equivalent-candidate (unreachable) |
| 5ce83ed87c36b9a5 | 5213 | 0.5 pin before off: ([0],[]) -> ([],[]) | 5 of 15 solves with 0.5 pins differ | candidate |
| fe3e41de6bdc640a | 5213 | optimize released [0,1] -> [] (17.0 C, off 0-1, on 2) | moves | candidate |
| f25414a9d4e32d19 | 5292 | long guess: [1,2,5] -> IndexError | reach 0 of 14 seed calls | equivalent-candidate (unreachable) |
| 70791cdb98f8ddd7 | 6027 | buffer cap at -20 C, tank 60 C: 60.0 -> 35.0 C | 20 result fields differ | candidate |
| 7516dd3d9e66d3ef | 6029 | buffer cap at -20 C, tank 60 C: 60.0 -> 35.0 C | 20 result fields differ | candidate |
| 65e0ffa75d60d319 | 6038 | wood cap 95.0 -> absent; stored kWh 361.75 -> 364.07 | 0 fields at 24/2/1 h horizons (held reference carries the plan's wood side) | equivalent-candidate (equivalent at the observable output) |
