#!/usr/bin/env python3
"""D6-s3 ledger: row the text_ledger.py D6 units of the seat's cells.

Metric (one line): units of the cells (text_ledger.py units --dim D6 over
translations/en.json and custom_components/heatpump_optimizer/*.py) rowed,
split into claim rows (each carrying claims.py's executed check and verdict)
and no-claim rows (by the classification rules below), and the units left
unrowed (not reached this round).

Run (from the export root), after claims.py has written claims.json:
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s3/claims.py
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s3/ledger.py
    python3 tools/audit/text_ledger.py check --dim D6 --plant dev/audit/rounds/round11/D6/s3/ledger.tsv \
        custom_components/heatpump_optimizer/translations/en.json $(ls custom_components/heatpump_optimizer/*.py | grep -v '/\\._')

Writes dev/audit/rounds/round11/D6/s3/ledger.tsv and not_reached.tsv.
Expected on the export audited (box B3, linux; baseline
92d38ecb640bd462f2e19c0814d0f0b7df1ee692): units=3331, see RESULT lines; exact.

No-claim rules (a unit matching one asserts nothing the code, data or page
can falsify):
  L1 en.json labels: a `name`, `title`, `flow_title`, a field label
     (`...data.<key>`), a `selector.*` option, a menu option or an entity
     state label, holding no digit.
  L2 en.json bare instructions: a sentence opening on an imperative verb that
     states no effect (no " to ", " so ", "clears", "keeps", "removes",
     "resets", "until", no digit).
  L3 Python labels and reason phrases: a string literal of at most six words
     with no digit and no claim word (never, always, only, every, within,
     until, at most, at least, cannot, will, must, retried, clears, keeps,
     because, instead, no longer) -- a name, vocabulary token, unit label or
     the reason phrase a branch emits by construction.
  L4 Python runtime narration: a %- or {}-format string with no digit and
     no claim word, which narrates values computed at run time.
Everything else is a claim; one claims.py checked is rowed with its verdict,
the rest stay unrowed and are listed in not_reached.tsv by file/section.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path.cwd()
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools/audit"))
import text_ledger as TL  # noqa: E402

PKG = "custom_components/heatpump_optimizer/"
EN_PATH = PKG + "translations/en.json"
CMD = "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D6/s3/claims.py"

LABEL = re.compile(r"(\.(name|title|flow_title)$|\.data\.[^.]+$|^selector\.|\.menu_options\.|\.state\.[^.]+$)")
IMPERATIVE = re.compile(r"^(Check|Choose|Pick|Leave|Set|Use|Correct|Assign|Switch|Turn|Restrict|Omit|Point|Configure|"
                        r"Lower|Raise|Change|Fix|Try|Reinstall|Please|Select|Enter|Keep|Give|Install|Add|Look|Open)\b")
EFFECT = re.compile(r"( to | so |clears|keeps|removes|resets|until|\d)")
CLAIM_WORD = re.compile(r"\b(never|always|only|every|within|until|at most|at least|cannot|can't|will|must|retried|"
                        r"clears|keeps|because|instead|no longer)\b", re.I)
FORMAT = re.compile(r"%[-+ 0-9.]*[sdfrgx]|\{[^}]*\}")


def seat_files():
    files = [EN_PATH] + sorted(PKG + p.name for p in (ROOT / PKG).glob("*.py") if not p.name.startswith("._"))
    return files


def en_paths():
    en = json.loads((ROOT / EN_PATH).read_text())
    out = []

    def walk(v, path):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, path + [k])
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk(x, path + [str(i)])
        elif isinstance(v, str):
            out.extend(".".join(path) for _ in TL.sentences(v))
    walk(en, [])
    return out


def classify(uid, kind, text, path):
    t = " ".join(text.split())
    if kind == "file":
        return "L0"
    if uid.startswith(EN_PATH):
        if LABEL.search(path) and not re.search(r"\d", t):
            return "L1"
        if IMPERATIVE.match(t) and not EFFECT.search(t):
            return "L2"
        return None
    if re.search(r"\d", t) or CLAIM_WORD.search(t):
        return None
    if len(t.split()) <= 6:
        return "L3"
    if FORMAT.search(t):
        return "L4"
    return None


def main():
    files = seat_files()
    units = TL.enumerate_units(ROOT, files, "D6")
    paths = iter(en_paths())
    path_of = {}
    for u in units:
        if u[0].startswith(EN_PATH):
            path_of[u[0]] = next(paths)
    claims = {r["unit"]: r for r in json.loads((HERE / "claims.json").read_text())}
    lpath = HERE / "links.json"
    for uid, r in (json.loads(lpath.read_text()) if lpath.exists() else {}).items():
        if uid not in claims:
            claims[uid] = {"claimed": "link resolves", "observed": f"HTTP {r['status']} for {r['url']}",
                           "symbol": "links.py HEAD", "verdict": r["verdict"], "cmd": "python3 dev/audit/rounds/round11/D6/s3/links.py"}
    rows, left = [], []
    counts = {"claim": 0, "L0": 0, "L1": 0, "L2": 0, "L3": 0, "L4": 0}
    for uid, line, kind, text in units:
        if uid in claims:
            c = claims[uid]
            res = f"claimed {c['claimed']} observed {c['observed']} via {c['symbol']}".replace("\t", " ").replace("\n", " ")
            truth = "" if c["verdict"] == "true" else f"production delivers {c['observed']} ({c['symbol']})"
            rows.append([uid, str(line), "claim", c.get("cmd", CMD), res, c["verdict"], truth])
            counts["claim"] += 1
            continue
        rule = classify(uid, kind, text, path_of.get(uid, ""))
        if rule:
            rows.append([uid, str(line), "no-claim", "", "", "-", ""])
            counts[rule] += 1
        else:
            group = uid.split("#")[0]
            if group == EN_PATH:
                group += "#" + ".".join(path_of[uid].split(".")[:2])
            left.append((group, uid, " ".join(text.split())[:160]))
    (HERE / "ledger.tsv").write_text("\n".join("\t".join(r) for r in [TL.HEADER] + rows) + "\n")
    (HERE / "not_reached.tsv").write_text("".join(f"{g}\t{u}\t{t}\n" for g, u, t in left))
    groups = {}
    for g, _, _ in left:
        groups[g] = groups.get(g, 0) + 1
    print(f"RESULT units={len(units)} count")
    for k, v in counts.items():
        print(f"RESULT rowed_{k}={v} count")
    print(f"RESULT rowed={len(rows)} count")
    print(f"RESULT unrowed={len(left)} count")
    print(f"RESULT unrowed_groups={len(groups)} count")
    for g, n in sorted(groups.items(), key=lambda x: -x[1]):
        print(f"   {n:5d} {g}")


if __name__ == "__main__":
    main()
