Fix review: merge f3d7310fa3cdbce64607ba32cb60aa564d1503b9

bus-nonce: 041410ada6686083112d5e23195d5dfc

Round 3 (delta review of the merge-forward and retaken body). Measured at head f3d7310fa3cdbce64607ba32cb60aa564d1503b9.

## Findings

- The residual seam, tests/entities.py judging the last commit while `bare_array.py --check` with no ref reads the working tree, is already carried by the body and not settled here. Carry: R10-SUITE-HOST-DETERMINISM

## Evidence

- Prior block (body-stale): the body's `## Head` names f3d7310fa3cdbce64607ba32cb60aa564d1503b9; the every-file design and its departure are stated; the twin null controls and the figures are retaken; `## Red checks` is present. Answered.
- `merge_train.py classify` at this head: GREEN (pending: none, red: none). No red at any check, so no root-cause answer is owed.
- `git merge-tree --write-tree origin/main f3d7310fa3cdbce64607ba32cb60aa564d1503b9`: rc 0 (tree a2426401a, only LEDGER-MERGE resolved tests/closures.json). Clean.
- `bare_array.py --check`: rc 0; `--self-test`: ok (ev/bare_array.txt).
- Mutants on the merge resolution (ev/mut_argv.txt): ARGV guard reverted gives tick_loop.sh:112 listed; the CODE_PATHS reason deleted gives tick_loop.sh:96 listed; the app_approve.sh norm() reason deleted gives app_approve.sh:480 listed. Each killed and restored. CODE_PATHS and SELF_PATHS are literal arrays at tick_loop.sh:81-82, so their never-empty reasons are true. The ARGV guard is a real fix for a start with no arguments.
- app_approve.sh differs from main's side only by the one comment line above norm(); main's awk stage is intact. `app_approve.sh --self-test`: 316 checks, 0 failed. `tick_loop.sh --self-test`: 26 checks, 0 failed. I did not rerun a mutant of norm()'s awk stage; I relied on the one-line diff.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2602 ENTITY CHECKS PASSED (ev/entities.txt). `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. Scoped gate: MODE: FULL (tests/closure.py changes the gate).
- Claim files and VERSION are byte-identical to origin/main; no golden changed. Delivery row dev/programme/delivery/3055.md is in the three-dot diff. Figures: the review packet reports FIGURES 7 resolved, 0 not verified; carry_audit routed 1 finding, 0 unrouted. No macOS bash 3.2 exists here, so the rc 0 run of `bus.sh orphans` on 3.2 is not recorded; the static rule stands in, as the body states.
- Head: ev/HEAD.txt holds f3d7310fa3cdbce64607ba32cb60aa564d1503b9.
