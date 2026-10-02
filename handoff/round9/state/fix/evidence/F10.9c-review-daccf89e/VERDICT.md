Fix review: merge daccf89e90690448635ff4f1afa8139a50f5fbc8

Merge-delta judgement for PR #1823 (stage 1): d3539e99..daccf89e, a merge of main e1ded322 (carrying #1828 and #1808).
- The tree of daccf89e equals git merge-tree e1ded322 d3539e99: clean, with no hand edits.
- The PR's own content against main, e1ded322..daccf89e (14 files), is byte-identical in +/- lines to its
  content against the previous main, fee38809..d3539e99. The auto-merged tests.yml, entities.py and prepr.sh
  therefore carry nothing new from this PR.
- At daccf89e: merge_fastpath --self-test passes 25/25, codeowners_gap reports uncovered_files=0, and every
  workflow that lists pull_request still declares concurrency.
- Main has since moved to 4ac63b0a (the v6.7.13 stamp). merge-tree against it is clean.
UNRUN: CI on daccf89e (merge on green only), typing, real-HA.
