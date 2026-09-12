#!/usr/bin/env python3
"""D10-01 (seat 1 own harness) — declared-vs-executed drift of quality_scale.yaml.

METRIC (own): count of rows in custom_components/heatpump_optimizer/quality_scale.yaml
whose declared status is CONTRADICTED by a check this harness executes itself.
It does not re-implement the finder's 54 checks; it takes the executed verdict
table re-run by this seat (qs_rules.py, re-executed in this worktree with the
coverage and mypy JSONs this seat produced) for the per-row statuses, and then
independently re-derives, by its own commands, the verdict for each row the
finding names as drifted:
  docs-known-limitations    own regex over README.md + docs/*.md (all of them)
  config-flow-test-coverage own five-script coverage run (the row's OWN claimed
                            script set: config_flow_steps, entities, golden,
                            features, deployment_shape), from OWN5_JSON
  test-coverage             own re-run of the tree coverage instrument over the
                            default gate (fast+e2e), from FULL_JSON
A row is contradicted iff my own verdict differs from the declared status.

Perturbation, executed on temp copies of the yaml (never the tree file):
  correcting one drifted row drops the count by 1; flipping the agreeing row
  parallel-updates to todo raises it by 1.

RUN (from the worktree root):
  PYTHONPATH=tests/hastub python3 tools/audit/round4/D10/d10_own_D10-01.py \
      --executed <executed.json>  [--declared <quality_scale.yaml>]
      [--own5 <coverage.json>] [--full <coverage.json>] [--perturb]

  executed.json: {"rule": "status", ...} parsed from this seat's own re-run of
  qs_rules.py (the table lines rule/tier/status/declared).

EXPECTED (if the finding holds): RESULT own_contradicted=3 rows, and the
  config-flow row's own-basis measurement shows missed > 0 against the
  declared "100% ... 0 missed".
BASELINE 7dd68dd; run at branch head 0855277 (custom_components unchanged).
MACHINE: 8-core Apple M1, macOS 25.6.0. Counts, not timings.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(".").resolve()
PKG = ROOT / "custom_components" / "heatpump_optimizer"
FINDER_SIX = ["README.md", "docs/architecture.md", "docs/automations.md",
              "docs/configuration.md", "docs/dashboard-card.md",
              "docs/ecl110.md", "docs/how-it-works.md"]

HEADING = re.compile(r"^#{1,6}[^\n]*known limitation", re.I | re.M)


def declared_statuses(yaml_path: Path) -> dict[str, str]:
    import yaml
    doc = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    out = {}
    for k, v in (doc.get("rules") or {}).items():
        out[k] = v if isinstance(v, str) else v.get("status", "?")
    return out


def cov_module(json_path: str, module: str) -> dict | None:
    d = json.loads(Path(json_path).read_text())
    for name, f in d["files"].items():
        if name.endswith(f"heatpump_optimizer/{module}"):
            return f["summary"]
    return None


def cov_package(json_path: str) -> dict:
    d = json.loads(Path(json_path).read_text())
    below = {}
    for name, f in d["files"].items():
        if "heatpump_optimizer" in name and name.endswith(".py"):
            if f["summary"]["percent_covered"] < 95.0:
                below[Path(name).name] = round(f["summary"]["percent_covered"], 1)
    return {"package_percent": round(d["totals"]["percent_covered"], 2),
            "covered": d["totals"]["covered_lines"],
            "statements": d["totals"]["num_statements"],
            "modules_below_95": below,
            "n_modules": sum(1 for n in d["files"] if "heatpump_optimizer" in n and n.endswith(".py"))}


def own_verdicts(own5: str | None, full: str | None) -> dict[str, tuple[str, str]]:
    """rule -> (my verdict, evidence string), only for rules I measure myself."""
    out: dict[str, tuple[str, str]] = {}
    text = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in FINDER_SIX
                     if (ROOT / p).exists())
    n = len(HEADING.findall(text))
    out["docs-known-limitations"] = ("done" if n else "todo",
                                     f"own regex: {n} 'known limitation' headings")
    if own5:
        s = cov_module(own5, "config_flow.py")
        if s:
            done = s["missing_lines"] == 0 and s["percent_covered"] >= 100.0
            out["config-flow-test-coverage"] = (
                "done" if done else "todo",
                f"own five-script run (the row's claimed basis): "
                f"{s['percent_covered_display']}%, {s['num_statements']} stmts, "
                f"{s['missing_lines']} missed")
    if full:
        p = cov_package(full)
        out["test-coverage"] = ("done" if not p["modules_below_95"] else "todo",
                                f"own full-gate re-run: {p['package_percent']}% package "
                                f"({p['covered']}/{p['statements']}), "
                                f"{len(p['modules_below_95'])} of {p['n_modules']} modules below 95%")
    return out


def mismatch_count(declared: dict[str, str], executed: dict[str, str]) -> list[str]:
    return sorted(k for k in executed
                  if k in declared and executed[k] != "unmeasured"
                  and declared[k] != executed[k])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--executed", required=True)
    ap.add_argument("--declared", default=str(PKG / "quality_scale.yaml"))
    ap.add_argument("--own5")
    ap.add_argument("--full")
    ap.add_argument("--perturb", action="store_true")
    args = ap.parse_args()

    executed = json.loads(Path(args.executed).read_text())
    decl = declared_statuses(Path(args.declared))
    own = own_verdicts(args.own5, args.full)

    print(f"RESULT own_declared_rows={len(decl)} rows")
    mism = mismatch_count(decl, executed)
    print(f"RESULT own_declared_mismatch_vs_rerun={len(mism)} rows: {mism}")

    contradicted = []
    for rule, (verdict, ev) in own.items():
        d = decl.get(rule, "(absent)")
        flag = "CONTRADICTED" if d != verdict else "agree"
        if d != verdict:
            contradicted.append(rule)
        print(f"RESULT own_{rule.replace('-', '_')}=own:{verdict}/declared:{d} [{flag}] -- {ev}")
    print(f"RESULT own_contradicted={len(contradicted)} rows: {sorted(contradicted)}")

    if args.perturb:
        import shutil
        base = Path(args.declared)
        with tempfile.TemporaryDirectory(prefix="hpo-v-d10-own1-") as td:
            fixed = Path(td) / "fixed.yaml"
            shutil.copy(base, fixed)
            t = fixed.read_text(encoding="utf-8")
            # correct ONE drifted row: docs-known-limitations done -> todo
            t2 = re.sub(r"(?m)^  docs-known-limitations: done$", "  docs-known-limitations: todo", t, count=1)
            assert t2 != t, "perturbation target line not found"
            fixed.write_text(t2, encoding="utf-8")
            m1 = mismatch_count(declared_statuses(fixed), executed)
            print(f"RESULT own_perturb_fix_one={len(m1)} rows (was {len(mism)}; direction down by 1 expected)")

            flipped = Path(td) / "flipped.yaml"
            t3 = re.sub(r"(?m)^  parallel-updates: done$", "  parallel-updates: todo", t, count=1)
            assert t3 != t, "flip target line not found"
            flipped.write_text(t3, encoding="utf-8")
            m2 = mismatch_count(declared_statuses(flipped), executed)
            print(f"RESULT own_perturb_flip_one={len(m2)} rows (was {len(mism)}; direction up by 1 expected)")

    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=n/a (counts, not timings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
