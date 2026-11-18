Fix review: merge e4fbf16e79cb90cb93284e57a4aeeaceaa738f55

bus-nonce: ba4a3a8b62c1785fdad6ef1a3b649a9f

Round 1 at e4fbf16e79cb90cb93284e57a4aeeaceaa738f55 (no verdict existed at f3b3f4f9); whole PR reviewed, three-dot against merge base ae0ed64af898d8923ac35afe6e9c031ac1e6b111.

## Evidence

- The diff touches only dev/programme/RULINGS.md, 46 added lines, one new section; VERSION, RELEASE_NOTES.md, the manifest, custom_components/ and the claim files are untouched (ev/record-checks.txt).
- git merge-tree --write-tree origin/main at the head exits 0 (ev/merge-tree.txt).
- No home path in the added text (ev/record-checks.txt). Every added entry carries the date 2026-11-18. No entry states an opinion; the two verbatim quotes are decisions ("I confirm your plan", "Let them land as planned").
- Steps 1-3, 6, 9, 14-16 have nothing to act on: no production, test, harness, budget or actuator line. The mutation and null-control "n/a" in the body is correct for a text-only diff.
- Check runs at the head have no red (ev/check-runs.txt). arch-score, budget-raise-gate and refresh were still running when read, so the merge step must re-read them live.

## Findings

- Note: record-count: the entry "2026-11-18, four rulings (as recorded)" lists only items (1) to (3); either a ruling is missing or the count is wrong. Carry: dismissed: author's correction inside this PR before merge, no later stage changes
- Note: record-stale-preamble: the new section says "the bracketed readings are the orchestrator's", but none of its entries has a bracketed reading; the file's own marker for an interpretation is "orchestrator's reading". Carry: dismissed: author's correction inside this PR before merge, no later stage changes
- Note: record-scope: "after one hour without an answer" and "ADR-006 part 2 was explained to him, then:" describe how the ruling came about, not what it decides (CLAUDE.md: an owner ruling is quoted only for what it decides). Carry: dismissed: author's correction inside this PR before merge, no later stage changes
- Note: body-stale: the PR title and the commit f3b3f4f9 say "rulings 2026-11-17 and 2026-11-18", but every added entry is dated 2026-11-18. Carry: dismissed: title wording only, no later stage changes

RESULT: merge e4fbf16e79cb90cb93284e57a4aeeaceaa738f55, 4 paperwork notes, no block (C5: records only, nothing under custom_components/).
