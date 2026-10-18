#!/usr/bin/env python3
"""Reviewer's round-10 plants for #2345: an anchor (not a form) outside the shadow root in a driven press, href by a built name, clicked."""
import sys, subprocess
sys.path.insert(0, "tools/audit/seat")
import r10_deeplink_mutants as d
P = d.P
PLANTS = {
  "RD6_anchor_built_href_outside_root_click_driven": d.after_nav('try { const a = document.createElement("a"); a.setAttribute(["hr", "ef"].join(""), "%s"); document.body.appendChild(a); a.click(); } catch (_e) {}' % P),
  "RD6c_anchor_built_href_in_root_driven_control": d.after_nav('try { const a = document.createElement("a"); a.setAttribute(["hr", "ef"].join(""), "%s"); root.appendChild(a); } catch (_e) {}' % P),
}
if __name__ == "__main__":
    print("HEAD", subprocess.run(["git","rev-parse","HEAD"],capture_output=True,text=True).stdout.strip())
    for n in sys.argv[1:] or list(PLANTS):
        d.run(n, PLANTS[n])
    left = subprocess.run(["git", "status", "--short", "--", d.CARD, d.TEST], capture_output=True, text=True).stdout
    print("restored" if not left.strip() else "NOT RESTORED:\n" + left)
