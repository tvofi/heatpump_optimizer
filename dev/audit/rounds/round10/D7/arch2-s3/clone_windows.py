"""Print the shared gapped-clone windows (the statement pairs) that join the named functions.

The score's C3 census (``counters.gapped_clones``) says WHICH functions are one clone class; this
prints WHAT they share, so a reader can tell a real duplicated computation from two functions that
happen to share a guard. Same window definition, same normalisation, re-implemented only to keep
the window text (the census keeps the digest).

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s3/clone_windows.py [--root ROOT] NAME [NAME ...]

NAME is ``module.function`` (e.g. ``tariff._smooth_topk_sum``). Counts only; contention-immune.
"""
import argparse
import ast
import hashlib
import sys
import tempfile
from collections import defaultdict
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


REPO = repo_root(__file__)
sys.path.insert(0, str(REPO / "tools" / "audit"))
from archscore import counters as K  # noqa: E402
from archscore import vector  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("names", nargs="+")
    a = ap.parse_args()
    want = set(a.names)
    with tempfile.TemporaryDirectory() as tmp:
        flat = Path(tmp)
        K.flatten(Path(a.root).resolve(), flat, inline=True)
        S = vector.load_structure(flat)
        windows = defaultdict(lambda: [set(), ""])
        for path in sorted(S.PACKAGE_DIR.glob("*.py")):
            tree = ast.parse(path.read_text())
            modalias = S._module_aliases(tree)
            for fn in S.all_functions(tree):
                tag = f"{path.stem}.{fn.name}"
                local = S._local_names(fn)
                stack = [fn]
                while stack:
                    node = stack.pop()
                    stack += [c for c in ast.iter_child_nodes(node)
                              if not isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef))]
                    blocks = [getattr(node, f) for f in ("body", "orelse", "finalbody")
                              if isinstance(getattr(node, f, None), list) and getattr(node, f)
                              and isinstance(getattr(node, f)[0], ast.stmt)]
                    for block in blocks + [h.body for h in getattr(node, "handlers", []) or []]:
                        block = [s for s in block if not S._is_docstring(s)
                                 and not isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
                        size = [sum(1 for _ in ast.walk(s)) for s in block]
                        for i in range(len(block)):
                            for j in range(i + 1, len(block)):
                                if size[i] + size[j] < S.DUP_MIN_NODES:
                                    continue
                                names = {}
                                key = K._LOCAL.sub(lambda m: names.setdefault(m.group(1), f"v{len(names)}"),
                                                   K._statement_form(S, block[i], local, modalias)
                                                   + K._statement_form(S, block[j], local, modalias))
                                d = hashlib.sha1(key.encode()).hexdigest()
                                windows[d][0].add(f"{tag}:{fn.lineno}")
                                if not windows[d][1]:
                                    windows[d][1] = (ast.unparse(block[i]).splitlines()[0][:110]
                                                     + "  ||  " + ast.unparse(block[j]).splitlines()[0][:110])
        n = 0
        for owners, text in windows.values():
            hit = {o for o in owners if o.rsplit(":", 1)[0] in want}
            if len(hit) >= 2:
                n += 1
                print(f"[{', '.join(sorted(hit))}]\n    {text}")
        print(f"RESULT shared_windows={n} count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
