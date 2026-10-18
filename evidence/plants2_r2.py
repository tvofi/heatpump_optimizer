"""Reviewer's round-2 plants (review-2373): neighbours of the round-1 games, nothing improved."""
import shutil, subprocess, sys
from pathlib import Path
S = Path("/Users/timmalmstrom/hpo-seats/r10s3/review-2373")
HEAD = S / "head2"
sys.path.insert(0, str(HEAD / "tools" / "audit"))
from archscore.metrics import card, literal_clones
PKG = Path("custom_components/heatpump_optimizer")
def fresh(name):
    root = S / "plants" / name
    shutil.rmtree(root, ignore_errors=True)
    (root / PKG).parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(HEAD / PKG, root / PKG)
    return root
spelled = "_number(1, 24, 1, slider=True)"
# P4: bare empty statements ';' splitting card windows (drop_noops skips an empty run)
r = fresh("P4_card_empty_stmt"); n = 0
for js in sorted((r / PKG / "www").glob("*.js")):
    out = []
    for ln in js.read_text().split("\n"):
        out.append(ln)
        if ln.rstrip().endswith(";") and ln.lstrip().startswith(("const ", "let ")):
            n += 1
            if n % 2 == 0:
                out.append(ln[:len(ln) - len(ln.lstrip())] + ";")
    js.write_text("\n".join(out))
rc = subprocess.run(["node", "--check", str(r / PKG / "www" / "heatpump-optimizer-card.js")], capture_output=True).returncode
print(f"RESULT P4_card_empty_stmt inserted={n // 2} node_check_rc={rc} card_clone_copies=108->{card.measure(r)['card_clone_copies']}")
# P5: module constants read through a module attribute (from . import const as _c; _c.X)
r = fresh("P5_literal_module_attr"); p = r / PKG / "config_flow.py"; s = p.read_text()
parts = s.split(spelled); out = parts[0] + spelled + parts[1]
for i, rest in enumerate(parts[2:]):
    out += f"_number(1, _rt_c.LAST_HOUR_{i}, 1, slider=True)" + rest
out = out.replace("\ndef _number(", "\nfrom . import const as _rt_c\n\n\ndef _number(", 1)
p.write_text(out)
cp = r / PKG / "const.py"; cp.write_text(cp.read_text() + "".join(f"\nLAST_HOUR_{i} = 24" for i in range(len(parts) - 2)) + "\n")
compile(out, str(p), "exec")
print(f"RESULT P5_literal_module_attr literal_clone_copies=184->{literal_clones.measure(r)['value']}")
