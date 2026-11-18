#!/usr/bin/env python3
"""R10-HOTFIX-STRESS-MEM-PEAK-2: a traced peak charged the interned-string table.

A solve interns a few fresh strings. When the interpreter's interned-string
table has fewer free slots than that, the solve rebuilds it inside the traced
window and the whole new table is billed to the scenario (1.83 MiB on CI,
3.67 MiB on the cloud seat's image). Where the import fill leaves the table
moves a few slots from process to process, so one tree read typical_slab/
shoulder at 2.1 MiB in one run and 3.9 MiB in the next.

Every mode takes TREE, a checkout (the merge base or the head), and drives
that tree's own tests/stress.py; nothing is re-implemented but the fill.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_stress_intern_fill.py MODE TREE ...

  probes TREE REPS LABEL...   the tree's own --memory-probe, REPS times each:
      RESULT probes label=<l> traced_mib=<a,b,...>
  edge TREE LABEL SHORT       stress imported, the table filled SHORT slots
      short of its rebuild (counted in a forked child sharing the table),
      then the tree's own _memory_probe_main -- so the fill lands before
      whatever the tree does before its traced window:
      RESULT edge label=<l> short=<k> interns_to_rebuild=<n> traced_mib=<x>
  count TREE LABEL            slots one untraced solve consumes (forked
      counts before and after build_case):
      RESULT count label=<l> slots=<n>
  rss TREE LABEL...           the tree's empty probe and probes:
      RESULT rss label=<l> baseline_mib=<b> probe_mib=<p> attrib_mib=<a>
  replay TREE FIXTURE         slots each traced (memory) cycle of
      tests/replay.py --one FIXTURE consumes, forked counts around it:
      RESULT replay fixture=<f> memory_cycles=<n> slots=<sorted set> total=<t>

EXPECTED RESULT (cloud seat, merge base 9b1bb58db7 vs this head):
  edge typical_slab/shoulder 1: base traced_mib ~5.7, head ~2.06 (null
      control: SHORT 50 reads ~2.06 at both ends)
  probes: the same readings at both ends, 2.05-2.07 typical_slab/shoulder
  replay synthetic-dhw-only.json: slots={0} at both ends
Null control: edge with a large SHORT; the bare probe of `probes`.
Perturbation: SHORT 1, which a solve that interns at all crosses.
"""
from __future__ import annotations

import importlib.util
import json
import os
import runpy
import tempfile
import sys
import tracemalloc
import warnings

STEP = 512 * 1024  # a table rebuild; one string is under 1 KiB


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


def until_rebuild(tag, limit=2_000_000):
    tracemalloc.start()
    try:
        prev = tracemalloc.get_traced_memory()[0]
        for n in range(1, limit + 1):
            sys.intern(f"__r10_fill_{tag}_{n}")
            cur = tracemalloc.get_traced_memory()[0]
            if cur - prev > STEP:
                return n, True
            prev = cur
        return limit, False
    finally:
        tracemalloc.stop()


def forked_count():
    r, w = os.pipe()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        pid = os.fork()
    if pid == 0:
        n, ok = until_rebuild("count")
        os.write(w, str(n if ok else -1).encode())
        os._exit(0)
    os.close(w)
    n = int(os.read(r, 32))
    os.waitpid(pid, 0)
    if n < 0:
        raise SystemExit("no interned-table rebuild seen")
    return n


def load_stress(tree):
    os.chdir(tree)
    sys.path[:0] = [os.path.join(tree, p)
                    for p in ("tests/hastub", "custom_components", "tests")]
    sys.argv = ["stress.py"]
    spec = importlib.util.spec_from_file_location("stress", "tests/stress.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["stress"] = mod
    spec.loader.exec_module(mod)
    return mod


def specs(stress):
    return {c["label"]: {k: v for k, v in c.items() if k != "label"}
            for c in stress.sweep_combinations()}


def main(argv):
    mode, tree = argv[0], os.path.abspath(argv[1])
    repo_root(tree)  # refuses a path that is not a checkout
    if mode == "probes":
        stress = load_stress(tree)
        combos, env = specs(stress), stress._memory_probe_env()
        for label in argv[3:]:
            reads = [stress._run_memory_probe(
                ["--memory-probe", json.dumps(combos[label])], env)["traced_mb"]
                for _ in range(int(argv[2]))]
            print(f"RESULT probes label={label} traced_mib="
                  + ",".join(f"{r:.2f}" for r in reads), flush=True)
    elif mode == "edge":
        label, short = argv[2], int(argv[3])
        stress = load_stress(tree)
        spec = json.dumps(specs(stress)[label])
        n = forked_count()
        until_rebuild("edge", limit=n - short)
        sys.stdout.flush()
        saved = os.dup(1)
        with tempfile.TemporaryFile() as captured:
            os.dup2(captured.fileno(), 1)
            try:
                stress._memory_probe_main(["stress.py", "--memory-probe", spec])
                sys.stdout.flush()
            finally:
                os.dup2(saved, 1)
            captured.seek(0)
            line = captured.read().decode().strip().splitlines()[-1]
        print(f"RESULT edge label={label} short={short} interns_to_rebuild={n} "
              f"traced_mib={json.loads(line)['traced_mb']:.2f}")
    elif mode == "count":
        stress = load_stress(tree)
        spec = specs(stress)[argv[2]]
        before = forked_count()
        stress.build_case(**spec)
        print(f"RESULT count label={argv[2]} slots={before - forked_count()}")
    elif mode == "rss":
        stress = load_stress(tree)
        combos, env = specs(stress), stress._memory_probe_env()
        base = float(stress._run_memory_probe(["--memory-baseline"], env)["rss_mb"])
        for label in argv[2:]:
            probe = float(stress._run_memory_probe(
                ["--memory-probe", json.dumps(combos[label])], env)["rss_mb"])
            print(f"RESULT rss label={label} baseline_mib={base:.1f} "
                  f"probe_mib={probe:.1f} attrib_mib={max(0.0, probe - base):.1f}",
                  flush=True)
    elif mode == "replay":
        fixture = argv[2]
        os.chdir(tree)
        sys.path[:0] = [os.path.join(tree, "tests/hastub")]
        real_start, real_get = tracemalloc.start, tracemalloc.get_traced_memory
        before, used = [], []

        def from_replay():
            return sys._getframe(2).f_code.co_filename.endswith("replay.py")

        def start(*a):
            if from_replay():
                before.append(forked_count())
            return real_start(*a)

        def get():
            cur, peak = real_get()
            if from_replay() and len(used) < len(before):
                used.append(before[-1] - forked_count())
            return cur, peak

        tracemalloc.start, tracemalloc.get_traced_memory = start, get
        sys.argv = ["tests/replay.py", "--one", fixture]
        try:
            runpy.run_path("tests/replay.py", run_name="__main__")
        except SystemExit:
            pass
        sys.stdout.flush()
        print(f"RESULT replay fixture={os.path.basename(fixture)} "
              f"memory_cycles={len(used)} slots={sorted(set(used))} "
              f"total={sum(used)}", file=sys.stderr)
    else:
        raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    main(sys.argv[1:])
