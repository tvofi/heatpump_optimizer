# `record_beat.py`

- `record_beat.py` — posts one #201 line per merged pull request from a
  fixed template (pull request, the full merge sha resolved from git, roster
  group, issues the merge closed, "Leaves #201 open"), the body file under the
  state directory, through `tools/pr/gh_comment.py` with its byte-identical
  read-back. When: `postmerge.py` calls it; by hand for a merge the tick reads
  as unrecorded. Refusals: an unmerged pull request, a merge commit git cannot
  resolve to 40 hex, or a read-back mismatch exits non-zero (`OWED record`).
