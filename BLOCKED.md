body_push.sh r11-pre-toolchain-pin exited 4 at code head b5df34db8aac1a0bd185cf7f4aa5bce831bf85b0 (handoff/r11-pre-toolchain-pin); prepr.sh was clean at that head (PRE-PR rc=0). The refused body is kept at handoff-wip/r11-pre-toolchain-pin-body. Output of body_push.sh, whole:

```
fill-red: the diff adds no unpinned mutation site; nothing written
figure_block: refreshed 1 block(s) at b5df34db8aac
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R11-PRE-TOOLCHAIN-PIN at b5df34db8aac, 9 live, 5 dispatched carries, 0 refused
CARRY-STATUS R11-PRE-TOOLCHAIN-PIN body item 275f4d36: a status line on its own carry, lands nothing: '- Carry 1: built (`open_driver.py retry`, acceptance (i)-(iv) in `open_driver_selftest.py`). Carry: '
CARRY-STATUS R11-PRE-TOOLCHAIN-PIN body item cee9f2a4: a status line on its own carry, lands nothing: "- Carry 2: built (acceptance (i)-(v) in `open_driver_selftest.py`; the beat's freshness arm is untou"
CARRY-STATUS R11-PRE-TOOLCHAIN-PIN body item 635d2038: a status line on its own carry, lands nothing: '- Carry 3: built (`cancel_superseded.py main`). Carry: R11-PRE-TOOLCHAIN-PIN'
CARRY-MISSING R11-PRE-TOOLCHAIN-PIN body item 3a999745: not in its brief or carries: "- The design's p1 other than carries 1 and 2 (the toolchain instrument with promote and behind, the "
CARRY-MISSING R11-PRE-TOOLCHAIN-PIN body item 690cba76: not in its brief or carries: '- fixer.md: contradiction: the dispatch\'s generated part line cuts a group by carry index ("Part 1 o'
CARRY-LANDED: 2 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
fatal: expected 'acknowledgments', received 'packfile'
warning: push negotiation failed; proceeding anyway with push
remote: 
remote: Create a pull request for 'handoff-wip/r11-pre-toolchain-pin-body' on GitHub by visiting:        
remote:      https://github.com/tvofi/heatpump_optimizer/pull/new/handoff-wip/r11-pre-toolchain-pin-body        
remote: 
body_push: refused body kept at handoff-wip/r11-pre-toolchain-pin-body 783a614c0bd20f90c579ff0fb956b7b5cd404698
```
