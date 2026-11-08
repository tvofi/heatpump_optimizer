R10-POLICY-ROLE-PACK part 2. Carries 1-3 are already delivered by #3256; this adds the two that were not: carry 4 (the frugal-routing line) and the dispatch side of carry 0 (seats render their role pack). Policy-adjacent: the owner approves before merge.

Carry 1 (brief's Carry 0): partly covered by 41aa9050f (`tools/policy/role_pack.py`, hook). The part that was not there is `cloud_dispatch.py` naming the role. The cloud payload's `session_context` is `{allowed_tools, model, sources}` and I found no per-seat environment field in the tree, so I did not invent one. Each role's setup line now tells the seat to run `role_pack.py render <role> --out $HOME/role-pack.md` and read that file once. The probe gets no pack. Open for the owner: the SessionStart route (`HPO_SEAT_ROLE`) stays unused in the cloud until a payload env field is confirmed. The local-subagent SessionStart measurement was not made.
Carry 2 (brief's Carry 1): covered by 41aa9050f; the pack is verbatim and `role_pack.py --self-test` proves it.
Carry 3 (brief's Carry 2): covered by 41aa9050f; `tests/entities.py` could not run here (see Red checks).
Carry 4 (brief's Carry 3): covered by 41aa9050f (`nudge.md` step 3 edited in #3256).
Carry 5 (brief's Carry 4): new. `FRUGAL_LINE` is appended as its own line to every role's prompt in `_prompt`, verbatim from the brief.

## Head

ef3f9fbe9822fc0b20fc8fdf2cc1ad953c337158

## Mutation proof

Dropping `FRUGAL_LINE` from the `text` join in `_prompt` turns the self-test red (1 FAIL: "every role's prompt carries the frugal-routing line once, verbatim"). Restored, the self-test is 129 checks, 0 failed.

## Null control

At the base the prompt carries no such line and no pack instruction. The self-test arms I added fail there.

## Figures

none. The diff-mutant step ran with `MUTANT_CMD` set to the group's self-test and reported no survivor. It skipped `mutants` as the diff touches no file that step reads. I did not record the wall time.

## Red checks

`closures`: `prepr.sh` refused because `tests/entities.py` exits 1 here with `ModuleNotFoundError: homeassistant`. That is the seat environment, not this diff, which touches only `cloud_dispatch.py`. I did not work around it and left closure recording to CI. Every other prepr step is ok or skip, and `ci predict` predicts no red. Main had not moved when I checked, so there was no second prepr run. `merge-tree` reports no conflict.

## Forward-carry

none

## Friction

none
