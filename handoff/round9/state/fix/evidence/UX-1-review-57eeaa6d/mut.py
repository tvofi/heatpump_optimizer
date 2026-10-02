import subprocess, sys, os
P = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
os.chdir("/tmp/claude-0/ux1")
orig = open(P).read()
MUTS = {
 "R1_no_solar": ("  if (s0 >= 0) {\n    let peak", "  if (false) {\n    let peak"),
 "R2_dhwmin_attr_renamed": ('dhwMin: plan.attr("dhw_min_temperature", null)', 'dhwMin: plan.attr("dhw_min_temp", null)'),
 "R3_dhw_ctx_is_space": ('dhw: plan.forecastOf("dhw"),', 'dhw: plan.forecastOf("space"),'),
 "R4_coast_no_step": ("to: whyClock(ts[end] + step) }", "to: whyClock(ts[end]) }"),
 "R5_rank_strict": ("prices.filter((v) => v >= price)", "prices.filter((v) => v > price)"),
 "R6_flip_at_60": ("leftPx > rect.width * 0.5 ? leftPx - ttWidth - 14", "leftPx > rect.width * 0.6 ? leftPx - ttWidth - 14"),
 "R7_no_coast": ("    if (end >= 0) {\n      let start = end;", "    if (false) {\n      let start = end;"),
 "R8_narrative_first_only": ('? published.filter((l) => typeof l === "string" && l)', '? published.filter((l) => typeof l === "string" && l).slice(0, 1)'),
 "R9_narrative_reversed": ('? published.filter((l) => typeof l === "string" && l)', '? published.filter((l) => typeof l === "string" && l).reverse()'),
 "R10_tank_on_space_ch": ('if (ch === "dhw" && min !== null', 'if (min !== null'),
}
out = []
for name, (a, b) in MUTS.items():
    assert orig.count(a) == 1, name
    open(P, "w").write(orig.replace(a, b))
    r = subprocess.run(["node", "tests/card.mjs"], capture_output=True, text=True,
                       env={**os.environ, "HPO_PLANDATA": "/tmp/claude-0/plan.json"})
    fails = [l for l in (r.stdout + r.stderr).splitlines() if l.strip().startswith("FAIL")]
    out.append(f"{name}: rc {r.returncode}, failing {len(fails)}")
    out += ["  " + f[:140] for f in fails[:4]]
open(P, "w").write(orig)
print("\n".join(out))
