"""Add the resume run's re-take to D3-s1-01's evidence (writes r2/f01.json)."""
import json
from pathlib import Path

S1 = Path(__file__).resolve().parent.parent
f = next(x for x in json.loads((S1 / "findings.json").read_text()) if x["id"] == "D3-s1-01")
f["evidence"]["rerun_r2"] = (
    "Resume run 2026-11-17T19:27-19:31Z, same machine (owner macOS arm64, 8 cores, load1 226-255): "
    "prescreen.py trace-capture re-took env_drift's --capture --all reach (rc=0, wall 217.4 s provisional, "
    "processes 2/2 recorded); its per-file executed lines equal the local run's exactly "
    "(state/baselines-local.json vs state/baselines.json). m5_envdrift_reach.py: capture_never_executes=681, "
    "gate_skippable=0; --as-if-fixed: gate_skippable=681; null_skippable=0 of 579. The count reproduces: 681 stands. "
    "Outputs: state/retrace-cap-r2.out, state/envdrift-reach-r2.out, state/envdrift-reach-r2-fixed.out.")
(S1 / "r2" / "f01.json").write_text(json.dumps(f, indent=1))
