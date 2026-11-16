"""Reviewer-built mutant driver for PR 3657 at 3868879d: apply one textual mutation, run the owning self-test, restore."""
import subprocess, sys, pathlib
LL, RL = "tools/audit/seat/loop_ledger.py", "tools/audit/seat/roster_lib.py"
T = {LL: [["python3", "-I", LL, "--self-test"]],
     RL: [["python3", RL, "--self-test"], ["python3", "-I", "tools/audit/seat/roster_edit.py", "--self-test"]]}
M = [
 ("blame-precedence", LL, "{**entered(b.stdout), **when}", "{**when, **entered(b.stdout)}"),
 ("kids-every", LL, "kids = sum(1 for g in every if", "kids = sum(1 for g in groups if"),
 ("refix-recorded", LL, 'if roster_lib.recorded(g, ("follows",), names)]', 'if g.get("follows")]'),
 ("week-unentered", LL, 'else "unentered"', 'else "unknown"'),
 ("entered-setdefault", LL, "out[m.group(1)] = t", "out.setdefault(m.group(1), t)"),
 ("rca-file", RL, "    except (OSError, UnicodeDecodeError):\n        return False\n    me, own", "    except (OSError, UnicodeDecodeError):\n        text = ''\n    me, own"),
 ("rca-id-regex", RL, "if not isinstance(rca, str) or not _RCA_ID.match(rca):", "if not isinstance(rca, str):"),
 ("rca-own-arm", RL, "(isinstance(own, list) and rca in own) or ", ""),
 ("rca-name-arm", RL, " or me in {t.strip(\".-\") for t in re.findall(r\"[\\w.-]+\", text)}", ""),
 ("rca-substring", RL, "me in {t.strip(\".-\") for t in re.findall(r\"[\\w.-]+\", text)}", "(me or '') in text"),
 ("rca-nostrip", RL, "{t.strip(\".-\") for t in", "{t for t in"),
 ("rca-bool-own", RL, "(isinstance(own, list) and rca in own)", "(bool(own) and (own is True or rca in own))"),
 ("cw-rca-gate", RL, "    if not rca_lists(rca, group, root):", "    if False:"),
]
only = sys.argv[1:]
for name, f, a, b in M:
    if only and name not in only: continue
    p = pathlib.Path(f); src = p.read_text()
    if src.count(a) != 1:
        print(f"{name}: SITE-NOT-UNIQUE ({src.count(a)})"); continue
    p.write_text(src.replace(a, b))
    try:
        killed = None
        for cmd in T[f]:
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=400)
                if r.returncode: killed = f"{cmd[-2] if cmd[-1]=='--self-test' else cmd[-1]} rc={r.returncode}: " + (([l for l in r.stdout.splitlines() if l.startswith("FAIL")] or r.stdout.splitlines()[-1:] or r.stderr.splitlines()[-1:]) [:1] or [""])[0][:160]; break
            except subprocess.TimeoutExpired:
                killed = "timeout"; break
        print(f"{name}: {'KILLED ' + killed if killed else 'SURVIVED'}", flush=True)
    finally:
        p.write_text(src)
