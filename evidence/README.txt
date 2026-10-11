head: 327845686e0a8ad8322037c27886497804c1e8bd
pr: 2128
branch: record/autofix
measured-at: 2026-10-11 (ls-remote re-checked immediately before verdict push)

Checks performed
1. Row truth vs live API: all 27 row subjects (#2010..#2125 per body) queried with
   `gh pr view <n> --json state,mergedAt,mergeCommit`. Every one MERGED; every row's
   7-hex sha is the prefix of the API mergeCommit.oid. Lowest 2010=1b72ca19..., highest
   2125=6be8883e...; full table in row-api-check.txt.
2. Duplicates: diff branch vs origin/main names 27 M files and one A file
   (dev/programme/delivery/2128.md). Main already carries stub rows ("open") for the 27;
   the PR rewrites stubs to merged, it does not add a second row. The one NEW file (2128)
   does not exist on main (`git show origin/main:dev/programme/delivery/2128.md` fails).
   File list in diff-file-list.txt.
3. Grammar: record_row.row_line() at the head, fed the API title + merge sha and
   roster_lib.group_for_branch against main's wave-3l-groups.json, reproduces rows
   2010, 2083, 2124, 2125 byte-for-byte (group=None: head branches fix/r9-ux-actions,
   fix/r9-closures-inert-prestudy, fix/r9-autofix-governance, docs/r9-rc-postreview-merge
   answer no roster group id, so the neutral phrasing is correct). self_row(2128)
   reproduces 2128.md byte-for-byte. Output in grammar-check.txt.
4. Write set: `git diff --name-status origin/main...<head>` touches only
   dev/programme/delivery/*.md (28 files). Nothing else. In diff-file-list.txt.
5. Red checks: check-runs at the head — no red; `coverage` in_progress at measurement
   time, all others success/skipped (check-runs.txt). pr-contract success.
   nightly-status / delivery-status-publish are success/skipped, not red.
6. Conflicts: `git merge-tree --write-tree origin/main <head>` exit 0, no conflict.
7. Head stability: ls-remote refs/heads/record/autofix = 327845686e0a8ad8322037c27886497804c1e8bd
   immediately before publishing.
