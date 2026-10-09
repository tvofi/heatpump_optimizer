"""The architecture score: a Pareto gate and a weighted log-ratio over the score vector.

The score is a review trigger that asks for a stated reason, never a target a
seat is rewarded for moving. ``gate.py`` is the required check that reads it (R9-EG-A4), and a gain that appears only without the counters did not happen
(``counters.py``).

* Gate: a change is admissible only if no SCORE metric and no gate-only tripwire rises. Every
  metric is a deterministic static count, so the tolerance is 0.
* Score: S = sum_i w_i * log2((ref_i + 1) / (cur_i + 1)). Halving a metric is worth w_i whatever its
  scale, and ``+1`` keeps a metric at its zero target finite. A change's delta-S is
  S(cur) - S(base), and a tripwire has weight 0.
* Weights: ``weights.json``, frozen -- its sha256 is in ``weights.sha256`` and ``tests/arch_score.py``
  refuses a file that does not hash to it. A weight change is a policy change.
  w = log2(1 + defect cost in hours) of the register class the metric guards, 1.0 for a metric that
  guards none.
* Verdict: IMPROVES if admissible and delta-S > 0; NULL if admissible and delta-S == 0; WORSENS
  otherwise (a gate rise, or delta-S < 0).

    python3 tools/audit/archscore/score.py --delta BASE.json HEAD.json
    python3 tools/audit/archscore/score.py --diff BASE_REF [HEAD_REF]       default HEAD_REF: the tree

A vector is ``vector.py``'s output. A metric missing (None) on either side is dropped from that
comparison and listed.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))

from archscore.vector import GATE_ONLY, SCORE_METRICS  # noqa: E402

WEIGHTS_FILE = HERE / "weights.json"
# weights.json names a class's metrics as the prototype did: ``dup_pairs`` was the pair count that
# ``duplication_copies`` (the shared clone census, copies not pairs) replaced.
WEIGHT_KEY = {"dup_pairs": "duplication_copies"}


def weights_hash() -> str:
    return hashlib.sha256(WEIGHTS_FILE.read_bytes()).hexdigest()


def weights(scale: dict | None = None) -> dict:
    spec = json.loads(WEIGHTS_FILE.read_text())
    w = {m: spec["floor"] for m in SCORE_METRICS}
    for cls in spec["classes"].values():
        share = cls["cost_h"] / len(cls["metrics"])
        for m in cls["metrics"]:
            w[WEIGHT_KEY.get(m, m)] = math.log2(1 + share)
    for m, f in (scale or {}).items():
        w[m] *= f
    return w


def term(w: float, ref: float, cur: float) -> float:
    return w * math.log2((ref + 1) / (cur + 1))


def delta(base: dict, cur: dict, w: dict | None = None) -> dict:
    w = w or weights()
    rises, terms, missing = [], {}, []
    for m in (*SCORE_METRICS, *GATE_ONLY):
        b, c = base.get(m), cur.get(m)
        if b is None or c is None:
            missing.append(m)
            continue
        if c > b:
            rises.append(f"{m} {b}->{c}")
        if m in w and (t := term(w[m], b, c)):
            terms[m] = round(t, 4)
    ds = round(sum(terms.values()), 4)
    admissible = not rises
    verdict = "IMPROVES" if admissible and ds > 0 else "NULL" if admissible and ds == 0 else "WORSENS"
    return {"admissible": admissible, "rises": rises, "dS": ds, "terms": terms,
            "missing": missing, "verdict": verdict}


def expected_ok(label: str, verdict: str) -> bool:
    """GOOD -> IMPROVES, BAD -> WORSENS, NULL -> NULL, NEUTRAL -> not IMPROVES (a change the record says
    moved a defect without removing it must not be scored as a gain)."""
    return {"GOOD": verdict == "IMPROVES", "BAD": verdict == "WORSENS", "NULL": verdict == "NULL",
            "NEUTRAL": verdict != "IMPROVES"}[label]


def report(base: dict, cur: dict) -> str:
    d = delta(base, cur)
    lines = [f"Architecture score: dS {d['dS']:+.4f} {d['verdict']}"
             + (" (inadmissible: " + "; ".join(d["rises"]) + ")" if d["rises"] else "")]
    for m in (*SCORE_METRICS, *GATE_ONLY):
        b, c = base.get(m), cur.get(m)
        if b is not None and c is not None and b != c:
            lines.append(f"  {m} {b} -> {c}" + (f"  {d['terms'][m]:+.4f}" if m in d["terms"] else "  (gate only)"))
    if d["missing"]:
        lines.append("  not measured on one side: " + ", ".join(d["missing"]))
    return "\n".join(lines)


def tree_of(ref: str, into: Path) -> Path:
    """The package at git ref ``ref``, extracted under ``into``.

    Read from the tree object, never through ``git archive``: archive honours the ``export-ignore`` and
    ``export-subst`` attributes of the tree it archives, so a head's own ``.gitattributes`` would decide
    which of its files the scorer sees (#2068 round 2). Symlinks and submodules are not extracted."""
    git = ["git", "-C", str(REPO)]
    listing = subprocess.run([*git, "ls-tree", "-r", "-z", ref, "custom_components"],
                             capture_output=True, check=True).stdout
    for entry in filter(None, listing.split(b"\0")):
        meta, path = entry.split(b"\t", 1)
        mode, kind, sha = meta.decode().split()
        if kind != "blob" or mode == "120000":
            continue
        dest = into / path.decode()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(subprocess.run([*git, "cat-file", "blob", sha], capture_output=True, check=True).stdout)
    return into


def main(argv: list[str]) -> int:
    if len(argv) >= 4 and argv[1] == "--delta":
        d = delta(json.loads(Path(argv[2]).read_text()), json.loads(Path(argv[3]).read_text()))
        print(json.dumps(d, indent=1, sort_keys=True))
        return 0
    if len(argv) >= 3 and argv[1] == "--diff":
        from archscore import vector
        with tempfile.TemporaryDirectory(prefix="archscore-ref-") as tmp:
            base = vector.measure(tree_of(argv[2], Path(tmp)))
            if len(argv) > 3:
                head_dir = Path(tmp) / "head"
                head_dir.mkdir()
                head = vector.measure(tree_of(argv[3], head_dir))
            else:
                head = vector.measure(REPO)
        print(report(base, head))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
