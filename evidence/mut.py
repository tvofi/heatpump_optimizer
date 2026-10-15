#!/usr/bin/env python3
"""Reviewer mutants for R10-DEEPLINK: apply, run tests/card.mjs, print FAIL lines, restore."""
import os, subprocess, sys

WT = sys.argv[1]
CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
TEST = "tests/card.mjs"

def sub(path, old, new, count=1):
    p = os.path.join(WT, path)
    s = open(p).read()
    n = s.count(old)
    if n < 1:
        raise SystemExit(f"MUTANT-APPLY-FAILED {path}: {old[:60]!r} found {n}")
    open(p, "w").write(s.replace(old, new, count))

MUTANTS = {
    "M1": [(CARD, '`${SETTINGS_PATH}#${q("config_entry", entryId)}`', 'SETTINGS_PATH')],
    "M2": [(CARD, '&${q("more-info-view", "settings")}`', '`')],
    "M3": [(TEST, '    "advisor:settings": "R10-ADVISOR",\n', '')],
    "M4": [(CARD, "// ---- The Health page (R9-UX-3)",
            'function unreachedLink(host) { openHaLink(host, "entities"); }\n\n// ---- The Health page (R9-UX-3)')],
    "M5": [(CARD, "this.pickerFocus = !!viaKeyboard;", "this.pickerFocus = false;")],
    "M6": [(CARD, '} else if (act === "settings" || act === "diagnostics") {\n        navigateTo(SETTINGS_PATH);',
            '} else if (act === "settings") {\n        await openHaLink(host, "options");\n        return;\n      } else if (act === "diagnostics") {\n        navigateTo(SETTINGS_PATH);')],
    # Reviewer-planted attacks (brief step 6)
    "R1_bypass": [(CARD, 'openSetupSlot(host, btn.dataset.key, ev);\n        return;',
                   'navigateTo("/config/entities?domain=heatpump_optimizer");\n        return;')],
    "R1b_bypass_samestring": [(CARD, 'openSetupSlot(host, btn.dataset.key, ev);\n        return;',
                   'try { const reg = await host.hass.callWS({ type: "config/entity_registry/get", entity_id: host.plan.resolveEntity("space") });\n        navigateTo(`/config/entities?config_entry=${reg.config_entry_id}`); } catch (_e) {}\n        return;')],
    "R1c_bypass_location": [(CARD, 'openSetupSlot(host, btn.dataset.key, ev);\n        return;',
                   'try { globalThis.location.assign("/config/entities"); } catch (_e) {}\n        return;')],
    "R1d_bypass_wrongentry": [(CARD, 'openSetupSlot(host, btn.dataset.key, ev);\n        return;',
                   'navigateTo("/config/entities?config_entry=SOMEOTHER");\n        return;')],
    "R2_stale": [(TEST, '    "health:diagnostics": "R10-UX-HEALTH",\n',
                  '    "health:diagnostics": "R10-UX-HEALTH",\n    "setup:configure": "R10-UX-SETUP",\n')],
    "R3_openSetupSlot_render": [(CARD, "  host.dialog.scroll = 0;\n  host._render();\n}\n\n/** The inbox's actions",
                                 "  host.dialog.scroll = 0;\n}\n\n/** The inbox's actions")],
    "R5_anchor_href": [(CARD, 'data-act="diagnostics">${esc(L("health.act_diagnostics"))}</button></div>',
                        'data-act="diagnostics">${esc(L("health.act_diagnostics"))}</button><a href="/config/integrations/integration/heatpump_optimizer">open</a></div>')],
    "R6_more_info_event": [(CARD, 'openSetupSlot(host, btn.dataset.key, ev);\n        return;',
                   'host.dispatchEvent(new CustomEvent("hass-more-info", { detail: { entityId: "sensor.x" }, bubbles: true, composed: true }));\n        return;')],
    "R4_entry_ignored":[(CARD, "entryId = (reg && reg.config_entry_id) || null;", "entryId = null;")],
}

which = sys.argv[2:] or list(MUTANTS)
for name in which:
    for path, old, new in MUTANTS[name]:
        sub(path, old, new)
    r = subprocess.run(["node", TEST], cwd=WT, capture_output=True, text=True)
    out = r.stdout + r.stderr
    fails = [l.strip() for l in out.splitlines() if l.lstrip().startswith("FAIL")]
    subprocess.run(["git", "checkout", "--", CARD, TEST], cwd=WT, check=True)
    print(f"RESULT mutant={name} rc={r.returncode} fails={len(fails)}")
    for f in fails:
        print(f"    {f[:300]}")
    if r.returncode and not fails:
        print("    tail:", out.strip().splitlines()[-3:])
st = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=WT, capture_output=True, text=True).stdout
print("RESTORED-CLEAN" if not st.strip() else f"DIRTY:\n{st}")
