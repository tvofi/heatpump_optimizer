import subprocess, sys
sys.path.insert(0, "tests")
import layout
rows = subprocess.run(["node", layout.locate(".claude/workflows/policy_lint.mjs"), "--budgets"], capture_output=True, text=True).stdout.splitlines()
BR = lambda f: [ln for ln in rows if ln.split()[:1] == [f]]
ok = (len(BR("dev/audit/README.md")) == 1
    and BR("dev/audit/README.md")[0].endswith("key tools/audit/README.md")
    and BR("tools/audit/README.md") == []
    and len(BR("tests/README.md")) == 1
    and " key " not in BR("tests/README.md")[0])
print("PASS" if ok else "FAIL", BR("dev/audit/README.md") + BR("tools/audit/README.md") + BR("tests/README.md"))
