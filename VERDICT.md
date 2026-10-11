Fix review: merge c6a35e0ef69d07853c92ae5c97efa609abaeef9c

Round 2+ review of the mechanical record beat #2128 (`record/autofix`), at
head c6a35e0ef69d07853c92ae5c97efa609abaeef9c. Contract read from
origin/main; one cosmetic drift noted in `dev/governance/roles/fixer.md`
(a harness path rename `tools/audit/harnesses/` -> `dev/audit/harnesses/`
landed on main after the merge base) — it does not affect this review.

What the PR is: two commits by hpo-author[bot] sitting directly on main
e743c2656f473c2f14e7e76bca62b56c0a2da1bd (its parent), promoting 31
pre-merge "open" delivery rows to merged rows and adding the PR's own row.

RESULT write-set: exactly 32 files, all `dev/programme/delivery/<N>.md` —
31 modified, 1 added (2128.md, this PR's own row). No production, test,
check, policy or claim file. `git merge-tree --write-tree origin/main
<head>` exits 0; no conflict.

RESULT rows: 15 PRs sampled across the range including the lowest (2010)
and highest (2131) — 2010, 2024, 2057, 2058, 2059, 2060, 2061, 2062, 2064,
2065, 2072, 2125, 2128, 2130, 2131. All 14 merged samples are MERGED in the
API and each row's 7-hex sha is the API mergeCommit's prefix (e.g. 2010 ->
1b72ca19fc40…, 2131 -> 5c02e2babd6a…). #2128 is OPEN in the API and its
row correctly reads "**open**".

RESULT grammar: byte-identical to the generator. Imported the head's
`tools/audit/seat/record_row.py` and regenerated rows for 2010, 2131 and
2072 from live API facts: MATCH on all three. #2128's open row matches
`open_row_line`'s shape with a title shortened to "record: delivery rows
(autofix)" because the real title names pull requests, which
`open_row_line` refuses — a correct application of the generator's own
refusal, not a deviation.

RESULT duplicates: 31 of 32 files pre-exist on main (as "open" rows);
the one new file (2128.md) does not exist on main. No duplicate rows, no
file on both that was not already there, no intra-branch duplicates
(`git ls-tree -r | sort | uniq -d` empty).

VERSION, manifest version and RELEASE_NOTES heading: untouched (absent
from the write set).

Red checks: no gate check red at the head (all success or skipped;
record/record-autofix skipped). The body's red-checks section names and
answers main's red `record` — the batch interval this PR is. Diff reaches
only delivery rows, so no unrelated red is this PR's.

Automerge predicate: `record_row.py --automerge-check --pr 2128 --head
c6a35e0ef…` REFUSES (31 rows are modified, not new files) — per
delivery-status-tracking.md that refusal is what sends the beat to manual
review; this review is that review, and nothing in the refusal is a
defect: promoting an open row to merged is necessarily a modification.

bus-nonce: e803eb352a153535b54b2615e8d87279
