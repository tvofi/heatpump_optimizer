"""R10-FLY-NIGHTLY-HB: the heartbeat container run N times, with the sampler probed.

The measurement behind the heartbeat sampler change, as a script over the tree's
own ``nightly_ha._stage(two_zone_dhw=True)`` and ``docker_command(...,
["--heartbeat-only"], ("SYS_PTRACE",))``. Every mode edits only the staged copy.

``--mode probe`` (a tree whose sampler is py-spy, the base): the staged py-spy
is wrapped. A call still running after 4.5 s is a hang; the wrapper then records
py-spy's own state (/proc stat: R or S, utime, stime), runs CPython's
``_remote_debugging`` unwinder against the same process twice, and a blocking
(ptrace-stopping) py-spy with a 20 s cut. Every first call is followed, while
the spin is still held, by one unwinder sample.

``--mode side`` (a tree whose sampler is the unwinder, the fix): every sample
also starts the staged py-spy beside it with a 4.5 s cut, so a run on a process
py-spy cannot read is identified, with the control's verdict on that process.

``--mode N1|N2|N3`` (a fix tree): null controls. N1 the spin stalls nothing,
N2 the watcher never dumps, N3 the sampler reads a pid that does not exist;
each must fail hb:positive_control.

Needs Docker, the image pulled, py-spy 0.4.2 on PATH, and an image layer holding
the ``threadpoolctl`` wheel (see r10_nightly_pyspy_retry.py).

    python3 dev/audit/harnesses/r10_fly_nightly_hb.py --tree <worktree> \\
        --mode side --runs 200 --out <dir> --image <image+threadpoolctl>

Prints one line per run, then ``SUMMARY mode=<m> runs=<n> ok=<k> fail=<f>
spy_hung=<h>`` (h: runs where a py-spy call ran past 4.5 s). Evidence of every
failed or py-spy-hung run is kept under ``--out``.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROBE = """import time, _remote_debugging as rd
t = time.monotonic()
try:
    st = rd.RemoteUnwinder(1, all_threads=True).get_stack_trace()
    print(f"stdlib ok {time.monotonic() - t:.3f}s threads={len(st)} names={'_hb_spin' in repr(st)}")
except Exception as e:
    print(f"stdlib err {time.monotonic() - t:.3f}s {type(e).__name__}: {e}")
"""
WRAP = r"""#!/bin/sh
c=/tmp/hpo-spy-calls; echo >> "$c"; k=$(wc -l < "$c" | tr -d ' ')
d=$(dirname "$0"); L=/config/spy-$k.log
"$d/py-spy.real" "$@" &
p=$!
( sleep 4.5; if kill -0 $p 2>/dev/null; then
    echo "hung call $k: $(cut -d' ' -f3,14,15 /proc/$p/stat) (state utime stime)" >> "$L"
    for j in 1 2; do timeout 10 python3 "$d/probe.py" >> "$L" 2>&1; done
    if [ "$k" = 1 ]; then timeout 20 "$d/py-spy.real" dump --pid 1 > /dev/null 2>&1
      echo "blocking py-spy rc=$?" >> "$L"; fi
  fi ) >/dev/null 2>&1 &
wait $p; rc=$?
[ "$k" = 1 ] && timeout 10 python3 "$d/probe.py" >> /config/first.log 2>&1
exit $rc
"""
SIDE = r"""#!/bin/sh
c=/tmp/hpo-side-calls; echo >> "$c"; k=$(wc -l < "$c" | tr -d ' ')
for a; do pid=$a; done
( timeout 4.5 /opt/hpo/py-spy dump --nonblocking --pid "$pid" > /config/side-$k.out 2>&1
  echo "side py-spy call $k rc=$? names=$(grep -c _hb_spin /config/side-$k.out)" >> /config/spy-$k.log ) >/dev/null 2>&1 &
exec "$@"
"""
EDITS = {
    "side": ('return [sys.executable, "-c", _STDLIB_SAMPLE]',
             'return ["/opt/hpo/side.sh", sys.executable, "-c", _STDLIB_SAMPLE]'),
    "N1": ("    end, bound = start + seconds, start + hold_max\n", "    end, bound = start, start\n"),
    "N2": ("            if stalled >= self.dump_after and not self._stall_dumped:", "            if False:"),
    "N3": ("[*self.sampler, str(os.getpid())]", "[*self.sampler, '999999']"),
}


def _load(tree: Path):
    sys.path[:0] = [str(tree / "tests"), str(tree / "tests" / "hastub"), str(tree)]
    spec = importlib.util.spec_from_file_location("nightly_ha", tree / "tests" / "nightly_ha.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["nightly_ha"] = mod
    spec.loader.exec_module(mod)
    return mod


def run_once(n, run_dir: Path, mode: str, image: str) -> tuple[str, str, bool, str]:
    config, driver = n._stage(run_dir, two_zone_dhw=True)
    spy = driver / "py-spy"
    if not spy.exists():
        raise SystemExit("no py-spy staged: put py-spy 0.4.2 on PATH")
    (driver / "probe.py").write_text(PROBE)
    if mode == "probe":
        shutil.move(spy, driver / "py-spy.real")
        spy.write_text(WRAP)
        spy.chmod(0o755)
    else:
        staged = driver / "nightly_ha.py"
        src, (old, new) = staged.read_text(), EDITS[mode]
        if src.count(old) != 1:
            raise SystemExit(f"--mode {mode}: the tree has no single {old.strip()!r}")
        staged.write_text(src.replace(old, new))
        if mode == "side":
            (driver / "side.sh").write_text(SIDE)
            (driver / "side.sh").chmod(0o755)
    cmd = n.docker_command(image, config, driver, 240.0, ["--heartbeat-only"], ("SYS_PTRACE",))
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    (run_dir / "out.txt").write_text(out.stdout + out.stderr)
    verdict = re.search(r"(ok|FAIL)\s+hb:positive_control\s+\[([^\]]*)\]", out.stdout + out.stderr)
    logs = " | ".join(p.read_text().strip().replace("\n", "; ")
                      for p in sorted(config.glob("spy-*.log")) + sorted(config.glob("first.log")))
    hung = "hung call" in logs or "rc=124" in logs or "rc=143" in logs
    return (verdict.group(1) if verdict else "NONE"), (verdict.group(2) if verdict else ""), hung, logs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--mode", choices=("probe", "side", "N1", "N2", "N3"), required=True)
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--image", default="homeassistant/home-assistant:stable")
    args = ap.parse_args()
    n = _load(args.tree.resolve())
    ok = fail = hung_runs = 0
    for i in range(1, args.runs + 1):
        run_dir = args.out / f"run{i}"
        shutil.rmtree(run_dir, ignore_errors=True)
        run_dir.mkdir(parents=True)
        verdict, detail, hung, logs = run_once(n, run_dir, args.mode, args.image)
        ok, fail, hung_runs = ok + (verdict == "ok"), fail + (verdict != "ok"), hung_runs + hung
        print(f"run {i}: {verdict} {detail} || {logs}", flush=True)
        if verdict == "ok" and not hung:
            shutil.rmtree(run_dir, ignore_errors=True)
    print(f"SUMMARY mode={args.mode} runs={args.runs} ok={ok} fail={fail} spy_hung={hung_runs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
