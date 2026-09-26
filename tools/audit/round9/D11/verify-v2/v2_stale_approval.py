#!/usr/bin/env python3
"""D11 round 9, verifier V2 (independent) for D11-s1-01 (and the sample arm of D11-s1-04 / D11-s2-03).

No GitHub read: the reviews come from the snapshot D11-s2 committed
(tools/audit/round9/D11/s2/reviews_snapshot.json, a separate seat's API read of 12 merged
PRs), joined to local git history.

METRIC (one line, s1-01): of the snapshot's merged PRs, those whose merge on main's
  first-parent line had NO review in state APPROVED on the merged head (merge commit's
  2nd parent) while the owner's last APPROVED review -- still APPROVED, i.e. not
  dismissed by GitHub -- sits on an older commit, and a non-merge branch commit after
  that review (in approved..head, not reachable from the merge's 1st parent) touched a
  CODEOWNERS-owned path (my own last-match-wins matcher, CODEOWNERS read at parent 1).
METRIC (s1-04/s2-03 sample arm): PRs where budget_raise_gate.approval(reviews, head) is
  True and every owner APPROVED review at head declares in its body it was given by the
  orchestrator (regex 'orchestrator'); and owner APPROVED reviews with an empty body.
COMMAND: PYTHONPATH=tests/hastub python tools/audit/round9/D11/verify-v2/v2_stale_approval.py [--perturb dismiss-stale]
  --perturb dismiss-stale: model dismiss_stale_reviews_on_push=true on the snapshot: an
  APPROVED review whose commit is followed by a branch commit changing the diff becomes
  DISMISSED -> stale_owned_merges must fall to 0 (and such a PR is then unmergeable).
EXPECTED (baseline 1936d5ca, snapshot of 12): printed; counts exact.
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import argparse, copy, importlib.util, json, re, subprocess, time

T0p, T0t = time.process_time(), time.thread_time()
BASE = "1936d5ca72a06556eeed4e8e5bf3dea520e517e1"
SNAP = "tools/audit/round9/D11/s2/reviews_snapshot.json"


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout


def owners_at(ref):
    rules = []
    for line in git("show", f"{ref}:.github/CODEOWNERS").splitlines():
        s = line.split("#", 1)[0].strip()
        if s:
            p = s.split()
            rules.append((p[0], p[1:]))
    return rules


def owned(rules, path):
    own = []
    for pat, o in rules:
        anchored = pat.startswith("/")
        pat = pat.lstrip("/")
        if pat.endswith("/"):
            m = path.startswith(pat) if anchored else ("/" + pat) in ("/" + path)
        else:
            rx = "^" + re.escape(pat).replace(r"\*", "[^/]*") + "$"
            m = re.match(rx, path) is not None
        if m:
            own = o  # last match wins; a bare pattern un-owns
    return bool(own)


def merges():
    out = {}
    for line in git("log", "--first-parent", "--merges", "--format=%H %P|%s", BASE).splitlines():
        shas, subj = line.split("|", 1)
        m = re.match(r"Merge pull request #(\d+)\b", subj)
        if m:
            p = shas.split()
            out[int(m.group(1))] = (p[0], p[1], p[2])
    return out


def branch_owned_after(rules, approved, head, p1):
    files = set(git("log", "--no-merges", "--format=", "--name-only", f"{approved}..{head}", f"^{p1}").split())
    return sorted(f for f in files if owned(rules, f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=["dismiss-stale"])
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("brg", ".claude/workflows/budget_raise_gate.py")
    brg = importlib.util.module_from_spec(spec); spec.loader.exec_module(brg)
    prs = json.load(open(SNAP))["prs"]
    mg = merges()
    stale_owned = head_ok = accepted_declared = owner_appr = owner_empty = owner_decl = no_approval_at_head = 0
    for pr in prs:
        n = pr["n"]
        merge, p1, p2 = mg[n]
        assert p2 == pr["head"], f"#{n}: snapshot head != merge parent 2"
        head_ok += 1
        rv = copy.deepcopy(pr["reviews"])
        if a.perturb:
            for r in rv:
                if r["state"] == "APPROVED" and r["commit_id"] != p2 and \
                        git("log", "--no-merges", "--format=%h", f"{r['commit_id']}..{p2}", f"^{p1}").strip():
                    r["state"] = "DISMISSED"
        own_appr = [r for r in rv if r["user"]["login"] == brg.OWNER_LOGIN and r["state"] == "APPROVED"]
        for r in own_appr:
            owner_appr += 1
            b = (r.get("body") or "").strip()
            owner_empty += not b
            owner_decl += bool(re.search("orchestrator", b, re.I))
        any_head = any(r["state"] == "APPROVED" and r["commit_id"] == p2 for r in rv)
        no_approval_at_head += not any_head
        if own_appr and not any_head and own_appr[-1]["commit_id"] != p2:
            f = branch_owned_after(owners_at(p1), own_appr[-1]["commit_id"], p2, p1)
            if f:
                stale_owned += 1
                print(f"# #{n}: owner APPROVED {own_appr[-1]['commit_id'][:8]} (not dismissed), head {p2[:8]}, "
                      f"merged {merge[:8]} with no approval at head; branch changed owned {f}")
        at_head = [r for r in own_appr if r["commit_id"] == p2]
        if at_head and all(re.search("orchestrator", r.get("body") or "", re.I) for r in at_head) \
                and brg.approval(rv, p2)[0]:
            accepted_declared += 1
    print(f"RESULT snapshot_prs={len(prs)} count")
    print(f"RESULT snapshot_head_eq_merge_parent2={head_ok} count")
    print(f"RESULT merged_without_any_approval_at_head={no_approval_at_head} count")
    print(f"RESULT stale_owned_merges={stale_owned} count")
    print(f"RESULT owner_approved_reviews={owner_appr} count")
    print(f"RESULT owner_approved_declared_orchestrator={owner_decl} count")
    print(f"RESULT owner_approved_empty_body={owner_empty} count")
    print(f"RESULT gate_accepts_orchestrator_declared_at_head={accepted_declared} count")
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
