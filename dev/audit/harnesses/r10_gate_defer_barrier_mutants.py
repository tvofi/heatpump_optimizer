#!/usr/bin/env python3
"""R10-GATE-DEFER-BARRIER: source mutants of the busy classifier (merge_train.busy_reads and its callers).

    python3 -I dev/audit/harnesses/r10_gate_defer_barrier_mutants.py [--tree DIR] [--corpus-under OTHER]

DIR is a tree root holding tools/audit/seat/ (default: this tree). Each row of MUTANTS replaces one
source fragment of tools/audit/seat/merge_train.py, which must occur exactly once (a fragment that no
longer occurs is a STALE row, counted as a failure, never skipped). The mutated source is compiled in
memory under the file's own path -- nothing is written -- and `_gate_reader_barrier_self_test` is run
against it. A mutant is KILLED when a check fails or the block raises. The unmutated source is run
first as the null control and must fail nothing. The table mutants of BUSY_ARMS (each arm replaced by
each other verdict, each operand field dropped) are not repeated here: the self-test block runs them
itself and this harness's `enumerator` and `corpus` rows show that block reddening.
--corpus-under OTHER runs no mutant: it reads DIR's BUSY_CORPUS (each expression as third positional and
as `busy=`) through OTHER's `blind_classify_readers` and through DIR's, and prints per tree how many
calls are judged against the recorded verdict, split by direction (`RESULT corpus ...`; exit 0).
A line per mutant, then `RESULT mutants=N survived=S stale=T baseline_failed=F`; exit 1 unless S, T and F are 0.
"""
import argparse
import sys
import types
from pathlib import Path

MUTANTS = [
 ("name: a builtin name reads", "return env.get(n.id, BLIND if n.id in _BUILTIN_NAMES else READS)", "return env.get(n.id, READS)"),
 ("name: env ignored", "return env.get(n.id, BLIND if n.id in _BUILTIN_NAMES else READS)", "return BLIND if n.id in _BUILTIN_NAMES else READS"),
 ("boolop: stop inverted", "if _static_truth(v) is stop:", "if _static_truth(v) is (not stop):"),
 ("boolop: no short-circuit", "            if _static_truth(v) is stop:\n                break", "            if _static_truth(v) is stop:\n                pass"),
 ("ifexp: test never folded", "return over([n.body, n.orelse] if t is None else [n.body] if t else [n.orelse])", "return over([n.body, n.orelse])"),
 ("ifexp: branches swapped", "else [n.body] if t else [n.orelse])", "else [n.orelse] if t else [n.body])"),
 ("ifexp: test is an operand", "return over([n.body, n.orelse] if t is None", "return over([n.test, n.body, n.orelse] if t is None"),
 ("comp: target not bound", "                    env[t.id] = got", "                    pass"),
 ("comp: refused iter passed", "        if REFUSED in gens:\n            return REFUSED\n", ""),
 ("comp: empty iter not folded", "        if any(_static_truth(g.iter) is False for g in n.generators):\n            return BLIND  # an iteration over a literal empty container yields nothing\n", ""),
 ("comp: dict key dropped", "over([n.key, n.value] if isinstance(n, ast.DictComp)", "over([n.value] if isinstance(n, ast.DictComp)"),
 ("comp: dict value dropped", "over([n.key, n.value] if isinstance(n, ast.DictComp)", "over([n.key] if isinstance(n, ast.DictComp)"),
 ("comp: filter is an operand", "else [n.elt], env)", "else [n.elt, *[i for g in n.generators for i in g.ifs]], env)"),
 ("over: READS dominates REFUSED", "return REFUSED if REFUSED in got else READS if READS in got else BLIND", "return READS if READS in got else REFUSED if REFUSED in got else BLIND"),
 ("unknown node reads", "arm = arms.get(type(n).__name__, REFUSED)", "arm = arms.get(type(n).__name__, READS)"),
 ("unknown node blind", "arm = arms.get(type(n).__name__, REFUSED)", "arm = arms.get(type(n).__name__, BLIND)"),
 ("subscript index is an operand", '"Subscript": ("value",)', '"Subscript": ("value", "slice")'),
 ("binding: literal * splat not flattened", "if isinstance(a, ast.Starred) and isinstance(a.value, (ast.Tuple, ast.List)):", "if False:"),
 ("binding: literal ** not flattened", "if k is None and isinstance(v, ast.Dict):", "if False:"),
 ("binding: only the busy key", 'if k == "busy" or not isinstance(k, str)]', 'if k == "busy"]'),
 ("binding: any key binds", 'if k == "busy" or not isinstance(k, str)]', 'if True]'),
 ("binding: splat ignored", "return cand + (splat or args[2:3])", "return cand + args[2:3]"),
 ("binding: fourth positional", "return cand + (splat or args[2:3])", "return cand + (splat or args[3:4])"),
 ("blind: REFUSED passes", "return READS not in got or REFUSED in got", "return READS not in got"),
 ("blind: absent busy passes", "return READS not in got or REFUSED in got", "return BLIND in got or REFUSED in got"),
 ("truth: constant unknown", "    if isinstance(n, ast.Constant):\n        return bool(n.value)\n", ""),
 ("truth: empty literal unknown", "        if not elts:\n            return False\n", ""),
 ("truth: non-empty literal unknown", "            return True\n    return None", "            return None\n    return None"),
 ("truth: a starred-only literal is true", "if any(e is not None and not isinstance(e, ast.Starred) for e in elts):", "if elts:"),
 ("enumerator: lists nothing", "                  if c.__name__ not in arms)", "                  if False)"),
 ("self-test functions counted", 'and not any("self_test" in x for x in fn)', ''),
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
    rows = [(want, form.format(e)) for want, e in here.BUSY_CORPUS if not e.startswith("slice:")
            for form in ("{}", "busy={}")]
    for label, mod in (("other", load(other, "mt_other")), ("tree", here)):
        bad = [want for want, arg in rows
               if (mod.blind_classify_readers(f"def f():\n    return classify(l, r, {arg})\n") == {}) != (want == here.READS)]
        print(f"RESULT corpus {label} calls={len(rows)} wrong={len(bad)} "
              f"not_reading_passed={sum(w != here.READS for w in bad)} reading_counted_blind={sum(w == here.READS for w in bad)}")
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
