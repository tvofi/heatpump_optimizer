# carry 5's entities predicate, copied, run against a given policy_lint.mjs --budgets output
import subprocess, sys
rows = subprocess.run(["node", sys.argv[1], "--budgets"], capture_output=True, text=True).stdout.splitlines()
BR = lambda f: [l for l in rows if l.split()[:1] == [f]]
ok = (len(BR("dev/audit/README.md")) == 1 and BR("dev/audit/README.md")[0].endswith("key tools/audit/README.md")
      and BR("tools/audit/README.md") == [] and len(BR("tests/README.md")) == 1 and " key " not in BR("tests/README.md")[0])
print("PASS" if ok else "FAIL")
