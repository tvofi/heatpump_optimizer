import json, subprocess, sys, time

MAP = json.load(open("/tmp/issue-map.json"))
L = "/Users/timmalmstrom/hpo-orch/r10s3/lint-main"
WT = "/Users/timmalmstrom/hpo-seats/r10s3/roster-r10"
CO = "/Users/timmalmstrom/heatpump_optimizer"
ROSTER = "origin/handoff/audit-r10-roster"

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def refresh_lint():
    run(["git", "-C", L, "fetch", "-q", "origin", "main"])
    run(["git", "-C", L, "checkout", "-q", "--detach", "origin/main"])

def roster_issues():
    run(["git", "-C", WT, "fetch", "-q", "origin", "handoff/audit-r10-roster"])
    blob = run(["git", "-C", WT, "show", f"{ROSTER}:dev/programme/rosters/wave-r10-groups.json"]).stdout
    data = json.loads(blob)
    return {g["group"]: set((g.get("issues") or []) + (g.get("fixes") or [])) for g in data["groups"]}

done, failed = [], []
for g, n in MAP.items():
    for attempt in range(3):
        have = roster_issues()
        if n in have.get(g, set()):
            done.append((g, n)); break
        refresh_lint()
        r = run(["python3", "tools/audit/seat/roster_edit.py", "wire-issue", g, str(n),
                 "--checkout", CO, "--worktree", WT, "--lint-cwd", L, "--push"],
                cwd="/Users/timmalmstrom/hpo-seats/r10s3/orch-wt")
        if r.returncode == 0:
            done.append((g, n)); break
        tail = (r.stderr or r.stdout).strip().splitlines()[-1] if (r.stderr or r.stdout).strip() else ""
        print(f"{g}: attempt {attempt+1} failed: {tail[:120]}", flush=True)
        if "unpushed commits would be lost" in tail:
            run(["git", "-C", WT, "reset", "--hard", ROSTER])
        elif "uncommitted changes" in tail:
            run(["git", "-C", WT, "checkout", "--", "."])
        time.sleep(2)
    else:
        failed.append((g, n))
    print(f"{g} -> #{n}: {'wired' if (g, n) in done else 'FAILED'}", flush=True)

print(f"SUMMARY wired={len(done)} failed={len(failed)} {failed}", flush=True)
