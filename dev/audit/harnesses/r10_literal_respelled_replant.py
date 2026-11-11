"""R10-BRIEFS-FOLD: are #2373 round 3's two open spellings of `literal_clone_copies` still open?

D7's M7 says a clone-copy drop counts only where the copies are gone from the
source, because the census folds spellings it knows (C20, C21) and not values.
This re-plants the two spellings the #2373 round-3 review measured open, on a
copy of the tree's package: every copy of `_number(1, 24, 1, slider=True)` in
config_flow after the first is respelled with its bound as a constant
expression (`expr`: `12 * 2`) or a class attribute (`cls`: `_H.L0`, `L0 = 24`).
Nothing is deduplicated, so a sound census reads each arm flat.

    python3 dev/audit/harnesses/r10_literal_respelled_replant.py     (from the tree root)

Metric, one line per arm: `RESULT arm=<name> literal_clone_copies=<n> verdict=<v>`,
the census on the copy and score.py's verdict against the unplanted copy.
  base   the unplanted copy; the reference, verdict NULL against itself (null control)
  expr   still open while it reads below base and IMPROVES
  cls    the same, for the class-attribute spelling
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path.cwd()
SPELLED = "_number(1, 24, 1, slider=True)"
ARMS = {"base": None, "expr": "_number(1, 12 * 2, 1, slider=True)", "cls": "_number(1, _H.L0, 1, slider=True)"}


def plant(dst, respelled):
    shutil.copytree(ROOT / "custom_components", dst / "custom_components")
    if respelled is None:
        return
    p = dst / "custom_components/heatpump_optimizer/config_flow.py"
    parts = p.read_text().split(SPELLED)
    if len(parts) < 4:
        sys.exit(f"config_flow carries {len(parts) - 1} copies of {SPELLED}; this harness needs three or more")
    out = parts[0] + SPELLED + parts[1] + "".join(respelled + rest for rest in parts[2:])
    if "_H.L0" in respelled:
        i = out.index("\ndef _number(")
        out = out[:i] + "\n\nclass _H:\n    L0 = 24\n" + out[i:]
    p.write_text(out)


def vector(tree, out):
    out.write_text(subprocess.run([sys.executable, "tools/audit/archscore/vector.py", str(tree)], cwd=ROOT,
                                  check=True, capture_output=True, text=True).stdout)
    data = json.loads(out.read_text())
    return data.get("metrics", data)["literal_clone_copies"]


with tempfile.TemporaryDirectory() as work:
    work = pathlib.Path(work)
    for arm, respelled in ARMS.items():
        plant(work / arm, respelled)
        copies = vector(work / arm, work / f"{arm}.json")
        delta = subprocess.run([sys.executable, "tools/audit/archscore/score.py", "--delta", str(work / "base.json"),
                                str(work / f"{arm}.json")], cwd=ROOT, check=True, capture_output=True, text=True).stdout
        print(f"RESULT arm={arm} literal_clone_copies={copies} verdict={json.loads(delta)['verdict']}")
