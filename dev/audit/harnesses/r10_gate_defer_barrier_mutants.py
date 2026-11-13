#!/usr/bin/env python3
"""R10-GATE-DEFER-BARRIER: mutants of the deferral barrier in merge_train.classify.

    python3 -I dev/audit/harnesses/r10_gate_defer_barrier_mutants.py [--tree DIR] [--plants-only]

DIR is a tree root holding tools/audit/seat/ and tools/ci/ (default: this tree); a baseline is measured by
exporting it first (`git archive <sha> tools/audit/seat tools/ci | tar -x -C "$D"`, then `--tree "$D"`).

Two arms. PLANT: one deferral-blind reader per shape the fourth blocked verdict named (import alias,
rebinding, getattr, functools.partial, a function named *self_test*, a module outside the four the
old scan read), each planted into a copy of DIR -- appended to tools/audit/seat/merge_train.py, or as
custom_components/elsewhere.py for the outside module -- and driven on a red `gate`. A plant passes
FINAL where DIR has it, else no busy (DIR's own blind spelling). It is KILLED when the read raises or
DIR's `_gate_reader_barrier_self_test`, loaded from the copy, fails a check; SURVIVED when it returns
a verdict and the block is green. SOURCE (skipped by --plants-only): each row of SOURCE_MUTANTS
replaces one fragment of merge_train.py that must occur exactly once (else STALE, a failure), and the
block runs over the mutated source compiled in memory under the file's path; the unmutated source
is the null control and must fail nothing.
A line per mutant, then `RESULT plants=N survived=S` and `RESULT mutants=N survived=S stale=T
baseline_failed=F`; exit 1 unless every count but N is 0.
"""
import argparse
import shutil
import sys
import tempfile
import types
from pathlib import Path

_F = "_F = (FINAL,) if 'FINAL' in globals() else ()\n"
PLANTS = [
    ("import alias", "merge_train.py",
     "def _planted(latest, required):\n    from merge_train import classify as judge\n    return judge(latest, required, *_F)\n"),
    ("rebinding", "merge_train.py", "_judge = classify\ndef _planted(latest, required):\n    return _judge(latest, required, *_F)\n"),
    ("getattr", "merge_train.py",
     "def _planted(latest, required):\n    return getattr(sys.modules['merge_train'], 'classify')(latest, required, *_F)\n"),
    ("functools.partial", "merge_train.py",
     "def _planted(latest, required):\n    return functools.partial(classify, latest, required)(*_F)\n"),
    ("a function named *self_test*", "merge_train.py",
     "def _planted_self_test(latest, required):\n    return classify(latest, required, *_F)\n_planted = _planted_self_test\n"),
    ("a module outside the four", "../../../custom_components/elsewhere.py",
     "def _planted(latest, required):\n    return classify(latest, required, *_F)\n"),
]

SOURCE_MUTANTS = [
    ("FINAL accepted from any frame", "elif busy is FINAL and caller_frame(1) in FINAL_READERS:", "elif busy is FINAL:"),
    ("any value accepted as busy (None, (), a list)", "    if isinstance(busy, Busy):\n        deferred",
     "    if isinstance(busy, (Busy, list, tuple, type(None))):\n        deferred"),
    ("an empty Busy minted anywhere", "if not self and caller_frame(1) not in BUSY_MINTERS:", "if False:"),
    ("FINAL frame read one level too shallow (classify itself)", "elif busy is FINAL and caller_frame(1) in FINAL_READERS:",
     "elif busy is FINAL and caller_frame(0) in FINAL_READERS:"),
    ("frames keyed by basename, not repo path", "return rel, code.co_qualname",
     "return 'tools/audit/seat/' + Path(rel).name, code.co_qualname"),
    ("frames keyed by path only", "return rel, code.co_qualname", "return rel, 'approval_owed'"),
]


def load(path: Path, source: str, name: str = "merge_train"):
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    sys.path.insert(0, str(path.parent))
    try:
        exec(compile(source, str(path), "exec"), mod.__dict__)
    finally:
        sys.path.remove(str(path.parent))
    return mod


def block(mod) -> list:
    failed = []
    try:
        mod._gate_reader_barrier_self_test(lambda name, ok: None if ok else failed.append(name))
    except Exception as e:  # noqa: BLE001  a crash of the block is a failure of the block
        failed.append(f"raised {type(e).__name__}: {e}")
    return failed


def plant(tree: Path, where: str, src: str) -> str:
    """'KILLED <why>' or 'SURVIVED <verdict>' for one plant in a copy of <tree>."""
    with tempfile.TemporaryDirectory() as d:
        for sub in ("tools/audit/seat", "tools/ci"):
            shutil.copytree(tree / sub, Path(d) / sub)
        seat = Path(d) / "tools/audit/seat"
        target = (seat / where).resolve()
        mt_src = (seat / "merge_train.py").read_text()
        if where == "merge_train.py":
            mt_src += "\n" + _F + src
            (seat / "merge_train.py").write_text(mt_src)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(_F + src)
        mod = load(seat / "merge_train.py", mt_src)
        if where == "merge_train.py":
            reader = mod._planted
        else:
            ns = {k: v for k, v in mod.__dict__.items() if not k.startswith("__")}
            exec(compile(target.read_text(), str(target), "exec"), ns)
            reader = ns["_planted"]
        red = mod.latest_runs([{"name": mod.GATE, "status": "completed", "conclusion": "failure", "started_at": "1"}])
        try:
            got = reader(red, [mod.GATE])
        except TypeError as e:
            return f"KILLED   read refused: {type(e).__name__}: {str(e)[:70]}"
        failed = block(mod)
        return f"KILLED   block: {failed[0][:70]}" if failed else f"SURVIVED read {got[0]}, block green"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", default=str(Path(__file__).resolve().parents[3]))
    ap.add_argument("--plants-only", action="store_true")
    args = ap.parse_args()
    tree = Path(args.tree).resolve()
    survived = 0
    for name, where, src in PLANTS:
        line = plant(tree, where, src)
        survived += line.startswith("SURVIVED")
        print(f"PLANT {name}: {line}")
    print(f"RESULT plants={len(PLANTS)} survived={survived}")
    if args.plants_only:
        return 1 if survived else 0
    path = tree / "tools/audit/seat/merge_train.py"
    src = path.read_text()
    base = block(load(path, src))
    print(f"BASELINE failed={len(base)} {base[:2]}")
    msurv = stale = 0
    for name, old, new in SOURCE_MUTANTS:
        if src.count(old) != 1:
            stale += 1
            print(f"STALE    {name} (fragment occurs {src.count(old)} times)")
            continue
        failed = block(load(path, src.replace(old, new)))
        msurv += not failed
        print(f"{'KILLED  ' if failed else 'SURVIVED'} {name} | {failed[0][:80] if failed else '-'} (+{max(len(failed) - 1, 0)})")
    print(f"RESULT mutants={len(SOURCE_MUTANTS)} survived={msurv} stale={stale} baseline_failed={len(base)}")
    return 1 if survived or msurv or stale or base else 0


if __name__ == "__main__":
    sys.exit(main())
