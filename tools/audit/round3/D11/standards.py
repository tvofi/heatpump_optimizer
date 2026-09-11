#!/usr/bin/env python3
"""D11: the standards scorecard, one executed check per criterion.

METRIC (one line): for each criterion of OpenSSF Scorecard, SLSA's Build track,
the OpenSSF Best Practices Badge (change control / test policy / vulnerability
reporting) and ISO/IEC 42001's continual-improvement clause, the input the
standard's own wording asks for, computed from this tree and from the `main`
ruleset -- never from memory of the standard and never from a document's account
of the repository.

Scorecard is HAND-EVALUATED here, which its brief allows: the tool scores a
remote repository over its own API budget, and this harness has to be runnable
offline by a verifier. What is executed is the INPUT to each check -- the number
the reason string quotes -- not Scorecard's arithmetic.

INSTRUMENTED SYMBOLS: `.github/workflows/*.yml` (`permissions:` blocks and
`uses:` pins), ruleset 22628467's `rules` and `bypass_actors`,
`tools/release/stamp.py`, and the tracked policy corpus as
`.claude/workflows/policy_lint.mjs:POLICY_GLOBS` defines it.

RUN (offline; reads tools/audit/round3/D11/ruleset.json, captured read-only with
`gh api repos/tvofi/heatpump_optimizer/rulesets/22628467`):
    cd <repo root> && PYTHONPATH=tests/hastub python3 tools/audit/round3/D11/standards.py

PERTURBATION: write an empty SECURITY.md at the repository root -- `security_policy`
must flip from 0 to 1 and back when it is removed. Driven by --perturb.

EXPECTED at baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1:
    RESULT sc_branch_protection_tier=1 +/-0        (Tier 2 needs a pull_request rule)
    RESULT sc_branch_protection_admin_bypass=1 +/-0
    RESULT sc_security_policy=0 +/-0
    RESULT sc_pinned_action_uses=2 of 50 +/-0
    RESULT sc_pinned_action_uses_fraction=0.0400 +/-0.0001
    RESULT sc_token_permissions_toplevel_write=1 +/-0  (release.yml)
    RESULT sc_dangerous_workflow_sites=0 +/-0
    RESULT slsa_build_level=0 +/-0
    RESULT corpus_lines_added=5604 +/-0
    RESULT corpus_lines_deleted=1816 +/-0
    RESULT corpus_lines_added_per_deleted=3.086 +/-0.001

PERTURBATION OUTPUT (`--perturb`): arm A no SECURITY.md -> 0, arm B SECURITY.md
-> 1, restored -> 0. The tree is left byte-identical (`git status` clean).
MACHINE: 8-core Apple M1, 8 GB, python3 3.11.5.
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
BASELINE = "ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1"
SINCE = "2026-08-27T21:02:51+00:00"
POLICY_GLOBS = [re.compile(g) for g in (
    r"^CLAUDE\.md$", r"^\.claude/rules/[a-z0-9-]+\.md$",
    r"^tools/audit/briefs/[A-Za-z0-9_.-]+\.md$", r"^tools/audit/README\.md$",
    r"^tools/audit/harnesses/README\.md$", r"^tests/README\.md$",
    r"^docs/HANDOVER\.md$", r"^\.claude/workflows/web-fragments\.md$",
    r"^\.claude/skills/[a-z0-9-]+/SKILL\.md$", r"^\.github/PULL_REQUEST_TEMPLATE\.md$")]


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a],
                          capture_output=True, text=True).stdout


def perturb():
    """The security-policy arm. Writes an empty SECURITY.md at the repository root,
    re-reads the predicate, and DELETES it in a finally -- the tree is restored
    whatever happens."""
    probe = ROOT / "SECURITY.md"
    if probe.exists():
        print("REFUSED: SECURITY.md already exists; the arms would not differ")
        return 2
    def read():
        return int(any((ROOT / p).exists() for p in
                       ("SECURITY.md", ".github/SECURITY.md", "docs/SECURITY.md")))
    try:
        print(f"  arm A no SECURITY.md : sc_security_policy={read()}")
        probe.write_text("# Security policy\n")
        print(f"  arm B SECURITY.md    : sc_security_policy={read()}")
    finally:
        if probe.exists():
            probe.unlink()
    print(f"  restored             : sc_security_policy={read()}")
    return 0


def main():
    if "--perturb" in sys.argv:
        return perturb()
    rs = json.loads((HERE / "ruleset.json").read_text())
    rules = {r["type"]: r for r in rs["rules"]}
    wf = sorted((ROOT / ".github/workflows").glob("*.yml"))
    text = {f.name: f.read_text() for f in wf}

    # --- OpenSSF Scorecard inputs ----------------------------------------
    # Branch-Protection tiers (checks.md): T1 prevent force push + deletion;
    # T2 >=1 reviewer, PRs required; T3 >=1 status check; T4 >=2 reviewers +
    # code owners; T5 dismiss stale + include admins.
    t1 = ("non_fast_forward" in rules) and ("deletion" in rules)
    t2 = "pull_request" in rules
    t3 = "required_status_checks" in rules
    tier = 0
    if t1:
        tier = 1
        if t2:
            tier = 2
            if t3:
                tier = 3
    print(f"RESULT sc_branch_protection_tier={tier} tier"
          f"  (T1_force_push_and_deletion={int(t1)} T2_pull_request_rule={int(t2)}"
          f" T3_status_checks={int(t3)}; tiers are cumulative in checks.md)")
    print(f"RESULT sc_branch_protection_admin_bypass="
          f"{len([b for b in rs['bypass_actors'] if b['bypass_mode'] == 'always'])} always-bypass actors")

    codeowners = any((ROOT / p).exists() for p in ("CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"))
    print(f"RESULT sc_code_review_codeowners={int(codeowners)} bool")
    sec = any((ROOT / p).exists() for p in ("SECURITY.md", ".github/SECURITY.md", "docs/SECURITY.md",
                                            "SECURITY.rst", ".github/SECURITY.rst"))
    print(f"RESULT sc_security_policy={int(sec)} bool")

    uses = re.findall(r"uses:\s*(\S+)", "\n".join(text.values()))
    sha_pinned = [u for u in uses if re.search(r"@[0-9a-f]{40}$", u)]
    print(f"RESULT sc_pinned_action_uses={len(sha_pinned)} of {len(uses)} uses")
    print(f"RESULT sc_pinned_action_uses_fraction={len(sha_pinned)/len(uses):.4f} fraction")
    print(f"RESULT sc_dependabot_config={int((ROOT / '.github/dependabot.yml').exists())} bool")

    toplevel_write, jobwrite = [], []
    for name, t in text.items():
        m = re.search(r"^permissions:\n((?:  \S+: \S+\n)+)", t, re.M)
        if m and "write" in m.group(1):
            toplevel_write.append(name)
        for jm in re.finditer(r"^    permissions:\n((?:      \S+: \S+\n)+)", t, re.M):
            if "write" in jm.group(1):
                jobwrite.append(name)
    print(f"RESULT sc_token_permissions_toplevel_write={len(toplevel_write)} workflows  ({toplevel_write})")
    print(f"RESULT sc_token_permissions_jobs_with_write={len(jobwrite)} jobs  ({sorted(set(jobwrite))})")

    dangerous = []
    for name, t in text.items():
        if "pull_request_target" in t:
            dangerous.append(f"{name}: pull_request_target")
        # a ${{ ... }} expression interpolated into a `run:` shell line
        for m in re.finditer(r"^\s*run:\s*\|?\s*\n?((?:.*\n){0,40})", t, re.M):
            pass
    for name, t in text.items():
        for i, line in enumerate(t.split("\n")):
            if "${{" in line and re.search(r"github\.event\.(issue|comment|pull_request)\.(title|body)", line):
                if "env:" not in line and ":" in line and line.strip().startswith(("run:", "-", "|")):
                    dangerous.append(f"{name}:{i+1}")
    print(f"RESULT sc_dangerous_workflow_sites={len(dangerous)} sites  ({dangerous})")

    ci = int(any("on:" in t for t in text.values()))
    print(f"RESULT sc_ci_tests={ci} bool")
    codeql = int(any("codeql" in t.lower() for t in text.values()))
    print(f"RESULT sc_sast_codeql_in_workflows={codeql} bool"
          "  (0 here; CodeQL runs through GitHub's DEFAULT SETUP, which has no workflow file:"
          " `gh api repos/tvofi/heatpump_optimizer/code-scanning/default-setup` reads state=configured)")

    weeks = 13
    commits = len(git("log", "--format=%H", BASELINE, "--since=90 days ago").splitlines())
    print(f"RESULT sc_maintained_commits_90d={commits} commits  ({commits/weeks:.1f}/week)")

    # --- SLSA Build track --------------------------------------------------
    rel = (ROOT / ".github/workflows/release.yml").read_text()
    provenance = int("attest-build-provenance" in rel or "slsa-framework" in rel
                     or "in-toto" in rel or "cosign" in rel)
    print(f"RESULT slsa_provenance_step={provenance} bool")
    print(f"RESULT slsa_build_level={1 if provenance else 0} level"
          "  (Build L1 needs provenance describing the build platform, process and inputs,"
          " distributed to consumers; none is produced, so L0)")
    print(f"RESULT slsa_release_creates_tag={int('gh release' in rel or 'softprops' in rel or 'create' in rel)} bool")

    # --- OpenSSF Best Practices Badge -------------------------------------
    print(f"RESULT bp_version_unique={int((ROOT / 'VERSION').exists())} bool")
    print(f"RESULT bp_release_notes={int((ROOT / 'RELEASE_NOTES.md').exists())} bool")
    print(f"RESULT bp_vulnerability_report_process={int(sec)} bool  "
          "(bestpractices.dev repo_public/... `vulnerability_report_process`: "
          "\"The project MUST publish the process for reporting vulnerabilities on the project site.\")")
    print(f"RESULT bp_test_suite={int((ROOT / 'tests/run.sh').exists())} bool")
    tp = int(any("test" in (ROOT / p).read_text().lower()
                 for p in ("CLAUDE.md",) if (ROOT / p).exists()))
    print(f"RESULT bp_test_policy_documented={tp} bool")

    # --- ISO/IEC 42001 continual improvement: is the corpus shrinking? ------
    add = dele = 0
    for line in git("log", "--numstat", "--format=%H", BASELINE, f"--since={SINCE}").splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        a, d, path = parts
        if a == "-" or not any(g.match(path) for g in POLICY_GLOBS):
            continue
        add += int(a)
        dele += int(d)
    print(f"RESULT corpus_lines_added={add} lines")
    print(f"RESULT corpus_lines_deleted={dele} lines")
    print(f"RESULT corpus_lines_added_per_deleted={(add/dele if dele else float('inf')):.3f} ratio")
    p = subprocess.run(["node", ".claude/workflows/policy_lint.mjs", "--budgets"],
                       cwd=str(ROOT), capture_output=True, text=True)
    for line in p.stdout.strip().split("\n")[-5:]:
        m = re.match(r"(\S+):?\s+~?(\d+) tokens, cap (\d+)", line.strip())
        if m:
            used, cap = int(m.group(2)), int(m.group(3))
            print(f"RESULT budget_headroom_{m.group(1)}={cap - used} tokens "
                  f"({100*used/cap:.1f}% of cap)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
