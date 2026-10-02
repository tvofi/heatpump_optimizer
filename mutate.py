"""Reviewer's own mutants: each disables one refusal predicate in a copy of
budget_raise_gate.py and runs its --self-test; prints failed-check counts."""
import subprocess, sys, pathlib, re
src = pathlib.Path(sys.argv[1]) / ".claude/workflows/budget_raise_gate.py"
text = src.read_text()
M = {
 "expired":   ("if end is not None and at >= end:", "if False and end is not None and at >= end:"),
 "not-yet":   ("if at < max(start, created):", "if False and at < max(start, created):"),
 "revoked":   ("if r and int(r.group(1)) == cid and _is_owner(c.get(\"user\")):", "if False:"),
 "revoker-owner": ("if r and int(r.group(1)) == cid and _is_owner(c.get(\"user\")):", "if r and int(r.group(1)) == cid:"),
 "author":    ("if not _is_owner(comment.get(\"user\")):", "if False:"),
 "author-id": ("return (user.get(\"login\") == OWNER_LOGIN and user.get(\"id\") == OWNER_ID", "return (user.get(\"login\") == OWNER_LOGIN"),
 "issue":     ("if not str(comment.get(\"issue_url\") or \"\").endswith(f\"/issues/{MANDATE_ISSUE}\"):\n        return False, f\"{name} is not a comment on", "if False:\n        return False, f\"{name} is not a comment on"),
 "scope":     ("if scope not in MANDATE_COVERS_RAISE:", "if False:"),
 "grammar":   ("if not m:\n        return False, f\"{name}'s first line", "if False:\n        return False, f\"{name}'s first line"),
 "edited":    ("if updated > at:", "if False:"),
 "two-cites": ("if len(cited) > 1:", "if False:"),
 "agent-state": ("if r.get(\"state\") != \"APPROVED\" or not cited:", "if not cited:"),
}
for name, (a, b) in M.items():
    n = text.count(a)
    if n != 1:
        print(f"RESULT mutant {name}: anchor count {n}, NOT APPLIED"); continue
    out = pathlib.Path(sys.argv[2]) / f"m_{name}.py"
    out.write_text(text.replace(a, b))
    p = subprocess.run([sys.executable, str(out), "--self-test"], capture_output=True, text=True, cwd=sys.argv[1])
    fails = [l for l in p.stdout.splitlines() if l.lstrip().startswith("FAIL")]
    last = (p.stdout.strip().splitlines() or ["<no output>"])[-1]
    print(f"RESULT mutant {name}: rc={p.returncode} :: {last} :: {fails[:3]}")
