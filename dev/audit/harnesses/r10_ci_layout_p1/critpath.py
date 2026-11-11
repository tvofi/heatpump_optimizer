"""W1's critical-path counterfactual over saved Tests pull-request runs (R10-CI-LAYOUT PR 1).

    python3 -I dev/audit/harnesses/r10_ci_layout_p1/critpath.py RAW CASES [--case SCOPED|FULL] [--n 20]

The method is DESIGN-P1/P2's `measure/p2/critpath.py` at archive/probe/design-ci-rev4,
unchanged in its model: holding every job's duration fixed, `closures` starts the
queue it actually waited after `closure-scope` instead of after `coverage` (W1 deletes
the coverage->closures edge), `composed-proof` (deleted with it) adds no tail, and the
run ends at the latest remaining job. RAW holds `tests_runs_pull_request*.json` (the
`actions/workflows/tests.yml/runs?event=pull_request&status=completed` pages) and
`tests_jobs_<run>.json` (`actions/runs/<run>/jobs?filter=latest`); CASES is a TSV of
`run_id job_id CASE line`, the CASE word read from that run's closure-scope log
("CASE: SCOPED -- ..."). The newest N runs of the asked case are taken, in the
listing's order. `--self-test` checks the model on two synthetic runs.
"""
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path


def t(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() if s else None


def gain(run, jobs):
    """(wall, gain) for one run: seconds the run ends sooner without the edge and composed-proof."""
    J = {j["name"]: j for j in jobs}
    st = t(run["run_started_at"])
    done = [j for j in J.values() if j.get("completed_at") and j["conclusion"] != "skipped"]
    old_end = max(t(j["completed_at"]) for j in done)
    cs_end, cov_end = t(J["closure-scope"]["completed_at"]), t(J["coverage"]["completed_at"])
    cl_start, cl_end = t(J["closures"]["started_at"]), t(J["closures"]["completed_at"])
    alt_cl_end = cs_end + max(0.0, cl_start - cov_end) + (cl_end - cl_start)
    others = [t(j["completed_at"]) for n, j in J.items() if j in done
              and n not in ("closures", "composed-proof", "closures-autofix")]
    new_end = max(others + [alt_cl_end])
    return old_end - st, old_end - new_end


def main(argv):
    if argv[:1] == ["--self-test"]:
        def j(n, s, e):
            return {"name": n, "conclusion": "success", "started_at": s, "completed_at": e}
        run = {"run_started_at": "2026-01-01T00:00:00Z"}
        base = [j("closure-scope", "2026-01-01T00:00:00Z", "2026-01-01T00:00:20Z"),
                j("fast (3.14)", "2026-01-01T00:00:20Z", "2026-01-01T00:10:00Z"),
                j("coverage", "2026-01-01T00:00:20Z", "2026-01-01T00:15:00Z")]
        late = base + [j("closures", "2026-01-01T00:15:05Z", "2026-01-01T00:20:00Z"),
                       j("composed-proof", "2026-01-01T00:20:05Z", "2026-01-01T00:20:30Z")]
        _, g = gain(run, late)
        # closures moves to 20 s + 5 s + 295 s = 320 s; coverage (900 s) then ends the run.
        ok1 = abs(g - (1230 - 900)) < 1e-6
        # Null control: a run whose closures already ends before coverage gains only composed-proof's tail.
        early = base + [j("closures", "2026-01-01T00:00:25Z", "2026-01-01T00:01:00Z")]
        _, g0 = gain(run, early)
        ok2 = abs(g0) < 1e-6
        print(f"self-test: edge+tail gain {g:.0f} s (want 330) {'ok' if ok1 else 'FAIL'}; "
              f"null control {g0:.0f} s (want 0) {'ok' if ok2 else 'FAIL'}")
        return 0 if ok1 and ok2 else 1
    raw, cases = Path(argv[0]), Path(argv[1])
    want = argv[argv.index("--case") + 1] if "--case" in argv else "SCOPED"
    n = int(argv[argv.index("--n") + 1]) if "--n" in argv else 20
    case = {l.split("\t")[0]: l.split("\t")[2] for l in cases.read_text().splitlines() if l.strip()}
    runs = [r for f in sorted(raw.glob("tests_runs_pull_request*.json"))
            for r in json.loads(f.read_text())["workflow_runs"]]
    runs.sort(key=lambda r: r["created_at"], reverse=True)
    rows = []
    for r in runs:
        if case.get(str(r["id"])) != want:
            continue
        rows.append((r["id"], *gain(r, json.loads((raw / f"tests_jobs_{r['id']}.json").read_text())["jobs"])))
        if len(rows) == n:
            break
    for rid, wall, g in rows:
        print(f"{rid}  wall {wall / 60:6.1f} min  W1 gain {g / 60:5.1f} min")
    gs, ws = [g for _, _, g in rows], [w for _, w, _ in rows]
    print(f"{want}: runs {len(rows)}; wall median {statistics.median(ws) / 60:.1f} min; "
          f"W1 gain median {statistics.median(gs) / 60:.1f} min, "
          f"min {min(gs) / 60:.1f}, max {max(gs) / 60:.1f}; runs gaining > 0: {sum(g > 0 for g in gs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
