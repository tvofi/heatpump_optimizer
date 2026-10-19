#!/usr/bin/env python3
"""Reviewer's own plants (round 1 review of #2452), built on the PR's driver's run()/kd().
Run from a worktree root at the head after plan_view.py."""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("d", "tools/audit/seat/r10_deeplink_mutants.py")
d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
LOC = 'globalThis[["loc", "ation"].join("")]'
PLANTS = {
    # a meta refresh appended to the head: navigates in a browser, names nothing on the static list
    "OWN1_meta_refresh_in_keydown": d.kd('{ const m = document.createElement("meta"); m.setAttribute("http-equiv", "refresh"); m.setAttribute("content", "0;url=/config/integrations"); document.head.appendChild(m); }'),
    # the location object's pathname setter, name built at run time: navigates in a browser
    "OWN2_location_pathname_built_in_keydown": d.kd(LOC + '.pathname = "/config/integrations";'),
    # the same object's href setter: control, expected RED
    "OWN2c_location_href_built_in_keydown_control": d.kd(LOC + '.href = "/config/integrations";'),
    # location.search setter, built name: navigates (reload with a query)
    "OWN3_location_search_built_in_keydown": d.kd(LOC + '.search = "?x=1";'),
}
for n in sys.argv[1:] or PLANTS:
    d.run(n, PLANTS[n])
