# BLOCKED: R11-PRE-PRODUCT-READS

Question: The approved design (design/R11-PRE-PRODUCT-READS 8daf118368, approved by a08d8f47c9) puts this group after R11-PRE-BRIEFS-CENSUS merges, because both parts import their universes from `tools/audit/enumerate.py` (`d12-cells`, `d16-writes --cells`, `d0-grid`, `d15-installs`). The dispatch says "After: none", but CENSUS (PR #3625, head 1c4704b8f4) is still open and `tools/audit/enumerate.py` is absent at origin/main 98847b99d7. Should the orchestrator add the `after` edge on R11-PRE-BRIEFS-CENSUS and re-dispatch once #3625 merges, or authorize cutting p1 on the CENSUS head?

Evidence, measured at origin/main 98847b99d7:
- `test -e tools/audit/enumerate.py || echo absent` prints `absent`.
- The GitHub PR list filtered to head `fix/r11-pre-briefs-census` returns #3625, state open, merged false.
- Design section 7: "Serial position: after CENSUS merges (the enumerator is on no main)"; the `after` edge is routed as "decision: orchestrator".

Without the enumerator, no read can meet the acceptance line ("exits 0 and prints a non-empty universe"), and cutting on an unmerged head would carry CENSUS's diff into this pull request. No code was written.
