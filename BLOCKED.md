# BLOCKED: r10-arch-docs, body push refused CARRY-LANDED

Code head: c4c28b4cef17868052d2018879340e617b2ca119, on `handoff/r10-arch-docs`. `tools/pr/prepr.sh <body>` at that head: rc=0, every step ok or skip.
Body: kept by `body_push.sh` at `handoff-wip/r10-arch-docs-body` 11135cc12284282966d74bdd5c2369127e8073d6.

Question: none. The three carries below land on the round's roster branch, which this seat may not write. The relay folds them and re-runs `bash tools/audit/seat/body_push.sh r10-arch-docs <body>`.

`body_push.sh` output (exit 4):

```
review-packet handoff: R10-ARCH-DOCS at c4c28b4cef17, 15 carries, 0 refused
CARRY-MISSING R10-ARCH-DOCS-DELTA body item 6bc4f4e1: not in its brief or carries: "- `dev/programme/rosters/wave-r10-groups.json`, R10-ARCH-DOCS-DELTA's brief: `tests/doc_claims.py` n"
CARRY-MISSING R10-ARCH-DOCS-DELTA body item d5ef2398: not in its brief or carries: "- `dev/programme/rosters/wave-r10-groups.json`, R10-ARCH-DOCS-DELTA's brief: `dev/README.md` states "
CARRY-MISSING R10-USER-DOCS-VERIFY body item a44d0012: not in its brief or carries: "- `dev/programme/rosters/wave-r10-groups.json`, R10-USER-DOCS-VERIFY's brief: `check_marker_census`'"
CARRY-LANDED: 3 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
```
