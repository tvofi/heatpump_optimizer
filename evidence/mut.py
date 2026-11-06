import subprocess, sys, os, json
W="/home/user/rev.q2OT"; C="custom_components/heatpump_optimizer"; CARD=C+"/www/heatpump-optimizer-card.js"
M = {
 # id: (base sha, file, old, new, tests)
 "M1": ("HEAD", C+"/ledger.py", "calibration = max(1.0, calibration)", "calibration = calibration", ["F"]),
 "M2": ("HEAD", C+"/ledger.py", '"savings_sek": None if old_basis else saved', '"savings_sek": saved', ["F"]),
 "M3": ("HEAD", C+"/notifier.py", '"saving_includes_wood": bool((data.get("wood_fuel") or {}).get("show_whatif"))', '"saving_includes_wood": False', ["F"]),
 "M4": ("HEAD", C+"/coordinator.py", "wood_configured=wood_furnace_on(_ctx_of(self)._config)", "wood_configured=False", ["F"]),
 "M4fork": ("0a7c84fa2", C+"/coordinator.py", "wood_configured=wood_furnace_on(_ctx_of(self)._config)", "wood_configured=False", ["F"]),
 "M5": ("HEAD", CARD, "const woodNote = wood", "const woodNote = false", ["J","B"]),
 "R1_drop_note": ("HEAD", CARD, '}))}</div>${wood\n', '}))}</div>${false\n', ["J","B"]),
 "R2_always": ("HEAD", CARD, '}))}</div>${wood\n', '}))}</div>${true\n', ["J","B"]),
 "R3_callsite_false": ("HEAD", CARD, "${receiptHtml(st, rows, cur, wood)}", "${receiptHtml(st, rows, cur, false)}", ["J","B"]),
 "R4_cond_fuel_only": ("HEAD", CARD, "const wood = !!(fuel && fuel.show_whatif);", "const wood = !!fuel;", ["J","B"]),
 "R5_wrong_key": ("HEAD", CARD, '${esc(L("savings.wood_note"))}</div>`\n        : ""}`', '${esc(L("receipt.saved"))}</div>`\n        : ""}`', ["J","B"]),
 "R6_sv_string": ("HEAD", CARD, '"savings.wood_note": "Sparandet inkluderar värme från ved. Vedens kostnad räknas inte."', '"savings.wood_note": "The saving includes heat from wood. Firewood\'s cost is not counted."', ["J","B"]),
 "NULL": ("HEAD", None, None, None, ["F","J","B"]),
}
T = {"F": "python3 tests/features.py", "J": "python3 tests/plan_view.py >/dev/null && node tests/card.mjs", "B": "PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs"}
mid = sys.argv[1]; base, f, old, new, tests = M[mid]
wt = f"/home/user/mut-{mid}"
subprocess.run(f"cd /home/user/heatpump_optimizer && git worktree remove --force {wt} 2>/dev/null; git worktree add -q --detach {wt} {'622be7c53b760156e2453dacbd1724325212b9e4' if base=='HEAD' else base}", shell=True, check=True)
if f:
    p = os.path.join(wt, f); s = open(p, encoding="utf-8").read()
    n = s.count(old); assert n == 1, (mid, n)
    open(p, "w", encoding="utf-8").write(s.replace(old, new))
out = [f"MUTANT {mid} base={base} file={f} matches=1" if f else f"MUTANT {mid} (null control, no edit)"]
for t in tests:
    r = subprocess.run(f"cd {wt} && export PYTHONPATH=tests/hastub && {T[t]}", shell=True, capture_output=True, text=True)
    fails = [l for l in (r.stdout+r.stderr).splitlines() if "FAIL" in l][:6]
    out.append(f"  {T[t].split('&&')[-1].strip()}: rc={r.returncode}")
    out += ["    "+l[:300] for l in fails]
    open(f"{W}/ev/mut_{mid}_{t}.log","w").write(r.stdout[-20000:]+r.stderr[-20000:])
open(f"{W}/ev/mut_{mid}.txt","w").write("\n".join(out)+"\n"); print("\n".join(out))
subprocess.run(f"cd /home/user/heatpump_optimizer && git worktree remove --force {wt}", shell=True)
