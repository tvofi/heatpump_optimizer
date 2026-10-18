"""Reviewer's round-3 plants (review-2373): the next spellings of the round-2 constant fold, nothing improved."""
import shutil, sys
from pathlib import Path
S = Path(sys.argv[1]); HEAD = S / "head3"
sys.path.insert(0, str(HEAD / "tools" / "audit"))
from archscore.metrics import literal_clones
PKG = Path("custom_components/heatpump_optimizer")
spelled = "_number(1, 24, 1, slider=True)"
def fresh(name):
    root = S / "plants" / name
    shutil.rmtree(root, ignore_errors=True)
    (root / PKG).parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(HEAD / PKG, root / PKG)
    return root
def plant(name, repl, header):
    r = fresh(name); p = r / PKG / "config_flow.py"; s = p.read_text()
    parts = s.split(spelled); out = parts[0] + spelled + parts[1]
    for i, rest in enumerate(parts[2:]):
        out += repl(i) + rest
    out = out.replace("\ndef _number(", "\n" + header(len(parts) - 2) + "\n\ndef _number(", 1)
    p.write_text(out); compile(out, str(p), "exec")
    print(f"RESULT {name} literal_clone_copies=186->{literal_clones.measure(r)['value']}")
# P6: class-attribute constants (class _H: L0 = 24 ...; _H.L0)
plant("P6_class_attr", lambda i: f"_number(1, _RtH.L{i}, 1, slider=True)",
      lambda n: "class _RtH:\n" + "".join(f"    L{i} = 24\n" for i in range(n)))
# P7: a constant spelled as an equal-valued expression (24 as 12 * 2, 20 + 4, ...)
exprs = ["12 * 2", "20 + 4", "48 // 2"]
plant("P7_constant_expr", lambda i: f"_number(1, {exprs[i]}, 1, slider=True)", lambda n: "")
