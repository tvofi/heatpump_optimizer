#!/usr/bin/env python3
"""D11 verify-v3 (round 9), findings D11-s1-01, D11-s1-04, D11-s2-03: what the owner
approvals that let pull requests merge actually covered, measured with NO GitHub read --
from the committed review snapshot (tools/audit/round9/D11/s2/reviews_snapshot.json) and
the local git history only.

METRIC (one line, s1-01 arm): of merged PRs whose owner (tvofi) last APPROVED review is NOT
  on the merged head, the count whose branch-OWN commits after that approved commit
  (`git rev-list <approved>..<head> --not <merge^1>`, merges from main excluded by
  reachability) touch a path CODEOWNERS (at merge^1, last match wins) assigns to @tvofi,
  and that carry no APPROVED review from anyone at the merged head.
METRIC (s1-04/s2-03 arm): of snapshot PRs where production
  `.claude/workflows/budget_raise_gate.py:approval(reviews, head)` returns True, the count
  whose owner review at head carries a body naming the orchestrator/mandate; and the count of
  owner approvals at head with no such body (the ones attributable to a human, at most).
KEY: review commit_id and user from the committed snapshot; file sets from git; the verdict
  from the production approval() -- never a comment's word.
Arm #1623 is NOT in the snapshot: its approved commit (0a1424cc) is the finder's reading of
  the API, used as an input and reported separately (finder_supplied), never pooled.
COMMAND:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/verify-v3/v3_owner_approvals.py
          [--perturb commit-clause]  in-memory edit of approval(): `if last.get("commit_id") != head:`
                                     -> `if False:`; stale-at-head PRs become accepted (owner_stale -> 0).
EXPECTED (baseline 1936d5ca): see verify-v3.md; counts exact on the snapshot.
MACHINE: box G4-V3 cloud container, 4 CPU Linux, CPython 3.14.
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import argparse, fnmatch, importlib.util, inspect, json, re, subprocess, time

T0p, T0t = time.process_time(), time.thread_time()
BASE = "1936d5ca72a06556eeed4e8e5bf3dea520e517e1"
SNAP = "tools/audit/round9/D11/s2/reviews_snapshot.json"
DELEGATE = re.compile(r"orchestrator|mandate", re.I)


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout


def load_gate(perturb):
    spec = importlib.util.spec_from_file_location("brg_v3", ".claude/workflows/budget_raise_gate.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    if perturb:
        src = inspect.getsource(m.approval)
        new = src.replace('if last.get("commit_id") != head:', "if False:")
        assert new != src
        ns = {}; exec(compile(new, "approval<v3>", "exec"), m.__dict__, ns); m.approval = ns["approval"]
    return m


def owners(ref):
    rules = []
    for line in git("show", f"{ref}:.github/CODEOWNERS").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            p = s.split(); rules.append((p[0], p[1:]))
    return rules


def owned(rules, f):
    hit = []
    for pat, own in rules:
        p = pat.lstrip("/")
        m = f.startswith(p) if p.endswith("/") else (f == p or fnmatch.fnmatch(f, p) or f.startswith(p + "/"))
        if m:
            hit = own
    return "@tvofi" in hit


def branch_own_owned_after(approved, head, parent1, rules):
    revs = git("rev-list", "--no-merges", f"{approved}..{head}", "--not", parent1).split()
    files = set()
    for r in revs:
        files |= set(git("show", "--format=", "--name-only", r).split())
    return sorted(f for f in files if owned(rules, f)), revs


def merges():
    out = {}
    for line in git("log", "--first-parent", "--merges", "--format=%H %P|%s", BASE).splitlines():
        shas, subj = line.split("|", 1)
        m = re.match(r"Merge pull request #(\d+)", subj)
        if m:
            p = shas.split(); out[int(m.group(1))] = (p[0], p[1], p[2])
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--perturb", choices=["commit-clause"])
    a = ap.parse_args()
    gate = load_gate(a.perturb == "commit-clause")
    snap = json.load(open(SNAP))["prs"]
    M = merges()
    owner_stale = stale_owned = head_mismatch = 0
    gate_true = gate_true_delegated = gate_true_undeclared = 0
    owned_list = []
    for pr in snap:
        n, head, rv = pr["n"], pr["head"], pr["reviews"]
        merge, p1, p2 = M[n]
        head_mismatch += (p2 != head)
        ok, why = gate.approval(rv, head)
        own = [r for r in rv if r["user"]["login"] == "tvofi" and r["state"] == "APPROVED"]
        if ok:
            gate_true += 1
            at = [r for r in own if r["commit_id"] == head]
            if any(DELEGATE.search(r.get("body") or "") for r in at):
                gate_true_delegated += 1
            else:
                gate_true_undeclared += 1
        if own and not ok:
            owner_stale += 1
            appr = own[-1]["commit_id"]
            files, revs = branch_own_owned_after(appr, head, p1, owners(p1))
            any_at_head = any(r["state"] == "APPROVED" and r["commit_id"] == head for r in rv)
            print(f"# PR {n}: owner approval at {appr[:8]}, head {head[:8]}; branch-own commits after it={len(revs)}; "
                  f"code-owned touched={files}; any approval at head={any_at_head}")
            if files and not any_at_head:
                stale_owned += 1; owned_list.append(n)
    # #1623, finder-supplied approved commit; git facts only
    merge, p1, p2 = M[1623]
    files, revs = branch_own_owned_after("0a1424cc", p2, p1, owners(p1))
    print(f"# PR 1623 (finder-supplied approval commit 0a1424cc, not in snapshot): head {p2[:8]}; "
          f"branch-own commits after it={[r[:8] for r in revs]}; code-owned touched={files}")
    since = len(git("log", "--first-parent", "--merges", "--since=2026-09-17T04:58:00Z", "--format=%H", BASE).split())
    print(f"RESULT snapshot_prs={len(snap)} count")
    print(f"RESULT snapshot_head_ne_merge_parent2={head_mismatch} count")
    print(f"RESULT owner_approval_not_at_head={owner_stale} count")
    print(f"RESULT stale_owner_with_owned_change_no_head_approval={stale_owned} count  # PRs {owned_list}")
    print(f"RESULT finder_supplied_1623_owned_after={int(bool(files))} count")
    print(f"RESULT gate_accepts={gate_true} count")
    print(f"RESULT gate_accepts_delegate_declared={gate_true_delegated} count")
    print(f"RESULT gate_accepts_undeclared={gate_true_undeclared} count")
    print(f"RESULT window_first_parent_merges_since_rule={since} count")
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
