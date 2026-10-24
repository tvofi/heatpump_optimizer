#!/usr/bin/env python3
"""Reviewer's own plants for #2452 round 2 (built by the reviewer, not the finder).
Uses the finder's driver (tools/audit/seat/r10_deeplink_mutants.py) run() and helpers."""
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), "tools/audit/seat"))
import r10_deeplink_mutants as m

P = "/config/integrations"
TOP = "function navigateTo("
def top(stmt):
    return m.card(TOP, stmt + "\n" + TOP)

REV = {
  # a reference captured at module load, before the census installs its sink
  "REV_CAP1_location_captured_at_load": top('const __revL = globalThis[["loc", "ation"].join("")];') + m.kd('try { __revL[["path", "name"].join("")] = "%s"; } catch (_e) {}' % P),
  "REV_CAP1c_captured_location_resolves_control": top('const __revL = globalThis[["loc", "ation"].join("")];') + m.kd('try { if (typeof __revL === "object" && __revL) globalThis[["hist", "ory"].join("")][["ba", "ck"].join("")](); } catch (_e) {}'),
  "REV_CAP1d_location_captured_in_constructor_scope_lazy": top('let __revL2 = null; const __revGetL = () => (__revL2 = __revL2 || globalThis[["loc", "ation"].join("")]);\n__revGetL();') + m.kd('try { __revGetL()[["path", "name"].join("")] = "%s"; } catch (_e) {}' % P),
  "REV_CAP4_history_captured_at_load_literal": top('const __revH = window.history;') + m.kd('try { __revH.back(); } catch (_e) {}'),
  "REV_CAP4c_window_captured_at_load_control": top('const __revW = window;') + m.kd('try { __revW.history.back(); } catch (_e) {}'),
  "REV_CAP2_history_captured_at_load": top('const __revH = globalThis[["hist", "ory"].join("")];') + m.kd('try { __revH[["ba", "ck"].join("")](); } catch (_e) {}'),
  "REV_CAP3_open_captured_at_load": top('const __revO = globalThis[["op", "en"].join("")];') + m.kd('try { __revO("%s", "_self"); } catch (_e) {}' % P),
  # deferred work nested deeper than the settle loop's rounds
  "REV_TM5_history_back_five_timeouts_deep": m.kd('setTimeout(() => setTimeout(() => setTimeout(() => setTimeout(() => setTimeout(() => { try { globalThis.history.back(); } catch (_e) {} })))));'),
  "REV_TM4c_history_back_four_timeouts_deep_control": m.kd('setTimeout(() => setTimeout(() => setTimeout(() => setTimeout(() => { try { globalThis.history.back(); } catch (_e) {} }))));'),
  # deferral through a promise the handler does not await
  "REV_PR1_history_back_in_unawaited_promise_chain": m.kd('Promise.resolve().then(() => null).then(() => null).then(() => { try { globalThis.history.back(); } catch (_e) {} });'),
  # an svg anchor's xlink:href in markup: the HTML parser puts it in the XLink namespace and the anchor navigates
  "REV_XL1_svg_xlink_href_markup": m.kd('try { document.body.innerHTML += `<svg><a xlink:${%s}="%s"><text>x</text></a></svg>`; } catch (_e) {}' % (m.HREF, P)),
  "REV_XL1c_svg_plain_href_markup_control": m.kd('try { document.body.innerHTML += `<svg><a ${%s}="%s"><text>x</text></a></svg>`; } catch (_e) {}' % (m.HREF, P)),
  # a form born from markup, no action
  "REV_FM1_form_from_markup_no_action": m.kd('try { document.body.innerHTML += "<fo" + "rm><input></fo" + "rm>"; } catch (_e) {}'),
  # the Reflect family on the location object and on an anchor
  "REV_RF1_reflect_set_location_hash": m.kd('try { Reflect.set(globalThis[["loc", "ation"].join("")], "hash", "#x"); } catch (_e) {}'),
  "REV_RF2_reflect_define_location_search": m.kd('try { Reflect.defineProperty(globalThis[["loc", "ation"].join("")], "search", { value: "?x" }); } catch (_e) {}'),
  # window.open through the document's view, built
  "REV_WO1_defaultview_open_built": m.kd('try { document.defaultView[["op", "en"].join("")]("%s"); } catch (_e) {}' % P),
  # an anchor click() built and detached via Proxy-wrapped element
  "REV_PX1_proxy_wrapped_anchor_href": m.kd('try { const a = new Proxy(document.createElement("a"), {}); a[%s] = "%s"; a.click(); } catch (_e) {}' % (m.HREF, P)),
}

def main():
    for name in sys.argv[1:]:
        edits = REV.get(name) or m.PLANTS.get(name)
        if name == "--null": m.run("NULL_no_plant", []); continue
        m.run(name, edits)
    import subprocess
    left = subprocess.run(["git", "status", "--short", "--", m.CARD, m.TEST], capture_output=True, text=True).stdout
    print("restored" if not left.strip() else "NOT RESTORED:\n" + left)

if __name__ == "__main__":
    main()
