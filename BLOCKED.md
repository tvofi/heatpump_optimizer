# BLOCKED: r11-pre-toolchain-pin-p2, body_push.sh exit 4 (REFUSED CARRY-LANDED)

Code head: `handoff/r11-pre-toolchain-pin-p2` at a2c094d8c0e7aa8d8e4f9263e2e0179da914ac28, the head `tools/pr/prepr.sh` ran clean on (rc=0, body check included).

Body: kept by `body_push.sh` at `handoff-wip/r11-pre-toolchain-pin-p2-body` 24f623cb04a2e36a3be335b16554e5727150d226; `handoff-body/r11-pre-toolchain-pin-p2` is not pushed.

Owed by the relay: fold the four CARRY-MISSING items below onto the round's roster (three to R11-PRE-TOOLCHAIN-PIN, one to R11-PRE-PARALLEL-PIPELINE), then re-run `bash tools/audit/seat/body_push.sh r11-pre-toolchain-pin-p2 <body.md>` with the kept body. The review packet refuses nothing at this head.

Output of `bash tools/audit/seat/body_push.sh r11-pre-toolchain-pin-p2 <body.md>`, verbatim:

~~~text
fill-red: the diff adds no unpinned mutation site; nothing written
figure_block: refreshed 1 block(s) at a2c094d8c0e7
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R11-PRE-TOOLCHAIN-PIN at a2c094d8c0e7, 12 live, 6 dispatched carries, 0 refused
CARRY-STATUS R11-PRE-TOOLCHAIN-PIN body item 9833c393: a status line on its own carry, lands nothing: "- Carry 9, the rest of the design's p1, not built: the section 3 freshness sites repointed at `toolc"
CARRY-STATUS R11-PRE-TOOLCHAIN-PIN body item a00789b0: a status line on its own carry, lands nothing: '- Carry 7, not built: `train.sh`, `remerge_main.sh` and `merge_pr.sh` refuse on `behind` > 0 (design'
CARRY-STATUS R11-PRE-TOOLCHAIN-PIN body item f7b54cbd: a status line on its own carry, lands nothing: "- Carry 9, the design's p2 less the verdict function, not built: the gate summary's PRODUCT and MACH"
CARRY-STATUS R11-PRE-TOOLCHAIN-PIN body item 766671f4: a status line on its own carry, lands nothing: '- Carry 5 (the L3 helper: a process check whose input is unreadable prints an advisory unread line, '
CARRY-STATUS R11-PRE-TOOLCHAIN-PIN body item 1eaf8e55: a status line on its own carry, lands nothing: '- Carry 6 (the review packet marked `introduced-red: pending` on a running self-tests job), not buil'
CARRY-STATUS R11-PRE-TOOLCHAIN-PIN body item 6fd3d308: a status line on its own carry, lands nothing: '- Carry 8 (`introduced_at` over a cancelled main run, and dispatch on an in-progress self-tests job)'
CARRY-STATUS R11-PRE-TOOLCHAIN-PIN body item a62b1fec: a status line on its own carry, lands nothing: "- fixer.md: contradiction: Carry 10 stands at this part too. The payload's part line cuts by carry i"
CARRY-MISSING R11-PRE-TOOLCHAIN-PIN body item 806e1101: not in its brief or carries: '- After the merge the orchestrator runs `python3 -I tools/audit/seat/toolchain.py promote --init --r'
CARRY-MISSING R11-PRE-TOOLCHAIN-PIN body item 3e0749c4: not in its brief or carries: "- `tools/pr/cancel_superseded.py main` still has no beat row (carry 9's last sentence); part 1 has n"
CARRY-MISSING R11-PRE-PARALLEL-PIPELINE body item 0feb43b0: not in its brief or carries: '- For R11-PRE-PARALLEL-PIPELINE part 2, which edits `REQUIRED` and `event_class` in `tools/ci/gate.p'
CARRY-MISSING R11-PRE-TOOLCHAIN-PIN body item 695d23a5: not in its brief or carries: "- fixer.md: contradiction: the approved design's section 6 states p1 and p2 touch disjoint files, an"
CARRY-LANDED: 4 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-pre-toolchain-pin-p2-body 24f623cb04a2e36a3be335b16554e5727150d226
~~~
