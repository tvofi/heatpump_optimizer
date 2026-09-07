Delivery-status, as it stands when two merges have gone unrecorded.

| item | state |
|---|---|
| docs merge | landed as #9003 |

Nothing here mentions the other two merges, which is the whole defect: a
resuming seat reading this table would not know they happened. The number 8888
appears nowhere either -- and it must not be demanded, because it is an issue
cited in a commit scope and not a merged pull request.
