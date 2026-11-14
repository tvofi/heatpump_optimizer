"""Enumerate R10-USER-TEXT-VERIFY-STRINGS' corpus: every user-visible string the integration ships outside the
dashboard card and outside the config flow (R10-CONFIG-FLOW-TEXT-VERIFY owns config, options and selector).

Run from the repository root: `python3 -I dev/audit/rounds/round10/user-text/enumerate.py [--json]`;
`--evidence <verdicts.json> <rev>` instead checks a judged record's evidence (see evidence_findings).
Sources, each walked, never listed by hand:
  strings.json   every leaf under a top-level key other than config/options/selector;
  services.yaml  every leaf string or number (examples, selector options, units, min, max, step, defaults);
  python         every call that hands text to a user: a WARNING-or-above log line, a repair or exception raised
                 with a translation key or placeholders, a persistent notification; found by the regex below;
  templates      every leaf of a module-level, language-keyed text table (a dict literal with an "en" key whose
                 value is a dict of strings, e.g. narrative.TEMPLATES, published in the Plan Narrative attributes).
"""
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

PKG = Path("custom_components/heatpump_optimizer")
SIBLING_KEYS = ("config", "options", "selector")
PY_RE = re.compile(r"_LOGGER\.(warning|error|critical|exception)\(|persistent_notification|"
                   r"async_create_issue\(|translation_placeholders|translation_key=")


def leaves(obj, path=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, path + (str(k),))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, path + (str(i),))
    elif isinstance(obj, (str, int, float)):  # a selector's min, max, step or default is shown too
        yield path, obj


def corpus(root: Path = Path(".")) -> list[dict]:
    rows = []
    strings = json.loads((root / PKG / "strings.json").read_text())
    for path, text in leaves({k: v for k, v in strings.items() if k not in SIBLING_KEYS}):
        rows.append({"source": "strings.json", "key": ".".join(path), "text": str(text)})
    import yaml  # noqa: PLC0415 -- the HA dependency set ships PyYAML

    services = yaml.safe_load((root / PKG / "services.yaml").read_text())
    for path, text in leaves(services):
        rows.append({"source": "services.yaml", "key": ".".join(path), "text": str(text)})
    for f in sorted((root / PKG).rglob("*.py")):
        for n, line in enumerate(f.read_text().splitlines(), 1):
            if PY_RE.search(line):
                rows.append({"source": "python", "key": f"{f.relative_to(root)}:{n}", "text": line.strip()})
        for node in ast.parse(f.read_text()).body:
            target = node.target if isinstance(node, ast.AnnAssign) else (
                node.targets[0] if isinstance(node, ast.Assign) else None)
            if not isinstance(target, ast.Name) or not isinstance(node.value, ast.Dict):
                continue
            try:
                table = ast.literal_eval(node.value)
            except ValueError:
                continue
            if isinstance(table.get("en"), dict) and all(isinstance(v, str) for v in table["en"].values()):
                for path, text in leaves(table):
                    rows.append({"source": "templates", "key": f"{f.relative_to(root)}:{target.id}." + ".".join(path),
                                 "text": str(text)})
    return rows


def translation_gaps(root: Path = Path(".")) -> dict:
    """Per translation file, the in-scope strings.json keys it lacks and the keys it has that strings.json lacks."""
    def keys(d):
        return {".".join(p) for p, _ in leaves({k: v for k, v in d.items() if k not in SIBLING_KEYS})}
    want = keys(json.loads((root / PKG / "strings.json").read_text()))
    out = {}
    for t in sorted((root / PKG / "translations").glob("*.json")):
        have = keys(json.loads(t.read_text()))
        out[t.name] = {"missing": sorted(want - have), "extra": sorted(have - want)}
    return out


def evidence_findings(verdicts: list[dict], rev: str) -> list[str]:
    """Rows whose evidence is not a repository path, or whose every cited Python line at ``rev`` is blank, a comment
    or inside a docstring: the round's rule is that the code deciding a claim is its evidence, never a comment."""
    out, kinds = [], {}

    def kind(path: str, line: int) -> str:
        if path not in kinds:
            text = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True, check=True).stdout
            doc = {n for node in ast.walk(ast.parse(text)) if isinstance(node, ast.Expr)
                   and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
                   for n in range(node.lineno, node.end_lineno + 1)}
            kinds[path] = (text.splitlines(), doc)
        lines, doc = kinds[path]
        src = lines[line - 1].strip() if 0 < line <= len(lines) else None
        return ("missing" if src is None else "blank" if not src else "comment" if src.startswith("#")
                else "docstring" if line in doc else "code")

    for r in verdicts:
        cited = []
        for e in r.get("evidence") or []:
            path, _, span = e.partition(":")
            if not path.startswith(str(PKG) + "/") and "/" in path or path.startswith("/"):
                out.append(f"{r['key']}: {e} is not a repository path")
                continue
            if path.endswith(".py") and span:
                first, _, last = span.partition("-")
                full = path if "/" in path else f"{PKG}/{path}"
                cited += [kind(full, n) for n in range(int(first), int(last or first) + 1)]
        if cited and "code" not in cited and not any(not e.split(":")[0].endswith(".py") for e in r["evidence"]):
            out.append(f"{r['key']}: every cited line is {sorted(set(cited))}")
    return out


if __name__ == "__main__":
    if "--evidence" in sys.argv:  # --evidence <verdicts.json> <rev>: the evidence rule over a judged record
        _, path, rev = sys.argv[sys.argv.index("--evidence"):][:3]
        found = evidence_findings(json.load(open(path)), rev)
        print("\n".join(found) or "evidence: every row cites a code line at a repository path")
        sys.exit(1 if found else 0)
    rows = corpus()
    if "--json" in sys.argv:
        json.dump({"rows": rows, "translations": translation_gaps()}, sys.stdout, indent=1, ensure_ascii=False)
    else:
        import collections
        print(dict(collections.Counter(r["source"] + ":" + r["key"].split(".")[0] if r["source"] not in ("python", "templates")
                                       else r["source"] for r in rows)))
        print({k: (len(v["missing"]), len(v["extra"])) for k, v in translation_gaps().items()})
