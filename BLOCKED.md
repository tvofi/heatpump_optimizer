body_push.sh r11-pre-toolchain-pin exited 4 at code head 75e1734490c895044e736ffe128850a718c1fb3b (handoff/r11-pre-toolchain-pin, pushed); prepr.sh was clean at that head (PRE-PR rc=0, PREPR_SKIP_CLOSURES=1 PREPR_SKIP_CODE=1 after a code run whose only refusals were the body's). The refused body is kept at handoff-wip/r11-pre-toolchain-pin-body 3af69d8133ca8926e37622272bc42fd398a2ee3e. Output of body_push.sh, whole:

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R11-PRE-TOOLCHAIN-PIN at 75e1734490c8, 13 live, 13 dispatched carries, 0 refused
CARRY-STATUS R11-PRE-TOOLCHAIN-PIN body item 275f4d36: a status line on its own carry, lands nothing: '- Carry 1: built (`open_driver.py retry`, acceptance (i)-(iv) in `open_driver_selftest.py`). Carry: '
CARRY-STATUS R11-PRE-TOOLCHAIN-PIN body item cee9f2a4: a status line on its own carry, lands nothing: "- Carry 2: built (acceptance (i)-(v) in `open_driver_selftest.py`; the beat's freshness arm is untou"
CARRY-STATUS R11-PRE-TOOLCHAIN-PIN body item 635d2038: a status line on its own carry, lands nothing: '- Carry 3: built (`cancel_superseded.py main`). Carry: R11-PRE-TOOLCHAIN-PIN'
CARRY-MISSING R11-PRE-TOKEN-LEDGER body item d29d6a0f: not in its brief or carries: "- fixer.md: unclear: this repair's dispatch PROMPT (`dispatch/fixer-r11-pre-toolchain-pin` at a546de"
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-pre-toolchain-pin-body 3af69d8133ca8926e37622272bc42fd398a2ee3e
```
