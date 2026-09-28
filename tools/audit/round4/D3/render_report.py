#!/usr/bin/env python3
"""D3 round 4 -- render the prescreened table into REPORT.md's data sections.

    PYTHONPATH=tests/hastub python3 tools/audit/round4/D3/render_report.py > /tmp/d3_tables.md

Reads pool.json and prescreen.json only; executes nothing.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = "custom_components/heatpump_optimizer/"


def main() -> int:
    pool = json.loads((HERE / "pool.json").read_text())
    st = json.loads((HERE / "prescreen.json").read_text())
    muts = st["mutants"]
    base = st["baseline"]

    print("### Baseline of every driver (rc and reported failures on the clean tree)\n")
    print("| script | rc | failed | wall s (provisional, load1 5.2-6.8) | closures.json recorded s |")
    print("|---|---|---|---|---|")
    rec = json.loads((HERE.parents[3] / "tests" / "closures.json").read_text())["recorded"]
    for s, v in sorted(base.items(), key=lambda kv: -kv[1]["seconds"]):
        key = s.split()[0]
        r = rec.get(key, {}).get("seconds", "-")
        print(f"| `{s}` | {v['rc']} | {v['failed']} | {v['seconds']} | {r} |")

    print("\n### The prescreened list\n")
    print("| id | w | operator | file:line | deleted | closure (fast) | scripts run | verdict |")
    print("|---|---|---|---|---|---|---|---|")
    for m in pool["mutants"]:
        r = muts.get(m["id"])
        if not r:
            print(f"| {m['id']} | {m['weight']} | {m['op']} | "
                  f"`{m['file'][len(PKG):]}:{m['line']}` | `{m['old'].strip()[:48]}` | - | - | NOT RUN |")
            continue
        ran = ", ".join(x["script"].replace("tests/", "") for x in r["scripts_run"])
        verdict = "**SURVIVED**" if r["survived"] else f"killed by `{r['killed_by']}`"
        print(f"| {m['id']} | {m['weight']} | {m['op']} | "
              f"`{m['file'][len(PKG):]}:{m['line']}` | `{m['old'].strip()[:48]}` | "
              f"{len(r['closure'])} | {ran} | {verdict} |")

    killers = {}
    for r in muts.values():
        k = r.get("killed_by") or "SURVIVED"
        killers[k] = killers.get(k, 0) + 1
    print("\n### Cheapest killer, by script\n")
    print("| script | mutants it killed first |")
    print("|---|---|")
    for k, n in sorted(killers.items(), key=lambda kv: -kv[1]):
        print(f"| `{k}` | {n} |")
    surv = [r for r in muts.values() if r["survived"]]
    print(f"\nRESULT prescreened={len(muts)} RESULT survivors={len(surv)} "
          f"RESULT survivor_fraction={len(surv) / max(1, len(muts)):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
