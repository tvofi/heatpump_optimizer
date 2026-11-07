import subprocess, sys, os, pathlib, json
W = pathlib.Path("/tmp/tmp.0w9kHgL2xk"); HEAD = "8bc540e052a8a4ac048715d4d2e7d0ab9a260c08"
BP="blueprints/automation/notifications.yaml"; CC="custom_components/heatpump_optimizer/"; CARD=CC+"www/heatpump-optimizer-card.js"
NOTE="The saving includes heat from wood. Firewood's cost is not counted."
M = {
 "NULL": (None, None, None, "all"),
 "B1": (BP, "\n                The saving includes heat from wood. Firewood's cost is not counted.", "", "bp"),
 "B2": (BP, "data.saving_sek is not none and data.saving_includes_wood %}", "data.saving_sek is not none %}", "bp"),
 "B3": (BP, NOTE, "The saving includes heat from wood.", "bp"),
 "B4": (BP, "data.saving_sek is not none and data.saving_includes_wood %}", "data.saving_includes_wood %}", "bp"),
 "R3": (BP, "data.saving_sek is not none and data.saving_includes_wood %}", "data.saving_sek is not none and not data.saving_includes_wood %}", "bp"),
 "R11": (BP, "data.saving_sek is not none and data.saving_includes_wood %}", "data.saving_sek is not none or data.saving_includes_wood %}", "bp"),
 "S1": (CC+"sensor.py", '"saving_includes_wood": saving_includes_wood(data),', '"saving_includes_wood": False,', "py"),
 "S2": (CC+"sensor.py", '"saving_includes_wood": saving_includes_wood(data),', '"saving_includes_wood": True,', "py"),
 "N1": (CC+"notifier.py", '"saving_includes_wood": saving_includes_wood(data),', '"saving_includes_wood": False,', "py"),
 "N2": (CC+"notifier.py", '"saving_includes_wood": saving_includes_wood(data),', '"saving_includes_wood": True,', "py"),
 "D1": (CC+"wood_fuel.py", 'return bool((data.get("wood_fuel") or {}).get("show_whatif"))', 'return bool(data.get("wood_fuel"))', "py"),
 "D2": (CC+"wood_fuel.py", 'return bool((data.get("wood_fuel") or {}).get("show_whatif"))', 'return bool((data.get("wood_fuel") or {}).get("ready"))', "py"),
 "L1": (CC+"wood_fuel.py", '    return bool((data.get("wood_fuel") or {}).get("show_whatif"))', '    pass', "py"),
 "C1": (CARD, '? `<div class="receipt-sub receipt-wood-note">${esc(L("savings.wood_note"))}</div>`', '? ``', "card"),
 "C2": (CARD, "const wood = !!(fuel && fuel.show_whatif);", "const wood = true;", "card"),
 "C3": (CARD, "const woodNote = wood\n", "const woodNote = false\n", "card"),
 "R8": (CARD, "}))}</div>${wood\n", "}))}</div>${!wood\n", "card"),
 "R9": (CARD, "const wood = !!(fuel && fuel.show_whatif);", "const wood = !!fuel;", "card"),
 "R10": (CARD, "${receiptHtml(st, rows, cur, wood)}", "${receiptHtml(st, rows, cur)}", "card"),
 "R12": (CARD, '"savings.wood_note": "Sparandet inkluderar värme från ved. Vedens kostnad räknas inte."', '"savings.wood_note": "The saving includes heat from wood. Firewood\'s cost is not counted."', "card"),
}
name = sys.argv[1]; f, old, new, kind = M[name]
wt = W/f"mw_{name}"
if not wt.exists():
    subprocess.run(["git","-C","/home/user/heatpump_optimizer","worktree","add","-q","--detach",str(wt),HEAD],check=True)
if f:
    p = wt/f; s = p.read_text()
    assert s.count(old)==1, (name, s.count(old)); p.write_text(s.replace(old,new))
env = {**os.environ, "PYTHONPATH":"tests/hastub", "PLAYWRIGHT_BROWSERS_PATH":"/opt/pw-browsers"}
cmds = {"bp":[["python3","tests/entities.py"],["/opt/hpo/venv-ha/bin/python","dev/audit/harnesses/r10_sav_receipt_render.py"]],
        "py":[["python3","tests/entities.py"],["python3","tests/features.py"]],
        "card":[["sh","-c","python3 tests/plan_view.py >/dev/null && node tests/card.mjs"],["sh","-c","python3 tests/plan_view.py >/dev/null && node tests/card_browser.mjs"]]}
run = cmds[kind] if kind!="all" else cmds["py"]+cmds["card"]+cmds["bp"][1:]
out = W/"ev/mutants"/f"{name}.txt"
with open(out,"w") as o:
    o.write(f"mutant {name}: {f}: {old!r} -> {new!r}\n")
    for c in run:
        r = subprocess.run(c, cwd=wt, env=env, capture_output=True, text=True)
        txt = r.stdout+r.stderr
        fails = [l for l in txt.splitlines() if ("FAIL" in l or "DEFECT" in l) and not any(t in l for t in ("a3:","a4:","a5:","a10:","a16:"))]
        last = [l for l in txt.splitlines() if l.strip()][-1:] 
        o.write(f"  {' '.join(c)}: rc={r.returncode} last={last}\n")
        for l in fails[:6]: o.write(f"    {l[:300]}\n")
