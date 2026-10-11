Fix review: merge 327845686e0a8ad8322037c27886497804c1e8bd

bus-nonce: 7ed9dcc8b19039fa042243e575d90d6d

Round: first review of this record PR (mechanical record beat R9-FR-10).
Head measured: 327845686e0a8ad8322037c27886497804c1e8bd (branch tip re-checked via
ls-remote immediately before publishing — unchanged).

RESULT rows-vs-api: 27 of 27 row subjects checked against the live REST API
(`gh pr view <n> --json state,mergedAt,mergeCommit`), not the sampled minimum —
lowest #2010 and highest #2125 included. Every one is MERGED and every row's
7-hex sha is a prefix of the API's own mergeCommit.oid. Evidence:
row-api-check.txt.

RESULT no-duplicates: the diff against origin/main carries 27 MODIFIED files and
exactly one ADDED file. Main already holds orchestrator stub rows reading
"**open**" for each of the 27 (written at PR-open time); this beat rewrites each
stub to "**merged `<sha7>`**", so no pull request gets a second row. The one new
file, dev/programme/delivery/2128.md, does not exist on main and is the PR's own
row, truthfully "**open**". Evidence: diff-file-list.txt.

RESULT grammar: regenerating with the head's own record_row.row_line() — fed the
API title, the API merge sha, and roster_lib.group_for_branch against main's
.claude/workflows/wave-3l-groups.json — reproduces four sampled rows (#2010,
#2083, #2124, #2125) byte-for-byte, group=None on each: the head branches
(fix/r9-ux-actions, fix/r9-closures-inert-prestudy,
fix/r9-autofix-governance, docs/r9-rc-postreview-merge) answer no roster group
id, so the neutral phrasing the body claims is what the generator itself
produces. record_row.self_row(2128) reproduces 2128.md byte-for-byte. No pipe
sanitising case arose in the sample (no title carried a `|`); no closing keyword
on any sampled line. Evidence: grammar-check.txt.

RESULT write-set: `git diff --name-status origin/main...<head>` touches only
dev/programme/delivery/*.md — 28 files, nothing else.

RESULT checks: check-runs at the head show no red. `coverage` was in_progress at
measurement time; every other check success or skipped (pr-contract success).
nightly-status success, delivery-status-publish skipped — neither red, so no
root-cause answer is owed.

RESULT conflicts: git merge-tree --write-tree origin/main <head> exits 0 —
clean merge.

Notes (non-blocking): #2121's row cites a745200, which is origin/main's current
tip — correct. The status-rewrite guard refusal the module docstring documents
(27 modified files) is exactly why this beat is under manual review rather than
automerge; consistent with the body's Approval section.

Evidence dir: /Users/timmalmstrom/hpo-seats/r9rev-2128/evidence/
(README.txt names the head; row-api-check.txt, diff-file-list.txt,
grammar-check.txt, check-runs.txt)
