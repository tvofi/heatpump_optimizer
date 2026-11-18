#!/usr/bin/env python3
"""Planted-defect recall: plant objective bugs into the baseline export, then count them after the judge.

    python3 -I plant_recall.py plant --plants P.json --tree EXPORT --population POP.txt --not NAME [--not NAME]...
    python3 -I plant_recall.py recall --plants P.json --judge-input JUDGE-INPUT.json --judge JUDGE.json
    python3 -I plant_recall.py --self-test [--no-mutants]

Decision 0018 section 5's first held-out check, built by R11-PRE-ROUND-METRICS.
Held out: no seat is scored on it, and it is no term of section 2.

THE PLANT LIST, P.json, is written by a seat that is neither finder,
orchestrator nor evaluator, and kept outside the finder wall (never inside a
tree a finder reads):
  {"round": N, "planter": "<seat>", "plants": [
    {"id": "P01", "space": "natural" | "config", "file": "<path in the tree>",
     "old": "<exact text, once in the file>", "new": "<the defect>",
     "symbol": "<the function or name the defect sits in>", "kind": "<bug kind>",
     "cell": "<axis>=<level>"   (config plants only)}]}

`plant` writes every plant into the export, and refuses first, writing nothing:
  - a planter named (case and punctuation aside) as one of the `--not` names:
    the round's finders, its orchestrator and its evaluator;
  - a plant list inside the tree it plants into (the list is held out);
  - a tree inside a git work tree: the tree itself or any ancestor holding
    `.git` (a directory, or the file a linked worktree or a submodule holds),
    since `git diff` there shows every plant; so the isolated dimensions'
    worktrees, and any subdirectory of one, take none (their recall is not read);
  - plants in only one of the two spaces: section 4 spreads them over the
    natural universe AND the configuration space;
  - a config plant whose cell is not a level `check_scopes.py --population`
    prints (POP.txt is that output at the baseline);
  - a plant whose `old` text is not in its file exactly once;
  - two plants in one file whose `old` texts overlap.
Plants sharing a file are spliced at their `old` text's place in the original
file, so one plant's `new` text never becomes another plant's target.

`recall` reads the plants and the judge's two records of the round:
  JUDGE-INPUT.json  [{id, files, instrumented_symbol, title, claim, ...}], every finding judged
  JUDGE.json        {"verdicts": [{id, verdict, into?}]}; a merged finding takes
                    its canonical finding's verdict (`merged` with `into`, or
                    the verdict text `merged into <id>`)
A finding NAMES a plant when its files hold the plant's file and the plant's
symbol is a word of its instrumented symbol, title or claim. A plant is FOUND
when a finding naming it was judged `verified` or `weakened`; LOST when every
finding naming it was refuted, unreproduced or never given a verdict (lost at
the verifier or the judge, a miss: section 4 item 3); MISSED when none names
it. Recall is found / planted, whole, per space and per kind.
NULL CONTROL: an empty plant list, or a judge record missing or with no
verdict, prints `unread (<why>)`, never a value.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REAL = ("verified", "weakened")
SPACES = ("natural", "config")


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def population(text: str) -> set[str]:
    """`check_scopes.py --population` lines `axis<TAB>count<TAB>a,b,c` -> {"axis=a", ...}."""
    cells = set()
    for ln in text.splitlines():
        parts = ln.split("\t")
        if len(parts) == 3 and parts[1].isdigit():
            cells |= {f"{parts[0]}={lv}" for lv in parts[2].split(",") if lv}
    return cells


def refusals(doc: dict, plants_path: Path, trees: list[Path], pop: set[str], banned: list[str]) -> list[str]:
    bad = []
    plants = doc.get("plants") or []
    if not plants:
        bad.append("the plant list is empty")
    if norm(doc.get("planter", "")) in {norm(b) for b in banned} or not norm(doc.get("planter", "")):
        bad.append(f"planter {doc.get('planter')!r} is unnamed or one of the finder, orchestrator and evaluator seats")
    for t in trees:
        held = next((d for d in (t.resolve(), *t.resolve().parents) if (d / ".git").exists()), None)
        if held:
            bad.append(f"{t} is inside the git work tree at {held}: a plant there shows in git diff")
        if plants_path.resolve().is_relative_to(t.resolve()):
            bad.append(f"the plant list {plants_path} is inside {t}, behind no wall")
    for sp in SPACES:
        if not any(p.get("space") == sp for p in plants):
            bad.append(f"no plant in the {sp} space")
    for p in plants:
        pid = p.get("id", "?")
        if p.get("space") not in SPACES:
            bad.append(f"{pid}: space {p.get('space')!r} is neither natural nor config")
        if p.get("space") == "config" and p.get("cell") not in pop:
            bad.append(f"{pid}: cell {p.get('cell')!r} is no population level")
        if not p.get("symbol") or not p.get("old") or p.get("old") == p.get("new"):
            bad.append(f"{pid}: a plant needs a symbol and an old text it changes")
            continue
        for t in trees:
            f = t / p.get("file", "")
            n = f.read_text(errors="replace").count(p["old"]) if f.is_file() else 0
            if n != 1:
                bad.append(f"{pid}: its old text is in {f} {n} times, not once")
    for t in trees:
        for f in {p.get("file", "") for p in plants}:
            here = [p for p in plants if p.get("file") == f]
            at = sorted(spans(t / f, here))
            for (_, end, a), (start, _, b) in zip(at, at[1:]):
                if start < end:
                    bad.append(f"{here[a].get('id', '?')} and {here[b].get('id', '?')}: their old texts overlap in {t / f}")
    return bad


def spans(f: Path, plants: list[dict]) -> list[tuple[int, int, int]]:
    """(start, end, index into `plants`) of each old text found once in `f`, as the original file holds it."""
    text = f.read_text(errors="replace") if f.is_file() else ""
    return [(text.index(p["old"]), text.index(p["old"]) + len(p["old"]), k) for k, p in enumerate(plants)
            if p.get("old") and text.count(p["old"]) == 1]


def plant(doc: dict, trees: list[Path]) -> list[str]:
    out = []
    for t in trees:
        for name in dict.fromkeys(p["file"] for p in doc["plants"]):
            f, here = t / name, [p for p in doc["plants"] if p["file"] == name]
            text = f.read_text(errors="replace")
            for start, end, k in sorted(spans(f, here), reverse=True):
                text = text[:start] + here[k]["new"] + text[end:]
            f.write_text(text)
        out += [f"PLANTED {p['id']} {p['space']} {p['file']}" for p in doc["plants"]]
    return out


def resolve(judge: dict) -> dict[str, tuple[str, str]]:
    """id -> (its canonical id, that one's verdict): the judge's merges followed.

    The one reader of the judge's merge grammar (`merged` with `into`, or the
    verdict text `merged into <id>`); finder_overlap.py imports it.
    """
    raw = {v["id"]: v for v in judge.get("verdicts", []) if "id" in v}

    def into(v: dict) -> str | None:
        if v.get("verdict") == "merged":
            return v.get("into")
        m = re.match(r"merged into (\S+)", str(v.get("verdict", "")))
        return m.group(1) if m else None

    out = {}
    for i in raw:
        cur, cid, seen = raw[i], i, {i}
        while (nxt := into(cur)) and nxt in raw and nxt not in seen:
            seen.add(nxt)
            cur, cid = raw[nxt], nxt
        out[i] = (cid, "merged-unresolved" if into(cur) else str(cur.get("verdict")))
    return out


def verdicts(judge: dict) -> dict[str, str]:
    """id -> final verdict, a merged finding resolved to its canonical one."""
    return {i: v for i, (_, v) in resolve(judge).items()}


def names(finding: dict, plant: dict) -> bool:
    text = " ".join(str(finding.get(k, "")) for k in ("instrumented_symbol", "title", "claim"))
    return plant["file"] in (finding.get("files") or []) and \
        re.search(r"(?<![\w])" + re.escape(plant["symbol"]) + r"(?![\w])", text) is not None


def recall(doc: dict | None, findings: list | None, judge: dict | None) -> list[str]:
    if not doc or not doc.get("plants"):
        return ["recall  unread (no plant list, or an empty one)"]
    if findings is None:
        return ["recall  unread (no judge input: JUDGE-INPUT.json missing or unreadable)"]
    if not judge or not judge.get("verdicts"):
        return ["recall  unread (no judge verdicts: JUDGE.json missing or empty)"]
    final = verdicts(judge)
    lines, tally = [], {}
    for p in doc["plants"]:
        hits = [f["id"] for f in findings if names(f, p)]
        real = [h for h in hits if final.get(h) in REAL]
        if real:
            state, why = "FOUND", ",".join(real)
        elif hits:
            state, why = "LOST", ",".join(f"{h}={final.get(h, 'no verdict')}" for h in hits)
        else:
            state, why = "MISSED", "no finding names it"
        lines.append(f"{state:6s} {p['id']} {p['space']} {p.get('kind', '?')} {p['file']}:{p['symbol']} ({why})")
        for key in ("all", "space " + p["space"], "kind " + p.get("kind", "?")):
            f, n = tally.get(key, (0, 0))
            tally[key] = (f + (state == "FOUND"), n + 1)
    head = []
    for key in sorted(tally, key=lambda k: (k != "all", k)):
        f, n = tally[key]
        label = "recall " if key == "all" else f"recall  {key}:"
        head.append(f"{label} {f}/{n} = {100 * f // n}% (found after the judge / planted)")
    return head + lines


def load(path: Path | None):
    try:
        return json.loads(path.read_text()) if path else None
    except (OSError, ValueError):
        return None


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        tests = Path(argv[argv.index("--tests") + 1]) if "--tests" in argv else Path(__file__).resolve().parents[3] / "tests"
        return self_test(Path(__file__), "--no-mutants" not in argv, tests)
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("cmd", choices=["plant", "recall"])
    ap.add_argument("--plants", required=True, type=Path)
    ap.add_argument("--tree", action="append", type=Path, default=[])
    ap.add_argument("--population", type=Path)
    ap.add_argument("--not", dest="banned", action="append", default=[])
    ap.add_argument("--judge-input", type=Path)
    ap.add_argument("--judge", type=Path)
    a = ap.parse_args(argv)
    doc = load(a.plants)
    if a.cmd == "recall":
        print("\n".join(recall(doc, load(a.judge_input), load(a.judge))))
        return 0
    if not a.tree or not a.population or not a.banned:
        print("plant: REFUSED --tree, --population and at least one --not are required")
        return 2
    try:
        pop = population(a.population.read_text())
    except OSError as e:
        print(f"plant: REFUSED the population is unreadable: {e}")
        return 2
    bad = refusals(doc or {}, a.plants, a.tree, pop, a.banned)
    if bad:
        print("\n".join("plant: REFUSED " + b for b in bad))
        return 1
    print("\n".join(plant(doc, a.tree)))
    return 0


SELF_TEST_MARK = "# ---" + "--- self-test: mutants edit only the code above this line"
# ------ self-test: mutants edit only the code above this line

def safe(fn, *a) -> list[str]:
    try:
        return fn(*a)
    except Exception as e:  # a crash is a failed case, never a skipped one
        return [f"crash {type(e).__name__}"]


def cases(m, tests: Path) -> dict[str, bool]:
    import subprocess
    import tempfile
    sys.path.insert(0, str(tests))
    from throwaway_git import throwaway_git_init
    r: dict[str, bool] = {}
    pop = m.population("layout\t2\tno_valve,slab_shunt\ntank_volume\tNO-READ\tcontinuous\nLEVELS: 2\n")
    r["population: levels read, a NO-READ axis gives none"] = pop == {"layout=no_valve", "layout=slab_shunt"}
    P = [{"id": "P01", "space": "natural", "file": "a.py", "old": "x < 1", "new": "x <= 1", "symbol": "clamp", "kind": "boundary"},
         {"id": "P02", "space": "config", "file": "b.py", "old": "return v", "new": "return -v", "symbol": "sign",
          "kind": "sign", "cell": "layout=slab_shunt"}]
    doc = {"round": 11, "planter": "plant-r11", "plants": P}
    with tempfile.TemporaryDirectory() as td:
        t = Path(td) / "export"
        t.mkdir()
        (t / "a.py").write_text("def clamp(x):\n    return x < 1\n")
        (t / "b.py").write_text("def sign(v):\n    return v\n")
        outside = Path(td) / "P.json"
        ref = lambda d, banned=("orch", "Evaluator-R11"), where=outside, p=pop: m.refusals(d, where, [t], p, list(banned))
        r["plant null: a sound list over both spaces is refused nothing"] = ref(doc) == []
        r["plant: a planter named as the evaluator (case, punctuation) is refused"] = \
            any("planter" in b for b in ref({**doc, "planter": "evaluator_r11"}))
        r["plant: an unnamed planter is refused"] = any("planter" in b for b in ref({**doc, "planter": ""}))
        r["plant: a list in one space only is refused"] = \
            any("no plant in the config space" in b for b in ref({**doc, "plants": P[:1]}))
        r["plant: a natural-only list is refused for config, a config-only one for natural"] = \
            any("no plant in the natural space" in b for b in ref({**doc, "plants": P[1:]}))
        r["plant: a config cell outside the population is refused"] = \
            any("no population level" in b for b in ref({**doc, "plants": [P[0], {**P[1], "cell": "layout=moon"}]}))
        r["plant: an old text not in the file once is refused"] = \
            any("not once" in b for b in ref({**doc, "plants": [{**P[0], "old": "y > 2"}, P[1]]}))
        r["plant: a plant whose file is not in the tree is refused"] = \
            any("0 times, not once" in b for b in ref({**doc, "plants": [{**P[0], "file": "nowhere.py"}, P[1]]}))
        r["plant: a plant in neither space is refused"] = \
            any("neither natural nor config" in b for b in ref({**doc, "plants": P + [{**P[0], "id": "P09", "space": "moon"}]}))
        (t / "c.py").write_text("x < 1\nx < 1\n")
        r["plant: an old text twice in the file is refused"] = \
            any("2 times, not once" in b for b in ref({**doc, "plants": [{**P[0], "file": "c.py"}, P[1]]}))
        r["plant: a plant changing nothing is refused"] = \
            any("old text it changes" in b for b in ref({**doc, "plants": [{**P[0], "new": P[0]["old"]}, P[1]]}))
        r["plant: a list inside the tree is refused"] = any("behind no wall" in b for b in ref(doc, where=t / "P.json"))
        r["plant: an empty list is refused"] = any("empty" in b for b in ref({**doc, "plants": []}))
        # git itself is the oracle for the work-tree domain: each tree below is asked of git first.
        repo, linked = Path(td) / "repo", Path(td) / "linked"
        env = throwaway_git_init(repo, "-q")
        g = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True, env=env)
        inside = lambda d: g("-C", str(d), "rev-parse", "--is-inside-work-tree").stdout.strip() == "true"
        (repo / "cc").mkdir()
        (repo / "cc" / "a.py").write_text((t / "a.py").read_text())
        g("-C", str(repo), "add", "-A")
        g("-C", str(repo), "commit", "-q", "-m", "x")
        g("-C", str(repo), "worktree", "add", "-q", str(linked))
        git = lambda tree: any("inside the git work tree" in b for b in m.refusals(doc, outside, [tree], pop, ["orch"]))
        r["plant: a tree holding .git is refused"] = inside(repo) and (repo / ".git").is_dir() and git(repo)
        r["plant: a subdirectory of a git work tree is refused"] = inside(repo / "cc") and git(repo / "cc")
        r["plant: a linked worktree (its .git a file) and a subdirectory of one are refused"] = \
            (linked / ".git").is_file() and inside(linked / "cc") and git(linked) and git(linked / "cc")
        r["plant null: a plain directory outside any work tree is refused nothing (git agrees)"] = \
            not inside(t) and g("--version").returncode == 0 and not git(t)
        out = m.plant(doc, [t])
        r["plant: each plant lands once and is printed"] = (t / "a.py").read_text().count("x <= 1") == 1 and \
            (t / "b.py").read_text().count("return -v") == 1 and len(out) == 2
        two = [{**P[0], "id": "P03", "file": "d.py", "old": "alpha", "new": "beta+alpha"},
               {**P[0], "id": "P04", "file": "d.py", "old": "beta", "new": "BETA"}, P[1]]
        (t / "b.py").write_text("def sign(v):\n    return v\n")
        (t / "d.py").write_text("alpha\nbeta\n")
        r["plant: a plant whose new text holds another's old text in one file is refused nothing"] = \
            ref({**doc, "plants": two}) == []
        m.plant({**doc, "plants": two[:2]}, [t])
        r["plant: two plants in one file each land at the original place of their old text"] = \
            (t / "d.py").read_text() == "beta+alpha\nBETA\n"
        (t / "e.py").write_text("abcdef\n")
        r["plant: two plants whose old texts overlap in one file are refused"] = any(
            "P05 and P06: their old texts overlap" in b for b in ref({**doc, "plants": [
                {**P[0], "id": "P05", "file": "e.py", "old": "abc"}, {**P[0], "id": "P06", "file": "e.py", "old": "cde"}, P[1]]}))
        r["plant: two plants with disjoint old texts in one file are refused nothing"] = ref({**doc, "plants": [
            {**P[0], "id": "P05", "file": "e.py", "old": "abc"}, {**P[0], "id": "P06", "file": "e.py", "old": "def"}, P[1]]}) == []
    F = [{"id": "D1-s1-01", "files": ["a.py"], "instrumented_symbol": "pkg.a:clamp", "title": "t", "claim": "c"},
         {"id": "D2-s1-02", "files": ["b.py"], "instrumented_symbol": "pkg.b:other", "title": "sign flips", "claim": "sign() negates"},
         {"id": "D2-s1-03", "files": ["b.py"], "instrumented_symbol": "pkg.b:signal", "title": "t", "claim": "c"}]
    other = [{**F[0], "id": "D1-s1-09", "files": ["z.py"]}]
    r["recall: a finding naming the symbol in another file names no plant"] = \
        any(x.startswith("MISSED P01") for x in m.recall(doc, other, {"verdicts": [{"id": "D1-s1-09", "verdict": "verified"}]}))
    J = lambda **v: {"verdicts": [{"id": k.replace("_", "-"), "verdict": s} for k, s in v.items()]}
    out = m.recall(doc, F, J(D1_s1_01="verified", D2_s1_02="weakened", D2_s1_03="verified"))
    r["recall: both judged real prints 2/2"] = out[0].startswith("recall  2/2 = 100%")
    out = m.recall(doc, F, J(D1_s1_01="verified", D2_s1_02="refuted", D2_s1_03="verified"))
    r["recall: a plant refuted at the judge is LOST, a miss"] = out[0].startswith("recall  1/2 = 50%") and \
        any(x.startswith("LOST   P02") and "D2-s1-02=refuted" in x for x in out)
    r["recall: a finding on a symbol sharing a prefix names no plant"] = not any("D2-s1-03" in x for x in out)
    r["recall: per space and per kind lines"] = "recall  space config: 0/1 = 0% (found after the judge / planted)" in out and \
        "recall  kind boundary: 1/1 = 100% (found after the judge / planted)" in out
    out = m.recall(doc, F[:1], J(D1_s1_01="verified"))
    r["recall: a plant no finding names is MISSED"] = any(x.startswith("MISSED P02") for x in out) and out[0].startswith("recall  1/2")
    out = m.recall(doc, F, J(D1_s1_01="unreproduced", D2_s1_02="verified"))
    r["recall: an unreproduced finding loses its plant"] = any(x.startswith("LOST   P01") for x in out)
    out = m.recall(doc, F, {"verdicts": [{"id": "D1-s1-01", "verdict": "merged into D9-s1-01 (x)"},
                                         {"id": "D9-s1-01", "verdict": "verified"},
                                         {"id": "D2-s1-02", "verdict": "merged", "into": "D9-s1-02"},
                                         {"id": "D9-s1-02", "verdict": "refuted"}]})
    r["recall: a merged finding takes its canonical verdict, either spelling"] = \
        any(x.startswith("FOUND  P01") for x in out) and any(x.startswith("LOST   P02") for x in out)
    out = m.recall(doc, F, {"verdicts": [{"id": "D2-s1-02", "verdict": "merged", "into": "D9-s1-02"},
                                         {"id": "D9-s1-02", "verdict": "verified"}]})
    r["recall: a merged finding (the into field) found real is FOUND"] = any(x.startswith("FOUND  P02") for x in out)
    out = m.recall(doc, F, {"verdicts": [{"id": "D2-s1-02", "verdict": "verified"}]})
    r["recall: a finding with no verdict loses its plant"] = any("D1-s1-01=no verdict" in x for x in out)
    r["recall null: an empty plant list prints unread, never a value"] = \
        m.recall({"plants": []}, F, J(D1_s1_01="verified")) == ["recall  unread (no plant list, or an empty one)"]
    r["recall null: no judge verdicts (an empty list) print unread"] = \
        m.recall(doc, F, {"verdicts": []})[0].startswith("recall  unread (no judge")
    r["recall null: no judge record prints unread"] = m.recall(doc, F, None)[0].startswith("recall  unread (no judge")
    r["recall null: no judge input prints unread"] = \
        safe(m.recall, doc, None, J(D1_s1_01="verified"))[0].startswith("recall  unread (no judge input")
    with tempfile.TemporaryDirectory() as td:
        empty = Path(td)
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = m.main(["recall", "--plants", str(empty / "P.json"), "--judge-input", str(empty / "I.json"), "--judge", str(empty / "J.json")])
        r["recall null: an empty input directory prints unread and no digit"] = rc == 0 and "unread" in buf.getvalue() \
            and not re.search(r"\d", buf.getvalue())
    return r


#: (needle, replacement, the case that must fail). One per predicate.
MUTANTS = {
    "planter ban": ("in {norm(b) for b in banned}", "in set()", "planter named as the evaluator"),
    "planter normalised": ('re.sub(r"[^a-z0-9]", "", name.lower())', "name", "planter named as the evaluator"),
    "planter unnamed": ("or not norm(doc.get(\"planter\", \"\"))", "or False", "unnamed planter"),
    "git tree": ('(d / ".git").exists()', "False", "holding .git"),
    "git ancestors": ("(t.resolve(), *t.resolve().parents)", "(t.resolve(),)", "subdirectory of a git work tree"),
    "git file": ('(d / ".git").exists()', '(d / ".git").is_dir()', "linked worktree"),
    "overlap": ("if start < end:", "if False:", "overlap in one file are refused"),
    "splice order": ("sorted(spans(f, here), reverse=True)", "sorted(spans(f, here))", "original place of their old text"),
    "list inside tree": ("plants_path.resolve().is_relative_to(t.resolve())", "False", "inside the tree"),
    "both spaces": ("if not any(p.get(\"space\") == sp for p in plants)", "if False", "one space only"),
    "config cell": ('p.get("cell") not in pop', "False", "outside the population"),
    "space known": ('if p.get("space") not in SPACES:', "if False:", "neither space"),
    "missing file": ('if f.is_file() else 0', "if f.is_file() else 1", "file is not in the tree"),
    "merged field": ('if v.get("verdict") == "merged":', "if False:", "the into field"),
    "old once": ("if n != 1:", "if n < 1:", "old text twice"),
    "plant changes": ('p.get("old") == p.get("new")', "False", "changing nothing"),
    "empty list": ("if not plants:\n", "if False:\n", "an empty list is refused"),
    "real verdicts": ('REAL = ("verified", "weakened")', 'REAL = ("verified", "weakened", "refuted", "unreproduced")', "refuted at the judge"),
    "weakened real": ('REAL = ("verified", "weakened")', 'REAL = ("verified",)', "both judged real"),
    "names: file": ('plant["file"] in (finding.get("files") or []) and', "True and", "in another file"),
    "names: word": ('r"(?<![\\w])" + re.escape(plant["symbol"]) + r"(?![\\w])"', 're.escape(plant["symbol"])', "sharing a prefix"),
    "lost vs missed": ("elif hits:", "elif False:", "refuted at the judge"),
    "merged resolved": ("cur, cid = raw[nxt], nxt", "break", "canonical verdict"),
    "merged text": (r'r"merged into (\S+)"', r'r"merged onto (\S+)"', "canonical verdict"),
    "null plants": ('if not doc or not doc.get("plants"):', "if not doc:", "empty plant list prints unread"),
    "null judge": ('if not judge or not judge.get("verdicts"):', "if not judge:", "an empty list) print unread"),
    "null judge input": ("if findings is None:", "if False:", "no judge input prints unread"),
}


def self_test(path: Path, mutants: bool, tests: Path) -> int:
    import importlib.util
    import subprocess
    import tempfile
    spec = importlib.util.spec_from_file_location("plant_recall_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    bad = []
    for name, ok in cases(mod, tests).items():
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
                p = subprocess.run([sys.executable, "-I", str(mp), "--self-test", "--no-mutants", "--tests", str(tests)],
                                   capture_output=True, text=True, timeout=120)
            killed = p.returncode != 0 and any(ln.startswith("FAIL") and case in ln for ln in p.stdout.splitlines())
            print(("ok   " if killed else "FAIL ") + f"mutant killed: {name} (by '{case}')")
            if not killed:
                bad.append("mutant " + name)
    print("plant_recall self-test: " + ("FAIL " + "; ".join(bad) if bad else f"ok ({'with' if mutants else 'without'} mutants)"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
