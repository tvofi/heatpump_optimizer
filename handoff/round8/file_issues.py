#!/usr/bin/env python3
"""File the 38 round-8 audit issues as tvofi (run on the Mac, gh authenticated as tvofi).

Usage: python3 handoff/round8/file_issues.py [--dry-run]
Refuses unless `gh api user --jq .login` is tvofi. Creates the round-8 label if missing,
files every entry of issues.json in order (severity, then dimension), records id -> number in
issues-filed.json, then closes the claude[bot] copy #1511 as a duplicate of the tvofi D2-s2-01 issue.
Re-runnable: ids already in issues-filed.json are skipped.
"""
import json, subprocess, sys, pathlib
HERE = pathlib.Path(__file__).parent
REPO = "tvofi/heatpump_optimizer"
dry = "--dry-run" in sys.argv
def gh(*a, capture=True):
    r = subprocess.run(["gh", *a], text=True, capture_output=capture)
    if r.returncode: sys.exit(f"gh {' '.join(a[:3])} failed: {r.stderr.strip()}")
    return r.stdout.strip()
login = gh("api", "user", "--jq", ".login")
if login != "tvofi": sys.exit(f"refused: gh is authenticated as {login}, issues must be authored by tvofi")
labels = set(gh("label", "list", "-R", REPO, "--limit", "500", "--json", "name", "--jq", ".[].name").split("\n"))
if "round-8" not in labels and not dry:
    gh("label", "create", "round-8", "-R", REPO, "--description", "Audit round 8 (2026-09-23/24, baseline cdf82daa)", "--color", "5319e7")
out = HERE / "issues-filed.json"
done = json.loads(out.read_text()) if out.exists() else {}
for it in json.loads((HERE / "issues.json").read_text()):
    if it["id"] in done: continue
    if dry: print("would file", it["id"], it["labels"]); continue
    url = gh("issue", "create", "-R", REPO, "--title", it["title"], "--body", it["body"], *sum((["--label", l] for l in it["labels"]), []))
    done[it["id"]] = int(url.rsplit("/", 1)[1]); out.write_text(json.dumps(done, indent=1))
    print(it["id"], url)
if not dry and "D2-s2-01" in done:
    st = gh("issue", "view", "1511", "-R", REPO, "--json", "state", "--jq", ".state")
    if st == "OPEN":
        gh("issue", "close", "1511", "-R", REPO, "--reason", "not planned", "--comment",
           f"Filed by the wrong identity (claude[bot]); re-filed as tvofi in #{done['D2-s2-01']}.")
print(f"{len(done)} filed; map in {out}")
