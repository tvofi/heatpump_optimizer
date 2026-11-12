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
  critical_path_minutes   WORK minutes of the newest PUSH_WINDOW (16)
                  completed push runs of the tests workflow (the GitHub API
                  run list with each run's jobs, fetched by --gather-runs),
                  priced off host speed (window_work_minutes): each heavy
                  `tests / *` job runs tests/host_probe.py, fixed work, as a
                  step of its own, and is priced at the median of its work
                  over its own runner's probe, in reference-host seconds
                  (job_price; R10-HOTFIX-CI-CRITPATH-4); a job without a
                  probe step at its fastest run in the window. The prices
                  are summed along the longest path through every need the
                  window observed, each runner queue removed -- see
                  run_minutes. Never the wall: the wall reads the account's
                  runner contention (59.7 wall on 32.1 work, CI job
                  121295715608). Never one run's work, and never a job's
                  fastest draw once it is probed: hosted runners differ
                  ~1.9x on the same work and the fleet's mix moves, so the
                  median of runs read which hosts the lanes drew
                  (8f286293b, R10-HOTFIX-CI-CRITPATH-3) and the fastest
                  draw read whether the window still held a fast host
                  (8e90d8144, R10-HOTFIX-CI-CRITPATH-4). Recorded at the
                  largest value any PUSH_WINDOW consecutive runs of a wider
                  window read (`--gather-runs FILE --window 40`), the
                  statistic's own window-to-window spread.
                  REPORT-ONLY (R10-CI-SLIM card C2, owner ruling 2026-11-05):
                  printed beside its recorded reference on every push and
                  never graded, so its growth never fails the job. Four
                  redefinitions (#2839..#3228) did not stop it reading the
                  hosted runners' draw; its band row is deleted with it. The
                  recorded value stays the reference orchestrator_tick.py's
                  ETA check reads.

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
    python3 tests/ci_ratchet.py --gather-runs FILE [--window N]  # its runs.json
    python3 tests/ci_ratchet.py --self-test                  # offline, no network

--metrics-dir holds the ci-metrics artifacts of this run and the recent
window, flat: lines of
  <lane>\t<script>\t<full|scoped|reused>\t<rc>\t<seconds>\t<event>\t<run id>
(the event and run id come from the runner environment, so a window's three
lane artifacts of one run group as one run), plus the fast lane's single
<fast>\tmode\t<full|scoped>\t<n_run>\t<n_skip>\t<event>\t<run id>.
--runs-json is the GitHub API workflow-runs listing for critical path, each
run carrying its own `jobs` (what --gather-runs writes).
--record re-records every metric from what was just derived, refusing without
a reason.
"""
from __future__ import annotations

import io
import json
import math
import os
import statistics
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
# Rows printed against their recorded reference and never graded (R10-CI-SLIM
# card C2): a growth here is reported, never a failure. Every other row stays
# graded at zero tolerance.
REPORT_ONLY = frozenset({"critical_path_minutes"})

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
#
# The list is read per lane by name, never repo-wide: from d5dc3e26 the
# unfiltered listing timed out server-side (~10 s, 0 bytes, "unexpected end
# of JSON input") on every attempt of every push run (CI job 120763639214),
# while the name-filtered listing answered in under a second. The window is
# therefore what tests.yml's gather step has always said it is -- the newest
# copy per lane per run of each lane's newest WINDOW_PER_LANE runs that are not
# this one -- rather than whatever ci-metrics artifacts the newest 100 of ANY
# name happened to hold. A lane listing that carries another name means the
# server ignored the filter; that refuses like any other failed fetch.
ARTIFACTS_URL = "repos/{repo}/actions/artifacts?name=ci-metrics-{lane}&per_page={n}"
WINDOW_LIMIT = 45          # the list the step has always downloaded from
WINDOW_LANES = ("fast", *LANES)
WINDOW_PER_LANE = WINDOW_LIMIT // len(WINDOW_LANES)    # runs kept per lane
# The listing page per lane: twice the runs kept, so this run's own copy and a
# re-run's second copy of one (run, lane) never shorten the window.
WINDOW_FETCH_PER_LANE = 2 * WINDOW_PER_LANE
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


def _listing(body, run_id) -> list:
    """One artifacts-list response's artifacts, or a refusal naming the fetch.

    An empty or truncated body is a FAILED FETCH, never an empty window: the
    API call can return rc 1 or a partial body on a shared runner's network,
    and a zero read as a window grades on nothing while looking like a pass.
    """
    body = body or ""
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
    return data["artifacts"]


def _lane_listing(body, run_id, lane: str) -> list:
    """One lane's name-filtered listing, refused if it carries another name:
    the server ignoring `name=` would hand back the newest artifacts of every
    name, a short window that would grade as if whole."""
    want = f"ci-metrics-{lane}"
    artifacts = _listing(body, run_id)
    stray = sorted({str(a.get("name")) for a in artifacts
                    if isinstance(a, dict) and a.get("name") != want})
    if stray:
        raise _refusal(f"the {want} artifacts fetch carried other names "
                       f"({', '.join(stray[:5])}); the name filter was not "
                       "applied, refusing to read that as the lane's window")
    return artifacts


def window_entries(payloads, run_id, limit: int = WINDOW_LIMIT,
                   per_name: int | None = None) -> list[dict]:
    """The recent ci-metrics window from one artifacts-list response, or from
    several (one per lane); any one that is not a whole listing refuses.
    `per_name` keeps each artifact name's newest that many runs, so a cut
    never drops one lane's newest runs to keep another's oldest."""
    if payloads is None or isinstance(payloads, str):
        payloads = [payloads]
    artifacts = [a for body in payloads for a in _listing(body, run_id)]
    me = _number(run_id)
    rows = []
    for art in artifacts:
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
    # the copy the step always downloaded. An artifact with no created_at
    # sorts LAST, as jq's `sort_by(.at) | reverse` put it (null sorts first
    # ascending, so it lands last once reversed).
    rows.sort(key=lambda r: r["at"] or "", reverse=True)
    seen, unique = set(), []
    for row in rows:
        key = (row["run"], row["name"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    if per_name is not None:
        # `unique` is newest first here, so each name keeps its newest runs.
        kept: dict[str, int] = {}
        capped = []
        for row in unique:
            if kept.get(row["name"], 0) < per_name:
                kept[row["name"]] = kept.get(row["name"], 0) + 1
                capped.append(row)
        unique = capped
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
    bodies = []
    for lane in WINDOW_LANES:
        url = ARTIFACTS_URL.format(repo=repo, lane=lane,
                                   n=WINDOW_FETCH_PER_LANE)
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
                        _lane_listing(body, run_id, lane)
                        bodies.append(body)
                        break
                    except SystemExit as exc:
                        failure = str(exc).removeprefix("ci-ratchet: ")
            print(f"ci-ratchet: ci-metrics-{lane} artifacts fetch attempt "
                  f"{attempt}/{attempts} failed: {failure}", file=sys.stderr)
            if attempt < attempts:
                wait(delay * 2 ** (attempt - 1))
        else:
            raise _refusal(f"the ci-metrics-{lane} artifacts fetch failed after "
                           f"{attempts} attempt(s): {failure}. This is a "
                           "refusal, not an empty window: the recent-window "
                           "metrics are unknown, so the ratchet cannot grade")
    return window_entries(bodies, run_id, per_name=WINDOW_PER_LANE)


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


# --- the push runs' window (R10-CI-LAYOUT P2b) -------------------------------
#
# After P2b a push to main runs ci.yml (`CI`), whose tests.yml jobs are named
# `tests / <job>` beside the other units and `gate`. The metric stays the
# tests workflow's wall (DESIGN-P2 3.2): a CI run counts from its creation to
# its last `tests / *` job's completion, so a unit or gate finishing later
# moves nothing; a pre-umbrella Tests run counts as it always did, so the
# window stays continuous across the cut-over and an old run reads the same.
#
# A run's workflow is its `.path`, never its `.name`: the API's `.name` is the
# run's display title, and ci.yml's `run-name:` makes that `CI code pr=- base=-
# sha=<sha>`. Keyed on `.name == "CI"`, every umbrella run read as another
# workflow's; once the newest PUSH_WINDOW push runs were all umbrella runs
# (from d5dc3e26) the window held no measurable run and the grade refused on
# every push (CI job 120791448344).
PUSH_RUNS = ("ci.yml", "tests.yml")
PUSH_RUN_KIND = {"ci.yml": "CI", "tests.yml": "Tests"}
PUSH_RUNS_URL = "repos/{repo}/actions/workflows/{wf}/runs?event=push&branch=main&per_page={n}"
JOBS_URL = "repos/{repo}/actions/runs/{run}/jobs?per_page=100"
PUSH_WINDOW = 16
TESTS_JOB_PREFIX = "tests / "


def _at(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def run_kind(r: dict) -> "str | None":
    """'CI' for an umbrella run, 'Tests' for a pre-umbrella one, else None:
    read from the run's workflow file (`.path`, which a ref suffix may
    follow), the one field `run-name:` does not rewrite."""
    path = str(r.get("path") or "").split("@")[0]
    return PUSH_RUN_KIND.get(path.rsplit("/", 1)[-1]) if path else None


QUEUE_EPS = 2.0      # seconds: the API's 1 s timestamps round a ready edge


def run_minutes(r: dict) -> "float | None":
    """One completed push run's tests WORK in minutes: its critical path with
    every runner wait removed. None for a run that is neither the umbrella's
    nor a pre-umbrella Tests run, not completed, or with a counted job that
    was cancelled (its work was cut short, so it is unknown, not small).

    A job's `created_at` is when its last need finished (the API creates a
    job when it becomes ready), so `started_at - created_at` is its runner
    queue and `completed_at - started_at` its work. Each job's zero-queue end
    is its work plus the zero-queue end of the job that finished last at its
    ready time -- ci_critpath.py's walk-back rule, the need that ended last --
    and the metric is the latest zero-queue end among the counted jobs: a CI
    run's `tests / *` jobs, a Tests run's every job. The wall (creation to the
    last tests job) read the account's runner contention: an overlapping
    train's three sibling pushes queued the same 32 minutes of lanes for 17-24
    minutes and read 59.7 (main red, CI job 121295715608).

    A run without its jobs, with no completed counted job, or with a ran job
    missing a timestamp refuses: its work is unknown, never its wall."""
    walked = _walk(r)
    if walked is None:
        return None
    return round(max(j["end"] for j in walked if j["counted"]) / 60, 3)


def _walk(r: dict) -> "list[dict] | None":
    """run_minutes' walk, kept per job: each ran job's name, work seconds,
    zero-queue end, whether it is counted, and the index of the job that
    supplied its base (its need that ended last; None at a root). None and
    the refusals are run_minutes'."""
    kind = run_kind(r)
    if r.get("status") != "completed" or kind is None:
        return None
    jobs = r.get("jobs")
    if not isinstance(jobs, list):
        raise _refusal(f"{kind} push run {r.get('id')} carries no jobs list; "
                       "--gather-runs embeds them (fail closed)")
    counted = ((lambda n: n.startswith(TESTS_JOB_PREFIX)) if kind == "CI"
               else (lambda n: True))
    ran = [j for j in jobs if j.get("completed_at")]
    for j in ran:
        if not (j.get("created_at") and j.get("started_at")):
            raise _refusal(f"{kind} push run {r.get('id')} job {j.get('name')!r} "
                           "has no created_at/started_at; its queue is unknown "
                           "(fail closed)")
        if not j.get("conclusion"):
            raise _refusal(f"{kind} push run {r.get('id')} job {j.get('name')!r} "
                           "has no conclusion; whether its work prices is unknown "
                           "(fail closed)")
    if any(counted(str(j.get("name") or "")) and j.get("conclusion") == "cancelled"
           for j in ran):
        return None
    ran.sort(key=lambda j: (_at(j["created_at"]), _at(j["completed_at"])))
    walked: list[dict] = []
    for j in ran:
        ready = _at(j["created_at"]).timestamp() + QUEUE_EPS
        before = [i for i, w in enumerate(walked) if w["completed"] <= ready]
        base, pred = 0.0, None
        if before:
            last = max(walked[i]["completed"] for i in before)
            near = [i for i in before if walked[i]["completed"] >= last - QUEUE_EPS]
            pred = max(near, key=lambda i: walked[i]["end"])
            base = walked[pred]["end"]
        name = str(j.get("name") or "")
        work = max(0.0, (_at(j["completed_at"]) - _at(j["started_at"])).total_seconds())
        walked.append({"name": name, "work": work, "end": base + work,
                       "completed": _at(j["completed_at"]).timestamp(),
                       "counted": counted(name), "pred": pred,
                       "priced": j.get("conclusion") == "success",
                       "reference_work": reference_work(j, work)})
    if not any(w["counted"] for w in walked):
        raise _refusal(f"{kind} push run {r.get('id')} has no completed "
                       f"{'`' + TESTS_JOB_PREFIX + '*` ' if kind == 'CI' else ''}job (fail closed)")
    return walked


# --- the host-speed probe (R10-HOTFIX-CI-CRITPATH-4) --------------------------
#
# A job's wall on a hosted runner is its work times the host's slowness, and
# the fleet's mix is not stationary: `tests / fast (3.14)` drew a fast host
# (its 13 heaviest scripts at 0.50-0.61 of their 60-run medians) in 10 of
# the 60 push runs 41331759691..41818271680 and in 1 of the newest 26.
# Pricing each job at its fastest draw read that mix: the one fast draw aged
# out of the window at 8e90d8144 and the grade moved 22.117 -> 29.067, while
# the lane's work over its own scripts' speed stayed flat over all 60 runs
# (dev/audit/harnesses/r10_hotfix_ci_critpath_4/replay.py).
#
# So each heavy `tests / *` job runs tests/host_probe.py -- fixed
# pure-Python work -- as a step of its own, named PROBE_STEP and its
# interpreter, `Probe the runner's speed (python 3.14)`, before its suite.
# The step's duration is that host's slowness, measured in the same runner;
# the job's work in REFERENCE-HOST seconds is its work times
# PROBE_REFERENCE_S[python] over the probe's seconds. A job with no probe
# step (every run before this one, the light jobs) is priced as before.
PROBE_STEP = "Probe the runner's speed"
# The probe's seconds on the reference host, per interpreter (the same work
# runs at different speeds under 3.13 and 3.14). The reference host is the
# fleet's fast class (UNIT, the median factor of `tests / fast (3.14)`'s
# fast-class draws), the host the pre-probe grade priced that lane on.
# Measured on the fleet, never off it (a local machine's probe-to-script
# ratio is its own: one implied 17.50, the fleet 22.4): derived by
# tools/audit/seat/probe_bridge.py's rule from the probed runs in
# dev/audit/harnesses/r10_hotfix_ci_critpath_4/fleet.json, whose
# --self-test refuses a value the record does not re-derive.
PROBE_REFERENCE_S = {"3.13": 22.12, "3.14": 22.40}


def reference_work(job: dict, work: float) -> "float | None":
    """The job's work in reference-host seconds, read off its own probe step:
    work * PROBE_REFERENCE_S[python] / the probe's seconds. None when the job
    ran no successful probe step, its step names no known interpreter, or
    the step's duration is not positive (1 s timestamps): the job is then
    priced on its wall, as before the probe."""
    for step in job.get("steps") or []:
        name = str(step.get("name") or "")
        if not name.startswith(PROBE_STEP) or step.get("conclusion") != "success":
            continue
        python = name[len(PROBE_STEP):].strip().removeprefix("(python ").removesuffix(")")
        ref = PROBE_REFERENCE_S.get(python)
        if not ref or not (step.get("started_at") and step.get("completed_at")):
            return None
        probe = (_at(step["completed_at"]) - _at(step["started_at"])).total_seconds()
        return work * ref / probe if probe > 0 else None
    return None


def run_chain(r: dict) -> "list[str] | None":
    """The run's critical chain, root first: from the counted job that ended
    last, back through each job's base (run_minutes' walk-back rule). Every
    link is a need that ended last, so the chain is a real dependency path of
    the workflow, whichever hosts the run drew."""
    walked = _walk(r)
    if walked is None:
        return None
    i = max((k for k, w in enumerate(walked) if w["counted"]),
            key=lambda k: walked[k]["end"])
    chain = []
    while i is not None:
        chain.append(walked[i]["name"])
        i = walked[i]["pred"]
    return chain[::-1]


def gather_runs(out_file, *, repo=None, runner=None, window: int = PUSH_WINDOW, sleep=None) -> int:
    """The ci-ratchet job's runs.json: the newest `window` (PUSH_WINDOW when
    grading) push runs of ci.yml and the pre-umbrella tests.yml together, each
    with its jobs. Any failed read refuses by name: a short window is not a
    fast one. Every read rides tools/audit/seat/gh_read.py's read rule (4 reads,
    transient statuses only): main went red twice in a day (2026-11-10, -11) on
    one HTTP 502 here, the grading step never having run."""
    sys.path.insert(0, str(ROOT / "tools" / "audit" / "seat"))
    import gh_read  # noqa: E402 -- the one read rule
    repo = repo or os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        raise _refusal("--gather-runs needs GITHUB_REPOSITORY")
    run = runner or subprocess.run

    def api(*argv):
        def attempt():
            proc = run(["gh", "api", *argv], capture_output=True, text=True)
            if proc.returncode != 0 or not (proc.stdout or "").strip():
                return proc, (proc.stderr or "").strip() or "gh printed nothing"
            return proc, None
        proc, failure, _n, why = gh_read.retry(attempt, gh_read.gh_wait, sleep or time.sleep)
        if failure is not None:
            raise _refusal(f"gh api {argv[-1]} failed (rc {proc.returncode}) {why}: {failure[:300]}")
        return proc.stdout
    runs = []
    for wf in PUSH_RUNS:
        runs += json.loads(api(PUSH_RUNS_URL.format(repo=repo, wf=wf, n=window))).get("workflow_runs") or []
    runs = sorted(runs, key=lambda r: r.get("created_at") or "", reverse=True)[:window]
    for r in runs:
        if run_kind(r) is not None:
            r["jobs"] = [json.loads(x) for x in api(
                "--paginate", "--jq", ".jobs[]", JOBS_URL.format(repo=repo, run=r["id"])).splitlines() if x.strip()]
    Path(out_file).write_text(json.dumps({"workflow_runs": runs}))
    print(f"push runs: {len(runs)} ({sum(run_kind(r) == 'CI' for r in runs)} CI)")
    return len(runs)


# A job's work on one host is up to ~2.4x its work on another (R10-HOTFIX-
# CI-CRITPATH-3: a CPU-bound reference solve read 45.0 ms against 18.8 ms on
# the same code; per-script ratios 1.6-2.9 over one job's 31 scripts). A run
# whose work is under a third of the job's window MEDIAN therefore did other
# work -- a consumed proof, a skipped lane -- not the same work on a faster
# host, and never prices the job. The median, never the maximum: one slow or
# hung run past three times the job's fastest lifted a maximum-keyed floor
# over every genuine fast run and priced the job on a slow draw (+6.95 on
# `tests / fast (3.14)`, review of #3180 at 563c8e6db).
OTHER_WORK_FRACTION = 1 / 3


def window_work_minutes(runs: list[dict]) -> float:
    """The window's tests WORK, read off host speed: every job priced over
    the window by job_price -- a probed job at the median of its work in
    reference-host seconds, an unprobed one at its fastest `success` run --
    and the prices summed along the longest path through the needs the
    window observed (each job's need that ended last, in any of its runs),
    whichever job ended its run.

    Why a path through the window's needs, not each run's own chain: which
    job ends last is itself a draw (a lane queued behind a slow sibling
    hides a longer one), so a run's chain read the draw a second way.
    A need observed in one run is a dependency in every run.

    What the unprobed minimum costs (every job before the probe, and the
    light ones after it). The hosts are not two-speed (`tests / closures`
    read 1117..2401 s over 40 runs with mid values between), so the price
    is the fastest host the window drew: losing the fastest draws reprices
    the job on a mid host -- main red at 8e90d8144, one fast draw of
    `tests / fast (3.14)` in 26 runs aged out -- and real growth reads only
    once every pre-growth fast run has aged out of the window. A probed job
    reads growth once it is in half the window, all of it by 12 of 16 runs
    (dev/audit/harnesses/r10_hotfix_ci_critpath_4/replay.py).

    Only a `success` job prices: a skipped one did no work, a cancelled or
    failed one stopped short. A job that never succeeded in the window costs
    nothing. What that costs: a chain job that fails stops pricing, so a
    broken lane under-reads the grade, and a record taken across such a
    stretch is recorded low (review of #3180 at 3f7777a59). None when no
    run in the window is measurable."""
    needs, counted, work, probed = {}, set(), {}, {}
    for r in runs:
        walked = _walk(r)
        if walked is None:
            continue
        for j in walked:
            needs.setdefault(j["name"], set())
            if j["pred"] is not None:
                needs[j["name"]].add(walked[j["pred"]]["name"])
            if j["counted"]:
                counted.add(j["name"])
            if j["priced"]:
                work.setdefault(j["name"], []).append(j["work"])
                if j["reference_work"] is not None:
                    probed.setdefault(j["name"], []).append(j["reference_work"])
    if not counted:
        return None
    price = {name: job_price(seen, probed.get(name)) for name, seen in work.items()}
    end: dict[str, float] = {}

    def path_end(name, seen=()):
        # A need observed in one run and its inverse in another is no
        # dependency (two jobs that merely ended in turn): the edge that
        # would close the loop is dropped, never followed.
        if name not in end:
            end[name] = price.get(name, 0.0) + max(
                (path_end(n, (*seen, name)) for n in needs[name] if n not in (*seen, name)),
                default=0.0)
        return end[name]
    return round(max(path_end(n) for n in counted) / 60, 3)


def job_price(walls: list[float], reference: "list[float] | None") -> float:
    """One job's price over the window. Probed (R10-HOTFIX-CI-CRITPATH-4):
    the MEDIAN of its reference-host work, every host's speed already taken
    out by its own probe, so neither a slow fleet nor a lost fast draw moves
    it, one hung run does not, and growth reads once it is in half the
    window. Unprobed: the fastest wall (window_work_minutes' rule). Either
    way a run under OTHER_WORK_FRACTION of the median did other work."""
    seen = reference or walls
    floor = statistics.median(seen) * OTHER_WORK_FRACTION
    kept = [w for w in seen if w >= floor]
    return statistics.median(kept) if reference else min(kept)


def critical_path_minutes(runs_json: Path, stat: str = "grade") -> float:
    """window_work_minutes over runs.json's push runs, newest first. Graded
    over the newest PUSH_WINDOW; recorded (`stat="record"`, over a wider
    `--gather-runs --window N`) at the largest value any PUSH_WINDOW
    consecutive runs of it read -- the budget's headroom is the statistic's
    own window-to-window spread, never one window's luck."""
    runs = sorted(json.loads(runs_json.read_text())["workflow_runs"],
                  key=lambda r: r.get("created_at") or "", reverse=True)
    if stat == "record":
        spans = [runs[i:i + PUSH_WINDOW]
                 for i in range(max(1, len(runs) - PUSH_WINDOW + 1))]
    else:
        spans = [runs[:PUSH_WINDOW]]
    values = [v for v in map(window_work_minutes, spans) if v is not None]
    if not values:
        raise SystemExit("ci-ratchet: no completed push CI or Tests runs in "
                         "runs.json; cannot derive critical_path_minutes "
                         "(fail closed)")
    return max(values)


def derive(metrics_dir: Path, runs_json: Path | None,
           record: bool = False) -> dict[str, float]:
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
        derived["critical_path_minutes"] = critical_path_minutes(
            runs_json, "record" if record else "grade")
    return derived


def record_table(budgets: dict, derived: dict, head: str, reason: str) -> dict:
    """The table `--record` writes: every derived metric, stamped."""
    return {**derived, "recorded_at": head, "reason": reason}


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
        if key in REPORT_ONLY:
            lines.append(f"  info  {key}: {cur} (reference {budget}; "
                         "report-only, never graded)")
            continue
        over = cur > budget
        mark = "GREW" if over else "ok"
        if over:
            grew.append(key)
        lines.append(f"  {mark:<5} {key}: {cur} (budget {budget})")
    for key in sorted(set(derived) - set(budgets) - REPORT_ONLY):
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
        _art(8, "ci-metrics-fast", 8, None),
    ]})
    got, msg = safe(lambda: window_entries(good, "77"))
    ids = [e["id"] for e in got or []]
    ck("a good response still yields the window (the null control)",
       got is not None and ids == [7, 3, 1], msg or f"got {ids}, want [7, 3, 1]")
    ck("a duplicate (run, name) keeps the newest copy",
       2 not in ids and 3 in ids, f"got {ids}")
    ck("an artifact with no created_at does not outrank a dated copy",
       8 not in ids and 3 in ids, f"got {ids}")
    ck("an expired artifact, another name and THIS run are all out",
       {4, 5, 6}.isdisjoint(ids), f"got {ids}")
    ck("the .run_id fallback attributes a null .workflow_run",
       bool(got) and got[0]["run"] == 7, f"run={got[0]['run'] if got else None}")
    cut, msg = safe(lambda: window_entries(good, "77", limit=2))
    ck("the cut is taken in (run, name) order, as jq's unique_by emitted it",
       [e["id"] for e in cut or []] == [7, 3], msg or f"got {cut}")

    # --- the retry ----------------------------------------------------------
    def served(body, url):
        """What the server answers a name-filtered list call from `body`:
        only the artifacts carrying the URL's name."""
        if "name=" not in url:
            return body
        want = url.split("name=")[1].split("&")[0]
        return json.dumps({"artifacts": [a for a in json.loads(body)["artifacts"]
                                         if a.get("name") == want]})

    def stub(sequence):
        calls, slept = [], []

        def run(argv, **_kw):
            calls.append(argv)
            rc, out, err = sequence[min(len(calls), len(sequence)) - 1]
            if out:
                out = served(out, argv[-1])
            return subprocess.CompletedProcess(argv, rc, out, err)
        return run, calls, slept

    runner, calls, slept = stub([(1, "", "gh: Server Error (HTTP 502)"),
                                 (0, good, "")])
    entries, msg = safe(lambda: fetch_window("o/r", "77", runner=runner,
                                             sleep=slept.append))
    ck("a failed list call is retried and the retry's window is used",
       [e["id"] for e in entries or []] == [7, 3, 1]
       and len(calls) == len(WINDOW_LANES) + 1 and slept == [2.0], msg or f"calls={len(calls)} slept={slept}")
    runner, calls, slept = stub([(0, "", ""), (0, good, "")])
    entries, msg = safe(lambda: fetch_window("o/r", "77", runner=runner,
                                             sleep=slept.append))
    ck("an rc 0 with 0 bytes is retried too, not read as a window",
       len(entries or []) == 3 and len(calls) == len(WINDOW_LANES) + 1,
       msg or f"calls={len(calls)}")
    runner, calls, slept = stub([(1, "", "gh: HTTP 500"), (1, "", "gh: HTTP 500")])
    msg = refused(lambda: fetch_window("o/r", "77", runner=runner,
                                       sleep=slept.append, attempts=3))
    ck("spent attempts refuse by name (exit code, attempts), no traceback",
       "after 3 attempt(s)" in msg and "HTTP 500" in msg and slept == [2.0, 4.0],
       msg or "no refusal")

    # --- the window is read per lane, never from the repo-wide listing ------
    # The unfiltered listing timed out server-side into a 0-byte body on 4 of
    # 4 attempts per push from d5dc3e26 (CI job 120763639214) while the
    # name-filtered one answered; this stub serves only the latter.
    def lanes(broken=()):
        calls, slept = [], []

        def run(argv, **_kw):
            calls.append(argv)
            url = argv[-1]
            lane = url.split("name=ci-metrics-")[1].split("&")[0] if "name=ci-metrics-" in url else None
            if lane is None or lane in broken:
                return subprocess.CompletedProcess(argv, 1, "", "unexpected end of JSON input")
            return subprocess.CompletedProcess(argv, 0, json.dumps({"artifacts": [
                _art(len(calls) * 10, f"ci-metrics-{lane}", 5, "2026-10-20T10:00:00Z"),
                _art(len(calls) * 10 + 1, f"ci-metrics-{lane}", 77, "2026-10-20T11:00:00Z")]}), "")
        return run, calls, slept

    runner, calls, slept = lanes()
    entries, msg = safe(lambda: fetch_window("o/r", "77", runner=runner, sleep=slept.append))
    ck("the window is each lane's name-filtered listing, one call per lane, no retry",
       [(e["run"], e["name"]) for e in entries or []] == [
           (5, "ci-metrics-closures"), (5, "ci-metrics-coverage"), (5, "ci-metrics-fast")]
       and len(calls) == 3 and slept == [], msg or f"calls={[c[-1] for c in calls]}")
    runner, calls, slept = lanes(broken=("closures",))
    msg = refused(lambda: fetch_window("o/r", "77", runner=runner, sleep=slept.append, attempts=2))
    ck("one lane's spent attempts refuse naming that lane (not a two-lane window)",
       "ci-metrics-closures" in msg and "after 2 attempt(s)" in msg, msg or "no refusal")

    # A server that ignores `name=` hands every lane the same mixed listing:
    # read as three windows that would triple-count, and as a short one. The
    # stub above (`stub`, filtering by name) is this arm's null control.
    runner, calls, slept = stub([(0, good, "")])
    unfiltered = lambda argv, **kw: subprocess.CompletedProcess(argv, 0, good, "")
    msg = refused(lambda: fetch_window("o/r", "77", runner=unfiltered,
                                       sleep=lambda _s: None, attempts=1))
    ck("a lane listing carrying another name refuses (the filter was ignored)",
       "ci-metrics-fast artifacts fetch carried other names" in msg
       and "ci-metrics-closures" in msg, msg or "no refusal")
    entries, msg = safe(lambda: fetch_window("o/r", "77", runner=runner,
                                             sleep=slept.append))
    ck("and the same listing, name-filtered, is a window (the null control)",
       [e["id"] for e in entries or []] == [7, 3, 1], msg or f"got {entries}")
    triple, msg = safe(lambda: window_entries([good, good, good], "77"))
    ck("one listing read three times still counts each (run, name) once",
       [e["id"] for e in triple or []] == [7, 3, 1], msg or f"got {triple}")

    # The cut keeps each lane's NEWEST runs. Every lane lists one more run
    # than it keeps and this run's copy is absent (an upload not yet listed):
    # the union cut in (run, name) order alone would keep run 1 and drop each
    # lane's newest run.
    many = json.dumps({"artifacts": [
        _art(1000 * k + r, f"ci-metrics-{lane}", r,
             f"2026-10-20T{r:02d}:00:00Z")
        for k, lane in enumerate(WINDOW_LANES)
        for r in range(1, WINDOW_PER_LANE + 2)]})
    runner, calls, slept = stub([(0, many, "")])
    entries, msg = safe(lambda: fetch_window("o/r", "77", runner=runner,
                                             sleep=slept.append))
    by_lane = {lane: sorted(e["run"] for e in entries or []
                            if e["name"] == f"ci-metrics-{lane}")
               for lane in WINDOW_LANES}
    ck("each lane keeps its newest WINDOW_PER_LANE runs, not the union's oldest",
       all(runs == list(range(2, WINDOW_PER_LANE + 2))
           for runs in by_lane.values())
       and calls and f"per_page={WINDOW_FETCH_PER_LANE}" in calls[0][-1],
       msg or f"runs per lane {by_lane}")

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

    # --- the push runs' window across the umbrella cut-over (P2b) -----------
    def ci_run(rid, created, tests_end, *, other_end="2026-10-22T02:00:00Z", jobs=True):
        # Every job ready and started at the run's creation (no queue), so its
        # work is its span: the wall these fixtures were written against.
        t0 = {"created_at": created, "started_at": created, "conclusion": "success"}
        js = [{"name": "tests / fast (3.14)", "completed_at": tests_end, **t0},
              {"name": "tests / ci-ratchet", "completed_at": "2026-10-22T00:10:00Z", **t0},
              {"name": "gate", "completed_at": other_end, **t0},
              {"name": "codeql / Analyze (python)", "completed_at": other_end, **t0}]
        # `.name` as the API returns it under ci.yml's run-name, not "CI".
        return {"id": rid, "name": f"CI code pr=- base=- sha={rid:040d}",
                "path": ".github/workflows/ci.yml", "status": "completed",
                "created_at": created,
                "updated_at": other_end, **({"jobs": js} if jobs else {})}
    tests_run = {"id": 1, "name": "Tests", "path": ".github/workflows/tests.yml",
                 "status": "completed",
                 "created_at": "2026-10-21T00:00:00Z", "updated_at": "2026-10-21T00:50:00Z",
                 "jobs": [{"name": "fast (3.14)", "created_at": "2026-10-21T00:00:00Z",
                           "started_at": "2026-10-21T00:00:00Z",
                           "completed_at": "2026-10-21T00:50:00Z",
                           "conclusion": "success"}]}
    m, msg = safe(lambda: run_minutes(ci_run(2, "2026-10-22T00:00:00Z", "2026-10-22T00:40:00Z")))
    ck("a CI push run is measured to its last `tests / *` job, not to gate or another unit (40, not 120)",
       m == 40.0, msg or f"got {m}")
    ck("a pre-umbrella Tests push run is measured on its every job (the null: 50)",
       run_minutes(tests_run) == 50.0)
    ck("another workflow's run, or one not completed, is not in the window",
       run_minutes({**tests_run, "name": "Card", "path": ".github/workflows/card.yml"}) is None
       and run_minutes({**tests_run, "path": None}) is None
       and run_minutes({**tests_run, "status": "in_progress"}) is None)
    for label, r in (("carries no jobs", ci_run(3, "2026-10-22T00:00:00Z", "x", jobs=False)),
                     ("has no completed tests job", {**ci_run(4, "2026-10-22T00:00:00Z", None),
                                                     "jobs": [{"name": "gate", "completed_at": "2026-10-22T01:00:00Z"},
                                                              {"name": "tests / fast (3.14)", "completed_at": None}]})):
        try:
            msg = refused(lambda r=r: run_minutes(r))
        except Exception as exc:  # a crash reddens this check by name, never the whole self-test
            msg = f"crashed: {type(exc).__name__}"
        ck(f"a CI push run that {label} refuses (its wall is unknown, never its run's)",
           "fail closed" in msg, msg or "no refusal")
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "runs.json"
        f.write_text(json.dumps({"workflow_runs": [tests_run, ci_run(2, "2026-10-22T00:00:00Z",
                                                                     "2026-10-22T00:40:00Z")]}))
        cp, msg = safe(lambda: critical_path_minutes(f))
        ck("a window across the cut-over measures both kinds, its longest chain (50)",
           cp == 50.0, msg or f"got {cp}")
        # The red this pins (CI job 120791448344): a window of umbrella runs
        # alone, each titled by run-name, is measured -- not "no runs".
        f.write_text(json.dumps({"workflow_runs": [
            ci_run(i, "2026-10-22T00:00:00Z", f"2026-10-22T00:{30 + i:02d}:00Z")
            for i in range(1, 9)]}))
        cp, msg = safe(lambda: critical_path_minutes(f))
        ck("an all-umbrella window, titled `CI code ...` by run-name, is measured "
           "by workflow path (its fastest run's 31)", cp == 31.0, msg or f"got {cp}")
        ck("a ci.yml run is kind CI whatever its title, a ref suffix included",
           run_kind({"name": "anything", "path": ".github/workflows/ci.yml@refs/heads/main"}) == "CI"
           and run_kind({"name": "CI", "path": ".github/workflows/card.yml"}) is None,
           "keyed on .name, not .path")

        listings = {"ci.yml": [ci_run(i, f"2026-10-22T{i:02d}:00:00Z", "2026-10-22T19:00:00Z", jobs=False)
                               for i in range(1, 11)],
                    "tests.yml": [{**tests_run, "id": 100 + i, "created_at": f"2026-10-21T{i:02d}:00:00Z"}
                                  for i in range(1, 11)]}
        reads = []

        def gh(argv, **_kw):
            reads.append(argv)
            url = argv[-1]
            if "/jobs?" in url:
                return subprocess.CompletedProcess(argv, 0, json.dumps(
                    {"name": "tests / fast (3.14)", "completed_at": "2026-10-22T09:00:00Z"}) + "\n", "")
            wf = url.split("/workflows/")[1].split("/")[0]
            return subprocess.CompletedProcess(argv, 0, json.dumps({"workflow_runs": listings[wf]}), "")
        n, msg = safe(lambda: gather_runs(f, repo="o/r", runner=gh))
        got = json.loads(f.read_text())["workflow_runs"] if n else []
        ck("--gather-runs keeps the newest PUSH_WINDOW (16) push runs of ci.yml and tests.yml together, jobs on every run",
           PUSH_WINDOW == 16 and n == 16 and [run_kind(r) for r in got].count("CI") == 10
           and all("jobs" in r for r in got)
           and sum("/jobs?" in a[-1] for a in reads) == 16, msg or f"n={n}")
        reads.clear()
        n, msg = safe(lambda: gather_runs(f, repo="o/r", runner=gh, window=3))
        ck("--gather-runs --window N keeps the newest N (a record's wider window)",
           n == 3 and sum("/jobs?" in a[-1] for a in reads) == 3
           and all("per_page=3" in a[-1] for a in reads if "/jobs?" not in a[-1]), msg or f"n={n}")
        naps = []
        msg = refused(lambda: gather_runs(f, repo="o/r", sleep=naps.append, runner=lambda argv, **_kw: subprocess.CompletedProcess(
            argv, 1, "", "gh: HTTP 502")))
        ck("a sustained 502 on the runs read refuses by name after the read rule's 4 reads (a short window is not a fast one)",
           "failed (rc 1)" in msg and "HTTP 502" in msg and len(naps) == 3, msg or "no refusal")
        # R10-GH-READ-RESIDUE: one 502 on the jobs listing of one run (main red 2026-11-10, -11) is ridden out.
        reads.clear()
        flaky = []

        def gh_502_once(argv, **kw):
            if "/jobs?" in argv[-1] and not flaky:
                flaky.append(argv)
                return subprocess.CompletedProcess(argv, 1, "", "gh: HTTP 502")
            return gh(argv, **kw)
        n, msg = safe(lambda: gather_runs(f, repo="o/r", runner=gh_502_once, sleep=lambda _s: None))
        ck("one injected 502 on a jobs listing still gathers the whole window",
           n == 16 and len(flaky) == 1 and all("jobs" in r for r in json.loads(f.read_text())["workflow_runs"]
                                               if run_kind(r) is not None), msg or f"n={n}")
        reads.clear()
        gone = []
        naps.clear()

        def gh_404(argv, **_kw):
            gone.append(argv)
            return subprocess.CompletedProcess(argv, 1, "", "gh: Not Found (HTTP 404)")
        msg = refused(lambda: gather_runs(f, repo="o/r", runner=gh_404, sleep=naps.append))
        ck("null control: a 404 refuses after one read, no sleep",
           len(gone) == 1 and not naps and "HTTP 404" in msg, msg or "no refusal")

    # --- runner queue is not work (main red, CI job 121295715608) ----------
    # Run 40225415246, its timeline as the jobs API gave it (minutes from the
    # run's creation): every heavy lane was created at +0.5 and waited 17-24
    # minutes for a runner behind three other push runs of one overlapping
    # train, so its wall read 59.7 while the same lanes' work read 32 -- the
    # 33.7-minute run da12aa37d queued nothing. The metric is the work.
    def j(name, created, started, completed, conclusion="success"):
        at = lambda m: (datetime(2026, 10, 25, 19, 18, 35, tzinfo=timezone.utc)
                        .timestamp() + m * 60)
        iso = lambda m: datetime.fromtimestamp(at(m), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return {"name": name, "created_at": iso(created), "started_at": iso(started),
                "completed_at": iso(completed), "conclusion": conclusion}
    queued = [j("prelude", 0.0, 0.2, 0.5), j("tests / closure-scope", 0.5, 0.5, 0.5, "skipped"),
              j("codeql / Analyze (python)", 0.5, 15.5, 34.9),
              j("tests / arch-instrument", 0.5, 17.9, 49.7), j("tests / closures", 0.5, 18.5, 45.1),
              j("tests / coverage", 0.5, 24.6, 51.9), j("tests / fast (3.14)", 0.5, 24.8, 54.6),
              j("tests / coverage-ratchet", 51.9, 52.7, 52.9),
              j("tests / ci-ratchet", 54.6, 58.6, 59.7), j("gate", 59.7, 66.7, 67.1)]
    run_q = {**ci_run(5, "2026-10-25T19:18:35Z", None), "jobs": queued}
    m, msg = safe(lambda: run_minutes(run_q))
    ck("a run whose lanes queued for runners reads its work, not its wall "
       "(32.1 = prelude 0.3 + arch-instrument 31.8, not 59.7)",
       m is not None and abs(m - 32.1) < 0.05, msg or f"got {m}")
    # The null control: the same jobs and work, replayed with no runner wait
    # (each ready at its last need's end and started at once), whose wall IS
    # its work -- the old wall measure and this one must agree on it.
    run_n = {**run_q, "jobs": [
        j("prelude", 0.0, 0.0, 0.3), j("tests / closure-scope", 0.3, 0.3, 0.3, "skipped"),
        j("codeql / Analyze (python)", 0.3, 0.3, 19.7),
        j("tests / arch-instrument", 0.3, 0.3, 32.1), j("tests / closures", 0.3, 0.3, 26.9),
        j("tests / coverage", 0.3, 0.3, 27.6), j("tests / fast (3.14)", 0.3, 0.3, 30.1),
        j("tests / coverage-ratchet", 27.6, 27.6, 27.8),
        j("tests / ci-ratchet", 30.1, 30.1, 31.2), j("gate", 32.1, 32.1, 32.5)]}
    m0, msg = safe(lambda: run_minutes(run_n))
    ck("the same work with no queue reads the same 32.1, its wall (the null control)",
       m0 is not None and m is not None and abs(m0 - m) < 0.05 and abs(m0 - 32.1) < 0.05,
       msg or f"got {m0} vs {m}")
    run_s = {**run_q, "jobs": queued[:-2] + [j("tests / ci-ratchet", 54.6, 58.6, 69.7)]}
    m1, msg = safe(lambda: run_minutes(run_s))
    ck("a slower job on the critical path still grows the metric (10 more minutes of ci-ratchet)",
       m1 is not None and abs(m1 - (0.3 + 29.8 + 11.1)) < 0.05, msg or f"got {m1}")
    run_c = {**run_q, "jobs": queued[:-2] + [j("tests / ci-ratchet", 54.6, 58.6, 59.0, "cancelled")]}
    mc, msg = safe(lambda: run_minutes(run_c))
    ck("a run with a cancelled `tests / *` job is not in the window (its work was cut short)",
       mc is None, msg or f"got {mc}")
    bare = {**run_q, "jobs": [{k: v for k, v in queued[0].items() if k != "conclusion"}] + queued[1:]}
    try:
        msg = refused(lambda: run_minutes(bare))
    except Exception as exc:  # a crash reddens this check by name
        msg = f"crashed: {exc!r}"
    ck("a ran job with no conclusion refuses (whether it prices is unknown)",
       "has no conclusion" in msg, msg or "no refusal")
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "runs.json"
        # R10-HOTFIX-CI-CRITPATH-3: the same arch-instrument work on a host
        # twice as slow (63.6 minutes, not 31.8) reads 63.9 per run, so a
        # window of fifteen slow draws and one fast one has median 63.9 --
        # the host draw. The grade prices each job at its fastest run: 32.1.
        slow = queued[:3] + [j("tests / arch-instrument", 0.5, 17.9, 81.5)] + queued[4:]
        run_sl = {**run_q, "jobs": slow}

        def window(runs):
            return json.dumps({"workflow_runs": [
                {**r, "id": i, "created_at": f"2026-10-{30 - i:02d}T00:00:00Z"}
                for i, r in enumerate(runs, 1)]})
        f.write_text(window([run_sl] * 15 + [run_q]))
        g, msg = safe(lambda: critical_path_minutes(f))
        ck("a window of slow host draws grades the work, not the draw "
           "(32.1, its median 63.9)",
           g is not None and abs(g - 32.1) < 0.05
           and abs(run_minutes(run_sl) - 63.9) < 0.05, msg or f"got {g}")
        grown = queued[:3] + [j("tests / arch-instrument", 0.5, 17.9, 54.7)] + queued[4:]
        f.write_text(window([{**run_q, "jobs": grown}] * 16))
        gg, msg = safe(lambda: critical_path_minutes(f))
        ck("a job grown by 5 minutes on every host grows the grade by 5 (37.1)",
           gg is not None and abs(gg - 37.1) < 0.05, msg or f"got {gg}")
        noop = queued[:3] + [j("tests / arch-instrument", 0.5, 17.9, 22.9)] + queued[4:]
        f.write_text(window([{**run_q, "jobs": noop}] + [run_sl] * 15))
        gn, msg = safe(lambda: critical_path_minutes(f))
        ck("a run under a third of the job's window median did other work and "
           "never prices it (63.9, not 5.3)",
           gn is not None and abs(gn - 63.9) < 0.05, msg or f"got {gn}")
        # Review of #3180 at 563c8e6db: one hung run of a lane, past three
        # times its fastest, lifted a maximum-keyed floor over every fast run
        # and priced the lane on it (+6.95 on real runs). Keyed on the median
        # it moves nothing, however slow.
        hung = queued[:3] + [j("tests / arch-instrument", 0.5, 17.9, 17.9 + 3.2 * 31.8)] + queued[4:]
        f.write_text(window([{**run_q, "jobs": hung}] + [run_q] * 15))
        g_hung, msg = safe(lambda: critical_path_minutes(f))
        ck("one run of a job past three times its fastest does not move the grade "
           "(32.1, not 102.1)",
           g_hung is not None and abs(g_hung - 32.1) < 0.05, msg or f"got {g_hung}")
        # A failed job stopped short: its work is not the job's, however far
        # above the other-work floor (15.0 against 31.8).
        failjob = queued[:3] + [j("tests / arch-instrument", 0.5, 17.9, 32.9, "failure")] + queued[4:]
        f.write_text(window([{**run_q, "jobs": failjob}] + [run_q] * 15))
        gf, msg = safe(lambda: critical_path_minutes(f))
        ck("a failed job never prices (32.1, not 15.3)",
           gf is not None and abs(gf - 32.1) < 0.05, msg or f"got {gf}")
        # A cancelled job outside `tests / *` leaves its run measurable, so its
        # truncated work would price the job (prelude 0.15, not 0.3).
        cut = [j("prelude", 0.0, 0.2, 0.35, "cancelled")] + queued[1:]
        f.write_text(window([{**run_q, "jobs": cut}] + [run_q] * 15))
        gx, msg = safe(lambda: critical_path_minutes(f))
        ck("a cancelled job never prices (32.1, not 31.95)",
           gx is not None and abs(gx - 32.1) < 0.02, msg or f"got {gx}")
        # OTHER_WORK_FRACTION's level, pinned from both sides (review of #3180
        # at 3f7777a59: the 1/3 -> 1/2 mutant passed every check above). A job
        # at 30.0 in fourteen runs, 12.0 in one (between a half and a third of
        # its median) and 9.0 in one (between a third and a quarter): a third
        # prices it at 12.0; a half would price 30.0, a quarter 9.0.
        def lone(i, w):
            return {**ci_run(i, f"2026-10-{30 - i:02d}T00:00:00Z", None),
                    "jobs": [j("prelude", 0.0, 0.0, 0.3),
                             j("tests / arch-instrument", 0.3, 0.3, 0.3 + w)]}
        level = [lone(1, 12.0), lone(2, 9.0)] + [lone(i, 30.0) for i in range(3, 17)]
        gl, msg = safe(lambda: window_work_minutes(level))
        ck("the other-work floor sits at a third of the window median "
           "(12.3: a half would read 30.3, a quarter 9.3)",
           gl is not None and abs(gl - 12.3) < 0.05, msg or f"got {gl}")
        # Twenty runs, the one fast draw newest: the newest sixteen grade 32.1;
        # a record over all twenty reads every sixteen-run window and keeps the
        # largest, 63.9 -- the statistic's own window-to-window spread.
        f.write_text(window([run_q] + [run_sl] * 19))
        g, msg = safe(lambda: critical_path_minutes(f))
        r, msg2 = safe(lambda: critical_path_minutes(f, stat="record"))
        ck("the grade reads the newest PUSH_WINDOW runs, a record the largest "
           "of its every PUSH_WINDOW-run window (32.1, 63.9)",
           g is not None and abs(g - 32.1) < 0.05 and r is not None and abs(r - 63.9) < 0.05,
           msg or msg2 or f"grade {g} record {r}")
        md = Path(td) / "m"
        md.mkdir()
        (md / "ci-metrics-fast.tsv").write_text("fast\tmode\tfull\t1\t0\tpush\t77\n")
        real = globals()["archscore_metrics"]
        globals()["archscore_metrics"] = lambda only=None: {}
        try:
            dg, msg = safe(lambda: derive(md, f))
            dr, msg2 = safe(lambda: derive(md, f, record=True))
        finally:
            globals()["archscore_metrics"] = real
        ck("derive grades the newest window and a --record derive writes the largest window",
           (dg or {}).get("critical_path_minutes") is not None
           and abs(dg["critical_path_minutes"] - 32.1) < 0.05
           and abs((dr or {}).get("critical_path_minutes", 0) - 63.9) < 0.05,
           msg or msg2 or f"grade {dg} record {dr}")

    # --- the host-speed probe (R10-HOTFIX-CI-CRITPATH-4) --------------------
    # main red at 8e90d8144: `tests / fast (3.14)`'s one fast draw in the
    # window aged out and the fastest-draw price moved 1223 -> 1640 s on the
    # same work. A probed job is priced on its work over its own runner's
    # probe; each fixture is a run of prelude (18 s) and one heavy lane whose
    # wall and probe step are given in seconds.
    ref = PROBE_REFERENCE_S["3.14"]
    P = 20  # the probe step's seconds on the fixtures' usual host (1 s timestamps)

    def probed(i, wall, probe, *, python="3.14", conclusion="success"):
        t0 = datetime(2026, 11, 1, tzinfo=timezone.utc).timestamp() + i * 7200
        iso = lambda s: datetime.fromtimestamp(t0 + s, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        lane = {"name": "tests / fast (3.14)", "created_at": iso(18), "started_at": iso(18),
                "completed_at": iso(18 + wall), "conclusion": "success"}
        if probe is not None:
            lane["steps"] = [
                {"name": "Run actions/checkout", "started_at": iso(18), "completed_at": iso(40),
                 "conclusion": "success"},
                {"name": f"{PROBE_STEP} (python {python})", "started_at": iso(40),
                 "completed_at": iso(40 + probe), "conclusion": conclusion}]
        return {**ci_run(i, iso(0), None),
                "jobs": [{"name": "prelude", "created_at": iso(0), "started_at": iso(0),
                          "completed_at": iso(18), "conclusion": "success"}, lane]}

    def grade(runs):
        return safe(lambda: window_work_minutes(runs))

    # The level: 1911 s of wall on a host whose probe took P seconds reads
    # 1911 * ref / P reference-host seconds; the grade adds prelude's 18.
    one = [probed(1, 1911, P)]
    g1, msg = grade(one)
    ck("a probed job prices its wall times PROBE_REFERENCE_S over its probe "
       "((18 + 1911 * ref / P) / 60)",
       ref > 0 and g1 is not None and abs(g1 - round((18 + 1911 * ref / P) / 60, 3)) < 0.002,
       msg or f"got {g1}")
    # The window this red read: fifteen slow draws (factor 1.0) and one fast
    # one (0.6) of the same work. Its fast draw ageing out moved the
    # fastest-draw price 40 %; the probed price moves nothing.
    slow = [probed(i, 1911, P) for i in range(1, 16)]
    fast = probed(16, round(1911 * 0.6), round(P * 0.6))
    g_with, msg = grade(slow + [fast])
    g_lost, msg2 = grade(slow + [probed(16, 1911, P)])
    ck("losing the window's one fast draw moves a probed grade by under 1 % "
       "(the red at 8e90d8144 moved the fastest-draw grade 31 %)",
       g_with is not None and g_lost is not None and abs(g_lost - g_with) / g_with < 0.01,
       msg or msg2 or f"{g_with} -> {g_lost}")
    u_with, msg = grade([probed(i, 1911, None) for i in range(1, 16)]
                        + [probed(16, round(1911 * 0.6), None)])
    u_lost, msg2 = grade([probed(i, 1911, None) for i in range(1, 17)])
    ck("the same windows unprobed reproduce the red: the fastest-draw grade "
       "moves over 30 % (the fixture's own null control)",
       u_with is not None and u_lost is not None and (u_lost - u_with) / u_with > 0.3,
       msg or msg2 or f"{u_with} -> {u_lost}")
    # The planted slow fleet: every run's host 1.9x slower, wall and probe.
    g_fleet, msg = grade([probed(i, round(1911 * 1.9), round(P * 1.9)) for i in range(1, 17)])
    g_base, msg2 = grade([probed(i, 1911, P) for i in range(1, 17)])
    ck("a fleet 1.9x slower on the same work does not move the grade",
       g_fleet is not None and g_base is not None and abs(g_fleet - g_base) / g_base < 0.01,
       msg or msg2 or f"{g_base} -> {g_fleet}")
    # The planted growth (the null control of the two above): 300 more
    # seconds of work on the same hosts, in the newest 9 of 16 runs -- the
    # median's lag -- reads all of it: 300 * ref / P / 60.
    grown = ([probed(i, 1911 + 300, P) for i in range(1, 10)]
             + [probed(i, 1911, P) for i in range(10, 17)])
    g_grown, msg = grade(grown)
    ck("300 s more work in 9 of 16 runs grows the grade by all of it (300 * ref / P / 60)",
       g_grown is not None and g_base is not None
       and abs(g_grown - g_base - 300 * ref / P / 60) < 0.01,
       msg or f"{g_base} -> {g_grown}")
    # One hung run, its wall 3.2x and its probe unremarkable, moves nothing.
    g_hung, msg = grade([probed(1, round(1911 * 3.2), P)]
                        + [probed(i, 1911, P) for i in range(2, 17)])
    ck("one hung run of a probed job does not move the grade",
       g_hung is not None and g_base is not None and abs(g_hung - g_base) < 0.01,
       msg or f"{g_base} -> {g_hung}")
    # The fall-backs, each priced on the wall as before the probe: no probe
    # step, a failed one, an interpreter with no reference, a 0 s step.
    for label, run in (("no probe step", probed(1, 1911, None)),
                       ("a failed probe step", probed(1, 1911, P, conclusion="failure")),
                       ("a probe under an unreferenced python", probed(1, 1911, P, python="3.99")),
                       ("a probe step of 0 s", probed(1, 1911, 0))):
        g_fb, msg = grade([run])
        ck(f"{label} prices the job on its wall (32.15, as before the probe)",
           g_fb is not None and abs(g_fb - round((18 + 1911) / 60, 3)) < 0.002,
           msg or f"got {g_fb}")
    ck("a probe step's interpreter selects its reference (3.13 and 3.14 differ)",
       reference_work({"steps": [{"name": f"{PROBE_STEP} (python 3.13)", "conclusion": "success",
                                  "started_at": "2026-11-01T00:00:00Z",
                                  "completed_at": "2026-11-01T00:00:10Z"}]}, 100.0)
       == 100.0 * PROBE_REFERENCE_S["3.13"] / 10
       and PROBE_REFERENCE_S["3.13"] != PROBE_REFERENCE_S["3.14"])

    # Which job ends last is itself a draw: a lane that queued behind a
    # sibling's slow host ends last and hides the longer one. The window is
    # priced over every need it observed, so a path counts whether or not
    # its job ended its run: arch-instrument's 30 minutes of work, which
    # ended before fast (3.14) and ci-ratchet in every run (fast queued 14.5
    # minutes), set the critical path (30.5, not the last job's 21.5).
    def dag_run(i, arch_work):
        return {**ci_run(i, f"2026-10-{30 - i:02d}T00:00:00Z", None), "jobs": [
            j("prelude", 0.0, 0.0, 0.5),
            j("tests / arch-instrument", 0.5, 0.5, 0.5 + arch_work),
            j("tests / fast (3.14)", 0.5, 15.0, 35.0),
            j("tests / ci-ratchet", 35.0, 35.0, 36.0)]}
    g_dag, msg = grade([dag_run(i, 30.0) for i in range(1, 17)])
    g_dag0, msg2 = grade([dag_run(i, 10.0) for i in range(1, 17)])
    ck("a longer path that never ended its run still sets the grade (30.5, "
       "not 21.5); shortened to 10 minutes, the last job's path is the "
       "grade again (21.5, the null control)",
       g_dag is not None and abs(g_dag - 30.5) < 0.01
       and g_dag0 is not None and abs(g_dag0 - 21.5) < 0.01,
       msg or msg2 or f"{g_dag}, {g_dag0}")

    # Report-only (R10-CI-SLIM card C2): critical_path_minutes is printed
    # against its reference and never graded; every other row stays graded at
    # zero tolerance, which a planted counter and a planted archscore growth
    # show beside it.
    bt = {"recorded_at": "x", "critical_path_minutes": 23.574,
          "script_runs_per_push": 54, "archscore.dead_members": 1}
    ok_cp = {"critical_path_minutes": 23.574, "script_runs_per_push": 54,
             "archscore.dead_members": 1}
    l_cp, g_cp = compare(bt, {**ok_cp, "critical_path_minutes": 99.0})
    _, g_count = compare(bt, {**ok_cp, "script_runs_per_push": 55})
    _, g_arch = compare(bt, {**ok_cp, "archscore.dead_members": 2})
    _, g_both = compare(bt, {**ok_cp, "critical_path_minutes": 99.0,
                              "script_runs_per_push": 55})
    _, g_norow = compare({k: v for k, v in bt.items() if k != "critical_path_minutes"},
                         {**ok_cp, "critical_path_minutes": 99.0})
    ck("critical_path_minutes growth (23.574 -> 99.0) is printed, never graded",
       g_cp == 0 and any(x.startswith("  info  critical_path_minutes: 99.0")
                         for x in l_cp), f"grew {g_cp}: {l_cp}")
    ck("a counter growth (54 -> 55) beside it still fails", g_count == 1, f"grew {g_count}")
    ck("an archscore growth (1 -> 2) beside it still fails", g_arch == 1, f"grew {g_arch}")
    ck("both planted: only the graded row counts", g_both == 1, f"grew {g_both}")
    ck("an unrecorded report-only row is not a new metric", g_norow == 0, f"grew {g_norow}")
    ck("the retired band row is not a row this ratchet knows",
       budget_problems(bt) == []
       and budget_problems({**bt, "critical_path_minutes_band": 1.3}) != [],
       f"{budget_problems(bt)}")
    rt = record_table(bt, {"critical_path_minutes": 35.317, "script_runs_per_push": 53},
                      "h" * 40, "r")
    ck("--record re-records every derived metric, the reference included",
       rt == {"critical_path_minutes": 35.317, "script_runs_per_push": 53,
              "recorded_at": "h" * 40, "reason": "r"},
       f"{rt}")

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
    if argv[:1] == ["--gather-runs"]:
        window = PUSH_WINDOW
        if len(argv) == 4 and argv[2] == "--window" and argv[3].isdigit() and int(argv[3]) > 0:
            window = int(argv[3])
        elif len(argv) != 2:
            print("ci-ratchet: --gather-runs needs exactly FILE [--window N]", file=sys.stderr)
            return 2
        gather_runs(argv[1], window=window)
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
    derived = derive(metrics_dir, runs_json, record=record_reason is not None)
    if record_reason is not None:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True,
                              check=True).stdout.strip()
        table = record_table(budgets, derived, head, record_reason)
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
