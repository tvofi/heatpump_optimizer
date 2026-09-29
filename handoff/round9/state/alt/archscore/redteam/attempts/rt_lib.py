"""Shared helpers for the red-team attempt scripts (source-span rewriting)."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

SCR = Path(__file__).resolve().parents[2]
A3 = SCR / "a3" / "metrics"
PKG_REL = "custom_components/heatpump_optimizer"


def pkg(root) -> Path:
    return Path(root) / PKG_REL


def metric(name: str, root):
    """Run one a3 metric on ROOT (used only to locate the sites an attempt rewrites)."""
    sys.path.insert(0, str(A3))
    mod = __import__(name)
    return mod.measure(Path(root))


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
