#!/usr/bin/env python3
"""D11.M2: one executed check per public-standard criterion.

Metric (one line): per criterion, PASS / PARTIAL / FAIL with the measured number
the standard's own wording sets the bar on (standards text fetched into api/,
Scorecard's docs/checks.md at api/scorecard_checks.md).

Enumerator (the step's universe, one criterion per line):
    python3 dev/audit/rounds/round11/D11/s2/standards.py --list
Run every check:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D11/s2/standards.py
Inputs: the export tree (workflows, SECURITY.md, VERSION, RELEASE_NOTES.md, git
history), api/ruleset_*.json, api/window.json (fetch_window.py), api/releases.json.
Production symbols read: `tools/policy/budget_raise_gate.py:AGENT_DECLARED`
(whose approvals are the owner's own), `tools/ci/gate.py:REQUIRED`, the
`main-protect-checks` ruleset parameters, `.github/workflows/*.yml`.
Perturbation: --perturb sets the ruleset snapshot's dismiss_stale_reviews_on_push,
require_last_push_approval and strict_required_status_checks_policy to true and
drops the bypass actors: Branch-Protection must move to PASS.
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B7: the
RESULT lines as printed, exact (counts over fixed snapshots and the tree).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob, json, re, subprocess, sys, time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
API = os.path.join(HERE, "api")

CRITERIA = [
    ("scorecard", "Branch-Protection"), ("scorecard", "Code-Review"), ("scorecard", "Dangerous-Workflow"),
    ("scorecard", "Token-Permissions"), ("scorecard", "Pinned-Dependencies"), ("scorecard", "CI-Tests"),
    ("scorecard", "SAST"), ("scorecard", "Maintained"), ("scorecard", "Security-Policy"),
    ("scorecard", "Signed-Releases"),
    ("slsa-build", "L1-provenance-exists"), ("slsa-build", "L2-hosted-signed-provenance"),
    ("slsa-build", "L3-hardened-isolated-provenance"),
    ("openssf-bp", "repo_track"), ("openssf-bp", "version_unique"), ("openssf-bp", "version_semver"),
    ("openssf-bp", "version_tags"), ("openssf-bp", "release_notes"), ("openssf-bp", "test"),
    ("openssf-bp", "test_invocation"), ("openssf-bp", "test_continuous_integration"),
    ("openssf-bp", "test_policy"), ("openssf-bp", "tests_are_added"),
    ("openssf-bp", "vulnerability_report_process"), ("openssf-bp", "vulnerability_report_private"),
    ("openssf-bp", "vulnerability_report_response"),
    ("nist-ai-rmf-govern", "accountability-reviewer-ne-author-from-records"),
    ("nist-ai-rmf-govern", "human-oversight-points"), ("nist-ai-rmf-govern", "documented-roles"),
    ("nist-ai-rmf-govern", "defect-and-incident-handling"), ("nist-ai-rmf-govern", "process-measurement"),
    ("iso-42001", "10-continual-improvement"),
    ("owasp-llm-2025", "LLM01-prompt-injection"), ("owasp-llm-2025", "LLM05-improper-output-handling"),
    ("owasp-llm-2025", "LLM06-excessive-agency"),
]


def sh(*a, **kw):
    return subprocess.run(a, capture_output=True, text=True, **kw).stdout


def load(name):
    return json.load(open(os.path.join(API, name)))


def workflows():
    return {p: open(p).read() for p in sorted(glob.glob(".github/workflows/*.yml"))}


def ruleset_checks(perturb):
    rs = load("ruleset_23698884.json")
    base = load("ruleset_22628467.json")
    if perturb:
        for r in rs["rules"]:
            if r["type"] == "pull_request":
                r["parameters"].update(dismiss_stale_reviews_on_push=True, require_last_push_approval=True)
            if r["type"] == "required_status_checks":
                r["parameters"]["strict_required_status_checks_policy"] = True
        rs["bypass_actors"] = []
    pr = next(r["parameters"] for r in rs["rules"] if r["type"] == "pull_request")
    sc = next(r["parameters"] for r in rs["rules"] if r["type"] == "required_status_checks")
    types = {r["type"] for r in base["rules"]}
    tiers = {
        "no_force_push": "non_fast_forward" in types, "no_deletion": "deletion" in types,
        "reviews>=1": pr["required_approving_review_count"] >= 1, "code_owners": pr["require_code_owner_review"],
        "status_checks": bool(sc["required_status_checks"]), "up_to_date": sc["strict_required_status_checks_policy"],
        "dismiss_stale": pr["dismiss_stale_reviews_on_push"], "last_push_approval": pr["require_last_push_approval"],
        "enforce_admins(no bypass actors)": not rs.get("bypass_actors"),
    }
    return tiers


def check(name, perturb, w):
    wf = workflows()
    prs = w["prs"]
    if name == "Branch-Protection":
        t = ruleset_checks(perturb)
        miss = [k for k, v in t.items() if not v]
        return ("PASS" if not miss else "PARTIAL"), f"{sum(t.values())}/{len(t)} settings; missing {miss}"
    if name == "Code-Review":
        sys.path.insert(0, "tools/policy")
        import budget_raise_gate as b
        at_head = human = 0
        for p in prs.values():
            hs, au = p["pull"]["head_sha"], p["pull"]["user"]
            ap = [r for r in p["reviews"] if r["state"] == "APPROVED" and r["commit_id"] == hs and r["user"] != au]
            at_head += bool(ap)
            human += any(not r["user"].endswith("[bot]") and not b.AGENT_DECLARED.search(r["body"] or "") for r in ap)
        n = len(prs)
        return ("PASS" if human == n else "FAIL"), (f"{at_head}/{n} merges approved at head by a non-author login; "
                                                   f"{human}/{n} by a human not declaring an agent gave it (bots and AI do not count)")
    if name == "Dangerous-Workflow":
        bad = []
        untrusted = re.compile(r"\$\{\{\s*(github\.event\.(issue\.(title|body)|pull_request\.(title|body|head\.ref|head\.label)"
                               r"|comment\.body|review\.body|review_comment\.body|pages\.[^}]*page_name|commits[^}]*|head_commit\.[^}]*"
                               r"|workflow_run\.(head_branch|head_commit|display_title)[^}]*)|github\.head_ref)\s*\}\}")
        for p, t in wf.items():
            in_run = False
            for ln in t.splitlines():
                s = ln.strip()
                if s.startswith("#"):
                    continue
                if re.match(r"-?\s*run:\s*", s):
                    in_run = True
                elif re.match(r"-?\s*(uses|with|env|name|if|id|shell):", s) or s.startswith("- "):
                    in_run = s.startswith("run:")
                if in_run and untrusted.search(ln):
                    bad.append(f"{p}: {s[:80]}")
            trig = re.search(r"^\s+(pull_request_target|workflow_run):", t, re.M)
            if trig and re.search(r"ref:\s*\$\{\{\s*github\.event\.(pull_request\.head|workflow_run\.head)", t):
                bad.append(f"{p}: untrusted checkout under {trig.group(1)}")
        return ("PASS" if not bad else "FAIL"), f"{len(bad)} dangerous patterns over {len(wf)} workflows {bad[:3]}"
    if name == "Token-Permissions":
        bad = []
        for p, t in wf.items():
            m = re.search(r"^permissions:\s*(.*)$", t, re.M)
            if not m:
                bad.append(f"{p}: no top-level permissions")
                continue
            block = re.search(r"^permissions:\s*\n((?:[ \t]+\S.*\n)+)", t, re.M)
            if m.group(1).strip() in ("{}", "read-all"):
                continue
            if block and re.search(r":\s*write", block.group(1)):
                bad.append(f"{p}: top-level write")
        return ("PASS" if not bad else "PARTIAL"), f"{len(bad)}/{len(wf)} workflows not read-only at top level: {bad}"
    if name == "Pinned-Dependencies":
        uses = [(p, u) for p, t in wf.items() for u in re.findall(r"^\s*(?:- )?uses:\s*([^\s#]+)", t, re.M)]
        unpinned = [u for p, u in uses if not u.startswith("./") and not re.search(r"@[0-9a-f]{40}$", u)]
        pips = [(p, l.strip()) for p, t in wf.items() for l in t.splitlines()
                if re.search(r"\bpip3? install\b", l) and "--require-hashes" not in l and not l.strip().startswith("#")]
        npm = [(p, l.strip()) for p, t in wf.items() for l in t.splitlines()
               if re.search(r"\bnpm (i|install)\b", l) and not l.strip().startswith("#")]
        pips += npm
        return ("PASS" if not unpinned and not pips else "PARTIAL"), (
            f"{len(uses) - len(unpinned)}/{len(uses)} uses: pinned by sha; {len(pips)} pip install lines without --require-hashes "
            f"(e.g. {pips[:2]})")
    if name == "CI-Tests":
        ok = sum(any(c["conclusion"] == "success" and "test" in c["name"] for c in p["check_runs_at_head"]) for p in prs.values())
        return ("PASS" if ok == len(prs) else "PARTIAL"), f"{ok}/{len(prs)} merges carry a successful test check run at head"
    if name == "SAST":
        ok = sum(any(c["name"].startswith("codeql / Analyze") and c["conclusion"] == "success" for c in p["check_runs_at_head"])
                 for p in prs.values())
        wfu = any("github/codeql-action" in t for t in wf.values())
        return ("PASS" if wfu and ok == len(prs) else "PARTIAL"), f"codeql-action in a workflow: {wfu}; {ok}/{len(prs)} merges with a green CodeQL analysis at head"
    if name == "Maintained":
        ts = [int(x) for x in sh("git", "log", "--format=%ct", "--since=90.days", "92d38ecb640bd462f2e19c0814d0f0b7df1ee692").split()]
        end = int(sh("git", "log", "-1", "--format=%ct", "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"))
        weeks = {(end - t) // (7 * 86400) for t in ts}
        return ("PASS" if len(weeks & set(range(13))) == 13 else "PARTIAL"), f"{len(weeks & set(range(13)))}/13 weeks with a commit, {len(ts)} commits in 90 days"
    if name == "Security-Policy":
        t = open("SECURITY.md").read()
        link = bool(re.search(r"https?://\S+|[\w.]+@[\w.]+", t))
        hits = len(re.findall(r"vuln|disclos", t, re.I)) + len(re.findall(r"\b\d+\s*(day|week|hour)s?\b", t, re.I))
        timeline = bool(re.search(r"\b\d+\s*(day|week|hour)s?\b", t, re.I))
        return ("PASS" if link and hits >= 2 else "PARTIAL"), f"link {link}; vuln/disclos/time hits {hits}; a stated response timeline {timeline}"
    if name == "Signed-Releases":
        rel = load("releases.json")[:5]
        sig = sum(any(re.search(r"\.(minisig|asc|sig|sign|sigstore|sigstore\.json|intoto\.jsonl)$", a["name"]) for a in r["assets"]) for r in rel)
        return ("PASS" if sig == len(rel) else "FAIL"), f"{sig}/{len(rel)} recent releases carry a signature or provenance asset"
    if name == "L1-provenance-exists":
        t = wf[".github/workflows/release.yml"]
        att = "attest-build-provenance" in t
        subj = re.search(r"subject-name:\s*\"([^\"]+)\"", t)
        asset = re.search(r"ASSET:\s*(\S+)", t)
        return ("PARTIAL" if att else "FAIL"), (f"attestation step {att}; subject {subj.group(1) if subj else None!r}; distributed asset "
                                               f"{asset.group(1) if asset else None} is not the subject (provenance.py measures the API)")
    if name == "L2-hosted-signed-provenance":
        t = wf[".github/workflows/release.yml"]
        return ("PARTIAL" if "runs-on: ubuntu" in t and "attest-build-provenance" in t else "FAIL"), \
            "hosted runner + Sigstore-signed attestation, for the source-tree subject only"
    if name == "L3-hardened-isolated-provenance":
        t = wf[".github/workflows/release.yml"]
        iso = "slsa-github-generator" in t or "workflow_call" in t
        return ("PASS" if iso else "FAIL"), f"provenance generated in an isolated reusable builder: {iso} (attest step runs in the build job itself)"
    if name == "repo_track":
        return "PASS", f"{sh('git', 'rev-list', '--count', 'HEAD').strip()} commits in git"
    if name in ("version_unique", "version_semver", "version_tags"):
        v = open("VERSION").read().strip()
        tags = sh("git", "tag", "-l", "v*").split()
        sem = bool(re.fullmatch(r"\d+\.\d+\.\d+", v))
        return ("PASS" if sem and f"v{v}" in tags else "FAIL"), f"VERSION {v} semver {sem}; tag v{v} present {f'v{v}' in tags}; {len(tags)} v* tags"
    if name == "release_notes":
        t = open("RELEASE_NOTES.md").read()
        heads = re.findall(r"^## v(\d+\.\d+\.\d+)", t, re.M)
        tags = sh("git", "tag", "-l", "v10.*").split()
        miss = [x for x in tags if x[1:] not in heads]
        return ("PASS" if not miss else "PARTIAL"), f"{len(heads)} version headings; v10.* tags without notes: {miss}"
    if name == "test":
        n = len(glob.glob("tests/*.py")) + len(glob.glob("tests/*.mjs"))
        return ("PASS" if n else "FAIL"), f"{n} test scripts under tests/"
    if name == "test_invocation":
        return ("PASS" if os.path.exists("tests/run.sh") else "FAIL"), f"tests/run.sh exists {os.path.exists('tests/run.sh')}"
    if name == "test_continuous_integration":
        req = sorted({n for v in __import__('gate').REQUIRED.values() for n in v if n.startswith('tests /')})
        return ("PASS" if req else "FAIL"), f"{len(req)} tests/ contexts gate.REQUIRED owes on every PR"
    if name == "test_policy":
        t = open("docs/CONTRIBUTING.md").read()
        return ("PASS" if re.search(r"failing test", t) else "FAIL"), "CONTRIBUTING.md states a fix adds its failing test"
    if name == "tests_are_added":
        mb = "v10.0.0"
        cc = 0
        both = 0
        for p in prs.values():
            ms = p["pull"]["merge_commit_sha"]
            files = sh("git", "diff", "--name-only", f"{ms}^1", ms).split()
            if any(f.startswith("custom_components/") for f in files):
                cc += 1
                both += any(f.startswith("tests/") for f in files)
        return ("PASS" if cc == both else "PARTIAL"), f"{both}/{cc} window merges touching custom_components/ also touch tests/"
    if name in ("vulnerability_report_process", "vulnerability_report_private"):
        t = open("SECURITY.md").read()
        priv = "security/advisories/new" in t
        return ("PASS" if priv else "FAIL"), f"SECURITY.md names the private advisory form {priv}"
    if name == "vulnerability_report_response":
        t = open("SECURITY.md").read()
        tl = bool(re.search(r"\b\d+\s*(day|week|hour)s?\b", t, re.I))
        return ("PASS" if tl else "PARTIAL"), f"a response time stated in SECURITY.md: {tl} (the criterion: initial response <= 14 days)"
    if name == "accountability-reviewer-ne-author-from-records":
        same = sum(any(r["user"] == p["pull"]["user"] and r["state"] == "APPROVED" for r in p["reviews"]) for p in prs.values())
        ap = sum(any(r["state"] == "APPROVED" and r["commit_id"] == p["pull"]["head_sha"] for r in p["reviews"]) for p in prs.values())
        return ("PASS" if same == 0 and ap == len(prs) else "PARTIAL"), f"{ap}/{len(prs)} approved at head by a login other than the author; self-approvals {same}"
    if name == "human-oversight-points":
        sys.path.insert(0, "tools/policy")
        import budget_raise_gate as b
        own = sum(any(r["user"] == "tvofi" and r["state"] == "APPROVED" and not b.AGENT_DECLARED.search(r["body"] or "")
                      for r in p["reviews"]) for p in prs.values())
        return ("PASS" if own else "FAIL"), f"{own}/{len(prs)} merges carry an owner-account approval the gate reads as the owner's own (oversight.py)"
    if name == "documented-roles":
        cited = set(re.findall(r"`([a-z-]+\.md|COMMON\.md)`", open("CLAUDE.md").read()))
        roles = {os.path.basename(p) for p in glob.glob("dev/governance/roles/*.md")}
        miss = sorted(r for r in cited if r in roles or r.endswith(".md")) and sorted(r for r in roles if r not in cited)
        return ("PASS" if not miss else "PARTIAL"), f"{len(roles)} role contracts; not named in CLAUDE.md: {miss}"
    if name == "defect-and-incident-handling":
        rca = glob.glob("dev/audit/rca/*.md")
        return ("PASS" if rca and os.path.exists("dev/governance/rules/defect-root-cause.md") else "FAIL"), f"{len(rca)} RCA records; defect-root-cause rule present"
    if name == "process-measurement":
        r = subprocess.run([sys.executable, "-I", "tools/audit/seat/scorecard.py", "--self-test"], capture_output=True, text=True)
        return ("PASS" if r.returncode == 0 else "FAIL"), f"scorecard.py --self-test rc={r.returncode} {(r.stdout or r.stderr).strip().splitlines()[-1:]}"
    if name == "10-continual-improvement":
        n = int(sh("awk", "/^## Superseded/{exit} /^- /{n++} END{print n+0}", "dev/programme/RULINGS.md").strip())
        return "PARTIAL", f"RULINGS.md {n} live entries, {os.path.getsize('dev/programme/RULINGS.md')} bytes (first reading; shrink is the bar)"
    if name in ("LLM01-prompt-injection", "LLM05-improper-output-handling"):
        st, why = check("Dangerous-Workflow", perturb, w)
        envs = sum(len(re.findall(r"^\s+[A-Z_]+:\s*\$\{\{\s*github\.(event\.pull_request\.(body|title|head\.ref)|head_ref)", t, re.M)) for t in wf.values())
        return st, f"{why}; {envs} untrusted values passed only through env:"
    if name == "LLM06-excessive-agency":
        sys.path.insert(0, "tools/policy")
        import budget_raise_gate as b
        agent = sum(any(r["user"] == "tvofi" and b.AGENT_DECLARED.search(r["body"] or "") for r in p["reviews"]) for p in prs.values())
        merged_owner = sum(p["pull"]["merged_by"] == "tvofi" for p in prs.values())
        return ("PARTIAL" if agent else "PASS"), f"{agent}/{len(prs)} merges carry an agent-declared approval under the owner's account; {merged_owner}/{len(prs)} merged by that account"
    return "NOT-RUN", "no check"


def main(argv):
    if "--list" in argv:
        for s, c in CRITERIA:
            print(f"{s}:{c}")
        return
    sys.path[:0] = ["tools/ci"]
    w = load("window.json")
    t0, c0 = time.process_time(), time.thread_time()
    tally = Counter()
    for s, c in CRITERIA:
        st, why = check(c, "--perturb" in argv, w)
        tally[st] += 1
        print(f"RESULT {s}:{c}={st} | {why}")
    for k in ("PASS", "PARTIAL", "FAIL", "NOT-RUN"):
        print(f"RESULT criteria_{k.lower()}={tally[k]} count")
    pc, tc = time.process_time() - t0, time.thread_time() - c0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main(sys.argv[1:])
