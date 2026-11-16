#!/usr/bin/env python3
"""Two-finder overlap: seat two finders on one universe, then estimate the bugs there after the judge.

    python3 -I finder_overlap.py seat --scopes scopes.json --seat D1-s1 --model-a M --model-b M --round N --out PAIR.json
    python3 -I finder_overlap.py estimate --scopes scopes.json --pair PAIR.json --report-a A.json --report-b B.json --judge JUDGE.json
    python3 -I finder_overlap.py --self-test [--no-mutants]

Decision 0018 section 5's second held-out check (the owner's round-11 trial),
built by R11-PRE-ROUND-METRICS. Held out: no seat is scored on it.

`seat` names the pair: seat A is the scopes.json seat itself, dispatched by
audit-find.js as ever; seat B is its twin, which the orchestrator dispatches
with the same brief, the same cells (`check_scopes.py --seat <seat>`) and the
same baseline export, numbering its findings from 71 so no id collides with
seat A's (01-50) or the leads seat's (51-70), its report at
`dev/audit/rounds/round<N>/<dim>/<key>-twin/REPORT.json`. scopes.json stays
disjoint: the twin is no seat of it. Refused: a seat scopes.json does not
hold, and a missing model. PAIR.json records the universe and both models.

OWNER-ONLY: a dimension whose scopes.json entry carries `owner_only: true`
publishes nothing, and a twin's report path is in the tree. So `seat` refuses
a seat of such a dimension, and `estimate` (which requires `--scopes`) refuses
a pair naming one before it opens a report or the judge record. Admission is
scopes.json membership alone: the seat pattern takes any dimension number.
Each refusal prints the seat id and that its dimension is owner-only, never a
path or a count.

`estimate` reads the two seats' reports (a report, or a box's
`reports-<box>.json` holding the seat under `reports`) and JUDGE.json. A
seat's findings are the ids its own report lists. Counted after the judge, as
recall is (section 4 item 3): each finding is resolved to its canonical one
through the judge's merges (`merged` with `into`, or `merged into <id>`), and
a canonical finding judged `verified` or `weakened` is one bug. n1 and n2 are
the bugs holding a finding of seat A, of seat B; m those holding both, so a
duplicate the judge merged is the shared bug. The estimate of the bugs in the
universe is (n1 + 1)(n2 + 1) / (m + 1) - 1, and of the unseen ones that less
n1 + n2 - m. Printed beside it: both seats' models, and when they are one
model that the estimate is biased low (section 4, assumption 2).
NULL CONTROL: a missing pair record, either seat's report missing (a seat
that never reported cannot be told from one that found nothing), or a judge
record missing or with no verdict prints `unread (<why>)`, never a value.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plant_recall  # noqa: E402 -- the judge's merge grammar has one reader, there

TWIN_FROM = 71


SEAT_RE = re.compile(r"(D[0-9]+)-(s[0-9]+)")


def owner_only(scopes: dict) -> set[str]:
    """The dimensions scopes.json declares owner-only: the one declaration, read by every caller."""
    return {d for d, e in scopes.items() if isinstance(e, dict) and e.get("owner_only") is True}


def owner_only_seat(scopes: dict, name) -> bool:
    m = SEAT_RE.match(name) if isinstance(name, str) else None
    return bool(m) and m.group(1) in owner_only(scopes)


def refuse_owner_only(scopes: dict, pair: dict | None) -> str:
    """Why this pair may not be estimated, or "": its universe or either seat is of an owner-only dimension."""
    names = [(pair or {}).get("universe")] + [s.get("name") for s in (pair or {}).get("seats") or [] if isinstance(s, dict)]
    hit = [n for n in names if owner_only_seat(scopes, n)]
    return f"{SEAT_RE.match(hit[0]).group(0)} is a seat of an owner-only dimension" if hit else ""


def seat_pair(scopes: dict, seat: str, model_a: str, model_b: str, rnd: int) -> tuple[dict | None, str]:
    m = SEAT_RE.fullmatch(seat)
    if not m or m.group(2) not in ((scopes.get(m.group(1)) or {}).get("seats") or {}):
        return None, f"{seat!r} is no seat of scopes.json"
    if owner_only_seat(scopes, seat):
        return None, f"{seat} is a seat of an owner-only dimension"
    # The owner-only test above reads any dimension number (SEAT_RE); a seat is seated only in the
    # dimensions a round's report schema admits (audit-find.js, D0 to D17).
    if not re.fullmatch(r"D(?:1[0-7]|[0-9])", m.group(1)):
        return None, f"{seat!r} names no dimension a round's report admits (D0 to D17)"
    if not model_a.strip() or not model_b.strip():
        return None, "both seats' models are required: the estimate is reported with them"
    dim, key = m.groups()
    twin = f"dev/audit/rounds/round{rnd}/{dim}/{key}-twin/REPORT.json"
    return {"round": rnd, "universe": seat,
            "seats": [{"name": seat, "model": model_a.strip(), "ids": f"{seat}-01..50"},
                      {"name": seat + "-twin", "model": model_b.strip(), "ids": f"{seat}-{TWIN_FROM}..99", "report": twin}]}, ""


def report_ids(rep: dict | None, name: str) -> set[str] | None:
    if not isinstance(rep, dict):
        return None
    if "reports" in rep:
        rep = (rep.get("reports") or {}).get(name)
    if not isinstance(rep, dict) or not isinstance(rep.get("findings"), list):
        return None
    return {f["id"] for f in rep["findings"] if isinstance(f, dict) and "id" in f}


def canonical(judge: dict) -> dict[str, str | None]:
    """id -> its canonical id when that one is judged real, else None."""
    return {i: cid if v in plant_recall.REAL else None for i, (cid, v) in plant_recall.resolve(judge).items()}


def estimate(pair: dict | None, ids_a: set | None, ids_b: set | None, judge: dict | None) -> list[str]:
    if not pair or len(pair.get("seats") or []) != 2:
        return ["overlap unread (no pair record)"]
    if ids_a is None or ids_b is None:
        return ["overlap unread (a seat's report is missing: a seat that never reported is not one that found nothing)"]
    if not judge or not judge.get("verdicts"):
        return ["overlap unread (no judge verdicts: JUDGE.json missing or empty)"]
    canon = canonical(judge)
    bugs_a = {canon[i] for i in ids_a if canon.get(i)}
    bugs_b = {canon[i] for i in ids_b if canon.get(i)}
    n1, n2, m = len(bugs_a), len(bugs_b), len(bugs_a & bugs_b)
    est = (n1 + 1) * (n2 + 1) / (m + 1) - 1
    a, b = pair["seats"]
    same = a["model"].strip().lower() == b["model"].strip().lower()
    return [f"overlap {pair['universe']}: n1={n1} n2={n2} m={m}, estimate {est:.1f} bugs, "
            f"{est - (n1 + n2 - m):.1f} unseen ((n1+1)(n2+1)/(m+1)-1, judged real)",
            f"overlap models: {a['name']}={a['model']} {b['name']}={b['model']}"
            + (" -- one model: the estimate is biased low (0018 section 4, assumption 2)" if same
               else " -- two models: the bias is narrowed, not measured")]


def load(path: Path | None):
    try:
        return json.loads(path.read_text()) if path else None
    except (OSError, ValueError):
        return None


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test(Path(__file__), mutants="--no-mutants" not in argv)
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("cmd", choices=["seat", "estimate"])
    ap.add_argument("--scopes", type=Path)
    ap.add_argument("--seat", default="")
    ap.add_argument("--model-a", default="")
    ap.add_argument("--model-b", default="")
    ap.add_argument("--round", type=int, default=0)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--pair", type=Path)
    ap.add_argument("--report-a", type=Path)
    ap.add_argument("--report-b", type=Path)
    ap.add_argument("--judge", type=Path)
    a = ap.parse_args(argv)
    if a.cmd == "seat":
        scopes = load(a.scopes)
        if not isinstance(scopes, dict) or not a.out or a.round < 1:
            print("seat: REFUSED --scopes (readable), --round and --out are required")
            return 2
        pair, why = seat_pair(scopes, a.seat, a.model_a, a.model_b, a.round)
        if not pair:
            print("seat: REFUSED " + why)
            return 1
        a.out.write_text(json.dumps(pair, indent=1) + "\n")
        print(f"SEATED {pair['universe']}: twin report {pair['seats'][1]['report']}, twin ids {pair['seats'][1]['ids']}")
        return 0
    scopes = load(a.scopes)
    if not isinstance(scopes, dict):
        print("estimate: REFUSED --scopes (readable) is required: it names the owner-only dimensions")
        return 2
    pair = load(a.pair)
    why = refuse_owner_only(scopes, pair if isinstance(pair, dict) else None)
    if why:
        print("estimate: REFUSED " + why)
        return 1
    names = [s.get("name", "") for s in (pair or {}).get("seats", [])] + ["", ""]
    print("\n".join(estimate(pair, report_ids(load(a.report_a), names[0]), report_ids(load(a.report_b), names[1]),
                             load(a.judge))))
    return 0


SELF_TEST_MARK = "# ---" + "--- self-test: mutants edit only the code above this line"
# ------ self-test: mutants edit only the code above this line

def safe(fn, *a):
    try:
        return fn(*a)
    except Exception as e:  # a crash is a failed case, never a skipped one
        return [f"crash {type(e).__name__}"]


def cases(m) -> dict[str, bool]:
    import contextlib
    import io
    import tempfile
    r: dict[str, bool] = {}
    scopes = {"D1": {"seats": {"s1": [{"files": ["**"]}]}}}
    pair, why = m.seat_pair(scopes, "D1-s1", "opus", "sonnet", 11)
    r["seat null: a scopes seat with two models is seated"] = pair is not None and why == "" and \
        pair["seats"][1]["report"] == "dev/audit/rounds/round11/D1/s1-twin/REPORT.json" and pair["seats"][1]["model"] == "sonnet"
    r["seat: the twin's ids start at 71, above the seat's own"] = pair["seats"][1]["ids"] == "D1-s1-71..99"
    r["seat: a seat scopes.json does not hold is refused"] = m.seat_pair(scopes, "D1-s2", "a", "b", 11)[0] is None and \
        m.seat_pair(scopes, "D2-s1", "a", "b", 11)[0] is None
    r["seat: a missing model is refused"] = m.seat_pair(scopes, "D1-s1", "a", " ", 11)[0] is None
    hi = {"D16": {"seats": {"s1": []}}, "D17": {"seats": {"s3": []}}, "D18": {"seats": {"s1": []}}}
    r["seat: a D16 and a D17 seat are seated, a D18 one refused"] = \
        (m.seat_pair(hi, "D16-s1", "a", "b", 11)[0] or {}).get("universe") == "D16-s1" and \
        (m.seat_pair(hi, "D17-s3", "a", "b", 11)[0] or {}).get("universe") == "D17-s3" and \
        m.seat_pair(hi, "D18-s1", "a", "b", 11)[0] is None
    rep = lambda *ids: {"findings": [{"id": i} for i in ids]}
    A, B = m.report_ids(rep("D1-s1-01", "D1-s1-02", "D1-s1-03"), "x"), m.report_ids(rep("D1-s1-71", "D1-s1-72"), "x")
    r["report: a box file is read under the seat's name"] = \
        m.report_ids({"reports": {"D1-s1": rep("D1-s1-05")}}, "D1-s1") == {"D1-s1-05"} and \
        m.report_ids({"reports": {"D1-s1": rep("D1-s1-05")}}, "D1-s1-twin") is None
    J = {"verdicts": [{"id": "D1-s1-01", "verdict": "verified"}, {"id": "D1-s1-02", "verdict": "weakened"},
                      {"id": "D1-s1-03", "verdict": "refuted"},
                      {"id": "D1-s1-71", "verdict": "merged into D1-s1-01 (same harness)"},
                      {"id": "D1-s1-72", "verdict": "verified"}]}
    out = safe(m.estimate, pair, A, B, J)
    # n1 = {01, 02} (03 refuted), n2 = {01 via the merge, 72}, m = {01}: (3)(3)/(2) - 1 = 3.5; unseen 3.5 - 3 = 0.5
    r["estimate: n1, n2, m after the judge and the Chapman estimate"] = \
        out[0] == "overlap D1-s1: n1=2 n2=2 m=1, estimate 3.5 bugs, 0.5 unseen ((n1+1)(n2+1)/(m+1)-1, judged real)"
    r["estimate: two models are printed and the bias called unmeasured"] = \
        out[1].startswith("overlap models: D1-s1=opus D1-s1-twin=sonnet") and "not measured" in out[1]
    same, _ = m.seat_pair(scopes, "D1-s1", "Opus", "opus ", 11)
    r["estimate: one model is printed as biased low"] = "biased low" in safe(m.estimate, same, A, B, J)[-1]
    J2 = {"verdicts": J["verdicts"][:3] + [{"id": "D1-s1-71", "verdict": "merged", "into": "D1-s1-03"},
                                          {"id": "D1-s1-72", "verdict": "unreproduced"}]}
    r["estimate: a merge into a refuted finding and an unreproduced one count no bug"] = \
        safe(m.estimate, pair, A, B, J2)[0].startswith("overlap D1-s1: n1=2 n2=0 m=0, estimate 2.0")
    r["estimate: disjoint finds share nothing"] = \
        safe(m.estimate, pair, A, {"D1-s1-72"}, J)[0].startswith("overlap D1-s1: n1=2 n2=1 m=0, estimate 5.0")
    r["estimate null: no pair prints unread"] = safe(m.estimate, None, A, B, J) == ["overlap unread (no pair record)"] and \
        safe(m.estimate, {"universe": "D1-s1", "seats": pair["seats"][:1]}, A, B, J) == ["overlap unread (no pair record)"]
    r["estimate null: a missing report prints unread"] = safe(m.estimate, pair, A, None, J)[0].startswith("overlap unread (a seat")
    r["estimate null: no judge verdicts print unread"] = safe(m.estimate, pair, A, B, {"verdicts": []})[0].startswith(
        "overlap unread (no judge")
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "s.json").write_text(json.dumps(scopes))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = m.main(["estimate", "--scopes", str(d / "s.json"), "--pair", str(d / "P"), "--report-a", str(d / "A"),
                         "--report-b", str(d / "B"), "--judge", str(d / "J")])
        r["estimate null: an empty input directory prints unread and no digit"] = rc == 0 and "unread" in buf.getvalue() \
            and not re.search(r"\d", buf.getvalue())
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = m.main(["estimate", "--pair", str(d / "P"), "--report-a", str(d / "A"), "--report-b", str(d / "B"),
                         "--judge", str(d / "J")])
        r["estimate: no --scopes is refused and prints no estimate"] = rc == 2 and "REFUSED" in buf.getvalue() \
            and "overlap" not in buf.getvalue()
        with contextlib.redirect_stdout(io.StringIO()):
            rc = m.main(["seat", "--scopes", str(d / "s.json"), "--seat", "D1-s1", "--model-a", "a", "--model-b", "b",
                         "--round", "11", "--out", str(d / "pair.json")])
        r["seat: the pair record is written"] = rc == 0 and json.loads((d / "pair.json").read_text())["universe"] == "D1-s1"
        (d / "pair.json").unlink()
        with contextlib.redirect_stdout(io.StringIO()):
            rc = m.main(["seat", "--scopes", str(d / "s.json"), "--seat", "D1-s1", "--model-a", "a", "--model-b", "b",
                         "--out", str(d / "pair.json")])
        r["seat: no --round is refused and writes nothing"] = rc == 2 and not (d / "pair.json").exists()
    r.update(owner_only_cases(m))
    return r


def run_main(m, argv: list[str]) -> tuple[int, str]:
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = m.main(argv)
    return rc, buf.getvalue()


def owner_only_cases(m) -> dict[str, bool]:
    """Row P10 of the owner-only channel: a canary seat and a nonce, drawn per run and never written to the tree."""
    import os
    import secrets
    import tempfile
    r: dict[str, bool] = {}
    k, rnd, nonce = 1 + secrets.randbelow(9000), 11, secrets.token_hex(16)
    dim, key = "D17", f"s{k}"
    canary = f"{dim}-{key}"
    real = Path(os.environ.get("FINDER_OVERLAP_SCOPES") or Path(__file__).resolve().parents[3] / "dev/audit/config/scopes.json")
    base = json.loads(real.read_text())

    def scratch(flag) -> dict:
        entry = {"mode": "cells", "universe": [], "seats": {key: [{"cells": "all"}]}}
        if flag is not None:
            entry["owner_only"] = flag
        return {"D15": base["D15"], dim: entry}

    def drive(d: Path, flag, seat: str) -> dict:
        """seat, then estimate over a hand-written pair with stub reports and a stub judge carrying the nonce."""
        (d / "s.json").write_text(json.dumps(scratch(flag)))
        out = d / "pair.json"
        rc_s, txt_s = run_main(m, ["seat", "--scopes", str(d / "s.json"), "--seat", seat, "--model-a", "a", "--model-b", "b",
                                   "--round", str(rnd), "--out", str(out)])
        wrote = out.exists()
        out.unlink(missing_ok=True)
        (d / "hand.json").write_text(json.dumps({"round": rnd, "universe": seat, "seats": [
            {"name": seat, "model": "a"}, {"name": seat + "-twin", "model": "b"}]}))
        finding = lambda n: {"id": f"{seat}-{n}", "title": nonce}
        (d / "A.json").write_text(json.dumps({"findings": [finding("01")]}))
        (d / "B.json").write_text(json.dumps({"findings": [finding("71")]}))
        (d / "J.json").write_text(json.dumps({"verdicts": [
            {"id": f"{seat}-01", "verdict": "verified", "note": nonce},
            {"id": f"{seat}-71", "verdict": f"merged into {seat}-01"}]}))
        before = sorted(p.name for p in d.iterdir())
        rc_e, txt_e = run_main(m, ["estimate", "--scopes", str(d / "s.json"), "--pair", str(d / "hand.json"),
                                   "--report-a", str(d / "A.json"), "--report-b", str(d / "B.json"), "--judge", str(d / "J.json")])
        return {"rc_s": rc_s, "txt_s": txt_s, "wrote": wrote, "rc_e": rc_e, "txt_e": txt_e,
                "new": sorted(p.name for p in d.iterdir()) != before}

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        x = drive(d, True, canary)
        r["owner-only seat: the canary seat is refused, no pair written, no twin path printed"] = \
            x["rc_s"] == 1 and not x["wrote"] and "REFUSED" in x["txt_s"] and "owner-only" in x["txt_s"] \
            and "-twin" not in x["txt_s"] and f"round{rnd}/{dim}" not in x["txt_s"] and "/" not in x["txt_s"]
        r["owner-only estimate: a pair naming the canary seat is refused before any report is read"] = \
            x["rc_e"] == 1 and "REFUSED" in x["txt_e"] and "owner-only" in x["txt_e"] and "n1=" not in x["txt_e"] \
            and nonce not in x["txt_e"] and "/" not in x["txt_e"] and not x["new"]
        (d / "twin.json").write_text(json.dumps({"round": rnd, "universe": "D15-s1", "seats": [
            {"name": "D15-s1", "model": "a"}, {"name": canary + "-twin", "model": "b"}]}))
        rc, txt = run_main(m, ["estimate", "--scopes", str(d / "s.json"), "--pair", str(d / "twin.json"),
                               "--report-a", str(d / "A.json"), "--report-b", str(d / "B.json"), "--judge", str(d / "J.json")])
        r["owner-only estimate: a public universe with an owner-only seat's name is refused"] = \
            rc == 1 and "n1=" not in txt and nonce not in txt
        for label, flag in (("removed", None), ("false", False)):
            n = drive(d, flag, canary)
            r[f"owner-only null: the same seat with the flag {label} is admitted and its twin path printed"] = \
                n["rc_s"] == 0 and n["wrote"] and f"round{rnd}/{dim}/{key}-twin/REPORT.json" in n["txt_s"] \
                and n["rc_e"] == 0 and "n1=1" in n["txt_e"]
        n = drive(d, True, "D15-s1")
        r["owner-only null: a D15 seat of the committed scopes is admitted beside an owner-only dimension"] = \
            "s1" in base["D15"]["seats"] and n["rc_s"] == 0 and n["wrote"] \
            and f"round{rnd}/D15/s1-twin/REPORT.json" in n["txt_s"] and n["rc_e"] == 0 and "n1=1" in n["txt_e"]
    pair, why = m.seat_pair(base, "D18-s1", "a", "b", rnd)
    declared = isinstance(base.get("D18"), dict)
    r["owner-only: D18-s1 over the committed scopes is refused (no seat until the dimension lands, owner-only after)"] = \
        pair is None and (("owner-only" in why) if declared else ("no seat of scopes.json" in why)) \
        and (not declared or base["D18"].get("owner_only") is True)
    return r


#: (needle, replacement, the case that must fail). One per predicate.
MUTANTS = {
    "seat in scopes": ('m.group(2) not in ((scopes.get(m.group(1)) or {}).get("seats") or {})', "False", "does not hold"),
    "seat bound D15": ("1[0-7]|[0-9]", "1[0-5]|[0-9]", "D17 seat are seated"),
    "seat bound D16": ("1[0-7]|[0-9]", "1[0-6]|[0-9]", "D17 seat are seated"),
    "seat bound D18": ("1[0-7]|[0-9]", "1[0-8]|[0-9]", "D17 seat are seated"),
    "seat models": ("if not model_a.strip() or not model_b.strip():", "if False:", "missing model"),
    "box key": ('rep = (rep.get("reports") or {}).get(name)', "rep = rep", "box file"),
    "shared": ("m = len(bugs_a), len(bugs_b), len(bugs_a & bugs_b)", "m = len(bugs_a), len(bugs_b), 0", "Chapman"),
    "chapman": ("(n1 + 1) * (n2 + 1) / (m + 1) - 1", "n1 * n2 / max(m, 1)", "Chapman"),
    "unseen": ("est - (n1 + n2 - m)", "est - (n1 + n2)", "Chapman"),
    "one model": ('a["model"].strip().lower() == b["model"].strip().lower()', 'a["model"] == b["model"]', "biased low"),
    "null pair": ('if not pair or len(pair.get("seats") or []) != 2:', "if not pair:", "no pair prints unread"),
    "null report": ("if ids_a is None or ids_b is None:", "if ids_a is None:", "missing report"),
    "null judge": ('if not judge or not judge.get("verdicts"):', "if not judge:", "no judge verdicts"),
    "twin ids": ("TWIN_FROM = 71", "TWIN_FROM = 72", "twin's ids start at 71"),
    "any dimension number": ('SEAT_RE = re.compile(r"(D[0-9]+)-(s[0-9]+)")',
                             'SEAT_RE = re.compile(r"(D(?:1[0-5]|[0-9]))-(s[0-9]+)")', "flag removed is admitted"),
    "owner-only declared": ('e.get("owner_only") is True', 'e.get("owner_only") is not None', "flag false is admitted"),
    "owner-only seat": ("    if owner_only_seat(scopes, seat):\n", "    if False:\n", "canary seat is refused"),
    "owner-only estimate": ("    if why:\n        print(\"estimate: REFUSED \" + why)", "    if False:\n        print(\"estimate: REFUSED \" + why)",
                            "refused before any report is read"),
    "owner-only seat name": ('[s.get("name") for s in (pair or {}).get("seats") or [] if isinstance(s, dict)]', "[]",
                             "owner-only seat's name is refused"),
    "scopes required": ('        print("estimate: REFUSED --scopes (readable) is required: it names the owner-only dimensions")\n        return 2',
                        '        print("estimate: REFUSED --scopes (readable) is required: it names the owner-only dimensions")\n        scopes = {}',
                        "no --scopes is refused"),
    "round required": ('ap.add_argument("--round", type=int, default=0)', 'ap.add_argument("--round", type=int, default=1)', "no --round"),
}


def self_test(path: Path, mutants: bool = True) -> int:
    import importlib.util
    import os
    import subprocess
    import tempfile
    scopes_file = Path(os.environ.get("FINDER_OVERLAP_SCOPES") or path.resolve().parents[3] / "dev/audit/config/scopes.json")
    spec = importlib.util.spec_from_file_location("finder_overlap_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    bad = []
    for name, ok in cases(mod).items():
        print(("ok   " if ok else "FAIL ") + name)
        if not ok:
            bad.append(name)
    if mutants:
        code, sep, tail = path.read_text().partition(SELF_TEST_MARK)
        for name, (old, new, case) in MUTANTS.items():
            if code.count(old) != 1:
                print(f"FAIL mutant {name}: needle found {code.count(old)} times in the code")
                bad.append("mutant " + name)
                continue
            with tempfile.TemporaryDirectory() as td:
                mp = Path(td) / path.name
                mp.write_text(code.replace(old, new) + sep + tail)
                (Path(td) / "plant_recall.py").write_text(path.with_name("plant_recall.py").read_text())
                p = subprocess.run([sys.executable, "-I", str(mp), "--self-test", "--no-mutants"],
                                   capture_output=True, text=True, timeout=120,
                                   env={**os.environ, "FINDER_OVERLAP_SCOPES": str(scopes_file)})
            killed = p.returncode != 0 and any(ln.startswith("FAIL") and case in ln for ln in p.stdout.splitlines())
            print(("ok   " if killed else "FAIL ") + f"mutant killed: {name} (by '{case}')")
            if not killed:
                bad.append("mutant " + name)
    print("finder_overlap self-test: " + ("FAIL " + "; ".join(bad) if bad else f"ok ({'with' if mutants else 'without'} mutants)"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
