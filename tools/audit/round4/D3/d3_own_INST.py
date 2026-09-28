#!/usr/bin/env python3
"""Verifiers' own harness for D3-INST (verifier seat 1 of panel D3-0, round 4).

FINDING (instrument): tests/closures.json's `recorded[*].seconds` are the
seconds of the CHEAP stub invocation tests/derive_closures.sh records with
(golden.py --only __no_such_scenario__, env_drift.py --cache-key <ref> --all),
not the seconds a real run costs — the finder measured a plain golden.py at
201.2 s against the recorded 0.4 s — and nothing in the tree reads those
seconds for a decision, so the table is accounting, not behaviour. Also:
standalone golden.py and env_drift.py --all are the same measurement, because
golden.py's resolve_mode defaults to drift and then execs
env_drift.py --all origin/main.

METRIC: (1) the committed recorded seconds for golden.py / env_drift.py and
one CHEAP sanity script (tests/config_flow_steps.py) next to that script's
own wall time measured here (provisional — other verifiers share the box);
(2) a repo grep counting scripts that READ recorded seconds for a decision;
(3) structural facts read out of golden.py / run.sh (no heavy runs): the
DEFAULT_REF golden.py would drift against, whether run_drift shells out to
tests/env_drift.py, and run.sh's drift-mode skip of golden.py.
The 150-200 s re-measurements are NOT taken here — marked for the judge on a
quiet box (finder numbers cited: golden.py 201.2 s, env_drift.py --all warm
152.0 s / cold 193.2 s, load1 4.2-6.8).

RUN (from this worktree's root; times one ~1 s script in the scratch tree):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D3/d3_own_INST.py

EXPECTED: recorded golden=0.4 s vs finder-measured 201.2 s; the sanity
script's own measured seconds within ~3x of its recorded value; readers=0;
golden_drift_execs_env_drift=1; run.sh skips golden.py when GOLDEN_MODE=drift.
BASELINE: measured against worktree HEAD 0855277 (finder used 7dd68dd)
MACHINE: 8-core Apple M1, macOS 25.6.0, python 3.11
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, "tools/audit/round4/D3")
from d3_own_common import (SCRATCH, heavy_neighbours, load1, run_driver,
                           swapins, thread_factor)

CHEAP = "tests/config_flow_steps.py"


def readers_of_recorded_seconds(root: Path) -> list:
    """Files that LOAD tests/closures.json and then touch a seconds value.

    closure.py is the writer (it serialises "seconds": ... into the file);
    entities.py's `recorded` mentions are schema-shape fixtures with empty
    literals, not loads of this file. A decision reader would have to do
    both, so that is what is counted.
    """
    hits = []
    for p in list(root.glob("tests/*.py")) + list(root.glob("tests/*.sh")) \
            + list(root.glob("tools/**/*.py")) \
            + list(root.glob("tools/**/*.sh")):
        if "tools/audit/round" in str(p):
            continue
        try:
            src = p.read_text()
        except Exception:
            continue
        loads = "closures.json" in src
        touches_seconds = re.search(r'["\']seconds["\']', src) is not None
        if loads and touches_seconds:
            hits.append(str(p))
    return sorted(set(hits))


def main() -> int:
    own_root = Path(".").resolve()
    cl = json.loads((SCRATCH / "tests/closures.json").read_text())
    rec = cl["recorded"]

    # (1) recorded vs measured for one CHEAP script (provisional, quoted)
    started = time.monotonic()
    out = run_driver(CHEAP)
    wall = round(time.monotonic() - started, 1)

    # (2) who reads recorded seconds
    readers = readers_of_recorded_seconds(SCRATCH)

    # (3) structural facts, no heavy runs
    golden = (SCRATCH / "tests/golden.py").read_text()
    run_sh = (SCRATCH / "tests/run.sh").read_text()
    derive = (SCRATCH / "tests/derive_closures.sh").read_text()
    facts = {
        "golden_default_mode_drift": 'DEFAULT_MODE = "drift"' in golden,
        "golden_default_ref": re.search(r'DEFAULT_REF = "([^"]+)"', golden).group(1),
        "golden_run_drift_execs_env_drift": (
            'DRIFT_SCRIPT = "tests/env_drift.py"' in golden
            and "subprocess.run(cmd, cwd=repo)" in golden
            and '"--all", ref' in golden
        ),
        "golden_docstring_says_unset_means_drift": "Unset means `drift`" in golden,
        "run_sh_skips_golden_in_drift": bool(re.search(
            r'if \[ "\$GOLDEN_MODE" = "drift" \]; then(.|\n)*?skip tests/golden\.py',
            run_sh)),
        "derive_cheap_args_golden": "--only __no_such_scenario__" in derive,
        "derive_cheap_args_env_drift": "--cache-key" in derive,
        "env_drift_cache_key_exits_early": "print(cache_key(" in
            (SCRATCH / "tests/env_drift.py").read_text(),
        "readme_lists_golden_and_env_drift_separately": all(
            s in (SCRATCH / "tests/README.md").read_text()
            for s in ("python tests/golden.py", "python tests/env_drift.py")),
    }

    print(f"heavy neighbours (stress.py/run.sh procs): {heavy_neighbours()}")
    print(f"RESULT INST_recorded_golden_s={rec['tests/golden.py']['seconds']} s")
    print(f"RESULT INST_recorded_env_drift_s={rec['tests/env_drift.py']['seconds']} s")
    print(f"RESULT INST_finder_measured_golden_s=201.2 s (cited, judge to re-take)")
    print(f"RESULT INST_finder_measured_env_drift_s=152.0 s (cited, judge to re-take)")
    print(f"RESULT INST_sanity_script={CHEAP}")
    print(f"RESULT INST_sanity_recorded_s={rec[CHEAP]['seconds']} s")
    print(f"RESULT INST_sanity_measured_s={wall} s (provisional, load-quoted)")
    print(f"RESULT INST_sanity_rc={out['rc']} exit_status")
    print(f"RESULT INST_recorded_seconds_decision_readers={len(readers)} count {readers}")
    for k, v in facts.items():
        print(f"RESULT INST_{k}={v}")
    print(f"RESULT thread_factor={thread_factor()}")
    print(f"RESULT load1={load1():.2f}")
    print(f"RESULT swapins={swapins()}")
    del own_root
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
