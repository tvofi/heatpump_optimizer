#!/usr/bin/env python3
"""Round-4 reviewer plants for #2283 (the reviewer's own instrument).

Run from a worktree root at the head, after plan_view.py. Reuses the fixer's
r10_deeplink_mutants.run (apply, run node tests/card.mjs, restore).
"""
import importlib.util, os, sys
spec = importlib.util.spec_from_file_location("d", os.path.join(os.getcwd(), "tools/audit/seat/r10_deeplink_mutants.py"))
d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
P = d.P
DISMISS = d.DISMISS
pre_dismiss = lambda stmt: d.card(DISMISS, "        " + stmt + "\n" + DISMISS)
EV = 'host.dispatchEvent(Object.assign(new Event(%s, { bubbles: true, composed: true }), { detail: { entityId: "sensor.x" } }));'
PLANTS = {
    # Navigation API: no token, no instrumented primitive.
    "K1_navigation_api_in_try": d.after_nav('try { globalThis.navigation.navigate("/config/entities"); } catch (_e) {}'),
    "K1c_navigation_api_bare (control: no-throw)": d.after_nav('globalThis.navigation.navigate("/config/entities");'),
    # Declarative form navigation on a rendered page (health), no listener.
    "K2_form_action_rendered": d.card(d.DIAG, '<form action="/config/entities"><button type="submit">go</button></form>' + d.DIAG),
    # HA's own fireEvent shape: new Event + detail, name assembled at run time, on a rendered pressed row.
    "K3_Event_runtime_more_info_rendered": d.after_nav(EV % d.RUNTIME_MORE_INFO),
    "K3c_Event_literal_more_info (control: token)": d.after_nav(EV % '"hass-more-info"'),
    # Bare global open(): the token needs a dot.
    "K5_bare_open_on_dismiss": pre_dismiss('open("/config/entities", "_self");'),
    "K5b_bracket_open_on_dismiss": pre_dismiss('globalThis["open"]("/config/entities", "_self");'),
    "K5c_open_call_on_dismiss": pre_dismiss('globalThis.open.call(globalThis, "/config/entities", "_self");'),
    "K5r_bare_open_rendered (control: dynamic)": d.after_nav('open("/config/entities", "_self");'),
    # Exemption probe: the exempt string followed by a real navigation on one line.
    "K6_exemption_same_line": d.card("    this.dialog.open();\n  }\n\n  _onExpandClick", '    this.dialog.open(); globalThis.open("/config/entities");\n  }\n\n  _onExpandClick'),
    # Added after the first pass (same run, see mut4_out.txt).
    "K3t_Event_runtime_more_info_rendered_in_try": d.after_nav('try { ' + EV % d.RUNTIME_MORE_INFO + ' } catch (_e) {}'),
    # A press that throws only inside the census (marker: the census's CustomEvent subclass).
    # T1/T2 (marker CustomEvent.name) were a bad marker: the rig's class is anonymous, so they crashed scenario 1.
    "T1b_census_only_throw_on_press": d.after_nav('if (Object.getPrototypeOf(CustomEvent).prototype) throw new Error("census-only boom");'),
    "T2b_census_only_async_reject_on_press": d.after_nav('if (Object.getPrototypeOf(CustomEvent).prototype) await Promise.reject(new Error("census-only reject"));'),
}
names = sys.argv[1:] or list(PLANTS)
for n in names:
    d.run(n, PLANTS[n])
