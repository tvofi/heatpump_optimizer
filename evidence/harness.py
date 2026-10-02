#!/usr/bin/env python3
"""Reviewer's own harness for PR #1844 (not the fixer's).
Usage: harness.py <repo> <base> <head> [override_dir]
For every docs/delivery/<N>.md changed base...head (except the PR's own row):
  - base line must contain '**open**', head line must equal base with '**open**' -> '**merged** <sha8>'
  - gh says state MERGED and mergeCommit.oid startswith sha8
override_dir: files there replace head content (null control).
"""
import json, os, re, subprocess, sys
repo, base, head = sys.argv[1:4]
ovr = sys.argv[4] if len(sys.argv) > 4 else None
OWN = "1844"
def git(*a): return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True).stdout
mb = git("merge-base", base, head).strip()
names = git("diff", "--name-only", f"{mb}...{head}").split()
non_delivery = [n for n in names if not re.fullmatch(r"docs/delivery/\d+\.md", n)]
fails, ok = [], 0
rows = [n for n in names if n not in non_delivery and n != f"docs/delivery/{OWN}.md"]
cache = {}
for n in rows:
    pr = re.search(r"(\d+)\.md$", n).group(1)
    b = git("show", f"{mb}:{n}")
    h = git("show", f"{head}:{n}")
    if ovr and os.path.exists(os.path.join(ovr, f"{pr}.md")):
        h = open(os.path.join(ovr, f"{pr}.md")).read()
    m = re.search(r"\*\*merged\*\* ([0-9a-f]{8}),", h)
    if not m: fails.append(f"FAIL #{pr} shape: head row has no '**merged** <8hex>,'"); continue
    sha8 = m.group(1)
    if "**open**" not in b: fails.append(f"FAIL #{pr} base row had no **open**"); continue
    if b.replace("**open**", f"**merged** {sha8}", 1) != h:
        fails.append(f"FAIL #{pr} text: head is not base with only the state token rewritten"); continue
    if pr not in cache:
        r = subprocess.run(["gh", "pr", "view", pr, "-R", "tvofi/heatpump_optimizer", "--json", "state,mergeCommit"], capture_output=True, text=True)
        if r.returncode != 0: fails.append(f"FAIL #{pr} gh error rc={r.returncode}: {r.stderr.strip()[:120]}"); continue
        cache[pr] = json.loads(r.stdout)
    d = cache[pr]
    oid = (d.get("mergeCommit") or {}).get("oid") or ""
    if d["state"] != "MERGED": fails.append(f"FAIL #{pr} gh state {d['state']}"); continue
    if not oid.startswith(sha8): fails.append(f"FAIL #{pr} sha {sha8} != gh mergeCommit {oid}"); continue
    try: git("merge-base", "--is-ancestor", oid, base)
    except subprocess.CalledProcessError: fails.append(f"FAIL #{pr} merge commit {oid} not reachable from {base}"); continue
    ok += 1
    print(f"ok   #{pr} MERGED {oid}")
for f in fails: print(f)
own = git("show", f"{head}:docs/delivery/{OWN}.md") if f"docs/delivery/{OWN}.md" in names else ""
print(f"RESULT non_delivery_paths={len(non_delivery)} {non_delivery}")
print(f"RESULT own_row={'present' if own else 'absent'}: {own.strip()}")
print(f"RESULT rows_checked={len(rows)} ok={ok} failures={len(fails)} gh_calls={len(cache)}")
print(f"RESULT changed_set={' '.join('#'+re.search(r'(\d+)\.md$',n).group(1) for n in rows)}")
