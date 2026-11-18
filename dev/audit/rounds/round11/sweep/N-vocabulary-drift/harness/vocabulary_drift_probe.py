#!/usr/bin/env python3
"""Probe each N-vocabulary-drift instance beyond the judged findings.
Usage: vocabulary_drift_probe.py SEAM  (exit 1 = drift reproduced)."""
import ast, re, sys
from pathlib import Path
sys.path.insert(0, "tools/audit/seat"); sys.path.insert(0, ".")


def lit(path, name):
    for n in ast.walk(ast.parse(Path(path).read_text())):
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
            return ast.literal_eval(n.value.args[0] if isinstance(n.value, ast.Call) else n.value)
    raise SystemExit(f"PROBE-ERROR {name} not in {path}")


def js_list(path, name):
    m = re.search(rf"const {name} = (?:new Set\(\s*)?\[([^\]]*)\]", Path(path).read_text())
    return re.findall(r"'([^']*)'", re.sub(r"//[^\n]*", "", m.group(1)))


def fail(msg):
    print("FAIL", msg); sys.exit(1)


seam = sys.argv[1]
if seam == "ci_priority_guard":
    import ci_priority as cp
    tiers = lit("tools/audit/seat/ci_priority.py", "TIERS")
    guards = lit("tools/audit/seat/ci_priority.py", "GUARDS")
    # check_setting admits TIERS+GUARDS in never_cancel; tier() returns only TIERS,
    # so a never_cancel guard word is a word the reader can never close.
    inert = [g for g in guards if g not in tiers]
    if inert:
        fail(f"never_cancel accepts {inert} (ci_priority.py check_setting) but tier() yields only {list(tiers)}")
elif seam == "stage_vocab":
    known = set(js_list(".claude/workflows/web-fix-wave.js", "KNOWN_STAGES"))
    import roster_lib
    kinds = {k[0] if isinstance(k, tuple) else k for k in roster_lib.STAGE_KIND}
    missing = sorted(kinds - known - {"pending"})
    if missing:
        fail(f"roster_lib.STAGE_KIND words the wave's KNOWN_STAGES refuses (web-fix-wave.js throws): {missing}")
elif seam == "friction_family":
    real = set(lit("tools/audit/seat/review_strength.py", "REAL_CATCH"))
    txt = Path("tools/policy/policy_lint.mjs").read_text()
    fam = re.search(r"const FRICTION_FAMILIES = [\s\S]*?\n\}?\]?\)?\n", txt).group(0)
    words = set(re.findall(r"'([a-z][a-z0-9-]*)'", fam))
    taught = set(js_list(".claude/workflows/web-fix-wave.js", "VERDICT_CLASSES"))
    lost = sorted(w for w in real - taught - words)
    if lost:
        fail(f"block words review_strength counts REAL that policy_lint's FRICTION_FAMILIES keys nowhere: {lost}")
elif seam == "design_verdict":
    import owed_watch as ow
    sha = "a" * 40
    m = ow.DESIGN_VERDICT.match(f"Design review: aprove {sha}") if hasattr(ow.DESIGN_VERDICT, "match") \
        else re.match(ow.DESIGN_VERDICT, f"Design review: aprove {sha}")
    if m and m.group(1) not in ("approve", "revise"):
        fail(f"DESIGN_VERDICT accepts '{m.group(1)}': neither FIXER-OWED (approve) nor DESIGN-REVIEW-OWED fires (owed_watch.py:219-228)")
elif seam == "blocked_grammar":
    import proof_watch as pw
    sha = "b" * 40
    wave = re.compile(r"^Fix review:\s+(?:(merge)\s+([0-9a-f]{40})|(blocked)\s+([0-9a-f]{40})"
                      r"(?:\s+([a-z][a-z0-9-]*)\s*:\s*(.+)|\s*:\s*(.+)|\s*))$")
    lost = [v for v in (f"Fix review: blocked {sha}: why", f"Fix review: blocked {sha}",
                        f"Fix review: blocked {sha} d13-s2: why")
            if wave.match(v) and pw.parse_verdict(v) is None]
    if lost:
        fail(f"verdicts web-fix-wave.js:VERDICT_RE parses that proof_watch.parse_verdict returns None for: {lost}")
else:
    raise SystemExit("unknown seam")
print("PASS", seam)
