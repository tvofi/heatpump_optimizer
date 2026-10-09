"""The planted cases, every one a scripted edit of one pinned tree.

    perturb/      edits of the pin: GOOD moves (G*), BAD moves (B*), behaviour-neutral nulls (N*)
    controls.py   each metric's control (adds one instance), fix (removes one) and null (rename/reformat)
    redteam/      the attempts to raise the score without improving the architecture, plus a rename null

A case is ``(id, label, base, apply)``. ``base`` is the tree a case is compared against: the pin, or
another case's tree (``a3_import_cycles_fix`` is applied on top of its control). Labels are the case
author's, recorded before any measurement: GOOD / BAD / NULL; a red-team attempt is GAME, expected
never to read IMPROVES (``tests/arch_score.py`` pins it); KNOWN-OPEN is a GAME expected to read IMPROVES.

The scripts anchor on the pin's text and assert each anchor occurs once: a tree that is not the pin
fails loudly. The pin is a commit on ``main``, never rewritten.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))

PINNED = "7952d8f9e4fbe9945bc8742e8dc02be8fbe4582c"
BASE = "_base"
# Attempts the counters do not close, expected IMPROVES; a fix flips one and the check asks for the re-record.
# 04h, 04i and 04j left this set in R9-EG-A2 (C3 joins a clone across any gap). 04zz1 splits a copy across
# blocks, which no window inside one block can join (ABOUT.md, "Interleaved junk").
KNOWN_OPEN = {"04zz1_dup_wrapsplit_uncharged"}


def extract_pin(into: Path) -> Path:
    """The pinned package (and seam map the perturbation scripts edit) under ``into``."""
    try:
        archive = subprocess.run(
            ["git", "-C", str(REPO), "archive", PINNED, "custom_components", "tests/seam_map.json"],
            capture_output=True, check=True).stdout
    except subprocess.CalledProcessError as err:
        raise SystemExit(f"the pinned commit {PINNED[:8]} is not in this clone ({err.stderr.decode()[-200:].strip()}); "
                         "a shallow clone is the environment, not the tree: git fetch --unshallow origin main")
    into.mkdir(parents=True, exist_ok=True)
    subprocess.run(["tar", "-x", "-C", str(into)], input=archive, check=True)
    return into


def _script(path: Path, tree: Path) -> None:
    subprocess.run([sys.executable, str(path), str(tree)], check=True, capture_output=True, text=True)


def cases() -> list[dict]:
    import controls
    out: list[dict] = []
    for p in sorted((HERE / "perturb").glob("[GBN]*.py")):
        out.append({"id": f"a1_{p.stem}", "label": {"G": "GOOD", "B": "BAD", "N": "NULL"}[p.stem[0]],
                    "base": BASE, "desc": p.stem, "apply": lambda tree, p=p: _script(p, tree)})
    for metric, arms in controls.plan().items():
        for arm, label in (("control", "BAD"), ("control_write", "BAD"), ("fix", "GOOD"), ("null", "NULL")):
            if arm not in arms:
                continue
            desc, edit = arms[arm]
            on_control = arm == "fix" and arms.get("fix_on") == "control"
            apply = (lambda tree, e=edit, c=arms["control"][1]: (c(tree), e(tree))) if on_control else edit
            out.append({"id": f"a3_{metric}_{arm}", "label": label,
                        "base": f"a3_{metric}_control" if on_control else BASE,
                        "desc": f"{metric} {arm}: {desc}", "apply": apply})
    for p in sorted((HERE / "redteam").glob("[0-9]*.py")):
        out.append({"id": f"rt_{p.stem}", "label": "NULL" if p.stem.startswith("00_") else "KNOWN-OPEN" if p.stem in KNOWN_OPEN else "GAME",
                    "base": BASE, "desc": (p.read_text().split('"""')[1].strip().splitlines() or [""])[0],
                    "apply": lambda tree, p=p: _script(p, tree)})
    return out


def build(case: dict, base: Path, work: Path) -> Path:
    """A fresh copy of the pin (or of the case's base) with the case applied."""
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(base, work)
    case["apply"](work)
    return work
