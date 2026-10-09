#!/usr/bin/env python3
"""The architecture score's own check (R9-EG-A1): its calibration, and the games that must stay closed.

The score (tools/audit/archscore/) is a review trigger; the required check `arch-score` grades other
pull requests with it (gate.py, R9-EG-A4), and this script is the regression test on the INSTRUMENT. It re-runs the calibration and fails when a
metric change silently moves a verdict or re-opens a game:

  * every planted case (a scripted edit of the pinned tree) and every red-team attempt is measured
    LIVE; the 45 corpus commits use their stored vectors (they are history). Each case's verdict and
    admissibility must equal tools/audit/archscore/calibration/expected.json, misses included -- a case
    the score gets wrong stays recorded as wrong, and one that turns, even to the right verdict, fails
    until ``calibrate.py --record`` makes it a diff a reviewer reads;
  * no red-team attempt reads IMPROVES, and the rename null reads NULL; how many there are is
    derived from planted/redteam/ and expected.json, never a literal;
  * halving or doubling any weight, or equalising them, moves no verdict (what expected.json
    records under ``_sensitivity``);
  * the weights are the frozen file: tools/audit/archscore/weights.json hashes to FROZEN_WEIGHTS below.
    A weight change is a policy change, so it is a change to this file as well, which is code-owned;
  * the check can fail: the same comparison on a vector with one metric nudged does not read as before;
  * the required check's rule (archscore/gate.py, R9-EG-A4): an admissible change passes, a rise passes
    only explained under ``## Architecture score``, one line per metric.

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
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools" / "audit"))

from harness import Results  # noqa: E402
from throwaway_git import throwaway_git_init  # noqa: E402

from archscore import calibrate, gate, score, vector  # noqa: E402

FROZEN_WEIGHTS = "2891a874ad476d7d761743ae7c47bae9779e150190aaf65f9a82e06ddd867978"

R = Results("architecture score calibration (R9-EG-A1)")


def attributes_do_not_hide_code() -> None:
    """#2068 round 2, plant 2: ``git archive`` honours ``export-ignore``, so a head's own (nested) ``.gitattributes``
    could hide a module from the scorer. ``score.tree_of`` reads the tree object instead."""
    with tempfile.TemporaryDirectory(prefix="archscore-attr-") as tmp:
        repo, pkg = Path(tmp) / "r", Path(tmp) / "r" / "custom_components" / "p"
        pkg.mkdir(parents=True)
        env = throwaway_git_init(repo, "-q")
        for name in ("a.py", "hidden.py"):
            (pkg / name).write_text("X = 1\n")
        (pkg / ".gitattributes").write_text("hidden.py export-ignore\n")
        for cmd in (["add", "-A"], ["commit", "-qm", "plant"]):
            subprocess.run(["git", "-C", str(repo), *cmd], check=True, env=env)
        archived = subprocess.run(["git", "-C", str(repo), "archive", "HEAD", "custom_components"],
                                  capture_output=True, check=True, env=env).stdout
        out, saved = Path(tmp) / "out", score.REPO
        out.mkdir()
        score.REPO = repo
        try:
            score.tree_of("HEAD", out)
        finally:
            score.REPO = saved
        got = sorted(f.name for f in (out / "custom_components" / "p").iterdir())
        R.check("the plant is real: git archive drops the export-ignore'd module (control)",
                not any(n.endswith("/hidden.py") for n in tarfile.open(fileobj=io.BytesIO(archived)).getnames()),
                "archive kept it")
        R.check("score.tree_of extracts the module the head's .gitattributes marks export-ignore",
                got == [".gitattributes", "a.py", "hidden.py"], f"{got}")
        # Plant 5 (#2068 round 3): a .py symlink to a .txt blob is imported by Python and unseen by a scorer
        # that skips links. A link is refused by name.
        (pkg / "linked.py").symlink_to("notes.txt")
        (pkg / "notes.txt").write_text("X = 1\n")
        for cmd in (["add", "-A"], ["commit", "-qm", "plant5"]):
            subprocess.run(["git", "-C", str(repo), *cmd], check=True, env=env)
        score.REPO = repo
        try:
            score.tree_of("HEAD", Path(tmp) / "out5")
            refused = ""
        except score.UnsupportedEntry as e:
            refused = str(e)
        finally:
            score.REPO = saved
        R.check("a symlink under custom_components/ is refused by name, not skipped (plant 5)",
                "linked.py is a symlink" in refused, f"{refused!r}")


def base_runs_the_gate() -> None:
    """The reviewer's plant on #2068 (round 1): ``vector.load_structure`` runs ``tests/structure.py`` inside the
    gate's process, so a pull request that edits it could wave its own rises through. The workflow runs the
    gate from a checkout of the BASE; this drives the workflow's own score step over a throwaway repository
    whose stub gate prints the ``tests/structure.py`` it can see. The head's copy is the plant."""
    import re

    import yaml
    steps = yaml.safe_load((ROOT / ".github" / "workflows" / "arch-score.yml").read_text())["jobs"]["arch-score"]["steps"]
    script = next(st["run"] for st in steps if st.get("name", "").startswith("Score the change"))
    stub = ('import sys\nfrom pathlib import Path\n'
            'if "--self-test" not in sys.argv:\n    print("SAW " + Path("tests/structure.py").read_text().strip())\n')

    def run(base_has_gate: bool) -> str:
        with tempfile.TemporaryDirectory(prefix="archscore-plant-") as tmp:
            repo, env = Path(tmp) / "r", {**os.environ, "RUNNER_TEMP": str(Path(tmp) / "t")}
            (Path(tmp) / "t").mkdir()
            (repo / "tests").mkdir(parents=True)
            g = ["git", "-C", str(repo)]
            env = {**env, **throwaway_git_init(repo, "-q")}
            (repo / "tests" / "structure.py").write_text("BASE\n")
            if base_has_gate:
                (repo / "tools" / "audit" / "archscore").mkdir(parents=True)
                (repo / "tools" / "audit" / "archscore" / "gate.py").write_text(stub)
            subprocess.run([*g, "add", "-A"], check=True, env=env)
            subprocess.run([*g, "commit", "-qm", "base"], check=True, env=env)
            base = subprocess.run([*g, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
            (repo / "tests" / "structure.py").write_text("PLANT\n")
            gate_dir = repo / "tools" / "audit" / "archscore"
            gate_dir.mkdir(parents=True, exist_ok=True)
            (gate_dir / "gate.py").write_text(stub)
            subprocess.run([*g, "add", "-A"], check=True, env=env)
            subprocess.run([*g, "commit", "-qm", "head"], check=True, env=env)
            head = subprocess.run([*g, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
            r = subprocess.run(["bash", "-c", script], cwd=repo, capture_output=True, text=True,
                               env={**env, "PR_BASE": base, "PR_HEAD": head})
            return r.stdout + r.stderr

    attributes_do_not_hide_code()
    out = run(True)
    R.check("arch-score.yml: a head edit to tests/structure.py is not what the gate loads (the #2068 plant)",
            re.search(r"^SAW BASE$", out, re.M) is not None and "PLANT" not in out, out[-300:])
    out = run(False)
    R.check("and a base with no gate.py is the adoption: the head's copy runs once (null control)",
            re.search(r"^SAW PLANT$", out, re.M) is not None, out[-300:])


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

    # The required check's decision rule (R9-EG-A4): what passes, and what an explanation must carry.
    for name, ok in gate.self_test():
        R.check(f"arch-score gate: {name}", ok)
    base_runs_the_gate()

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
        # The counts are derived, never carried: the red-team scripts on disk, labelled by cases.py,
        # against what expected.json records (code-owned, so a case leaves only by an owner's review).
        import cases
        on_disk = {f"rt_{p.stem}" for p in (calibrate.HERE / "planted" / "redteam").glob("[0-9]*.py")}
        recorded = {lab: {k for k, v in want.items() if v["set"] == "redteam" and v["label"] == lab}
                    for lab in ("GAME", "KNOWN-OPEN")}
        games = [r for r in rows if r["set"] == "redteam" and r["label"] == "GAME"]
        R.check("the red-team attempts are all present: every script is a case, every recorded GAME ran",
                {r["id"] for r in games} == recorded["GAME"] and {r["id"] for r in rows} >= on_disk,
                f"ran {len(games)} recorded {len(recorded['GAME'])}; "
                f"missing {sorted(recorded['GAME'] - {r['id'] for r in games})}")
        R.check("no red-team attempt reads IMPROVES",
                not [r["id"] for r in games if r["verdict"] == "IMPROVES"],
                f"{[r['id'] for r in games if r['verdict'] == 'IMPROVES']}")
        known = [r for r in rows if r["label"] == "KNOWN-OPEN"]
        R.check("the known-open attempts are present and still read IMPROVES (a class fix flips them: re-record)",
                {r["id"] for r in known} == recorded["KNOWN-OPEN"] == {f"rt_{k}" for k in cases.KNOWN_OPEN}
                and all(r["verdict"] == "IMPROVES" for r in known),
                f"{[(r['id'], r['verdict']) for r in known]}; recorded {sorted(recorded['KNOWN-OPEN'])}")
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
