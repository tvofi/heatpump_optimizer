#!/usr/bin/env python3
"""The architecture score's own check (R9-EG-A1): its calibration, and the games that must stay closed.

The score (tools/audit/archscore/) is a report and a review trigger, never a gate on other pull
requests, so this is a regression test on the INSTRUMENT. It re-runs the calibration and fails when a
metric change silently moves a verdict or re-opens a game:

  * every planted case (58 scripted edits of the pinned tree) and every red-team attempt is measured
    LIVE; the 45 corpus commits use their stored vectors (they are history). Each case's verdict and
    admissibility must equal tools/audit/archscore/calibration/expected.json, misses included -- a case
    the score gets wrong stays recorded as wrong, and one that turns, even to the right verdict, fails
    until ``calibrate.py --record`` makes it a diff a reviewer reads;
  * no red-team attempt reads IMPROVES, and the rename null reads NULL;
  * halving or doubling any weight, or equalising them, moves no verdict (what expected.json
    records under ``_sensitivity``);
  * the weights are the frozen file: tools/audit/archscore/weights.json hashes to FROZEN_WEIGHTS below.
    A weight change is a policy change, so it is a change to this file as well, which is code-owned;
  * the check can fail: the same comparison on a vector with one metric nudged does not read as before.

The corpus and the planted verdicts are what the pre-study recorded (PRE-STUDY section 6 on
handoff/audit-r9-alt), re-measured with the metrics tests/structure.py now defines; the changes that made
are listed in tools/audit/archscore/ABOUT.md.

    PYTHONPATH=tests/hastub python3 tests/arch_score.py            full
    PYTHONPATH=tests/hastub python3 tests/arch_score.py --stored   corpus and weights only, seconds
    PYTHONPATH=tests/hastub python3 tests/arch_score.py --smoke    --stored, and every planted case built but not
                                                                   measured: what the closure is recorded with, since
                                                                   it reads every file the full run does

It measures the PINNED tree and stored history, never the working tree, so a change to the integration
does not select it. tests/arch_score_head.py is the one that reads today's tree.
"""
from __future__ import annotations

import ast
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools" / "audit"))

from harness import Results  # noqa: E402

from archscore import calibrate, score, vector  # noqa: E402

FROZEN_WEIGHTS = "2891a874ad476d7d761743ae7c47bae9779e150190aaf65f9a82e06ddd867978"

R = Results("architecture score calibration (R9-EG-A1)")


def smoke() -> None:
    """Every planted case's script applies to the pin: the anchors still hold and every file the full
    run reads is read, at the cost of the scripts alone. The helpers the scripts import are read and
    parsed here too: a script runs as a child process, whose own reads the recorder does not see."""
    sys.path.insert(0, str(calibrate.HERE / "planted"))
    # The full run loads tests/structure.py for every case, in worker processes the recorder does not
    # see; loading it here puts it in the recorded closure, so a structure.py-only diff selects this script.
    R.check("tests/structure.py loads as the score's definition source",
            hasattr(vector.load_structure(ROOT), "duplicate_clones"))
    for helper in sorted((calibrate.HERE / "planted").rglob("*.py")):
        try:
            ast.parse(helper.read_text())
            ok, detail = True, ""
        except SyntaxError as err:
            ok, detail = False, str(err)
        R.check(f"{helper.relative_to(calibrate.HERE)} parses", ok, detail)
    import cases
    with tempfile.TemporaryDirectory(prefix="archscore-smoke-") as tmp:
        pin = cases.extract_pin(Path(tmp) / "pin")
        for c in cases.cases():
            try:
                cases.build(c, pin, Path(tmp) / "w")
                ok, detail = True, ""
            except Exception as err:  # reported against the case
                ok, detail = False, f"{type(err).__name__}: {str(err)[-300:]}"
            R.check(f"{c['id']} applies to the pinned tree", ok, detail)


def main() -> int:
    only_smoke = "--smoke" in sys.argv
    stored = "--stored" in sys.argv or only_smoke
    want = json.loads(calibrate.EXPECTED.read_text())
    want_sens = want.pop("_sensitivity", {})

    R.check("weights.json is the frozen file", score.weights_hash() == FROZEN_WEIGHTS,
            f"hash {score.weights_hash()}")
    recorded = (calibrate.HERE / "weights.sha256").read_text().split()[0]
    R.check("weights.sha256 names the frozen file", recorded == FROZEN_WEIGHTS, recorded)

    jobs = min(4, os.cpu_count() or 1)
    collected = calibrate.collect(stored, jobs)
    rows = calibrate.classify(collected)
    got = calibrate.pinned(rows, collected)
    got_sens = got.pop("_sensitivity")
    ids = {r["id"] for r in rows}
    R.check("every case is recorded, and every recorded case ran",
            ids <= set(want) and (stored or ids == set(want)),
            f"unrecorded {sorted(ids - set(want))} unrun {sorted(set(want) - ids) if not stored else '-'}")
    for r in rows:
        w = want.get(r["id"])
        R.check(f"{r['id']} ({r['label']}) classifies as recorded", w == got[r["id"]],
                f"recorded {w} now {got[r['id']]}; rises {r['rises'][:3]}")
    R.check("no weight perturbation moves a verdict beyond what is recorded", got_sens == want_sens,
            f"recorded {want_sens} now {got_sens}")
    if only_smoke:
        smoke()
    if not stored:
        games = [r for r in rows if r["set"] == "redteam" and r["label"] == "GAME"]
        R.check("the red-team attempts are all present", len(games) >= 39, f"{len(games)}")
        R.check("no red-team attempt reads IMPROVES",
                not [r["id"] for r in games if r["verdict"] == "IMPROVES"],
                f"{[r['id'] for r in games if r['verdict'] == 'IMPROVES']}")
        import cases
        known = [r for r in rows if r["label"] == "KNOWN-OPEN"]
        R.check("the known-open attempts are present and still read IMPROVES (a class fix flips them: re-record)",
                len(known) == len(cases.KNOWN_OPEN) and all(r["verdict"] == "IMPROVES" for r in known),
                f"{[(r['id'], r['verdict']) for r in known]}")
        R.check("the rename null reads NULL",
                next(r for r in rows if r["id"] == "rt_00_null_rename")["verdict"] == "NULL")

    # The check can fail: a moved case must not read as it did.
    good = next(c for c in collected if c["id"] == "d979110c")
    nudged = {**good["cur"], "coord_footprint": good["cur"]["coord_footprint"] + 500}
    R.check("a vector with one metric nudged up changes the verdict",
            score.delta(good["base"], good["cur"])["verdict"] != score.delta(good["base"], nudged)["verdict"],
            "the comparison is blind to a metric")
    return R.close("ARCHITECTURE SCORE CHECKS")


if __name__ == "__main__":
    raise SystemExit(main())
