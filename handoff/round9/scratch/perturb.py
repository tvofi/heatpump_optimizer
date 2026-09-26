import pathlib,subprocess,sys,os,re
P=[
 ("count elsewhere: README 75->76", "README.md", "All 75 entities", "All 76 entities"),
 ("platform head: Buttons total +1", "README.md", "### Buttons (4 total)", "### Buttons (5 total)"),
 ("state list: drop `eco` from Heat Pump Action row", "README.md", "`eco`, `normal`", "`normal`"),
 ("census: drop DHW Setpoint Advisor from the sentence", "README.md", "DHW Setpoint Advisor and Plan", "Plan"),
 ("card comment names a ghost member", "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js", "// ", "// see `_ghostMember` ", ),
 ("sv help text writes '45 C'", "custom_components/heatpump_optimizer/translations/sv.json", "°C", " 45 C"),
 ("ANCHOR: README loses its Disabled-by-default list", "README.md", "Disabled by default: ", "Off unless enabled: "),
 ("ANCHOR: no '<N> entities' left in corpus", None, None, None),
]
env=dict(os.environ,PYTHONPATH="tests/hastub:tests:custom_components")
for label,f,old,new in P:
    saved={}
    if f:
        p=pathlib.Path(f); t=p.read_text(); assert old in t,(label); saved[p]=t; p.write_text(t.replace(old,new,1))
    else:
        for p in [pathlib.Path("README.md"),pathlib.Path("docs/architecture.md"),pathlib.Path("docs/configuration.md")]:
            t=p.read_text(); saved[p]=t; p.write_text(re.sub(r"\b(\d{2,3}) entities\b", r"\1 things", t))
    r=subprocess.run(["/home/claude/venv314/bin/python","tests/doc_claims.py"],env=env,capture_output=True,text=True)
    for p,t in saved.items(): p.write_text(t)
    fails=[l.strip()[:150] for l in r.stdout.splitlines() if "FAIL" in l]
    print(f"[{label}] rc={r.returncode} fails={len(fails)}"); [print("    ",x) for x in fails]
