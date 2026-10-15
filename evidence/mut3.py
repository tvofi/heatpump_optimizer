#!/usr/bin/env python3
"""Round-3 reviewer plants for #2283. Usage: mut3.py <worktree>. One plant at a time; restores after each."""
import subprocess, sys, os
wt = sys.argv[1]; os.chdir(wt)
F = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
orig = open(F).read()
NAV = "        navigateTo(SETTINGS_PATH);\n        return;\n      } else if (act === \"apply_valve\")"
DIAG = '<button type="button" class="adv-act" data-act="diagnostics">'
LOOP = '  for (const btn of root.querySelectorAll(".adv-act")) {\n    btn.addEventListener("click", async (ev) => {'
DISMISS = "        dismissFeedback();\n        host._render();\n        return;"
P = "/config/integrations/integration/heatpump_optimizer"
def after_nav(stmt):
    return [(NAV, NAV.replace("navigateTo(SETTINGS_PATH);", "navigateTo(SETTINGS_PATH); " + stmt))]
def attach(sel, stmt):
    return [(DIAG, '<a class="zz"></a>' + DIAG), (LOOP, f'  for (const a of root.querySelectorAll("{sel}")) {stmt}\n' + LOOP)]
plants = {
  # history/navigation primitives the static regex does not name
  "N1_replaceState_after_pending_push": after_nav('globalThis.history.replaceState(null, "", "/config/entities"); globalThis.dispatchEvent(new CustomEvent("location-changed"));'),
  "N2_replaceState_on_dismiss": [(DISMISS, '        globalThis.history.replaceState(null, "", "/config/entities");\n        globalThis.dispatchEvent(new CustomEvent("location-changed"));\n        return;')],
  "N3_globalThis_open": after_nav('globalThis.open("/config/entities", "_self");'),
  "N4_location_assign_bare": after_nav('globalThis.location = "/config/entities";'),
  "N5_open_on_dismiss": [(DISMISS, '        globalThis.open("/config/entities", "_self");\n        return;')],
  "N1t_replaceState_in_try_after_pending_push": after_nav('try { globalThis.history.replaceState(null, "", "/config/entities"); globalThis.dispatchEvent(new CustomEvent("location-changed")); } catch (_e) { /* no router */ }'),
  "N3t_globalThis_open_in_try": after_nav('try { globalThis.open("/config/entities", "_self"); } catch (_e) { /* no window */ }'),
  "H9t_innerHTML_template_in_try": [(LOOP, '  try { const u = "%s"; const d = root.querySelector(".adv-act"); if (d) d.insertAdjacentHTML("afterend", `<a href=${u}>x</a>`); } catch (_e) {}\n' % P + LOOP)],
  # href spellings
  "H1_setAttribute_backtick_rendered": attach(".zz", 'a.setAttribute(`href`, "%s");' % P),
  "H2_setAttribute_backtick_unrendered": attach("a.zz", 'a.setAttribute(`href`, "%s");' % P),
  "H3_Reflect_set_rendered": attach(".zz", 'Reflect.set(a, "href", "%s");' % P),
  "H4_Reflect_set_unrendered": attach("a.zz", 'Reflect.set(a, "href", "%s");' % P),
  "H5_Object_assign_unrendered": attach("a.zz", 'Object.assign(a, { href: "%s" });' % P),
  "H6_bracket_unrendered": attach("a.zz", 'a["href"] = "%s";' % P),
  "H7_attributes_setNamedItem": attach("a.zz", '{ const at = document.createAttribute("href"); at.value = "%s"; a.attributes.setNamedItem(at); }' % P),
  "H8_innerHTML_anchor_single_quote": [(LOOP, "  { const d = root.querySelector('.setup-result'); if (d) d.innerHTML = \"<a href='%s'>x</a>\"; }\n" % P + LOOP)],
  "H9_innerHTML_template": [(LOOP, '  { const u = "%s"; const d = root.querySelector(".adv-act"); if (d) d.insertAdjacentHTML("afterend", `<a href=${u}>x</a>`); }\n' % P + LOOP)],
  "H10_setAttribute_literal_rendered_R7b_ctrl": attach(".zz", 'a.setAttribute("href", "%s");' % P),
}
only = sys.argv[2:] or list(plants)
for name in only:
    s = orig
    for old, new in plants[name]:
        assert s.count(old) == 1, (name, old[:60])
        s = s.replace(old, new)
    open(F, "w").write(s)
    try:
        r = subprocess.run(["node", "tests/card.mjs"], capture_output=True, text=True, timeout=900)
        out = r.stdout + r.stderr
        fails = [l.strip() for l in out.splitlines() if l.startswith("  FAIL") or l.startswith("FAIL")]
        print(f"RESULT mutant={name} rc={r.returncode} fails={len(fails)}")
        for l in fails: print("    " + l[:220])
        if r.returncode and not fails:
            for l in out.splitlines()[-6:]: print("    tail: " + l[:220])
        # the line after each FAIL is the detail
        lines = out.splitlines()
        for i, l in enumerate(lines):
            if l.startswith("  FAIL") and i + 1 < len(lines): print("      " + lines[i+1].strip()[:220])
    finally:
        open(F, "w").write(orig)
    sys.stdout.flush()
assert open(F).read() == orig
print("restored", subprocess.run(["git", "status", "--short"], capture_output=True, text=True).stdout or "clean")
