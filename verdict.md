Fix review: merge db78749e927707a20e320318c335b5302ca98ed3

bus-nonce: a9991998c2ef9c3f368145dac2f7a2e7

## Round

Round 3 review of #2709 (R10-FLY-CLOUD-SETUP-TOOLCHAIN). The PR's seven files are byte-identical to round 2's head 5e4fbb0d3b14 (`git diff 5e4fbb0d3b14 db78749e9 -- <the seven files>` is empty). This round judges the carry routing, which round 2 blocked as carry-missing, and re-checks the head.

## Carry routing (step 10)

- Forward-carry and the `cloud_dispatch` Friction line → R10-FLOW-DESIGN-STAGES. Roster commit 65c67fc26392c4d39eca929fa9cc7b59bd1c8cb3 ("roster_edit append-carry R10-FLOW-DESIGN-STAGES") adds the carry "From #2709 (r10-fly-cloud-setup-toolchain), Forward-carry: cloud_dispatch.py's rendered setup line runs `bash tools/audit/seat/cloud-setup.sh --check` and stops the seat on REFUSE …" (ev/roster-65c67fc26.diff). The group is live (stage `not-started`), and its `files` include `tools/audit/seat/cloud_dispatch.py`. The carry is still present at the roster tip 1debc245a7c4.
- `fixer.md#2` Friction → R10-POLICY-FIXER-MD. Roster commit 8ecacecb114c56ce75370e643d7fc00dbbdfcaf9 adds "From #2709 …, ## Friction "fixer.md#2: cost": under `set -e`, an `exit $?` -> `exit 0` mutant is equivalent …" (ev/roster-8ecacecb1.diff). The group is live (stage `in-progress`), owns `dev/governance/roles/fixer.md`, and still holds the carry at the roster tip.
- Both commits are ancestors of `handoff/audit-r10-roster`. R10-ORCH-MACHINERY (`absorbed`) holds no #2709 carry, so nothing is left at the dead group.

## Findings

- The R10-FLOW-DESIGN-STAGES carry states the behaviour (stop on REFUSE) but names no control. The other carries in that group name one ("Controls: … refused; … passes; each has a mutant"). Owed with it: a self-test arm in which the rendered setup line under a refusing environment (`env -u OPENBLAS_CORETYPE`) stops the seat, a null control in which an OK environment proceeds, and a mutant that drops the stop. This is an orchestrator roster append, not a change to this PR. Carry: R10-FLOW-DESIGN-STAGES
- R10-POLICY-FIXER-MD is `in-progress`, and its fixer was dispatched 2026-10-24T07:52Z with a snapshotted brief. The carry landed at 8ecacecb1 at 16:48Z, so the running fixer has not read it. It reaches that group only at its next re-fire or review round, and the orchestrator should name it there. Carry: R10-POLICY-FIXER-MD
- My mutant R2 survives: `[ -x "${HPO_TYPING_PYTHON:-}" ]` → `[ -n "${HPO_TYPING_PYTHON:-}" ]` leaves the self-test at `13 checks, 0 failed`. So "`--check` answers OK only when HPO_TYPING_PYTHON is executable" is pinned only as "set" (M3 removes the whole half and is killed). Impact: a seat whose HPO_TYPING_PYTHON names a missing file reads OK, and then fails loudly at its first typing run. dismissed: low impact, the failure is loud and immediate rather than a silent wrong float, and a one-arm pin (a non-executable path) can ride the next change to cloud-setup.sh
- My mutant R3 survives: removing "OPENBLAS_CORETYPE is ${OPENBLAS_CORETYPE:-unset};" from the REFUSE text leaves the self-test green. The refusal-text arm pins the `NAME=value` remedy list, not the three read values the body says REFUSE names. dismissed: message text only, the exit code and the remedy list that a seat acts on are both pinned

## Evidence

- Head: db78749e927707a20e320318c335b5302ca98ed3, and still the branch tip by `git ls-remote` before writing (ev/HEAD.txt).
- Merge: `git merge-tree --write-tree origin/main db78749e9` exits 0 against origin/main 4a00a3f05, with no conflict (ev/merge_tree.txt). The merge base is 4a00a3f05, so the head already contains main.
- Three-dot diff vs the merge base: 7 files, +363/−13. VERSION, RELEASE_NOTES.md, the manifest and tests/golden are untouched (step 5), and no claim file moved (step 4: nothing to claim).
- sha1s at the head match the body: cloud-setup.sh c634e178…, r10_cloud_setup_mutants.py b4b5ba0d…, r10_cloud_setup_toolchain.py e5d50e1f… (ev/sha1.txt).
- Mutation table re-run in a Linux container with `/opt/hpo` (`python3 -I dev/audit/harnesses/r10_cloud_setup_mutants.py`): M0 PASS 3/3; M1–M13 and M12b each KILLED 3/3; `RESULT survivors=0`, rc 0 (ev/mutants_table.txt). This matches the body's table row for row.
- My own mutants, outside the fixer's table (ev/reviewer_mutants.txt): R1, the CORETYPE comparison inverted → `13 checks, 1 failed`, killed. R2 and R3 survive (Findings).
- Self-test at the head on a /dev/null stdin, 3 runs: `cloud_setup self-test: 13 checks, 0 failed` each time (ev/selftest.txt).
- `--check` in this container: `OK python3 is /opt/hpo/venv-ci/bin/python3`, rc 0. Under `env -u BASH_ENV -u OPENBLAS_CORETYPE`: REFUSE naming `OPENBLAS_CORETYPE is unset`, rc 1. Both outcomes are reachable, as the body's null control says.
- CI at this head: both CI runs (400 code, 399 edit) were still queued or in progress when this verdict was written. The heavy legs read `skipped` in run 399, and no check at this head has concluded red. At round 2's head 5e4fbb0d3 (same code), the "CI code" run 40105987941 concluded success. The "CI edit" run 40105987937's pr-contract failed at its "Wait for code scanning" step, before the body check ran. That is an infrastructure wait at a superseded head, not this code. Step 11 has no concluded red at this head to answer. The merge train reads this head's CI itself.
- Not re-derived: the macOS-seat figures (scoped gate `2 script(s) run`, structure, archscore `dS +0.0000`, ci_predict). I did not re-take them because the code is unchanged since round 2 and they are CI's heavy runs.
- Finder's harness (step 2): round 2's both-ends RESULT lines stand. The harness file and the script are byte-identical to round 2's (same sha1s), so I did not re-run it at both ends this round.
