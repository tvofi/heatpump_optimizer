import subprocess, sys, pathlib
wt = pathlib.Path(sys.argv[1]); card = wt/"custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
orig = card.read_text()
M = {
 "M1 block_ignored guard deleted": (' && !(ext.attributes && ext.attributes.block_ignored === true)', ''),
 "M2 external-heat branch disabled": ('if (ext && ext.state === "on"', 'if (false && ext && ext.state === "on"'),
 "M3 both-active forced false": ('const text = heatSpace && heatDhw ?', 'const text = false ?'),
 "M4 DHW collapsed to space": (': heatSpace ? L("status.heating_space") : L("status.heating_dhw")', ': L("status.heating_space")'),
 "M5 twin read as any suffix": ('    if (st) return st;\n  }\n  return null;\n}', '    if (st) return st;\n  }\n  const k = Object.keys(plan.hass && plan.hass.states ? plan.hass.states : {}).find((id) => id.startsWith("binary_sensor.") && id.endsWith(suffix));\n  return k ? plan.stateOf(k) : null;\n}'),
 "M6 ext heat ahead of stale (stale check removed)": ('if (age && age.minutes > age.limit) {', 'if (false && age && age.minutes > age.limit) {'),
 "M7 ext state==on check dropped": ('ext && ext.state === "on" &&', 'ext &&'),
 "M8 heating_dhw text swapped to both": ('L("status.heating_space") : L("status.heating_dhw")', 'L("status.heating_space") : L("status.heating_both")'),
 "M9 heatDhw ignored": ('const heatDhw = active(dhw);', 'const heatDhw = false;'),
}
for name,(a,b) in M.items():
    n = orig.count(a)
    if n != 1:
        print(f"{name}: SKIP anchor count {n}"); continue
    card.write_text(orig.replace(a,b))
    try:
        r = subprocess.run(["node","tests/card.mjs"],cwd=wt,capture_output=True,text=True,timeout=600)
        fails=[l for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
        print(f"{name}: rc={r.returncode} {len(fails)} FAIL"); [print("   ",f[:200]) for f in fails[:6]]
    finally:
        card.write_text(orig)
print("restored", subprocess.run(["git","diff","--quiet"],cwd=wt).returncode==0)
