#!/usr/bin/env python3
"""Render the orchestrator sweep from its tracked template and a session overlay.

    python3 -I tools/audit/seat/sweep_render.py --overlay <overlay.json> [--template <md>] [--out <file>]
    python3 -I tools/audit/seat/sweep_render.py --self-test

WHY THIS EXISTS. Round 10's sweep lived only in a session's timer prompt, so a
new session or round re-derived it from memory. `tools/audit/seat/sweep_template.md`
is that prompt with every session-specific value a named `{{placeholder}}`;
this file fills them from a JSON overlay the session keeps out of the tree.

WHAT IT RENDERS. The text between the template's `<!-- sweep:begin -->` and
`<!-- sweep:end -->` markers, each exactly once, with every `{{name}}`
replaced by the overlay's value, printed to stdout or written to `--out`.

THE PLACEHOLDER REGISTRY is the template's own `## Placeholders` table: one row
per name, the name in backticks in the first cell. The table is the one owner,
so this file holds no second list. Each refusal below exits 1, names what
failed and writes nothing:
  unknown      the sweep uses a `{{name}}` the table does not declare, or the
               overlay carries a key the table does not declare;
  unfilled     a declared name the overlay omits, or gives an empty value, or a
               value that is not a string or an integer (a JSON `true` is not
               a seat cap); a value holding a newline or `{{` (no second pass);
  unused       a declared name the sweep never uses: the table has rotted;
  host-path    a home directory (`ref_privacy.py`'s `HOME_DIR` grammar, the one
               owner of what names a host) in the rendered text that does not
               lie wholly inside one overlay value -- the template is tracked
               text and may name no host; a session that puts its own paths in
               the overlay is supplying them, and a match that straddles
               template text and a value is the template's;
  citation     a path the template cites in backticks under `tools/`, `tests/`,
               `dev/` or `.github/`, or `CLAUDE.md`, that does not exist in the
               checkout the template is read from: a step cites the
               instrument it runs, and a citation that does not resolve
               re-derives nothing and runs nothing;
  structure    a missing or repeated marker, an overlay that is not a JSON
               object, a table row that repeats a name.

WHAT IT DOES NOT CHECK. Whether a step restates policy instead of citing it,
and whether a cited section number says what the step claims: those are a
reviewer's reading. A value's own correctness (a mandate that has expired, a
cap the owner did not set) is the session's.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = ROOT / "tools/audit/seat/sweep_template.md"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ref_privacy import HOME_DIR  # noqa: E402  (the host-path grammar's one owner)

BEGIN, END = "<!-- sweep:begin -->", "<!-- sweep:end -->"
PLACEHOLDER = re.compile(r"\{\{([A-Za-z0-9_]*)\}\}")
TABLE_ROW = re.compile(r"^\|\s*`([A-Za-z0-9_]+)`\s*\|")
CITED = re.compile(r"`((?:tools|tests|dev|\.github)/[^`\s{}<>*]+|CLAUDE\.md)[^`]*`")
HOST = re.compile(HOME_DIR)


class Refused(Exception):
    pass


def declared(text: str) -> list[str]:
    """The names in the `## Placeholders` table, in order; a repeat is refused."""
    names, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip() == "## Placeholders"
            continue
        m = TABLE_ROW.match(line) if inside else None
        if m:
            if m.group(1) in names:
                raise Refused(f"structure: the placeholder table declares `{m.group(1)}` twice")
            names.append(m.group(1))
    if not names:
        raise Refused("structure: the template has no `## Placeholders` table rows")
    return names


def body(text: str) -> str:
    if text.count(BEGIN) != 1 or text.count(END) != 1 or text.index(BEGIN) > text.index(END):
        raise Refused(f"structure: the template needs exactly one {BEGIN} before exactly one {END}")
    return text[text.index(BEGIN) + len(BEGIN):text.index(END)].strip("\n") + "\n"


def citations(text: str, root: Path) -> list[str]:
    """Every cited tree path that does not exist under root."""
    return sorted({m.group(1) for m in CITED.finditer(text) if not (root / m.group(1)).exists()})


def value_text(name: str, v) -> str:
    if isinstance(v, bool) or not isinstance(v, (str, int)):
        raise Refused(f"unfilled: `{name}` is a {type(v).__name__}, not a string or an integer")
    s = str(v)
    if not s.strip():
        raise Refused(f"unfilled: `{name}` is empty")
    if "\n" in s or "{{" in s:
        raise Refused(f"unfilled: `{name}` holds a newline or `{{{{`")
    return s


def render(template: str, overlay, root: Path = ROOT) -> str:
    if not isinstance(overlay, dict):
        raise Refused("structure: the overlay is not a JSON object")
    names = declared(template)
    sweep = body(template)
    used = PLACEHOLDER.findall(sweep)
    unknown = sorted({n for n in used if n not in names} | {k for k in overlay if k not in names})
    if unknown:
        raise Refused("unknown: " + ", ".join(f"`{n}`" for n in unknown) + " not in the placeholder table")
    unused = [n for n in names if n not in used]
    if unused:
        raise Refused("unused: " + ", ".join(f"`{n}`" for n in unused) + " declared and never used by the sweep")
    missing = [n for n in names if n not in overlay]
    if missing:
        raise Refused("unfilled: the overlay omits " + ", ".join(f"`{n}`" for n in missing))
    values = {n: value_text(n, overlay[n]) for n in names}
    bad = citations(template, root)
    if bad:
        raise Refused("citation: " + ", ".join(f"`{p}`" for p in bad) + " cited and not in the tree")
    out, spans, pos = [], [], 0
    for m in PLACEHOLDER.finditer(sweep):
        out.append(sweep[pos:m.start()])
        start = sum(map(len, out))
        out.append(values[m.group(1)])
        spans.append((start, start + len(values[m.group(1)])))
        pos = m.end()
    out.append(sweep[pos:])
    text = "".join(out)
    for m in HOST.finditer(text):
        if not any(a <= m.start() and m.end() <= b for a, b in spans):
            line = text.count("\n", 0, m.start()) + 1
            raise Refused(f"host-path: rendered line {line} names a home directory no overlay value supplied")
    return text


def self_test() -> int:
    passed = failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + cond, failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    def refusal(template: str, overlay, root: Path = ROOT) -> str:
        try:
            render(template, overlay, root)
        except Refused as e:
            return str(e)
        except Exception as e:  # a mutant that crashes reads as a failed check, not a dead run
            return f"crashed: {e.__class__.__name__}"
        return ""

    home = "/" + "Users" + "/someone"  # built at run time: no tracked line names a home
    tracked = TEMPLATE.read_text(encoding="utf-8")
    names = declared(tracked)
    full = {n: f"<{n}>" for n in names}
    full["local_seat_cap"] = 8
    try:
        text = render(tracked, full)
        ok = all(f"<{n}>" in text for n in names if n != "local_seat_cap") and "{{" not in text
    except Refused as e:
        print(f"    {e}")
        ok = False
    check("the tracked template renders from a complete overlay, every placeholder filled (null control)", ok)
    check("the tracked template cites only paths that exist", citations(tracked, ROOT) == [])
    check("the tracked template's sweep names no host", not HOST.search(body(tracked)))

    mini = "## Placeholders\n\n| `a` | x |\n| `b` | y |\n\n## Other\n\n" + BEGIN + "\nrun {{a}} then {{b}}\n" + END + "\n"
    check("a minimal template renders (null control for the refusals below)",
          render(mini, {"a": "A", "b": 2}) == "run A then 2\n")
    check("an omitted placeholder is refused as unfilled", refusal(mini, {"a": "A"}).startswith("unfilled"))
    check("an empty value is refused as unfilled", refusal(mini, {"a": "A", "b": " "}).startswith("unfilled"))
    check("a boolean value is refused", refusal(mini, {"a": "A", "b": True}).startswith("unfilled"))
    check("a null value is refused", refusal(mini, {"a": "A", "b": None}).startswith("unfilled"))
    check("a value holding {{ is refused (no second pass)",
          refusal(mini, {"a": "{{b}}", "b": "B"}).startswith("unfilled"))
    check("a value holding a newline is refused", refusal(mini, {"a": "A\nB", "b": "B"}).startswith("unfilled"))
    check("an overlay key the table does not declare is refused as unknown",
          refusal(mini, {"a": "A", "b": "B", "c": "C"}).startswith("unknown"))
    undeclared = mini.replace("{{b}}", "{{b}} {{z}}")
    check("a sweep placeholder the table does not declare is refused as unknown",
          refusal(undeclared, {"a": "A", "b": "B"}).startswith("unknown"))
    check("a declared placeholder the sweep never uses is refused",
          refusal(mini.replace(" then {{b}}", ""), {"a": "A", "b": "B"}).startswith("unused"))
    check("a repeated table row is refused",
          refusal(mini.replace("| `b` | y |", "| `a` | y |"), {"a": "A"}).startswith("structure"))
    check("a missing end marker is refused", refusal(mini.replace(END, ""), {"a": "A", "b": "B"}).startswith("structure"))
    check("a non-object overlay is refused", refusal(mini, ["A", "B"]).startswith("structure"))

    literal = mini.replace("run {{a}}", "run " + home + "/x {{a}}")
    check("a home directory written in the template is refused",
          refusal(literal, {"a": "A", "b": "B"}).startswith("host-path"))
    check("the same home directory supplied by an overlay value renders (null control)",
          render(mini, {"a": home + "/x", "b": "B"}) == "run " + home + "/x then B\n")
    straddle = mini.replace("run {{a}}", "run /Users{{a}}")
    check("a home directory straddling template text and a value is refused",
          refusal(straddle, {"a": "/someone", "b": "B"}).startswith("host-path"))

    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "tools/audit/seat").mkdir(parents=True)
        (root / "tools/audit/seat/real.sh").write_text("", encoding="utf-8")
        cite = mini.replace("then {{b}}", "then {{b}} with `tools/audit/seat/real.sh --x` and `tools/audit/seat/gone.sh`")
        check("a cited instrument that is not in the tree is refused",
              refusal(cite, {"a": "A", "b": "B"}, root) == "citation: `tools/audit/seat/gone.sh` cited and not in the tree")
        check("a cited instrument that exists passes, arguments and all (null control)",
              refusal(cite.replace(" and `tools/audit/seat/gone.sh`", ""), {"a": "A", "b": "B"}, root) == "")
    print(f"sweep_render self-test: {passed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--overlay", type=Path, help="the session's JSON overlay")
    ap.add_argument("--template", type=Path, default=TEMPLATE)
    ap.add_argument("--out", type=Path, help="write the rendered sweep here instead of stdout")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.overlay is None:
        ap.error("--overlay is required")
    try:
        overlay = json.loads(a.overlay.read_text(encoding="utf-8"))
        text = render(a.template.read_text(encoding="utf-8"), overlay)
    except (OSError, ValueError) as e:
        print(f"sweep_render: REFUSED structure: {e.__class__.__name__}: {e}", file=sys.stderr)
        return 1
    except Refused as e:
        print(f"sweep_render: REFUSED {e}", file=sys.stderr)
        return 1
    if a.out:
        a.out.write_text(text, encoding="utf-8")
        print(f"sweep_render: wrote {len(text.splitlines())} lines to {a.out.name}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
