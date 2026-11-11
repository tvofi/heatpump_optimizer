Delivery-status, as it stands when two merges have gone unrecorded.

| item | state |
|---|---|
| docs merge | landed as #9003 |

Nothing here mentions the other two merges, which is the whole defect: a
resuming seat reading this table would not know they happened. The number 8888
appears nowhere either -- and it must not be demanded, because it is an issue
cited in a commit scope and not a merged pull request.

A second table, split by a blank line, which is the `table` acceptance. The two
halves below are one table in the source and two things on the page: everything
under the gap renders as literal text with its pipes showing.

| lane | state |
|---|---|
| first | recorded |

| second | invisible |

A stated cap, stale: the cap on `tools/audit/briefs/fixer.md` is 999 lines.
