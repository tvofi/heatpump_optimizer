#!/usr/bin/env python3
"""Per-check mutation proofs and null controls for the seven repaired checks.

Round 1 of PR #573 was blocked because five new checks survived a production
mutation: three were identity tautologies (`x.forecast is x._forecast`, with
`_forecast` and `_observed` both initialised to the SAME `_EMPTY` singleton),
one used a `None` body that a LATER guard rejected regardless of the status
check it was named for, and one asserted an outcome that occurred on both
branches. Round 2 found two more of the same class already in the original
commit: the #21 humidity and #30 snowfall checks asserted only `len(...) == 6`
over two fixture blocks that are both length 6, so the two side series were
interchangeable. This script is the evidence that all seven discriminate.

For every repaired check it runs, in order:

  KILL     apply the exact production mutation the check is named for; the
           named check must FAIL.
  NULL     apply a DIFFERENT production mutation the check must ignore; the
           named check must still PASS (so the repair is not simply always-red),
           while the check that mutation IS named for fails.

The production file's md5 is captured before and after every mutation, so a
run that leaves the tree dirty is visible rather than assumed.

    PYTHONPATH=tests/hastub python3 tools/audit/w5-g5-195-coverage/mutation_probe.py
"""
from __future__ import annotations

import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
SRC = ROOT / "custom_components" / "heatpump_optimizer"
OPEN_METEO = SRC / "open_meteo.py"
FRONTEND = SRC / "frontend.py"


def md5(path: pathlib.Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def run_script(script: str) -> dict[str, bool]:
    """Run a test script and return {check name: passed}."""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "tests" / "hastub")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-B", str(ROOT / "tests" / script)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    results: dict[str, bool] = {}
    for line in proc.stdout.splitlines():
        m = re.match(r"^\s+(ok|FAIL)\s+(.*?)\s*$", line)
        if not m:
            continue
        name = m.group(2)
        # open_meteo.py's check() appends "  [detail]" to a FAILING line only,
        # so the raw remainder is not the check name on exactly the lines this
        # probe cares about. Stripping it is what makes a kill visible; without
        # it every genuine kill reports as NOT FOUND.
        name = re.sub(r"\s+\[.*\]$", "", name)
        results[name] = m.group(1) == "ok"
    return results


def mutate(path: pathlib.Path, old: str, new: str) -> None:
    text = path.read_text()
    if text.count(old) != 1:
        raise SystemExit(
            f"mutation anchor is not unique in {path.name} "
            f"({text.count(old)} occurrences): {old!r}"
        )
    path.write_text(text.replace(old, new))
    # Re-read from disk to prove the mutation is live, not a stale buffer.
    assert new in path.read_text(), "mutation did not reach disk"


# Every __pycache__ is purged once up front and bytecode writing is disabled
# for every child, so a "survived" verdict can never be a caching artifact.
for cached in ROOT.rglob("__pycache__"):
    shutil.rmtree(cached, ignore_errors=True)

# (label, file, old, new, script, check that must FAIL, checks that must PASS)
PROBES = [
    (
        "KILL 1  forecast property returns self._observed",
        OPEN_METEO, "    def forecast(self) -> IrradianceSeries:\n        return self._forecast",
        "    def forecast(self) -> IrradianceSeries:\n        return self._observed",
        "open_meteo.py",
        "forecast property returns the forecast series, not the observed one",
        ["observed property returns the observed series, not the forecast one"],
    ),
    (
        "KILL 2  observed property returns self._forecast",
        OPEN_METEO, "    def observed(self) -> IrradianceSeries:\n        return self._observed",
        "    def observed(self) -> IrradianceSeries:\n        return self._forecast",
        "open_meteo.py",
        "observed property returns the observed series, not the forecast one",
        ["forecast property returns the forecast series, not the observed one"],
    ),
    (
        "KILL 3  last_success returns literal None",
        OPEN_METEO, "    def last_success(self) -> datetime | None:\n        return self._last_success",
        "    def last_success(self) -> datetime | None:\n        return None",
        "open_meteo.py",
        "last_success property returns the recorded timestamp, not None",
        ["forecast property returns the forecast series, not the observed one"],
    ),
    (
        "NULL 3  available property forced False (last_success must ignore it)",
        OPEN_METEO, "        return bool(self._forecast) or bool(self._observed)",
        "        return False",
        "open_meteo.py",
        None,
        [
            "last_success property returns the recorded timestamp, not None",
            "forecast property returns the forecast series, not the observed one",
            "observed property returns the observed series, not the forecast one",
        ],
    ),
    (
        "KILL 4  _get_json status guard removed",
        OPEN_METEO, "                if resp.status != 200:",
        "                if False:",
        "open_meteo.py",
        "_get_json returns None on a non-200 status carrying an otherwise-good body",
        ["_get_json returns the parsed body on HTTP 200"],
    ),
    (
        "NULL 4  non-dict/error guard removed (status check must ignore it)",
        OPEN_METEO, "        if not isinstance(data, dict) or data.get(\"error\"):",
        "        if False:",
        "open_meteo.py",
        None,
        ["_get_json returns None on a non-200 status carrying an otherwise-good body"],
    ),
    (
        "KILL 5  .data fallback removed",
        FRONTEND, "        elif hasattr(resources, \"data\"):",
        "        elif False:",
        "frontend.py",
        "a resources object without async_items() falls back to .data",
        ["a missing resource is created"],
    ),
    (
        "NULL 5  shadow-copy warning removed (.data check must ignore it)",
        FRONTEND, "                _LOGGER.warning(\n                    \"Another copy of the Heat Pump Optimizer card is \"",
        "                _LOGGER.debug(\n                    \"Another copy of the Heat Pump Optimizer card is \"",
        "frontend.py",
        "the shadowing copy found via .data is named in a warning",
        ["a resources object without async_items() falls back to .data"],
    ),
    # Round 2 found two more of the identical class, both from the ORIGINAL
    # commit rather than the round-1 repair: the #21 humidity and #30 snowfall
    # checks asserted only len(...) == 6 and both fixture blocks are length 6,
    # so the two series were interchangeable. These two probes are each other's
    # null control by construction -- each swaps one side series onto the other
    # variable, and the check named for the UNMUTATED series must stay green.
    (
        "KILL 6  _humidity parsed from the snowfall block",
        OPEN_METEO,
        "        humidity = _parse_block(hourly_block, _VARIABLE_HUMIDITY, max_value=100.0)",
        "        humidity = _parse_block(hourly_block, _VARIABLE_SNOWFALL, max_value=100.0)",
        "open_meteo.py",
        "_fetch_forecast parses the humidity side series onto the client (#21)",
        ["_fetch_forecast parses the snowfall side series onto the client (#30)"],
    ),
    (
        "KILL 7  _snowfall parsed from the humidity block",
        OPEN_METEO,
        "        snowfall = _parse_block(hourly_block, _VARIABLE_SNOWFALL, max_value=50.0)",
        "        snowfall = _parse_block(hourly_block, _VARIABLE_HUMIDITY, max_value=100.0)",
        "open_meteo.py",
        "_fetch_forecast parses the snowfall side series onto the client (#30)",
        ["_fetch_forecast parses the humidity side series onto the client (#21)"],
    ),
]

baseline = {OPEN_METEO: md5(OPEN_METEO), FRONTEND: md5(FRONTEND)}
print(f"baseline md5 open_meteo.py = {baseline[OPEN_METEO]}")
print(f"baseline md5 frontend.py   = {baseline[FRONTEND]}\n")

# Unmutated control: every named check must pass on the clean tree.
clean = {s: run_script(s) for s in ("open_meteo.py", "frontend.py")}
failures = 0
for _, _, _, _, script, must_fail, must_pass in PROBES:
    for name in ([must_fail] if must_fail else []) + must_pass:
        if not clean[script].get(name, False):
            print(f"  CONTROL FAIL  {script}: {name!r} is not green on the clean tree")
            failures += 1
print(f"clean-tree control: every named check green = {failures == 0}\n")

for label, path, old, new, script, must_fail, must_pass in PROBES:
    original = path.read_text()
    mutate(path, old, new)
    try:
        results = run_script(script)
    finally:
        path.write_text(original)
    assert md5(path) == baseline[path], f"restore failed for {path.name}"

    ok = True
    detail = []
    if must_fail is not None:
        got = results.get(must_fail)
        if got is None:
            ok, note = False, "NOT FOUND"
        elif got:
            ok, note = False, "SURVIVED"
        else:
            note = "killed"
        detail.append(f'    {note:9s} "{must_fail}"')
    for name in must_pass:
        got = results.get(name)
        if got is not True:
            ok = False
            detail.append(f'    UNEXPECTED-FAIL "{name}" (must have been ignored)')
        else:
            detail.append(f'    ignored   "{name}"')
    print(f"{'PASS' if ok else 'FAIL'}  {label}")
    print("\n".join(detail))
    print(f"    restored, md5 {md5(path)} (unchanged)\n")
    if not ok:
        failures += 1

print(f"md5 after all probes: open_meteo.py {md5(OPEN_METEO)}, frontend.py {md5(FRONTEND)}")
print(f"RESULT probes={len(PROBES)} failures={failures}")
raise SystemExit(1 if failures else 0)
