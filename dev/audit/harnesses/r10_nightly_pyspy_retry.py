"""R10-NIGHTLY-PYSPY-RETRY: the lane's heartbeat container, run N times against a tree.

The reproduction of dev/audit/rca/nightly-ha-pyspy-timeout.md (#2479), section
"Reproduce", as a script: the tree's own ``nightly_ha._stage(two_zone_dhw=True)``
and ``docker_command(..., ["--heartbeat-only"], ("SYS_PTRACE",))``, so the same
command measures a base tree and a fix tree. ``--sampler hang-once`` replaces
the staged py-spy with a wrapper whose first call hangs and whose later calls
run the real binary: the RCA's owed demonstration (red at the base, green at
the fix). ``--sampler real`` stages py-spy untouched.

Needs Docker, the image pulled, and py-spy on PATH (tests/requirements-nightly-ha.txt).
A container without network cannot pip-install ``threadpoolctl``; as the RCA
did, pass ``--image`` naming the image plus a layer holding that one wheel.

    python3 dev/audit/harnesses/r10_nightly_pyspy_retry.py --tree <worktree> \
        --sampler hang-once --runs 3

Prints one line per run, then ``SUMMARY sampler=<s> runs=<n> ok=<k> fail=<m>``.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# The first call hangs past any per-attempt timeout; the counter lives in the
# container's /tmp because the driver mount is read-only.
HANG_ONCE = """#!/bin/sh
c=/tmp/hpo-pyspy-calls
echo >> "$c"
[ "$(wc -l < "$c")" = 1 ] && exec sleep 600
exec "$(dirname "$0")/py-spy.real" "$@"
"""
RUN_TIMEOUT_S = 600.0


def _load(tree: Path):
    sys.path[:0] = [str(tree / "tests"), str(tree / "tests" / "hastub"), str(tree)]
    spec = importlib.util.spec_from_file_location("nightly_ha", tree / "tests" / "nightly_ha.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["nightly_ha"] = mod
    spec.loader.exec_module(mod)
    return mod


def run_once(n, image: str, sampler: str) -> tuple[bool | None, str]:
    with tempfile.TemporaryDirectory() as tmp:
        config, driver = n._stage(Path(tmp), two_zone_dhw=True)
        spy = driver / "py-spy"
        if not spy.exists():
            raise SystemExit("no py-spy staged: put py-spy 0.4.2 on PATH")
        if sampler == "hang-once":
            shutil.move(spy, driver / "py-spy.real")
            spy.write_text(HANG_ONCE)
            spy.chmod(0o755)
        cmd = n.docker_command(image, config, driver, 240.0, ["--heartbeat-only"], ("SYS_PTRACE",))
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=RUN_TIMEOUT_S)
    text = out.stdout + out.stderr
    verdict = re.search(r"(ok|FAIL)\s+hb:positive_control\s+\[([^\]]*)\]", text)
    # The control's echoed dump lines: "  ..   hb:positive_control| py-spy ...".
    spied = [ln.split("| ", 1)[1] for ln in text.splitlines()
             if re.search(r"hb:positive_control\| py-spy (attempt \d+/\d+ )?(rc=|did not run)", ln)]
    if verdict is None:
        return None, f"rc={out.returncode} no hb:positive_control line; tail: {text[-300:]!r}"
    return verdict.group(1) == "ok", f"{verdict.group(2)} | " + " / ".join(s[-140:] for s in spied)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--sampler", choices=("real", "hang-once"), required=True)
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--image", default="homeassistant/home-assistant:stable")
    args = ap.parse_args()
    n = _load(args.tree.resolve())
    ok = fail = 0
    for i in range(1, args.runs + 1):
        passed, detail = run_once(n, args.image, args.sampler)
        ok += passed is True
        fail += passed is not True
        print(f"run {i}: {'ok' if passed else 'FAIL' if passed is False else 'NO-VERDICT'} {detail}",
              flush=True)
    print(f"SUMMARY sampler={args.sampler} runs={args.runs} ok={ok} fail={fail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
