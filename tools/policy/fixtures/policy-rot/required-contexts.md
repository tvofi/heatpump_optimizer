# Rot fixture: required-contexts

The three literal shapes the required-contexts class reads, one finding each,
so emptying any one regex from `REQUIRED_CONTEXT_RES` in counts.mjs reports
here rather than nowhere. The rule reads one line at a time, so each literal
sits on its own line; the live count the drive hands it is three.

The merge boundary is guarded by 18 required status checks.
`record` is one of `main-protect`'s 18 required contexts.
`hassfest` was the one member of the 18-context required set that had none.

The two lines below carry the same stale literal in the two dated-record
shapes -- a Delivery-status table row and a per-PR row -- and must produce
nothing: a record of what was measured at a merge is history, not a live
claim, and over-firing on it is what would get this class bypassed.

| **#9101** a table row | 18 required contexts stated here, and none of it is live |
- [#9101](x/pull/9101) a per-PR row, with its own 18 required contexts, is a dated record
