#!/usr/bin/env python3
"""The CI ratchet (round-9, tvofi's request): CI cost and code health may only improve.

One-way budgets, in the shape tests/structure.py established: every metric is
DERIVED from a measurement made by this run (never carried by hand), recorded
in tests/ci_budgets.json, and any metric that GREW fails the run. A deliberate
re-record needs --record "<reason>", and the reason belongs in the commit
message (CLAUDE.md rule 2). The inputs are produced by the CI jobs themselves
-- the emitter lines the gate and its instruments already write (run.sh's
scope decision, derive_closures.sh's rec(), coverage_tree.sh's measure()) --
because a ratchet whose input is typed by a human is not a ratchet
(qntm.org/ratchets; Betterer and eslint-seatbelt freeze the same
tool-produced baseline).

THE METRICS, each an answer to a named cost:

  archscore.<m>   tools/audit/archscore's score vector, measured on this
                  tree -- ratcheting THE architecture score's own number,
                  not a second one. Deterministic static counts, tolerance 0.
  script_runs_per_push    instrumented heavy-script executions in a push
                  run (the closures re-derive plus the coverage stage): the
                  "number of script re-runs" the round-9 consolidation
                  pre-study measured (3.8 per merge average, 7 worst case).
                  A `reused` coverage row executes nothing and is not
                  counted. Recorded at the every-script-measured-once count
                  (the closures lane's full plan less the composed script it
                  consumes, plus the coverage `fast` stage), so a push that
                  measures any script twice in one instrument grows it.
  script_runs_full_case_pr   the same count on a full-case pull-request run
                  (every script measured and re-derived once). Scoping's
                  ratchet: what a full-case PR costs may only shrink.
  critical_path_minutes   median wall minutes of the last completed push
                  Tests runs (the GitHub API run list, fetched by the job).
                  A NOISY metric: recorded at the window's p75 for headroom,
                  because shared runners vary far more than the medians do
                  (Bencher documents >30 % variance on shared runners); the
                  ratchet refuses beyond the headroom, not beyond the median.

WHAT IS DELIBERATELY NOT HERE, so nobody re-adds it wrongly:

  * a scoped-FRACTION ratchet. Measured before refusing it: 33 of the last
    60 merges are full-case BY DESIGN (gate files, closures.json, unscoped
    docs each force MODE: FULL -- CLAUDE.md rule 1's push-forces-full is the
    same defensive pattern), so a full-share ratchet would refuse legitimate
    merges the day two gate-file PRs land in one window. The flapping-gate
    and perverse-incentive pitfalls every ratchet source warns about. The
    per-event absolute counts above are the honest form.
  * complexity. tests/structure_budgets.json already ratchets max_cc,
    functions_cc_over_* and the rest, one-way; a second file with the same
    metric would be a duplicate owner. Pylint --fail-under, xenon and
    pitest/Stryker thresholds are the same pattern with one owner each.

Usage (the ci-ratchet job; stdlib only besides the archscore import):

    python3 tests/ci_ratchet.py --metrics-dir DIR [--runs-json FILE]
    python3 tests/ci_ratchet.py --metrics-dir DIR --runs-json FILE \
        --record "reason"
    python3 tests/ci_ratchet.py --gather --metrics-dir DIR   # the job's fetch
    python3 tests/ci_ratchet.py --self-test                  # offline, no network

--metrics-dir holds the ci-metrics artifacts of this run and the recent
window, flat: lines of
  <lane>\t<script>\t<full|scoped|reused>\t<rc>\t<seconds>\t<event>\t<run id>
(the event and run id come from the runner environment, so a window's three
lane artifacts of one run group as one run), plus the fast lane's single
<fast>\tmode\t<full|scoped>\t<n_run>\t<n_skip>\t<event>\t<run id>.
--runs-json is the GitHub API workflow-runs listing for critical path.
--record re-records every metric from what was just derived, refusing without
a reason.
"""
from __future__ import annotations

import io
import json
import math
import os
import subprocess
import sys
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUDGETS = ROOT / "tests" / "ci_budgets.json"
METADATA_KEYS = {"recorded_at", "reason"}

LANES = ("closures", "coverage")

# --- the recent-window fetch (the ci-ratchet job's gather step) --------------
#
# This lane's input is two API calls: the artifacts list -- the heaviest read
# the workflow makes -- and up to 45 artifact zips. Both DECISIONS live here,
# not in a workflow heredoc, because a decision inside a heredoc cannot be
# tested offline (decision 0013) and this one has already failed in
# production: the list call returned a body gh's jq engine could not parse
# ("unexpected end of JSON input"), `|| true` swallowed the exit code, and the
# step died ten seconds later on `json.load` of a 0-byte file with a traceback
# naming nothing (CI job 118878630676, 2026-10-20). An EMPTY OR PARTIAL BODY IS
# A FAILED FETCH, NEVER AN EMPTY WINDOW.
ARTIFACTS_URL = "repos/{repo}/actions/artifacts?per_page=100"
WINDOW_LIMIT = 45          # the list the step has always downloaded from
FETCH_ATTEMPTS = 4         # the list call's attempts, in total
FETCH_DELAY = 2.0          # seconds before the second attempt; doubles
EXPIRED_HTTP = ("404", "410")


def _refusal(text: str) -> SystemExit:
    """The module's refusal shape: one named line, never a traceback the
    reader has to reverse-engineer."""
    return SystemExit(f"ci-ratchet: {text}")


def _run_field(art: dict):
    """The artifact's run association: .workflow_run.id with a .run_id
    fallback. The list API stopped returning .run_id (null for every
    artifact, 2026-10-12), which once left the old filter selecting on null;
    both forms stay null-safe because .workflow_run itself may be null."""
    run = art.get("workflow_run") or {}
    if not isinstance(run, dict):
        run = {}
    rid = run.get("id")
    return rid if rid is not None else art.get("run_id")


def _number(value):
    """An int run id, else None: a non-numeric field stays in the window
    rather than being silently matched to the current run."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def window_entries(payload, run_id, limit: int = WINDOW_LIMIT) -> list[dict]:
    """The recent ci-metrics window from one artifacts-list response.

    An empty or truncated body is a FAILED FETCH, never an empty window: the
    API call can return rc 1 or a partial body on a shared runner's network,
    and a zero read as a window grades on nothing while looking like a pass.
    Every refusal here therefore names the fetch.
    """
    body = payload or ""
    if not body.strip():
        raise _refusal(f"the artifacts fetch returned 0 bytes for run "
                       f"{run_id}; refusing to read that as an empty window")
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise _refusal(f"the artifacts fetch returned {len(body)} bytes of "
                       f"incomplete JSON ({exc}); refusing to read that as "
                       "an empty window") from None
    if not isinstance(data, dict) or not isinstance(data.get("artifacts"), list):
        raise _refusal(f"the artifacts fetch returned {len(body)} bytes with "
                       "no artifacts list; refusing to read that as an empty "
                       "window")
    me = _number(run_id)
    rows = []
    for art in data["artifacts"]:
        if not isinstance(art, dict):
            continue
        name = art.get("name")
        if not isinstance(name, str) or not name.startswith("ci-metrics-"):
            continue
        if art.get("expired") is not False:
            continue
        run = _run_field(art)
        if me is not None and _number(0 if run is None else run) == me:
            continue
        rows.append({"id": art.get("id"), "run": run, "name": name,
                     "at": art.get("created_at")})
    # Newest first, then one artifact per (run, name): the newest, which is
    # the copy the step always downloaded.
    rows.sort(key=lambda r: (r["at"] is None, r["at"] or ""), reverse=True)
    seen, unique = set(), []
    for row in rows:
        key = (row["run"], row["name"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    # jq's unique_by sorts by its key before keeping the first of each group,
    # so the list the step received was ordered by (run, name) ascending; the
    # --limit cut below is taken in that order.
    unique.sort(key=lambda r: (r["run"] is not None, r["run"] or 0, r["name"]))
    return unique[:limit]


def fetch_window(repo, run_id, *, runner=None, sleep=None,
                 attempts: int = FETCH_ATTEMPTS,
                 delay: float = FETCH_DELAY) -> list[dict]:
    """The recent window, retried, or a refusal that names the fetch.

    A retry with a bounded backoff turns a transient refusal into a green run
    and a sustained one into a red JOB whose log says why. When the attempts
    are spent the refusal carries gh's exit code, the byte count and gh's own
    stderr, so the log says what failed instead of a JSON traceback naming
    nothing."""
    run = runner or subprocess.run
    wait = sleep or time.sleep
    url = ARTIFACTS_URL.format(repo=repo)
    failure = "no attempt ran"
    for attempt in range(1, attempts + 1):
        try:
            proc = run(["gh", "api", url], capture_output=True, text=True)
        except OSError as exc:
            failure = f"gh could not be run ({exc})"
            proc = None
        if proc is not None:
            body = proc.stdout or ""
            if proc.returncode != 0:
                failure = (f"gh exited {proc.returncode} after {len(body)} "
                           f"byte(s): {(proc.stderr or '').strip()[:400]}")
            elif not body.strip():
                failure = "gh exited 0 and returned 0 bytes"
            else:
                try:
                    return window_entries(body, run_id)
                except SystemExit as exc:
                    failure = str(exc).removeprefix("ci-ratchet: ")
        print(f"ci-ratchet: artifacts fetch attempt {attempt}/{attempts} "
              f"failed: {failure}", file=sys.stderr)
        if attempt < attempts:
            wait(delay * 2 ** (attempt - 1))
    raise _refusal(f"the artifacts fetch failed after {attempts} attempt(s): "
                   f"{failure}. This is a refusal, not an empty window: the "
                   "recent-window metrics are unknown, so the ratchet cannot "
                   "grade")


def download_artifacts(entries, out_dir, repo, *, runner=None) -> list[dict]:
    """Write each window artifact's .tsv files into out_dir, returning the
    artifacts skipped as expired.

    An artifact that expired between the listing and the download (HTTP
    404/410) is skipped and said so: the window is listed first and up to 45
    zips are fetched minutes later, and one expired artifact must not discard
    the other 44. Any other failure refuses by name."""
    run = runner or subprocess.run
    out = Path(out_dir)
    skipped = []
    for art in entries:
        url = f"repos/{repo}/actions/artifacts/{art['id']}/zip"
        proc = run(["gh", "api", url], capture_output=True)
        if proc.returncode != 0:
            err = (proc.stderr or b"").decode("utf-8", "replace").strip()
            if any(f"HTTP {code}" in err for code in EXPIRED_HTTP):
                first = err.splitlines()[0][:200] if err else "no stderr"
                print(f"ci-ratchet: skipping expired artifact {art['id']} "
                      f"({art['name']}): {first}")
                skipped.append(art)
                continue
            raise _refusal(f"downloading artifact {art['id']} ({art['name']}) "
                           f"failed: gh exited {proc.returncode}: {err[:400]}")
        with zipfile.ZipFile(io.BytesIO(proc.stdout)) as zf:
            for name in zf.namelist():
                if name.endswith(".tsv"):
                    (out / f"w{art['id']}-{Path(name).name}").write_bytes(
                        zf.read(name))
    return skipped


def gather(metrics_dir, *, repo=None, run_id=None, runner=None,
           sleep=None) -> dict:
    """The ci-ratchet job's gather step: this run's lane artifacts are already
    in metrics_dir; add the recent window's and return the counts printed, so
    a caller (and --self-test) can assert them."""
    repo = repo or os.environ.get("GITHUB_REPOSITORY")
    run_id = run_id or os.environ.get("GITHUB_RUN_ID")
    if not repo or not run_id:
        raise _refusal("gather needs GITHUB_REPOSITORY and GITHUB_RUN_ID")
    out = Path(metrics_dir)
    out.mkdir(parents=True, exist_ok=True)
    entries = fetch_window(repo, run_id, runner=runner, sleep=sleep)
    print(f"window: {len(entries)} ci-metrics artifact(s)")
    skipped = download_artifacts(entries, out, repo, runner=runner)
    if skipped:
        print(f"ci-ratchet: {len(skipped)} of {len(entries)} artifact(s) "
              "expired before download and were skipped")
    return {"window": len(entries), "skipped": len(skipped),
            "downloaded": len(entries) - len(skipped)}


def _finite_number(value) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def budget_problems(table: dict) -> list[str]:
    """Refuse a table this ratchet cannot honestly grade."""
    problems = []
    if not isinstance(table, dict):
        return ["the table is not an object"]
    if "recorded_at" not in table:
        problems.append("no recorded_at -- a ratchet row must name the tree "
                        "it was measured on")
    counts = ("script_runs_per_push", "script_runs_full_case_pr")
    for key, value in table.items():
        if key in METADATA_KEYS:
            continue
        if not _finite_number(value):
            problems.append(f"{key}={value!r} is not a finite number")
            continue
        if key.startswith("archscore."):
            if not isinstance(value, int) or value < 0:
                problems.append(f"{key}={value!r} is not a non-negative "
                                "integer count")
        elif key in counts:
            if not isinstance(value, int) or value < 0:
                problems.append(f"{key}={value!r} is not a non-negative "
                                "integer count")
        elif key == "critical_path_minutes":
            if not 0 < value <= 600:
                problems.append(f"{key}={value!r} is outside 0..600 minutes")
        else:
            problems.append(f"{key} is not a metric this ratchet knows")
    return problems


def archscore_metrics(only: set[str] | None = None) -> dict[str, int]:
    """The score vector as ratchet keys; ``only`` is vector.measure's job filter (the census arm
    of tools/policy/field_coverage.mjs runs the card job alone)."""
    sys.path.insert(0, str(ROOT / "tools" / "audit"))
    from archscore import vector  # noqa: E402
    return {f"archscore.{k}": v for k, v in vector.measure(ROOT, only).items()}


def file_lane(path: Path) -> str:
    """The lane an artifact file is named for: each job writes its own
    ci-metrics-<lane>.tsv, and the window keeps that basename behind a
    w<artifact id>- prefix. A file naming no lane is refused, not guessed."""
    for lane in ("fast", *LANES):
        if path.name.endswith(f"ci-metrics-{lane}.tsv"):
            return lane
    raise SystemExit(f"ci-ratchet: {path.name} names no lane "
                     "(ci-metrics-<lane>.tsv); its rows cannot be "
                     "attributed (fail closed)")


def read_metrics(metrics_dir: Path) -> dict[tuple[str, str], list[dict]]:
    """Every emitter line, grouped into runs by the (event, run id) every
    line carries: one run's three lane artifacts land as three files, and
    the per-run counts must not read them as three runs.

    A row counts only from its own lane's file. A row of another lane inside
    a file was written by a child of that lane's instrument that inherited
    HPO_CI_METRICS -- closure.py's selftest driving derive_closures.sh under
    a stub put fixture `closures` rows in ci-metrics-fast.tsv, and a nested
    run.sh raced them to 69 on push run 38639862216. The emitters no longer
    export the variable; this keeps the artifacts already in the window, and
    any emitter added later, from being graded as cost."""
    runs: dict[tuple[str, str], list[dict]] = {}
    foreign = 0
    for f in sorted(metrics_dir.rglob("*.tsv")):
        lane = file_lane(f)
        for line in f.read_text().splitlines():
            parts = line.split("\t")
            if len(parts) < 7:
                continue
            if parts[0] != lane:
                foreign += 1
                continue
            runs.setdefault((parts[5], parts[6]), []).append(
                {"lane": parts[0], "name": parts[1], "class": parts[2]})
    if foreign:
        print(f"ci-ratchet: not counted: {foreign} row(s) carried by another "
              "lane's artifact (a child that inherited HPO_CI_METRICS)",
              file=sys.stderr)
    return runs


def script_runs(run: list[dict]) -> int:
    """Instrumented script EXECUTIONS in one run. A `reused` coverage row is a
    copy of the base's per-script data, not an execution -- it runs nothing
    -- so it is no script run (R10-CI-LAYOUT PR 0). Counting it graded push
    run 39213675232's 19 copies as 19 runs, 73 against a budget of 68."""
    return sum(1 for r in run if r["lane"] in LANES and r["class"] != "reused")


def critical_path_minutes(runs_json: Path) -> float:
    """Median wall minutes over the window's COMPLETED push Tests runs."""
    runs = json.loads(runs_json.read_text())["workflow_runs"]
    minutes = []
    for r in runs:
        if r.get("name") != "Tests" or r.get("status") != "completed":
            continue
        start = datetime.fromisoformat(
            r["created_at"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(
            r["updated_at"].replace("Z", "+00:00"))
        minutes.append((end - start).total_seconds() / 60)
    if not minutes:
        raise SystemExit("ci-ratchet: no completed push Tests runs in "
                         "runs.json; cannot derive critical_path_minutes "
                         "(fail closed)")
    minutes.sort()
    n = len(minutes)
    mid = n // 2
    return minutes[mid] if n % 2 else (minutes[mid - 1] + minutes[mid]) / 2


def derive(metrics_dir: Path, runs_json: Path | None) -> dict[str, float]:
    derived: dict[str, float] = dict(archscore_metrics())
    events = read_metrics(metrics_dir)
    push_runs = [rows for (event, _), rows in events.items()
                 if event == "push"]
    if not push_runs:
        raise SystemExit("ci-ratchet: no push metrics in "
                         f"{metrics_dir}; the emitters the gate and its "
                         "instruments carry did not run (fail closed)")
    # A push event is one run; a window that ever carries more is graded on
    # its most expensive one -- the waste direction is the max.
    derived["script_runs_per_push"] = max(script_runs(r) for r in push_runs)
    # The full-case PR arm: the most expensive pull-request run in the
    # window whose own fast lane reported MODE: FULL. What a full-case PR
    # costs may only shrink -- that is scoping's ratchet.
    full_pr = [script_runs(rows) for (event, _), rows in events.items()
               if event == "pull_request"
               and any(x["lane"] == "fast" and x["class"] == "full"
                       for x in rows)]
    if full_pr:
        derived["script_runs_full_case_pr"] = max(full_pr)
    if runs_json is not None:
        derived["critical_path_minutes"] = critical_path_minutes(runs_json)
    return derived


def compare(budgets: dict, derived: dict) -> tuple[list[str], int]:
    grew = []
    lines = []
    for key in sorted(set(budgets) - METADATA_KEYS):
        budget = budgets[key]
        if key not in derived:
            lines.append(f"  ?     {key}: not derived this run "
                         "(missing input); not graded")
            continue
        cur = derived[key]
        mark = "ok" if cur <= budget else "GREW"
        if cur > budget:
            grew.append(key)
        lines.append(f"  {mark:<5} {key}: {cur} (budget {budget})")
    for key in sorted(set(derived) - set(budgets)):
        grew.append(key)
        lines.append(f"  GREW  {key}: {derived[key]} (no budget row; a new "
                     "metric starts unrecorded -- record it or remove it)")
    return lines, len(grew)


def _art(aid, name, run, at, *, expired=False, fallback_only=False):
    """One artifact as the list API shapes it; `fallback_only` leaves
    .workflow_run null so only the .run_id fallback can attribute it."""
    return {"id": aid, "name": name, "created_at": at, "expired": expired,
            "workflow_run": None if fallback_only else ({"id": run}
                                                        if run is not None
                                                        else None),
            "run_id": run}


def _zip_of(name: str, text: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(name, text)
    return buf.getvalue()


def self_test() -> int:
    """Drive every refusal and the selection offline: no network, no sleep."""
    passed = failed = 0

    def ck(name: str, ok: bool, detail: str = "") -> None:
        nonlocal passed, failed
        passed, failed = passed + ok, failed + (not ok)
        print(f"  {'ok  ' if ok else 'FAIL'} {name}{'' if ok else ' -- ' + detail}")

    def refused(fn):
        try:
            fn()
        except SystemExit as exc:
            return str(exc)
        return ""

    def safe(fn):
        """(value, "") or (None, refusal). Every arm goes through this, so a
        mutant that crashes REDDENS its own named check instead of aborting
        the self-test -- a crash reads like a proof and is not one."""
        try:
            return fn(), ""
        except SystemExit as exc:
            return None, str(exc)

    # The failing-test-first arm: an empty body must redden naming the fetch
    # AND the run whose fetch it was. The run is what the explicit 0-byte
    # guard adds over the JSON catch -- the two causes (nothing arrived vs a
    # body cut short) have different diagnoses, so the arm separates them.
    got, msg = safe(lambda: window_entries("", "77"))
    ck("an empty response refuses, naming the 0-byte fetch and its run "
       "(not an empty window)",
       got is None and "artifacts fetch" in msg and "0 bytes" in msg
       and "run 77" in msg, msg or f"returned {got!r}")
    for label, body in (("whitespace-only", "  \n"),
                        ("truncated", '{"artifacts": ['),
                        ("no artifacts list", '{"total_count": 3}')):
        msg = refused(lambda b=body: window_entries(b, "77"))
        ck(f"a {label} artifacts response refuses (not an empty window)",
           "artifacts fetch" in msg and "empty window" in msg, msg or "no refusal")

    # --- the selection, and its null control: a good body still selects ----
    good = json.dumps({"artifacts": [
        _art(1, "ci-metrics-fast", 9, "2026-10-20T10:00:00Z"),
        _art(2, "ci-metrics-fast", 8, "2026-10-20T11:00:00Z"),
        _art(3, "ci-metrics-fast", 8, "2026-10-20T12:00:00Z"),
        _art(4, "other-name", 8, "2026-10-20T13:00:00Z"),
        _art(5, "ci-metrics-fast", 8, "2026-10-20T14:00:00Z", expired=True),
        _art(6, "ci-metrics-fast", 77, "2026-10-20T15:00:00Z"),
        _art(7, "ci-metrics-closures", 7, "2026-10-20T09:00:00Z",
             fallback_only=True),
    ]})
    got, msg = safe(lambda: window_entries(good, "77"))
    ids = [e["id"] for e in got or []]
    ck("a good response still yields the window (the null control)",
       got is not None and ids == [7, 3, 1], msg or f"got {ids}, want [7, 3, 1]")
    ck("a duplicate (run, name) keeps the newest copy",
       2 not in ids and 3 in ids, f"got {ids}")
    ck("an expired artifact, another name and THIS run are all out",
       {4, 5, 6}.isdisjoint(ids), f"got {ids}")
    ck("the .run_id fallback attributes a null .workflow_run",
       bool(got) and got[0]["run"] == 7, f"run={got[0]['run'] if got else None}")
    cut, msg = safe(lambda: window_entries(good, "77", limit=2))
    ck("the cut is taken in (run, name) order, as jq's unique_by emitted it",
       [e["id"] for e in cut or []] == [7, 3], msg or f"got {cut}")

    # --- the retry ----------------------------------------------------------
    def stub(sequence):
        calls, slept = [], []

        def run(argv, **_kw):
            calls.append(argv)
            rc, out, err = sequence[min(len(calls), len(sequence)) - 1]
            return subprocess.CompletedProcess(argv, rc, out, err)
        return run, calls, slept

    runner, calls, slept = stub([(1, "", "gh: Server Error (HTTP 502)"),
                                 (0, good, "")])
    entries, msg = safe(lambda: fetch_window("o/r", "77", runner=runner,
                                             sleep=slept.append))
    ck("a failed list call is retried and the retry's window is used",
       [e["id"] for e in entries or []] == [7, 3, 1] and len(calls) == 2
       and slept == [2.0], msg or f"calls={len(calls)} slept={slept}")
    runner, calls, slept = stub([(0, "", ""), (0, good, "")])
    entries, msg = safe(lambda: fetch_window("o/r", "77", runner=runner,
                                             sleep=slept.append))
    ck("an rc 0 with 0 bytes is retried too, not read as a window",
       len(entries or []) == 3 and len(calls) == 2,
       msg or f"calls={len(calls)}")
    runner, calls, slept = stub([(1, "", "gh: HTTP 500"), (1, "", "gh: HTTP 500")])
    msg = refused(lambda: fetch_window("o/r", "77", runner=runner,
                                       sleep=slept.append, attempts=3))
    ck("spent attempts refuse by name (exit code, attempts), no traceback",
       "after 3 attempt(s)" in msg and "HTTP 500" in msg and slept == [2.0, 4.0],
       msg or "no refusal")

    # --- the expired-artifact download --------------------------------------
    zips = {11: _zip_of("ci-metrics-fast.tsv", "fast\tmode\tfull\t0\t0\tpush\t1\n"),
            12: _zip_of("ci-metrics-closures.tsv", "closures\ta.py\tfull\t0\t1\tpush\t1\n"),
            14: _zip_of("ci-metrics-coverage.tsv", "coverage\tb.py\tfull\t0\t1\tpush\t1\n")}

    def dl_run(argv, **_kw):
        aid = int(argv[-1].rstrip("/zip").rsplit("/", 1)[-1])
        if aid == 12:
            return subprocess.CompletedProcess(argv, 1, b"",
                                               b"gh: Artifact has expired (HTTP 404)")
        if aid == 13:
            return subprocess.CompletedProcess(argv, 1, b"", b"gh: HTTP 500")
        return subprocess.CompletedProcess(argv, 0, zips[aid], b"")

    with tempfile.TemporaryDirectory() as td:
        skipped, msg = safe(lambda: download_artifacts(
            [{"id": 11, "name": "ci-metrics-fast"},
             {"id": 12, "name": "ci-metrics-closures"},
             {"id": 14, "name": "ci-metrics-coverage"}],
            td, "o/r", runner=dl_run))
        names = sorted(p.name for p in Path(td).iterdir())
        ck("an expired artifact is skipped and the rest of the window survives",
           [a["id"] for a in skipped or []] == [12] and names == [
               "w11-ci-metrics-fast.tsv", "w14-ci-metrics-coverage.tsv"],
           msg or f"skipped={[a['id'] for a in skipped or []]} files={names}")
        msg = refused(lambda: download_artifacts(
            [{"id": 13, "name": "ci-metrics-coverage"}], td, "o/r",
            runner=lambda argv, **_kw: subprocess.CompletedProcess(
                argv, 3, b"", b"gh: HTTP 500")))
        ck("a non-expiry download failure still refuses by name",
           "artifact 13" in msg and "exited 3" in msg, msg or "no refusal")

    print(f"ci-ratchet self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ["--self-test"]:
        return self_test()
    if "--gather" in argv:
        argv.remove("--gather")
        metrics_dir = None
        if "--metrics-dir" in argv:
            i = argv.index("--metrics-dir")
            metrics_dir = argv[i + 1]
            del argv[i:i + 2]
        if metrics_dir is None or argv:
            print("ci-ratchet: --gather needs exactly --metrics-dir DIR",
                  file=sys.stderr)
            return 2
        gather(metrics_dir)
        return 0
    record_reason = None
    if "--record" in argv:
        i = argv.index("--record")
        if i + 1 >= len(argv):
            print("ci-ratchet: --record needs a reason", file=sys.stderr)
            return 2
        record_reason = argv[i + 1]
        del argv[i:i + 2]
    metrics_dir = runs_json = None
    args = list(argv)
    for flag in ("--metrics-dir", "--runs-json"):
        if flag in args:
            i = args.index(flag)
            value = args[i + 1]
            if flag == "--metrics-dir":
                metrics_dir = Path(value)
            else:
                runs_json = Path(value)
            del args[i:i + 2]
    if metrics_dir is None or args:
        print(__doc__)
        return 2
    budgets = json.loads(BUDGETS.read_text())
    problems = budget_problems(budgets)
    if problems:
        for p in problems:
            print(f"ci-ratchet: refusing the budget table: {p}",
                  file=sys.stderr)
        return 1
    derived = derive(metrics_dir, runs_json)
    if record_reason is not None:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True,
                              check=True).stdout.strip()
        table = {**{k: v for k, v in derived.items()},
                 "recorded_at": head, "reason": record_reason}
        problems = budget_problems(table)
        if problems:
            for p in problems:
                print(f"ci-ratchet: refusing to record: {p}", file=sys.stderr)
            return 1
        BUDGETS.write_text(json.dumps(table, indent=1, sort_keys=True) + "\n")
        print(f"ci-ratchet: recorded {len(derived)} metric(s) at {head[:12]} "
              f"-- {record_reason}")
        return 0
    lines, grew = compare(budgets, derived)
    print("CI ratchet:")
    print("\n".join(lines))
    if grew:
        print(f"ci-ratchet: {grew} metric(s) grew; pay the debt or re-record "
              "deliberately with --record \"<reason>\" (CLAUDE.md rule 2)",
              file=sys.stderr)
        return 1
    print("ci-ratchet: every metric at or under its budget")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
