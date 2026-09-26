#!/usr/bin/env python3
"""The judge's scripted re-runs: every finding's harness, perturbation and null
control, serially, under the gate lease, one table row per finding.

`tools/audit/briefs/judge.md` makes a scripted re-run of the headers' commands
the judge's own measurement, and keeps the verdicts the judge's. So this script
measures and never decides: a row says what ran, what it printed and whether
the perturbation moved the number in the stated direction; `void` is the one
mechanical consequence judge.md step 2 draws from that, and everything the
script cannot run is `by-hand`, never a pass.

    python3 tools/audit/judge_batch.py --input JUDGE-INPUT.json \\
        --label judge-r9 --out-json rows.json --out-md rows.md [--shard 1/2]

INPUT is a JSON list of findings in `tools/audit/finding.schema.json`'s shape
(or entries carrying one under `finding`, as round 8's JUDGE-INPUT.json does).
Per finding it reads the harness at `evidence.harness_path` and takes, from the
harness header as `tests/harness_headers.py` delimits it (`header_lines`), any
of these lines, each on one line, with any comment prefix:

    JUDGE-RUN: <command>        default: the finding's evidence.command
    JUDGE-PERTURB: <command>    absent: perturbation `by-hand`
    JUDGE-NULL: <command>       absent: null control `by-hand`
    JUDGE-METRIC: <RESULT name> default: the header's first EXPECTED RESULT
    JUDGE-TOLERANCE: <rule>     default: the finding's evidence.tolerance

A finding may carry `judge_batch: {run, perturb, null, metric, tolerance}`,
which the judge writes to override the header for its own measurement. The
expected value is the header's `RESULT <metric>=<value>` (`expected_from`).
Direction is the finding's `perturbation.expected_direction`: `up`, `down`,
`to_zero`, `sign_flip`. Tolerance rules read: `exact`, `±N %` / `+-N%`
(relative), `±N` / `+-N` (absolute); anything else is `by-hand`.

`load1` and `thread_factor` are what the harness printed on its main run
(the harness contract in `tools/audit/README.md` requires both); a harness that
printed no `load1` gets the batch's own 1-minute load, flagged, and one that
printed no `thread_factor` is flagged, as is a factor over 1.05 (re-take).

The lease is `tests/gate_lock.py`'s: taken once, with this process as its
owner pid and a lease longer than one command's timeout, renewed before each
command (a refused renew releases and queues again behind the waiter, as
`gate-scoping.md` says), released on exit. Commands run from `--repo` through
`bash -c`, one at a time, with the LEASE held and flock NOT held: the child sees
`HPO_GATE_LOCK_DIR` and `HPO_GATE_LOCK_LABEL`, so a harness that goes through
`tests/run.sh` onto `stress.py`, or through `gate_lock.py flock-wrap`, renews
this label and takes flock itself -- the route `run.sh` already has for a seat's
own label. Holding flock here instead would make that nested take wait out the
command's whole timeout.

Every command runs against a snapshot of the tree (`git status --porcelain`,
untracked included, plus the bytes of every path already dirty): a command that
leaves the tree different -- a perturbation that edits production on disk, or a
harness killed at the timeout before its own restore ran -- is flagged
`tree edited by <arm>` on its row and the tree is put back before the next
command (tracked paths from the snapshot or `git checkout`, new files removed),
so one finding's perturbation cannot move the next finding's number. A `--repo`
that is not a git worktree is flagged `tree unchecked` on every row.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT / "tests" / "hastub", ROOT / "tests"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import gate_lock  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()):  # its Results banner
    import harness_headers  # noqa: E402

DIRECTIVE = re.compile(r"^\W*JUDGE-(RUN|PERTURB|NULL|METRIC|TOLERANCE):\s*(.+?)\s*$")
THREAD_FACTOR_MAX = 1.05
DIRECTIONS = ("up", "down", "to_zero", "sign_flip")


def directives(harness: Path) -> dict[str, str]:
    """The JUDGE-* lines of the harness header, lower-cased keys."""
    found: dict[str, str] = {}
    for line in harness_headers.header_lines(harness):
        m = DIRECTIVE.match(line)
        if m and m.group(1).lower() not in found:
            found[m.group(1).lower()] = m.group(2)
    return found


def results(stdout: str) -> dict[str, str]:
    """Every `RESULT name=value` printed, the last one per name winning."""
    out: dict[str, str] = {}
    for line in stdout.splitlines():
        for m in harness_headers.RESULT.finditer(line):
            out[m.group(1)] = m.group(2)
    return out


def number(value: str | None) -> float | None:
    if value is None:
        return None
    text = value.strip().rstrip("%")
    try:
        return float(text)
    except ValueError:
        pass
    if text.count("/") == 1:
        a, b = text.split("/")
        try:
            return float(a) / float(b)
        except (ValueError, ZeroDivisionError):
            return None
    return None


def within(expected: str | None, got: str | None, rule: str | None) -> str:
    """`yes`, `no` or `by-hand`: the got value against the header's expected."""
    if expected is None or got is None or not rule:
        return "by-hand"
    rule = rule.strip().lower()
    e, g = number(expected), number(got)
    if rule.startswith("exact"):
        if e is not None and g is not None:
            return "yes" if e == g else "no"
        return "yes" if expected == got else "no"
    m = re.match(r"^(?:±|\+-|\+/-)\s*([0-9.eE+-]+)\s*(%?)", rule)
    if not m or e is None or g is None:
        return "by-hand"
    try:
        bound = float(m.group(1))
    except ValueError:
        return "by-hand"
    if m.group(2):
        bound = abs(e) * bound / 100.0
    return "yes" if abs(g - e) <= bound else "no"


def moved(base: str | None, perturbed: str | None, direction: str | None) -> str:
    """`moved`, `not-moved`, `wrong-direction` or `by-hand` (judge.md step 2)."""
    if base is None or perturbed is None:
        return "by-hand"
    b, p = number(base), number(perturbed)
    if b is None or p is None:
        return "not-moved" if base == perturbed else "by-hand"
    if b == p:
        return "not-moved"
    ok = {
        "up": p > b,
        "down": p < b,
        "to_zero": p == 0,
        "sign_flip": b != 0 and p != 0 and (b > 0) != (p > 0),
    }.get(direction or "")
    if ok is None:
        return "by-hand"
    return "moved" if ok else "wrong-direction"


class Lease:
    """The gate lease held across the batch; flock is the child's to take."""

    def __init__(self, label: str, lock_dir: Path, seconds: int = gate_lock.LEASE_SECONDS) -> None:
        self.label, self.lock_dir, self.seconds = label, lock_dir, seconds

    def _take(self) -> None:
        gate_lock.take(self.label, lock_dir=self.lock_dir, lease_seconds=self.seconds,
                       owner_pid=os.getpid())

    def __enter__(self) -> Lease:
        self._take()
        return self

    def __exit__(self, *exc: object) -> None:
        with contextlib.suppress(RuntimeError):
            gate_lock.release(self.label, lock_dir=self.lock_dir)

    def renew(self) -> None:
        try:
            gate_lock.renew(self.label, lock_dir=self.lock_dir, lease_seconds=self.seconds,
                            owner_pid=os.getpid())
        except gate_lock.RenewRefused as exc:
            print(f"judge_batch: {exc}; re-queueing", file=sys.stderr)
            gate_lock.release(self.label, lock_dir=self.lock_dir)
            self._take()
        except RuntimeError:  # expired, or stolen after expiry: queue again
            self._take()


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True)


def snapshot(repo: Path) -> dict[str, bytes | None] | None:
    """Every dirty or untracked path with its bytes (None: absent); None off git."""
    p = _git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--no-renames")
    if p.returncode != 0:
        return None
    snap: dict[str, bytes | None] = {}
    for entry in p.stdout.decode("utf-8", "surrogateescape").split("\0"):
        if len(entry) > 3:
            path = entry[3:]
            f = repo / path
            snap[path] = f.read_bytes() if f.is_file() else None
    return snap


def restore(repo: Path, before: dict[str, bytes | None]) -> list[str]:
    """Put the tree back to ``before``; return the paths that had moved."""
    after = snapshot(repo) or {}
    moved = sorted(p for p in set(before) | set(after) if before.get(p, b"") != after.get(p, b""))
    for path in moved:
        f = repo / path
        if path in before:
            if before[path] is None:
                f.unlink(missing_ok=True)
            else:
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes(before[path])
        elif _git(repo, "ls-files", "--error-unmatch", "--", path).returncode == 0:
            _git(repo, "checkout", "--", path)
        else:
            f.unlink(missing_ok=True)
    return moved


def run(cmd: str, *, repo: Path, lease: Lease, timeout: int, arm: str = "run") -> dict:
    lease.renew()
    env = {**os.environ, "HPO_GATE_LOCK_DIR": str(lease.lock_dir),
           "HPO_GATE_LOCK_LABEL": lease.label}
    before = snapshot(repo)
    start = time.monotonic()
    proc = subprocess.Popen(["bash", "-c", cmd], cwd=repo, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            start_new_session=True)
    try:
        out, err = proc.communicate(timeout=timeout)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        rc = "timeout"
    flags = []
    if before is None:
        flags.append("tree unchecked")
    elif moved := restore(repo, before):
        flags.append(f"tree edited by {arm}: {', '.join(moved[:5])}"
                     + (f" (+{len(moved) - 5})" if len(moved) > 5 else "") + "; restored")
    return {"rc": rc, "results": results(out), "stderr": err[-400:], "flags": flags,
            "seconds": round(time.monotonic() - start, 1)}


def _finding(entry: dict) -> dict:
    return entry.get("finding", entry) if isinstance(entry, dict) else {}


def measure(entry: dict, *, repo: Path, lease: Lease, timeout: int) -> dict:
    f = _finding(entry)
    ev = f.get("evidence") or {}
    rel = ev.get("harness_path") or ""
    harness = repo / rel
    row: dict = {"id": f.get("id", "?"), "harness": rel, "flags": []}
    if not rel or not harness.is_file():
        row.update(reproduced="by-hand", perturbation="by-hand", void=None)
        row["flags"].append("harness not found")
        return row
    d = directives(harness)
    d.update({k: v for k, v in (f.get("judge_batch") or {}).items() if v})
    expected = harness_headers.expected_from(harness)
    cmd = d.get("run") or ev.get("command")
    main = run(cmd, repo=repo, lease=lease, timeout=timeout) if cmd else None
    if main:
        row["flags"] += main["flags"]
    printed = main["results"] if main else {}
    metric = d.get("metric") or next(iter(expected), None) or next(
        (k for k in printed if k not in harness_headers.SKIP), None)
    got = printed.get(metric) if metric else None
    row.update(metric=metric, expected=expected.get(metric) if metric else None, got=got,
               rc=main["rc"] if main else None, seconds=main["seconds"] if main else None)
    row["reproduced"] = within(row["expected"], got, d.get("tolerance") or ev.get("tolerance"))
    if main is None:
        row["flags"].append("no command")
    elif main["rc"] != 0:
        row["flags"].append(f"rc={main['rc']}")
    for k, v in printed.items():
        if k not in ("load1", "thread_factor") and metric and k != metric:
            row.setdefault("other", {})[k] = v
    row["held"] = printed.get("held")
    row["load1"] = printed.get("load1")
    if row["load1"] is None:
        row["load1"] = f"{os.getloadavg()[0]:.2f}"
        row["flags"].append("load1 from batch")
    row["thread_factor"] = printed.get("thread_factor")
    tf = number(row["thread_factor"])
    if tf is None:
        row["flags"].append("no thread_factor")
    elif tf > THREAD_FACTOR_MAX:
        row["flags"].append("re-take: thread_factor > 1.05")
    direction = (f.get("perturbation") or {}).get("expected_direction")
    row["direction"] = direction
    if d.get("perturb") and metric:
        pert = run(d["perturb"], repo=repo, lease=lease, timeout=timeout, arm="perturb")
        row["flags"] += [f for f in pert["flags"] if f != "tree unchecked"]
        row["perturbed"] = pert["results"].get(metric)
        row["perturbation"] = moved(got, row["perturbed"], direction)
        if pert["rc"] != 0:
            row["flags"].append(f"perturb rc={pert['rc']}")
    else:
        row["perturbed"], row["perturbation"] = None, "by-hand"
    row["void"] = {"moved": False, "not-moved": True,
                   "wrong-direction": True}.get(row["perturbation"])
    if direction not in DIRECTIONS:
        row["flags"].append(f"direction {direction!r} not machine-checkable")
    if d.get("null") and metric:
        null = run(d["null"], repo=repo, lease=lease, timeout=timeout, arm="null")
        row["flags"] += [f for f in null["flags"] if f != "tree unchecked"]
        row["null_value"] = null["results"].get(metric)
        if null["rc"] != 0:
            row["flags"].append(f"null rc={null['rc']}")
    else:
        row["null_value"] = "by-hand"
    return row


def run_batch(entries: list, *, repo: Path, lock_dir: Path = gate_lock.DEFAULT_LOCK_DIR,
              label: str, timeout: int = 1800) -> list[dict]:
    """Every finding measured serially under one lease, in input order."""
    rows = []
    # A lease longer than one command, so a harness that holds the box for its
    # whole timeout is not stolen from mid-run.
    with Lease(label, lock_dir, max(gate_lock.LEASE_SECONDS, timeout + 300)) as lease:
        for entry in entries:
            rows.append(measure(entry, repo=Path(repo), lease=lease, timeout=timeout))
    return rows


COLUMNS = ("id", "metric", "expected", "got", "reproduced", "direction", "perturbed",
           "perturbation", "void", "null_value", "load1", "thread_factor", "flags")


def render_table(rows: list[dict]) -> str:
    def cell(v: object) -> str:
        if isinstance(v, list):
            v = "; ".join(v)
        return "" if v is None else str(v).replace("|", "\\|")
    lines = ["| " + " | ".join(COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
    lines += ["| " + " | ".join(cell(r.get(c)) for c in COLUMNS) + " |" for r in rows]
    return "\n".join(lines) + "\n"


def _shard(entries: list, spec: str | None) -> list:
    if not spec:
        return entries
    k, n = (int(x) for x in spec.split("/"))
    if not 1 <= k <= n:
        raise SystemExit(f"--shard {spec}: want k/n with 1 <= k <= n")
    ordered = sorted(entries, key=lambda e: str(_finding(e).get("id", "")))
    return [e for i, e in enumerate(ordered) if i % n == k - 1]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--repo", type=Path, default=Path.cwd())
    p.add_argument("--label", required=True)
    p.add_argument("--lock-dir", type=Path, default=gate_lock.DEFAULT_LOCK_DIR)
    p.add_argument("--timeout", type=int, default=1800, help="seconds per command")
    p.add_argument("--shard", help="k/n: this runner's share, for a second quiet box")
    p.add_argument("--out-json", type=Path)
    p.add_argument("--out-md", type=Path)
    a = p.parse_args(argv)
    entries = _shard(json.loads(a.input.read_text()), a.shard)
    rows = run_batch(entries, repo=a.repo, lock_dir=a.lock_dir, label=a.label,
                     timeout=a.timeout)
    table = render_table(rows)
    if a.out_json:
        a.out_json.write_text(json.dumps(rows, indent=1) + "\n")
    if a.out_md:
        a.out_md.write_text(table)
    sys.stdout.write(table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
