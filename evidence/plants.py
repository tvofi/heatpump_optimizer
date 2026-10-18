"""Reviewer's own plants (review-2373, fix-review.md step 14): the diff's kind of move, nothing improved."""
import re, shutil, subprocess, sys
from pathlib import Path
S = Path("/Users/timmalmstrom/hpo-seats/r10s3/review-2373")
HEAD = S / "head"
sys.path.insert(0, str(HEAD / "tools" / "audit"))
from archscore.metrics import card, literal_clones
PKG = Path("custom_components/heatpump_optimizer")
def fresh(name):
    root = S / "plants" / name
    shutil.rmtree(root, ignore_errors=True)
    (root / PKG).parent.mkdir(parents=True)
    shutil.copytree(HEAD / PKG, root / PKG)
    return root
base = fresh("base")
lb, cb = literal_clones.measure(base)["value"], card.measure(base)["card_clone_copies"]
print(f"RESULT plant_base literal_clone_copies={lb} card_clone_copies={cb}")
spelled = "_number(1, 24, 1, slider=True)"
# P1: module-level aliases, one per copy (C21 covers locals only)
r = fresh("P1_module_alias"); p = r / PKG / "config_flow.py"; s = p.read_text()
parts = s.split(spelled); assert len(parts) == 5, len(parts)
out = parts[0] + spelled + parts[1]
for i, rest in enumerate(parts[2:]):
    out += f"_number(1, _LAST_HOUR_{i}, 1, slider=True)" + rest
out = out.replace("\ndef _number(", "\n" + "".join(f"_LAST_HOUR_{i} = 24\n" for i in range(3)) + "\n\ndef _number(", 1)
p.write_text(out); compile(out, str(p), "exec")
print(f"RESULT P1_module_alias literal_clone_copies={lb}->{literal_clones.measure(r)['value']}")
# P2: positional vs keyword spelling of the same arguments (C20 sorts keywords, never binds positionals)
r = fresh("P2_keyword_mix"); p = r / PKG / "config_flow.py"; s = p.read_text()
parts = s.split(spelled)
variants = ["_number(1, 24, step=1, slider=True)", "_number(1, maximum=24, step=1, slider=True)",
            "_number(minimum=1, maximum=24, step=1, slider=True)"]
out = parts[0] + spelled + parts[1]
for i, rest in enumerate(parts[2:]):
    out += variants[i] + rest
p.write_text(out); compile(out, str(p), "exec")
print(f"RESULT P2_keyword_mix literal_clone_copies={lb}->{literal_clones.measure(r)['value']}")
# P3: distinct no-op statements breaking 20-token windows in the card (nothing deduplicated)
r = fresh("P3_card_noop_split"); n = 0
for js in sorted((r / PKG / "www").glob("*.js")):
    src = js.read_text(); lines = src.split("\n"); outl = []
    for ln in lines:
        outl.append(ln)
        if ln.rstrip().endswith(";") and ln.lstrip().startswith(("const ", "let ")):
            n += 1
            if n % 2 == 0:
                outl.append(ln[:len(ln) - len(ln.lstrip())] + f"void {n};")
    js.write_text("\n".join(outl))
node = subprocess.run(["node", "--check", str(r / PKG / "www" / "heatpump-optimizer-card.js")], capture_output=True, text=True)
c3 = card.measure(r)
print(f"RESULT P3_card_noop_split inserted={n // 2} node_check_rc={node.returncode} card_clone_copies={cb}->{c3['card_clone_copies']} card_dead_definitions={c3['card_dead_definitions']}")
