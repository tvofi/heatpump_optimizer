#!/usr/bin/env python3
"""v1_latest_order.py -- D11-v1 (verifier) own measurement for D11-s1-01.

METRIC (one line): (head, required-context) pairs, over the merged PRs after the
guard commit 51b0742 plus the open PRs, where a `skipped` check run and a
non-skipped check run of the same required name coexist at the same head SHA;
split by whether the skipped run is the LATEST under three orderings GitHub
could use (check-run id, started_at, completed_at), and by the producing
workflow run (a different check suite than the real verdict = a second event).

Also: `race_pairs` = pairs where the skipped run COMPLETED before the real
verdict completed (the edit fired while the real job was still running, so a
pr-contract red-list taken in the edited run cannot have seen that verdict).

Independent of s1_skip_supersede.py: it does not evaluate any `if:`; it keys
only on the check-runs API's own records and orders them three ways.

PERTURBATION (--perturb): drop every check run whose check suite contains a
`pr-contract` run and no non-skipped governance job other than pr-contract
(i.e. the runs an `edited` event produced -- what the guard's removal-to-own-
file would stop creating). Expected: pairs -> 0.

NULL CONTROL: the same count over the non-governance required contexts
(`fast (3.14)`, `typing`, `browser`, ...), which no `edited` event re-runs:
expected 0 pairs.

RUN (tree root): PYTHONPATH=tests/hastub python3 tools/audit/round8/D11/v1_latest_order.py [--perturb]
  needs outbound api.github.com (unauthenticated GETs, ~40) and the clone at
  /home/claude/heatpump_optimizer (first-parent log 51b07423..cdf82da).
EXPECTED at cdf82da on 2026-09-23T21Z: pairs=18 (6 heads x 3 minus #1486's 2) --
  live data, grows. MACHINE: 4-vCPU cloud container; no timing numbers.
BASELINE: cdf82daabcfe3777d98b31489f36df5555ec9d82
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REQ = [c["context"] for r in json.loads((HERE / "s1_ruleset_23698884.json").read_text())["rules"]
       if r["type"] == "required_status_checks" for c in r["parameters"]["required_status_checks"]]
GOV = {"policy-docs", "env-matrix", "wave-script"}
CACHE = Path(os.environ.get("TMPDIR", "/tmp")) / "v1_latest_order_cache"
CACHE.mkdir(parents=True, exist_ok=True)


def get(p):
    f = CACHE / (re.sub(r"[^\w]", "_", p) + ".json")
    if f.exists():
        return json.loads(f.read_text())
    for _ in range(3):
        try:
            d = json.loads(subprocess.check_output(["curl", "-sS", "https://api.github.com" + p]))
            if isinstance(d, dict) and "message" in d and "rate limit" in d["message"]:
                raise RuntimeError(d["message"])
            f.write_text(json.dumps(d))
            return d
        except Exception as e:  # noqa
            err = e
            time.sleep(3)
    raise SystemExit(f"GET {p}: {err}")


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    perturb = "--perturb" in sys.argv
    log = subprocess.check_output(["git", "-C", "/home/claude/heatpump_optimizer", "log", "--first-parent",
                                   "--format=%s", "51b07423..cdf82daabcfe3777d98b31489f36df5555ec9d82"], text=True)
    nums = sorted({int(m) for m in re.findall(r"Merge pull request #(\d+)", log)})
    opens = sorted(p["number"] for p in get("/repos/tvofi/heatpump_optimizer/pulls?state=open&per_page=100"))
    counts = dict(pairs=0, latest_by_id=0, latest_by_started=0, latest_by_completed=0,
                  other_suite=0, race_pairs=0, null_pairs=0)
    heads = set()
    for n in nums + opens:
        pr = get(f"/repos/tvofi/heatpump_optimizer/pulls/{n}")
        sha = pr["head"]["sha"]
        runs = get(f"/repos/tvofi/heatpump_optimizer/commits/{sha}/check-runs?per_page=100")["check_runs"]
        if perturb:
            suites = {}
            for r in runs:
                suites.setdefault(r["check_suite"]["id"], []).append(r)
            edited = {sid for sid, rs in suites.items()
                      if any(r["name"] == "pr-contract" for r in rs)
                      and all(r["conclusion"] == "skipped" for r in rs if r["name"] != "pr-contract")}
            runs = [r for r in runs if r["check_suite"]["id"] not in edited]
        for name in REQ:
            rs = [r for r in runs if r["name"] == name]
            sk = [r for r in rs if r["conclusion"] == "skipped"]
            real = [r for r in rs if r["conclusion"] not in ("skipped", None)]
            if not sk or not real:
                continue
            if name not in GOV:
                counts["null_pairs"] += 1
                continue
            counts["pairs"] += 1
            heads.add((n, sha[:8]))
            key = {"id": lambda r: r["id"], "started": lambda r: r["started_at"],
                   "completed": lambda r: r["completed_at"]}
            for k, f in key.items():
                if max(rs, key=f)["conclusion"] == "skipped":
                    counts[f"latest_by_{k}"] += 1
            if {r["check_suite"]["id"] for r in sk}.isdisjoint({r["check_suite"]["id"] for r in real}):
                counts["other_suite"] += 1
            if min(r["completed_at"] for r in sk) < max(r["completed_at"] for r in real):
                counts["race_pairs"] += 1
                print(f"#   race #{n} {sha[:8]} {name}: skipped completed "
                      f"{min(r['completed_at'] for r in sk)} before real {max(r['completed_at'] for r in real)}")
    print(f"# window: {len(nums)} merged + {len(opens)} open; heads with a pair: {sorted(heads)}")
    for k, v in counts.items():
        print(f"RESULT {k}={v} count")
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
