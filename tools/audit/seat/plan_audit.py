#!/usr/bin/env python3
"""P3's two instruments: the move ledger and the round's holdout check.

    python3 tools/audit/seat/plan_audit.py end-to-end --fork SHA [--head REF] [--target 22.7]
    python3 tools/audit/seat/plan_audit.py ledger --plan PLAN.json [--bodies DIR] \\
        --fork SHA --head REF [--tolerance 1.0] [--json OUT]
    python3 tools/audit/seat/plan_audit.py snapshot --ref SHA [--instrument REF] --out FILE
    python3 tools/audit/seat/plan_audit.py compare --fork FILE --stamp FILE [--allow KIND:KEY]...
    python3 tools/audit/seat/plan_audit.py --self-test

R10-FLOW-AUDIT-PLAN. The architect's plan (`plan/r<N>`, `dev/governance/roles/
architect-planner.md`) is only a target if the round can be checked against it
afterwards, so this file is P3's measuring half:

* **The move ledger.** A plan's `moves` name, per group, the scored metrics it
  expects to move and its predicted dS. At the stamp, each merged PR's body
  carries its own `## Architecture score` block (score.py's `report`, copied in
  by the fixer). `ledger` parses those blocks with the parser `end-to-end` uses
  for score.py's own output, reconciles each metric against the plan, and runs
  `score.py --diff <fork> <head>` for the round's end-to-end reading. A metric
  a merged PR moved that no planned move names, a merged group with no body,
  and a dS the sum of the moves does not account for are each refused: a dS no
  planned move explains is `metric-gamed` (`fix-review.md` step 14), not
  banked.
* **The holdout check.** `snapshot` records, for one ref, the five measures the
  score does not contain or must not be traded against: `tests/structure.py`'s
  budget metrics, the archscore gate-only tripwires, a behaviour inventory
  (entities, services, options and the card's pages), the mutation ledger's
  kill rate, and change coupling over the last `--window` first-parent PR
  merges. `compare` fails on any regression. The fork is snapshotted with
  `--instrument <fork>`, so both sides are read by the base's scorer and the
  base's `tests/structure.py`; `--allow structure:<metric>` (or tripwire:) is
  the plan's declared exception for a number the stamp's own ratchet reads
  differently, printed as ALLOWED and never silently dropped.

Neither re-implements an instrument it can call: `end-to-end` runs `score.py`
itself, and `snapshot` imports the instrument tree's own `archscore.vector` and
runs its `tests/structure.py` over the target -- the measuring code is the
instrument's on both sides, so a round cannot lower a number by editing the
measurer. `ARCHSCORE_ABLATE` is refused, because
a gain that appears only without the counters did not happen.

WHAT IT DOES NOT CATCH. A PR body that predates the required block, or whose
score lines were hand-edited (the ledger parses text, not the tree; the
reviewer's `score.py --diff` is the control). A plan with no `moves` at all
(the ledger says so and passes the end-to-end reading only). A behaviour
removed by a finding the plan approved: `compare --allow KIND:KEY` names it,
and the plan's own ADR is the record that it was deliberate. Coupling over a
window shorter than the round's own history (the window is explicit and both
snapshots carry it).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCORE = ROOT / "tools" / "audit" / "archscore" / "score.py"
PKG = "custom_components/heatpump_optimizer"
LEDGER = "tests/mutation_ledger"
TARGET_DS = 22.7

_HEAD = re.compile(r"^Architecture score: dS ([+-]\d+\.\d+) (IMPROVES|NULL|WORSENS)"
                   r"(?: \(inadmissible: (.*)\))?$", re.M)
_TERM = re.compile(r"^  (\w+) (\d+) -> (\d+)(?:  ([+-]\d+\.\d+))?(  \(gate only\))?$", re.M)


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def parse_score(text: str) -> dict:
    """One ``Architecture score`` block, as score.py's report prints it.

    The block is the first `Architecture score:` line and the indented metric
    lines under it. A body that carries none is refused by name: a ledger that
    read absence as "moved nothing" would pass a group that never reported.
    """
    head = _HEAD.search(text)
    if not head:
        raise ValueError("no `Architecture score: dS ...` line in the text")
    terms, gate_only, seen = {}, [], []
    tail = text[head.end():]
    for line in tail.splitlines():
        if not line.startswith("  "):
            if line.strip() == "":
                continue
            break
        m = _TERM.match(line)
        if not m:
            continue
        metric = m[1]
        seen.append(metric)
        if m[5]:
            gate_only.append(metric)
        elif m[4] is not None:
            terms[metric] = float(m[4])
    return {"dS": float(head[1]), "verdict": head[2],
            "rises": [r.strip() for r in (head[3] or "").split(";") if r.strip()],
            "terms": terms, "gate_only": gate_only, "metrics": seen}


def run_end_to_end(fork: str, head: str) -> dict:
    if (ablated := os.environ.get("ARCHSCORE_ABLATE")):
        raise SystemExit(f"ARCHSCORE_ABLATE={ablated}: a gain that appears only without the "
                         f"counters did not happen; unset it and re-run")
    out = subprocess.run([sys.executable, str(SCORE), "--diff", fork, head],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"score.py --diff refused (rc={out.returncode}): {out.stderr.strip()[-400:]}")
    return parse_score(out.stdout)


def read_bodies(directory: Path | None) -> dict:
    """`<group>.md` -> its parsed score block. A body without one is an error,
    not an empty reading."""
    bodies = {}
    if directory is None:
        return bodies
    for path in sorted(Path(directory).glob("*.md")):
        bodies[path.stem] = parse_score(path.read_text())
    return bodies


def reconcile(plan: dict, bodies: dict, end: dict, tolerance: float) -> dict:
    """The plan against the merged bodies against score.py's end-to-end reading.

    Returns ``{rows, failures, warnings, residual, target_met}``. ``rows`` is
    one per (group, metric) either side names, with predicted, merged and the
    difference. A merged metric no planned move names, a merged group with no
    body or no planned move, and a residual larger than ``tolerance`` are
    failures; a planned metric that did not move is a warning (the plan is a
    prediction, and a fixer may have found a sounder route).
    """
    failures, warnings, rows = [], [], []
    by_group = {m.get("group"): m for m in plan.get("moves") or []}
    observed_sum = 0.0
    for group, move in by_group.items():
        if move.get("merged") is False:
            warnings.append(f"ORPHAN move {group} is marked merged:false; the round's plan "
                            f"still names it, so its body is owed before the stamp")
            continue
        body = bodies.get(group)
        if body is None:
            failures.append(f"OWED body {group}: a planned move merged with no "
                            f"`## Architecture score` body at <bodies>/{group}.md")
            continue
        observed_sum += body["dS"]
        planned = move.get("metrics") or {}
        for metric, value in sorted(body["terms"].items()):
            if metric not in planned:
                failures.append(f"UNEXPLAINED metric {group} {metric} {value:+.4f}: no planned "
                                f"move names it")
            else:
                rows.append({"group": group, "metric": metric, "predicted": planned[metric],
                             "merged": value, "diff": round(value - planned[metric], 4)})
        for metric, value in sorted(planned.items()):
            if metric not in body["terms"]:
                warnings.append(f"UNREALISED {group} {metric} {value:+.4f}: predicted, the body "
                                f"reports no change")
        predicted_total = move.get("dS")
        if predicted_total is None:
            predicted_total = round(sum(planned.values()), 4)
        rows.append({"group": group, "metric": "(group dS)", "predicted": predicted_total,
                     "merged": body["dS"], "diff": round(body["dS"] - predicted_total, 4)})
    for group, body in bodies.items():
        if group not in by_group:
            failures.append(f"UNPLANNED group {group}: a merged body with no move in the plan "
                            f"({body['dS']:+.4f})")
    residual = round(end["dS"] - observed_sum, 4)
    if abs(residual) > tolerance:
        failures.append(f"UNEXPLAINED dS {residual:+.4f}: the end-to-end reading is {end['dS']:+.4f} "
                        f"and the merged bodies account for {observed_sum:+.4f} (tolerance {tolerance})")
    if not end.get("admissible", not end["rises"]):
        failures.append("INADMISSIBLE end to end: " + "; ".join(end["rises"]))
    if end["verdict"] == "WORSENS" and not end["rises"]:
        failures.append(f"WORSENS end to end: dS {end['dS']:+.4f}")
    return {"rows": rows, "failures": failures, "warnings": warnings, "residual": residual,
            "observed_sum": round(observed_sum, 4), "end": end,
            "target_met": end["dS"] >= plan.get("target_dS", TARGET_DS)}


def _print_ledger(result: dict) -> None:
    for row in result["rows"]:
        print(f"  {row['group']} {row['metric']}: predicted {row['predicted']:+.4f} "
              f"merged {row['merged']:+.4f} diff {row['diff']:+.4f}")
    end = result["end"]
    print(f"end-to-end dS {end['dS']:+.4f} {end['verdict']}"
          + (f" (inadmissible: {'; '.join(end['rises'])})" if end["rises"] else ""))
    print(f"target {'MET' if result['target_met'] else 'NOT MET'} "
          f"(dS >= {TARGET_DS:+.4f}); residual {result['residual']:+.4f}")
    for warning in result["warnings"]:
        print(f"  WARN {warning}")
    for failure in result["failures"]:
        print(f"  FAIL {failure}")


# --------------------------------------------------------------------- holdouts

def _worktree(ref: str) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="plan-audit-"))
    subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "--detach", "--force", str(tmp), ref],
                   capture_output=True, text=True, check=True)
    return tmp


def _drop_worktree(path: Path) -> None:
    subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(path)],
                   capture_output=True, text=True)
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


def _py(tree: Path, code: str, *args: str) -> str:
    out = subprocess.run([sys.executable, "-c", code, *args], cwd=str(tree),
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"measurement refused in {tree.name}: {out.stderr.strip()[-500:]}")
    return out.stdout


STRUCTURE_CODE = ("import json,sys; sys.path.insert(0,'tests'); import structure; "
                  "print(json.dumps(structure.measure()['metrics'],sort_keys=True))")
VECTOR_CODE = ("import json,sys; sys.path.insert(0,'tools/audit'); from archscore import vector; "
               "print(json.dumps({'vector': vector.measure(sys.argv[1]), "
               "'gate_only': list(vector.GATE_ONLY)},sort_keys=True))")


def structure_metrics(tree: Path, instrument: Path | None = None) -> dict:
    """`tests/structure.py`'s budget metrics for `tree`.

    The measuring *code* is the `instrument` tree's, copied into the throwaway
    worktree before it runs: a round that lowers a number by editing
    `structure.py` would otherwise read as no regression, because the fork's
    snapshot would use the fork's file and the stamp's the lowered one. The
    budgets it reads stay the target's own data, so the metrics are the
    instrument's and the tree under test is the stamp's.
    """
    if instrument is not None and instrument != tree:
        shutil.copyfile(instrument / "tests" / "structure.py", tree / "tests" / "structure.py")
    return json.loads(_py(tree, STRUCTURE_CODE))


def vector_at(target: Path, instrument: Path) -> dict:
    """The whole score vector and the gate-only names, measured by the
    `instrument` tree's own copy -- the base's scorer reads both sides."""
    got = json.loads(_py(instrument, VECTOR_CODE, str(target)))
    metrics = got["vector"]
    return {"vector": metrics, "tripwires": {k: metrics.get(k) for k in got["gate_only"]}}


def behaviour_inventory(tree: Path) -> dict:
    """The user-visible behaviours, as sets keyed by kind.

    `strings.json` is the integration's translation catalogue: every entity
    name under `entity.<platform>`, every service under `services`, every
    options-menu step under `options.step`. The card's pages are the
    `header.tab_*` keys of its English strings. A count alone would miss a
    rename that keeps it, so the sets are compared; a removal is a regression
    unless the plan's ADR names it (`compare --allow`).
    """
    pkg = Path(tree) / PKG
    strings = json.loads((pkg / "strings.json").read_text())
    out = {"entities": [], "services": [], "options": [], "card": []}
    for platform, names in sorted((strings.get("entity") or {}).items()):
        for name in sorted((names or {}).keys() if isinstance(names, dict) else []):
            out["entities"].append(f"entity:{platform}.{name}")
    for name in sorted((strings.get("services") or {}).keys()):
        out["services"].append(f"service:{name}")
    for step in sorted(((strings.get("options") or {}).get("step") or {}).keys()):
        out["options"].append(f"option:{step}")
    card = (pkg / "www" / "heatpump-optimizer-card.js").read_text()
    for tab in sorted(set(re.findall(r'"header\.tab_([a-z0-9_]+)"', card))):
        out["card"].append(f"card:tab:{tab}")
    return {k: sorted(v) for k, v in out.items()}


def mutation_kill(tree: Path) -> dict:
    """The ledger's dispositions: a killed site or a triaged survivor. The rate
    is the share of dispositioned sites a driver kills; the round may add
    either, but a survivor that drives the share down is a held-out regression.
    """
    killed = len(list((Path(tree) / LEDGER / "killed_by").rglob("*.json")))
    triaged = len(list((Path(tree) / LEDGER / "survivor_triage").rglob("*.json")))
    return {"killed": killed, "triaged": triaged,
            "rate": round(killed / (killed + triaged), 4) if killed + triaged else 0.0}


def coupling(ref: str, window: int, repo: Path = ROOT) -> dict:
    """Change coupling from git history: within the last `window` first-parent
    PR merges, how many distinct module pairs changed in the same merge, and
    how many pair occurrences that is per 100 merges. The window is fixed so
    the fork and the stamp read comparable samples of a history that only
    grows.
    """
    merges = 0
    pairs: set[tuple[str, str]] = set()
    occurrences = 0
    for line in git("log", "--first-parent", f"-n{window}", "--format=%H %P", ref, cwd=repo).splitlines():
        parts = line.split()
        if len(parts) != 3:
            continue  # a direct commit on main is not a merged pull request
        sha, parent = parts[0], parts[1]
        merges += 1
        # `--name-status -M`, not `--name-only`: `tests/closure.py`'s census
        # refuses a rename-collapsing `--name-only` diff under RENAME_SITES,
        # because a collapse hides a deleted path from a list the gate scopes
        # on (`closure.py`'s own `changed_between` reads both sides). The
        # question here is module identity, so detection is kept and the
        # destination taken: one rename is one module, never a false pair --
        # `--no-renames` would split it into a deleted plus an added module and
        # count a co-change that no one made.
        changed = []
        for row in git("diff", "--name-status", "-M", parent, sha, "--", PKG, cwd=repo).splitlines():
            path = row.split("\t")[-1]
            if path.endswith(".py"):
                changed.append(path)
        modules = sorted({str(Path(p).relative_to(PKG)) for p in changed})
        if len(modules) < 2:
            continue
        occurrences += len(list(combinations(modules, 2)))
        pairs.update(combinations(modules, 2))
    return {"window": window, "merges": merges, "pairs": len(pairs), "occurrences": occurrences,
            "cochange_per_100": round(100.0 * occurrences / merges, 4) if merges else 0.0}


def compare_snapshots(fork: dict, stamp: dict, allow: set[str]) -> list[str]:
    """Every regression the round's holdouts can see, one line each."""
    bad = []
    for metric, value in sorted(fork["structure"].items()):
        if metric == "recorded_at":
            continue
        now = stamp["structure"].get(metric)
        if now is None:
            bad.append(f"structure {metric}: missing at the stamp (was {value})")
        elif now > value:
            bad.append(f"structure {metric}: {value} -> {now}")
    for metric, value in sorted(fork["tripwires"].items()):
        now = stamp["tripwires"].get(metric)
        if now is None:
            bad.append(f"tripwire {metric}: missing at the stamp (was {value})")
        elif now > value:
            bad.append(f"tripwire {metric}: {value} -> {now}")
    for kind, keys in sorted(fork["behaviour"].items()):
        gone = [k for k in keys if k not in set(stamp["behaviour"].get(kind, []))]
        for key in gone:
            if key not in allow:
                bad.append(f"behaviour {kind}: removed {key}")
    rate, was = stamp["mutation"]["rate"], fork["mutation"]["rate"]
    if rate < was:
        bad.append(f"mutation kill rate: {was} -> {rate}")
    if stamp["coupling"]["cochange_per_100"] > fork["coupling"]["cochange_per_100"]:
        bad.append(f"change coupling: {fork['coupling']['cochange_per_100']} -> "
                   f"{stamp['coupling']['cochange_per_100']} pair-occurrences per 100 merges")
    return bad


def unallowed(bad: list[str], allow: set[str]) -> list[str]:
    """Structure and tripwire regressions the plan did not declare.

    `--allow structure:<metric>` / `--allow tripwire:<metric>` is the declared
    exception: the base's measuring code can flag a number the stamp's own
    ratchet does not (a detector that changed between them), and a round must
    be able to say so with its ADR rather than be stopped by the base's drift.
    It never hides a rise silently -- `compare` prints every allowed line.
    """
    keep = []
    for line in bad:
        kind, _, rest = line.partition(" ")
        metric = rest.split(":", 1)[0]
        if kind in ("structure", "tripwire") and f"{kind}:{metric}" in allow:
            continue
        keep.append(line)
    return keep


def snapshot(ref: str, instrument: str | None) -> dict:
    inst_ref = instrument or ref
    target = _worktree(ref)
    inst = target if inst_ref == ref else _worktree(inst_ref)
    try:
        vec = vector_at(target, inst)
        return {
            "ref": git("rev-parse", ref),
            "instrument": git("rev-parse", inst_ref),
            "structure": structure_metrics(target, inst),
            "vector": vec["vector"],
            "tripwires": vec["tripwires"],
            "behaviour": behaviour_inventory(target),
            "mutation": mutation_kill(target),
            "coupling": coupling(ref, 200),
        }
    finally:
        _drop_worktree(target)
        if inst != target:
            _drop_worktree(inst)


# ------------------------------------------------------------------- self-test

def self_test() -> int:
    checks = failures = 0

    def t(name: str, cond: bool, detail: str = "") -> None:
        nonlocal checks, failures
        checks += 1
        if cond:
            print(f"  ok   {name}")
        else:
            failures += 1
            print(f"  FAIL {name} {detail}")

    # The parser, and the two shapes score.py prints (a term, a gate-only line).
    body = ("## Architecture score\n"
            "Architecture score: dS +3.5000 IMPROVES\n"
            "  hub_solve_writes 41 -> 38  +0.5000\n"
            "  duplication_copies 41 -> 35  +1.0000\n"
            "  shape_copies 4 -> 3  (gate only)\n"
            "  not measured on one side: public_unused\n")
    parsed = parse_score(body)
    t("a score block parses its dS, verdict and two moving metrics",
      parsed["dS"] == 3.5 and parsed["verdict"] == "IMPROVES"
      and parsed["terms"] == {"hub_solve_writes": 0.5, "duplication_copies": 1.0}
      and parsed["gate_only"] == ["shape_copies"], repr(parsed))
    try:
        parse_score("no block here")
        t("a body with no score block is refused", False)
    except ValueError:
        t("a body with no score block is refused", True)

    # The ledger: a plan whose moves explain the bodies passes.
    plan = {"target_dS": 2.0, "moves": [
        {"group": "G1", "metrics": {"hub_solve_writes": 0.5}, "dS": 0.5},
        {"group": "G2", "metrics": {"duplication_copies": 1.0}, "dS": 1.0}]}
    bodies = {
        "G1": {"dS": 0.5, "verdict": "IMPROVES", "rises": [], "terms": {"hub_solve_writes": 0.5},
               "gate_only": [], "metrics": ["hub_solve_writes"]},
        "G2": {"dS": 1.0, "verdict": "IMPROVES", "rises": [], "terms": {"duplication_copies": 1.0},
               "gate_only": [], "metrics": ["duplication_copies"]},
    }
    end = {"dS": 1.5, "verdict": "IMPROVES", "rises": [], "terms": {}, "gate_only": [], "metrics": [], "admissible": True}
    good = reconcile(plan, bodies, end, 0.1)
    t("a plan the merged bodies account for reconciles with no failure",
      good["failures"] == [], "; ".join(good["failures"]))

    # A metric no planned move names is refused -- the null control is the same
    # input with the metric planned, which passes above.
    bad_bodies = {k: {**v, "terms": dict(v["terms"])} for k, v in bodies.items()}
    bad_bodies["G2"]["terms"]["literal_clone_copies"] = 0.75
    unexplained = reconcile(plan, bad_bodies, end, 0.1)
    t("a merged metric no planned move names is refused",
      any("UNEXPLAINED metric G2 literal_clone_copies" in f for f in unexplained["failures"]),
      repr(unexplained["failures"]))
    t("and its flagged run exits non-zero on the same input the passing run exits 0",
      bool(unexplained["failures"]) and not good["failures"])

    # A planned group with no body is owed, never read as "moved nothing".
    owed = reconcile(plan, {"G1": bodies["G1"]}, end, 0.1)
    t("a planned move with no merged body is OWED",
      any("OWED body G2" in f for f in owed["failures"]), repr(owed["failures"]))

    # A body with no planned move is a group the plan never named, refused even
    # though every planned move explains itself.
    unplanned = reconcile(plan, {**bodies, "G3": bodies["G2"]}, {**end, "dS": 2.5}, 0.1)
    t("a merged group the plan never names is refused",
      any("UNPLANNED group G3" in f for f in unplanned["failures"]), repr(unplanned["failures"]))

    # End-to-end inadmissible fails even when every body is explained.
    inad = reconcile(plan, bodies, {**end, "admissible": False, "rises": ["private_cross_module 9 -> 12"]}, 0.1)
    t("an inadmissible end-to-end reading fails the round",
      any("INADMISSIBLE end to end" in f for f in inad["failures"]), repr(inad["failures"]))

    worse = reconcile(plan, bodies, {**end, "dS": 1.5, "verdict": "WORSENS"}, 0.1)
    t("a WORSENS end-to-end reading fails even with no named regression",
      any("WORSENS end to end" in f for f in worse["failures"]), repr(worse["failures"]))

    # A residual larger than the tolerance is a dS no move explains.
    resid = reconcile(plan, bodies, {**end, "dS": 5.0}, 0.1)
    t("a dS the moves do not account for is refused",
      any("UNEXPLAINED dS +3.5000" in f for f in resid["failures"]), repr(resid["failures"]))
    t("and a residual inside the tolerance is not",
      not any("UNEXPLAINED dS" in f for f in reconcile(plan, bodies, end, 1.0)["failures"]))

    # The behaviour inventory, on a tree shaped like the package.
    with tempfile.TemporaryDirectory(prefix="plan-audit-fixture-") as tmp:
        pkg = Path(tmp) / PKG
        (pkg / "www").mkdir(parents=True)
        (pkg / "strings.json").write_text(json.dumps({
            "entity": {"sensor": {"a": {}, "b": {}}, "climate": {"c": {}}},
            "services": {"set_away": {}, "run_optimization": {}},
            "options": {"step": {"init": {}, "advanced": {}}},
        }))
        (pkg / "www" / "heatpump-optimizer-card.js").write_text(
            '"header.tab_plan": "Plan",\n"header.tab_setup": "Setup",\n"away.toggle": "Away",\n')
        inv = behaviour_inventory(Path(tmp))
        t("the inventory reads entities, services, options and the card's pages",
          inv["entities"] == ["entity:climate.c", "entity:sensor.a", "entity:sensor.b"]
          and inv["services"] == ["service:run_optimization", "service:set_away"]
          and inv["options"] == ["option:advanced", "option:init"]
          and inv["card"] == ["card:tab:plan", "card:tab:setup"], repr(inv))
        stamp_inv = {k: list(v) for k, v in inv.items()}
        stamp_inv["card"].remove("card:tab_setup".replace("_", ":", 1))
        snap = {"structure": {"dup": 1}, "tripwires": {"shape_copies": 1},
                "behaviour": inv, "mutation": {"rate": 0.9},
                "coupling": {"cochange_per_100": 10.0}}
        t("a removed card page is a holdout regression",
          compare_snapshots(snap, {**snap, "behaviour": stamp_inv}, set())
          == ["behaviour card: removed card:tab:setup"])
        t("and the plan's approved removal (--allow) suppresses it",
          compare_snapshots(snap, {**snap, "behaviour": stamp_inv}, {"card:tab:setup"}) == [])
        t("a raised structure metric is a regression",
          compare_snapshots(snap, {**snap, "structure": {"dup": 2}}, set()) == ["structure dup: 1 -> 2"])
        t("a raised gate-only tripwire is a regression",
          compare_snapshots(snap, {**snap, "tripwires": {"shape_copies": 2}}, set())
          == ["tripwire shape_copies: 1 -> 2"])
        t("the plan's declared structure exception allows that one rise",
          unallowed(["structure dup: 1 -> 2", "tripwire shape_copies: 1 -> 2"],
                    {"structure:dup"}) == ["tripwire shape_copies: 1 -> 2"])
        t("and an unrelated declaration leaves the rise (the null control)",
          unallowed(["structure dup: 1 -> 2"], {"structure:other"}) == ["structure dup: 1 -> 2"])
        t("a falling mutation kill rate is a regression",
          compare_snapshots(snap, {**snap, "mutation": {"rate": 0.8}}, set())
          == ["mutation kill rate: 0.9 -> 0.8"])
        t("a rising change coupling is a regression",
          compare_snapshots(snap, {**snap, "coupling": {"cochange_per_100": 11.0}}, set())
          == ["change coupling: 10.0 -> 11.0 pair-occurrences per 100 merges"])
        t("the null control: identical snapshots regress on nothing",
          compare_snapshots(snap, {**snap}, set()) == [])

    # The structure metric is the instrument's measuring code over the target's
    # tree: the target's own `structure.py` must not be the one that answers,
    # or a round lowers a number by editing the measurer.
    with tempfile.TemporaryDirectory(prefix="plan-audit-structure-") as tmp:
        tree, inst = Path(tmp) / "stamp", Path(tmp) / "fork"
        for root, word in ((tree, "stamp"), (inst, "fork")):
            (root / "tests").mkdir(parents=True)
            (root / "tests" / "structure.py").write_text(
                f"def measure():\n    return {{'metrics': {{'m': '{word}'}}}}\n")
        # The null control first: the copy the instrument arm makes is
        # deliberate and one-way, so the self-measure runs before it.
        t("a target measured against itself uses its own file (the null control)",
          structure_metrics(tree) == {"m": "stamp"})
        t("the structure metrics are the instrument's code, not the target's",
          structure_metrics(tree, inst) == {"m": "fork"}, repr(structure_metrics(tree, inst)))

    # Change coupling from a real (throwaway) history: the same two modules
    # changing together is coupling, each changing alone is none.
    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_environ, throwaway_git_init
    # The harness owns its git identity for this block (`throwaway_git_environ`,
    # the tree's mechanism for a self-test that drives production code making
    # its own git calls): `coupling()` runs `git` itself, so threading an `env`
    # argument through it would put a test-only parameter on the production
    # signature. Without this the fixture inherits whatever identity the box
    # has, and a box without one fails at the first `git commit` (exit 128).
    with throwaway_git_environ(), tempfile.TemporaryDirectory(prefix="plan-audit-couple-") as tmp:
        repo = Path(tmp)
        throwaway_git_init(repo, "-q", "-b", "main")
        t("the fixture commits under the harness's own identity, not the box's",
          git("var", "GIT_AUTHOR_IDENT", cwd=repo).startswith("t <t@t>"),
          git("var", "GIT_AUTHOR_IDENT", cwd=repo))
        (repo / PKG).mkdir(parents=True)
        (repo / PKG / "a.py").write_text("a = 1\n")
        git("add", "-A", cwd=repo); git("commit", "-qm", "a", cwd=repo)
        (repo / PKG / "b.py").write_text("b = 1\n")
        git("add", "-A", cwd=repo); git("commit", "-qm", "b", cwd=repo)
        git("checkout", "-qb", "side", cwd=repo)
        for name in ("a.py", "b.py"):
            (repo / PKG / name).write_text("x = 2\n")
        git("add", "-A", cwd=repo); git("commit", "-qm", "both", cwd=repo)
        git("checkout", "-q", "main", cwd=repo)
        git("merge", "-q", "--no-ff", "-m", "merge both", "side", cwd=repo)
        coupled = coupling("main", 50, repo)
        t("two modules changed in one merge read as one coupled pair",
          coupled["merges"] == 1 and coupled["pairs"] == 1 and coupled["cochange_per_100"] == 100.0,
          repr(coupled))
        git("checkout", "-qb", "single", "HEAD", cwd=repo)
        (repo / PKG / "c.py").write_text("c = 3\n")
        git("add", "-A", cwd=repo); git("commit", "-qm", "one", cwd=repo)
        git("checkout", "-q", "main", cwd=repo)
        git("merge", "-q", "--no-ff", "-m", "merge one", "single", cwd=repo)
        both = coupling("main", 50, repo)
        t("the null control: a later merge of one module alone lowers the rate",
          both["merges"] == 2 and both["cochange_per_100"] == 50.0, repr(both))
        # The rename arm: `--no-renames` would read this as a.py deleted and
        # d.py added in one merge, a pair nobody made; detection reads one
        # module. The rate therefore falls with the third merge and no pair.
        git("checkout", "-qb", "renamed", "HEAD", cwd=repo)
        git("mv", f"{PKG}/a.py", f"{PKG}/d.py", cwd=repo)
        git("commit", "-qm", "rename a", cwd=repo)
        git("checkout", "-q", "main", cwd=repo)
        git("merge", "-q", "--no-ff", "-m", "merge rename", "renamed", cwd=repo)
        renamed = coupling("main", 50, repo)
        t("a rename alone is one module, so it adds no co-change pair",
          renamed["merges"] == 3 and renamed["cochange_per_100"] == round(100 / 3, 4),
          repr(renamed))

    print(f"plan_audit self-test: {checks} checks, {failures} failed")
    return 1 if failures else 0


# ----------------------------------------------------------------------- main

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    e2e = sub.add_parser("end-to-end")
    e2e.add_argument("--fork", required=True)
    e2e.add_argument("--head", default="HEAD")
    led = sub.add_parser("ledger")
    led.add_argument("--plan", required=True)
    led.add_argument("--bodies")
    led.add_argument("--fork", required=True)
    led.add_argument("--head", required=True)
    led.add_argument("--tolerance", type=float, default=1.0)
    led.add_argument("--json")
    snap = sub.add_parser("snapshot")
    snap.add_argument("--ref", required=True)
    snap.add_argument("--instrument")
    snap.add_argument("--out", required=True)
    cmp_ = sub.add_parser("compare")
    cmp_.add_argument("--fork", required=True)
    cmp_.add_argument("--stamp", required=True)
    cmp_.add_argument("--allow", action="append", default=[])
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.cmd == "end-to-end":
        end = run_end_to_end(args.fork, args.head)
        print(f"end-to-end dS {end['dS']:+.4f} {end['verdict']}")
        for metric, term in sorted(end["terms"].items()):
            print(f"  {metric} {term:+.4f}")
        for metric in end["gate_only"]:
            print(f"  {metric} (gate only)")
        print(f"target {'MET' if end['dS'] >= TARGET_DS else 'NOT MET'} (dS >= {TARGET_DS:+.4f})")
        return 0 if end["verdict"] != "WORSENS" and not end["rises"] else 1
    if args.cmd == "ledger":
        plan = json.loads(Path(args.plan).read_text())
        stale = plan.get("fork")
        if stale and not git("rev-parse", args.fork).startswith(stale):
            raise SystemExit(f"the plan names fork {stale}, the ledger was given {args.fork}")
        end = run_end_to_end(args.fork, args.head)
        result = reconcile(plan, read_bodies(Path(args.bodies) if args.bodies else None),
                           end, args.tolerance)
        _print_ledger(result)
        if args.json:
            Path(args.json).write_text(json.dumps(result, indent=1, sort_keys=True))
        return 1 if result["failures"] else 0
    if args.cmd == "snapshot":
        data = snapshot(args.ref, args.instrument)
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(data, indent=1, sort_keys=True))
        print(f"snapshot {data['ref'][:12]} (instrument {data['instrument'][:12]}) -> {args.out}")
        print(f"  structure {len(data['structure'])} metric(s), tripwires "
              f"{ {k: v for k, v in data['tripwires'].items()} }")
        print(f"  behaviour { {k: len(v) for k, v in data['behaviour'].items()} }, "
              f"mutation {data['mutation']}, coupling {data['coupling']}")
        return 0
    if args.cmd == "compare":
        fork = json.loads(Path(args.fork).read_text())
        stamp = json.loads(Path(args.stamp).read_text())
        if fork["instrument"] != stamp["instrument"]:
            print(f"HOLDOUT FAIL instrument: the fork was read by {fork['instrument'][:12]} and "
                  f"the stamp by {stamp['instrument'][:12]}; one scorer must read both")
            return 1
        bad = compare_snapshots(fork, stamp, set(args.allow))
        allow = set(args.allow)
        for line in bad:
            if line not in unallowed([line], allow):
                print(f"  ALLOWED  {line}")
            else:
                print(f"  REGRESSED {line}")
        bad = unallowed(bad, allow)
        print("HOLDOUT " + ("FAIL" if bad else "PASS"))
        return 1 if bad else 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
