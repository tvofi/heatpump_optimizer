"""The Python-side readers of agreement.mjs, run as their own step.

    python3 -I .claude/workflows/agreement_py.py --out FILE   # writes the JSON
    python3 -I .claude/workflows/agreement_py.py --run        # writes it, then runs agreement.mjs on it

agreement.mjs compares readers of one governance concept (class I4). The
readers written in Python load production and test code (structure.py,
stamp.py, delivery_status.py, governance_cost.py). They run here, under
`python3 -I` after the job's restore from the base, so a pull request cannot
change a reader it is graded by (codeowners_gap.py reads the interpreter off
the line that starts the process); agreement.mjs only reads the JSON this
writes and never names those files.
"""
import ast
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "tools/release")]
from layout import locate  # noqa: E402  the reorganisation's move map (R9-RO-2)
# R9-RO-8: D11's library moved under dev/audit/rounds/. locate() names it where it is.
sys.path.insert(0, str(ROOT / Path(locate("tools/audit/round4/D11/governance_cost.py")).parent))


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def merge_subjects():
    since = git("describe", "--tags", "--abbrev=0", "--match", "v6.5.0").strip() or "v6.5.0"
    live = [s for s in git("log", "--first-parent", "--format=%s", f"{since}..HEAD").split("\n") if s]
    shapes = ["Merge pull request #1052 from tvofi/fix/d11-pins", "fix: a squash (#1234)",
              "v6.7.1: stamp", "ci: re-record closures"]
    return list(dict.fromkeys(live + shapes))


def merge():
    import delivery_status as d
    import stamp
    out = {}
    for s in merge_subjects():
        n = d.subject_number(s)
        out[s] = {"stamp": stamp.pr_from_subject(s), "delivery_status": str(n) if n is not None else None}
    return out


def structure_rows():
    import structure
    # Boundary items the live tree may not hold (D7-s3-02): a class nothing
    # references whose methods only call each other, and one a live function
    # reaches. Both readers must call the first dead and the second live, so a
    # reader that stops finding dead members (`dead = []`) disagrees here.
    probe = (
        "class ProbeOrphanKind:\n"
        "    def probe_orphan_run(self):\n        return self.probe_orphan_help()\n"
        "    def probe_orphan_help(self):\n        return 1\n"
        "class ProbeUsedKind:\n"
        "    def probe_used_go(self):\n        return 1\n"
        "def probe_entry():\n    return ProbeUsedKind().probe_used_go()\n"
    )
    probe_path = structure.PACKAGE_DIR / "zz_agreement_probe.py"
    trees = structure.module_trees() + [(probe_path, ast.parse(probe))]
    pkg = structure.Package(trees)
    dead, _ = structure.dead_members(pkg)
    dead_set = {(r, c, m) for r, c, m, _ in dead}
    bound = structure.bound_references(trees)
    rows = {}
    for (mod, cname), cls in pkg.classes.items():
        rel = pkg.mods[mod][0]
        ms = [i.name for i in cls.body if isinstance(i, (ast.FunctionDef, ast.AsyncFunctionDef))
              and not (i.name.startswith("__") and i.name.endswith("__"))]
        if not ms:
            continue
        flow = any(getattr(b, "id", getattr(b, "attr", "")).endswith(("ConfigFlow", "OptionsFlow")) for b in cls.bases)
        rows[f"{rel}::{cname}"] = {
            "bound": ((rel, cname) in bound) or cname in structure.HA_CONVENTION_NAMES or flow,
            "live_methods": any((rel, cname, m) not in dead_set for m in ms)}
    if not rows:
        raise SystemExit("no production class measured")
    return rows


def job_ids(text):
    i = text.rfind("\njobs:\n")
    return set(re.findall(r"^  ([A-Za-z][\w-]*):", text[i:], re.M)) if i >= 0 else set()


def governance_jobs():
    spec = importlib.util.spec_from_file_location("gc", locate("tools/audit/round4/D11/governance_cost.py"))
    gc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gc)
    src = Path("tests/entities.py").read_text()
    m = re.search(r"_GOV_FILES = \[(.*?)\]", src, re.S)
    files = re.findall(r'"(\.github/[^"]+\.yml)"', m.group(1)) if m else []
    w = re.search(r'^_GOV_WF = "([^"]+)"', src, re.M)
    if m and "_GOV_WF" in m.group(1) and w:
        files.append(w.group(1))
    if not files:
        raise SystemExit("entities.py: no _GOV_FILES list")
    pin = {"briefs"}
    for f in files:
        pin |= job_ids(Path(f).read_text())
    jobs = set()
    for f in sorted(Path(".github/workflows").glob("*.y*ml")):
        jobs |= job_ids(f.read_text())
    return {"jobs": sorted(jobs), "gov": sorted(gc.GOV), "pin": sorted(pin)}


def main(argv):
    data = {"merge": merge(), "structure": structure_rows(), "governance_jobs": governance_jobs()}
    if argv[:1] == ["--out"] and len(argv) == 2:
        Path(argv[1]).write_text(json.dumps(data))
        return 0
    if argv == ["--run"]:
        out = ROOT / ".agreement-py.json"
        out.write_text(json.dumps(data))
        try:
            ag = Path(__file__).with_name("agreement.mjs")
            if not ag.is_file():
                ag = ROOT / ".claude/workflows/agreement.mjs"
            return subprocess.run(["node", str(ag), "--py-json", str(out)], cwd=ROOT).returncode
        finally:
            out.unlink(missing_ok=True)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
