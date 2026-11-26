"""Shared in-memory mutation helper for the D3-g44 probes (no production file is written)."""
import ast, os, sys, textwrap
from pathlib import Path
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "custom_components/heatpump_optimizer/manifest.json").is_file())
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import thermal_model as tm  # noqa: E402

TM_PATH = Path(tm.__file__)
LINES = TM_PATH.read_text().splitlines(keepends=True)


def mutant(cls, name, line, old, new):
    """Return the function `cls.name` recompiled from the file with `old`->`new` on file line `line` only."""
    tree = ast.parse("".join(LINES))
    node = next(f for c in ast.walk(tree) if isinstance(c, ast.ClassDef) and c.name == cls
                for f in c.body if isinstance(f, (ast.FunctionDef,)) and f.name == name)
    start = min([node.lineno] + [d.lineno for d in node.decorator_list])
    seg = LINES[start - 1: node.end_lineno]
    i = line - start
    assert seg[i].count(old) == 1, (line, seg[i])
    seg[i] = seg[i].replace(old, new, 1)
    src = textwrap.dedent("".join(seg))
    ns = dict(tm.__dict__)
    exec(compile("\n" * (start - 1) + src, str(TM_PATH), "exec"), ns)
    f = ns[name]
    return f.fget if isinstance(f, property) else f
