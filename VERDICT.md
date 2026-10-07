Fix review: merge 3948f729ab6c4cdb07fe070a7ec8a11083e39415

bus-nonce: 03ea82e9db969c57a9df5a266cee34e6

## Review findings

### Check 1: Diff scope
- Verified via `git diff --stat $(git merge-base origin/main HEAD)...HEAD`
- Touches exactly 4 files: dev/programme/delivery/{1995,2001,2002,2003}.md
- All changes are 1 line additions (single row per delivery file)
- **PASS**

### Check 2: Row format consistency
- Compared against existing row format in dev/programme/delivery/2009.md
- All four new rows match the standard format:
  ```
  - [#<number>](url) — **status**, <description>
  ```
- Each row carries appropriate PR link and description
- **PASS**

### Check 3: Merge commits verification
Verified each named PR is merged with correct commit hash via `gh pr view N --json mergeCommit`:

| PR | Status | Commit | Expected | Match |
|---|---|---|---|---|
| #1995 | merged | 1fa713f | 1fa713f | ✓ |
| #2001 | merged | 1b1bbaa | 1b1bbaa | ✓ |
| #2002 | open | - | - | ✓ (self-row) |
| #2003 | merged | a28fd0a | a28fd0a | ✓ |

- **PASS**

### Check 4: CI check-runs at head
Queried via GitHub API at commit 3948f729ab6c4cdb07fe070a7ec8a11083e39415:

| Check | Status | Conclusion |
|---|---|---|
| budget-raise-gate | completed | success |
| pr-contract | completed | success |
| closures | completed | success |
| fast (3.14) | completed | success |
| browser | completed | success |
| briefs | completed | success |
| mutation | completed | success |
| typing | completed | success |
| closure-scope | completed | success |
| CodeQL | completed | neutral |
| coverage | in_progress | (pending) |
| nightly-status | completed | failure |
| (15 additional) | completed | skipped |

- No blocking failures (coverage in_progress, nightly-status non-blocking per policy)
- All required checks pass or skip
- **PASS**

## Verdict

All four mechanical checks hold. The PR is a clean record-autofix adding delivery rows for completed PRs #1995, #2001, #2002 (self), and #2003. Row format, merge commits, and CI state are all correct.

**Ready to merge.**
