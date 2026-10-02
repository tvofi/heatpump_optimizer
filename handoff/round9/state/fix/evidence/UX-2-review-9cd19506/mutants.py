import sys,subprocess,re
F=sys.argv[1]
M={
"R1_nosort":("return rows.sort((a, b) => (b.value ?? -1) - (a.value ?? -1));","return rows;"),
"R3_gap0":("if (!(value > 0) || !attrs.top_slot) return null;","if (!attrs.top_slot) return null;"),
"R4_atrec":("|| to === from) return null;",") return null;"),
"R6_round":("const target = Math.min(30, Math.max(0, Math.round(to * 2) / 2));","const target = to;"),
"D1_norun":("        host.whatIf.run();\n        return;","        return;"),
"D2_noseed":("if (Number.isFinite(to)) host.whatIf.draft().comfort = Math.min(24, Math.max(16, to));",""),
"D3_uptile":("target: Number(tiles.down.overrides && tiles.down.overrides.target_temp),","target: Number(tiles.up.overrides && tiles.up.overrides.target_temp),"),
"D4_nointerp":("  return y0 + ((y1 - y0) * (setpoint - x0)) / (x1 - x0);","  return y1;"),
"D5_unavail_attrs":("if (st.state === \"unavailable\") return { kind, status: \"error\" };\n  const attrs = st.attributes || {};\n  if (st.state === \"unknown\") {","const attrs = st.attributes || {};\n  if (st.state === \"unavailable\" || st.state === \"unknown\") {"),
"D6_degsign":("value: Number(tiles.down.monthly_cost_delta) < 0 ? -Number(tiles.down.monthly_cost_delta) : null,","value: Number(tiles.down.monthly_cost_delta),"),
"D7_optin_always":("(priceTiles(host.plan) ? ADVISOR_OPT_IN : [\"degree\", ...ADVISOR_OPT_IN])","[\"degree\", ...ADVISOR_OPT_IN]"),
}
src=open(F).read()
for k,(o,n) in M.items():
    c=src.count(o)
    if c!=1: print(k,"NOT APPLIED count",c); continue
    open(F,"w").write(src.replace(o,n))
    r=subprocess.run(["node","tests/card.mjs"],capture_output=True,text=True)
    fails=[l.strip() for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
    print(k,"rc",r.returncode,"KILLED" if fails or r.returncode else "SURVIVED",fails[:3])
    open(F,"w").write(src)
