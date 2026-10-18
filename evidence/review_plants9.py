#!/usr/bin/env python3
"""Reviewer's round-9 plants for #2345: the RV spellings placed in a DRIVEN press (after_nav), to test the residual's 'exactly'."""
import sys, subprocess
sys.path.insert(0, "tools/audit/seat")
import r10_deeplink_mutants as d
P = d.P
PLANTS = {
  "RD1_history_bracket_back_driven": d.after_nav('try { globalThis.history["back"](); } catch (_e) {}'),
  "RD4_form_ns_action_member_button_click_driven": d.after_nav('try { const u = "%s"; const f = document.createElementNS("http://www.w3.org/1999/xhtml", "form"); f.action = u; const b = document.createElement("button"); f.appendChild(b); document.body.appendChild(f); b.click(); } catch (_e) {}' % P),
  "RD5_action_member_to_variable_on_rendered_form_driven": d.after_nav('try { const u = "%s"; const f = document.createElementNS("http://www.w3.org/1999/xhtml", "form"); f.action = u; root.appendChild(f); } catch (_e) {}' % P),
}
if __name__ == "__main__":
    print("HEAD", subprocess.run(["git","rev-parse","HEAD"],capture_output=True,text=True).stdout.strip())
    for n in sys.argv[1:] or list(PLANTS):
        d.run(n, PLANTS[n])
    left = subprocess.run(["git", "status", "--short", "--", d.CARD, d.TEST], capture_output=True, text=True).stdout
    print("restored" if not left.strip() else "NOT RESTORED:\n" + left)
