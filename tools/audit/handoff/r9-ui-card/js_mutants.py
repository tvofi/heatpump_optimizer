"""R9-UI-3 mutation proof for the card's JS: mutation_table.py measures only
Python sites, so it reports no candidate site for this diff.

Run from the repository root of a clean tree (it restores the card file when
it ends): python3 tools/audit/handoff/r9-ui-card/js_mutants.py
Each mutant breaks one seam of the change and runs tests/card.mjs; KILLED means
card.mjs exited non-zero, with the failing checks it printed. A mutant whose
replacement does not apply prints NOAPPLY rather than a kill.
"""
import subprocess
P='custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js'
orig=open(P).read()
M=[
 ("headline drops indoor", lambda s: s.replace("function headlineSignature(plan, cfg, indoor, now) {", "function headlineSignature(plan, cfg, indoor, now) { indoor = null;",1)),
 ("_signature drops statusSignature", lambda s: s.replace("statusSignature(this.plan, Date.now())", '"-"',1)),
 ("stale floor 90->60", lambda s: s.replace("PLAN_STALE_FLOOR_MIN = 90","PLAN_STALE_FLOOR_MIN = 60",1)),
 ("stale intervals 3->1", lambda s: s.replace("PLAN_STALE_INTERVALS = 3","PLAN_STALE_INTERVALS = 1",1)),
 ("interval estimate ignored", lambda s: s.replace("? est : DEFAULT_SOLVE_INTERVAL_MIN","? DEFAULT_SOLVE_INTERVAL_MIN : DEFAULT_SOLVE_INTERVAL_MIN",1)),
 ("stale > to <", lambda s: s.replace("age.minutes > age.limit","age.minutes < age.limit",1)),
 ("fallback every->some", lambda s: s.replace('plans.every((st) => st.state === "no plan")','plans.some((st) => st.state === "no plan")',1)),
 ("fallback after stale", lambda s: s.replace('if (plans.every((st) => st.state === "no plan")) {','if (false) {',1)),
 ("heating some->every", lambda s: s.replace("plans.some((st) => !!(st.attributes && st.attributes.active_now))","plans.every((st) => !!(st.attributes && st.attributes.active_now))",1)),
 ("manual ignored", lambda s: s.replace("const manual = plan.manualOverride();","const manual = null;",1)),
 ("themeFallbacks identity", lambda s: s.replace("function themeFallbacks(css, darkMode) {","function themeFallbacks(css, darkMode) { return css;",1)),
 ("dark surface literal", lambda s: s.replace('light: "#ffffff", dark: "#1c1c1c"','light: "#ffffff", dark: "#ffffff"',1)),
 ("indoorValue null", lambda s: s.replace("function indoorValue(st) {","function indoorValue(st) { return null;",1)),
 ("cost tile reads energy", lambda s: s.replace('const cost = planTotal(plan, "total_cost");','const cost = planTotal(plan, "total_energy_kwh");',1)),
 ("show_stats ignored", lambda s: s.replace("function tilesHtml(plan, cfg, indoor, now) {\n  if (!cfg.show_stats) return \"\";","function tilesHtml(plan, cfg, indoor, now) {",1)),
 ("price area 0.16->0.18", lambda s: s.replace("areaOpacity: 0.16","areaOpacity: 0.18",1)),
 ("solar area 0.1->0.18", lambda s: s.replace("areaOpacity: 0.1,","areaOpacity: 0.18,",1)),
 ("tile order swap", lambda s: s.replace('const temp = indoorValue(indoor);','const temp = indoorValue(indoor); tiles.reverse();',1)),
]
try:
    for name, f in M:
        s = f(orig)
        if s == orig:
            print(f"NOAPPLY {name}")
            continue
        open(P, "w").write(s)
        r = subprocess.run(["node", "tests/card.mjs"], capture_output=True, text=True)
        fails = [l.strip() for l in r.stdout.split("\n") if l.startswith("  FAIL")]
        print(f"{'KILLED' if r.returncode else 'SURVIVED'} {name}: {len(fails)} fail(s) {fails[:2]}")
finally:
    open(P, "w").write(orig)
