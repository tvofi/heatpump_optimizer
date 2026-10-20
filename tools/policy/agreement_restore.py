#!/usr/bin/env python3
"""Derive the wave-script restore list from the agreement reader's imports.

    python3 -I tools/policy/agreement_restore.py --print
    python3 -I tools/policy/agreement_restore.py --check
    python3 -I tools/policy/agreement_restore.py --self-test

WHY THIS EXISTS. governance.yml's `wave-script` job restores its check source
from the base commit (decision 0013) so a pull request cannot change a reader
it is graded by. `agreement_py.py` is that job's Python reader, and it loads
other modules: `import stamp` and `import delivery_status` in `merge()`,
`structure`, `layout`, the governance library it names through `locate()`, the
seat modules `merge_train.py` pulls in, and whatever those import in turn.
Before this check the restore list was a hand-written pathspec set, and it had
drifted: on a head whose readers agreed the job read `divergent=2` (#2423),
because the base's `agreement_py.py` ran against head copies of
`tests/delivery_status.py`, `tools/release/stamp.py`, `merge_train.py` and the
modules those load.

THE RULE. The list is the transitive import closure of the agreement reader
(`tools/policy/agreement_py.py`, or `.claude/workflows/agreement_py.py` when
that one is present), resolved over the directories that reader puts on
sys.path, plus every file it loads by path through `locate("...")`. Every
tracked `.py` file in that closure must be covered by a pathspec of the
wave-script job's "Restore the check source from the base commit" step: the
file itself, a directory containing it, or a glob whose `*` does not cross
`/`. `--check` names each closure file no pathspec covers and exits 1.
"""
from __future__ import annotations

import ast
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READERS = ("tools/policy/agreement_py.py", ".claude/workflows/agreement_py.py")
WORKFLOW = ".github/workflows/governance.yml"
JOB = "wave-script"
# The directories agreement_py.py puts on sys.path, then what the modules it
# loads add: tests/, tools/release/, the D11 library's directory, tools/policy/
# and tools/audit/seat/.
SEARCH = ("tools/policy", "", "tests", "tools/release", "tools/audit/seat",
          "tools/seat", "tools/audit/round4/D11", "dev/audit/rounds/round4/D11",
          "tools/audit/round6/D11/fix", "dev/audit/rounds/round6/D11/fix",
          ".claude/workflows")


def reader(root: Path) -> Path:
    for rel in READERS:
        if (root / rel).is_file():
            return root / rel
    raise SystemExit(f"agreement_restore: no agreement reader at "
                     f"{' or '.join(READERS)}")


def resolve(root: Path, mod: str) -> Path | None:
    for d in SEARCH:
        p = root / d / Path(*mod.split("."))
        if p.with_suffix(".py").is_file():
            return p.with_suffix(".py")
    return None


def imports_of(path: Path) -> tuple[set[str], list[str]]:
    """(module names imported, paths loaded through locate())."""
    tree = ast.parse(path.read_text())
    mods: set[str] = set()
    dynamic: list[str] = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods.update(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            if n.level == 0 and n.module:
                mods.add(n.module)
                # `from sub import nested` may load a module, not an attribute.
                mods.update(f"{n.module}.{a.name}" for a in n.names)
        elif isinstance(n, ast.Call):
            f = n.func
            name = getattr(f, "id", getattr(f, "attr", ""))
            if (name == "locate" and n.args
                    and isinstance(n.args[0], ast.Constant)
                    and isinstance(n.args[0].value, str)):
                dynamic.append(n.args[0].value)
    return mods, dynamic


def closure(root: Path) -> list[str]:
    """Every tracked .py file the agreement reader loads, relative to root."""
    seen: dict[str, bool] = {}
    base = root.resolve()
    stack = [reader(root)]
    while stack:
        p = stack.pop()
        try:
            rel = p.resolve().relative_to(base).as_posix()
        except ValueError:  # outside the tree: not ours to restore
            continue
        if rel in seen:
            continue
        seen[rel] = True
        try:
            mods, dynamic = imports_of(p)
        except (OSError, SyntaxError):
            continue
        for m in mods:
            r = resolve(root, m)
            if r:
                stack.append(r)
        for d in dynamic:
            q = root / d
            if q.is_file() and q.suffix == ".py":
                stack.append(q)
            elif q.with_suffix(".py").is_file():
                stack.append(q.with_suffix(".py"))
    return sorted(seen)


def restore_specs(text: str) -> list[str]:
    """The wave-script restore step's pathspecs, as written."""
    job = re.search(rf"^  {re.escape(JOB)}:\n(.*?)(?=^  [a-z][\w-]*:\n|\Z)",
                    text, re.M | re.S)
    if not job:
        raise ValueError(f"no `{JOB}` job")
    step = re.search(r"- name: Restore the check source from the base commit\n"
                     r"(.*?)(?=\n      - |\Z)", job.group(1), re.S)
    if not step:
        raise ValueError("no restore step in the job")
    body = step.group(1).replace("\\\n", " ")
    listed = re.search(r'"\$PINNED" --(.*?)>\s*"\$RUNNER_TEMP/pinned\.list"', body, re.S)
    # The pathspecs are single-quoted; split on the quote rather than match it
    # with a regex, so this tool adds no grammar agreement.mjs has to register.
    parts = listed.group(1).split("'") if listed else []
    specs = [p for i, p in enumerate(parts) if i % 2]
    if not specs:
        raise ValueError("the restore step lists no pathspec")
    return specs


def covers(spec: str, rel: str) -> bool:
    """Git pathspec semantics, as far as the restore list uses them: a plain
    path is itself or a directory above the file; a wildcard matches within
    one path segment."""
    spec = spec.rstrip("/")
    if not any(ch in spec for ch in "*?["):
        return rel == spec or rel.startswith(spec + "/")
    pat = "".join("[^/]*" if c == "*" else "[^/]" if c == "?" else re.escape(c)
                  for c in spec)
    return re.fullmatch(pat, rel) is not None


def check(root: Path) -> tuple[list[str], list[str], list[str]]:
    files = closure(root)
    specs = restore_specs((root / WORKFLOW).read_text())
    missing = [f for f in files if not any(covers(s, f) for s in specs)]
    return files, specs, missing


def report(root: Path) -> int:
    try:
        files, specs, missing = check(root)
    except (OSError, ValueError) as e:
        print(f"agreement_restore: {e}")
        return 1
    for f in missing:
        print(f"  UNRESTORED {f}: no {JOB} restore pathspec covers it")
    print(f"agreement_restore: {len(files)} closure file(s), "
          f"{len(files) - len(missing)} covered by the {JOB} restore list, "
          f"{len(missing)} missing")
    return 1 if missing else 0


def self_test() -> int:
    passed = failed = 0

    def ck(name: str, ok: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + ok, failed + (not ok)
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")

    def tree(files: dict[str, str]) -> Path:
        root = Path(tempfile.mkdtemp())
        for rel, body in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body)
        return root

    def workflow(specs: list[str]) -> str:
        listed = "".join(f"            '{s}' \\\n" for s in specs)
        return ("jobs:\n"
                "  wave-script:\n"
                "    steps:\n"
                "      - name: Restore the check source from the base commit\n"
                "        env:\n"
                "          PINNED: x\n"
                "        run: |\n"
                "          set -euo pipefail\n"
                '          git diff --name-only -z "$(git hash-object -t tree '
                '/dev/null)" "$PINNED" -- \\\n'
                f"{listed}"
                '            > "$RUNNER_TEMP/pinned.list"\n'
                "      - name: next\n"
                "        run: true\n"
                "  record:\n"
                "    steps:\n"
                "      - run: true\n")

    # A reader that imports a module directly, one through a `from`, and one
    # through locate(); each of those imports another, so only the closure —
    # not a first-level read — finds tests/deep.py and tools/release/stamp.py.
    files = {
        "tools/policy/agreement_py.py":
            "import delivery_status\n"
            "from helper import thing\n"
            "def load():\n"
            "    locate('tools/x/dyn.py')\n",
        "tests/delivery_status.py": "import helper\n",
        "tests/helper.py": "import deep\n",
        "tests/deep.py": "from sub import nested\n",
        "tests/sub/nested.py": "X = 1\n",
        "tools/x/dyn.py": "import stamp\n",
        "tools/release/stamp.py": "X = 1\n",
        "tools/unused.py": "X = 1\n",
        "tools/dropped.py": "import stamp\n",
    }
    root = tree(files)
    want = ["tests/deep.py", "tests/delivery_status.py", "tests/helper.py",
            "tests/sub/nested.py", "tools/policy/agreement_py.py",
            "tools/release/stamp.py", "tools/x/dyn.py"]
    ck("the closure is transitive and includes a locate() load, not a file "
       "nothing imports", closure(root) == want)
    ck("a wildcard does not cross a slash, and a directory pathspec does",
       covers("tests/*.py", "tests/deep.py")
       and not covers("tests/*.py", "tests/sub/deep.py")
       and covers("tests", "tests/sub/deep.py")
       and covers("tests/deep.py", "tests/deep.py"))
    (root / WORKFLOW).parent.mkdir(parents=True, exist_ok=True)
    (root / WORKFLOW).write_text(workflow(["tests", "tools/policy/agreement_py.py",
                                           "tools/x/dyn.py",
                                           "tools/release/stamp.py"]))
    ck("a list that covers the closure passes (null control)", report(root) == 0)
    (root / WORKFLOW).write_text(workflow([
        "tests/delivery_status.py", "tests/helper.py", "tests/sub/nested.py",
        "tools/policy/agreement_py.py", "tools/x/dyn.py",
        "tools/release/stamp.py"]))
    out = ""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = report(root)
    out = buf.getvalue()
    ck("a list missing one transitive reader exits 1 and names it",
       rc == 1 and "UNRESTORED tests/deep.py" in out)
    (root / WORKFLOW).write_text("jobs:\n  record:\n    steps:\n      - run: true\n")
    ck("a workflow with no wave-script job is refused, not read as covered",
       report(root) == 1)
    (root / WORKFLOW).write_text(workflow(["tests/*.py",
                                           "tools/policy/agreement_py.py",
                                           "tools/x/dyn.py",
                                           "tools/release/stamp.py"]))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = report(root)
    ck("a wildcard pathspec that would cover tests/ does not cover a nested "
       "file", rc == 1 and "UNRESTORED tests/sub/nested.py" in buf.getvalue())
    # The reader the job prefers when the reorganisation has moved it.
    old = ".claude/workflows/agreement_py.py"  # tools/policy/agreement_py.py is the live reader
    moved = tree({"tests/a.py": "X = 1\n"})
    p = moved / old
    p.parent.mkdir(parents=True)
    p.write_text("import a\n")
    ck("the .claude/workflows reader is used when it is present",
       [f for f in closure(moved) if f.endswith("agreement_py.py")]
       == [old])
    print(f"agreement_restore self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if argv == ["--check"]:
        return report(ROOT)
    if argv == ["--print"]:
        for f in closure(ROOT):
            print(f)
        return 0
    print(__doc__.split("\n\n")[0], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
