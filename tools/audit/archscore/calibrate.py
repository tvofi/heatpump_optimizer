"""The calibration: every labelled case classified, and the classification pinned.

    python3 tools/audit/archscore/calibrate.py                 live planted + red-team, stored corpus; exit 0 iff
                                                               every verdict equals calibration/expected.json
    python3 tools/audit/archscore/calibrate.py --record        write expected.json from this run, listing each change
    python3 tools/audit/archscore/calibrate.py --measure-corpus   re-measure the corpus trees from git history
    python3 tools/audit/archscore/calibrate.py --jobs N        worker processes (default min(4, cpus))
    python3 tools/audit/archscore/calibrate.py --stored-only | --only ID,ID   subsets, for development

Three sets, 103 labelled cases and the red-team attempts:

  corpus   45 commits of main's history, each labelled GOOD / BAD / NEUTRAL from a source that is not a
           metric (an RCA, a probe-confirmed review verdict, an issue, a PR body, an owner decision; the
           quote is in ``calibration/corpus.tsv``). Both sides of each commit are STORED vectors
           (``calibration/corpus_vectors.json``): the trees are history, and re-measuring ~90 of them costs minutes.
           ``--measure-corpus`` re-derives them.
  planted  58 scripted edits of the pinned tree (``planted/``), measured LIVE on every run: this is what
           notices a metric change.
  redteam  the attempts to raise the score without improving the architecture, measured live.

``expected.json`` pins each case's VERDICT and its admissibility, misses included: a case the score gets
wrong stays recorded as wrong, and a metric change that turns any verdict (even to the right one) fails
until ``--record`` makes the change a diff a reviewer reads. The pre-study's acceptance bar was that every
case classifies correctly; it was not met and is not claimed -- see the totals ``--record`` prints.
"""
from __future__ import annotations

import csv
import json
import multiprocessing
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE / "planted"))

from archscore import score, vector  # noqa: E402

CORPUS = HERE / "calibration" / "corpus.tsv"
VECTORS = HERE / "calibration" / "corpus_vectors.json"
EXPECTED = HERE / "calibration" / "expected.json"


def _measure_case(args: tuple) -> tuple[str, dict]:
    case_id, pin = args
    import cases
    case = next(c for c in cases.cases() if c["id"] == case_id)
    with tempfile.TemporaryDirectory(prefix="archscore-case-") as tmp:
        tree = cases.build(case, Path(pin), Path(tmp) / "tree")
        return case_id, vector.measure(tree)


def live_vectors(jobs: int, only: set[str] | None = None) -> dict[str, dict]:
    """The pin's vector (``_base``) and every planted / red-team case's, measured now."""
    import cases
    ids = [c["id"] for c in cases.cases() if only is None or c["id"] in only]
    with tempfile.TemporaryDirectory(prefix="archscore-pin-") as tmp:
        pin = cases.extract_pin(Path(tmp))
        base_vec = vector.measure(pin)
        work = [(i, str(pin)) for i in ids]
        if jobs > 1:
            with multiprocessing.get_context("spawn").Pool(jobs) as pool:
                done = dict(pool.imap_unordered(_measure_case, work))
        else:
            done = dict(map(_measure_case, work))
    done[cases.BASE] = base_vec
    return done


def corpus_cases() -> list[dict]:
    out = []
    stored = json.loads(VECTORS.read_text())
    with open(CORPUS) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            out.append({"id": r["sha"], "set": "corpus", "label": r["label"], "desc": r["description"],
                        "base": stored[r["parent"]], "cur": stored[r["sha"]]})
    return out


def collect(only_corpus: bool, jobs: int, only: set[str] | None = None) -> list[dict]:
    """Every case with both sides' vectors: stored for the corpus, measured now for the rest."""
    import cases
    out = corpus_cases()
    if not only_corpus:
        vecs = live_vectors(jobs, only)
        for c in cases.cases():
            if only is None or c["id"] in only:
                out.append({"id": c["id"], "set": "redteam" if c["id"].startswith("rt_") else "planted",
                            "label": c["label"], "desc": c["desc"], "base": vecs[c["base"]], "cur": vecs[c["id"]]})
    return out


def classify(collected: list[dict], w: dict | None = None) -> list[dict]:
    return [{**{k: c[k] for k in ("id", "set", "label", "desc")}, **score.delta(c["base"], c["cur"], w)}
            for c in collected]


def sensitivity(collected: list[dict]) -> dict[str, list[str]]:
    """Cases whose VERDICT moves when one weight is halved or doubled, or all weights are equal.
    Empty lists mean the classification is decided by the gate and the signs, and the weights only
    set magnitude."""
    base = {r["id"]: r["verdict"] for r in classify(collected)}
    w0 = score.weights()
    moved = {}
    for m in w0:
        for f in (0.5, 2.0):
            rows = classify(collected, score.weights({m: f}))
            moved[f"{m} x{f}"] = [r["id"] for r in rows if r["verdict"] != base[r["id"]]]
    rows = classify(collected, {m: 1.0 for m in w0})
    moved["all weights equal"] = [r["id"] for r in rows if r["verdict"] != base[r["id"]]]
    return moved


def pinned(rows: list[dict], collected: list[dict]) -> dict:
    """What ``expected.json`` records: each case's verdict and admissibility, and the weight
    perturbations that move any verdict (``_sensitivity``; none is the recorded state)."""
    doc = {r["id"]: {"set": r["set"], "label": r["label"], "verdict": r["verdict"],
                     "admissible": r["admissible"]} for r in rows}
    doc["_sensitivity"] = {k: v for k, v in sensitivity(collected).items() if v}
    return doc


def summary(rows: list[dict]) -> list[str]:
    lines = []
    for st in ("planted", "corpus"):
        for lab in ("GOOD", "BAD", "NULL", "NEUTRAL"):
            sub = [r for r in rows if r["label"] == lab and r["set"] == st]
            if sub:
                ok = [r for r in sub if score.expected_ok(lab, r["verdict"])]
                blind = sum(1 for r in sub if r not in ok and r["verdict"] == "NULL")
                lines.append(f"  {st:8} {lab:8} {len(ok):>3}/{len(sub):<3} blind {blind:>2}  "
                             f"wrong-way {len(sub) - len(ok) - blind:>2}")
    labelled = [r for r in rows if r["set"] != "redteam"]
    right = sum(score.expected_ok(r["label"], r["verdict"]) for r in labelled)
    lines.append(f"  CALIBRATION {right}/{len(labelled)} labelled cases classify as their label says")
    games = [r for r in rows if r["set"] == "redteam" and r["label"] == "GAME"]
    lines.append(f"  RED TEAM {sum(r['verdict'] != 'IMPROVES' for r in games)}/{len(games)} attempts read NULL or "
                 f"inadmissible; IMPROVES: {', '.join(r['id'] for r in games if r['verdict'] == 'IMPROVES') or 'none'}")
    known = [r for r in rows if r["set"] == "redteam" and r["label"] == "KNOWN-OPEN"]
    if known:
        lines.append(f"  KNOWN-OPEN {len(known)} attempts the counters do not close (ABOUT.md, 'Interleaved junk'); IMPROVES: "
                     f"{', '.join(r['id'] for r in known if r['verdict'] == 'IMPROVES') or 'none (a class fix? re-record)'}")
    return lines


def measure_corpus(jobs: int) -> None:
    shas = set()
    with open(CORPUS) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            shas |= {r["sha"], r["parent"]}
    done = {}
    with multiprocessing.get_context("spawn").Pool(jobs) as pool:
        for sha, vec in pool.imap_unordered(_measure_sha, sorted(shas)):
            done[sha] = vec
            print(sha, "ok" if not any(k.startswith("_") and k.endswith("_error") for k in vec) else "ERRORS", flush=True)
    VECTORS.write_text(json.dumps(done, sort_keys=True, indent=0, separators=(",", ": ")) + "\n")


def _measure_sha(sha: str) -> tuple[str, dict]:
    with tempfile.TemporaryDirectory(prefix="archscore-hist-") as tmp:
        archive = subprocess.run(["git", "-C", str(REPO), "archive", sha, "custom_components"],
                                 capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", tmp], input=archive, check=True)
        return sha, vector.measure(Path(tmp))


def main(argv: list[str]) -> int:
    jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else min(4, os.cpu_count() or 1)
    if "--measure-corpus" in argv:
        measure_corpus(jobs)
        return 0
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    collected = collect("--stored-only" in argv, jobs, only)
    rows = classify(collected)
    print(f"{'case':44} {'set':8} {'label':8} {'verdict':9} {'adm':4} {'dS':>9}  rises / top terms")
    for r in rows:
        top = sorted(r["terms"].items(), key=lambda kv: -abs(kv[1]))[:3]
        info = "; ".join(r["rises"][:3]) if r["rises"] else ", ".join(f"{k}{v:+.3f}" for k, v in top)
        print(f"{r['id'][:44]:44} {r['set']:8} {r['label']:8} {r['verdict']:9} {'y' if r['admissible'] else 'n':4} "
              f"{r['dS']:>9.4f}  {info[:130]}")
    print("\n".join(summary(rows)))
    print(f"weights.json sha256 {score.weights_hash()}")
    got = pinned(rows, collected)
    for name, ids in got["_sensitivity"].items():
        print(f"SENSITIVE {name}: verdict moves on {', '.join(ids)}")
    if "--record" in argv:
        old = json.loads(EXPECTED.read_text()) if EXPECTED.exists() else {}
        for k in sorted(got):
            if old.get(k) != got[k]:
                print(f"RECORD {k}: {old.get(k)} -> {got[k]}")
        EXPECTED.write_text(json.dumps(got, indent=1, sort_keys=True) + "\n")
        return 0
    want = json.loads(EXPECTED.read_text())
    moved = [k for k in sorted(set(want) | set(got)) if want.get(k) != got.get(k)]
    for k in moved:
        print(f"MOVED {k}: recorded {want.get(k)} now {got.get(k)}")
    print("calibration pinned" if not moved else f"calibration moved on {len(moved)} case(s)")
    return 1 if moved else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
