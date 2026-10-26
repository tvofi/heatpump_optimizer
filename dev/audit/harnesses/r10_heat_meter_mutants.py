#!/usr/bin/env python3
"""R10-HEAT-METER (#2261): the mutation table for the design's mutation targets.

    python3 dev/audit/harnesses/r10_heat_meter_mutants.py [-j N] [NAME ...]   (from the repository root)

Each mutant is one exact string replacement in a production file, applied to
its own copy of the committed tree (``git archive HEAD``), never the working
tree; ``tests/features.py`` runs in that copy and the row prints its summary
line and the first failing checks. A mutant is killed when the summary names
more failing checks than the unmutated null control row, which is a
comment-only edit run the same way. A ``NOT APPLIED`` row means the mutated
text moved: the table is stale and says so instead of reading as a survivor.
Rows, by the design's target list: C1 the span-close condition, C2 the
time-close (span too long) comparison, Q the ``q / expected`` bound, R the
reset branch, P the counter-first precedence (#2753's M1 mirror), O the
``observed`` test in ``attribution``, L the ``last_changed`` split, E the
earned-basis upgrade, A the ``span_clean`` AND, I the ``integrated`` branch
in ``space_heat_kw``; and the carries' own: D the counter's on-change decision
(R10-INPUT-STALENESS), L6 the house meter's on-change limit, L9 the snapshot's
named input (the D15 leads).
"""
from __future__ import annotations

import argparse
import concurrent.futures
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

PKG = "custom_components/heatpump_optimizer/"
HE, CO, FM = PKG + "heat_energy.py", PKG + "coordinator.py", PKG + "flow_meter.py"

MUTANTS = {
    "N0 null control (a comment)": (HE, "def _after(newer: datetime, older: datetime) -> bool:\n",
                                    "def _after(newer: datetime, older: datetime) -> bool:  # null\n"),
    "C1 span closes at the minimum, not past close_after_h": (
        HE, "elif hours < close_after_h(cadence_h, bounds_h):", "elif hours < bounds_h[0]:"),
    "C2 a span past the maximum is not refused": (
        HE, "        if hours > bounds_h[1]:\n            self.refusal = SPAN_REFUSED_LONG\n        elif",
        "        if False:\n            self.refusal = SPAN_REFUSED_LONG\n        elif"),
    "Q resolution bound dropped": (
        HE, "if q is None or not expected_kwh > 0.0 or q / expected_kwh > HEAT_RESOLUTION_EPS:",
        "if q is None or not expected_kwh > 0.0:"),
    "R reset branch dropped": (HE, "        elif heat_kwh < 0.0:\n", "        elif False:\n"),
    "P counter-first precedence dropped": (
        FM, "    if cfg.get(const.CONF_HEAT_ENERGY_ENTITY):\n", "    if False:\n"),
    "O observed test inverted": (HE, "    if shares is not None:\n        return Attribution(shares[0], shares[1], True)",
                                 "    if shares is None and False:\n        return Attribution(shares[0], shares[1], True)"),
    "L split at the read, not at last_changed": (
        HE, "Segment(changed_at if changed_at is not None and moved else seen, duty)", "Segment(seen, duty)"),
    "E earned basis never set": (CO, "    meter.earned = True\n", "    pass\n"),
    "A span_clean AND dropped (last cycle wins)": (
        HE, "self._clean = {k: self._clean.get(k, True) and v for k, v in clean.items()}",
        "self._clean = {k: v for k, v in clean.items()}"),
    "I integrated branch ignored": (HE, "    if a.observed and integrated:\n", "    if a.observed:\n"),
    "D the heat counter's on-change decision dropped": (
        PKG + "const.py", "    CONF_HEAT_ENERGY_ENTITY: math.inf,  # and so does the heat it delivered\n", ""),
    "L6 the house meter's on-change limit back to 30 min": (
        PKG + "const.py", "    CONF_HOUSE_POWER_ENTITY: math.inf,  # a quiet circuit holds its reading\n",
        "    CONF_HOUSE_POWER_ENTITY: 30.0,  # a quiet circuit holds its reading\n"),
    "L9 the snapshot ignores the named input": (
        PKG + "snapshots.py", '"unhealthy_input": None if healthy else self.day_unhealthy,',
        '"unhealthy_input": None,'),
}

SUMMARY = re.compile(r"^(ALL \d+ FEATURE CHECKS PASSED|\d+ of \d+ FEATURE CHECKS FAILED)", re.M)


def _tree(root: Path) -> Path:
    out = Path(tempfile.mkdtemp(prefix="r10hm-mut-"))
    blob = subprocess.run(["git", "-C", str(root), "archive", "HEAD"], check=True, capture_output=True).stdout
    tar_path = out / "tree.tar"
    tar_path.write_bytes(blob)
    with tarfile.open(tar_path) as tar:
        tar.extractall(out, filter="data")
    tar_path.unlink()
    return out


def _run(root: Path, name: str) -> tuple[str, int | None, str]:
    path, old, new = MUTANTS[name]
    tree = _tree(root)
    target = tree / path
    text = target.read_text()
    if text.count(old) != 1:
        return name, None, f"NOT APPLIED ({text.count(old)} matches in {path})"
    target.write_text(text.replace(old, new))
    run = subprocess.run(
        [sys.executable, "tests/features.py"], cwd=tree, capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": "tests/hastub", "PYTHONHASHSEED": "0"}, timeout=3600,
    )
    out = run.stdout + run.stderr
    m = SUMMARY.search(out)
    failed = 0 if m and m.group(1).startswith("ALL") else (int(m.group(1).split()[0]) if m else -1)
    fails = [ln.strip()[:160] for ln in out.splitlines() if ln.startswith("  FAIL")][:3]
    summary = m.group(1) if m else f"no summary (rc={run.returncode}) {out[-300:]!r}"
    return name, failed, summary + "".join("\n      " + f for f in fails)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-j", type=int, default=3)
    ap.add_argument("names", nargs="*")
    args = ap.parse_args()
    root = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True,
                               capture_output=True, text=True).stdout.strip())
    names = [n for n in MUTANTS if not args.names or any(n.startswith(p) for p in args.names)]
    if not any(n.startswith("N0") for n in names):
        names.insert(0, next(iter(MUTANTS)))
    with concurrent.futures.ThreadPoolExecutor(args.j) as pool:
        rows = dict((r[0], r[1:]) for r in pool.map(lambda n: _run(root, n), names))
    null = rows[next(iter(MUTANTS))][0]
    survivors = 0
    for name in names:
        failed, text = rows[name]
        if name.startswith("N0"):
            verdict = "NULL" if failed == 0 else "NULL DIED"
        elif failed is None or failed < 0:
            verdict = "STALE"
        else:
            verdict = "KILLED" if null is not None and failed > null else "SURVIVED"
        survivors += verdict in ("SURVIVED", "STALE", "NULL DIED")
        print(f"{verdict:9} {name}: {text}")
    print(f"{survivors} survivor(s) of {len(names) - 1} mutant(s), null failed={null}")
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main())
