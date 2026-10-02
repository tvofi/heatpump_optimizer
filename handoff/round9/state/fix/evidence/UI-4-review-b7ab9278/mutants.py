import subprocess, sys, os, shutil
F="custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
W="/tmp/claude-0/r2"
orig=open(f"{W}/{F}").read()
M={
 "MA_bars_on_plot_floor": ("    return p ? p.bottom : plotB;\n","    return plotB;\n"),
 "MB_actioned_band_plotB": ("        const base = baseOf(\"power\");\n","        const base = plotB;\n"),
 "MC_shared_band_full_height": ("sharedSpanBands(visible, scaleX, power.top, power.bottom,","sharedSpanBands(visible, scaleX, plotT, plotB,"),
 "MD_outdoor_dark_eq_house": ("    color: \"#3b7dd8\",\n    colorDark: \"#4b95e8\",","    color: \"#3b7dd8\",\n    colorDark: \"#1f9d1f\","),
 "ME_estimated_first_panel_only": ("    for (const p of panels) {\n    // The wash","    for (const p of panels.slice(0, 1)) {\n    // The wash"),
 "MF_nowtemp_at_top": ("y=\"${panelOf(\"temp\").top + labelRow}\"","y=\"${top + labelRow}\""),
 "MG_grid_v_full_height": ("      panels.map((p) => [p.top, p.bottom])\n","      null\n"),
 "MH_hidden_panel_keeps_height": ("  let shown = CHART_PANELS.filter((p) => p.axes.some((n) => axes[n]));","  let shown = CHART_PANELS;"),
}
env=dict(os.environ)
for name,(a,b) in M.items():
    if orig.count(a)!=1: print(name,"PATTERN-COUNT",orig.count(a)); continue
    open(f"{W}/{F}","w").write(orig.replace(a,b))
    r=subprocess.run(["node","tests/card.mjs"],cwd=W,capture_output=True,text=True,env=env)
    out=r.stdout+r.stderr
    open(f"/tmp/claude-0/mut/r2_{name}.card.txt","w").write(out)
    fails=[l for l in out.splitlines() if "FAIL" in l]
    print(f"{name}: card rc={r.returncode} fails={len(fails)}")
    for l in fails[:6]: print("   ",l[:200])
open(f"{W}/{F}","w").write(orig)
print("restored", subprocess.run(["git","status","--short"],cwd=W,capture_output=True,text=True).stdout or "clean")
