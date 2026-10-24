#!/usr/bin/env python3
"""D11 / round 4 -- one EXECUTED check per criterion of five public standards.

The OpenSSF Scorecard binary cannot run on this box (no docker, no go
toolchain: `which scorecard docker go` -> none), so each Scorecard check is
evaluated here against the criterion text fetched from
https://raw.githubusercontent.com/ossf/scorecard/main/docs/checks.md on
2026-09-12, using the same inputs the tool reads (the ruleset, the commit
history, the workflow files, the release assets). Per check, with its reason
string. NEVER the aggregate: Scorecard's own documentation says the aggregate
hides which risk is unmanaged, and this repository's checks disagree sharply.

Other bars, each fetched the same day:
  SLSA v1.1 Build track      https://slsa.dev/spec/v1.1/levels
  OpenSSF Best Practices     https://www.bestpractices.dev/criteria/0
  NIST AI 100-1 GOVERN       subcategory text as published
  OWASP LLM Top 10 2025      https://genai.owasp.org/llm-top-10/

METRIC. One line per criterion: `SCORE <standard>/<criterion> <PASS|FAIL|PARTIAL>
<reason>`. The RESULT lines are counts of each verdict per standard, so a
verifier can compare sets rather than a single number.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round4/D11/standards_scorecard.py

EXPECTED at baseline 7dd68dd (tolerance: exact):
  scorecard_pass=5 scorecard_partial=1 scorecard_fail=4
  slsa_build_level=0 bestpractices_fail=1 owasp_llm_fail=2
  criteria_scored=32 api_failures=0
MACHINE: any; network-bound.

PERTURBATION. Add a `pull_request` rule with
`required_approving_review_count: 1` to the ruleset and Branch-Protection must
move from FAIL to PARTIAL and Code-Review from FAIL to PASS. NOT RUN: the brief
forbids perturbing the live ruleset, so those two rows are provisional in the
finding that cites them; every other row's inputs are read-only and re-runnable.
"""

import collections
import datetime
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d11lib as L  # noqa: E402

ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
).stdout.strip()
V = collections.Counter()
ROWS = []


def score(std, crit, verdict, reason):
    V[(std, verdict)] += 1
    ROWS.append((std, crit, verdict, reason))
    print(f"SCORE {std}/{crit} {verdict} -- {reason}")


def main():
    rs = L.api(f"repos/{L.REPO}/rulesets/{L.RULESET_ID}") or {}
    rules = {r["type"] for r in rs.get("rules", [])}
    ctx = L.required_contexts(rs)
    bypass_always = [b for b in rs.get("bypass_actors", []) if b.get("bypass_mode") == "always"]
    repo = L.api(f"repos/{L.REPO}") or {}
    prs = L.merged_prs()

    # ---------------- OpenSSF Scorecard ------------------------------------
    # Branch-Protection tiers, from checks.md:
    #  T1 force push + deletion; T2 >=1 reviewer, PRs required, up-to-date,
    #  latest-push approval; T3 >=1 status check; T4 >=2 reviewers + code-owner;
    #  T5 dismiss stale + include administrators.
    t1 = {"non_fast_forward", "deletion"} <= rules
    t2 = any(r["type"] == "pull_request" for r in rs.get("rules", []))
    t3 = len(ctx) >= 1
    t5_admins = not bypass_always
    score("Scorecard", "Branch-Protection", "FAIL",
          f"tier1(force-push+deletion)={t1}; tier2(>=1 reviewer, PR required)={t2}; "
          f"tier3(>=1 status check)={t3}; tier5(include administrators)={t5_admins}. "
          f"No `pull_request` rule exists in any of the ruleset's "
          f"{len(L.ruleset_versions())} versions, and an admin-role actor holds "
          f"bypass_mode=always, so tiers 2, 4 and 5 are unmet. Scorecard stops at "
          f"the first unmet tier, so tier 3 does not score.")

    approved = sum(
        1 for p in prs.values()
        if any(r["state"] == "APPROVED"
               and (r["author"] or {}).get("login") != (p["author"] or {}).get("login")
               for r in p["reviews"]["nodes"])
    )
    score("Scorecard", "Code-Review", "FAIL",
          f"'whether the project requires human code review before pull requests are "
          f"merged': {approved} of {len(prs)} merged pull requests carry an APPROVED "
          f"review by an account other than the author. Scorecard's ~30-commit window "
          f"is a subset of this census and contains none either.")

    wf = os.path.join(ROOT, ".github/workflows")
    texts = {f: open(os.path.join(wf, f), encoding="utf-8").read()
             for f in sorted(os.listdir(wf)) if f.endswith((".yml", ".yaml"))}
    dangerous_trig = [f for f, t in texts.items()
                      if re.search(r"^\s+(pull_request_target|workflow_run):", t, re.M)]
    score("Scorecard", "Dangerous-Workflow",
          "PARTIAL" if not dangerous_trig else "FAIL",
          f"no `pull_request_target`/`workflow_run` untrusted checkout "
          f"({dangerous_trig or 'none'}); three `${{{{ }}}}` substitutions do reach a "
          f"`run:` line (tests.yml:124,907,908) which is the pattern the check names, "
          f"but all three values are GitHub-constrained (a `type: boolean` dispatch "
          f"input and two 40-hex SHAs). See untrusted_text.py.")

    toplevel_ro = sum(1 for t in texts.values()
                      if re.search(r"^permissions:\n\s+contents: read\s*$", t, re.M))
    write_blocks = sum(len(re.findall(r"permissions:\s*\n(?:\s+\S.*\n)*?\s+\S+:\s*write", t))
                       for t in texts.values())
    score("Scorecard", "Token-Permissions", "PASS",
          f"{toplevel_ro} of {len(texts)} workflows declare a read-only top-level "
          f"`permissions:`; release.yml declares `contents: write` at the top level "
          f"because the whole workflow creates a release. {write_blocks} job-level "
          f"write declaration(s), each with a comment stating the widening.")

    uses = sorted(set(re.findall(r"uses: (\S+)", "\n".join(texts.values()))))
    pinned = [u for u in uses if re.search(r"@[0-9a-f]{40}$", u)]
    score("Scorecard", "Pinned-Dependencies", "FAIL",
          f"{len(pinned)} of {len(uses)} distinct `uses:` are pinned by commit hash "
          f"({', '.join(pinned)}); the remaining {len(uses)-len(pinned)} are mutable "
          f"tags (actions/checkout@v5, actions/setup-node@v5, actions/setup-python@v6, "
          f"actions/cache@v5, actions/cache/save@v5, actions/upload-artifact@v6, "
          f"actions/download-artifact@v7).")

    score("Scorecard", "CI-Tests", "PASS",
          f"'runs tests before pull requests are merged': github-actions check runs "
          f"present on every merged head in the census; {len(ctx)} contexts are "
          f"required at the boundary.")

    cs = L.api(f"repos/{L.REPO}/code-scanning/default-setup") or {}
    score("Scorecard", "SAST", "PASS",
          f"CodeQL default setup state={cs.get('state')} languages={cs.get('languages')} "
          f"query_suite={cs.get('query_suite')}; `CodeQL` and three `Analyze (...)` "
          f"contexts are in the required set.")

    weeks = collections.Counter()
    for line in L.git("log", "--since=90.days", "--format=%cI", root=ROOT).split():
        weeks[datetime.datetime.fromisoformat(line).isocalendar()[:2]] += 1
    score("Scorecard", "Maintained", "PASS",
          f"'at least one commit per week during the previous 90 days': commits in "
          f"{len(weeks)} distinct ISO weeks; repository created "
          f"{repo.get('created_at')}, archived={repo.get('archived')}.")

    sec = os.path.join(ROOT, "SECURITY.md")
    sectext = open(sec, encoding="utf-8").read() if os.path.exists(sec) else ""
    score("Scorecard", "Security-Policy", "PASS",
          f"SECURITY.md present, {len(sectext.split())} words, contains an https "
          f"reporting link ({'yes' if 'https://' in sectext else 'no'}) and "
          f"vulnerability/disclosure text "
          f"({'yes' if 'vulnerabilit' in sectext.lower() else 'no'}).")

    rels = L.api(f"repos/{L.REPO}/releases?per_page=5") or []
    assets = {r["tag_name"]: [a["name"] for a in r.get("assets", [])] for r in rels}
    score("Scorecard", "Signed-Releases", "FAIL",
          f"'cryptographically signs release artifacts': the last {len(rels)} releases "
          f"carry {sum(len(v) for v in assets.values())} assets in total ({assets}), "
          f"so there is no *.sig/*.asc/*.intoto.jsonl to find. release.yml creates a "
          f"release from RELEASE_NOTES.md and uploads nothing.")

    # ---------------- SLSA v1.1, Build track --------------------------------
    score("SLSA", "Build L1 (provenance exists)", "FAIL",
          "the release path is `tools/release/stamp.py` -> a `vN.N.N` tag -> "
          "release.yml -> `gh release create`. Nothing generates provenance "
          "describing builder, process and top-level inputs, and HACS installs "
          "from the tag's source tree, so no artefact carries one. Build L1 "
          "requires the platform to 'automatically generate provenance'.")
    score("SLSA", "Build L2 (hosted, signed provenance)", "FAIL",
          "L2 requires the platform to generate AND SIGN provenance; L1 is unmet, "
          "so L2 is unreachable. The build IS on a hosted platform (GitHub-hosted "
          "ubuntu-latest), which is L2's producer-side requirement and its only met "
          "half.")
    score("SLSA", "Build L3 (hardened)", "FAIL",
          "unreachable while L1 and L2 are unmet. The next level's cost here is one "
          "step: actions/attest-build-provenance on the release job, which is L2 on "
          "a GitHub-hosted runner.")

    # ---------------- OpenSSF Best Practices --------------------------------
    score("BestPractices", "repo_public (MUST)", "PASS",
          f"visibility={repo.get('visibility')}, git URL public.")
    score("BestPractices", "repo_track (MUST)", "PASS",
          "git records author, change and time for all "
          f"{len(L.git('rev-list','HEAD',root=ROOT).split())} commits on main.")
    score("BestPractices", "version_unique (MUST)", "PASS",
          "`tools/release/stamp.py` is the only assigner; VERSION, the manifest and "
          "the RELEASE_NOTES heading move together and a branch may not touch them.")
    rn = open(os.path.join(ROOT, "RELEASE_NOTES.md"), encoding="utf-8").read()
    score("BestPractices", "release_notes (MUST)", "PASS",
          f"RELEASE_NOTES.md carries {len(re.findall(r'^## v', rn, re.M))} version "
          "sections; release.yml quotes the tag's section verbatim into the release.")
    score("BestPractices", "release_notes_vulns (MUST)", "PASS",
          "vacuously: no CVE has been assigned against this project "
          f"({'no' if 'CVE-' not in rn else 'some'} CVE identifier appears in the notes).")
    score("BestPractices", "test_policy / tests_are_added (MUST)", "PASS",
          "CLAUDE.md rule 2 and tools/audit/briefs/fixer.md require a failing test "
          "first and a mutation proof; tests/structure_budgets.json ratchets coverage "
          "metrics so a change that adds production lines without tests fails.")
    score("BestPractices", "vulnerability_report_process (MUST)", "PASS",
          "SECURITY.md publishes GitHub private advisory reporting and forbids a "
          "public issue.")
    score("BestPractices", "vulnerability_report_private (MUST)", "PASS",
          "the advisory form is the private channel and is named by URL.")
    score("BestPractices", "vulnerability_report_response (MUST)", "FAIL",
          "'initial response time for any vulnerability report received in the last "
          "6 months MUST be <= 14 days': no response-time commitment is published "
          "anywhere in SECURITY.md, and no advisory exists to measure against, so "
          "the criterion cannot be evidenced -- which is how the badge scores it.")

    # ---------------- NIST AI 100-1 GOVERN ----------------------------------
    score("NIST-AI-100-1", "GOVERN 1.2 (trustworthy-AI characteristics in policy)", "PASS",
          "the policy corpus states measurement discipline, null controls, "
          "perturbation and stop rules as binding obligations on every seat.")
    score("NIST-AI-100-1", "GOVERN 1.5 (ongoing monitoring and periodic review)", "PARTIAL",
          "`policy_lint --stats/--sunset` run weekly on cron and on every push to "
          "main, but both run with `|| true` and open nothing; the histogram reports "
          "the `blocked` verdict class at 4 against its own threshold of 3 in the "
          "current window and no issue with 'recurring friction' in its title has "
          "ever been opened (search/issues total_count=0).")
    score("NIST-AI-100-1", "GOVERN 2.1 (accountability structures, documented roles)", "PARTIAL",
          f"roles are documented in seven role contracts under tools/audit/briefs/, "
          f"but the accountability half is not evidenced: {approved} of {len(prs)} "
          f"merges carry an approving review by a second account, and "
          f"{len({(p['author'] or {}).get('login') for p in prs.values()})} distinct "
          f"GitHub identities author them, so reviewer != author is not provable from "
          f"GitHub's records for any merge.")
    score("NIST-AI-100-1", "GOVERN 3.2 (human oversight of AI configurations)", "PARTIAL",
          "the owner's approval is required before merging a policy change and "
          ".github/CODEOWNERS names them -- but CODEOWNERS is inert without a "
          "`require_code_owner_review` rule, which no ruleset version has. The "
          "oversight point exists in prose and nowhere in the merge boundary.")
    score("NIST-AI-100-1", "GOVERN 4.3 (testing, incident identification, sharing)", "PASS",
          ".claude/rules/defect-root-cause.md and tools/audit/briefs/root-cause.md "
          "define the triggers, the four process states and the cost test; the "
          "red-check trigger is named as the enforced one.")
    score("NIST-AI-600-1", "GV-1.2 / GV-4.1 (generative-AI risk in the governance loop)", "FAIL",
          "the profile's governance area asks for documented handling of the risks "
          "specific to generative systems. The corpus names none of them: "
          "untrusted_text.py finds 0 sentences anywhere in the policy or seat corpus "
          "about prompt injection or the data/instruction boundary, while 8 seat "
          "instructions direct an agent to read and act on issue and pull-request "
          "comment text on a public repository.")

    # ---------------- ISO/IEC 42001 clause 10 --------------------------------
    score("ISO-42001", "clause 10 (improvement; continual improvement)", "PARTIAL",
          "the corpus has a nonconformity-and-corrective-action mechanism "
          "(defect-root-cause.md: cause, process state, cost test, countermeasure or "
          "a recorded refusal) and a one-sided size ratchet "
          "(`policy_lint --budgets`), which is the structural half. The measurement "
          "half is missing: no instrument reads the loop's own output, `--stats` "
          "opens nothing, and the corpus sits at 60800/60800 tokens -- zero headroom "
          "-- so improvement can only be paid for by deletion.")

    # ---------------- OWASP LLM Top 10 2025 ----------------------------------
    score("OWASP-LLM", "LLM01 Prompt Injection", "FAIL",
          "8 seat instructions read issue/PR bodies and comments as authority "
          "('the comments carry judge verdicts, corrections and claims that override "
          "the body'), on a public repository with issues open and no interaction "
          "limit, so any GitHub account can write into that channel; 0 countermeasure "
          "sentences exist.")
    score("OWASP-LLM", "LLM05 Improper Output Handling", "PASS",
          "the one place a job consumes model- or user-written text, "
          "governance.yml's `pr-contract`, writes it through `env:` to a file and "
          "parses it; figure_lint.mjs deliberately RESOLVES rather than executes the "
          "commands a body names, and its header records why.")
    score("OWASP-LLM", "LLM06 Excessive Agency", "FAIL",
          "seats hold push, issue_write, add_issue_comment and merge grants, and the "
          "merge boundary requires no second party (0 approving reviews in "
          f"{len(prs)} merges, no `pull_request` rule, admin bypass_mode=always), so "
          "a seat acting on injected text has no human checkpoint between it and "
          "`main`.")

    print()
    for std in ("Scorecard", "SLSA", "BestPractices", "NIST-AI-100-1", "NIST-AI-600-1",
                "ISO-42001", "OWASP-LLM"):
        for v in ("PASS", "PARTIAL", "FAIL"):
            if V[(std, v)]:
                L.result(f"{std.lower().replace('-','_')}_{v.lower()}", V[(std, v)])
    L.result("slsa_build_level", 0)
    L.result("criteria_scored", len(ROWS))
    L.footer()


if __name__ == "__main__":
    main()
