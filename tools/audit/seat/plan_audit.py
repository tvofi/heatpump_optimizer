#!/usr/bin/env python3
"""P3's two instruments: the move ledger and the round's holdout check.

    python3 tools/audit/seat/plan_audit.py end-to-end --fork SHA [--head REF] [--target 22.7]
    python3 tools/audit/seat/plan_audit.py ledger --plan PLAN.json [--bodies DIR] \\
        --fork SHA --head REF [--tolerance 1.0] [--json OUT]
    python3 tools/audit/seat/plan_audit.py snapshot --ref SHA [--instrument REF] --out FILE
    python3 tools/audit/seat/plan_audit.py compare --fork FILE --stamp FILE [--allow KIND:KEY]...
    python3 tools/audit/seat/plan_audit.py objective-check --ref SHA --plan PATH --register PATH \\
        [--previous SETTLEMENT.json] [--write]
    python3 tools/audit/seat/plan_audit.py settle --plan PLAN.json --record OBJECTIVE.json \\
        [--bodies DIR] [--json OUT]
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


# ------------------------------------------------------- the objective (0018)
#
# R11-ARCH-OBJECTIVE. Decision 0018's objective ranks the plan's work; the
# score stays the floor `reconcile` and `compare` read. The plan commits to an
# `objective` block in PLAN.json (the grammar is OBJECTIVE_KEYS); `check_block`
# refuses a block that games either number, and `settle` credits a lagging read
# only through a keyed effect. Hours stay `tools/plan/replan.py`'s: the check
# runs it twice at the plan's pin and derives every time figure from the two
# projections, never from the block.

OBJECTIVE_CONFIG = Path("dev/audit/config/objective.json")
BUGCLASSES = Path("dev/audit/config/bugclasses.json")
REPLAN = Path("tools/plan/replan.py")
# 0018 section 2's "target; direction" column: the way each term improves. A
# design choice: objective.json carries no direction, so the self-test pins this
# table's keys to that file's `terms` and an unknown term refuses.
BETTER = {"regret": "down", "operation": "up", "generality": "up", "unowned": "down",
          "escapes": "down", "injected": "down", "product_green": "up", "coverage": "up",
          "unexamined": "down", "first_pass": "up", "lead_time": "down",
          "closure_slip": "down", "tokens_per_change": "down"}
RELATIVE_BAND = {"lead_time": "band_lead_time", "closure_slip": "band_closure_slip",
                 "tokens_per_change": "band_tokens_per_change"}
VERIFIED = ("verified", "weakened")
DIRECTIONS = ("up", "down", "hold", "undecided")
# Each keyed effect, and the terms its HELD line credits.
# Every rank-1 key but `removes` (checked against the judge register), with the
# register its ids must name: derived_rank and check_block both read this table,
# so a rank-1 key cannot be added without a register (#3703 review, item 1).
REGISTERED = {"escapes": ("escape", "the baseline's escapes ledger, ruled `in`"),
              "cards": ("card", "the round's open cards, check_scopes.py --open-cards"),
              "classes": ("class", "bugclasses.json")}
BASELINE = "dev/audit/yardstick/round{}/OBJECTIVE.json"
KEYED_TERMS = {"removes": ("escapes",), "escapes": ("escapes", "unowned"),
               "classes": ("escapes", "injected"), "cards": (), "examined_by": ("unexamined",),
               "injected": ("injected",), "rereport": ("escapes",)}
OBJECTIVE_KEYS = {
    "": {"baseline", "pin", "terms", "groups", "edges", "dispositions"},
    "baseline": {"record", "tree"},
    "pin": {"roster_path", "roster_blob", "start", "durations_blob"},
    "term": {"direction", "basis", "builder"},
    "group": {"rank", "removes", "escapes", "classes", "cards", "examined_by"},
    "edge": {"from", "to", "adr"},
}
_TIME_KEY = re.compile(r"hour|chain|critical|closure|lead|wall|finish|start|eta|date|slip", re.I)
_FRACTION = re.compile(r"(\d+)/(\d+)")


def _grammar(block: dict) -> list[str]:
    """Every key outside OBJECTIVE_KEYS, one line each; a time-shaped key is
    named as authored time, since the projections own every hour."""
    bad = []

    def keys(obj, level: str, where: str) -> None:
        if not isinstance(obj, dict):
            bad.append(f"SHAPE {where or 'objective'}: not an object")
            return
        for key in obj:
            if key not in OBJECTIVE_KEYS[level]:
                kind = "AUTHORED time" if _TIME_KEY.search(key) else "UNKNOWN key"
                bad.append(f"{kind} {where + '.' if where else ''}{key}: the block's grammar "
                           f"is OBJECTIVE_KEYS; hours are replan.py's projections")
    keys(block, "", "")
    for level in ("baseline", "pin"):
        keys(block.get(level, {}), level, level)
    for term, entry in (block.get("terms") or {}).items():
        keys(entry, "term", f"terms.{term}")
    for group, entry in (block.get("groups") or {}).items():
        keys(entry, "group", f"groups.{group}")
    for i, edge in enumerate(block.get("edges") or []):
        keys(edge, "edge", f"edges[{i}]")
    return bad


def derived_rank(entry: dict, bugs: set[str]) -> int:
    """1 when the group carries a layer-1 key (a verified `bug` finding, an
    escape row, an open card or an open class); 2 otherwise."""
    if any(f in bugs for f in entry.get("removes") or []):
        return 1
    return 1 if any(entry.get(kind) for kind in REGISTERED) else 2


def after_closure(name: str, projected: dict) -> set[str]:
    """Every group `name` waits on through `after`, read off a replan.py plan."""
    seen, todo = set(), list((projected.get(name) or {}).get("after") or [])
    while todo:
        cur = todo.pop()
        if cur not in seen:
            seen.add(cur)
            todo.extend((projected.get(cur) or {}).get("after") or [])
    return seen


def kept_in_floor(block: dict, projected: dict) -> set[str]:
    """Projection B's group names: projection A's less every open rank-2 group
    no rank-1 group reaches through `after`. A done group stays, ranked or not:
    A omits the `after` edges to it that the roster still names, and replan.py
    refuses a roster whose edge names no group. Edges are A's, so no roster
    grammar is re-declared here."""
    ranks = {g: e.get("rank") for g, e in (block.get("groups") or {}).items()
             if isinstance(e, dict)}
    reached = set()
    for group, rank in ranks.items():
        if rank == 1:
            reached |= after_closure(group, projected)
    return {g for g, e in projected.items() if e.get("done") or ranks.get(g) != 2 or g in reached}


def reduced_roster(roster: dict, keep: set[str]) -> dict:
    return {**roster, "groups": [g for g in roster.get("groups") or [] if g.get("group") in keep]}


def _hours(later: str, earlier: str) -> float:
    from datetime import datetime
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return round((datetime.strptime(later, fmt) - datetime.strptime(earlier, fmt)).total_seconds()
                 / 3600, 2)


def _rank_pct(values: list[float], pct: int) -> float | None:
    """Nearest-rank percentile; None over no value."""
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, -(-pct * len(ordered) // 100) - 1)]


def projection_record(block: dict, a: dict, b: dict, production: set[str]) -> dict:
    """The derived figures and the pin: never the two plans, and nothing the
    checkout's VERSION writes (`generated.version`, `closure_stamp`)."""
    start = a["generated"]["start"]
    ranks = {g: e.get("rank") for g, e in (block.get("groups") or {}).items()}
    lead = [_hours(g["finish"], start) for name, g in a["groups"].items()
            if name in production and g.get("finish")]
    delay = {}
    for name, rank in sorted(ranks.items()):
        fa, fb = (a["groups"].get(name) or {}).get("finish"), (b["groups"].get(name) or {}).get("finish")
        if rank == 1 and fa and fb:
            delay[name] = _hours(fa, fb)
    return {
        "pin": {**block.get("pin", {}), "caps": a["generated"].get("caps")},
        "production": sorted(production),
        "a": {"critical_path_hours": a["binding"]["critical_path_hours"],
              "wall_hours": a["summary"]["wall_hours"], "closure": a["summary"]["closure"],
              "lead_time_p50_hours": _rank_pct(lead, 50), "lead_time_p90_hours": _rank_pct(lead, 90)},
        "b": {"critical_path_hours": b["binding"]["critical_path_hours"],
              "wall_hours": b["summary"]["wall_hours"], "closure": b["summary"]["closure"],
              "dropped": sorted(set(a["groups"]) - set(b["groups"]))},
        "floor_cost": {
            "critical_path_hours": round(a["binding"]["critical_path_hours"]
                                         - b["binding"]["critical_path_hours"], 2),
            "wall_hours": round(a["summary"]["wall_hours"] - b["summary"]["wall_hours"], 2),
            "delay_hours": delay},
    }


def projection_refusals(block: dict, a: dict, b: dict) -> list[str]:
    """Projection A is the pinned roster, B is exactly its floor reduction."""
    bad = []
    pin = block.get("pin") or {}
    if a["generated"].get("roster_blob") != pin.get("roster_blob"):
        bad.append(f"STALE pin: projection A read roster blob {a['generated'].get('roster_blob')!r}, "
                   f"the plan pins {pin.get('roster_blob')!r}")
    if a["generated"].get("start") != pin.get("start") or b["generated"].get("start") != pin.get("start"):
        bad.append(f"STALE pin: the projections start at {a['generated'].get('start')!r} and "
                   f"{b['generated'].get('start')!r}, the plan pins {pin.get('start')!r}")
    want = kept_in_floor(block, a["groups"])
    for extra in sorted(set(b["groups"]) - want):
        bad.append(f"REDUCED roster keeps {extra}: a rank-2 group no rank-1 group reaches "
                   f"through `after`, so the floor cost reads smaller than it is")
    for gone in sorted(want - set(b["groups"])):
        bad.append(f"REDUCED roster drops {gone}: B is A less the unreached rank-2 groups only")
    return bad


def escape_rows(ledger: str) -> set[str]:
    """The groups an escapes ledger (a TSV under its `#` header) rules `in`."""
    rows = [ln.split("\t") for ln in ledger.splitlines() if ln and not ln.startswith("#")]
    if not rows or "group" not in rows[0] or "ruling" not in rows[0]:
        return set()
    g, r = rows[0].index("group"), rows[0].index("ruling")
    return {row[g] for row in rows[1:] if len(row) > max(g, r) and row[r] == "in"}


def baseline_refusals(plan: dict, baseline: dict, blobs: dict) -> list[str]:
    """The baseline is derived, never the plan's choice: the previous round's
    record at BASELINE, of that round, and the same blob at the plan SHA, at
    any `baseline.tree` and where the plan's branch left main (#3703 review,
    item 2). `blobs` maps each of those reads to its blob id, None if absent."""
    rnd = (plan.get("round") or 0) - 1
    want = BASELINE.format(rnd)
    got = (((plan.get("objective") or {}).get("baseline")) or {}).get("record")
    bad = []
    if got != want:
        bad.append(f"BASELINE {got!r}: the baseline is the previous round's record, {want}")
    if baseline.get("round") != rnd:
        bad.append(f"BASELINE round {baseline.get('round')!r}: {want} must record round {rnd}")
    if blobs.get("plan") is None or len(set(blobs.values())) > 1:
        bad.append(f"BASELINE edited: {want} is not one blob at the plan SHA, its tree and "
                   f"main's merge base ({', '.join(f'{k} {v}' for k, v in sorted(blobs.items()))})")
    return bad


def check_block(plan: dict, register: list[dict], baseline: dict, terms: list[str],
                previous: list[dict] | None, projected: dict, known: dict) -> list[str]:
    """The P3 check on the plan's objective block, one refusal per line.

    `register` is the judge's verdict list, `baseline` the previous round's
    objective record, `terms` objective.json's, `previous` the previous plan's
    settlement lines (None for a first plan), `projected` projection A's
    `groups` and `known` each REGISTERED key's ids.
    """
    block = plan.get("objective")
    if not isinstance(block, dict):
        return ["NO objective block: PLAN.json commits to one (0018, architect-planner.md)"]
    bad = _grammar(block)
    ids = {f.get("id") for f in register}
    bugs = {f["id"] for f in register
            if f.get("verdict") in VERIFIED and f.get("stop_rule_class") == "bug"}
    for row in plan.get("triage") or []:
        if row.get("id") in bugs and row.get("verdict") == "defer" and not row.get("card"):
            bad.append(f"DEFERRED bug {row['id']}: a verified `bug` finding deferred with no card "
                       f"(its lead_time is bought with the round's)")
    stated = block.get("terms") or {}
    for term in terms:
        entry = stated.get(term)
        if not isinstance(entry, dict) or entry.get("direction") not in DIRECTIONS:
            bad.append(f"TERM {term}: no predicted direction, one of {', '.join(DIRECTIONS)}")
            continue
        unread = "value" not in ((baseline.get("terms") or {}).get(term) or {})
        if unread and entry["direction"] != "undecided":
            bad.append(f"NO-READ {term} predicted {entry['direction']!r}: a term NO-READ in the "
                       f"baseline takes only \"undecided\" with its builder")
        if entry["direction"] == "undecided" and unread and not entry.get("builder"):
            bad.append(f"NO-READ {term} undecided with no builder")
        if entry["direction"] != "undecided" and not entry.get("basis"):
            bad.append(f"TERM {term}: a predicted direction with no basis")
    for term in sorted(set(stated) - set(terms)):
        bad.append(f"TERM {term}: not a term of objective.json")
    named = {g.get("group") for g in plan.get("groups") or []}
    entries = block.get("groups") or {}
    for group in sorted(named - set(entries)):
        bad.append(f"RANK {group}: a planned group with no objective entry")
    for group in sorted(set(entries) - named):
        bad.append(f"RANK {group}: an objective entry for no planned group")
    owner: dict[str, str] = {}
    for group, entry in sorted(entries.items()):
        if not isinstance(entry, dict):
            continue
        for fid in entry.get("removes") or []:
            if fid not in ids:
                bad.append(f"UNKNOWN finding {group} {fid}: not in the register")
            elif fid in owner:
                bad.append(f"DOUBLE closure {fid}: {owner[fid]} and {group} both remove it")
            else:
                owner[fid] = group
        for kind, (noun, source) in REGISTERED.items():
            for item in entry.get(kind) or []:
                if item not in (known.get(kind) or set()):
                    bad.append(f"UNKNOWN {noun} {group} {item}: not in {source}")
        want = derived_rank(entry, bugs)
        if entry.get("rank") != want:
            bad.append(f"RANK {group} declares {entry.get('rank')!r}, its keys make it {want}")
        if want == 2 and not entry.get("examined_by"):
            bad.append(f"UNEXAMINED move {group}: a rank-2 group names the finder pass that "
                       f"examines its diff before the close")
    adrs = {m.get("adr") for m in plan.get("moves") or [] if m.get("adr")}
    edges = {(e.get("from"), e.get("to")): e.get("adr") for e in block.get("edges") or []
             if isinstance(e, dict)}
    for group, entry in sorted(entries.items()):
        if not isinstance(entry, dict) or entry.get("rank") != 1:
            continue
        for waits in sorted(after_closure(group, projected)):
            if (entries.get(waits) or {}).get("rank") == 2 and edges.get((group, waits)) not in adrs:
                bad.append(f"RANK edge {group} after {waits}: a rank-1 group waits on a rank-2 "
                           f"group with no ADR among the plan's moves")
    for name, g in sorted(projected.items()):
        if not g.get("done") and name not in entries:
            bad.append(f"UNRANKED open group {name}: projection A schedules it and the plan "
                       f"gives it no rank")
        elif g.get("done") and name in entries:
            bad.append(f"RANKED done group {name}: a done group is kept unranked, and B keeps it")
    dispositions = block.get("dispositions") or {}
    for line in previous or []:
        if line.get("status") == "MISSED" and not dispositions.get(line.get("key")):
            bad.append(f"UNDISPOSED {line.get('key')}: the previous plan MISSED it; name a "
                       f"group or a card")
    return bad


# -------------------------------------------------------------- the settlement

def term_reading(entry: dict | None) -> dict | None:
    """A term's value per enumerator, each as a number or a (k, n) share;
    None when the term is NO-READ."""
    if not entry or "value" not in entry or entry["value"] is None:
        return None
    values = entry["value"] if isinstance(entry["value"], dict) else {"": entry["value"]}
    counts = entry.get("counts") if isinstance(entry.get("counts"), dict) else {"": entry.get("counts")}
    out = {}
    for name, value in values.items():
        share = None
        for k, n in _FRACTION.findall(str(counts.get(name) or "")):
            if int(n) and round(int(k) / int(n), 4) == round(float(value), 4):
                share = (int(k), int(n))
                break
        out[name] = share if share else value
    return out


def moved(term: str, was, now, thresholds: dict) -> str | None:
    """"up", "down" or "tie" beyond 0018's band; None when no band reads it."""
    if term in RELATIVE_BAND:
        band = (thresholds.get(RELATIVE_BAND[term]) or {}).get("value")
        if band is None or not isinstance(was, (int, float)) or not isinstance(now, (int, float)):
            return None
        width = band * abs(was)
    elif isinstance(was, tuple) and isinstance(now, tuple):
        (k1, n1), (k2, n2) = was, now
        p1, p2 = k1 / n1, k2 / n2
        width = 2 * (p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2) ** 0.5
        was, now = p1, p2
    elif isinstance(was, int) and isinstance(now, int) and not isinstance(was, bool):
        width = 2 * (was + now) ** 0.5
    else:
        return None
    if abs(now - was) <= width:
        return "tie"
    return "up" if now > was else "down"


def _keyed(record: dict, kind: str) -> list[dict] | None:
    rows = (record.get("keyed") or {}).get(kind)
    return rows if isinstance(rows, list) else None


def settle(plan: dict, baseline: dict, record: dict, merged: set[str], thresholds: dict,
           production: set[str]) -> list[dict]:
    """One line per prediction: HELD, MISSED, UNDECIDED, NOT-DUE or UNPREDICTED.

    A record of the plan's own round settles the terms and the effects due at
    its close (a removal, a card, an examining pass); cause, re-report and
    escape keys fall due at the next round's close (0018 section 4 link 3), so
    they print NOT-DUE until a record of round + 1 is given. A record carries
    keyed rows under `keyed.<kind>`; a kind with none prints UNDECIDED.
    """
    block = plan.get("objective") or {}
    entries = block.get("groups") or {}
    due_next = record.get("round") == (plan.get("round") or 0) + 1
    lines = []

    def line(key: str, status: str, detail: str, terms=()) -> None:
        lines.append({"key": key, "status": status, "detail": detail, "terms": list(terms)})

    def next_round(key: str, kind: str, hit) -> None:
        terms = KEYED_TERMS[kind]
        if not due_next:
            line(key, "NOT-DUE", "falls due at the next round's close", terms)
        elif (rows := _keyed(record, kind)) is None:
            line(key, "UNDECIDED", f"the record carries no keyed `{kind}` rows", terms)
        else:
            found = [r for r in rows if hit(r)]
            line(key, "MISSED" if found else "HELD", f"{len(found)} keyed row(s) match", terms)

    for group, entry in sorted(entries.items()):
        if not due_next:
            for kind in ("removes", "cards"):
                for item in entry.get(kind) or []:
                    status = "HELD" if group in merged else "MISSED"
                    line(f"{group}:{kind}:{item}", status,
                         "its group merged" if group in merged else "its group did not merge",
                         KEYED_TERMS[kind])
            if entry.get("rank") == 2:
                rows = _keyed(record, "examined_by")
                if rows is None:
                    line(f"{group}:examined_by", "UNDECIDED",
                         "the record carries no keyed `examined_by` rows", KEYED_TERMS["examined_by"])
                else:
                    seen = any(r.get("group") == group for r in rows)
                    line(f"{group}:examined_by", "HELD" if seen else "MISSED",
                         f"examined before the close: {seen}", KEYED_TERMS["examined_by"])
        for fid in entry.get("removes") or []:
            next_round(f"{group}:rereport:{fid}", "rereport", lambda r, f=fid: r.get("finding") == f)
        for row in entry.get("escapes") or []:
            next_round(f"{group}:escapes:{row}", "escapes", lambda r, k=row: r.get("key") == k)
        for cid in entry.get("classes") or []:
            next_round(f"{group}:classes:{cid}", "classes", lambda r, c=cid: r.get("class") == c)
        if group in production:
            next_round(f"{group}:injected", "injected", lambda r, g=group: r.get("group") == g)
    if due_next:
        return lines
    credited = {t for ln in lines if ln["status"] == "HELD" for t in ln["terms"]}
    for term, entry in sorted((block.get("terms") or {}).items()):
        was = term_reading((baseline.get("terms") or {}).get(term))
        now = term_reading((record.get("terms") or {}).get(term))
        if was is None or now is None:
            line(f"term:{term}", "UNDECIDED", "NO-READ on one side")
            continue
        for name in sorted(set(was) & set(now)):
            key = f"term:{term}" + (f":{name}" if name else "")
            move = moved(term, was[name], now[name], thresholds)
            want, better = entry.get("direction"), BETTER.get(term)
            worse = {"up": "down", "down": "up"}.get(better)
            if move is None:
                line(key, "UNDECIDED", "no band reads this term (unset, or no denominator)")
            elif move == better and term not in credited:
                line(key, "UNPREDICTED", f"moved {move} with no HELD keyed effect; not banked")
            elif want in ("up", "down"):
                line(key, "HELD" if move == want else "MISSED", f"moved {move}, predicted {want}")
            elif want == "hold":
                line(key, "MISSED" if move == worse else "HELD", f"moved {move}, predicted hold")
            else:
                line(key, "UNDECIDED", f"moved {move}, predicted undecided")
    return lines


def projection_differs(committed: str | None, rerun: dict) -> list[str]:
    want = json.dumps(rerun, indent=1, sort_keys=True) + "\n"
    if committed is None:
        return ["PROJECTION missing: commit the record `objective-check --write` prints"]
    if committed != want:
        return ["PROJECTION differs: the committed record is not the re-run's bytes at the pin"]
    return []


# ------------------------------------------------- the objective's command line

def _show(ref: str, path: str) -> str:
    return git("show", f"{ref}:{path}") + "\n"


def _json_at(ref: str, path: str):
    return json.loads(_show(ref, path))


def _replan(tree: Path, out: Path, *args: str) -> dict:
    run = subprocess.run([sys.executable, str(tree / REPLAN), "--repo", str(ROOT), *args,
                          "--out", str(out)], cwd=str(tree), capture_output=True, text=True)
    if run.returncode != 0:
        raise SystemExit(f"replan.py refused (rc={run.returncode}): "
                         f"{(run.stderr or run.stdout).strip()[-400:]}")
    return json.loads(out.read_text())


def _blob(ref: str, path: str) -> str | None:
    run = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--verify", "-q", f"{ref}:{path}"],
                         capture_output=True, text=True)
    return run.stdout.strip() if run.returncode == 0 else None


def open_cards(tree: Path, ref: str, rnd: int) -> set[str]:
    """`check_scopes.py --open-cards` at the plan SHA: the cards a group may name."""
    run = subprocess.run([sys.executable, str(tree / "tools/audit/check_scopes.py"), "--repo", str(ROOT),
                          "--ref", ref, "--round", str(rnd), "--open-cards", "--roster-ref", ref],
                         cwd=str(tree), capture_output=True, text=True)
    if run.returncode not in (0, 1):
        raise SystemExit(f"check_scopes.py --open-cards refused (rc={run.returncode}): "
                         f"{(run.stderr or run.stdout).strip()[-400:]}")
    return set(json.loads(run.stdout.strip().splitlines()[-1]).get("open_cards") or [])


def run_projections(tree: Path, ref: str, block: dict, roster: dict) -> tuple[dict, dict]:
    """Projection A (the pinned roster at the plan SHA) and B (A less the
    unreached rank-2 groups), both by replan.py at the plan SHA with the
    pinned start and durations, so a later model or VERSION moves neither."""
    pin = block["pin"]
    with tempfile.TemporaryDirectory(prefix="plan-objective-") as tmp:
        durations = Path(tmp) / "durations.json"
        durations.write_text(git("cat-file", "blob", pin["durations_blob"]) + "\n")
        common = ("--durations", str(durations), "--start", pin["start"])
        a = _replan(tree, Path(tmp) / "a.json", "--roster-ref", ref,
                    "--roster-path", pin["roster_path"], *common)
        # B is named as the round's roster is: roster_lib.roster_round reads
        # the round off the basename (design verdict, item dr2-b).
        floor = Path(tmp) / "floor" / Path(pin["roster_path"]).name
        floor.parent.mkdir()
        floor.write_text(json.dumps(reduced_roster(roster, kept_in_floor(block, a["groups"])),
                                    indent=1))
        b = _replan(tree, Path(tmp) / "b.json", "--roster-file", str(floor), *common)
        return a, b


def production_groups(ref: str, block: dict, roster: dict) -> set[str]:
    """The plan's groups whose roster files touch a product path, by
    `machinery_ratchet.is_product` at the plan SHA (0018: a production merge)."""
    import importlib.util
    with tempfile.TemporaryDirectory(prefix="plan-ratchet-") as tmp:
        path = Path(tmp) / "machinery_ratchet.py"
        path.write_text(_show(ref, "tools/audit/machinery_ratchet.py"))
        spec = importlib.util.spec_from_file_location("plan_audit_ratchet", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    files = {g.get("group"): g.get("files") or [] for g in roster.get("groups") or []}
    return {g for g in block.get("groups") or {} if any(mod.is_product(f) for f in files.get(g, []))}


def objective_check(ref: str, plan_path: str, register_path: str, previous: str | None,
                    write: bool, main: str = "origin/main") -> int:
    plan = _json_at(ref, plan_path)
    block = plan.get("objective")
    bad = check_block(plan, [], {}, [], None, {}, {}) if not isinstance(block, dict) else []
    pin = (block or {}).get("pin") or {}
    if not bad and set(pin) != OBJECTIVE_KEYS["pin"]:
        bad = [f"PIN incomplete: {sorted(OBJECTIVE_KEYS['pin'] - set(pin))}; nothing projects "
               f"without it"]
    if bad:
        for line in bad:
            print(f"  FAIL {line}")
        print("OBJECTIVE FAIL")
        return 1
    register = _json_at(ref, register_path)
    register = register.get("verdicts", []) if isinstance(register, dict) else register
    rnd = plan.get("round") or 0
    path = BASELINE.format(rnd - 1)
    blobs = {"plan": _blob(ref, path),
             "main": _blob(git("merge-base", ref, main), path)}
    if (block.get("baseline") or {}).get("tree"):
        blobs["tree"] = _blob(block["baseline"]["tree"], path)
    baseline = _json_at(ref, path) if blobs["plan"] else {}
    terms = _json_at(ref, str(OBJECTIVE_CONFIG))["terms"]
    ledger = (((baseline.get("terms") or {}).get("escapes") or {}).get("by_hand") or {}).get("ledger")
    roster = _json_at(ref, pin["roster_path"])
    tree = _worktree(ref)
    try:
        known = {"classes": {k for k in _json_at(ref, str(BUGCLASSES)) if not k.startswith("_")},
                 "escapes": escape_rows(_show(ref, ledger)) if ledger else set(),
                 "cards": open_cards(tree, ref, rnd)}
        a, b = run_projections(tree, ref, block, roster)
    finally:
        _drop_worktree(tree)
    prev = json.loads(Path(previous).read_text()) if previous else None
    bad = (baseline_refusals(plan, baseline, blobs)
           + check_block(plan, register, baseline, terms, prev, a["groups"], known)
           + projection_refusals(block, a, b))
    record = projection_record(block, a, b, production_groups(ref, block, roster))
    out = str(Path(plan_path).parent / "PROJECTION.json")
    if write:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
        print(f"projection record -> {out}")
    else:
        try:
            committed = _show(ref, out)
        except subprocess.CalledProcessError:
            committed = None
        bad += projection_differs(committed, record)
    print(f"projection A: critical path {record['a']['critical_path_hours']} h, wall "
          f"{record['a']['wall_hours']} h, closure {record['a']['closure']}, lead time p50/p90 "
          f"{record['a']['lead_time_p50_hours']}/{record['a']['lead_time_p90_hours']} h")
    print(f"floor cost (A less B): critical path {record['floor_cost']['critical_path_hours']} h, "
          f"wall {record['floor_cost']['wall_hours']} h, dropped {len(record['b']['dropped'])}")
    for group, hours in record["floor_cost"]["delay_hours"].items():
        print(f"  rank-1 {group} finishes {hours} h later than on the floor")
    for line in bad:
        print(f"  FAIL {line}")
    print("OBJECTIVE " + ("FAIL" if bad else "PASS"))
    return 1 if bad else 0


def objective_settle(plan_path: str, record_path: str, bodies: str | None, out: str | None) -> int:
    plan = json.loads(Path(plan_path).read_text())
    baseline = json.loads((ROOT / BASELINE.format((plan.get("round") or 0) - 1)).read_text())
    record = json.loads(Path(record_path).read_text())
    projection = json.loads((Path(plan_path).parent / "PROJECTION.json").read_text())
    thresholds = json.loads((ROOT / OBJECTIVE_CONFIG).read_text())["thresholds"]
    merged = set(read_bodies(Path(bodies)).keys()) if bodies else set()
    lines = settle(plan, baseline, record, merged, thresholds, set(projection.get("production") or []))
    for ln in lines:
        print(f"  {ln['status']:<11} {ln['key']}: {ln['detail']}")
    if out:
        Path(out).write_text(json.dumps(lines, indent=1, sort_keys=True) + "\n")
    print(f"settlement: {len(lines)} line(s), HELD "
          f"{sum(ln['status'] == 'HELD' for ln in lines)}, MISSED "
          f"{sum(ln['status'] == 'MISSED' for ln in lines)}")
    return 0


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
    from throwaway_git import IDENTITY, throwaway_git_environ, throwaway_git_init
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
          git("var", "GIT_AUTHOR_IDENT", cwd=repo).startswith(f'{IDENTITY["GIT_AUTHOR_NAME"]} <{IDENTITY["GIT_AUTHOR_EMAIL"]}>'),
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

    # ---- the objective block (R11-ARCH-OBJECTIVE): each planted plan beside
    # its passing twin, the null control, on in-memory dicts (no replan.py run).
    terms = json.loads((ROOT / OBJECTIVE_CONFIG).read_text())["terms"]
    t("BETTER names exactly objective.json's terms (a new term refuses until 0018 gives it "
      "a direction)", sorted(BETTER) == sorted(terms), repr(sorted(set(BETTER) ^ set(terms))))
    register = [{"id": "D1-01", "verdict": "verified", "stop_rule_class": "bug"},
                {"id": "D1-02", "verdict": "weakened", "stop_rule_class": "bug"},
                {"id": "D7-01", "verdict": "verified", "stop_rule_class": "hygiene"}]
    baseline = {"round": 10, "terms": {term: {"no_read": "x", "builder": "B"} for term in terms}}
    baseline["terms"]["first_pass"] = {"value": 0.5, "counts": "first-pass 50/100"}
    when = lambda h: f"2026-11-17T{h:02d}:00:00Z"  # noqa: E731
    proj_a = {"G1": {"after": ["G2"], "done": False, "finish": when(9)},
              "G2": {"after": [], "done": False, "finish": when(4)},
              "G3": {"after": [], "done": False, "start": when(3), "finish": when(6)},
              "OLD": {"after": [], "done": True, "finish": None}}

    def objective_plan() -> dict:
        return {"round": 11, "triage": [{"id": "D1-01", "verdict": "keep"},
                                        {"id": "D1-02", "verdict": "defer", "card": "E11-1"}],
                "groups": [{"group": g} for g in ("G1", "G2", "G3")],
                "moves": [{"group": "G1", "adr": "ADR-1"}, {"group": "G2"}, {"group": "G3"}],
                "objective": {
                    "baseline": {"record": "dev/audit/yardstick/round10/OBJECTIVE.json", "tree": "c0"},
                    "pin": {"roster_path": "r/wave-r11-groups.json", "roster_blob": "b0",
                            "start": when(0), "durations_blob": "d0"},
                    "terms": {**{term: {"direction": "undecided", "builder": "B"} for term in terms},
                              "first_pass": {"direction": "up", "basis": "review clause"}},
                    "groups": {"G1": {"rank": 1, "removes": ["D1-01"]},
                               "G2": {"rank": 2, "removes": ["D7-01"], "examined_by": "D7 pass"},
                               "G3": {"rank": 2, "examined_by": "D3 pass"}},
                    "edges": [{"from": "G1", "to": "G2", "adr": "ADR-1"}]}}

    known = {"classes": {"P1"}, "cards": {"E11-1"}, "escapes": {"G-ESC"}}

    def refused(plan: dict, previous=None, projected=None) -> list[str]:
        return check_block(plan, register, baseline, terms, previous,
                           proj_a if projected is None else projected, known)

    good_plan = objective_plan()
    block_of = lambda plan: json.loads(json.dumps(plan["objective"]))  # noqa: E731
    t("a plan with a sound objective block passes the P3 check (every arm's twin)",
      refused(good_plan) == [], repr(refused(good_plan)))
    t("a plan with no objective block is refused",
      refused({k: v for k, v in good_plan.items() if k != "objective"})[0].startswith("NO objective"))

    def planted(edit) -> list[str]:
        plan = json.loads(json.dumps(good_plan))
        edit(plan)
        return refused(plan)

    def has(lines: list[str], head: str) -> bool:
        return any(line.startswith(head) for line in lines)

    def defer_bug(p):
        p["triage"][1].pop("card")
    t("a verified bug deferred with no card is refused (lead_time bought)",
      has(planted(defer_bug), "DEFERRED bug D1-02"))
    t("the null control: deferring a hygiene finding needs no card",
      not has(planted(lambda p: p["triage"].append({"id": "D7-01", "verdict": "defer"})), "DEFERRED"))
    t("a group claiming an unregistered finding is refused (unexamined dressed as a fix)",
      has(planted(lambda p: p["objective"]["groups"]["G2"]["removes"].append("D9-99")),
          "UNKNOWN finding G2 D9-99"))
    t("a hold predicted on a term NO-READ in the baseline is refused (free credit)",
      has(planted(lambda p: p["objective"]["terms"].__setitem__(
          "escapes", {"direction": "hold", "basis": "x"})), "NO-READ escapes"))
    t("and undecided with no builder is refused, while undecided with one passes (above)",
      has(planted(lambda p: p["objective"]["terms"].__setitem__(
          "escapes", {"direction": "undecided"})), "NO-READ escapes undecided"))
    t("a read term predicted with no basis is refused",
      has(planted(lambda p: p["objective"]["terms"]["first_pass"].pop("basis")),
          "TERM first_pass: a predicted"))
    t("a term objective.json does not name is refused, and a missing one too",
      has(planted(lambda p: p["objective"]["terms"].__setitem__(
          "speed", {"direction": "up", "basis": "x"})), "TERM speed")
      and has(planted(lambda p: p["objective"]["terms"].pop("regret")), "TERM regret"))
    t("one finding closed by two groups is refused (lead_time and tokens counted twice)",
      has(planted(lambda p: p["objective"]["groups"]["G3"].__setitem__("removes", ["D7-01"])),
          "DOUBLE closure D7-01"))
    t("a rank-1 group after a rank-2 group with no ADR edge is refused (dS first)",
      has(planted(lambda p: p["objective"].__setitem__("edges", [])), "RANK edge G1 after G2"))
    t("and an edge whose ADR no move carries is refused alike",
      has(planted(lambda p: p["objective"]["edges"][0].__setitem__("adr", "ADR-9")), "RANK edge"))
    t("a rank-2 group with no examining pass is refused (dS at unexamined's cost)",
      has(planted(lambda p: p["objective"]["groups"]["G3"].pop("examined_by")), "UNEXAMINED move G3"))
    t("a rank the keys contradict is refused both ways",
      has(planted(lambda p: p["objective"]["groups"]["G3"].__setitem__("rank", 1)), "RANK G3 declares 1")
      and has(planted(lambda p: p["objective"]["groups"]["G1"].__setitem__("rank", 2)), "RANK G1 declares 2"))
    t("an unknown class id is refused; a known one makes the group rank 1",
      has(planted(lambda p: p["objective"]["groups"]["G1"].__setitem__("classes", ["P9"])),
          "UNKNOWN class G1 P9")
      and not planted(lambda p: p["objective"]["groups"]["G1"].__setitem__("classes", ["P1"])))
    t("an hours key authored in the block is refused (cost hidden)",
      has(planted(lambda p: p["objective"].__setitem__("critical_path_hours", 40)), "AUTHORED time")
      and has(planted(lambda p: p["objective"]["groups"]["G1"].__setitem__("finish", when(3))),
              "AUTHORED time groups.G1.finish")
      and has(planted(lambda p: p["objective"]["pin"].__setitem__("wall_hours", 9)), "AUTHORED time"))
    t("and any other key outside the grammar is refused by name",
      has(planted(lambda p: p["objective"]["groups"]["G1"].__setitem__("weight", 3)),
          "UNKNOWN key groups.G1.weight"))
    t("a planned group with no objective entry is refused, and an entry for no group",
      has(planted(lambda p: p["groups"].append({"group": "G4"})), "RANK G4: a planned")
      and has(planted(lambda p: p["objective"]["groups"].__setitem__(
          "G5", {"rank": 2, "examined_by": "x"})), "RANK G5: an objective entry"))
    t("an open group projection A schedules and the plan never ranks is refused (dr2-g)",
      has(refused(good_plan, projected={**proj_a, "G6": {"after": [], "done": False}}),
          "UNRANKED open group G6"))
    t("the null control: a done group needs no rank",
      refused(good_plan, projected={**proj_a, "G6": {"after": [], "done": True}}) == [])
    missed = [{"key": "G1:removes:D1-01", "status": "MISSED"}, {"key": "G2:x", "status": "HELD"}]
    t("plan N+1 silent on a MISSED line of plan N is refused",
      refused(good_plan, previous=missed) == ["UNDISPOSED G1:removes:D1-01: the previous plan "
                                             "MISSED it; name a group or a card"])
    t("and passes once it disposes the line; a first plan has no previous settlement",
      refused({**good_plan, "objective": {**good_plan["objective"],
                                          "dispositions": {"G1:removes:D1-01": "card E12-1"}}},
              previous=missed) == []
      and refused(good_plan, previous=None) == [])

    # The projections: B is A less the rank-2 groups no rank-1 group reaches.
    block = good_plan["objective"]
    t("the floor keeps a reached rank-2 group and drops an unreached one",
      kept_in_floor(block, proj_a) == {"G1", "G2", "OLD"}, repr(kept_in_floor(block, proj_a)))
    roster = {"cutover": 1, "groups": [{"group": g} for g in ("G1", "G2", "G3", "OLD")]}
    t("the reduced roster filters entries by name and keeps the rest of the file",
      [g["group"] for g in reduced_roster(roster, {"G1", "OLD"})["groups"]] == ["G1", "OLD"]
      and reduced_roster(roster, set())["cutover"] == 1)

    def plan_of(groups: dict, cp: float, wall: float, blob: str = "b0", version: str = "1.0.0") -> dict:
        return {"generated": {"roster_blob": blob, "start": when(0), "version": version,
                              "caps": {"slots": 20}},
                "binding": {"critical_path_hours": cp},
                "summary": {"wall_hours": wall, "closure": when(10), "closure_stamp": f"v{version}"},
                "groups": groups}
    a = plan_of(proj_a, 9.0, 10.0)
    b = plan_of({k: {**v, "finish": when(7) if k == "G1" else v["finish"]}
                 for k, v in proj_a.items() if k != "G3"}, 7.0, 8.0)
    t("projections at the pin, B the exact reduction, pass",
      projection_refusals(block, a, b) == [], repr(projection_refusals(block, a, b)))
    t("projection A of another roster blob is refused (a stale pin)",
      has(projection_refusals(block, plan_of(proj_a, 9.0, 10.0, blob="b1"), b), "STALE pin"))
    t("a B that keeps an unreached rank-2 group is refused (the floor cost shrunk)",
      has(projection_refusals(block, a, plan_of(proj_a, 9.0, 10.0)), "REDUCED roster keeps G3"))
    record = projection_record(block, a, b, {"G1", "G3"})
    t("lead time reads production groups only",
      projection_record(block, a, b, {"G1"})["a"]["lead_time_p50_hours"] == 9.0)
    t("the record holds the floor cost: A less B, and each rank-1 group's delay",
      record["floor_cost"] == {"critical_path_hours": 2.0, "wall_hours": 2.0,
                               "delay_hours": {"G1": 2.0}}
      and record["b"]["dropped"] == ["G3"], repr(record["floor_cost"]))
    t("lead time runs from the plan's start, the clock 0018 starts at the roster entry (dr2-a)",
      record["a"]["lead_time_p50_hours"] == 6.0 and record["a"]["lead_time_p90_hours"] == 9.0,
      repr(record["a"]))
    t("the same inputs under another VERSION give the same record (dr2-c)",
      projection_record(block, plan_of(proj_a, 9.0, 10.0, version="9.9.9"), b, {"G1", "G3"}) == record)
    t("a committed record equal to the re-run's bytes passes; one edited is refused",
      projection_differs(json.dumps(record, indent=1, sort_keys=True) + "\n", record) == []
      and has(projection_differs(json.dumps({**record, "floor_cost": {}}, indent=1, sort_keys=True)
                                 + "\n", record), "PROJECTION differs")
      and has(projection_differs(None, record), "PROJECTION missing"))

    # Arms the diff's mutants named (prepr step 6d): each pins one line by value.
    shape = planted(lambda p: p["objective"]["terms"].__setitem__("escapes", "down"))
    t("a term entry that is not an object is refused by shape, once, not read key by key",
      has(shape, "SHAPE terms.escapes") and not has(shape, "UNKNOWN key terms.escapes."), repr(shape))
    t("the grammar reaches a term's and an edge's keys",
      has(planted(lambda p: p["objective"]["terms"]["first_pass"].__setitem__("weight", 2)),
          "UNKNOWN key terms.first_pass.weight")
      and has(planted(lambda p: p["objective"]["edges"][0].__setitem__("why", "x")),
              "UNKNOWN key edges[0].why"))
    t("a card alone makes a group rank 1 (no examining pass owed)",
      planted(lambda p: p["objective"]["groups"].__setitem__("G3", {"rank": 1, "cards": ["E11-1"]})) == [])
    # #3703 review item 1: every rank-1 key names a registered id, or a string ranks a group 1.
    for kind, item in (("cards", "NO-SUCH-CARD"), ("escapes", "NO-SUCH-ROW"), ("classes", "P9")):
        lines = planted(lambda p, k=kind, i=item: p["objective"]["groups"].__setitem__(
            "G3", {"rank": 1, k: [i]}))
        t(f"a rank-1 `{kind}` id no register holds is refused by name",
          lines == [f"UNKNOWN {REGISTERED[kind][0]} G3 {item}: not in {REGISTERED[kind][1]}"], repr(lines))
    t("an escape row ruled `in` makes a group rank 1",
      planted(lambda p: p["objective"]["groups"].__setitem__("G3", {"rank": 1, "escapes": ["G-ESC"]})) == [])
    t("every rank-1 key derived_rank reads is a REGISTERED key, checked against its register",
      all(derived_rank({kind: ["x"]}, set()) == 1 for kind in REGISTERED)
      and derived_rank({"removes": ["D7-01"], "examined_by": "x"}, set()) == 2)
    ledger = ("# header\ngroup\tpr\truling\nG-ESC\t1\tin\nG-OUT\t-\tout\nshort\n")
    t("the escapes ledger yields its `in` rows' groups; a ledger with no header yields none",
      escape_rows(ledger) == {"G-ESC"} and escape_rows("G-ESC\t1\tin\n") == set())
    b10 = {"round": 10}
    same = {"plan": "x1", "tree": "x1", "main": "x1"}
    t("the baseline is the previous round's record, one blob everywhere: passes",
      baseline_refusals(good_plan, b10, same) == [])
    t("a baseline path the plan chose is refused (#3703 review item 2)",
      has(baseline_refusals({**good_plan, "objective": {**good_plan["objective"], "baseline": {
          "record": "dev/audit/rounds/round11/PLAN/doctored.json"}}}, b10, same), "BASELINE 'dev/audit/rounds"))
    t("a record of another round is refused",
      baseline_refusals(good_plan, {"round": 9}, same)
      == ["BASELINE round 9: dev/audit/yardstick/round10/OBJECTIVE.json must record round 10"])
    t("a record edited on the plan's branch, or at its tree, is refused; an absent one too",
      has(baseline_refusals(good_plan, b10, {**same, "plan": "x2"}), "BASELINE edited")
      and has(baseline_refusals(good_plan, b10, {**same, "tree": "x2"}), "BASELINE edited")
      and has(baseline_refusals(good_plan, b10, {"plan": None, "main": None}), "BASELINE edited"))
    t("a ranked done group is refused by name (#3703 review item 4)",
      refused({**good_plan, "groups": good_plan["groups"] + [{"group": "OLD"}],
               "objective": {**block_of(good_plan), "groups": {**block_of(good_plan)["groups"],
                                                               "OLD": {"rank": 2, "examined_by": "x"}}}})
      == ["RANKED done group OLD: a done group is kept unranked, and B keeps it"])
    t("and the floor keeps a done group whatever its rank",
      "OLD" in kept_in_floor({"groups": {"OLD": {"rank": 2}}}, proj_a))
    t("an objective entry that is not an object is refused by shape and read no further",
      has(planted(lambda p: p["objective"]["groups"].__setitem__("G3", "x")), "SHAPE groups.G3"))
    t("a rank-2 group waiting on a rank-2 group owes no edge",
      refused(good_plan, projected={**proj_a, "G3": {**proj_a["G3"], "after": ["G2"]}}) == [])
    t("a rank-1 group waiting on a rank-1 group owes no edge",
      refused({**good_plan, "objective": {**block_of(good_plan), "groups": {
          **block_of(good_plan)["groups"], "G3": {"rank": 1, "cards": ["E11-1"]}}}},
              projected={**proj_a, "G1": {**proj_a["G1"], "after": ["G2", "G3"]}}) == [])
    two = {"groups": {"G1": {"rank": 1}, "G3": {"rank": 2}, "G4": {"rank": 2}}}
    t("the floor drops a rank-2 group only another rank-2 group reaches",
      kept_in_floor(two, {**proj_a, "G3": {"after": ["G4"]}, "G4": {"after": []}})
      == {"G1", "G2", "OLD"})
    t("the rank edge reads the whole `after` closure, not the first hop",
      has(refused(good_plan, projected={**proj_a, "G2": {**proj_a["G2"], "after": ["G3"]}}),
          "RANK edge G1 after G3"))
    t("hours are seconds over 3600, to the hundredth",
      _hours("2026-11-21T04:00:00Z", when(0)) == 100.0
      and _hours(when(1), "2026-11-17T00:00:20Z") == round(3580 / 3600, 2))
    t("a percentile over no value is None, not an index error", _rank_pct([], 50) is None)
    fine = projection_record(block, plan_of(proj_a, 9.125, 10.0), plan_of(proj_a, 7.0, 8.004), set())
    t("the floor cost is rounded to the hundredth",
      fine["floor_cost"]["critical_path_hours"] == 2.12 and fine["floor_cost"]["wall_hours"] == 2.0,
      repr(fine["floor_cost"]))
    late = plan_of({k: v for k, v in proj_a.items() if k != "G3"}, 7.0, 8.0)
    late["generated"]["start"] = when(1)
    t("a projection started at another instant than the pin is refused",
      has(projection_refusals(block, a, late), "STALE pin: the projections start"))
    t("a B missing a group the floor keeps is refused",
      has(projection_refusals(block, a, plan_of({k: v for k, v in proj_a.items() if k not in ("G3", "G2")},
                                                7.0, 8.0)), "REDUCED roster drops G2"))

    # The settlement: only a HELD keyed effect is credit.
    thresholds = {"band_lead_time": {"value": None}}
    base10 = {"round": 10, "terms": {**baseline["terms"], "escapes": {"value": 20}}}
    rec11 = {"round": 11, "terms": {**baseline["terms"], "escapes": {"value": 2}}}
    sp = json.loads(json.dumps(good_plan))
    sp["objective"]["terms"]["escapes"] = {"direction": "down", "basis": "G1 removes D1-01"}
    status = lambda lines, key: next((ln["status"] for ln in lines if ln["key"] == key), None)  # noqa: E731
    held = settle(sp, base10, rec11, {"G1", "G2", "G3"}, thresholds, {"G1"})
    t("a term read on both sides, moved as predicted, with its keyed effect HELD: HELD",
      status(held, "term:escapes") == "HELD" and status(held, "G1:removes:D1-01") == "HELD",
      repr(held))
    t("a term NO-READ on one side settles UNDECIDED, never HELD",
      status(settle(sp, baseline, rec11, {"G1"}, thresholds, set()), "term:escapes") == "UNDECIDED")
    unpredicted = settle(sp, base10, rec11, set(), thresholds, set())
    t("a term that improved with no HELD keyed effect is UNPREDICTED, not banked",
      status(unpredicted, "term:escapes") == "UNPREDICTED"
      and status(unpredicted, "G1:removes:D1-01") == "MISSED", repr(unpredicted))
    flipped = {**rec11, "terms": {**rec11["terms"], "escapes": {"value": 40}}}
    diff = [x for x, y in zip(held, settle(sp, base10, flipped, {"G1", "G2", "G3"}, thresholds, {"G1"}))
            if x != y]
    t("perturbation: one record value flipped flips exactly one settlement line",
      len(diff) == 1 and diff[0]["key"] == "term:escapes", repr(diff))
    t("a share settles on its counts' band; a tie inside it is no move",
      status(settle(good_plan, baseline, {**rec11, "terms": {**rec11["terms"], "first_pass": {
          "value": 0.9, "counts": "first-pass 90/100"}}}, set(), thresholds, set()),
          "term:first_pass") == "UNPREDICTED"
      and moved("first_pass", (50, 100), (55, 100), thresholds) == "tie")
    t("a relative band left unset by the owner is UNDECIDED",
      moved("lead_time", 10.0, 2.0, thresholds) is None
      and moved("lead_time", 10.0, 2.0, {"band_lead_time": {"value": 0.2}}) == "down")
    t("cause, re-report and escape keys are NOT-DUE at the plan's own close",
      status(held, "G1:injected") == "NOT-DUE" and status(held, "G1:rereport:D1-01") == "NOT-DUE")
    nxt = {"round": 12, "terms": {}}
    t("at the next close they settle on keyed rows, and with none they are UNDECIDED",
      status(settle(good_plan, baseline, nxt, set(), thresholds, {"G1"}), "G1:injected") == "UNDECIDED"
      and status(settle(good_plan, baseline, {**nxt, "keyed": {"injected": [{"group": "G1"}]}},
                        set(), thresholds, {"G1"}), "G1:injected") == "MISSED"
      and status(settle(good_plan, baseline, {**nxt, "keyed": {"injected": [{"group": "G9"}]}},
                        set(), thresholds, {"G1"}), "G1:injected") == "HELD")

    # #3703 review item 3: each settlement status choice, pinned by value.
    t("perturbation: the flipped line's status flips, HELD to MISSED (a move against `down`)",
      [d["status"] for d in diff] == ["HELD"]
      and status(settle(sp, base10, flipped, {"G1", "G2", "G3"}, thresholds, {"G1"}),
                 "term:escapes") == "MISSED")
    up = json.loads(json.dumps(sp))
    up["objective"]["terms"]["escapes"]["direction"] = "up"
    t("a move the other way than an `up` prediction is MISSED",
      status(settle(up, base10, rec11, {"G1"}, thresholds, {"G1"}), "term:escapes") == "MISSED")
    hold = json.loads(json.dumps(sp))
    hold["objective"]["terms"]["escapes"]["direction"] = "hold"
    tie = {**rec11, "terms": {**rec11["terms"], "escapes": {"value": 22}}}
    t("`hold` settles MISSED on a worse move, HELD on a tie and on a credited better move",
      status(settle(hold, base10, flipped, set(), thresholds, set()), "term:escapes") == "MISSED"
      and status(settle(hold, base10, tie, set(), thresholds, set()), "term:escapes") == "HELD"
      and status(settle(hold, base10, rec11, {"G1"}, thresholds, set()), "term:escapes") == "HELD")
    und = json.loads(json.dumps(sp))
    und["objective"]["terms"]["escapes"] = {"direction": "undecided", "builder": "B"}
    t("`undecided` on a read term settles UNDECIDED, whichever way it moved",
      status(settle(und, base10, flipped, set(), thresholds, set()), "term:escapes") == "UNDECIDED")
    lt = json.loads(json.dumps(sp))
    lt["objective"]["terms"]["lead_time"] = {"direction": "down", "basis": "x"}
    lead = {"lead_time": {"value": 10.0}}
    t("a term no band reads settles UNDECIDED, named so",
      [ln["detail"] for ln in settle(lt, {**base10, "terms": lead},
                                     {**rec11, "terms": {"lead_time": {"value": 2.0}}}, set(),
                                     thresholds, set()) if ln["key"] == "term:lead_time"]
      == ["no band reads this term (unset, or no denominator)"])
    t("only a rank-2 group owes an examining pass: UNDECIDED with no rows",
      status(held, "G2:examined_by") == "UNDECIDED" and status(held, "G1:examined_by") is None)
    seen = settle(sp, base10, {**rec11, "keyed": {"examined_by": [{"group": "G2"}]}}, set(),
                  thresholds, set())
    t("and with rows, HELD where a row names the group, MISSED where none does",
      status(seen, "G2:examined_by") == "HELD" and status(seen, "G3:examined_by") == "MISSED")
    ek = json.loads(json.dumps(good_plan))
    ek["objective"]["groups"]["G1"].update({"escapes": ["G-ESC"], "classes": ["P1"]})
    at12 = lambda keyed: settle(ek, baseline, {**nxt, "keyed": keyed}, set(), thresholds, set())  # noqa: E731
    t("escape and class keys settle at the next close on their own rows",
      status(at12({"escapes": [{"key": "G-ESC"}], "classes": [{"class": "P9"}]}), "G1:escapes:G-ESC")
      == "MISSED"
      and status(at12({"escapes": [], "classes": [{"class": "P1"}]}), "G1:classes:P1") == "MISSED"
      and status(at12({"escapes": [], "classes": []}), "G1:classes:P1") == "HELD"
      and status(at12({}), "G1:escapes:G-ESC") == "UNDECIDED")
    t("the next close settles no term and no own-close effect",
      not [ln for ln in at12({}) if ln["key"].startswith("term:") or ":examined_by" in ln["key"]])
    t("only a production group owes an `injected` line",
      status(held, "G2:injected") is None)
    t("a plan with no round is round 0, so a round-1 record is its next close",
      status(settle({k: v for k, v in good_plan.items() if k != "round"}, baseline, {"round": 1},
                    set(), thresholds, {"G1"}), "G1:injected") == "UNDECIDED")
    t("a share reads off its counts to four places; a zero denominator is no share",
      term_reading({"value": 0.3333, "counts": "1/3"}) == {"": (1, 3)}
      and term_reading({"value": 0.2, "counts": "1/3 then 1/5"}) == {"": (1, 5)}
      and term_reading({"value": 0.5, "counts": "0/0"}) == {"": 0.5}
      and term_reading({"value": None}) is None)
    t("a count's band is twice the root of the two counts",
      moved("escapes", 20, 32, thresholds) == "tie" and moved("escapes", 20, 36, thresholds) == "up"
      and moved("escapes", 40, 20, thresholds) == "down")
    t("a share's band is twice the pooled standard error",
      moved("first_pass", (50, 100), (65, 100), thresholds) == "up"
      and moved("first_pass", (50, 100), (63, 100), thresholds) == "tie")
    t("a value that is neither a count nor a share has no band",
      moved("escapes", 2.5, 9.0, thresholds) is None and moved("escapes", True, 9, thresholds) is None)

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
    obj = sub.add_parser("objective-check")
    obj.add_argument("--ref", required=True, help="the plan commit; every input is read at it")
    obj.add_argument("--plan", required=True)
    obj.add_argument("--register", required=True)
    obj.add_argument("--previous", help="the previous plan's `settle --json` lines")
    obj.add_argument("--write", action="store_true", help="write PROJECTION.json beside --plan")
    obj.add_argument("--main", default="origin/main",
                     help="main's ref; the baseline must be the blob the plan's branch left it at")
    stl = sub.add_parser("settle")
    stl.add_argument("--plan", required=True)
    stl.add_argument("--record", required=True)
    stl.add_argument("--bodies")
    stl.add_argument("--json")
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
    if args.cmd == "objective-check":
        return objective_check(args.ref, args.plan, args.register, args.previous, args.write,
                               args.main)
    if args.cmd == "settle":
        return objective_settle(args.plan, args.record, args.bodies, args.json)
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
