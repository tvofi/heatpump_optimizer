#!/usr/bin/env python3
"""D11 round 5 seat b -- the policy corpus's size and direction, and merges
with no disposition row.

METRIC 1, corpus_churn_ratio: lines added per line deleted across the capped
policy corpus (the files named in .claude/workflows/policy_budgets.json
"files", the committed definition of the corpus) over the 30 days ending at
the baseline commit. git log --numstat is the counter; the ratio is the
direction of travel the one-sided caps exist to force.

METRIC 2, rowless_merges: merged pull requests with no disposition on any
surface policy_lint's DISPOSITION_FILES/ROW_DIR rules name -- no
docs/delivery/<N>.md, no `pull/<N>` anchor in docs/plan-2026-09-open-issues.md
or docs/HANDOVER.md -- counted over the merges of the last 14 days. Split into
past_interval (merge >= 12 commits before HEAD, past the batch interval
delivery_status.py allows) and pending.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D11/seat-b/corpus_churn.py

EXPECTED at baseline 1cc89e0: corpus_churn_ratio ~ 2.5-3.5 added/deleted
(tolerance: the ratio moves with any policy edit; the rowless counts are exact
against a frozen tree). rowless past_interval >= 13, pending = 4.

MACHINE: audit box (darwin, arm64); counts, not timing -- load1/thread_factor
quoted for the contract only.

PERTURBATION: add docs/delivery/1280.md with the anchor line
`- [#1280](https://github.com/tvofi/heatpump_optimizer/pull/1280)` -- under
it rowless_past_interval and the v6.6.7 tag-window rowless count fall by one
(down). The harness takes D11_SIM_ROW=<path to a one-row .md file> to count
that row exactly as the tree rule would, without touching the read-only tree;
the judge may instead make the real one-line edit and re-run bare.
"""

import os
import re
import subprocess
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True,
                          text=True, check=True).stdout


def corpus_files():
    import json
    with open(os.path.join(ROOT, ".claude/workflows/policy_budgets.json")) as f:
        return list(json.load(f)["files"].keys())


def churn(since):
    files = corpus_files()
    added = deleted = 0
    per_file = {}
    log = git("log", "--numstat", "--format=%H", f"--since={since}", "--", *files)
    cur = None
    for line in log.splitlines():
        if re.fullmatch(r"[0-9a-f]{40}", line.strip()):
            cur = line.strip()
            continue
        m = re.match(r"(\d+|-)\t(\d+|-)\t(.+)", line)
        if m and cur:
            a, d, path = m.group(1), m.group(2), m.group(3)
            if a != "-":
                added += int(a)
            if d != "-":
                deleted += int(d)
            if path in files:
                fa, fd = per_file.get(path, (0, 0))
                per_file[path] = (fa + (int(a) if a != "-" else 0),
                                  fd + (int(d) if d != "-" else 0))
    return added, deleted, per_file


def rowless():
    merges = git("log", "--merges", "--format=%H %s", "--since=2026-09-06")
    # Hook the production constants: the disposition surfaces are read out of
    # policy_lint.mjs itself (DISPOSITION_FILES / ROW_DIR), never carried.
    lint_src = open(os.path.join(ROOT, ".claude/workflows/policy_lint.mjs")).read()
    disp_files = re.search(r"const DISPOSITION_FILES = \[(.*?)\]", lint_src).group(1)
    disp_files = re.findall(r"'([^']+)'", disp_files)
    row_dir = re.search(r"const ROW_DIR = '([^']+)'", lint_src).group(1)
    rows_dir = os.path.join(ROOT, row_dir)
    have_row = set(os.listdir(rows_dir)) if os.path.isdir(rows_dir) else set()
    sim = os.environ.get("D11_SIM_ROW")  # perturbation: one extra row file
    if sim:
        m = re.search(r"pull/(\d+)\)", open(sim).read())
        if not m:
            sys.exit("D11_SIM_ROW file carries no `pull/<N>)` anchor")
        have_row.add(f"{m.group(1)}.md")
    disp_texts = [open(os.path.join(ROOT, p)).read() for p in disp_files]
    out = {"past_interval": [], "pending": []}
    for line in merges.splitlines():
        m = re.match(r"([0-9a-f]{40}) Merge pull request #(\d+)", line)
        if not m:
            continue  # non-PR merges (absorbs) carry no pull request number
        sha, pr = m.group(1), m.group(2)
        if f"{pr}.md" in have_row:
            continue
        if any(f"pull/{pr})" in t for t in disp_texts):
            continue
        since_n = int(git("rev-list", "--count", f"{sha}..HEAD").strip())
        out["pending" if since_n < 12 else "past_interval"].append((pr, since_n))
    return out


def tag_windows():
    """The record job's own window rule (governance.yml 'Choose the window'):
    <last v* tag>..origin/main. Each stamp therefore closes the window over
    whatever rowless merges sit inside it. Per v* tag: merges inside the
    window it closed, and how many of those have no disposition surface."""
    lint_src = open(os.path.join(ROOT, ".claude/workflows/policy_lint.mjs")).read()
    disp_files = re.findall(r"'([^']+)'", re.search(
        r"const DISPOSITION_FILES = \[(.*?)\]", lint_src).group(1))
    row_dir = re.search(r"const ROW_DIR = '([^']+)'", lint_src).group(1)
    rows_dir = os.path.join(ROOT, row_dir)
    have_row = set(os.listdir(rows_dir)) if os.path.isdir(rows_dir) else set()
    disp_texts = [open(os.path.join(ROOT, p)).read() for p in disp_files]
    sim = os.environ.get("D11_SIM_ROW")
    if sim:
        m = re.search(r"pull/(\d+)\)", open(sim).read())
        have_row.add(f"{m.group(1)}.md")
    tags = sorted(git("tag", "--list", "v*", "--sort=creatordate").splitlines(),
                  key=lambda t: git("show", "-s", "--format=%ct", t).strip())
    out = []
    for i, tag in enumerate(tags):
        prev = tags[i - 1] if i else None
        rng = f"{prev}..{tag}" if prev else f"{tag}"
        log = git("log", "--merges", "--format=%H %s", rng)
        prs = re.findall(r"Merge pull request #(\d+)", log)
        rowless = [p for p in prs
                   if f"{p}.md" not in have_row
                   and not any(f"pull/{p})" in t for t in disp_texts)]
        if prs:
            out.append((tag, len(prs), len(rowless),
                        ",".join(rowless) if rowless else "-"))
    return out[-6:]


def main():
    baseline = git("rev-parse", "HEAD").strip()
    print(f"# baseline {baseline}")
    added, deleted, per_file = churn("2026-08-21")
    ratio = round(added / deleted, 2) if deleted else float("inf")
    print(f"RESULT corpus_added={added} lines")
    print(f"RESULT corpus_deleted={deleted} lines")
    print(f"RESULT corpus_churn_ratio={ratio} added_per_deleted")
    worst = sorted(per_file.items(), key=lambda kv: kv[1][0] - kv[1][1], reverse=True)[:5]
    print("RESULT top_net_growth=" + "; ".join(
        f"{p}:{a}-{d}" for p, (a, d) in worst))
    r = rowless()
    print(f"RESULT rowless_past_interval={len(r['past_interval'])} merges")
    print(f"RESULT rowless_pending={len(r['pending'])} merges")
    print("RESULT rowless_prs=" + ",".join(pr for pr, _ in
          sorted(r["past_interval"], key=lambda x: -x[1])))
    for tag, n, bad, prs in tag_windows():
        print(f"RESULT tag_window {tag}: merges={n} rowless={bad} ({prs})")
    load1 = float(subprocess.run(["uptime"], capture_output=True, text=True)
                  .stdout.split()[-3].rstrip(","))
    tf = 1.0
    print(f"RESULT thread_factor={tf}")
    print(f"RESULT load1={load1}")
    print("counts only; no timing measured")


if __name__ == "__main__":
    main()
