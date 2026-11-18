"""R9-UX-5: the per-channel idle classifier against the per-step one it replaced.

Two measurements, each tree exported with ``git archive`` so nothing is
imported from the checkout this runs in:

1. Equivalence. Random channels (lengths that disagree, NaN, values on the
   0.05 threshold and the 1e-6 surplus cut, absent arrays) are classified by
   the per-step ``idle_reason`` at OLD and by ``idle_codes`` at NEW, step by
   step, and through ``classify_space_steps`` and ``classify_dhw_steps``. A
   code that differs in value or type is a mismatch.
2. Cost. ``tests/stress.py``'s own ``production_calls`` meter, read from the
   NEW tree's source, counts optimizer.py calls for one 96-step
   ``classify_space_steps`` call at BASE, OLD and NEW.

    python3 dev/audit/harnesses/ux5_idle_codes.py OLD NEW BASE [seed] [rounds]

OLD is a commit with ``idle_reason`` (97f89cdaf5fb7fbcc046b40d0d26f16164f3e88e),
NEW one with ``idle_codes``, BASE a commit before either (the merge base).
Null control: a NEW whose solar test reads ``>= 1e-6`` for ``> 1e-6`` printed
mismatches=509 at seed 1, 20000 rounds.
"""
from __future__ import annotations

import ast
import hashlib
import random
import subprocess
import sys
import tempfile
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


REPO = repo_root(__file__)


def export(ref: str, dest: Path) -> Path:
    """``ref``'s package, stub and stress meter, unpacked under ``dest``."""
    dest.mkdir(parents=True)
    archive = subprocess.run(
        ["git", "-C", str(REPO), "archive", ref, "custom_components", "tests/hastub",
         "tests/stress.py"],
        check=True, capture_output=True).stdout
    subprocess.run(["tar", "-x", "-C", str(dest)], input=archive, check=True)
    return dest


def load(root: Path):
    """``root``'s optimizer module, imported fresh."""
    for name in [n for n in sys.modules if n.startswith("heatpump_optimizer")]:
        del sys.modules[name]
    sys.path[:0] = [str(root / "tests" / "hastub"), str(root / "custom_components")]
    try:
        import heatpump_optimizer.optimizer as module
    finally:
        del sys.path[:2]
    return module


def equivalence(old, new, seed: int, rounds: int) -> tuple[int, int]:
    import numpy as np
    rng = random.Random(seed)

    def arr(n, temps=False):
        if rng.random() < 0.15:
            return None
        vals = []
        for _ in range(max(0, n + rng.choice([-2, -1, 0, 0, 0, 1, 3]))):
            r = rng.random()
            if r < 0.03:
                vals.append(float("nan"))
            elif r < 0.35:
                vals.append(0.0)
            elif r < 0.45:
                vals.append(0.05)
            elif r < 0.5:
                vals.append(1e-6)
            else:
                vals.append(round(rng.uniform(0, 30 if temps else 3), rng.choice([0, 1, 2])))
        return np.array(vals, dtype=float)

    cases = mismatches = 0
    for _ in range(rounds):
        n = rng.randint(0, 14)
        power = arr(n)
        power = np.zeros(n) if power is None else power
        if len(power) < n:
            power = np.concatenate([power, np.zeros(n - len(power))])
        prices, level, floor = arr(n), arr(n + 1, True), arr(n, True)
        surplus, other, caps = arr(n), arr(n), arr(n)
        thr = rng.choice([0.05, 0.05, 0.0, 1.0])
        for i in range(len(power) + 2):
            a = old.idle_reason(i, power, prices, level, floor, surplus, other, caps, thr)
            b = new.idle_codes(max(i + 1, len(power)), power, prices, level, floor,
                               surplus, other, caps, thr)[i]
            cases += 1
            mismatches += a != b or type(a) is not type(b)
        if (prices is not None and len(prices) >= n and level is not None and len(level)
                and floor is not None and len(floor) >= n):
            a = old.classify_space_steps(power, prices, level, floor, np.ones(n), surplus, n,
                                         thr, other=other, caps=caps)
            b = new.classify_space_steps(power, prices, level, floor, np.ones(n), surplus, n,
                                         thr, other=other, caps=caps)
            cases += 1
            mismatches += a != b or [type(x) for x in a] != [type(x) for x in b]
        ctx = dict(prices=prices, level=level, floor=floor, surplus=surplus, other=other, caps=caps)
        a = old.classify_dhw_steps(power, np.zeros(n, bool), np.zeros(n), None, n, thr,
                                   old.IdleContext(**ctx))
        b = new.classify_dhw_steps(power, np.zeros(n, bool), np.zeros(n), None, n, thr,
                                   new.IdleContext(**ctx))
        cases += 1
        mismatches += a != b
    return cases, mismatches


def calls(meter, root: Path) -> tuple[int, str]:
    import numpy as np
    module = load(root)
    n = 96
    rng = np.random.default_rng(0)
    power = np.where(rng.random(n) < 0.3, rng.uniform(0.5, 3, n), 0.0)
    prices = rng.uniform(0.1, 2.0, n)
    level = rng.uniform(19, 23, n + 1)
    floor = np.full(n, 19.0)
    surplus = np.where((np.arange(n) % 24 > 9) & (np.arange(n) % 24 < 16), 1.5, 0.0)
    codes, counts = meter(
        lambda: module.classify_space_steps(power, prices, level, floor, np.ones(n), surplus, n),
        str(root / "custom_components" / "heatpump_optimizer"))
    return counts.get("optimizer.py", 0), hashlib.sha1(repr(codes).encode()).hexdigest()[:12]


def main() -> None:
    old_ref, new_ref, base_ref = sys.argv[1:4]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    rounds = int(sys.argv[5]) if len(sys.argv) > 5 else 20000
    with tempfile.TemporaryDirectory() as tmp:
        trees = {k: export(r, Path(tmp) / k)
                 for k, r in (("base", base_ref), ("old", old_ref), ("new", new_ref))}
        cases, mismatches = equivalence(load(trees["old"]), load(trees["new"]), seed, rounds)
        print(f"RESULT cases={cases}")
        print(f"RESULT mismatches={mismatches}")
        src = (trees["new"] / "tests" / "stress.py").read_text()
        fn = next(node for node in ast.parse(src).body
                  if isinstance(node, ast.FunctionDef) and node.name == "production_calls")
        scope: dict = {}
        exec(compile(ast.Module([fn], []), "production_calls", "exec"), scope)
        for key in ("base", "old", "new"):
            count, digest = calls(scope["production_calls"], trees[key])
            print(f"RESULT {key}_calls={count} codes={digest}")


if __name__ == "__main__":
    main()
