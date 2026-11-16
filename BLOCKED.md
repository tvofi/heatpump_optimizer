# BLOCKED: r11-pre-shared-files, part 1, at the body push

`bash tools/audit/seat/body_push.sh r11-pre-shared-files BODY.md` exited 4 at 2026-11-16T05:58Z. The carries land on the roster this seat may not write; the relay folds them and re-runs `body_push.sh`.

State:
- Code: `handoff/r11-pre-shared-files` at `8be9d5a6b82721998212347c39224c91d5477aeb`, pushed. `tools/pr/prepr.sh BODY.md` at that head: `PRE-PR: 8be9d5a6b82721998212347c39224c91d5477aeb ... rc=0` (04:17Z to 05:51Z; one `WARN`, the 7 diff-mutant survivors `## Unpinned sites` disposes of). `git merge-tree --write-tree origin/main HEAD` exits 0 against `origin/main` `f9b680fee4`.
- Body: the refused body is kept by `body_push.sh` at `handoff-wip/r11-pre-shared-files-body` `34f6be97343e0c84127b822e3df9c3b9d6dfe1c9` (BODY.md). `handoff-body/r11-pre-shared-files` is unwritten.
- The review packet passes at this head (`0 refused`); the only refusal is CARRY-LANDED, on three body items that all carry to this group itself (the unbuilt `absorb` job pending owner decisions D1 and D2; the `touched_steps` rule; the cost of tracing `prepr.sh`'s self-test).

Output of `body_push.sh`, from the review packet's line to its end:

```
review-packet handoff: R11-PRE-SHARED-FILES at 8be9d5a6b827, 13 live, 5 dispatched carries, 0 refused
CARRY-MISSING R11-PRE-SHARED-FILES body item 8689c635: not in its brief or carries: '- dev/programme/rosters/wave-r10-groups.json, group R11-PRE-SHARED-FILES: the job that runs `python3'
CARRY-MISSING R11-PRE-SHARED-FILES body item 6aae4897: not in its brief or carries: '- dev/programme/rosters/wave-r10-groups.json, group R11-PRE-SHARED-FILES: `precheck` selects a step '
CARRY-MISSING R11-PRE-SHARED-FILES body item f25ed2c6: not in its brief or carries: "- fixer.md: cost: one `prepr.sh` run on a diff that changes `tools/pr/prepr.sh` traces that script's"
CARRY-LANDED: 3 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-pre-shared-files-body 34f6be97343e0c84127b822e3df9c3b9d6dfe1c9
```
