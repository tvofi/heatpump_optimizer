"""Catch-up verifier arch-b, V2 for ARCH2-s5 F1 and the hot_water_pumps label (static, not flow-driven).

Metrics (AST over config_flow.py at --root, default cwd):
  wizard_selector_calls = selector-builder calls (_number, _select, _entity_of, _text, _bool, _duration,
      selector.*Selector) inside ``vol.Optional/vol.Required`` dict entries OUTSIDE the _OPTION_FIELDS
      tuple, whose key constant also has an _OPTION_FIELDS row (a second construction of a registered
      key's widget).
  label_vs_menu = _OPTION_PAGES labels that differ from en.json options.step.{init,advanced}.menu_options
  label_vs_title = _OPTION_PAGES labels that differ from en.json options.step.<page>.title (second oracle)
Null control: label_vs_menu over sv.json must count only real Swedish text (every label differs), so the
  harness reports en/sv side by side; the en count is the finding, the sv count proves the compare runs.
Perturbation: --mislabel PAGE edits that page's code label in memory; label_vs_menu rises by 1.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/arch-b/v2_s5_flow.py [--root DIR] [--mislabel PAGE]

Expected at 9061fbd3d: label_vs_menu=1 (hot_water_pumps). Counts only; writes nothing.
"""
import ast
import json
import sys
from pathlib import Path

root = Path(sys.argv[sys.argv.index("--root") + 1]) if "--root" in sys.argv else Path.cwd()
pkg = root / "custom_components" / "heatpump_optimizer"
src = (pkg / "config_flow.py").read_text()
tree = ast.parse(src)
BUILDERS = {"_number", "_select", "_entity_of", "_text", "_bool", "_duration", "_entities_of"}

reg_keys, reg_nodes, pages = set(), set(), {}
for node in ast.walk(tree):
    if isinstance(node, (ast.AnnAssign, ast.Assign)):
        tgt = node.target if isinstance(node, ast.AnnAssign) else node.targets[0]
        name = getattr(tgt, "id", None)
        if name == "_OPTION_FIELDS":
            for sub in ast.walk(node.value):
                reg_nodes.add(id(sub))
                if isinstance(sub, ast.Call) and getattr(sub.func, "id", "") == "_F" and len(sub.args) > 1:
                    reg_keys.add(ast.unparse(sub.args[1]))
        if name == "_OPTION_PAGES":
            for sub in ast.walk(node.value):
                if isinstance(sub, ast.Call) and getattr(sub.func, "id", "") == "_P":
                    pages[sub.args[0].value] = sub.args[1].value


def is_builder(call):
    f = call.func
    n = getattr(f, "id", None) or getattr(f, "attr", "")
    return n in BUILDERS or n.endswith("Selector")


second = 0
for node in ast.walk(tree):
    if isinstance(node, ast.Dict) and id(node) not in reg_nodes:
        for k, v in zip(node.keys, node.values):
            if (isinstance(k, ast.Call) and getattr(k.func, "attr", "") in ("Optional", "Required")
                    and k.args and ast.unparse(k.args[0]) in reg_keys
                    and isinstance(v, ast.Call) and is_builder(v)):
                second += 1
print(f"RESULT registry_keys={len(reg_keys)} count")
print(f"RESULT wizard_selector_calls={second} count")

if "--mislabel" in sys.argv:
    pages[sys.argv[sys.argv.index("--mislabel") + 1]] = "MISLABELLED"
for lang in ("en", "sv"):
    tr = json.loads((pkg / "translations" / f"{lang}.json").read_text())["options"]["step"]
    menu = {**tr["init"].get("menu_options", {}), **tr["advanced"].get("menu_options", {})}
    dm = [p for p, lab in pages.items() if p in menu and menu[p] != lab]
    dt = [p for p, lab in pages.items() if tr.get(p, {}).get("title") not in (None, lab)]
    print(f"RESULT {lang}_label_vs_menu={len(dm)} of {sum(p in menu for p in pages)} {','.join(dm[:4]) if lang == 'en' else ''}")
    print(f"RESULT {lang}_label_vs_title={len(dt)} of {sum(p in tr for p in pages)} {','.join(dt[:6]) if lang == 'en' else ''}")
