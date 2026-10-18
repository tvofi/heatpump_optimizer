#!/bin/sh
# Review item 8: every reader and writer of the C1 composition at a tree, so PR 1
# can remove the composition AT ITS SOURCE and show nothing is left to prove.
#   sh measure/rev/c1_consumers.sh <rev>    (from a full checkout; default origin/main)
# Prints each tracked file outside the historical record that names a C1 token,
# with its matching lines. After PR 1, the same command at PR 1's head must print
# only the fixture lines of merge_train.py / orchestrator_tick.py (a non-required
# lane that never concludes, named after composed-proof; kept as a class fixture)
# and nothing under .github/, tools/coverage/, tests/ (the check PR 1's entities.py
# pin makes permanent).
REV=${1:-origin/main}
PAT='composed_closures|composed-closures|composed-verify|composed_verify|composed_proof|composed-proof|CHEAP_ARGV_OR_ENV|\$COMPOSED|COMPOSED=|COMPOSED"|_COMPOSED|composed_arm'
git grep -n -E "$PAT" "$REV" -- . ':!dev/archive' ':!dev/audit/rca' ':!dev/audit/rounds' \
  ':!dev/programme' ':!RELEASE_NOTES.md' | sed "s#^$REV:##" | cut -c1-160
echo "--- files:"
git grep -l -E "$PAT" "$REV" -- . ':!dev/archive' ':!dev/audit/rca' ':!dev/audit/rounds' \
  ':!dev/programme' ':!RELEASE_NOTES.md' | sed "s#^$REV:##"
