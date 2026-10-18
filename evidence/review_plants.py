#!/usr/bin/env python3
"""Reviewer's own plants for #2345, applied with the PR driver's run() (same
apply/run/restore). Run from a worktree root at the head, after plan_view.py."""
import sys, subprocess
sys.path.insert(0, "tools/audit/seat")
import r10_deeplink_mutants as d
K = d.KEYDOWN
P = d.P
def kd(stmt): return d.card(K, "      " + stmt + "\n" + K)
PLANTS = {
  # history member through a computed key / optional chain, written, undriven
  "RV1_history_bracket_back_in_undriven_keydown": kd('try { globalThis.history["back"](); } catch (_e) {}'),
  "RV2_history_optional_back_in_undriven_keydown": kd('try { globalThis.history?.back(); } catch (_e) {}'),
  "RV3_history_destructure_in_undriven_keydown": kd('try { const { back } = globalThis.history; back.call(globalThis.history); } catch (_e) {}'),
  # programmatic form with no refused row: createElementNS, .action by member to a variable, submit by button click
  "RV4_form_ns_action_member_button_click_in_undriven_keydown": kd('try { const u = "%s"; const f = document.createElementNS("http://www.w3.org/1999/xhtml", "form"); f.action = u; const b = document.createElement("button"); f.appendChild(b); document.body.appendChild(f); b.click(); } catch (_e) {}' % P),
  "RV5_action_member_to_variable_in_undriven_keydown": kd('try { const u = "%s"; const f = document.createElement("div"); f.action = u; } catch (_e) {}' % P),
  "RV6_object_assign_quoted_action_key_in_undriven_keydown": kd('try { const f = document.createElement("div"); Object.assign(f, { "action": "%s" }); } catch (_e) {}' % P),
  "RV7_create_element_ns_form_in_undriven_keydown": kd('try { const f = document.createElementNS("http://www.w3.org/1999/xhtml", "form"); root.appendChild(f); } catch (_e) {}'),
  # controls: same position, spellings the census claims (red expected)
  "RV1c_history_dot_back_control": kd('try { globalThis.history.back(); } catch (_e) {}'),
  "RV5c_action_member_to_literal_control": kd('try { const f = document.createElement("div"); f.action = "%s"; } catch (_e) {}' % P),
}
if __name__ == "__main__":
    if subprocess.run(["git", "status", "--short", "--", d.CARD, d.TEST], capture_output=True, text=True).stdout.strip():
        sys.exit("refusing: dirty")
    print("HEAD", subprocess.run(["git","rev-parse","HEAD"],capture_output=True,text=True).stdout.strip())
    for n in sys.argv[1:] or list(PLANTS):
        d.run(n, PLANTS[n])
    left = subprocess.run(["git", "status", "--short", "--", d.CARD, d.TEST], capture_output=True, text=True).stdout
    print("restored" if not left.strip() else "NOT RESTORED:\n" + left)
