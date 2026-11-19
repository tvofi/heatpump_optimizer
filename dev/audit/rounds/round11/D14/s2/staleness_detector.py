"""N-staleness detector (D14-s2, round 11): every age-limited input read through a quiet night.

Metric: number of age-limited input keys (const.INPUT_MAX_AGE_MINUTES, the
universe of every key InputReader applies an age limit to) whose reading
``inputs.InputReader.read_state`` delivers with ``problem == "stale"`` when the
entity is a report-on-change source (``last_reported == last_updated``) whose
value has legitimately held for a quiet spell of Q minutes. Key: the
``problem`` field the production reader delivers, never the table value.

Arms:
  quiet     on-change source, last change Q min ago        -> a seam per stale key
  polled    the null control: same value re-reported 1 min ago (a polling
            source): age is measured from last_reported, so 0 stale keys
  Q values  255 (the D1-s5-51 field gap: 4 h 15 min between two reports of a
            healthy room probe) and 480 (one calm night)

Run (from the export root):
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s2/staleness_detector.py
  ... --at 3e9f1878bd^      re-find R9 D1-s5-51 (indoor at 60 min) at its pre-fix tree
  ... --at 9c988fc580^      re-find R10 D14-s3-02 (power meter idle) at its pre-fix tree
  ... --reintroduce power   one-line re-introduction: INPUT_ON_CHANGE_MAX_AGE_MINUTES
                            [CONF_POWER_ENTITY] = 30 in memory -> q255 count rises by 1
  ``--at`` needs this checkout's git (git archive into a private temp root).

Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (box B7, linux):
  RESULT quiet_stale_q255=13 keys (exact), quiet_stale_q480=19 keys (exact),
  polled_stale_q255=0, polled_stale_q480=0. At 3e9f1878bd^: indoor_temp_entity
  among the q255 seams (RESULT refind_D1_s5_51=1; all 25 keys stale at q255). At 9c988fc580^:
  heat_pump_power_entity among the q480 seams (RESULT refind_D14_s3_02=1; q255=20, q480=25). --reintroduce power: q255 13 -> 14.
  Counts are exact (no timing); thread_factor/load1 printed per the contract.
"""
import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import argparse
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone

QUIETS = (255, 480)


def _child(tree: str, reintroduce: str | None) -> None:
    tree = os.path.abspath(tree)
    sys.path.insert(0, os.path.join(tree, "tests", "hastub"))
    sys.path.insert(0, os.path.join(tree, "tests"))
    sys.path.insert(0, os.path.join(tree, "custom_components"))
    os.chdir(tree)  # an older harness.py inserts cwd-relative paths
    import harness
    from heatpump_optimizer import const
    from heatpump_optimizer.inputs import InputReader

    print(f"# measured package: {os.path.dirname(const.__file__)}")

    on_change = getattr(const, "INPUT_ON_CHANGE_MAX_AGE_MINUTES", None)
    if reintroduce == "power":
        if on_change is None:
            const.INPUT_MAX_AGE_MINUTES[const.CONF_POWER_ENTITY] = 30.0
        else:
            on_change[const.CONF_POWER_ENTITY] = 30.0
    elif reintroduce == "pump-flags-inf":
        # The opposite direction: what the seams below would read with every
        # pump flag declared unbounded on change (the proposed barrier's arm).
        for k in (
            const.CONF_HEAT_PUMP_DEFROST_ENTITY,
            const.CONF_HEAT_PUMP_ONLINE_ENTITY,
            const.CONF_HEAT_PUMP_FAULT_ENTITY,
            const.CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY,
            const.CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY,
            const.CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY,
        ):
            on_change[k] = float("inf")

    now = datetime(2026, 1, 15, 3, 0, tzinfo=timezone.utc)
    keys = sorted(const.INPUT_MAX_AGE_MINUTES)
    print(f"RESULT age_limited_keys={len(keys)} keys")
    for q in QUIETS:
        for arm in ("quiet", "polled"):
            seams = []
            for key in keys:
                hass = harness.FakeHass()
                st = harness.FakeState(
                    "1.0",
                    last_updated=now - timedelta(minutes=q),
                    last_reported=(now - timedelta(minutes=1)) if arm == "polled" else None,
                )
                hass.states.set("sensor.x", st)
                r = InputReader(hass, {key: "sensor.x"}, now=lambda: now).read_state(key)
                if r.problem == "stale":
                    seams.append((key, r.max_age_minutes))
            for key, lim in seams:
                print(f"SEAM arm={arm} q={q} key={key} limit_min={lim}")
            print(f"RESULT {arm}_stale_q{q}={len(seams)} keys")
            if arm == "quiet":
                names = {k for k, _ in seams}
                if q == 255:
                    print(f"RESULT refind_D1_s5_51={int(const.CONF_INDOOR_TEMP_ENTITY in names)}")
                if q == 480:
                    print(f"RESULT refind_D14_s3_02={int(const.CONF_POWER_ENTITY in names)}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", default=".")
    ap.add_argument("--at", default=None, help="a git revision to export and measure")
    ap.add_argument("--reintroduce", choices=("power", "pump-flags-inf"), default=None)
    ap.add_argument("--child", action="store_true")
    a = ap.parse_args()
    if a.child:
        _child(a.tree, a.reintroduce)
        return 0
    t0, c0 = time.thread_time(), time.process_time()
    tree = a.tree
    tmp = None
    if a.at:
        tmp = tempfile.mkdtemp(prefix="d14s2-stale-", dir=os.environ.get("TMPDIR"))
        arch = subprocess.run(["git", "archive", a.at], check=True, capture_output=True).stdout
        subprocess.run(["tar", "-x", "-C", tmp], input=arch, check=True)
        tree = tmp
        print(f"# measuring {a.at} exported to {tmp}")
    env = dict(os.environ)
    env["PYTHONPATH"] = os.path.join(os.path.abspath(tree), "tests", "hastub")
    cmd = [sys.executable, os.path.abspath(__file__), "--child", "--tree", os.path.abspath(tree)]
    if a.reintroduce:
        cmd += ["--reintroduce", a.reintroduce]
    rc = subprocess.run(cmd, env=env).returncode
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as f:
            print("RESULT swapins=" + next(l.split()[1] for l in f if l.startswith("pswpin")))
    except OSError:
        print("RESULT swapins=unknown")
    return rc


if __name__ == "__main__":
    sys.exit(main())
