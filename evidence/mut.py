"""Reviewer's own mutant runner: one exact replacement per mutant, in its own detached worktree."""
import subprocess, sys, os, shutil

REPO = "/home/user/heatpump_optimizer"
HEAD = "a258212553e123d735c7eff139a8e347a1a52ea3"
EV = "/tmp/claude-0/ev/mutants"
os.makedirs(EV, exist_ok=True)
BP = "blueprints/automation/notifications.yaml"
SN = "custom_components/heatpump_optimizer/sensor.py"
NT = "custom_components/heatpump_optimizer/notifier.py"
WF = "custom_components/heatpump_optimizer/wood_fuel.py"
CJ = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
ENT = "PYTHONPATH=tests/hastub python3 tests/entities.py"
FEA = "PYTHONPATH=tests/hastub python3 tests/features.py"
CARD = "PYTHONPATH=tests/hastub python3 tests/plan_view.py && node tests/card.mjs"
BROW = "node tests/card_browser.mjs"

MUTANTS = [
    ("NULL", None, None, None, [ENT, CARD]),
    ("R1-bp-guard-drop-wood", BP, "data.saving_sek is not none and data.saving_includes_wood %}",
     "data.saving_sek is not none %}", [ENT]),
    ("R2-bp-guard-drop-saving", BP, "data.saving_sek is not none and data.saving_includes_wood %}",
     "data.saving_includes_wood %}", [ENT]),
    ("R3-bp-guard-negate", BP, "data.saving_sek is not none and data.saving_includes_wood %}",
     "data.saving_sek is not none and not data.saving_includes_wood %}", [ENT]),
    ("R4-bp-text", BP, "Firewood's cost is not counted.", "Firewood is free.", [ENT]),
    ("R5-sensor-false", SN, '"saving_includes_wood": saving_includes_wood(data),', '"saving_includes_wood": False,', [ENT]),
    ("R6-notifier-true", NT, '"saving_includes_wood": saving_includes_wood(data),', '"saving_includes_wood": True,', [FEA]),
    ("R7-def-present-not-configured", WF, 'return bool((data.get("wood_fuel") or {}).get("show_whatif"))',
     'return bool(data.get("wood_fuel"))', [ENT, FEA]),
    ("R8-card-receipt-invert", CJ, "}))}</div>${wood\n", "}))}</div>${!wood\n", [CARD, BROW]),
    ("R9-card-wood-present", CJ, "const wood = !!(fuel && fuel.show_whatif);", "const wood = !!fuel;", [CARD, BROW]),
    ("R10-card-receipt-not-passed", CJ, "${receiptHtml(st, rows, cur, wood)}", "${receiptHtml(st, rows, cur)}", [CARD, BROW]),
]

only = set(sys.argv[1:])
for name, path, old, new, cmds in MUTANTS:
    if only and name not in only:
        continue
    wt = f"/tmp/claude-0/mwt-{name}"
    shutil.rmtree(wt, ignore_errors=True)
    subprocess.run(["git", "-C", REPO, "worktree", "prune"], check=True)
    subprocess.run(["git", "-C", REPO, "worktree", "add", "-q", "--detach", wt, HEAD], check=True)
    out = open(f"{EV}/{name}.log", "w")
    if path:
        p = os.path.join(wt, path)
        src = open(p).read()
        n = src.count(old)
        if n != 1:
            out.write(f"REFUSE pattern occurs {n} times\n"); out.close()
            print(f"{name}: REFUSE count={n}", flush=True)
            continue
        open(p, "w").write(src.replace(old, new))
        out.write(subprocess.run(["git", "-C", wt, "diff"], capture_output=True, text=True).stdout)
    res = []
    for c in cmds:
        r = subprocess.run(c, shell=True, cwd=wt, capture_output=True, text=True)
        lines = (r.stdout + r.stderr).splitlines()
        fails = [l for l in lines if ("FAIL" in l or "✗" in l) and not l.lstrip().startswith(("a5:", "a10:", "hb:"))]
        out.write(f"\n=== {c} rc={r.returncode}\n" + "\n".join(fails[:40]) + "\n--- tail\n" + "\n".join(lines[-5:]) + "\n")
        res.append(f"{c.split()[-1]} rc={r.returncode}")
    out.close()
    print(f"{name}: " + "; ".join(res), flush=True)
    subprocess.run(["git", "-C", REPO, "worktree", "remove", "--force", wt])
