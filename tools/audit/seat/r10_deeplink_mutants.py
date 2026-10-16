#!/usr/bin/env python3
"""R10-DEEPLINK (#2253, #2283): every plant the census in tests/card.mjs must refuse.

Metric, one line per plant: `RESULT mutant=<name> rc=<rc> fails=<n>`, then the
failing check names. Each plant is a set of exact one-occurrence replacements
in the card (or, for M3, in tests/card.mjs); the driver applies one plant, runs
`node tests/card.mjs`, restores the file byte for byte, and refuses to start on
a dirty tree. Expected: every plant rc=1 with fails>=1 -- a FAIL line, not a
crash; a plant that kills only by crashing the run prints its tail.

Plants:
  M1-M6    the fixer's round-1 mutants (haLink routes, PENDING, reach, focus,
           stale row).
  R4-R7d   the review's round-1 to round-3 plants and the fixer's variants
           (registry lookup ignored, anchor, hass-more-info, setAttribute).
  N1-N5,   the round-3 review's mut3.py, verbatim: replaceState, open and
  H1-H10   location navigations, in and out of try; href in eight spellings,
           on a selector the stub resolves (".zz") and one it cannot ("a.zz").

    python3 tools/audit/seat/r10_deeplink_mutants.py [plant ...]

Run from the worktree root after `PYTHONPATH=tests/hastub python3
tests/plan_view.py` (card.mjs reads its payload). Null control: run with no
plant applied (`--null`), which must print rc=0 fails=0.
"""
import subprocess
import sys

CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
TEST = "tests/card.mjs"
P = "/config/integrations/integration/heatpump_optimizer"
NAV = '        navigateTo(SETTINGS_PATH);\n        return;\n      } else if (act === "apply_valve")'
DIAG = '<button type="button" class="adv-act" data-act="diagnostics">'
LOOP = '  for (const btn of root.querySelectorAll(".adv-act")) {\n    btn.addEventListener("click", async (ev) => {'
DISMISS = "        dismissFeedback();\n        host._render();\n        return;"
STOP = "      stop(ev);\n      const act = btn.dataset.act;"
EVENT = 'host.dispatchEvent(new CustomEvent(%s, { detail: { entityId: "sensor.x" }, bubbles: true, composed: true }));'
RUNTIME_MORE_INFO = '["hass", "more", "info"].join("-")'


def after_nav(stmt):
    return [(CARD, NAV, NAV.replace("navigateTo(SETTINGS_PATH);", "navigateTo(SETTINGS_PATH); " + stmt))]


def attach(sel, stmt):
    return [(CARD, DIAG, '<a class="zz"></a>' + DIAG),
            (CARD, LOOP, f'  for (const a of root.querySelectorAll("{sel}")) {stmt}\n' + LOOP)]


def card(old, new):
    return [(CARD, old, new)]


PLANTS = {
    # Round 1 (fixer).
    "M1_options_drops_entry": card('`${SETTINGS_PATH}#${q("config_entry", entryId)}`', "SETTINGS_PATH"),
    "M2_entity_drops_settings_view": card('}&${q("more-info-view", "settings")}`', "}`"),
    "M3_delete_advisor_pending_row": [(TEST, '    "advisor:settings": { group: "R10-ADVISOR", path: BARE },\n', "")],
    "M4_unreached_link_site": card("function healthPageHtml(host) {",
                                   'function unreachedLink(host) { openHaLink(host, "entities"); }\n\nfunction healthPageHtml(host) {'),
    "M5_openPicker_no_focus": card("    this.pickerFocus = !!viaKeyboard;", "    this.pickerFocus = false;"),
    "M6_convert_advisor_settings": card("        navigateTo(SETTINGS_PATH);", '        await openHaLink(host, "options");'),
    # Rounds 1-3 (review) and the fixer's variants.
    "R4_entry_ignored": card("    entryId = (reg && reg.config_entry_id) || null;", "    entryId = null;"),
    "R5_anchor_href": card(DIAG, f'<a href="{P}">open</a>' + DIAG),
    "R6_more_info_instead_of_nav": card("        navigateTo(SETTINGS_PATH);", "        " + EVENT % '"hass-more-info"'),
    "R6b_pending_nav_plus_event": card("        navigateTo(SETTINGS_PATH);",
                                       "        navigateTo(SETTINGS_PATH); " + EVENT % RUNTIME_MORE_INFO),
    "R6c_assign_fires_event": card("        openSetupSlot(host, btn.dataset.key, ev);", "        " + EVENT % RUNTIME_MORE_INFO),
    "R7b_setAttribute_unresolved": attach("a.zz", f'a.setAttribute("href", "{P}");'),
    "R7c_setAttribute_runtime_name": attach(".zz", f'a.setAttribute(["hr", "ef"].join(""), "{P}");'),
    "R7d_setAttribute_at_click": [(CARD, DIAG, '<a class="zz"></a>' + DIAG),
                                  (CARD, STOP, STOP.replace("stop(ev);", 'stop(ev);\n      for (const a of root.querySelectorAll(".zz")) a.setAttribute(["hr", "ef"].join(""), "%s");' % P))],
    # Round 3 (review, mut3.py verbatim).
    "N1_replaceState_after_pending_push": after_nav('globalThis.history.replaceState(null, "", "/config/entities"); globalThis.dispatchEvent(new CustomEvent("location-changed"));'),
    "N2_replaceState_on_dismiss": card(DISMISS, '        globalThis.history.replaceState(null, "", "/config/entities");\n        globalThis.dispatchEvent(new CustomEvent("location-changed"));\n        return;'),
    "N3_globalThis_open": after_nav('globalThis.open("/config/entities", "_self");'),
    "N4_location_assign_bare": after_nav('globalThis.location = "/config/entities";'),
    "N5_open_on_dismiss": card(DISMISS, '        globalThis.open("/config/entities", "_self");\n        return;'),
    "N1t_replaceState_in_try": after_nav('try { globalThis.history.replaceState(null, "", "/config/entities"); globalThis.dispatchEvent(new CustomEvent("location-changed")); } catch (_e) { /* no router */ }'),
    "N3t_globalThis_open_in_try": after_nav('try { globalThis.open("/config/entities", "_self"); } catch (_e) { /* no window */ }'),
    "H9t_innerHTML_template_in_try": card(LOOP, '  try { const u = "%s"; const d = root.querySelector(".adv-act"); if (d) d.insertAdjacentHTML("afterend", `<a href=${u}>x</a>`); } catch (_e) {}\n' % P + LOOP),
    "H1_setAttribute_backtick_rendered": attach(".zz", 'a.setAttribute(`href`, "%s");' % P),
    "H2_setAttribute_backtick_unrendered": attach("a.zz", 'a.setAttribute(`href`, "%s");' % P),
    "H3_Reflect_set_rendered": attach(".zz", 'Reflect.set(a, "href", "%s");' % P),
    "H4_Reflect_set_unrendered": attach("a.zz", 'Reflect.set(a, "href", "%s");' % P),
    "H5_Object_assign_unrendered": attach("a.zz", 'Object.assign(a, { href: "%s" });' % P),
    "H6_bracket_unrendered": attach("a.zz", 'a["href"] = "%s";' % P),
    "H7_attributes_setNamedItem": attach("a.zz", '{ const at = document.createAttribute("href"); at.value = "%s"; a.attributes.setNamedItem(at); }' % P),
    "H8_innerHTML_anchor_single_quote": card(LOOP, "  { const d = root.querySelector('.setup-result'); if (d) d.innerHTML = \"<a href='%s'>x</a>\"; }\n" % P + LOOP),
    "H9_innerHTML_template": card(LOOP, '  { const u = "%s"; const d = root.querySelector(".adv-act"); if (d) d.insertAdjacentHTML("afterend", `<a href=${u}>x</a>`); }\n' % P + LOOP),
    "H10_setAttribute_literal_rendered": attach(".zz", 'a.setAttribute("href", "%s");' % P),
}


def run(name, edits):
    orig = {f: open(f).read() for f in {e[0] for e in edits}}
    try:
        for f, old, new in edits:
            s = open(f).read()
            if s.count(old) != 1:
                print(f"RESULT mutant={name} rc=ERR fails=0\n    anchor not unique in {f}: {old[:60]!r}")
                return
            open(f, "w").write(s.replace(old, new))
        r = subprocess.run(["node", TEST], capture_output=True, text=True, timeout=1800)
        lines = (r.stdout + r.stderr).splitlines()
        fails = [i for i, l in enumerate(lines) if l.startswith("  FAIL")]
        print(f"RESULT mutant={name} rc={r.returncode} fails={len(fails)}")
        for i in fails:
            print("    " + lines[i].strip()[:200])
            if i + 1 < len(lines):
                print("      " + lines[i + 1].strip()[:200])
        if r.returncode and not fails:
            for l in lines[-4:]:
                print("    tail: " + l[:200])
    finally:
        for f, s in orig.items():
            open(f, "w").write(s)
    sys.stdout.flush()


def main():
    if subprocess.run(["git", "status", "--short", "--", CARD, TEST], capture_output=True, text=True).stdout.strip():
        sys.exit("refusing: the card or tests/card.mjs is modified")
    args = sys.argv[1:]
    if args == ["--null"]:
        run("NULL_no_plant", [])
        return
    for name in args or list(PLANTS):
        run(name, PLANTS[name])
    left = subprocess.run(["git", "status", "--short", "--", CARD, TEST], capture_output=True, text=True).stdout
    print("restored" if not left.strip() else "NOT RESTORED:\n" + left)


if __name__ == "__main__":
    main()
