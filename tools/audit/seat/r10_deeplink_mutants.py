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
  K*       the round-4 review's mut4.py (#2317), and this fix's isolating
           variants of them: a bare open() on a row nothing rendered, the
           Navigation API under three spellings, a form's action, and an
           Event-built more-info. K5r and K3c are the review's own controls:
           red before this fix, on the spellings its denylist held.
  W*       two seams this fix found for itself: a global the census cannot see
           the use of, read behind a feature test, and the history object's own
           back step behind a name built at run time.
  Z2, Z3   the round-5 review's two written spellings in the chart's undriven
           keydown handler -- an indirect open (`globalThis.open.call(...)`)
           and `navigateTo ("...")` with a space before the paren -- plus the
           other written invocation forms the name rules must catch (`.apply`,
           a computed key, `Reflect.apply`, `.call` on the reach side, a
           newline before the paren). Z3c is the control: the standard spelling
           in the same position is red on reach.
  V1-V13   the round-7 review's written programmatic form (#2345) and this
           fix's isolating variants of it: createElement("form") (V2, and V13
           with the tag's upper case), the action written through setAttribute
           (V3), createAttribute (V9), setAttributeNS (V12), Reflect.set (V7),
           Object.assign (V8) and a computed key (V11), and a submit by name
           (V4), computed key (V5), requestSubmit (V6) and indirect .call
           (V10). V1 is the review's plant verbatim. Each is wrapped in the
           try its own handler has, so a stub missing `submit` cannot kill it
           by a crash -- a crash is rc=1 with no FAIL line, i.e. no census arm
           ran.
  T1c,T2c  a press that throws, or rejects, only inside the census (the card
           detects the census's one-parameter open).
  Y1       the residual's witness, expected GREEN: a run-time name written
           through a selector the stub DOM cannot resolve (see the census's
           Residual paragraph).
  F1-F4    the CONTROLS that must stay GREEN (rc=0 fails=0): the same words as
           values or as a key on a legitimate object (`sensor === "action"`
           inside a setAttribute value, `key === "action"` inside an
           Object.assign value, `{ action: "off" }`), and an identifier that
           begins with `submit`. They are what shows the new rows key on the
           name position rather than the word.
  X*       this fix's own lines, each mutated where a plant it closes sits
           beside it (X1K5b, X3K2b, X4K3t, X5W1, X6Z, X6Z2, X9Z3, X10V2,
           X10V13, X11V3, X11V9, X11V12, X12V7, X12V8, X12V11, X13V4, X13V5,
           X13V6, X13V10): if the
           mutant alone leaves the plant green, the plant's catch DEPENDS on
           that line, and a fix line whose removal changes no check is a line
           this census does not need. X1 and X2 alone are red: each makes
           the line's own check fire on an otherwise unmodified card. Every
           other X alone (X3-X13) reads rc=0 fails=0 -- with the line gone the
           card holds nothing for it to refuse -- and is read paired with the
           plant beside it, which then goes green. X7K1b is red on `no press
           throws`: without the surface member the plant's navigate call
           throws inside the census, and the member is what records it as a
           navigation instead.
  RV1-RV7  the round-8 review's written spellings in the undriven keydown
           handler, expected GREEN (rc=0 fails=0): the residual's witnesses
           (the census's Residual paragraph). RV1c and RV5c are their controls,
           the spellings the rows do name, expected red. They are the control
           R10-DEEPLINK-HANDLERS starts from: each goes red when the dynamic
           arm drives that handler.

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


def kd(stmt):
    """One statement at the head of the chart's keydown handler, which no census press reaches."""
    return card(KEYDOWN, "      " + stmt + "\n" + KEYDOWN)


def test(old, new):
    return [(TEST, old, new)]


# The four nav-less spellings the round-4 review planted, and this fix's
# isolating variants of them.
K5 = card(DISMISS, '        open("/config/entities", "_self");\n' + DISMISS)
K5B = card(DISMISS, '        globalThis["open"]("/config/entities", "_self");\n' + DISMISS)
K1B = after_nav('globalThis[["navi", "gation"].join("")].navigate("/config/entities");')
K2B = after_nav('{ const f = document.createElement("form"); f.setAttribute("action", "%s"); root.appendChild(f); }' % P)
K3T = after_nav('try { const ev = new Event(%s, { bubbles: true, composed: true }); ev.detail = { entityId: "sensor.x" }; globalThis.dispatchEvent(ev); } catch (_e) { /* no router */ }' % RUNTIME_MORE_INFO)
KEYDOWN = '      const wantsRemove = key === "Delete" || key === "Backspace";'
Z_KEYDOWN = card(KEYDOWN, '      open("/config/entities", "_self");\n' + KEYDOWN)
# The round-5 review's two written spellings that passed both arms in that same
# unreached handler: an indirect `open` (`open.call(` names the member without
# matching a `open(` token) and `navigateTo` split from its `(` by a space. Z3c
# is the control: the standard spelling in the same position is red on reach,
# so the space alone is what hid the call.
Z2_KEYDOWN_OPEN_CALL = card(
    KEYDOWN, '      globalThis.open.call(globalThis, "/config/entities", "_self");\n' + KEYDOWN)
# The other written ways to invoke the member by name, so the round closes the
# CLASS the review's spelling belongs to rather than that one spelling: an
# `.apply`, a computed string key, a function value handed to `Reflect.apply`,
# and the same on the reach side. Each must be refused by the census's name
# rules in that unreached handler.
Z2B_KEYDOWN_OPEN_APPLY = card(
    KEYDOWN, '      globalThis.open.apply(globalThis, ["/config/entities", "_self"]);\n' + KEYDOWN)
Z2C_KEYDOWN_OPEN_BRACKET = card(
    KEYDOWN, '      globalThis["open"]("/config/entities", "_self");\n' + KEYDOWN)
Z2D_KEYDOWN_OPEN_REFLECT = card(
    KEYDOWN, '      Reflect.apply(globalThis.open, globalThis, ["/config/entities", "_self"]);\n' + KEYDOWN)
Z3_KEYDOWN_NAV_SPACE = card(KEYDOWN, '      navigateTo ("/config/entities");\n' + KEYDOWN)
Z3B_KEYDOWN_NAV_CALL = card(KEYDOWN, '      navigateTo.call(globalThis, "/config/entities");\n' + KEYDOWN)
Z3D_KEYDOWN_NAV_NEWLINE = card(KEYDOWN, '      navigateTo\n        ("/config/entities");\n' + KEYDOWN)
Z3C_KEYDOWN_NAV_SPACE_CONTROL = card(KEYDOWN, '      navigateTo("/config/entities");\n' + KEYDOWN)
# The round-7 review's plant (#2345): a form built, given an action and
# submitted entirely by name, in that same undriven keydown handler. The
# written `"form"` and `"action"` strings matched neither markup row
# (`/<form\b/`, `action\s*=`) and `submit` was on no list, so it passed both
# arms. V2-V10 isolate each written spelling the class admits -- creating the
# form by name, writing its action through an attribute, a member, a
# computed key or a setter, and submitting it by name directly, indirectly or
# through a computed key -- so the surface closes the CLASS rather than this
# one plant. Every one is a written spelling; a name BUILT at run time stays
# the residual the census states.
V1_KEYDOWN_PROGRAMMATIC_FORM = card(
    KEYDOWN, '      { try { const f = document.createElement("form"); f.setAttribute("action", "%s"); document.body.appendChild(f); f.submit(); } catch (_e) {} }\n' % P + KEYDOWN)
V2_KEYDOWN_CREATE_FORM = card(
    KEYDOWN, '      try { const f = document.createElement("form"); root.appendChild(f); } catch (_e) {}\n' + KEYDOWN)
V3_KEYDOWN_SET_ATTRIBUTE_ACTION = card(
    KEYDOWN, '      try { const f = document.createElement("div"); f.setAttribute("action", "%s"); root.appendChild(f); } catch (_e) {}\n' % P + KEYDOWN)
V4_KEYDOWN_SUBMIT = card(
    KEYDOWN, '      try { const f = document.createElement("div"); root.appendChild(f); f.submit(); } catch (_e) {}\n' + KEYDOWN)
V5_KEYDOWN_SUBMIT_BRACKET = card(
    KEYDOWN, '      try { const f = document.createElement("div"); root.appendChild(f); f["submit"](); } catch (_e) {}\n' + KEYDOWN)
V6_KEYDOWN_REQUEST_SUBMIT = card(
    KEYDOWN, '      try { const f = document.createElement("div"); root.appendChild(f); f.requestSubmit(); } catch (_e) {}\n' + KEYDOWN)
V7_KEYDOWN_REFLECT_ACTION = card(
    KEYDOWN, '      try { const f = document.createElement("div"); Reflect.set(f, "action", "%s"); } catch (_e) {}\n' % P + KEYDOWN)
V8_KEYDOWN_OBJECT_ASSIGN_ACTION = card(
    KEYDOWN, '      try { const f = document.createElement("div"); Object.assign(f, { action: "%s" }); } catch (_e) {}\n' % P + KEYDOWN)
V9_KEYDOWN_CREATE_ATTRIBUTE_ACTION = card(
    KEYDOWN, '      try { const f = document.createElement("div"); const at = document.createAttribute("action"); at.value = "%s"; } catch (_e) {}\n' % P + KEYDOWN)
V10_KEYDOWN_SUBMIT_CALL = card(
    KEYDOWN, '      try { const f = document.createElement("div"); root.appendChild(f); f.submit.call(f); } catch (_e) {}\n' + KEYDOWN)
V11_KEYDOWN_BRACKET_ACTION = card(
    KEYDOWN, '      try { const f = document.createElement("div"); f["action"] = "%s"; } catch (_e) {}\n' % P + KEYDOWN)
V12_KEYDOWN_SET_ATTRIBUTE_NS_ACTION = card(
    KEYDOWN, '      try { const f = document.createElement("div"); f.setAttributeNS("http://www.w3.org/1999/xhtml", "action", "%s"); } catch (_e) {}\n' % P + KEYDOWN)
V13_KEYDOWN_CREATE_FORM_UPPER = card(
    KEYDOWN, '      try { const f = document.createElement("FORM"); root.appendChild(f); } catch (_e) {}\n' + KEYDOWN)
# The CONTROLS: legitimate card code that writes the same WORDS as values or
# keys, which the new rows must leave green. The action rows key on a call's
# name position, so a value that merely equals `"action"` is not a name; the
# submit row keys on a member, so an identifier that begins with `submit` is
# not one. Expected rc=0 fails=0 -- the opposite verdict from every other
# plant in this file, and the reason the rows are anchored.
F1_KEYDOWN_ACTION_AS_A_VALUE = card(
    KEYDOWN, '      try { const d = document.createElement("div"); d.setAttribute("aria-label", sensor === "action" ? "a" : "b"); } catch (_e) {}\n' + KEYDOWN)
# F2 compares the handler's own `key`, not `act`: `act === "x"` is the act-
# branch syntax the reach check reads, so a control written on `act` declares
# an act branch and is red on reach, not on the form rows it controls.
F2_KEYDOWN_ACTION_AS_AN_OBJECT_VALUE = card(
    KEYDOWN, '      try { const f = document.createElement("div"); Object.assign(f, { label: key === "action" ? "a" : "b" }); } catch (_e) {}\n' + KEYDOWN)
F3_KEYDOWN_ACTION_AS_AN_OBJECT_KEY = card(
    KEYDOWN, '      try { const cur = { action: "off" }; } catch (_e) {}\n' + KEYDOWN)
F4_KEYDOWN_SUBMIT_AS_AN_IDENTIFIER = card(
    KEYDOWN, '      try { const submission = { submitted: true }; } catch (_e) {}\n' + KEYDOWN)
# The two seams this fix found for itself.
W1 = after_nav('if (globalThis.frames) globalThis.dispatchEvent(new Event("nothing-to-see"));')
W2 = after_nav('globalThis[["hist", "ory"].join("")].go(-1);')
# The scan's grammar, ECMAScript's IdentifierName production: under the ASCII
# word grammar the source split `främes` at the `ä`, so the name was never
# watched and the read of the global went unrecorded and unrefused.
W3 = after_nav('if (globalThis.främes) globalThis.dispatchEvent(new Event("nothing-to-see"));')
X8 = test(r'  const IDENT = /[$_\p{ID_Start}][$\u200C\u200D\p{ID_Continue}]*/gu;',
          r'  const IDENT = /[A-Za-z_$][\w$]*/g;')
X1 = test('    s[`${ADVISOR_PFX}_sensor_gap_advisor`].attributes.feedback_gaps =\n'
          '      [{ class: "power", key: "heat_pump_power_entity" }];\n', "")
X3 = test('  for (const at of ["href", "action", "formaction"]) {', '  for (const at of ["href"]) {')
X4 = test('    if (typeof type === "string" && !EVENT_TYPES.has(type)) {', '    if (false) {')
X5 = test('      unknown.add(name);\n      return uninstrumented(name);', '      return undefined;')
X6 = test('  { what: "the open member, named", re: /\\bopen\\b/, exact: true },',
          '  { what: "the open member, named", re: /(?!)open/, exact: true },')
# The reach rule enumerates every mention of a link function; the pre-fix form
# enumerated the `name(` call-site spelling, which a space before the paren
# escaped. X9 is that old enumeration, so Z3 must go green under it.
X9 = test('  const LINK_NAME = /\\b(navigateTo|openHaLink)\\b/;',
          '  const LINK_NAME = /\\b(navigateTo|openHaLink)\\(/;')
# The round-7 fix's four new surface rows, one mutant each: X10 the form
# created by name, X11 its action written through an attribute, X12 its action
# written through a member or a computed key, X13 a submit by name. Each is
# run alone (green: it moves no check by itself) and paired with every plant
# its row is the only closure of -- if the pair is green, the row is what
# closes that plant.
X10 = test(r'''  { what: "a form created by name", re: /\bcreateElement\s*\(\s*["'`]form["'`]/ },
''', "")
X11 = test(r'''  { what: "a form's action written through an attribute",
    re: /(?:\bsetAttribute\s*\(\s*["'`]action["'`]|\bsetAttributeNS\s*\([^,]*,\s*["'`]action["'`]|\bcreateAttribute\s*\(\s*["'`]action["'`])/ },
''', "")
X12 = test(r'''  { what: "a form's action written through a member",
    re: /(?:\bReflect\.set\s*\([^,]*,\s*["'`]action["'`]|\bObject\.assign\s*\([^,]*,\s*\{[^}]*\baction\s*:|\[\s*["'`]action["'`]\s*\]\s*=)/ },
''', "")
X13 = test(r'''  { what: "a form submitted by name",
    re: /(?:\.\s*(?:submit|requestSubmit)\b|\[\s*["'`](?:submit|requestSubmit)["'`]\s*\])/ },
''', "")
X7 = test('  sink.navigation.navigate = (u) => { left.push(["navigation", String(u)]); return null; };',
          '  sink.navigation.navigate = undefined;')


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
    # Round 4 (the review's mut4.py, #2317) and this fix's isolating variants.
    "K5_bare_open_on_dismiss": K5,
    "K5b_bracket_open_on_dismiss": K5B,
    "K5c_open_call_on_dismiss": card(DISMISS, '        globalThis.open.call(globalThis, "/config/entities", "_self");\n' + DISMISS),
    "K5r_bare_open_rendered_control": after_nav('open("/config/entities", "_self");'),
    "K1_navigation_api_in_try": after_nav('try { globalThis.navigation.navigate("/config/entities"); } catch (_e) { /* no router */ }'),
    "K1c_navigation_api_no_try": after_nav('globalThis.navigation.navigate("/config/entities");'),
    "K1b_navigation_name_built": K1B,
    "K2_form_action_rendered": card(DIAG, '<form action="/config/entities"><button type="submit">go</button></form>' + DIAG),
    "K2b_action_set_at_run_time": K2B,
    "K3t_event_runtime_more_info": K3T,
    "K3c_event_literal_more_info_control": after_nav('globalThis.dispatchEvent(new Event("hass-more-info"));'),
    "Z_open_in_undriven_keydown": Z_KEYDOWN,
    "Z2_open_call_in_undriven_keydown": Z2_KEYDOWN_OPEN_CALL,
    "Z2b_open_apply_in_undriven_keydown": Z2B_KEYDOWN_OPEN_APPLY,
    "Z2c_open_bracket_in_undriven_keydown": Z2C_KEYDOWN_OPEN_BRACKET,
    "Z2d_open_reflect_in_undriven_keydown": Z2D_KEYDOWN_OPEN_REFLECT,
    "Z3_navigate_to_space_in_undriven_keydown": Z3_KEYDOWN_NAV_SPACE,
    "Z3b_navigate_to_call_in_undriven_keydown": Z3B_KEYDOWN_NAV_CALL,
    "Z3d_navigate_to_newline_in_undriven_keydown": Z3D_KEYDOWN_NAV_NEWLINE,
    "Z3c_navigate_to_standard_in_undriven_keydown_control": Z3C_KEYDOWN_NAV_SPACE_CONTROL,
    "V1_programmatic_form_in_undriven_keydown": V1_KEYDOWN_PROGRAMMATIC_FORM,
    "V2_create_element_form_in_undriven_keydown": V2_KEYDOWN_CREATE_FORM,
    "V3_set_attribute_action_in_undriven_keydown": V3_KEYDOWN_SET_ATTRIBUTE_ACTION,
    "V4_submit_in_undriven_keydown": V4_KEYDOWN_SUBMIT,
    "V5_submit_bracket_in_undriven_keydown": V5_KEYDOWN_SUBMIT_BRACKET,
    "V6_request_submit_in_undriven_keydown": V6_KEYDOWN_REQUEST_SUBMIT,
    "V7_reflect_set_action_in_undriven_keydown": V7_KEYDOWN_REFLECT_ACTION,
    "V8_object_assign_action_in_undriven_keydown": V8_KEYDOWN_OBJECT_ASSIGN_ACTION,
    "V9_create_attribute_action_in_undriven_keydown": V9_KEYDOWN_CREATE_ATTRIBUTE_ACTION,
    "V10_submit_call_in_undriven_keydown": V10_KEYDOWN_SUBMIT_CALL,
    "V11_bracket_action_in_undriven_keydown": V11_KEYDOWN_BRACKET_ACTION,
    "V12_set_attribute_ns_action_in_undriven_keydown": V12_KEYDOWN_SET_ATTRIBUTE_NS_ACTION,
    "V13_create_element_form_upper_in_undriven_keydown": V13_KEYDOWN_CREATE_FORM_UPPER,
    "F1_action_as_a_setattribute_value_control": F1_KEYDOWN_ACTION_AS_A_VALUE,
    "F2_action_as_an_object_assign_value_control": F2_KEYDOWN_ACTION_AS_AN_OBJECT_VALUE,
    "F3_action_as_an_object_key_control": F3_KEYDOWN_ACTION_AS_AN_OBJECT_KEY,
    "F4_submit_as_an_identifier_prefix_control": F4_KEYDOWN_SUBMIT_AS_AN_IDENTIFIER,
    # A press that throws, or rejects, only inside the census: the card can
    # tell the census's open (one parameter) from the rig's, so a check keyed
    # on the rig alone would never see the failure. Ported from the
    # 2026-10-16 snapshot of this group's first design (a3b1c00e2), whose
    # census's CustomEvent subclass the R10-DEEPLINK round-4 plants had keyed.
    "T1c_census_only_throw_on_press": after_nav('if (globalThis.open.length === 1) throw new Error("census-only boom");'),
    "T2c_census_only_async_reject_on_press": after_nav(
        'if (globalThis.open.length === 1) await Promise.reject(new Error("census-only reject"));'),
    # The residual's witness, expected GREEN (rc=0 fails=0): a name built at
    # run time, written through a selector the stub DOM cannot resolve, in a
    # handler a press does reach. The write runs on no element, so the
    # dynamic arm sees nothing, and the static arm refuses only a written
    # name. R7c is the same write on a selector the stub resolves (red).
    # The round-8 review's written spellings (#2345, the reviewer's
    # review_plants.py, verbatim), expected GREEN: navigation written in the
    # undriven keydown handler in a spelling no static row names. RV1c and
    # RV5c, the spellings the rows do name in the same position, are red.
    "RV1_history_bracket_back_in_undriven_keydown": kd('try { globalThis.history["back"](); } catch (_e) {}'),
    "RV2_history_optional_back_in_undriven_keydown": kd('try { globalThis.history?.back(); } catch (_e) {}'),
    "RV3_history_destructure_in_undriven_keydown": kd('try { const { back } = globalThis.history; back.call(globalThis.history); } catch (_e) {}'),
    "RV4_form_ns_action_member_button_click_in_undriven_keydown": kd('try { const u = "%s"; const f = document.createElementNS("http://www.w3.org/1999/xhtml", "form"); f.action = u; const b = document.createElement("button"); f.appendChild(b); document.body.appendChild(f); b.click(); } catch (_e) {}' % P),
    "RV5_action_member_to_variable_in_undriven_keydown": kd('try { const u = "%s"; const f = document.createElement("div"); f.action = u; } catch (_e) {}' % P),
    "RV6_object_assign_quoted_action_key_in_undriven_keydown": kd('try { const f = document.createElement("div"); Object.assign(f, { "action": "%s" }); } catch (_e) {}' % P),
    "RV7_create_element_ns_form_in_undriven_keydown": kd('try { const f = document.createElementNS("http://www.w3.org/1999/xhtml", "form"); root.appendChild(f); } catch (_e) {}'),
    "RV1c_history_dot_back_control": kd('try { globalThis.history.back(); } catch (_e) {}'),
    "RV5c_action_member_to_literal_control": kd('try { const f = document.createElement("div"); f.action = "%s"; } catch (_e) {}' % P),
    "Y1_runtime_name_on_unresolved_selector_residual": attach("a.zz", 'a.setAttribute(["hr", "ef"].join(""), "%s");' % P),
    "W1_guarded_frames": W1,
    "W2_history_go_built": W2,
    "W3_unicode_global": W3,
    # This fix's own lines, and the plant each one closes.
    "X1_fixture_drops_feedback_row": X1,
    "X1K5b_fixture_line_is_what_closes_K5b": X1 + K5B,
    "X2_card_gains_an_act_branch": card(
        '      } else if (act === "apply_valve") {',
        '      } else if (act === "navigate_home") {\n        navigateTo(SETTINGS_PATH);\n        return;\n      } else if (act === "apply_valve") {'),
    "X3_anchors_drop_action": X3,
    "X3K2b_anchors_line_is_what_closes_K2b": X3 + K2B,
    "X4_recordEvent_disabled": X4,
    "X4K3t_recordEvent_line_is_what_closes_K3t": X4 + K3T,
    "X5_watch_swallows": X5,
    "X5W1_watch_line_is_what_closes_W1": X5 + W1,
    "X6_surface_drops_the_open_name": X6,
    "X6Z_surface_member_is_what_closes_Z": X6 + Z_KEYDOWN,
    "X6Z2_surface_member_is_what_closes_Z2": X6 + Z2_KEYDOWN_OPEN_CALL,
    "X9_reach_enumerates_call_sites_not_names": X9,
    "X9Z3_reach_line_is_what_closes_Z3": X9 + Z3_KEYDOWN_NAV_SPACE,
    "X7_sink_drops_navigation": X7,
    "X7K1b_surface_member_names_the_primitive_K1b": X7 + K1B,
    "X8_ascii_grammar": X8,
    "X8W3_grammar_line_is_what_closes_W3": X8 + W3,
    "X10_create_form_row_dropped": X10,
    "X10V2_create_form_row_is_what_closes_V2": X10 + V2_KEYDOWN_CREATE_FORM,
    "X10V13_create_form_row_is_what_closes_V13": X10 + V13_KEYDOWN_CREATE_FORM_UPPER,
    "X11_action_attribute_row_dropped": X11,
    "X11V3_action_attribute_row_is_what_closes_V3": X11 + V3_KEYDOWN_SET_ATTRIBUTE_ACTION,
    "X11V9_action_attribute_row_is_what_closes_V9": X11 + V9_KEYDOWN_CREATE_ATTRIBUTE_ACTION,
    "X11V12_action_attribute_row_is_what_closes_V12": X11 + V12_KEYDOWN_SET_ATTRIBUTE_NS_ACTION,
    "X12_action_member_row_dropped": X12,
    "X12V7_action_member_row_is_what_closes_V7": X12 + V7_KEYDOWN_REFLECT_ACTION,
    "X12V8_action_member_row_is_what_closes_V8": X12 + V8_KEYDOWN_OBJECT_ASSIGN_ACTION,
    "X12V11_action_member_row_is_what_closes_V11": X12 + V11_KEYDOWN_BRACKET_ACTION,
    "X13_submit_row_dropped": X13,
    "X13V4_submit_row_is_what_closes_V4": X13 + V4_KEYDOWN_SUBMIT,
    "X13V5_submit_row_is_what_closes_V5": X13 + V5_KEYDOWN_SUBMIT_BRACKET,
    "X13V6_submit_row_is_what_closes_V6": X13 + V6_KEYDOWN_REQUEST_SUBMIT,
    "X13V10_submit_row_is_what_closes_V10": X13 + V10_KEYDOWN_SUBMIT_CALL,
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
