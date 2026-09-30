"""R9-F2.4: winter/cycle's attributable RSS, base against head, interleaved.

The stress lane's memory arm judges ONE draw of `--memory-probe` minus ONE draw
of `--memory-baseline` against a recorded maximum, and its own docstring says
that statistic's clean spread reaches 2.1x. This runs the lane's own two
entry points (the same file, interpreter and environment a gate run uses, via
stress.py's `_memory_probe_env` rule) N times per tree, alternating trees so a
drift in the box lands on both, and prints every draw and the per-tree
min / median / max. It judges nothing; it prints the distribution a single
gate draw is one sample of.

    python tools/audit/handoff/r9-f2-solver-4/rss_ab.py BASE_TREE HEAD_TREE [N]
"""
import json
import os
import statistics
import subprocess
import sys

SPEC = {"season": "winter", "two_zone": True, "dhw": True, "tariff": False,
        "pv": False, "cycling": 1.0}


def probe(tree: str, args: list[str]) -> dict:
    env = dict(os.environ)
    for part in (os.path.join(tree, "tests", "hastub"),
                 os.path.join(tree, "custom_components")):
        env["PYTHONPATH"] = part + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run([sys.executable, os.path.join(tree, "tests", "stress.py")] + args,
                          capture_output=True, text=True, env=env, cwd=tree)
    return json.loads(proc.stdout.strip().splitlines()[-1])


def main() -> int:
    base, head = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    draws: dict[str, list[tuple[float, float, float]]] = {"base": [], "head": []}
    for i in range(n):
        for name, tree in (("base", base), ("head", head)) if i % 2 == 0 else (("head", head), ("base", base)):
            b = probe(tree, ["--memory-baseline"])["rss_mb"]
            p = probe(tree, ["--memory-probe", json.dumps(SPEC)])
            attrib = max(0.0, p["rss_mb"] - b)
            draws[name].append((attrib, p["rss_mb"], p["traced_mb"]))
            print(f"draw {i + 1} {name}: baseline {b:.1f} probe {p['rss_mb']:.1f} "
                  f"attributable {attrib:.1f} MiB traced {p['traced_mb']:.2f} MiB", flush=True)
    for name, rows in draws.items():
        a = [r[0] for r in rows]
        t = [r[2] for r in rows]
        print(f"RESULT {name}_attrib_min={min(a):.1f} median={statistics.median(a):.1f} "
              f"max={max(a):.1f} traced_max={max(t):.2f} n={len(a)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
