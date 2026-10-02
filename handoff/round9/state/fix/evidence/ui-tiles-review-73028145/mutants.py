import subprocess,sys
F="custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
orig=open(F).read()
M={
"M1_tiles4":('.tiles {\n        display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));','.tiles {\n        display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));'),
"M2_no_stats_on_plan":('? `${stats}${this.plan.awayStripHtml()}','? `${this.plan.awayStripHtml()}'),
"M3_hlstats_media4":('      @media (max-width: 600px) {','      @media (min-width: 601px) { .hl-stats { grid-template-columns: repeat(4, minmax(0, 1fr)); } }\n      @media (max-width: 600px) {'),
"M4_both_media4":('      @media (max-width: 600px) {','      @media (min-width: 601px) { .tiles, .hl-stats { grid-template-columns: repeat(4, minmax(0, 1fr)); } }\n      @media (max-width: 600px) {'),
"M5_score_single":("for (const scoreStat of this.shadowRoot.querySelectorAll('[data-stat=\"score\"]')) {","for (const scoreStat of [this.shadowRoot.querySelector('[data-stat=\"score\"]')].filter(Boolean)) {"),
"M6_anywhere":('color: var(--hpo-text, #212121); overflow-wrap: break-word;\n      }\n      .tile.accent','color: var(--hpo-text, #212121); overflow-wrap: anywhere;\n      }\n      .tile.accent'),
}
for k,(a,b) in M.items():
    assert orig.count(a)==1,(k,orig.count(a))
    open(F,"w").write(orig.replace(a,b))
    r=subprocess.run(["node","tests/card.mjs"],capture_output=True,text=True)
    fails=[l.strip() for l in (r.stdout+r.stderr).splitlines() if l.strip().startswith("FAIL")]
    print(k,"rc=%d"%r.returncode,"KILLED" if r.returncode else "SURVIVED",fails[:3])
open(F,"w").write(orig)
