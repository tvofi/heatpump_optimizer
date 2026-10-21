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
  V1-V13   the round-7 review's written programmatic form (#2345) and its
           isolating variants: createElement("form") (V2, V13 upper case), an
           action written through setAttribute (V3), createAttribute (V9),
           setAttributeNS (V12), Reflect.set (V7), Object.assign (V8) or a
           computed key (V11), and a submit by name (V4), computed key (V5),
           requestSubmit (V6) or .call (V10). Since R10-DEEPLINK-HANDLERS the
           keydown they sit in is driven, so each is the dynamic arm's except
           the submits, which the bare `submit` / `requestSubmit` names
           refuse. V9 is GREEN there: an attribute node built and attached to
           nothing names no way out, and only the retired spelling row
           refused it.
  T1c,T2c  a press that throws, or rejects, only inside the census. The card
           tells the census by the selector-list shim it alone installs: since
           round 3 the navigation surface is the same object everywhere, so
           the census's one-parameter `open` is no longer a tell.
  Y1       the residual's witness, expected GREEN: a run-time name written
           through a selector the stub DOM cannot resolve (see the census's
           Residual paragraph).
  F1-F4    the CONTROLS that must stay GREEN (rc=0 fails=0): the same words as
           values or as a key on a legitimate object, and an identifier that
           begins with `submit`.
  X*       this fix's own lines, each mutated where a plant it closes sits
           beside it: if the mutant alone leaves the plant green, the plant's
           catch DEPENDS on that line. Read each alone and paired; the body
           of the pull request that added a line records both verdicts.
  RV1-RV7  the round-8 review's written spellings in the chart's keydown
           handler, which R10-DEEPLINK-HANDLERS drives: expected RED. RV1-RV3
           and RV5-RV7 are red on the drive; RV4 is a form appended to
           document.body and submitted by a button's click(), the same shape
           as RD4, so it is red on the document-level read, not on the drive
           -- RD4's entry below states that read. RV1c and RV5c, their
           controls, stay red.
  RD4-RD6c markup appended outside the shadow root inside a driven press
           (rounds 9 and 10): RD4 a form submitted by click(), RD6 an anchor
           with a run-time-built href, click()ed -- expected RED under the
           document-level read; RD5 and RD6c, the same elements in the shadow
           root, stay red.
  RD7      a detached anchor, never appended, built href, click()ed: RED, the
           read covers every element the document made.
  RD8      the residual's stub-fidelity witness, expected GREEN: markup with a
           built name inserted through insertAdjacentHTML, which the stub does
           not implement.
  AL1,KD1, navigation reached only with every modifier held (AL1), under one
  FT1,ON1  key literal (KD1), in a handler a drive registers (FT1, the slot
           menu's Escape), and a handler wired as an `on<event>` property
           (ON1): each RED, and each green beside the X line that closes it.
  OWN1-3   the #2452 round-1 review's plants (its own_plants.py, verbatim) in
           the driven chart keydown: a head meta refresh, and the location
           object's pathname and search setters under a built name. OWN2c,
           its href control, stays red.
  L*,D*,   the class those three belong to, enumerated by the rule "every
  I*,MR*,  member, alias, interface or element through which a browser leaves
  B*,UQ*,  the page": each URL part of the location object (hash, host,
  TM*      hostname, port, protocol), its reload, a write through
           Object.assign, the location assigned whole on the global, the
           window and the document, the location reached through every alias
           of the window (top, parent, frames, window.self, defaultView), the
           history and Navigation members reached through their interface's
           prototype, the document's open / write / writeln, the refresh
           pragma as a member, as quoted markup and as unquoted markup, a base
           element's href, an area's href, single-quoted and unquoted markup
           attributes the stub's parser drops, and navigation deferred to a
           timer the handler starts. Each RED. LRc, MRc and TMc are their
           controls, GREEN: a location read, a meta that is no pragma, and a
           timer that does nothing.
  REV_*,   the round-2 review's plants (its rev_plants.py, verbatim): a
  CAP*,    reference to the surface taken when the card LOADS (REV_CAP1-4),
  TMX      deferred work five timers deep, an svg anchor's xlink:href in
           markup, and its other probes; and the captured-at-load class beyond
           them -- document.write, the element factory, CustomEvent,
           setTimeout, the registration method, the Navigation API, the
           History prototype, the location's own descriptor and a window
           alias, each taken at load (CAP5-CAP13) -- and a timer chain 80 deep
           (TMX), past the settle cap, refused as unsettled. Each RED;
           REV_CAP4c and REV_XL1c, the review's controls, stay red.

    python3 tools/audit/seat/r10_deeplink_mutants.py [plant ...]

Run from the worktree root after `PYTHONPATH=tests/hastub python3
tests/plan_view.py` (card.mjs reads its payload). Null control: run with no
plant applied (`--null`), which must print rc=0 fails=0. Each plant's node
runs with `--max-old-space-size=4096`, because the census's live set is past
node's default old space (`run()` records the measurement).
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
    KEYDOWN, '      try { const d = document.createElement("div"); d.setAttribute("aria-label", key === "action" ? "a" : "b"); } catch (_e) {}\n' + KEYDOWN)
# F1 and F2 compare the handler's own `key`: F1 once read `sensor`, a name
# not bound in that handler, which is a read of an unbound global the census
# refuses by name once the handler is driven (R10-DEEPLINK-HANDLERS). F2 also
# compares `key`, not `act`: `act === "x"` is the act-
# branch syntax the reach check reads, so a control written on `act` declares
# an act branch and is red on reach, not on the form rows it controls.
F2_KEYDOWN_ACTION_AS_AN_OBJECT_VALUE = card(
    KEYDOWN, '      try { const f = document.createElement("div"); Object.assign(f, { label: key === "action" ? "a" : "b" }); } catch (_e) {}\n' + KEYDOWN)
F3_KEYDOWN_ACTION_AS_AN_OBJECT_KEY = card(
    KEYDOWN, '      try { const cur = { action: "off" }; } catch (_e) {}\n' + KEYDOWN)
F4_KEYDOWN_SUBMIT_AS_AN_IDENTIFIER = card(
    KEYDOWN, '      try { const submission = { submitted: true }; } catch (_e) {}\n' + KEYDOWN)
# The two seams this fix found for itself.
# `frames` is bound to the window since #2452 round 2 (the window's aliases
# lead to its location), so W1 reads a browser global the rig still binds
# nothing to.
W1 = after_nav('if (globalThis.visualViewport) globalThis.dispatchEvent(new Event("nothing-to-see"));')
W2 = after_nav('globalThis[["hist", "ory"].join("")].go(-1);')
# The scan's grammar, ECMAScript's IdentifierName production: under the ASCII
# word grammar the source split `främes` at the `ä`, so the name was never
# watched and the read of the global went unrecorded and unrefused.
W3 = after_nav('if (globalThis.främes) globalThis.dispatchEvent(new Event("nothing-to-see"));')
X8 = test(r'  const IDENT = /[$_\p{ID_Start}][$\u200C\u200D\p{ID_Continue}]*/gu;',
          r'  const IDENT = /[A-Za-z_$][\w$]*/g;')
X1 = test('    s[`${ADVISOR_PFX}_sensor_gap_advisor`].attributes.feedback_gaps =\n'
          '      [{ class: "power", key: "heat_pump_power_entity" }];\n', "")
X3 = test('      for (const at of ["href", "xlink:href", "action", "formaction"]) {', '      for (const at of ["href", "xlink:href"]) {')
X4 = test('    if (typeof type === "string" && !EVENT_TYPES.has(type)) {', '    if (false) {')
X5 = test('      unknown.add(name);\n      return uninstrumented(name);', '      return undefined;')
X6 = test('  { what: "the open member", name: "open", exact: true },',
          '  { what: "the open member", name: "(?!)open", exact: true },')
# The reach rule enumerates every mention of a link function; the pre-fix form
# enumerated the `name(` call-site spelling, which a space before the paren
# escaped. X9 is that old enumeration, so Z3 must go green under it.
X9 = test('  const LINK_NAME = /\\b(navigateTo|openHaLink)\\b/;',
          '  const LINK_NAME = /\\b(navigateTo|openHaLink)\\(/;')
X7 = test('    navigate(u) { navRecord("navigation", String(u)); return null; },', '    navigate: undefined,')


# R10-DEEPLINK-HANDLERS (#2317): the handler drive and the document-level read.
ESCAPE = '      const origin = this.menuOrigin;'
RD7 = after_nav('try { const a = document.createElement("a"); a.setAttribute(["hr", "ef"].join(""), "%s"); a.click(); } catch (_e) {}' % P)
AL1 = kd('if (ev.ctrlKey) { try { globalThis.history.back(); } catch (_e) {} }')
KD1 = kd('if (key === "Delete") { try { globalThis.history.back(); } catch (_e) {} }')
FT1 = card(ESCAPE, '      try { globalThis.history.back(); } catch (_e) {}\n' + ESCAPE)
ON1 = card(LOOP, '  for (const b of root.querySelectorAll(".adv-act")) b.onkeydown = () => null;\n' + LOOP)
RV1 = kd('try { globalThis.history["back"](); } catch (_e) {}')
X14 = test('    [document.head, document.body, c, ...made].forEach(walk);',
           '    [c, ...made].forEach(walk);')
X15 = test('    ...["plan", "setup", "savings", "advisor", "health"].map((page) => ({ page })),\n', '')
RD9 = after_nav('try { document.body.innerHTML += `<a ${["hr", "ef"].join("")}="%s">x</a>`; } catch (_e) {}' % P)
UL1 = card("function healthPageHtml(host) {",
           'function unreachedListener(host) { host.addEventListener("keydown", () => null); }\n\nfunction healthPageHtml(host) {')
X16 = test('  navHook.made = (n) => { made.push(n); };', '  navHook.made = null;')
X17 = test('  for (const v of FIXTURES) {', '  for (const v of FIXTURES.filter((f) => !f.name)) {')
X18 = test('      saved.findAll.call(this, one.trim().replace(', '      saved.findAll.call(this, sel, out); break; saved.findAll.call(this, one.trim().replace(')
X19 = test('  Node.prototype.setAttributeNS = function (_ns, q, v) { this.setAttribute(String(q).split(":").pop(), v); };', '')
X20 = test('          if (VARY.some((f) => reads.has(f))) await', '          if (false) await')
X21 = test('        const keys = base.has("key") || base.has("code") ? [undefined, ...KEYS] : [undefined];',
           '        const keys = [undefined];')
X22 = test('      for (let j = 0; j < (first.has("target") ? nt : 1); j++) {', '      for (let j = 0; j < 1; j++) {')
X23 = test('      if (f.type === "click" || !(isDoc(f.on) || madeNow.has(f.on))) continue;', '      continue;')
X24 = test('    inline.size === 0, [...inline].join(", "));', '    true, [...inline].join(", "));')
X25 = test('    .filter(([l]) => /\\baddEventListener\\s*\\(/.test(l)).map(([, i]) => i + 1);',
           '    .filter(([l]) => /\\baddEventListener\\s*\\(/.test(l)).map(([, i]) => i + 1).filter((i) => driven.has(i));')
# #2452 round 1: the location object's every member, its aliases, the
# interfaces, the document's page-replacing members, the refresh pragma and
# markup the stub's parser drops, and deferred work -- each in the driven
# chart keydown, each name built so the static arm cannot see it.
LOC = 'globalThis[["loc", "ation"].join("")]'
BUILT_LOC = '[["loc", "ation"].join("")]'
HREF = '["hr", "ef"].join("")'
X26 = test('    set: (_t, k, v) => { navRecord("location", k === "href" ? String(v) : `${String(k)}=${String(v)}`); return true; },',
           '    set: (_t, k, v) => { if (k === "href") navRecord("location", String(v)); return true; },')
X27 = test('      if (typeof eq === "string" && eq.trim().toLowerCase() === "refresh") {', '      if (false) {')
X28 = test('      if (typeof n._html === "string") markupWaysOut(n._html, out);', '')
X29 = test('  Object.defineProperty(document, "location", locDesc);\n', '  document.location = { ...LOCATION_PARTS };\n')
X30 = test('  navHook.timer = {\n', '  navHook.timer = null && {\n')
X31 = test('    for (const a of WINDOW_ALIASES) g[a] = ctx.window;\n', '')
X32 = test('    History: navInterface("History", history),\n', '    History: function History() {},\n')
X33 = test('    write(...a) { navRecord("document", `write ${a.join("")}`); },', '    write() {},')
OWN1 = kd('{ const m = document.createElement("meta"); m.setAttribute("http-equiv", "refresh"); m.setAttribute("content", "0;url=/config/integrations"); document.head.appendChild(m); }')
OWN2 = kd(LOC + '.pathname = "/config/integrations";')
LD = kd('try { document%s = "/config/integrations"; } catch (_e) {}' % BUILT_LOC)
LT = kd('try { globalThis[["t", "op"].join("")]%s.pathname = "/config/integrations"; } catch (_e) {}' % BUILT_LOC)
LT2 = kd('try { globalThis[["par", "ent"].join("")]%s.pathname = "/config/integrations"; } catch (_e) {}' % BUILT_LOC)
IH = kd('try { globalThis[["Hist", "ory"].join("")].prototype[["push", "State"].join("")].call(globalThis.history, null, "", "/config/integrations"); } catch (_e) {}')
DW = kd('try { document[["wri", "te"].join("")]("<p>x</p>"); } catch (_e) {}')
UQ1 = kd('try { document.body.innerHTML += `<a ${%s}=/config/integrations>x</a>`; } catch (_e) {}' % HREF)
TM1 = kd('setTimeout(() => { try { globalThis.history.back(); } catch (_e) {} }, 50);')
# #2452 round 3: a reference to the surface taken when the card LOADS, before
# the census switches its recorders on (the round-2 review's rev_plants.py,
# verbatim, and the class it belongs to: every member, factory, timer, event
# class and registration method the census records through, captured at load).
TOP = "function navigateTo("
def at_load(stmt, use):
    return card(TOP, stmt + "\n" + TOP) + kd(use)
CAP4 = at_load('const __revH = window.history;', 'try { __revH.back(); } catch (_e) {}')
CAP5 = at_load('const __capW = document[["wri", "te"].join("")].bind(document);', 'try { __capW("<p>x</p>"); } catch (_e) {}')
CAP6 = at_load('const __capCE = document.createElement.bind(document);',
               'try { const a = __capCE("a"); a.setAttribute(%s, "%s"); a.click(); } catch (_e) {}' % (HREF, P))
CAP8 = at_load('const __capST = globalThis[["set", "Timeout"].join("")];',
               '__capST(() => { try { globalThis.history.back(); } catch (_e) {} }, 50);')
CAP9 = at_load('const __capAdd = HTMLElement.prototype.addEventListener;',
               'try { const el = document.createElement("div"); __capAdd.call(el, "keyup", () => { try { globalThis.history.back(); } catch (_e) {} }); } catch (_e) {}')
TMX = kd('{ const go = (n) => setTimeout(() => { if (n) go(n - 1); else { try { globalThis.history.back(); } catch (_e) {} } }); go(80); }')
XL1 = kd('try { document.body.innerHTML += `<svg><a xlink:${%s}="%s"><text>x</text></a></svg>`; } catch (_e) {}' % (HREF, P))
X34 = [(TEST, 'const cardSrc = fs.readFileSync("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js","utf8");\nvm.runInContext(cardSrc, ctx);\n',
        'const cardSrc = fs.readFileSync("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js","utf8");\n'),
       (TEST, '// --- A browser\'s navigation surface, live before the card loads (R10-DEEPLINK) --\n',
        'vm.runInContext(fs.readFileSync("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js","utf8"), ctx);\n// --- A browser\'s navigation surface, live before the card loads (R10-DEEPLINK) --\n')]
X35 = test("      threw.push(`${key}: deferred work had not settled after ${SETTLE_CAP} rounds`);\n", '')
X36 = [(TEST, '      for (const at of ["href", "xlink:href", "action", "formaction"]) {', '      for (const at of ["href", "action", "formaction"]) {'),
       (TEST, '  const MARKUP_WAY_OUT = /\\s(?:xlink:)?(href|action|formaction)', '  const MARKUP_WAY_OUT = /\\s(href|action|formaction)')]
RD4 = after_nav('try { const u = "%s"; const f = document.createElementNS("http://www.w3.org/1999/xhtml", "form"); f.action = u; const b = document.createElement("button"); f.appendChild(b); document.body.appendChild(f); b.click(); } catch (_e) {}' % P)
RD6 = after_nav('try { const a = document.createElement("a"); a.setAttribute(["hr", "ef"].join(""), "%s"); document.body.appendChild(a); a.click(); } catch (_e) {}' % P)


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
    "T1c_census_only_throw_on_press": after_nav('if (root.querySelectorAll(".adv-act, .adv-act").length) throw new Error("census-only boom");'),
    "T2c_census_only_async_reject_on_press": after_nav(
        'if (root.querySelectorAll(".adv-act, .adv-act").length) await Promise.reject(new Error("census-only reject"));'),
    # The residual's witness, expected GREEN (rc=0 fails=0): a name built at
    # run time, written through a selector the stub DOM cannot resolve, in a
    # handler a press does reach. The write runs on no element, so the
    # dynamic arm sees nothing, and the static arm refuses only a written
    # name. R7c is the same write on a selector the stub resolves (red).
    # The round-8 review's written spellings (#2345, the reviewer's
    # review_plants.py, verbatim), green at #2345's head, where the keydown
    # handler was undriven and no static row named the spelling. Expected RED
    # since R10-DEEPLINK-HANDLERS drives that handler. RV1c and RV5c, the
    # spellings #2345's rows named in the same position, stay red.
    "RV1_history_bracket_back_in_undriven_keydown": RV1,
    "RV2_history_optional_back_in_undriven_keydown": kd('try { globalThis.history?.back(); } catch (_e) {}'),
    "RV3_history_destructure_in_undriven_keydown": kd('try { const { back } = globalThis.history; back.call(globalThis.history); } catch (_e) {}'),
    "RV4_form_ns_action_member_button_click_in_undriven_keydown": kd('try { const u = "%s"; const f = document.createElementNS("http://www.w3.org/1999/xhtml", "form"); f.action = u; const b = document.createElement("button"); f.appendChild(b); document.body.appendChild(f); b.click(); } catch (_e) {}' % P),
    "RV5_action_member_to_variable_in_undriven_keydown": kd('try { const u = "%s"; const f = document.createElement("div"); f.action = u; } catch (_e) {}' % P),
    "RV6_object_assign_quoted_action_key_in_undriven_keydown": kd('try { const f = document.createElement("div"); Object.assign(f, { "action": "%s" }); } catch (_e) {}' % P),
    "RV7_create_element_ns_form_in_undriven_keydown": kd('try { const f = document.createElementNS("http://www.w3.org/1999/xhtml", "form"); root.appendChild(f); } catch (_e) {}'),
    "RV1c_history_dot_back_control": kd('try { globalThis.history.back(); } catch (_e) {}'),
    "RV5c_action_member_to_literal_control": kd('try { const f = document.createElement("div"); f.action = "%s"; } catch (_e) {}' % P),
    # The round-9 review's driven-press plants (#2345, review_plants9.py,
    # verbatim). RD4, green at #2345's head: a form appended to document.body,
    # outside the shadow root that census read, and submitted by a button's
    # click(), inside the advisor:settings press it drove; expected RED under
    # the document-level read. RD5, its red control, is the same form element
    # and action appended in the shadow root, placed and not submitted.
    "RD4_form_ns_action_member_button_click_driven": RD4,
    "RD5_action_member_to_variable_on_rendered_form_driven": after_nav('try { const u = "%s"; const f = document.createElementNS("http://www.w3.org/1999/xhtml", "form"); f.action = u; root.appendChild(f); } catch (_e) {}' % P),
    # The round-10 review's anchor (#2345, review_plants10.py, verbatim): RD6,
    # green at #2345's head and RED under the document-level read, is an
    # anchor whose href name is built at run time, appended to document.body
    # and click()ed in the same driven press; RD6c, the same anchor appended
    # in the shadow root and not clicked, is red.
    "RD6_anchor_built_href_outside_root_click_driven": RD6,
    "RD6c_anchor_built_href_in_root_driven_control": after_nav('try { const a = document.createElement("a"); a.setAttribute(["hr", "ef"].join(""), "%s"); root.appendChild(a); } catch (_e) {}' % P),
    # R10-DEEPLINK-HANDLERS (#2317). RD7: a detached anchor, never appended,
    # with a run-time-built href, click()ed in a driven press -- a browser
    # navigates by it, and the read covers every element the document made.
    # RD8, expected GREEN: markup inserted through a DOM member the stub does
    # not implement (insertAdjacentHTML) with a built name -- the residual's
    # stub-fidelity witness, beside Y1. AL1, KD1, FT1: navigation reached only
    # at the far end of the event's fields (ctrlKey), under one key literal,
    # and in a handler a drive registers (the slot menu's Escape). ON1: a
    # handler wired as an `on<event>` property, which no registration records.
    "RD7_detached_anchor_built_href_click_driven": RD7,
    "RD8_insert_adjacent_html_built_href_driven_residual": after_nav('try { const d = root.querySelector(".adv-act"); d.insertAdjacentHTML("afterend", `<a ${["hr", "ef"].join("")}="%s">x</a>`); } catch (_e) {}' % P),
    "AL1_history_back_under_ctrl_in_keydown": AL1,
    "KD1_history_back_under_delete_in_keydown": KD1,
    "FT1_history_back_in_slot_menu_escape": FT1,
    "ON1_inline_keydown_property": ON1,
    # RD9: markup with a built href written into document.body's innerHTML in
    # a driven press -- no factory made it, so only the body read sees it.
    # UL1: an addEventListener site no fixture renders.
    "RD9_body_inner_html_built_href_driven": RD9,
    "UL1_listener_site_no_fixture_renders": UL1,
    # #2452 round 1 (the review's own_plants.py, verbatim) and the class.
    "OWN1_meta_refresh_in_keydown": OWN1,
    "OWN2_location_pathname_built_in_keydown": OWN2,
    "OWN2c_location_href_built_in_keydown_control": kd(LOC + '.href = "/config/integrations";'),
    "OWN3_location_search_built_in_keydown": kd(LOC + '.search = "?x=1";'),
    "L1_location_hash_built": kd('try { %s.hash = "#x"; } catch (_e) {}' % LOC),
    "L2_location_host_built": kd('try { %s.host = "example.org"; } catch (_e) {}' % LOC),
    "L3_location_hostname_built": kd('try { %s.hostname = "example.org"; } catch (_e) {}' % LOC),
    "L4_location_port_built": kd('try { %s.port = "8124"; } catch (_e) {}' % LOC),
    "L5_location_protocol_built": kd('try { %s.protocol = "https:"; } catch (_e) {}' % LOC),
    "L6_location_reload_built": kd('try { %s.reload(); } catch (_e) {}' % LOC),
    "L7_location_object_assign_built": kd('try { Object.assign(%s, { pathname: "/config/integrations" }); } catch (_e) {}' % LOC),
    "L8_global_location_assigned_built": kd('try { globalThis%s = "/config/integrations"; } catch (_e) {}' % BUILT_LOC),
    "L9_window_location_assigned_built": kd('try { globalThis.window%s = "/config/integrations"; } catch (_e) {}' % BUILT_LOC),
    "LD1_document_location_assigned_built": LD,
    "LD2_document_location_pathname_built": kd('try { document%s.pathname = "/config/integrations"; } catch (_e) {}' % BUILT_LOC),
    "LT1_top_location_pathname_built": LT,
    "LT2_parent_location_pathname_built": LT2,
    "LT3_frames_location_pathname_built": kd('try { globalThis[["fra", "mes"].join("")]%s.pathname = "/config/integrations"; } catch (_e) {}' % BUILT_LOC),
    "LT4_window_self_location_hash_built": kd('try { globalThis.window[["se", "lf"].join("")]%s.hash = "#x"; } catch (_e) {}' % BUILT_LOC),
    "LT5_default_view_location_hash_built": kd('try { document[["default", "View"].join("")]%s.hash = "#x"; } catch (_e) {}' % BUILT_LOC),
    "IH1_history_prototype_push_state_built": IH,
    "IH2_history_get_prototype_back": kd('try { Object.getPrototypeOf(globalThis.history).back.call(globalThis.history); } catch (_e) {}'),
    "IN1_navigation_prototype_navigate_built": kd('try { const N = globalThis[["Navi", "gation"].join("")]; N.prototype.navigate.call(globalThis[["navi", "gation"].join("")], "/config/integrations"); } catch (_e) {}'),
    "DO1_document_open_url_built": kd('try { document[["op", "en"].join("")]("/config/integrations", "_self", ""); } catch (_e) {}'),
    "DW1_document_write_built": DW,
    "DW2_document_writeln_built": kd('try { document[["wri", "teln"].join("")]("<p>x</p>"); } catch (_e) {}'),
    "MR1_meta_refresh_member_in_body": kd('try { const m = document.createElement("meta"); m.httpEquiv = "Refresh"; m.content = "0"; document.body.appendChild(m); } catch (_e) {}'),
    "MR2_meta_refresh_quoted_markup": kd('try { document.body.innerHTML += \'<meta http-equiv="refresh" content="0;url=/config/integrations">\'; } catch (_e) {}'),
    "MR3_meta_refresh_unquoted_markup": kd('try { document.head.innerHTML += "<meta http-equiv=refresh content=0>"; } catch (_e) {}'),
    "B1_base_built_href_in_head": kd('try { const b = document.createElement("base"); b.setAttribute(%s, "/config/integrations/"); document.head.appendChild(b); } catch (_e) {}' % HREF),
    "B2_area_built_href_detached": kd('try { const a = document.createElement("area"); a.setAttribute(%s, "/config/integrations"); a.click(); } catch (_e) {}' % HREF),
    "UQ1_unquoted_built_href_markup": UQ1,
    "UQ2_single_quoted_built_href_markup": kd("try { document.body.innerHTML += `<a ${%s}='/config/integrations'>x</a>`; } catch (_e) {}" % HREF),
    "TM1_history_back_in_timeout": TM1,
    "TM2_history_back_in_interval": kd('{ const t = setInterval(() => { try { globalThis.history.back(); } catch (_e) {} }, 50); }'),
    "LRc_location_read_control": kd('try { const p = %s.pathname + %s.hash; void p; } catch (_e) {}' % (LOC, LOC)),
    "MRc_meta_not_a_pragma_control": kd('try { const m = document.createElement("meta"); m.setAttribute("name", "viewport"); document.head.appendChild(m); } catch (_e) {}'),
    "TMc_timer_does_nothing_control": kd('setTimeout(() => null, 0);'),
    # #2452 round 3: the round-2 review's plants (rev_plants.py, verbatim).
    "REV_CAP1_location_captured_at_load": at_load('const __revL = globalThis[["loc", "ation"].join("")];', 'try { __revL[["path", "name"].join("")] = "%s"; } catch (_e) {}' % "/config/integrations"),
    "REV_CAP1c_captured_location_resolves": at_load('const __revL = globalThis[["loc", "ation"].join("")];', 'try { if (typeof __revL === "object" && __revL) globalThis[["hist", "ory"].join("")][["ba", "ck"].join("")](); } catch (_e) {}'),
    "REV_CAP1d_location_captured_lazily": card(TOP, 'let __revL2 = null; const __revGetL = () => (__revL2 = __revL2 || globalThis[["loc", "ation"].join("")]);\n__revGetL();\n' + TOP) + kd('try { __revGetL()[["path", "name"].join("")] = "%s"; } catch (_e) {}' % "/config/integrations"),
    "REV_CAP2_history_captured_at_load": at_load('const __revH = globalThis[["hist", "ory"].join("")];', 'try { __revH[["ba", "ck"].join("")](); } catch (_e) {}'),
    "REV_CAP3_open_captured_at_load": at_load('const __revO = globalThis[["op", "en"].join("")];', 'try { __revO("%s", "_self"); } catch (_e) {}' % "/config/integrations"),
    "REV_CAP4_history_captured_at_load_literal": CAP4,
    "REV_CAP4c_window_captured_at_load_control": at_load('const __revW = window;', 'try { __revW.history.back(); } catch (_e) {}'),
    "REV_TM5_history_back_five_timeouts_deep": kd('setTimeout(() => setTimeout(() => setTimeout(() => setTimeout(() => setTimeout(() => { try { globalThis.history.back(); } catch (_e) {} })))));'),
    "REV_TM4c_history_back_four_timeouts_deep_control": kd('setTimeout(() => setTimeout(() => setTimeout(() => setTimeout(() => { try { globalThis.history.back(); } catch (_e) {} }))));'),
    "REV_PR1_history_back_in_unawaited_promise_chain": kd('Promise.resolve().then(() => null).then(() => null).then(() => { try { globalThis.history.back(); } catch (_e) {} });'),
    "REV_XL1_svg_xlink_href_markup": XL1,
    "REV_XL1c_svg_plain_href_markup_control": kd('try { document.body.innerHTML += `<svg><a ${%s}="%s"><text>x</text></a></svg>`; } catch (_e) {}' % (HREF, "/config/integrations")),
    "REV_FM1_form_from_markup_no_action": kd('try { document.body.innerHTML += "<fo" + "rm><input></fo" + "rm>"; } catch (_e) {}'),
    "REV_RF1_reflect_set_location_hash": kd('try { Reflect.set(globalThis[["loc", "ation"].join("")], "hash", "#x"); } catch (_e) {}'),
    "REV_RF2_reflect_define_location_search": kd('try { Reflect.defineProperty(globalThis[["loc", "ation"].join("")], "search", { value: "?x" }); } catch (_e) {}'),
    "REV_WO1_defaultview_open_built": kd('try { document.defaultView[["op", "en"].join("")]("%s"); } catch (_e) {}' % "/config/integrations"),
    "REV_PX1_proxy_wrapped_anchor_href": kd('try { const a = new Proxy(document.createElement("a"), {}); a[%s] = "%s"; a.click(); } catch (_e) {}' % (HREF, "/config/integrations")),
    # The captured-at-load class beyond the review's four: every other thing
    # the census records through, taken when the card loads.
    "CAP5_document_write_captured_at_load": CAP5,
    "CAP6_create_element_captured_at_load": CAP6,
    "CAP7_custom_event_captured_at_load": at_load('const __capCEv = globalThis[["Custom", "Event"].join("")];',
        'try { globalThis.dispatchEvent(new __capCEv(%s, { detail: { entityId: "sensor.x" } })); } catch (_e) {}' % RUNTIME_MORE_INFO),
    "CAP8_set_timeout_captured_at_load": CAP8,
    "CAP9_add_event_listener_captured_at_load": CAP9,
    "CAP10_navigation_captured_at_load": at_load('const __capN = globalThis[["navi", "gation"].join("")];', 'try { __capN.navigate("/config/integrations"); } catch (_e) {}'),
    "CAP11_history_interface_captured_at_load": at_load('const __capHI = globalThis[["Hist", "ory"].join("")].prototype;',
        'try { __capHI[["push", "State"].join("")].call(globalThis.history, null, "", "/config/integrations"); } catch (_e) {}'),
    "CAP12_location_descriptor_captured_at_load": at_load('const __capLD = Object.getOwnPropertyDescriptor(globalThis, ["loc", "ation"].join(""));',
        'try { __capLD.get()[["ha", "sh"].join("")] = "#x"; } catch (_e) {}'),
    "CAP13_window_alias_captured_at_load": at_load('const __capT = globalThis[["par", "ent"].join("")];', 'try { __capT[["loc", "ation"].join("")].hash = "#x"; } catch (_e) {}'),
    "TMX_history_back_eighty_timeouts_deep": TMX,
    "Y1_runtime_name_on_unresolved_selector_residual": attach("a.zz", 'a.setAttribute(["hr", "ef"].join(""), "%s");' % P),
    "W1_guarded_unbound_global": W1,
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
    # This fix's own lines (R10-DEEPLINK-HANDLERS), alone and with the plant
    # each one closes.
    "X14_read_shadow_root_only": X14,
    "X14RD9_document_read_is_what_closes_RD9": X14 + RD9,
    "X16RD4_made_tracking_also_closes_RD4": X16 + RD4,
    "X15_no_handler_drive": X15,
    "X15RV1_handler_drive_is_what_closes_RV1": X15 + RV1,
    "X16_made_untracked": X16,
    "X16RD7_made_tracking_is_what_closes_RD7": X16 + RD7,
    "X17_no_variants": X17,
    "X18_selector_engine_unshimmed": X18,
    "X19_no_set_attribute_ns": X19,
    "X19V12_set_attribute_ns_is_what_closes_V12": X19 + V12_KEYDOWN_SET_ATTRIBUTE_NS_ACTION,
    "X20_no_alt_drive": X20,
    "X20AL1_alt_drive_is_what_closes_AL1": X20 + AL1,
    "X21_no_key_drive": X21,
    "X21KD1_key_drive_is_what_closes_KD1": X21 + KD1,
    "X22_own_target_only": X22,
    "X22RV1_targets_are_what_close_RV1": X22 + RV1,
    "X23_no_follow_through": X23,
    "X23FT1_follow_through_is_what_closes_FT1": X23 + FT1,
    "X24_inline_check_off": X24,
    "X24ON1_inline_check_is_what_closes_ON1": X24 + ON1,
    "X25_reach_counts_driven_sites_only": X25,
    "X25UL1_reach_line_is_what_closes_UL1": X25 + UL1,
    # This fix's own lines (#2452 round 2), alone and with the plant each closes.
    "X26_location_records_href_only": X26,
    "X26OWN2_member_trap_is_what_closes_OWN2": X26 + OWN2,
    "X27_no_refresh_read": X27,
    "X27OWN1_refresh_read_is_what_closes_OWN1": X27 + OWN1,
    "X28_no_markup_read": X28,
    "X28UQ1_markup_read_is_what_closes_UQ1": X28 + UQ1,
    "X29_document_location_inert": X29,
    "X29LD1_document_location_is_what_closes_LD1": X29 + LD,
    "X30_no_settle": X30,
    "X30TM1_settle_is_what_closes_TM1": X30 + TM1,
    "X31_no_window_aliases": X31,
    "X31LT1_aliases_are_what_close_LT1": X31 + LT,
    # LT1 stays red under X31: the card's code mentions `top`, so the watch
    # refuses the global by name. `parent` it does not mention.
    "X31LT2_aliases_are_what_close_LT2": X31 + LT2,
    "X32_history_interface_inert": X32,
    "X32IH1_interface_is_what_closes_IH1": X32 + IH,
    "X33_document_write_inert": X33,
    "X33DW1_write_recorder_is_what_closes_DW1": X33 + DW,
    # Round 3: the surface installed before the card loads, the settle cap,
    # the xlink read and registration through the live method.
    "X34_card_loads_before_the_surface": X34,
    "X34CAP4_load_order_is_what_closes_REV_CAP4": X34 + CAP4,
    "X35_settle_cap_drops_silently": X35,
    "X35TMX_cap_refusal_is_what_closes_TMX": X35 + TMX,
    "X36_no_xlink_read": X36,
    "X36XL1_xlink_read_is_what_closes_REV_XL1": X36 + XL1,
    "X16CAP6_made_hook_is_what_closes_CAP6": X16 + CAP6,
    "X30CAP8_timer_hook_is_what_closes_CAP8": X30 + CAP8,
    "X33CAP5_write_recorder_is_what_closes_CAP5": X33 + CAP5,
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
        # The census's live set -- every element the document's factories made,
        # held for the whole run -- is past node's default old space on an
        # 8-core box. Measured 2026-10-20: `node tests/card.mjs` alone at the
        # default 2096 MB dies rc=134 (SIGABRT, "Ineffective mark-compacts near
        # heap limit"); 2560 MB completes rc=0 at 1 233 567 744 B peak RSS;
        # 4096 MB completes rc=0 at 841 007 104 B. The flag buys the collector
        # its own budget and no plant's verdict can depend on it.
        r = subprocess.run(["node", "--max-old-space-size=4096", TEST],
                           capture_output=True, text=True, timeout=1800)
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
