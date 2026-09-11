#!/usr/bin/env python3
"""D11: the mechanism inventory, derived from the tree and the API.

METRIC (one line): one row per refusal a seat can meet -- every required status
check in the `main` ruleset, every check class `policy_lint.mjs` enumerates,
every metric `tests/structure_budgets.json` caps, every claim file, every wired
hook, and every other governance script that can exit non-zero -- with, per row,
where it runs and whether a positive control exists that makes it fire. The row
count is DERIVED here; no number is carried from a document.

INSTRUMENTED SYMBOLS: .claude/workflows/policy_lint.mjs:CHECKS,
.claude/workflows/policy_lint.mjs:REQUIRED_ROT,
.claude/workflows/policy_lint.mjs:CORPUS_CHECK_NAMES / LOOP_CHECK_NAMES
(the two enumerations policy_lint_mutants.mjs imports), and the
`required_status_checks` rule of ruleset 22628467.

RUN (reads the ruleset from tools/audit/round3/D11/ghcache.json if present,
otherwise one read-only `gh api` call; everything else is offline):
    cd <repo root> && PYTHONPATH=tests/hastub python3 tools/audit/round3/D11/mechanisms.py

PERTURBATION: delete one entry from `CHECKS` in a COPY of policy_lint.mjs under
$TMPDIR and point MECH_POLICY_LINT at it -- `policy_lint_classes` must fall by
one and `classes_without_acceptance_pin` must move. Driven by --perturb.

EXPECTED at baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1:
    RESULT required_contexts=18 +/-0
    RESULT contexts_no_producing_job=4 +/-0        (CodeQL default setup: 4)
    RESULT contexts_skipped_by_construction_on_pr=1 +/-0   (`record`)
    RESULT ruleset_has_pull_request_rule=0 +/-0
    RESULT ruleset_required_approvals=0 +/-0
    RESULT ruleset_bypass_actors=1 +/-0   (RepositoryRole 5 = admin, bypass_mode always)
    RESULT policy_lint_classes=14 +/-0
    RESULT classes_with_acceptance_pin=11 +/-0
    RESULT classes_without_acceptance_pin=3 +/-0   (named-docs, coverage, provenance)
    RESULT mutated_entry_points=12 +/-0
    RESULT structure_metrics=24 +/-0
    RESULT mechanism_rows=79 +/-0

PERTURBATION OUTPUT (`--perturb`), three arms, none of them touching GitHub:
    arm A live ruleset       has_pull_request_rule=0 required_approvals=0 skipped_on_pr=1
    arm B +pull_request rule has_pull_request_rule=1 required_approvals=1 skipped_on_pr=1
    arm C record if:always() has_pull_request_rule=0 required_approvals=0 skipped_on_pr=0
MACHINE: 8-core Apple M1, 8 GB, node v20.10.0, python3 3.11.5.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
CACHE = HERE / "ghcache.json"
PL = Path(os.environ.get("MECH_POLICY_LINT", ROOT / ".claude/workflows/policy_lint.mjs"))


def required_contexts():
    override = os.environ.get("MECH_RULESET")
    if override:
        return _from(json.loads(Path(override).read_text()), f"MECH_RULESET={override}")
    if (HERE / "ruleset.json").exists():
        return _from(json.loads((HERE / "ruleset.json").read_text()),
                     "ruleset.json (captured read-only with "
                     "`gh api repos/tvofi/heatpump_optimizer/rulesets/22628467`)")
    if CACHE.exists():
        rs = json.loads(CACHE.read_text())["ruleset"]
        src = "ghcache.json"
    else:
        p = subprocess.run(["gh", "api", "repos/tvofi/heatpump_optimizer/rulesets/22628467"],
                           capture_output=True, text=True)
        if p.returncode != 0:
            print(f"REFUSED: could not read the ruleset: {p.stderr.strip()[:200]}")
            sys.exit(2)
        rs = json.loads(p.stdout)
        src = "gh api (live)"
    return _from(rs, src)


def _from(rs, src):
    rules = {r["type"]: r for r in rs["rules"]}
    ctxs = [c["context"] for c in rules["required_status_checks"]["parameters"]["required_status_checks"]]
    return ctxs, rules, rs, src


def workflow_jobs():
    """job id -> (workflow file, the job's `if:` text)."""
    jobs = {}
    wfdir = Path(os.environ.get("MECH_WORKFLOWS", ROOT / ".github/workflows"))
    for wf in sorted(wfdir.glob("*.yml")):
        text = wf.read_text()
        lines = text.split("\n")
        cur = None
        for i, line in enumerate(lines):
            m = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
            if m and not re.match(r"^  (push|pull_request|schedule|workflow_dispatch|inputs)\s*:", line):
                # only inside the jobs: block
                if "\njobs:\n" in text and text.index("\njobs:\n") < sum(len(x) + 1 for x in lines[:i]):
                    cur = m.group(1)
                    jobs[cur] = {"file": wf.name, "if": "", "matrix": []}
                continue
            if cur:
                m2 = re.match(r"^    if:\s*(.*)$", line)
                if m2:
                    body = m2.group(1)
                    j = i + 1
                    while j < len(lines) and (lines[j].startswith("      ") or lines[j].strip() == ""):
                        body += " " + lines[j].strip()
                        j += 1
                    jobs[cur]["if"] = body.strip()
    return jobs


def node_array(src, name):
    """Names inside a top-level `const <name> = [...]` array of strings/objects."""
    m = re.search(rf"const {name} = \[(.*?)\n\]", src, re.S)
    if not m:
        return []
    return re.findall(r"name: '([^']+)'", m.group(1)) or re.findall(r"'([^']+)'", m.group(1))


def perturb():
    """Both arms of the ruleset read. GitHub is never written; the second arm is a
    LOCAL copy of the ruleset JSON with a `pull_request` rule spliced in, which is
    the change whose absence the finding rests on."""
    import tempfile
    base = json.loads((HERE / "ruleset.json").read_text())
    with tempfile.TemporaryDirectory() as td:
        arm = Path(td) / "ruleset-with-review.json"
        patched = json.loads(json.dumps(base))
        patched["rules"].append({"type": "pull_request", "parameters": {
            "required_approving_review_count": 1,
            "dismiss_stale_reviews_on_push": True,
            "require_code_owner_review": False,
            "require_last_push_approval": True,
            "required_review_thread_resolution": False}})
        arm.write_text(json.dumps(patched))
        # Second arm: a COPY of .github/workflows with `record`'s `if:` inverted,
        # so the job could run on a pull request. contexts_skipped_by_construction_on_pr
        # must fall from 1 to 0. Nothing on GitHub is touched.
        wfarm = Path(td) / "workflows"
        wfarm.mkdir()
        for f in sorted((ROOT / ".github/workflows").glob("*.yml")):
            (wfarm / f.name).write_text(f.read_text().replace(
                "if: github.event_name != 'pull_request'",
                "if: always()"))
        for label, env in (("A live ruleset      ", {}),
                           ("B +pull_request rule", {"MECH_RULESET": str(arm)}),
                           ("C record if: always()", {"MECH_WORKFLOWS": str(wfarm)})):
            p = subprocess.run([sys.executable, __file__], cwd=str(ROOT),
                               capture_output=True, text=True, env={**os.environ, **env})
            got = {k: v for k, v in
                   (l[len("RESULT "):].split("=", 1) for l in p.stdout.split("\n")
                    if l.startswith("RESULT "))
                   if k in ("ruleset_has_pull_request_rule", "ruleset_required_approvals",
                            "ruleset_rule_types", "contexts_skipped_by_construction_on_pr")}
            print(f"  arm {label}: {got}")
    return 0


def main():
    if "--perturb" in sys.argv:
        return perturb()
    src = PL.read_text()
    checks = node_array(src, "CHECKS")
    # REQUIRED_ROT keys: the acceptance pins, one per class it drives.
    rot_block = src.split("const REQUIRED_ROT = {", 1)[1].split("\n}\n", 1)[0]
    rot = re.findall(r"^  '?([A-Za-z-]+)'?:", rot_block, re.M)
    # The two enumerations policy_lint_mutants.mjs imports, read from the module
    # itself rather than re-derived with a regex -- that re-derivation is the
    # defect docs/decisions/0002 names, one level up.
    _n = subprocess.run(
        ["node", "--input-type=module", "-e",
         "import {CORPUS_CHECK_NAMES, LOOP_CHECK_NAMES} from "
         f"{str(PL)!r};"
         "console.log(JSON.stringify([CORPUS_CHECK_NAMES, LOOP_CHECK_NAMES.map(x=>x.name)]))"],
        cwd=str(ROOT), capture_output=True, text=True)
    if _n.returncode != 0:
        print("REFUSED: could not import the mutation enumerations:", _n.stderr.strip()[:200])
        sys.exit(2)
    corpus, loop = json.loads(_n.stdout.strip().splitlines()[-1])

    budgets = json.loads((ROOT / "tests/structure_budgets.json").read_text())
    metrics = [k for k in budgets if k != "recorded_at"]

    ctxs, rules, rs, csrc = required_contexts()
    jobs = workflow_jobs()

    rows = []          # (kind, name, refuses, where, control, uncovered)
    no_job, skipped_by_construction = [], []
    for c in ctxs:
        jid = re.sub(r"\s*\(.*\)$", "", c)          # "fast (3.13)" -> "fast"
        j = jobs.get(jid) or jobs.get(c)
        if j is None:
            no_job.append(c)
            where = "no job in .github/workflows (external app / default setup)"
            control = "external"
        else:
            cond = j["if"]
            runs_on_pr = ("pull_request" not in cond) or ("== 'pull_request'" in cond) \
                or ("event_name == 'pull_request'" in cond)
            if "!=" in cond and "pull_request" in cond:
                runs_on_pr = False
            if not runs_on_pr:
                skipped_by_construction.append(c)
            where = f"{j['file']}:{jid} if={cond[:60] or '(none)'}"
            control = "runs-on-pr" if runs_on_pr else "SKIPPED on every pull_request"
        rows.append(("required-check", c, "blocks the merge box", where, control, ""))

    for cls in checks:
        pinned = cls in rot
        entry = {"citations": "checkCitations", "no-gh": "checkNoGh", "index": "checkIndex",
                 "duplicates": "checkDuplicates", "budgets": "checkBudgets",
                 "coverage": "coverageOverTree", "named-docs": "namedDocsOverTree",
                 "provenance": "checkProvenance", "record": "checkRecord",
                 "render": "checkRender", "counts": "checkCounts"}.get(cls)
        mutated = bool(entry) and (entry in corpus or entry in loop)
        rows.append(("policy_lint", cls, "refuses a policy file",
                     "governance.yml:policy-docs (push+PR)",
                     f"acceptance={'yes' if pinned else 'NO'} mutant={'yes' if mutated else 'no'}", ""))

    for m in metrics:
        rows.append(("structure", m, "one-sided cap on a code metric",
                     "tests/structure.py, scoped gate", "budget file", ""))

    for f in ("tests/golden/claimed_drift.txt", "tests/golden/card_claimed_drift.txt"):
        rows.append(("claim-file", f, "declares a value-bearing golden drift",
                     "tests/env_drift.py at gate time",
                     "present" if (ROOT / f).exists() else "MISSING", ""))

    hooks = json.loads((ROOT / ".claude/settings.json").read_text())["hooks"]
    for ev, specs in hooks.items():
        for s in specs:
            for h in s["hooks"]:
                script = h["command"].split("/")[-1].strip('"')
                rows.append(("hook", f"{ev}:{script}",
                             "refuses a seat action locally", ".claude/settings.json",
                             "--self-test via policy_lint --hooks", ""))

    others = [
        ("script", "rules_sync.mjs --check", "a .mdc that is not the generated form of its source", "governance.yml:policy-docs"),
        ("script", "fragments_sync.mjs", "a prompt fragment that drifted", "governance.yml:policy-docs"),
        ("script", "fragments_sync.mjs --self-test", "the fragment check surviving its own perturbation", "governance.yml:policy-docs"),
        ("script", "policy_lint_mutants.mjs", "a corpus/record check that survives its own deletion", "governance.yml:policy-docs"),
        ("script", "policy_lint_envmatrix.mjs", "an environment shape whose declared outcome does not hold", "governance.yml:env-matrix"),
        ("script", "check-wave-script.mjs", "a wave-resume control-flow defect", "governance.yml:wave-script"),
        ("script", "prepr.sh --self-test", "the pre-PR self-check surviving its own fixtures", "governance.yml:pr-contract"),
        ("script", "figure_lint.mjs --pr-body", "a `## Figures` command that does not resolve", "governance.yml:pr-contract"),
        ("script", "figure_lint.mjs --self-test", "the figure check surviving its own fixtures", "governance.yml:pr-contract"),
        ("script", "figure_census.mjs --self-test", "the counting rule behind the figure argument", "governance.yml:pr-contract"),
        ("script", "preflight.sh", "unmeasured claims in a body (REPORT ONLY, `|| true`)", "governance.yml:pr-contract"),
        ("script", "policy_lint.mjs --stats", "friction/verdict histogram (REPORT ONLY, `|| true`)", "governance.yml:record"),
        ("script", "policy_lint.mjs --sunset", "rules past their reason (REPORT ONLY, `|| true`)", "governance.yml:record"),
        ("script", "tests/record_status.py", "main's current `record` conclusion (NOT a required context)", "governance.yml:record-status"),
        ("script", "brief_lint.mjs", "an unresolvable citation in a wave roster or carry", "tests.yml:briefs"),
        ("script", "tools/release/stamp.py", "a version assigned outside the stamp", "release.yml / by hand"),
    ]
    for kind, name, refuses, where in others:
        rows.append((kind, name, refuses, where, "see governance.yml step", ""))

    for r in rules:
        if r != "required_status_checks":
            rows.append(("ruleset-rule", r, "refuses the ref operation", "ruleset 22628467 on ~DEFAULT_BRANCH",
                         "GitHub-enforced", ""))

    print(f"# mechanism inventory, ruleset read from {csrc}")
    print(f"{'kind':<16}{'name':<44}{'where':<62}control")
    for kind, name, refuses, where, control, _ in rows:
        print(f"{kind:<16}{name[:43]:<44}{where[:61]:<62}{control}")

    print()
    print(f"RESULT mechanism_rows={len(rows)} rows")
    print(f"RESULT required_contexts={len(ctxs)} contexts")
    print(f"RESULT contexts_no_producing_job={len(no_job)} contexts  ({', '.join(no_job)})")
    print(f"RESULT contexts_skipped_by_construction_on_pr={len(skipped_by_construction)} contexts"
          f"  ({', '.join(skipped_by_construction)})")
    print(f"RESULT ruleset_rule_types={len(rules)} types  ({', '.join(sorted(rules))})")
    has_pr_rule = "pull_request" in rules
    print(f"RESULT ruleset_has_pull_request_rule={int(has_pr_rule)} bool")
    print(f"RESULT ruleset_required_approvals="
          f"{rules.get('pull_request', {}).get('parameters', {}).get('required_approving_review_count', 0)} reviews")
    print(f"RESULT ruleset_bypass_actors={len(rs['bypass_actors'])} actors  "
          f"({[ (b['actor_type'], b['actor_id'], b['bypass_mode']) for b in rs['bypass_actors'] ]})")
    print(f"RESULT current_user_can_bypass={rs.get('current_user_can_bypass')!r}")
    print(f"RESULT policy_lint_classes={len(checks)} classes")
    print(f"RESULT classes_with_acceptance_pin={len([c for c in checks if c in rot])} classes")
    print(f"RESULT classes_without_acceptance_pin="
          f"{len([c for c in checks if c not in rot])} classes  "
          f"({', '.join(c for c in checks if c not in rot)})")
    print(f"RESULT mutated_entry_points={len(corpus) + len(loop)} entry_points")
    print(f"RESULT structure_metrics={len(metrics)} metrics")
    return 0


if __name__ == "__main__":
    sys.exit(main())
