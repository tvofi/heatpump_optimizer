"""Self-test of scorecard.py: a null control and a planted case per line, and one mutant per predicate.

Run through scorecard.py's own test mode, with or without the mutants. Offline, in-process over
planted inputs; the mutants edit a temp copy of scorecard.py, and a mutant that survives, or whose
copy does not run, fails the test.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

H = "a" * 40


def load(path: Path):
    spec = importlib.util.spec_from_file_location("scorecard_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def runs(spec):
    """[(conclusion, id)] -> run rows with ascending stamps."""
    return [{"id": i, "t": f"2026-11-{1 + k // 24:02d}T{k % 24:02d}:00:00Z", "c": c} for k, (c, i) in enumerate(spec)]


def verdicts(spec):
    return [{"pr": p, "head": H, "kind": k, "cls": c, "t": f"2026-11-01T00:{n % 60:02d}:{n // 60:02d}Z"}
            for n, (p, k, c) in enumerate(spec)]


FAM = [("carry-bookkeeping", r"carry"), ("code", r"code")]
TRAIN_CLEAN = "BATCH #1001 #1002\nMERGED #1001\nMERGED #1002\n"


def cases(sc) -> dict[str, bool]:
    r: dict[str, bool] = {}
    # A_gate / A_run
    rs = runs([("success", 1)] * 4 + [("failure", 5)])
    ag, ar = sc.line_a(rs, {5: "success"})  # only a non-gate job failed
    r["A_gate null: a run failing only outside the gate job counts green"] = "5/5 read = 100%" in ag
    r["A_run null: the same run counts red"] = ar.startswith("A_run   4/5 = 80%")
    ag, _ = sc.line_a(rs, {5: "failure"})
    r["A_gate planted: a run whose gate job failed counts red"] = "4/5 read = 80%" in ag
    ag, _ = sc.line_a(rs, {})
    r["A_gate: a failed run with no job listing is unread, not guessed"] = "4/4 read = 100%" in ag and "unread 1 of 5" in ag
    ag, ar = sc.line_a(runs([("cancelled", 9)] + [("success", 1)] * 2), {})
    r["A_*: a cancelled run is not a concluded run"] = "2/2" in ag and "2/2" in ar
    ag, ar = sc.line_a(runs([("failure", 100 + i) for i in range(5)] + [("success", i) for i in range(20)]), {})
    r["A_*: only the last 20 concluded runs are read"] = "20/20 read = 100%" in ag and "20/20 = 100%" in ar
    # Y_rev / M_first
    bus = verdicts([(i, "merge", "none") for i in range(60)])
    y, m = sc.line_review(bus, FAM)
    r["Y_rev null: a bus of merge verdicts prints 100% over the last 50"] = "50/50 = 100%" in y
    r["M_first null: the same bus prints 0%"] = m.startswith("M_first 0/50 = 0%")
    mix = verdicts([(1, "blocked", "carry-x"), (2, "blocked", "code-x"), (3, "merge", "carry-x"), (4, "blocked", "zzz"),
                    (1, "merge", "none"), (1, "blocked", "carry-x")])
    y, m = sc.line_review(mix, FAM)
    r["Y_rev planted: one merge first in four pull requests"] = "merge 1/4 = 25%" in y
    r["M_first planted: only a blocked first verdict in a machinery family counts"] = m.startswith("M_first 1/4 = 25%")
    # the first verdict is the earliest by t, in any file order; the window is the 50 latest first verdicts
    shuf = [{"pr": 1, "head": H, "kind": "blocked", "cls": "carry-x", "t": "2026-11-03T00:00:00Z"},
            {"pr": 1, "head": H, "kind": "merge", "cls": "none", "t": "2026-11-01T00:00:00Z"},
            {"pr": 2, "head": H, "kind": "blocked", "cls": "zzz", "t": "2026-11-02T00:00:00Z"}]
    y, m = sc.line_review(shuf, FAM)
    r["Y_rev unordered: the earliest verdict by t is the first, not the first in the file"] = \
        "merge 1/2 = 50%" in y and "first verdicts 2026-11-01T00:00 .. 2026-11-02T00:00" in y and m.startswith("M_first 0/2 = 0%")
    rev = [{"pr": i, "head": H, "kind": "merge" if i < 50 else "blocked", "cls": "none",
            "t": f"2026-11-{1 + (99 - i) // 24:02d}T{(99 - i) % 24:02d}:00:00Z"} for i in range(60)]
    y, _ = sc.line_review(rev, FAM)
    r["Y_rev unordered window: the 50 latest first verdicts, whatever the file order"] = "merge 50/50 = 100%" in y
    y, _ = sc.line_review([{"pr": 1, "head": H, "kind": "blocked", "cls": "zzz", "t": "2026-11-01T00:00:00Z"},
                           {"pr": 1, "head": H, "kind": "merge", "cls": "none", "t": "2026-11-02T00:00:00Z"}], FAM)
    r["Y_rev first verdict: a later merge does not make a blocked first verdict a merge"] = "merge 0/1 = 0%" in y
    y, m = sc.line_review(mix, None)
    r["M_first without a family map is unread, Y_rev still prints"] = "unread" in m and "1/4" in y
    # Y_train
    mg = ["1001", "1002", "1003"]
    t = sc.line_train(mg, TRAIN_CLEAN)
    r["Y_train null: a log with no SKIP or PARK line prints 100%; an unnamed pull request is not counted"] = "2/2 = 100%" in t
    t = sc.line_train(mg, TRAIN_CLEAN + "SKIP #1001 red\nPARK #1002 held\n")
    r["Y_train planted: a SKIP line and a PARK line each cost the pull request"] = "0/2 = 0%" in t
    t = sc.line_train(["1003"], "MERGED #1003\n")
    r["Y_train named: a pull request named only on a MERGED line is counted"] = "1/1 = 100%" in t
    # H
    rows = [{"class": "production", "tokens": "hotfix-x"}, {"class": "instrument", "tokens": "hotfix"},
            {"class": "docs", "tokens": "hotfix"}, {"class": "production", "tokens": "feat"}]
    r["H: hotfix-token merges over code merges, docs not counted, production beside"] = \
        "2/3 of the last 50 code merges; production merges among them 2" in sc.line_hotfix(rows)
    r["H states it has no null control"] = "no null control" in sc.line_hotfix(rows)
    # E
    g = [{"group": "A", "source": "outside", "resume": {"stage": "done"}},
         {"group": "R10-HOTFIX-X", "files": ["custom_components/a.py"], "resume": {"stage": "fix"}},
         {"group": "B", "kind": "bug", "files": ["custom_components/b.py"]},
         {"group": "C", "kind": "bug", "files": ["tools/x.py"]},
         {"group": "D", "files": ["custom_components/d.py"]}]
    e = sc.line_escapes(g)
    r["E planted: one outside, two product hotfix or bug groups, two open"] = "outside reports 1;" in e and "product 2;" in e and "open among both 2" in e
    r["E null: a round with no escape adds none"] = "reports 0; hotfix or bug groups touching the product 0; open among both 0" in sc.line_escapes([{"group": "D"}])
    # C / K
    cn = sc.line_ck(runs([("success", 1)] * 4), "all fine\n")
    r["C, K null: no cancelled run and no recycle line are both 0"] = "C 0; K 0" in cn
    cp = sc.line_ck(runs([("cancelled", 1), ("success", 2), ("cancelled", 3), ("cancelled", 4), ("cancelled", 5), ("success", 6)]),
                    "standing-dispatch recycle at 10:00\nstanding triage RECYCLE\nroster recycle\nstanding-dispatch ok\n")
    r["C planted: the longest consecutive cancelled streak"] = "C 3;" in cp
    r["K planted: only recycle lines of the dispatch and triage seats"] = "K 2" in cp
    r["C, K unread input is named, never 0"] = "C unread; K unread" in sc.line_ck(None, None)
    # S
    def fake(argv, cwd):
        if "machinery_ratchet.py" in argv[2]:
            return 0, '{"nonproduction_merges": 498, "window": 580, "churn_per_kilo_product_lines": 12299}\n'
        paths = argv[-1:] if False else argv
        n = "100" if "custom_components" in argv else "300"
        return 0, f"origin/main:f:{n}\n"
    s = sc.line_size(Path("."), fake)
    r["S: the ratchet line verbatim and machinery over product"] = any("merges 498 per 580; churn 12299 per" in x for x in s) and any("300 / product 100 = 3.00" in x for x in s)
    s2 = sc.line_size(Path("."), lambda argv, cwd: (0, "x:1\n") if "machinery_ratchet.py" not in argv[2] else (0, '{"nonproduction_merges": 1, "window": 2, "churn_per_kilo_product_lines": 3}'))
    r["S null: frozen machinery and product give an unchanged ratio"] = s2[-1] == sc.line_size(Path("."), lambda argv, cwd: (0, "x:1\n") if "machinery_ratchet.py" not in argv[2] else (0, '{"nonproduction_merges": 1, "window": 2, "churn_per_kilo_product_lines": 3}'))[-1]
    s3 = sc.line_size(Path("."), lambda argv, cwd: (2, ""))
    s4 = sc.line_size(Path("."), lambda argv, cwd: fake(argv, cwd) if "machinery_ratchet.py" in argv[2] else (2, "origin/main:f:5\n"))
    r["S: an unreadable ratchet is unread, never a number"] = "ratchet unread" in s3[0]
    s5 = sc.line_size(Path("."), lambda argv, cwd: (3, '{"nonproduction_merges": 1, "window": 2, "churn_per_kilo_product_lines": 3}\n')
                      if "machinery_ratchet.py" in argv[2] else fake(argv, cwd))
    r["S: a ratchet that exits non-zero is unread even when it printed JSON"] = "ratchet unread" in s5[0]
    r["S: an unreadable line count is unread, never a ratio"] = "498 per 580" in s4[0] and s4[-1].endswith("unread")
    # the whole report over a planted state dir, and over an empty one
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "scorecard"
        (d / "jobs").mkdir(parents=True)
        (d / "runs.json").write_text(json.dumps(rs))
        (d / "jobs" / "jobs_5.json").write_text(json.dumps({"jobs": [{"name": "gate", "conclusion": "success"},
                                                                    {"name": "governance / instrument-self-tests", "conclusion": "failure"}]}))
        (d / "verdicts.json").write_text(json.dumps({"verdicts": mix}))
        (d / "merges.tsv").write_text("pr\tct\tclass\ttokens\n1001\t1\tproduction\thotfix\n1002\t2\tproduction\tx\n")
        (d / "roster.json").write_text(json.dumps({"groups": g}))
        (Path(td) / "study" / "work").mkdir(parents=True)
        (Path(td) / "study" / "work" / "yield.py").write_text(f"FAMILY = {FAM!r}\ndef fam(c):\n    pass\n")
        (Path(td) / "train.log").write_text(TRAIN_CLEAN)
        (Path(td) / "sweep.txt").write_text("dispatch recycle\n")
        out = sc.report(d, Path(td) / "train.log", None, Path(td) / "sweep.txt")
        r["report: ten lines' worth over a planted state dir (S unread without a checkout)"] = \
            len(out) == 9 and not any("unread (" in x for x in out if x[:2] != "S ") and out[0].startswith("A_gate  5/5")
        r["report: A_gate reads the job named gate, not the last job listed"] = out[0].startswith("A_gate  5/5 read = 100%") and out[1].startswith("A_run   4/5")
        r["report: K reads the sweep record it is given"] = "K 1 " in out[-1] and "K unread" not in out[-1]
        empty = sc.report(Path(td) / "none", Path(td) / "none.log", None, None)
        r["report: an empty state dir prints unread on every line, none a number"] = \
            all("unread" in x for x in empty if not x.startswith("C, K")) and "C unread; K unread" in empty[-1]
    return r


#: (needle, replacement, the case that must fail). One per predicate.
MUTANTS = {
    "A_gate reads the run conclusion": ('"success" if r["c"] == "success" else gate.get(r["id"], "unread")', 'r["c"]', "A_gate null"),
    "A_gate window": ("WINDOW_RUNS = 20", "WINDOW_RUNS = 21", "only the last 20"),
    "A_run counts cancelled green": ('sum(r["c"] == "success" for r in ok)', 'sum(r["c"] != "cancelled" for r in ok)', "A_run null"),
    "Y_rev not merge": ('first_merge = sum(v["kind"] == "merge"', 'first_merge = sum(v["kind"] != "merge"', "Y_rev null"),
    "Y_rev window": ("WINDOW_PRS = 50", "WINDOW_PRS = 51", "Y_rev null"),
    "M_first ignores kind": ('v["kind"] == "blocked" and family_of', 'True and family_of', "M_first planted"),
    "M_first family inverted": ("in MACH for v in last", "not in MACH for v in last", "M_first planted"),
    "Y_rev first verdict kept": ("first.setdefault(v[\"pr\"], v)", "first[v[\"pr\"]] = v", "Y_rev first verdict"),
    "Y_rev ordered by t": ('sorted(verdicts, key=lambda v: v["t"])', "list(verdicts)", "Y_rev unordered"),
    "A_gate job named gate": ('if j["name"] == "gate":', "if True:", "report: A_gate reads the job named gate"),
    "report passes the record": ("rd(record) if record else None", "None", "report: K reads"),
    "Y_train MERGED names": ('(BATCH|SKIP|PARK|MERGED|ADMIT|ALREADY)', '(BATCH|SKIP|PARK|ADMIT|ALREADY)', "Y_train named"),
    "S ratchet exit": ("json.loads(out) if rc == 0 else None", "json.loads(out)", "S: a ratchet that exits non-zero"),
    "Y_train SKIP": ('r"SKIP #(\\d+)"', 'r"SKIPX #(\\d+)"', "Y_train planted"),
    "Y_train PARK": ('ln.startswith("PARK")', 'ln.startswith("PARKX")', "Y_train planted"),
    "Y_train unnamed counted": ("tn = [p for p in merged if p in named]", "tn = [p for p in merged]", "Y_train null"),
    "H token": ('"hotfix" in r["tokens"]', '"hotfixx" in r["tokens"]', "H: hotfix"),
    "H class filter": ('("production", "instrument")', '("production",)', "H: hotfix"),
    "H production beside": ('r["class"] == "production" for r in code', 'r["class"] != "x" for r in code', "H: hotfix"),
    "E outside": ('x.get("source") == "outside"', 'x.get("source") != "outside"', "E planted"),
    "E hotfix name": ('"HOTFIX" in x["group"]', '"HOTFIXX" in x["group"]', "E planted"),
    "E product files": ('f.startswith("custom_components/")', 'f.startswith("custom_componentsX/")', "E planted"),
    "E open": ('.get("stage") != "done"', '.get("stage") == "done"', "E planted"),
    "C streak": ('cur = cur + 1 if r["c"] == "cancelled" else 0', 'cur = cur + 1 if r["c"] == "cancelled" else cur', "C planted"),
    "K seats": ("RECYCLE.search(ln) and SEATS.search(ln)", "RECYCLE.search(ln) or SEATS.search(ln)", "K planted"),
    "S ratio inverted": ("mach / prod:.2f", "prod / mach:.2f", "S: the ratchet"),
    "S unreadable count": ("if rc not in (0, 1):\n        return None", "if False:\n        return None", "S: an unreadable line count"),
}


def run(path: Path, mutants: bool = True) -> int:
    bad: list[str] = []

    def show(res: dict[str, bool]) -> None:
        for name, ok in res.items():
            print(("ok   " if ok else "FAIL ") + name)
            if not ok:
                bad.append(name)

    show(cases(load(path)))
    if mutants:
        src = path.read_text()
        here = Path(__file__).resolve()
        for name, (old, new, case) in MUTANTS.items():
            if src.count(old) != 1:
                print(f"FAIL mutant {name}: needle found {src.count(old)} times")
                bad.append(name)
                continue
            with tempfile.TemporaryDirectory() as td:
                (Path(td) / path.name).write_text(src.replace(old, new))
                (Path(td) / here.name).write_text(here.read_text())
                p = subprocess.run([sys.executable, "-I", str(Path(td) / here.name)], capture_output=True, text=True, timeout=120)
            killed = p.returncode != 0 and any(ln.startswith("FAIL") and case in ln for ln in p.stdout.splitlines())
            print(("ok   " if killed else "FAIL ") + f"mutant killed: {name} (by '{case}')")
            if not killed:
                bad.append("mutant " + name)
    print("scorecard self-test: " + ("FAIL " + "; ".join(bad) if bad else f"ok ({'with' if mutants else 'without'} mutants)"))
    return 1 if bad else 0


if __name__ == "__main__":  # a mutant copy runs its cases only
    sys.exit(run(Path(__file__).with_name("scorecard.py"), mutants=False))
