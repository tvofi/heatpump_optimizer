#!/usr/bin/env python3
"""R10-REPLAY-REAL-DAY's mutation proof for the sites no CI lane mutates.

``mutation-autofix`` mutates ``custom_components/`` only, so the export's
recorder and masking guards (``tools/replay/export.py``), the fixture cutter
(``tools/replay/cut_day.py``) and the replay lane's own guards
(``tests/replay.py``) carry their proof here, in the tree, where a reviewer
re-runs it. Each mutant is one exact substitution, applied to a copy of the
tree (``tests``, ``tools``, ``custom_components``); the checks named beside it
must turn red, and the unmutated copy (the null) must be all green.

The fast tier runs, per mutant, ``tests/replay.py``'s ``controls()``,
``sanitiser_checks()`` over the committed fixtures and
``synthetic_reproduces()`` in a fresh interpreter -- seconds each. The slow
tier (``--replay``) replays ``tests/replay/owner-2026-10-30-away.json``
through ``tests/replay.py --one`` for the mutants only a recorded day can see
(the controls never run ``run_fixture``), minutes each.

Prints one ``KILLED``/``SURVIVED`` row per mutant, naming the red checks, and
``RESULT killed=<k> mutants=<n> null_red=<r>``. Run from a worktree root:

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_replay_real_day_mutants.py [--replay]
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
COPIED = ("tests", "tools", "custom_components")
OWNER = "tests/replay/owner-2026-10-30-away.json"
MARK = "<<<replay-json>>>"  # tests/replay.py MARK

EXPORT, CUT, LANE = "tools/replay/export.py", "tools/replay/cut_day.py", "tests/replay.py"

#: (name, file, old, new, a check that must turn red). ``old`` occurs once.
FAST = [
    ("no db_url from configuration.yaml", EXPORT,
     "url = db_url or (None if db else recorder_url(config_dir))", "url = db_url",
     "recorder:db_url_whole_day_read"),
    ("no read-only session", EXPORT,
     'cur.execute("SET SESSION TRANSACTION READ ONLY")', 'cur.execute("SELECT 1")',
     "recorder:db_url_read_only_session_selects_only"),
    ("URL not redacted", EXPORT,
     "return f\"{parts.scheme}://{parts.hostname or ''}{port}{parts.path}\"", "return url",
     "recorder:db_url_credentials_never_printed"),
    ("connect refusal carries the driver's text", EXPORT,
     'f"{type(err).__name__}") from None', 'f"{err}") from None',
     "recorder:db_url_connect_refusal_names_no_credential"),
    ("no quiet-input refusal", EXPORT, "    if quiet:\n", "    if False:\n",
     "recorder:stale_sqlite_near_empty_day_refused"),
    ("no !secret resolution", EXPORT,
     "return _secret(config_dir, _yaml_scalar(found.group(1)))",
     "return _yaml_scalar(found.group(1))", "recorder:url_from_configuration:secret"),
    ("no !include followed", EXPORT, "    if include:\n", "    if False:\n",
     "recorder:url_from_configuration:include"),
    ("retired-key filter removed", EXPORT,
     "mapped_entities({k: v for k, v in sec.items() if k in conf})",
     "mapped_entities(sec)", "recorder:retired_key_left_out"),
    ("untimed dropped from check_file", EXPORT,
     "return found + untimed(payload)", "return found",
     "mask:check_refuses_a_document_with_its_times_nulled"),
    ("no thinning", CUT,
     "thinned(rows, ahead if _read_ahead(doc, eid) else instants)", "rows",
     "cut_day:every_cycle_instant_reads_as_the_whole_export"),
    ("no read-ahead", CUT,
     "ahead if _read_ahead(doc, eid) else instants", "instants",
     "cut_day:price_series_kept_to_the_export_end"),
    ("a restart counted as a reload", CUT,
     "and not inputs.get(minute))", ")",
     "cut_day:null_restart_with_inputs_gone_is_no_reload"),
    ("published entities kept", CUT,
     'for eid, rows in doc["states"].items() if eid in doc["inputs"]}',
     'for eid, rows in doc["states"].items()}', "cut_day:no_published_entity_kept"),
    ("two paired switches not refused", CUT,
     "if len(switches) > 1 or (set_at and not switches):",
     "if set_at and not switches:", "cut_day:two_paired_switches_refused"),
    ("away floor unchecked", LANE,
     'o["floor"] <= o["target"])', "True)", "control:away:floor"),
    ("away override unchecked", LANE,
     'if not (o["active"] and o["override"] and floor_ok):',
     'if not (o["active"] and floor_ok):', "control:away:override"),
    ("away command not compared with the recording", LANE,
     'if bool(held) != bool(o.get("commanded_return")):', "if False:",
     "control:away:replayed"),
    ("no_default setpoint exemption removed", LANE,
     "for k in supplied):", "for k in ()):",
     "control:no_default:setpoint_value_on_a_reading"),
    ("no_default setpoint exemption on every entity", LANE,
     'SETPOINT_KEYS.get(rec.get("key"), ())', '("max_temperature",)',
     "control:no_default:setpoint_value_on_a_reading"),
    ("no_default setpoint at any value", LANE,
     "if any(config.get(k) is not None and _is(v, config[k]) for k in supplied):",
     "if supplied:",
     "control:no_default:setpoint_at_an_unconfigured_default"),
    ("arms skipped everywhere allowed", LANE,
     "    if not committed - skipped:\n", "    if False:\n",
     "control:cycle_cost:arms_skipped_never_everywhere"),
]

#: (name, file, old, new, the fixture's result key that must hold offenders).
REPLAY = [
    ("the recorded away command not replayed (round 1's survivor)", LANE,
     "commanded = returns if active else None", "commanded = None", "away"),
    ("no_default setpoint exemption not handed the config", LANE,
     "inv_no_default(records, defaults, readings, config)",
     "inv_no_default(records, defaults, readings)", "no_default"),
]

FAST_DRIVER = """
import json, sys; sys.path.insert(0, 'tests'); import replay
try:
    r = (replay.controls() + replay.sanitiser_checks(sorted(replay.FIXTURES.glob('*.json')))
         + [replay.synthetic_reproduces()])
    red = [n for n, ok, _ in r if not ok]
    print('RED ' + json.dumps(red))
except BaseException as err:
    print('RED ' + json.dumps(['raised ' + type(err).__name__ + ': ' + str(err)[:120]]))
"""


def env() -> dict[str, str]:
    out = {**os.environ, "PYTHONPATH": "tests/hastub"}
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        out.setdefault(var, "1")
    return out


def fast(tree: Path) -> list[str]:
    proc = subprocess.run([sys.executable, "-c", FAST_DRIVER], cwd=tree, env=env(),
                          capture_output=True, text=True)
    line = next((ln for ln in proc.stdout.splitlines() if ln.startswith("RED ")), None)
    if line is None:
        return [f"no result: rc={proc.returncode} {proc.stderr.strip()[-200:]}"]
    return json.loads(line[4:])


def replay(tree: Path) -> dict:
    zone = json.loads((tree / OWNER).read_text()).get("time_zone") or "UTC"
    proc = subprocess.run([sys.executable, "tests/replay.py", "--one", OWNER], cwd=tree,
                          env={**env(), "HASTUB_TZ": zone}, capture_output=True, text=True)
    line = next((ln for ln in proc.stdout.splitlines() if ln.startswith(MARK)), None)
    if line is None:
        return {"counts": {}, "error": f"rc={proc.returncode} {proc.stderr.strip()[-200:]}"}
    return json.loads(line[len(MARK):])


def apply(tree: Path, rel: str, old: str, new: str) -> str:
    path = tree / rel
    text = path.read_text()
    if text.count(old) != 1:
        raise SystemExit(f"{rel}: the mutant's site occurs {text.count(old)} times: {old!r}")
    path.write_text(text.replace(old, new))
    return text


def main(argv: list[str]) -> int:
    slow = "--replay" in argv
    killed = total = 0
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp)
        for name in COPIED:
            shutil.copytree(ROOT / name, tree / name, ignore=shutil.ignore_patterns(
                "__pycache__", ".mypy_cache"))
        null = fast(tree)
        print(f"null: red {null}")
        for name, rel, old, new, want in FAST:
            original = apply(tree, rel, old, new)
            try:
                red = fast(tree)
            finally:
                (tree / rel).write_text(original)
            hit = want in red or any(r.startswith("raised") for r in red)
            killed += hit
            total += 1
            print(f"{'KILLED' if hit else 'SURVIVED'} {rel}: {name}: red {red[:4]}")
        null_replay = None
        if slow:
            null_replay = replay(tree)["counts"]
            print(f"null replay: counts {null_replay}")
            for name, rel, old, new, key in REPLAY:
                original = apply(tree, rel, old, new)
                try:
                    counts = replay(tree)["counts"]
                finally:
                    (tree / rel).write_text(original)
                hit = counts.get(key, 0) > 0
                killed += hit
                total += 1
                print(f"{'KILLED' if hit else 'SURVIVED'} {rel}: {name}: counts {counts}")
    null_red = len(null) + (sum((null_replay or {}).get(k, 0) for k in
                                ("away", "no_default")) if slow else 0)
    print(f"RESULT killed={killed} mutants={total} null_red={null_red}")
    return 0 if killed == total and not null_red else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
