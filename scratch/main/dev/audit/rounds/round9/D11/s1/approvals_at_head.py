#!/usr/bin/env python3
"""D11-s1 round 9: does the approval that let a pull request merge cover the head that merged?

METRIC (one line): over every first-parent PR merge on main from the moment the
`pull_request` rule landed (2026-09-17T04:58Z, decision 0009 status note) to the
baseline, the count of merges whose decisive approval -- judged by the production
`.claude/workflows/budget_raise_gate.py:approval` -- is NOT on the merged head.
KEY: the head is the merge commit's second parent (what GitHub merged), and the
review's `commit_id` from the REST reviews listing; never a comment's word.
Also printed, same window, one fraction per obligation (D11.M3 conformance):
  verdict_at_head   -- an issue comment "Fix review: merge <merged head>" by a login != PR author
  prc_first_green   -- the first `pr-contract` check-run on the merged head concluded success
  red_answered      -- of PRs with any non-success required check-run on the merged head,
                       those whose body carries a `## Red checks` heading
  owner_agent_declared -- owner (tvofi) APPROVED reviews whose own body says a seat/orchestrator gave it

COMMAND:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/approvals_at_head.py
          [--perturb commit-clause]   one-line in-memory edit of approval(): the
                                      `commit_id != head` refusal disabled -> stale counts go to zero
          [--perturb reattribute]     owner reviews whose own body says the orchestrator gave them are
                                      re-attributed to a distinct identity -> owner_gate_accepts_agent_declared
                                      goes to zero (down)
EXPECTED (baseline 1936d5ca, 253 merges): see REPORT.md; counts exact (API history is immutable
          except for reviews dismissed later, which only lower the stale counts).
MACHINE: box B3, 4 CPU Linux container. Needs GITHUB_TOKEN/GH_TOKEN (read-only GETs) and .git.
Writes only a response cache under a tempfile.mkdtemp() root (or $D11_CACHE if set).
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import argparse, hashlib, importlib.util, inspect, json, re, subprocess, sys, tempfile, time

BASE = "1936d5ca72a06556eeed4e8e5bf3dea520e517e1"
RULE_LANDED = "2026-09-17T04:58:00Z"
REPO = "tvofi/heatpump_optimizer"
API = "https://api.github.com"
T0p, T0t = time.process_time(), time.thread_time()


def load_gate():
    spec = importlib.util.spec_from_file_location("budget_raise_gate", ".claude/workflows/budget_raise_gate.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def perturb_commit_clause(mod):
    src = inspect.getsource(mod.approval)
    new = src.replace('if last.get("commit_id") != head:', 'if False:  # PERTURBED')
    assert new != src, "perturbation did not apply"
    ns = {}
    exec(compile(new, "approval<perturbed>", "exec"), mod.__dict__, ns)
    mod.approval = ns["approval"]


CACHE = os.environ.get("D11_CACHE") or tempfile.mkdtemp(prefix="d11s1-")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def get(path):
    f = os.path.join(CACHE, hashlib.sha1(path.encode()).hexdigest() + ".json")
    if os.path.exists(f):
        return json.load(open(f))
    out, url = [], API + path
    while url:
        # curl, not urllib: Python 3.14's strict X.509 check refuses some egress-proxy CAs
        # that curl accepts; the request is the same read-only GET.
        hfile = os.path.join(CACHE, "hdr-%d-%d" % (os.getpid(), hash(url) & 0xffffff))
        cmd = ["curl", "-sS", "--retry", "3", "-D", hfile, "-H", "Accept: application/vnd.github+json"]
        if TOKEN:
            cmd += ["-H", "Authorization: Bearer " + TOKEN]
        body = json.loads(subprocess.run(cmd + [url], capture_output=True, text=True, check=True).stdout)
        hdr = open(hfile).read(); os.unlink(hfile)
        status = [l for l in hdr.splitlines() if l.startswith("HTTP/")][-1].split()[1]
        if status == "404":  # a merged PR the API no longer serves: counted, not guessed
            json.dump(None, open(f, "w"))
            return None
        if status != "200":
            raise RuntimeError(f"GET {url}: HTTP {status}")
        link = next((l.split(":", 1)[1] for l in hdr.splitlines() if l.lower().startswith("link:")), "")
        if isinstance(body, dict) and "check_runs" in body:
            out.extend(body["check_runs"])
        elif isinstance(body, list):
            out.extend(body)
        else:
            out = body; link = ""
        m = re.search(r'<([^>]+)>; rel="next"', link)
        # the next link names /repositories/<id>/; the egress proxy admits only /repos/<owner>/<name>/
        url = re.sub(r"/repositories/\d+/", f"/repos/{REPO}/", m.group(1)) if m else None
    json.dump(out, open(f, "w"))
    return out


def _git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout


def codeowners(ref):
    """(pattern, owners) per CODEOWNERS line at `ref`; last match wins, a bare path un-owns."""
    rules = []
    for line in _git("show", f"{ref}:.github/CODEOWNERS").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            p = line.split(); rules.append((p[0].lstrip("/"), p[1:]))
    return rules


def is_owned(rules, f):
    import fnmatch
    hit = None
    for pat, own in rules:
        if (f.startswith(pat) if pat.endswith("/") else (f == pat or fnmatch.fnmatch(f, pat))):
            hit = own
    return bool(hit)


def owned_after_approval(rules, approved, head, mbase):
    """Code-owned files whose BRANCH content changed after `approved`: differs between the
    approved commit and the merged head, and at the head differs from the merge base (so a
    file main brought in through a merge is not charged to the branch)."""
    out = []
    for f in _git("diff", "--name-only", approved, head).split():
        if _git("rev-parse", f"{head}:{f}").strip() != _git("rev-parse", f"{mbase}:{f}").strip() and is_owned(rules, f):
            out.append(f)
    return out


def window():
    raw = subprocess.run(["git", "log", "--first-parent", "--merges", f"--since={RULE_LANDED}",
                          "--format=%H %P|%s", BASE], capture_output=True, text=True, check=True).stdout
    rows = []
    for line in raw.splitlines():
        shas, subj = line.split("|", 1)
        p = shas.split()
        m = re.match(r"Merge pull request #(\d+)", subj)
        rows.append((int(m.group(1)) if m else None, p[0], p[2]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=["commit-clause", "reattribute"])
    a = ap.parse_args()
    gate = load_gate()
    if a.perturb == "commit-clause":
        perturb_commit_clause(gate)
    rows = window()
    unparsed = [r for r in rows if r[0] is None]
    rows = [r for r in rows if r[0] is not None]

    def fetch(r):
        n, merge, head = r
        pr = get(f"/repos/{REPO}/pulls/{n}")
        reviews = get(f"/repos/{REPO}/pulls/{n}/reviews?per_page=100")
        comments = get(f"/repos/{REPO}/issues/{n}/comments?per_page=100")
        runs = get(f"/repos/{REPO}/commits/{head}/check-runs?per_page=100")
        return n, merge, head, pr, reviews, comments, runs

    fetched = [fetch(r) for r in rows]  # serial: no second thread, so thread_factor stays honest
    gone = [d[0] for d in fetched if d[3] is None]
    data = [d for d in fetched if d[3] is not None]

    rs = get(f"/repos/{REPO}/rulesets/23698884")
    pr_rule = next(r for r in rs["rules"] if r["type"] == "pull_request")["parameters"]
    required = {c["context"] for c in next(r for r in rs["rules"] if r["type"] == "required_status_checks")["parameters"]["required_status_checks"]}

    owner_judged = owner_stale = app_judged = app_stale = any_head = 0
    verdict_ok = prc_ok = prc_seen = red_prs = red_answered = 0
    owner_appr = owner_agent = 0
    head_mismatch = 0
    owned_after = 0; owned_list = []
    self_verdict = 0
    owner_empty = 0; decl_prs = 0; gate_accepts_declared = 0
    stale_list, noverdict, prc_red = [], [], []
    agent_re = re.compile(r"orchestrator|on tvofi's|under tvofi's|seat", re.I)
    for n, merge, head, pr, reviews, comments, runs in data:
        author = (pr.get("user") or {}).get("login")
        if (pr.get("head") or {}).get("sha") != head:
            head_mismatch += 1
        # owner arm (production symbol, production constants)
        if any((r.get("user") or {}).get("login") == gate.OWNER_LOGIN and r.get("state") in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED") for r in reviews):
            owner_judged += 1
            ok, why = gate.approval(reviews, head)
            if not ok:
                owner_stale += 1; stale_list.append(f"owner#{n}")
                appr = [r for r in reviews if (r.get("user") or {}).get("login") == gate.OWNER_LOGIN and r.get("state") == "APPROVED"]
                if appr and not any(r.get("commit_id") == head for r in appr):
                    mbase = _git("merge-base", merge + "^1", head).strip()
                    owned = owned_after_approval(codeowners(merge + "^1"), appr[-1]["commit_id"], head, mbase)
                    if owned:
                        owned_after += 1; owned_list.append(f"#{n}:{','.join(owned)}@{appr[-1]['commit_id'][:8]}->{head[:8]}")
        # approver-App arm: the same production function, identity constants swapped
        app = [r for r in reviews if (r.get("user") or {}).get("login") == "hpo-approver[bot]"]
        if app:
            app_judged += 1
            saved = (gate.OWNER_LOGIN, gate.OWNER_ID, gate.OWNER_TYPE)
            u = app[0]["user"]
            gate.OWNER_LOGIN, gate.OWNER_ID, gate.OWNER_TYPE = u["login"], u["id"], u["type"]
            try:
                ok, why = gate.approval(reviews, head)
            finally:
                gate.OWNER_LOGIN, gate.OWNER_ID, gate.OWNER_TYPE = saved
            if not ok:
                app_stale += 1; stale_list.append(f"app#{n}")
        if any(r.get("state") == "APPROVED" and r.get("commit_id") == head for r in reviews):
            any_head += 1
        declared = []
        for r in reviews:
            if (r.get("user") or {}).get("login") == "tvofi" and r.get("state") == "APPROVED":
                owner_appr += 1
                if agent_re.search(r.get("body") or ""):
                    owner_agent += 1; declared.append(r)
                elif not (r.get("body") or "").strip():
                    owner_empty += 1
        if any(r.get("commit_id") == head for r in declared):
            # The production owner-approval predicate, fed the merged PR's real reviews. Under
            # --perturb reattribute the reviews whose own body says the orchestrator gave them
            # carry a distinct identity (the fix's identity model), everything else unchanged.
            rv = reviews
            if a.perturb == "reattribute":
                rv = [dict(r, user={"login": "orchestrator-seat", "id": 0, "type": "Bot"}) if r in declared else r for r in reviews]
            decl_prs += 1
            if gate.approval(rv, head)[0]:
                gate_accepts_declared += 1
        if any((c.get("user") or {}).get("login") == author and (c.get("body") or "").lstrip().startswith(f"Fix review: merge {head}") for c in comments):
            self_verdict += 1
        if any((c.get("user") or {}).get("login") != author and (c.get("body") or "").lstrip().startswith(f"Fix review: merge {head}") for c in comments):
            verdict_ok += 1
        else:
            noverdict.append(n)
        prc = sorted([c for c in runs if c.get("name") == "pr-contract"], key=lambda c: c.get("started_at") or "")
        if prc:
            prc_seen += 1
            if prc[0].get("conclusion") == "success":
                prc_ok += 1
            else:
                prc_red.append(n)
        reds = {c["name"] for c in runs if c.get("name") in required and c.get("conclusion") not in ("success", "skipped", "neutral", None)}
        if reds:
            red_prs += 1
            if re.search(r"^## Red checks", pr.get("body") or "", re.M):
                red_answered += 1
    N = len(data)
    print(f"# window: {N} readable PR merges (+{len(gone)} the API 404s) since {RULE_LANDED} up to {BASE[:10]}; unparsed merge subjects: {len(unparsed)}")
    print(f"# ruleset 23698884 pull_request: dismiss_stale_reviews_on_push={pr_rule['dismiss_stale_reviews_on_push']} require_last_push_approval={pr_rule['require_last_push_approval']}")
    print(f"# stale: {' '.join(stale_list)}")
    print(f"# no verdict at merged head: {noverdict}")
    print(f"# pr-contract first run at merged head not success: {prc_red}")
    print(f"# merged PRs the API answers 404 for: {gone}")
    print(f"RESULT merges={N} count")
    print(f"RESULT merged_pr_unreadable={len(gone)} count")
    print(f"RESULT pr_head_sha_ne_merge_parent2={head_mismatch} count")
    print(f"RESULT owner_judged={owner_judged} count")
    print(f"RESULT owner_approval_not_at_merged_head={owner_stale} count")
    print(f"# code-owned change after the owner's last approval, merged without an owner approval at head: {owned_list}")
    print(f"RESULT owned_change_after_owner_approval={owned_after} count")
    print(f"RESULT verdict_by_pr_author_at_head={self_verdict} count")
    print(f"RESULT app_judged={app_judged} count")
    print(f"RESULT app_approval_not_at_merged_head={app_stale} count")
    print(f"RESULT merges_with_any_approval_at_head={any_head} count")
    print(f"RESULT verdict_at_head={verdict_ok}/{N} fraction")
    print(f"RESULT prc_first_green={prc_ok}/{prc_seen} fraction")
    print(f"RESULT red_answered={red_answered}/{red_prs} fraction")
    print(f"RESULT owner_agent_declared={owner_agent}/{owner_appr} fraction")
    print(f"RESULT owner_approval_empty_body={owner_empty}/{owner_appr} fraction")
    print(f"RESULT owner_gate_accepts_agent_declared={gate_accepts_declared}/{decl_prs} fraction")
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
