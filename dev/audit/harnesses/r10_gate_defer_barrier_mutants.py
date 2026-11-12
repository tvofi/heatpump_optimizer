#!/usr/bin/env python3
"""R10-GATE-DEFER-BARRIER: source mutants of the busy barrier (merge_train.busy_reads, _busy_candidates, blind_classify_readers).

    python3 -I dev/audit/harnesses/r10_gate_defer_barrier_mutants.py [--tree DIR] [--corpus-under OTHER]

DIR is a tree root holding tools/audit/seat/ (default: this tree). Each row of MUTANTS replaces one
source fragment of tools/audit/seat/merge_train.py, which must occur exactly once (a fragment that no
longer occurs is a STALE row, counted as a failure, never skipped). The mutated source is compiled in
memory under the file's own path -- nothing is written -- and `_gate_reader_barrier_self_test` is run
against it. A mutant is KILLED when a check fails or the block raises. The unmutated source is run
first as the null control and must fail nothing.
--corpus-under OTHER runs no mutant: it reads DIR's BUSY_CORPUS (each expression as third positional,
as `busy=`, and as `busy=` beside a reading `**kw`) through OTHER's `blind_classify_readers` and through
DIR's, and prints per tree how many calls are judged against the recorded verdict, split by direction
(`RESULT corpus ...`; exit 0).
A line per mutant, then `RESULT mutants=N survived=S stale=T baseline_failed=F`; exit 1 unless S, T and F are 0.
"""
import argparse
import sys
import types
from pathlib import Path

MUTANTS = [
    ("grammar: a Call is not unwrapped to its func", "    if isinstance(n, ast.Call):\n        n = n.func\n", ""),
    ("grammar: an Attribute chain is not walked to its root", "    while isinstance(n, ast.Attribute):\n        n = n.value\n", ""),
    ("grammar: a builtin Name reads", "return isinstance(n, ast.Name) and n.id not in _BUILTIN_NAMES", "return isinstance(n, ast.Name)"),
    ("grammar: open (anything but a literal or builtin reads -- the fold shape)",
     "return isinstance(n, ast.Name) and n.id not in _BUILTIN_NAMES",
     "return not isinstance(n, ast.Constant) and not (isinstance(n, ast.Name) and n.id in _BUILTIN_NAMES)"),
    ("grammar: a Subscript base walks like an Attribute", "while isinstance(n, ast.Attribute):", "while isinstance(n, (ast.Attribute, ast.Subscript)):"),
    ("binding: one reading candidate passes the call (the a6076a0f regression)",
     "not all(busy_reads(b) for b in got)", "not any(busy_reads(b) for b in got)"),
    ("binding: a call with no candidate passes", "return not got or not all(", "return not all("),
    ("binding: a * splat before the third positional is not a candidate", "if i >= 2 or isinstance(a, ast.Starred)]", "if i >= 2]"),
    ("binding: only the third positional is a candidate", "if i >= 2 or isinstance(a, ast.Starred)]", "if i == 2]"),
    ("binding: a ** splat is not a candidate", 'k.arg in ("busy", None)]', 'k.arg == "busy"]'),
    ("binding: a busy= keyword is not a candidate", 'k.arg in ("busy", None)]', 'k.arg is None]'),
    ("binding: a * splat is read as its Starred node", "a.value if isinstance(a, ast.Starred) else a\n", "a\n"),
    ("scope: self-test functions are counted", ' and not any("self_test" in x for x in fn)', ""),
]

def run(path: Path, source: str) -> list:
    """The names of the barrier block's failing checks over <source>, or the exception it raised."""
    mod = types.ModuleType("mt_mutant")
    mod.__file__ = str(path)
    sys.modules["mt_mutant"] = mod
    failed = []
    try:
        exec(compile(source, str(path), "exec"), mod.__dict__)
        mod._gate_reader_barrier_self_test(lambda name, ok: None if ok else failed.append(name))
    except Exception as e:  # noqa: BLE001  a mutant that crashes the block is a killed mutant
        failed.append(f"raised {type(e).__name__}: {e}")
    return failed


def load(seat: Path, name: str):
    mod = types.ModuleType(name)
    mod.__file__ = str(seat / "merge_train.py")
    sys.modules[name] = mod
    sys.path.insert(0, str(seat))
    try:
        exec(compile((seat / "merge_train.py").read_text(), mod.__file__, "exec"), mod.__dict__)
    finally:
        sys.path.remove(str(seat))
    return mod


def corpus_under(seat: Path, other: Path) -> int:
    here = load(seat, "mt_here")
    rows = [(want, form.format(e)) for want, e in here.BUSY_CORPUS for form in ("{}", "busy={}", "busy={}, **kw")]
    for label, mod in (("other", load(other, "mt_other")), ("tree", here)):
        bad = [want for want, arg in rows
               if (mod.blind_classify_readers(f"def f():\n    return classify(l, r, {arg})\n") == {}) is not want]
        print(f"RESULT corpus {label} calls={len(rows)} wrong={len(bad)} "
              f"not_reading_passed={sum(not w for w in bad)} reading_counted_blind={sum(bool(w) for w in bad)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", default=str(Path(__file__).resolve().parents[3]))
    ap.add_argument("--corpus-under")
    args = ap.parse_args()
    seat = Path(args.tree) / "tools/audit/seat"
    if args.corpus_under:
        return corpus_under(seat, Path(args.corpus_under) / "tools/audit/seat")
    sys.path.insert(0, str(seat))
    path = seat / "merge_train.py"
    src = path.read_text()
    base = run(path, src)
    print(f"BASELINE failed={len(base)} {base[:2]}")
    survived = stale = 0
    for name, old, new in MUTANTS:
        if src.count(old) != 1:
            stale += 1
            print(f"STALE    {name} (fragment occurs {src.count(old)} times)")
            continue
        failed = run(path, src.replace(old, new))
        survived += not failed
        print(f"{'KILLED  ' if failed else 'SURVIVED'} {name} | {failed[0][:80] if failed else '-'} (+{max(len(failed) - 1, 0)})")
    print(f"RESULT mutants={len(MUTANTS)} survived={survived} stale={stale} baseline_failed={len(base)}")
    return 1 if survived or stale or base else 0


if __name__ == "__main__":
    sys.exit(main())
