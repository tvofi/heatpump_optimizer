"""Reviewer probe (review-2401): does the archscore card census see one more inline spelling of a card rule?
The finder's perturbation (ARCH2-s5 card_shapes.mjs): any shape spelled once more moves its count by 1."""
import re, shutil, subprocess, sys
from pathlib import Path
S = Path(sys.argv[1]); HEAD = S / "head"
sys.path.insert(0, str(HEAD / "tools" / "audit"))
from archscore.metrics import card
PKG = Path("custom_components/heatpump_optimizer"); JS = PKG / "www" / "heatpump-optimizer-card.js"
def fresh(name):
    r = S / "plants" / name; shutil.rmtree(r, ignore_errors=True)
    (r / PKG).parent.mkdir(parents=True, exist_ok=True); shutil.copytree(HEAD / PKG, r / PKG); return r
def report(name, r):
    c = card.measure(r)
    sh = subprocess.run(["node", str(S / "card_shapes.mjs"), str(r / JS)], capture_output=True, text=True).stdout
    tot = re.search(r"RESULT total=(\d+)", sh).group(1)
    chk = subprocess.run(["node", "--check", str(r / JS)], capture_output=True).returncode
    print(f"RESULT {name} node_check={chk} finder_shapes_total={tot} card_clone_copies={c['card_clone_copies']} card_dead_definitions={c['card_dead_definitions']}")
report("base", fresh("base"))
# P1: each of three rules spelled once more, inline, inside existing functions (one statement each, a guard on a fresh local)
r = fresh("P1_inline_spellings"); src = (r / JS).read_text()
lines = src.split("\n"); out = []; done = 0
rules = ['if (_rt.state === "unavailable" || _rt.state === "unknown") return;',
         'if (_rt === null || _rt === undefined || _rt === "") return;',
         'if (typeof _rt === "number" && Number.isFinite(_rt)) void 0;']
for i, ln in enumerate(lines):
    out.append(ln)
    m = re.match(r"^  (\w+)\(([^)]*)\) \{$", ln)  # a class method's opening line
    if m and done < 3 and m.group(1) not in ("constructor", "render", "if", "for", "while", "switch"):
        ind = "    "
        out.append(ind + "const _rt = this._rtProbe;")
        out.append(ind + rules[done]); done += 1
(r / JS).write_text("\n".join(out)); report(f"P1_inline_spellings(n={done})", r)
