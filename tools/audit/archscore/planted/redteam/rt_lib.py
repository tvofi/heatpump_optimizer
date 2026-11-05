"""Shared helpers for the red-team attempt scripts (source-span rewriting)."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[3]  # tools/audit
sys.path.insert(0, str(TOOLS))
PKG_REL = "custom_components/heatpump_optimizer"


def pkg(root) -> Path:
    return Path(root) / PKG_REL


def metric(name: str, root):
    """Run one metric module on ROOT (used only to locate the sites an attempt rewrites)."""
    import importlib
    return importlib.import_module(f"archscore.metrics.{name}").measure(Path(root))


def structure(root):
    """``tests/structure.py`` re-pointed at ROOT: where an attempt locates what the score reads there."""
    from archscore import vector
    return vector.load_structure(Path(root).resolve())


def seg(src: str, node) -> str:
    return ast.get_source_segment(src, node)


def replace_nodes(path: Path, edits: list[tuple[ast.AST, str]]) -> int:
    """Replace each node's exact source span with new text (bottom-up, byte offsets)."""
    raw = path.read_text()
    lines = raw.splitlines(keepends=True)
    blines = [ln.encode() for ln in lines]
    starts = [0]
    for b in blines:
        starts.append(starts[-1] + len(b))
    data = b"".join(blines)
    spans = []
    for node, text in edits:
        a = starts[node.lineno - 1] + node.col_offset
        b = starts[node.end_lineno - 1] + node.end_col_offset
        spans.append((a, b, text.encode()))
    spans.sort(reverse=True)
    last = None
    for a, b, t in spans:
        if last is not None and b > last:
            raise SystemExit(f"overlapping edits in {path}")
        data = data[:a] + t + data[b:]
        last = a
    path.write_text(data.decode())
    return len(spans)


def insert_after_line(path: Path, lineno: int, text: str) -> None:
    lines = path.read_text().splitlines(keepends=True)
    lines.insert(lineno, text)
    path.write_text("".join(lines))


def coordinator_runs(src: str, pred, independent: bool = True) -> list[list[ast.stmt]]:
    """Runs of two or more adjacent statements of the coordinator class that ``pred`` accepts (and, when
    ``independent``, that read nothing an earlier statement of the run binds): the sites a packing attempt rewrites."""
    cls = next(n for n in ast.parse(src).body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")

    def names(e):
        return {n.id for n in ast.walk(e) if isinstance(n, ast.Name)}

    out = []
    for fn in ast.walk(cls):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for body in [fn.body] + [b for n in ast.walk(fn) for b in (getattr(n, "body", None), getattr(n, "orelse", None)) if isinstance(b, list)]:
            run: list[ast.stmt] = []
            for s in body + [None]:
                if s is not None and pred(s) and not (independent and names(s) & {n for r in run for n in names(r)}
                                                      and isinstance(s, ast.Assign)):
                    run.append(s)
                    continue
                if len(run) >= 2:
                    out.append(run)
                run = [s] if s is not None and pred(s) else []
    seen: set[int] = set()
    return [r for r in out if not (id(r[0]) in seen or seen.add(id(r[0])))]
