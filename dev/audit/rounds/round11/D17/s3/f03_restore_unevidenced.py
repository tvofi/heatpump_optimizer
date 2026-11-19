"""D17-s3-03: restore_learned_snapshot accepts a snapshot that carried no accuracy evidence.

Documented effect (strings.json services.restore_learned_snapshot, and
docs/configuration.md): roll every learner back to the most recent weekly
snapshot "captured while all inputs were healthy and prediction accuracy was
in band"; "The call fails with an error when no snapshot qualifies".

Metric: on a fresh install after one update cycle (the ring then holds only
the snapshot the first heartbeat takes), the number of restore calls that
succeed out of one, plus the snapshot's recorded ``accuracy.temperature_bias``
and the house heat-loss scale after the call when the learner had moved to
1.3 since the snapshot (the state the restore discards).

Key: the action's outcome through its registered schema (raised or not) and
the coordinator's published ``house_heat_loss_scale`` after it.

Perturbation (``--perturb``): ``snapshots:SnapshotRing.best_restore`` skips a
snapshot whose ``temperature_bias`` is None (the one-line
``if bias is None: continue`` before the band test), applied in memory; the
restore count moves 1 -> 0 (to_zero) and the scale stays 1.3.

Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D17/s3/f03_restore_unevidenced.py [--perturb]
Expected (baseline): restored=1, snapshot_bias_is_none=1, scale_after=1.0; exact.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13 (shared, 3 seats).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402

import asyncio  # noqa: E402
import logging  # noqa: E402
import time  # noqa: E402

logging.disable(logging.WARNING)
PERTURB = "--perturb" in sys.argv


async def main() -> None:
    from heatpump_optimizer import snapshots

    if PERTURB:
        orig = snapshots.SnapshotRing.best_restore

        def patched(self):
            saved = self.snapshots
            self.snapshots = [
                s for s in saved
                if (s.get("accuracy") or {}).get("temperature_bias") is not None
            ]
            try:
                return orig(self)
            finally:
                self.snapshots = saved

        snapshots.SnapshotRing.best_restore = patched

    t0, t1 = time.process_time(), time.thread_time()
    rig.freeze()
    inst = rig.Install(entry_id="f03")
    await inst.setup()
    await inst.cycle()
    ring = inst.coord._snapshot_ring.snapshots
    print(f"RESULT snapshots_in_ring={len(ring)} count")
    bias_none = sum(
        1 for s in ring if (s.get("accuracy") or {}).get("temperature_bias") is None
    )
    print(f"RESULT snapshot_bias_is_none={bias_none} count")
    # Learning moves on after the snapshot.
    inst.coord._apply_house_heat_loss_scale(1.3)
    inst.coord._house_heat_loss_samples = 40
    restored = 0
    try:
        await inst.call("restore_learned_snapshot", {})
        restored = 1
    except Exception as err:  # noqa: BLE001
        print(f"# refused: {type(err).__name__}: {err}")
    data = await inst.cycle()
    print(f"RESULT restored={restored} count")
    print(f"RESULT scale_after={data['house_heat_loss_scale']} ratio")
    print(f"RESULT perturbed={int(PERTURB)} bool")
    rig.footer(t0, t1)


asyncio.run(main())
