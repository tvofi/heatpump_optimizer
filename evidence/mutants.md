Mutants over p2's tree (handoff-wip/r11-pre-finder-contract, tip d761df1655 = cb6600d2f1 + BLOCKED.md, p2-BODY.md), graded by this head's copy of tools/policy/check-wave-script.mjs:
M1 dual edit (schema drops "enumerator" + fold_ledger.py sync): mut-M1-dual-edit.txt, 164 passed 2 failed (body: 164/2) KILLED
M2 DIMS.filter((d) => d !== "D5"): mut-M2-filter.txt, 182 passed 28 failed (body: 182/28) KILLED
M3 CADENCE + activeIn declared unused in DISPATCH: mut-M3-declared-unused.txt, 247 passed 1 failed (body: 247/1) KILLED
M4 (reviewer) renamed odd-round skip .filter((s) => !(round % 2 && s.dim === 'D5')): 183 passed 27 failed KILLED
M5 (reviewer) renamed skip at multiples of 5 .filter((s) => !(round % 5 === 0 && s.dim === 'D6')): 248 passed 0 failed SURVIVED
G1 grader: the "declares no cadence" test deleted, M3 applied: 247 passed 0 failed -> that test is M3's only killer (not vacuous)
G2 grader: the round 11/13 loop deleted, M4 applied: 183 passed 25 failed -> M4 is also killed by the round-9 box/scope checks
