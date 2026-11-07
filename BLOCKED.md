BLOCKED: r10-friction-ci-red repair round 2, toolchain.

The record correction is done and pushed on handoff-wip/r10-friction-ci-red: #3219 re-filed from group A to D (tests / mutation job 127045678304 failed 2026-11-05T04:18:12Z on aca500910, before the 04:32:06Z verdict; checked with filter=all over pages 1-3). Section 2, 3, 4 and 5 figures re-taken (A 7/7, 637 over 6 = 106 min, P_A 7/93; D 3/3); entries tsv unchanged (the reader prints verdict lines, not groups).

tools/pr/prepr.sh exits rc=1 on one step only: "REFUSE closures: failed while being recorded: tests/entities.py (exit 1)". Cause: ModuleNotFoundError: No module named 'homeassistant' (tests/harness.py:25). After `bash tools/audit/seat/cloud-setup.sh` and `--check`, neither /opt/hpo/venv-ci nor /opt/hpo/venv-ha has homeassistant; venv-ha also lacks scipy. The diff touches only markdown, and every other prepr step is ok. Not worked around.

Question: refresh the cached venvs (homeassistant, numpy, scipy) or rule that this refusal does not block a record-only head, then re-dispatch. Draft body: BODY.md at this ref's parent commit is not pushed; it is rebuilt from the prior kept body with the Head, Figures and Red checks re-taken.
