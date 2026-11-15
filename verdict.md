Fix review: merge 62abeb4849dbb7443240fd9d879d970ff2f98780

bus-nonce: 18f8df63f41c94b4605b3cc4d4175ed9

## Evidence
- Round 1. Head 62abeb4849dbb7443240fd9d879d970ff2f98780 is the head I measured; the three-dot diff touches only tools/audit/seat/beatd.py, tools/audit/seat/bus.sh and dev/programme/delivery/3613.md. No VERSION, manifest, notes, golden or claim file and no custom_components/ file is touched.
- CI: `merge_train.py classify` printed `GREEN 62abeb4849dbb7443240fd9d879d970ff2f98780 pending: none red: none`. `merge-tree --write-tree origin/main <head>` exits 0 (clean).
- RESULT bus.sh --self-test at head: 239 checks, 0 failed (ev/bus-self-test.txt). The body's figure is reproduced.
- RESULT beatd.py --self-test 9 at head: 34 checks, 0 failed with mutants (ev/beatd9-mutants.txt); 24 checks, 0 failed with --no-mutants (ev/beatd9.txt).
- RESULT mutation, bus.sh: replacing `until mkdir "$lk" 2>/dev/null; do` with `mkdir -p "$lk"; until true; do` makes three P354 arms FAIL (live holder waits; two concurrent confirms; pid not yet written), as the body states (ev/bus-mutant.txt). The file was restored; the tree is clean.
- RESULT mutation, beatd: `mutant m9_running_ignored turns (9) 'a running instance defers the restart to the next pass' red`; the anchor occurs once in production.
- Null controls: both existing P354 takeover controls and the beatd null arms are ok in the unmodified runs.
- Barrier design read: the beatd running arm waits on the journal's START lines and beatd's own deferral line, not a wall-clock window; the bus arm opens the gate only after the second confirm has marked itself waiting on a live holder. The production line in confirm() is a no-op unless HPO_BUS_WAIT_MARK is set.
- Not re-derived: the body's 1-of-12 base flake rate under CPU load. The body itself says the sample does not establish a base rate. The bus base failure was not reproduced, as the body discloses; detection rests on the mutation above.
- No finder's harness is named; the flake is a self-test arm, and the instrument's own self-test is the harness. Class: the two arms the issue names are both changed and the third (carry 167) is already on main; I found no further seat of the class.
- Red checks: none. Forward-carry: carry 0 is dismissed as already repaired on main by f38124f19c.
- Note: carry-missing-none. The body's single carry is routed.
