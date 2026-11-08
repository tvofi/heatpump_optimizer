Part 2 of R10-SUITE-HOST-DETERMINISM: carries 4-8, the host determinism of `tests/entities.py`. Carries 5, 6 and 7 are built; 4 is dismissed with a control; 8 is left open.

## Head

b974110d7c800d78cd49382e8b8d22245aa8bc7d, cut from origin/main b4ec2f332fe3ab8dcf169bd3066276d3bb8848ab. `tools/pr/prepr.sh` ran clean at this head (rc=0, the body check not yet passed to it). Main had not moved when it ran.

Body-repair note: the earlier field-coverage refusal on the settings hook file was not re-measured in this pass (no code changed; this diff does not touch that file).

## Mutation proof

Each mutant applied to `tests/entities.py` alone and the full `entities.py` run read; each leaves exactly `1 of 2647 ENTITY CHECKS FAILED`, then the good copy was restored:
- drop the `if platform != "darwin": raise` lines of `_hb_stdlib_arm`: FAIL "a task-port refusal is a printed skip on darwin only: linux and any other exception still fail, and a bad sample is still judged by the arm"
- widen `except PermissionError` to `except Exception` in `_hb_stdlib_arm`: the same check goes red
- make the HEAD scan read the working tree (`_ba.scan()` in place of `_ba.scan("HEAD")` in the control): FAIL "bare_array: an uncommitted bare site is invisible to the HEAD scan this row runs and red to the tree scan"

The mutants ran before the control repo was rebuilt on `throwaway_git` (prepr's `throwaway git` step refused the first form); the predicate under mutation is unchanged by that rebuild.

## Null control

At the merge base b4ec2f332, `PYTHONPATH=tests/hastub python3 tests/entities.py` reads `ALL 2645 ENTITY CHECKS PASSED`, rc=0. At this head it reads `ALL 2647 ENTITY CHECKS PASSED`, rc=0: the two added checks, nothing else moved.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/entities.py` at the merge base: 2645 passed; at this head: 2647 passed.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED at the first commit; the second only moves the control repo's construction.
- `tools/pr/prepr.sh` at b974110d7: rc=0.

## Red checks

none

## Forward-carry

Carry 4 (cost): dismissed. `tests/entities.py` reads `ALL 2645 ENTITY CHECKS PASSED` at the merge base in this cloud seat, so the `gate-sweep.yml` U0c and `graders-head-copy` delivery_status failures do not reproduce here. Control: that same run. If they recur in another seat the reading is that seat's. Carry: dismissed: not reproduced here, control is the same run

Carry 5 (bare_array HEAD vs working tree): built as the documentation arm. The row's name now says it judges HEAD (a tree read would open every tools/*.sh and join the closure), and a planted control in a throwaway repo (`throwaway_git_init`) shows an uncommitted bare site is clean to `scan("HEAD")` and red to `scan()`. Mutant above. Carry: dismissed: built in this pull request, nothing left to carry

Carry 6 and Carry 7 (darwin task-port, wrapper copies): built as one platform rule, `_hb_stdlib_arm`. A `PermissionError` on darwin prints `SKIP stdlib sampler control: macOS denies the task port (<message>)` and the module continues; linux, any other exception, and a bad sample still fail or are judged. One row pins all four cases; the two mutants above go red. The py-spy stub's `wc -l` padding is already handled (`| tr -d " "`), so no change. The out-of-tree wrapper copies are not in the repository and no tools/ file was added. Carry: dismissed: built in this pull request, nothing left to carry

Carry 8 (heartbeat respawn): left open. The nightly history (schedule events of `nightly.yml`) shows failures after the stdlib-sampler fix on 2026-11-03, 11-04 and 11-05; I read the jobs for 11-05 only (run 41943946464): both `nightly-ha` jobs succeeded and the failure was the `slow` job's replay step, so not `hb:positive_control`. The 11-03 and 11-04 runs and the pre-fix null count were not read. Carry: R10-FLY-SUITE-ENV-FLAKES | dismissed: the respawn stays conditional exactly as that done group's brief states, no live group fits (R10-ARCH-DOCS and R10-ROUND-PLAYBOOK-FINAL do not own nightly flakes)

## Friction

none
