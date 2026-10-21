"""The Python-side readers of agreement.mjs, run as their own step.

    python3 -I tools/policy/agreement_py.py --out FILE   # writes the JSON
    python3 -I tools/policy/agreement_py.py --run        # writes it, then runs agreement.mjs on it
    python3 -I tools/policy/agreement_py.py --restore    # the restore precondition alone
    python3 -I tools/policy/agreement_py.py --self-test

agreement.mjs compares readers of one governance concept (class I4). The
readers written in Python load production and test code (structure.py,
stamp.py, delivery_status.py, governance_cost.py). They run here, under
`python3 -I` after the job's restore from the base, so a pull request cannot
change a reader it is graded by (codeowners_gap.py reads the interpreter off
the line that starts the process); agreement.mjs only reads the JSON this
writes and never names those files.

THE RESTORE PRECONDITION (#2423). Those answers are the base's only if every
file this reader loads was restored from the base. The wave-script job once
restored a hand-written list that had drifted, and on a head whose readers
agreed it read `divergent=2`: the base's reader ran against head copies of
`tests/delivery_status.py`, `tools/release/stamp.py` and what they load. So the
list is derived here, from this file's transitive import closure over the
directories it puts on sys.path plus every file it loads through
`locate("...")`, and `--out` and `--run` refuse to answer while a pathspec of
that job's "Restore the check source from the base commit" step misses one
(the file, a directory above it, or a glob whose `*` stays within one path
segment). The check lives in this file and not beside it because a program
added beside a pinned one runs as the pull request's own (governance.yml's
policy-docs restore note) and is a registry entry the base cannot carry.
"""
import ast
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "tools/release")]
from layout import locate  # noqa: E402  the reorganisation's move map (R9-RO-2)
# R9-RO-8: D11's library moved under dev/audit/rounds/. locate() names it where it is.
sys.path.insert(0, str(ROOT / Path(locate("tools/audit/round4/D11/governance_cost.py")).parent))


# --- the restore precondition ---------------------------------------------
WORKFLOW = ".github/workflows/governance.yml"
JOB = "wave-script"
# The directories this reader puts on sys.path, then what the modules it loads
# add: tests/, tools/release/, the D11 library's directory (both layouts),
# tools/policy/ and tools/audit/seat/ (budget_raise), and tools/seat/.
SEARCH = ("tools/policy", "", "tests", "tools/release", "tools/audit/seat",
          "tools/seat", "tools/audit/round4/D11", "dev/audit/rounds/round4/D11",
          "tools/audit/round6/D11/fix", "dev/audit/rounds/round6/D11/fix",
          ".claude/workflows")


def _resolve(root, mod):
    for d in SEARCH:
        p = (root / d / Path(*mod.split("."))).with_suffix(".py")
        if p.is_file():
            return p
    return None


def _loads(path):
    """(module names imported, paths loaded through locate())."""
    mods, dynamic = set(), []
    for n in ast.walk(ast.parse(path.read_text())):
        if isinstance(n, ast.Import):
            mods.update(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
            mods.add(n.module)
            # `from sub import nested` may load a module, not an attribute.
            mods.update(f"{n.module}.{a.name}" for a in n.names)
        elif (isinstance(n, ast.Call) and getattr(n.func, "id", getattr(n.func, "attr", "")) == "locate"
              and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)):
            dynamic.append(n.args[0].value)
    return mods, dynamic


def closure(root, reader):
    """Every .py file under root that `reader` loads, transitively, sorted."""
    base, seen, stack = root.resolve(), set(), [reader]
    while stack:
        p = stack.pop()
        try:
            rel = p.resolve().relative_to(base).as_posix()
        except ValueError:  # outside the tree: not the job's to restore
            continue
        if rel in seen:
            continue
        seen.add(rel)
        try:
            mods, dynamic = _loads(p)
        except (OSError, SyntaxError):
            continue
        stack += [r for r in map(lambda m: _resolve(root, m), mods) if r]
        for d in dynamic:
            q = root / d
            q = q if q.suffix == ".py" else q.with_suffix(".py")
            if q.is_file():
                stack.append(q)
    return sorted(seen)


def restore_specs(text):
    """The wave-script restore step's pathspecs, as written."""
    job = re.search(rf"^  {re.escape(JOB)}:\n(.*?)(?=^  [a-z][\w-]*:\n|\Z)", text, re.M | re.S)
    if not job:
        raise ValueError(f"no `{JOB}` job")
    step = re.search(r"- name: Restore the check source from the base commit\n(.*?)(?=\n      - |\Z)",
                     job.group(1), re.S)
    if not step:
        raise ValueError("no restore step in the job")
    listed = re.search(r'"\$PINNED" --(.*?)>\s*"\$RUNNER_TEMP/pinned\.list"',
                       step.group(1).replace("\\\n", " "), re.S)
    # Split on the single quote rather than match it with a regex, so this
    # reader adds no grammar agreement.mjs has to register.
    specs = listed.group(1).split("'")[1::2] if listed else []
    if not specs:
        raise ValueError("the restore step lists no pathspec")
    return specs


def covers(spec, rel):
    """Git pathspec semantics as far as the restore list uses them: a plain
    path is the file or a directory above it; a wildcard stays in one segment."""
    spec = spec.rstrip("/")
    if not any(ch in spec for ch in "*?["):
        return rel == spec or rel.startswith(spec + "/")
    pat = "".join("[^/]*" if c == "*" else "[^/]" if c == "?" else re.escape(c) for c in spec)
    return re.fullmatch(pat, rel) is not None


def restore_check(root, reader):
    """Print each closure file no restore pathspec covers; 0 when none."""
    try:
        files = closure(root, reader)
        specs = restore_specs((root / WORKFLOW).read_text())
    except (OSError, ValueError) as e:
        print(f"agreement_py restore: {e}")
        return 1
    missing = [f for f in files if not any(covers(s, f) for s in specs)]
    for f in missing:
        print(f"  UNRESTORED {f}: no {JOB} restore pathspec covers it")
    print(f"agreement_py restore: {len(files)} closure file(s), {len(files) - len(missing)} "
          f"covered by the {JOB} restore list, {len(missing)} missing")
    return 1 if missing else 0


def self_test():
    import contextlib
    import io
    passed = failed = 0

    def ck(name, ok):
        nonlocal passed, failed
        passed, failed = passed + ok, failed + (not ok)
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")

    def run(root):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = restore_check(root, root / "tools/policy/agreement_py.py")
        return rc, buf.getvalue()

    def workflow(specs):
        listed = "".join(f"            '{s}' \\\n" for s in specs)
        return ("jobs:\n  wave-script:\n    steps:\n"
                "      - name: Restore the check source from the base commit\n"
                "        run: |\n"
                '          git diff --name-only -z "$(git hash-object -t tree /dev/null)" "$PINNED" -- \\\n'
                f"{listed}"
                '            > "$RUNNER_TEMP/pinned.list"\n'
                "      - name: next\n        run: true\n"
                "  record:\n    steps:\n      - run: true\n")

    # A reader importing one module directly, one through `from`, and one
    # through locate(); each loads another, so only the closure -- not a
    # first-level read -- finds tests/deep.py and tools/release/stamp.py.
    files = {
        "tools/policy/agreement_py.py":
            "import delivery_status\nfrom helper import thing\ndef load():\n    locate('tools/x/dyn.py')\n",
        "tests/delivery_status.py": "import helper\n",
        "tests/helper.py": "import deep\n",
        "tests/deep.py": "from sub import nested\n",
        "tests/sub/nested.py": "X = 1\n",
        "tools/x/dyn.py": "import stamp\n",
        "tools/release/stamp.py": "X = 1\n",
        "tools/unused.py": "X = 1\n",
        "tools/dropped.py": "import stamp\n",
    }
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for rel, body in files.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(body)
        ck("the closure is transitive and includes a locate() load, not a file nothing imports",
           closure(root, root / "tools/policy/agreement_py.py")
           == ["tests/deep.py", "tests/delivery_status.py", "tests/helper.py", "tests/sub/nested.py",
               "tools/policy/agreement_py.py", "tools/release/stamp.py", "tools/x/dyn.py"])
        ck("a wildcard does not cross a slash, and a directory pathspec does",
           covers("tests/*.py", "tests/deep.py") and not covers("tests/*.py", "tests/sub/deep.py")
           and covers("tests", "tests/sub/deep.py") and covers("tests/deep.py", "tests/deep.py"))
        wf = root / WORKFLOW
        wf.parent.mkdir(parents=True)
        wf.write_text(workflow(["tests", "tools/policy/agreement_py.py", "tools/x/dyn.py",
                                "tools/release/stamp.py"]))
        ck("a list that covers the closure passes (null control)", run(root)[0] == 0)
        wf.write_text(workflow(["tests/delivery_status.py", "tests/helper.py", "tests/sub/nested.py",
                                "tools/policy/agreement_py.py", "tools/x/dyn.py", "tools/release/stamp.py"]))
        rc, out = run(root)
        ck("a list missing one transitive reader exits 1 and names it",
           rc == 1 and "UNRESTORED tests/deep.py" in out)
        wf.write_text(workflow(["tests/*.py", "tools/policy/agreement_py.py", "tools/x/dyn.py",
                                "tools/release/stamp.py"]))
        rc, out = run(root)
        ck("a wildcard pathspec over tests/ does not cover a nested file",
           rc == 1 and "UNRESTORED tests/sub/nested.py" in out)
        wf.write_text("jobs:\n  record:\n    steps:\n      - run: true\n")
        ck("a workflow with no wave-script job is refused, not read as covered", run(root)[0] == 1)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = main(["--out", str(root / "ag.json")], root=root, reader=root / "tools/policy/agreement_py.py")
        ck("and --out refuses to answer on it (the precondition, not a report)",
           rc == 1 and not (root / "ag.json").exists())
    print(f"agreement_py self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def merge_subjects():
    since = git("describe", "--tags", "--abbrev=0", "--match", "v6.5.0").strip() or "v6.5.0"
    live = [s for s in git("log", "--first-parent", "--format=%s", f"{since}..HEAD").split("\n") if s]
    shapes = ["Merge pull request #1052 from tvofi/fix/d11-pins", "fix: a squash (#1234)",
              "v6.7.1: stamp", "ci: re-record closures",
              # A hand merge's custom subject (5756f2b1, 07a09406): pinned here as
              # well as live, so a corpus window that moves keeps the shape.
              "Merge pull request #2379 (R10-SENSOR-PAYLOAD)",
              "Merge pull request #2401 (R10-ARCHSCORE-COVERAGE p5)",
              "Merge pull request #13: Broaden the disclaimer",
              # Null controls: no pull request is named, so every reader answers null.
              "Merge pull request from a fork", "Merge pull request #12x from a/b",
              "Record #424 W1-G14 merge in delivery-status", "Merge branch 'main' into fix/x"]
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


def budget_raise():
    """Whether a diff is a budget raise, read by budget_raise_gate.py's
    `raises_between` (what the budget-raise-gate check refuses) and by
    merge_train.py's `Train.raise_hold` (what the train holds at approve and
    queue_pre_flight.py PARKs; it calls the same method). #2401: the train
    keyed on the `*_budgets.json` path and stopped a head the gate passed. The
    corpus is every tracked budget file at HEAD under eight edits; both readers
    see the same two trees, the train's through its own `run`."""
    sys.path[:0] = [str(ROOT / "tools/policy"), str(ROOT / "tools/audit/seat")]
    import budget_raise_gate as g
    import merge_train as mt
    base, head = "b" * 40, "c" * 40
    files = [f for f in git("ls-files", f"*{g.SUFFIX}").split("\n") if f]
    if not files:
        raise SystemExit("no tracked budget file")

    def bump(text):  # the first numeric leaf, one up
        d = json.loads(text)
        for k, v in d.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                d[k] = v + 1
                return json.dumps(d, indent=1) + "\n"
        return json.dumps(dict(d, zz_agreement_probe=1), indent=1) + "\n"

    def sibling(text):  # #2401's shape: a new row beside the first numeric one, under its pattern
        d = json.loads(text)
        k = next((k for k, v in d.items() if isinstance(v, (int, float)) and not isinstance(v, bool)), "zz")
        return json.dumps(dict(d, **{f"{k}_agreement_probe": 0}), indent=1) + "\n"

    out = {}
    for f in files:
        text = Path(f).read_text()
        row = json.dumps(dict(json.loads(text), zz_agreement_new_row=0), indent=1) + "\n"
        for case, ends in (("same", (text, text)), ("new-row", (text, row)), ("sibling-row", (text, sibling(text))),
                           ("bump", (text, bump(text))),
                           ("unbump", (bump(text), text)), ("deleted", (text, None)), ("added", (None, text)),
                           ("unparsable", (text, text[:-3]))):
            world = {f: ends}

            def ls(sha, world=world):
                return [p for p, e in world.items() if e[0 if sha == base else 1] is not None] + ["README.md"]

            def show(sha, p, world=world):
                return world.get(p, (None, None))[0 if sha == base else 1]

            gate = bool(g.raises_between(base, head, ls, show)[1])

            def run(argv, cwd=None, stdin=None, world=world):
                got = mt.budget_fixture(world, argv, base)
                if got is not None:
                    return got
                if argv[:2] == ["git", "ls-tree"]:
                    return 0, "README.md\n"
                if argv[:3] == ["git", "merge-base", "origin/main"]:
                    return 0, base + "\n"
                if argv[:2] == ["gh", "api"] and "/reviews" in " ".join(argv):
                    return 0, "[[]]"
                return 1, f"agreement_py: no answer for {argv[:3]}"
            import tempfile
            with tempfile.TemporaryDirectory() as d:
                t = mt.Train("o/r", Path(d), None, "", (), 1, run=run)
                try:
                    train = bool(t.raise_hold(7, head, [f, "README.md"])[0])
                except mt.Stop as e:
                    train = f"STOP {e.step}: {e.why}"
            out[f"{f}:{case}"] = {"gate": gate, "train": train}
    return out


def main(argv, root=ROOT, reader=Path(__file__).resolve()):
    if argv == ["--self-test"]:
        return self_test()
    if argv == ["--restore"]:
        return restore_check(root, reader)
    if not (argv == ["--run"] or argv[:1] == ["--out"] and len(argv) == 2):
        print(__doc__)
        return 2
    if restore_check(root, reader):
        return 1  # the precondition: an answer from unrestored readers is no verdict
    data = {"merge": merge(), "structure": structure_rows(), "governance_jobs": governance_jobs(),
            "budget_raise": budget_raise()}
    if argv[0] == "--out":
        Path(argv[1]).write_text(json.dumps(data))
        return 0
    out = ROOT / ".agreement-py.json"
    out.write_text(json.dumps(data))
    try:
        ag = Path(__file__).with_name("agreement.mjs")
        if not ag.is_file():
            ag = ROOT / ".claude/workflows/agreement.mjs"
        return subprocess.run(["node", str(ag), "--py-json", str(out)], cwd=ROOT).returncode
    finally:
        out.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
