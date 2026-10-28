"""Reviewer's own mutants on Train.policy_approve's guard (built by the reviewer, not the finder's)."""
import subprocess, sys, concurrent.futures
from pathlib import Path
SRC = Path(sys.argv[1]) / "tools/audit/seat/merge_train.py"
MUT = [
 ("R0", "null: unmutated", "", ""),
 ("R1", "in-force: scope widened to code-owned", '"merge", g.MANDATE_COVERS_POLICY, "policy merging")\n        except',
  '"merge", g.MANDATE_COVERS_POLICY + ("code-owned",), "policy merging")\n        except'),
 ("R2", "in-force: unread mandate fails OPEN", "            live, why = False, f\"mandate {cid} could not be read",
  "            live, why = True, f\"mandate {cid} could not be read"),
 ("R3", "no owner approval yet: a stale owner approval (other head) counts",
  'r.get("state") == "APPROVED" and r.get("commit_id") == h\n               for r in self._reviews(pr, "the policy approval")',
  'r.get("state") == "APPROVED"\n               for r in self._reviews(pr, "the policy approval")'),
 ("R4", "no owner approval yet: any user's approval at head counts",
  'g._is_owner(r.get("user")) and r.get("state") == "APPROVED" and r.get("commit_id") == h\n               for r in self._reviews(pr, "the policy approval")',
  'r.get("state") == "APPROVED" and r.get("commit_id") == h\n               for r in self._reviews(pr, "the policy approval")'),
 ("R5", "budgets: guard reads only the policy paths", "if any(f.endswith(g.SUFFIX) for f in files):",
  "if any(f.endswith(g.SUFFIX) for f in pol):"),
 ("R6", "exactly one: first of several cited ids taken", "return cited.pop() if len(cited) == 1 else None",
  "return cited.pop() if cited else None"),
 ("R7", "head re-check before the post dropped", "        if self.head(pr) != h:\n            raise Stop(\"approve\", \"head moved before the mandate approval\")\n", ""),
]
def one(m):
    mid, arm, old, new = m
    t = SRC.read_text()
    if old and t.count(old) != 1: return mid, arm, f"STALE ({t.count(old)})", []
    d = SRC.parent / f"_rmut_{mid}.py"
    try:
        d.write_text(t.replace(old, new) if old else t)
        r = subprocess.run([sys.executable, str(d), "--self-test"], cwd=SRC.parents[3], capture_output=True, text=True, timeout=3000)
        f = [l.strip() for l in r.stdout.splitlines() if l.startswith("  FAIL")]
        st = ("PASS" if not f and r.returncode == 0 else "BROKEN") if mid == "R0" else ("KILLED" if f or r.returncode else "SURVIVED")
        return mid, arm, st, f
    finally: d.unlink(missing_ok=True)
with concurrent.futures.ThreadPoolExecutor(4) as ex:
    for mid, arm, st, f in ex.map(one, MUT):
        print(f"RESULT {mid} {st}: {arm}"); [print("    " + x[:220]) for x in f[:4]]
