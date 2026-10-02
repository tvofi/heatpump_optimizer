"""Reviewer's own round-2 mutants on budget_raise_gate.py (out-of-tree copies;
the unmutated copy fails exactly 2 environment checks, see mutant_none)."""
import subprocess, sys, pathlib
src = pathlib.Path(sys.argv[1]) / ".claude/workflows/budget_raise_gate.py"
text = src.read_text()
M = {
 "none": ("", ""),
 "revoked-off": ("and re.search(rf\"(?<!\\d){cid}(?!\\d)\", body)):", "and re.search(rf\"(?<!\\d){cid}(?!\\d)\", body)) and False:"),
 "revoked-owner": ("if (_is_owner(c.get(\"user\")) and MANDATE_REVOKED.search(body)", "if (MANDATE_REVOKED.search(body)"),
 "revoked-wholenum": ("re.search(rf\"(?<!\\d){cid}(?!\\d)\", body)", "re.search(rf\"{cid}\", body)"),
 "revoked-word": ("MANDATE_REVOKED.search(body)\n", "True\n"),
 "revoked-strict": ("MANDATE_REVOKED = re.compile(r\"revok\", re.I)", "MANDATE_REVOKED = re.compile(r\"^MANDATE REVOKED\")"),
 "edited-off": ("if updated != created:", "if False:"),
 "edited-old": ("if updated != created:", "if updated > at:"),
 "cr-override-off": ("if under and theirs and theirs[-1].get(\"state\") == \"CHANGES_REQUESTED\":", "if False:"),
 "issue-url-old": ("if not str(comment.get(\"issue_url\") or \"\").endswith(MANDATE_ISSUE_URL):\n        return False", "if not str(comment.get(\"issue_url\") or \"\").endswith(\"/issues/201\"):\n        return False"),
 "grammar-off": ("if not m:\n        return False, f\"{name}'s first line", "if False:\n        return False, f\"{name}'s first line"),
}
for name, (a, b) in M.items():
    n = text.count(a) if a else 1
    if n != 1:
        print(f"RESULT mutant {name}: anchor count {n}, NOT APPLIED"); continue
    out = pathlib.Path(sys.argv[2]) / f"r2_{name}.py"
    out.write_text(text.replace(a, b, 1) if a else text)
    p = subprocess.run([sys.executable, str(out), "--self-test"], capture_output=True, text=True, cwd=sys.argv[1])
    fails = [l.strip() for l in p.stdout.splitlines() if l.lstrip().startswith("FAIL") and "budget files" not in l]
    last = (p.stdout.strip().splitlines() or ["<no output>"])[-1]
    print(f"RESULT mutant {name}: rc={p.returncode} :: {last} :: non-env fails {len(fails)} :: {fails[:2]}")
