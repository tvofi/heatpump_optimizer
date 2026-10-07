"""Reviewer-built harness (not the finder's): path tricks against automerge_refusals."""
import sys
sys.path.insert(0, "tools/audit/seat")
import record_row as R
pr = {"number": 2002, "mergeable": True,
      "user": {"login": R.RECORD_AUTHOR, "type": "Bot", "id": R.RECORD_AUTHOR_ID},
      "head": {"ref": R.RECORD_BRANCH, "repo": {"full_name": R.DEFAULT_REPO}},
      "base": {"ref": "main", "repo": {"full_name": R.DEFAULT_REPO}}}
sha = "1fa713f" + "0"*33
facts = {1995: {"merged": True, "merge_commit_sha": sha, "title": "fix: x"}}
line = R.row_line(1995, "fix: x", sha, None)
def f(name): return {"filename": name, "status": "added", "additions": 1, "deletions": 0, "patch": "@@ -0,0 +1 @@\n+" + line}
cases = {
  "control canonical path": "dev/programme/delivery/1995.md",
  "arabic-indic digits": "dev/programme/delivery/١٩٩٥.md",
  "fullwidth digits": "dev/programme/delivery/１９９５.md",
  "leading zero": "dev/programme/delivery/01995.md",
  "trailing newline in name": "dev/programme/delivery/1995.md\n",
  "other dir": "dev/programme/delivery2/1995.md",
}
for k, name in cases.items():
    why = R.automerge_refusals(pr, [f(name)], facts)
    print(f"RESULT {k!r}: {'PASS (not refused)' if not why else 'REFUSED: ' + why[0]}")
# two files rowing the same PR
why = R.automerge_refusals(pr, [f("dev/programme/delivery/1995.md"), f("dev/programme/delivery/01995.md")], facts)
print("RESULT duplicate row for one PR at two paths:", "PASS (not refused)" if not why else why)
