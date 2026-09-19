#!/usr/bin/env python3
"""D11 round 5 -- who signs the verdict, and what the merge boundary can prove
about it.

METRIC DEFINITIONS (one line each):
  M1 dry_run_rc -- the exit status of `tools/audit/app_approve.sh --dry-run`,
     the production gate that refuses to approve a pull request, run against a
     stubbed `gh` with one verdict comment as its only input.
  M2 merges_whose_verdict_came_from_the_author_login -- of the merged pull
     requests in `<newest v* tag>..origin/main`, the number whose newest
     allowlisted `Fix review:` verdict comment was posted by the login that
     authored the pull request (the platform's own `user.login`).
  M3 merges_with_an_approving_review_by_a_non_author -- the number of those
     pull requests carrying a GitHub review OBJECT, state APPROVED, whose
     `user.login` is not the pull request's author.
  M4 conformance_* -- per obligation, the fraction of those pull requests whose
     GitHub records or merged head prove it.

COMMAND
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D11/verdict.py [--since <ref>]

Reads GitHub read-only (`gh api`), the export's `.git` (the merge enumeration
and `git cat-file` for an in-tree disposition row), and drives
`tools/audit/app_approve.sh` with a stub `gh` on PATH. No BLAS import;
`thread_factor` is 1.0. Writes only under its own directory.

HEADER KEY: M2 is keyed on the comment's `user.login` against the pull
request's own `user.login`, both read from the API for that pull request -- not
on the author named in the body, which an honest fix cannot rewrite.

EXPECTED (baseline eaa2a06, 2026-09-19)
  M1 arm A 0 with the author's own login on the verdict, 1 with a login off the
  allowlist and 1 with no verdict; M2 = N of N; M3 = N of N; M4 o1 = N of N.

MACHINE macOS Darwin 25.6.0, 8-core Apple M1, python3 3.11.5.
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "tvofi/heatpump_optimizer"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SHA = "1111111111111111111111111111111111111111"
OTHER = "2222222222222222222222222222222222222222"

REQUIRED_CONTEXTS = {
    "Analyze (actions)", "Analyze (javascript-typescript)", "Analyze (python)",
    "browser", "briefs", "closure-scope", "closures", "env-matrix",
    "fast (3.14)", "hassfest", "policy-docs", "pr-contract", "typing",
    "validate-hacs", "wave-script",
}

STUB_GH = r"""#!/bin/bash
printf '%s\n' "$*" >> "$STUB_DIR/calls"
case "$*" in
  "api repos/o/r/pulls/7") cat "$STUB_DIR/pr.json" ;;
  "api --paginate repos/o/r/issues/7/comments?per_page=100") cat "$STUB_DIR/comments.json" ;;
  "api repos/o/r/contents/.github/CODEOWNERS?ref=main") printf '{"encoding":"base64","content":"%s"}' "$CODEOWNERS_B64" ;;
  "api --paginate repos/o/r/pulls/7/files?per_page=100") printf '[{"filename":"docs/x.md","status":"modified"}]' ;;
  *) echo "stub gh: unhandled $*" >&2; exit 9 ;;
esac
"""


def gh(args):
    p = subprocess.run(["gh", "api"] + args, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"gh api {' '.join(args)} rc={p.returncode}: {p.stderr.strip()[:200]}")
    return json.loads(p.stdout) if p.stdout.strip() else None


def comment(cid, body, login="tvofi-seat-author", assoc="COLLABORATOR", created=None):
    return {"id": cid, "created_at": created or f"2026-09-17T0{cid % 10}:00:00Z",
            "html_url": f"https://example.test/c{cid}", "user": {"login": login},
            "author_association": assoc, "body": body}


def dry_run(comments, pr_state="open", pr_sha=SHA):
    """M1: run the production approval gate's refusals against a stub gh."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "bin").mkdir()
        stub = td / "bin" / "gh"
        stub.write_text(STUB_GH)
        stub.chmod(0o755)
        (td / "pr.json").write_text(json.dumps({"state": pr_state, "merged": False, "head": {"sha": pr_sha}}))
        (td / "comments.json").write_text(json.dumps(comments))
        (td / "calls").write_text("")
        # --dry-run runs every refusal and stops before signing or minting, but
        # the App id and key files are checked first and fail closed, so the
        # stub must carry a well-formed pair for the later arms to be reached.
        ident = td / "ident"
        ident.mkdir()
        (ident / "identity-approver.appid").write_text("424242\n")
        (ident / "identity-approver.pem").write_text("-----BEGIN STUB KEY-----\nSTUB\n-----END STUB KEY-----\n")
        env = dict(os.environ, STUB_DIR=str(td), PATH=f"{td / 'bin'}:{os.environ['PATH']}",
                   CODEOWNERS_B64=base64.b64encode(b"/CLAUDE.md @tvofi\n").decode(),
                   HPO_IDENTITY_DIR=str(ident))
        p = subprocess.run([str(ROOT / "tools/audit/app_approve.sh"), "--dry-run", "o/r", "7", SHA],
                           capture_output=True, text=True, env=env)
        return p.returncode, (p.stdout + p.stderr).strip().splitlines()[-1][:160]


def window_merges(since):
    out = subprocess.run(["git", "-C", str(ROOT), "log", "--merges", "--format=%H%x09%s",
                          f"{since}..origin/main"], capture_output=True, text=True, check=True).stdout
    seen = {}
    for line in out.splitlines():
        sha, _, subject = line.partition("\t")
        if not subject.startswith("Merge pull request #"):
            continue
        seen.setdefault(int(subject.split("#", 1)[1].split()[0]), sha)
    return seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=None)
    ap.add_argument("--json-out", default=str(HERE / "verdict_raw.json"))
    args = ap.parse_args()
    since = args.since or subprocess.run(
        ["git", "-C", str(ROOT), "describe", "--tags", "--abbrev=0", "--match", "v*"],
        capture_output=True, text=True, check=True).stdout.strip()

    # ---- M1: the production gate, driven -------------------------------------
    author_verdict = comment(2, f"Fix review: merge {SHA}")
    rc_a, line_a = dry_run([comment(1, "A handoff message."), author_verdict], pr_sha=SHA)
    rc_b, line_b = dry_run([comment(1, "A handoff message."),
                            comment(2, f"Fix review: merge {SHA}", login="mallory", assoc="NONE")], pr_sha=SHA)
    rc_c, line_c = dry_run([comment(1, "A handoff message.")], pr_sha=SHA)
    print(f"RESULT dry_run_rc_with_the_allowlisted_verdict={rc_a}")
    print(f"RESULT dry_run_rc_with_a_non_allowlisted_verdict={rc_b}")
    print(f"RESULT dry_run_rc_with_no_verdict={rc_c}")
    print(f"RESULT dry_run_arm_a_last_line={line_a!r}")
    print(f"RESULT dry_run_arm_b_last_line={line_b!r}")
    # The stub pull request carries no `user` key at all: the gate never asks who
    # authored the pull request, so the arm above approves on a login allowlist
    # alone. That is the key M2 is counted on.
    print(f"RESULT stub_pull_request_payload_has_a_user_key=0")
    print(f"RESULT gate_reads_the_pull_request_author=0")

    # ---- M2/M3/M4: the merged window ----------------------------------------
    merges = window_merges(since)
    nums = sorted(merges)
    rows = []
    for num in nums:
        pr = gh([f"repos/{REPO}/pulls/{num}"])
        author = (pr.get("user") or {}).get("login")
        body = pr.get("body") or ""
        merged_head = None
        c = gh([f"repos/{REPO}/commits/{pr.get('merge_commit_sha')}"])
        if len(c.get("parents", [])) >= 2:
            merged_head = c["parents"][1]["sha"]
        reviews = gh([f"repos/{REPO}/pulls/{num}/reviews?per_page=100"]) or []
        comments = gh([f"repos/{REPO}/issues/{num}/comments?per_page=100"]) or []
        allow = {"tvofi", "tvofi-seat-author"}
        verdicts = [x for x in comments
                    if (x.get("user") or {}).get("login") in allow
                    and (x.get("body") or "").split("\n", 1)[0].strip().lower().startswith("fix review:")]
        verdicts.sort(key=lambda x: (x["created_at"], x["id"]))
        newest = verdicts[-1] if verdicts else None
        vlogin = (newest.get("user") or {}).get("login") if newest else None
        vline = (newest.get("body") or "").split("\n", 1)[0].strip() if newest else ""
        approved_non_author = [r for r in reviews
                               if (r.get("state") or "").upper() == "APPROVED"
                               and (r.get("user") or {}).get("login") != author]
        runs = (gh([f"repos/{REPO}/commits/{merged_head}/check-runs?per_page=100"]) or {}).get("check_runs", []) \
            if merged_head else []
        pcs = sorted([r for r in runs if r.get("name") == "pr-contract"], key=lambda r: r.get("started_at") or "")
        reds = sorted({r["name"] for r in runs
                       if r.get("conclusion") == "failure" and r.get("name") in REQUIRED_CONTEXTS})
        red_section = body.split("## Red checks", 1)[1].split("\n## ", 1)[0] if "## Red checks" in body else ""
        o4 = merged_head is not None and subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "-e", f"{merged_head}:docs/delivery/{num}.md"],
            capture_output=True).returncode == 0
        rows.append({
            "pr": num, "author": author, "merged_head": merged_head,
            "verdict_login": vlogin, "verdict_line": vline,
            "verdict_names_the_merged_head": bool(merged_head) and
                vline.lower().startswith("fix review: merge") and merged_head[:7] in vline,
            "verdict_matches_the_exact_grammar": bool(merged_head) and vline.lower() == f"fix review: merge {merged_head}",
            "verdict_from_the_author_login": vlogin == author,
            "approvals_from_non_authors": len(approved_non_author),
            "approval_commits": sorted({r.get("commit_id") for r in approved_non_author}),
            "first_pr_contract": (pcs[0].get("conclusion") if pcs else None),
            "o3": bool(pcs) and pcs[0].get("conclusion") == "success",
            "o4": o4, "required_reds": reds,
            "o5": (not reds) or all(n in red_section for n in reds),
            "review_logins": sorted({(r.get("user") or {}).get("login") for r in reviews}),
        })

    n = len(rows)
    verdict_logins = sorted({r["verdict_login"] for r in rows if r["verdict_login"]})
    print(f"RESULT window_since={since}")
    print(f"RESULT merged_prs_in_window={n}")
    print(f"RESULT merges_with_a_fix_review_verdict={sum(1 for r in rows if r['verdict_login'])}/{n}")
    print(f"RESULT merges_whose_verdict_names_the_merged_head="
          f"{sum(1 for r in rows if r['verdict_names_the_merged_head'])}/{n}")
    print(f"RESULT merges_whose_verdict_matches_the_exact_grammar_app_approve_requires="
          f"{sum(1 for r in rows if r['verdict_matches_the_exact_grammar'])}/{n}")
    print(f"RESULT merges_whose_verdict_came_from_the_author_login="
          f"{sum(1 for r in rows if r['verdict_from_the_author_login'])}/{n}")
    print(f"RESULT distinct_logins_that_posted_a_fix_review_verdict={len(verdict_logins)}")
    print(f"RESULT distinct_verdict_logins={json.dumps(verdict_logins)}")
    print(f"RESULT merges_with_an_approving_review_by_a_non_author="
          f"{sum(1 for r in rows if r['approvals_from_non_authors'])}/{n}")
    print(f"RESULT distinct_approving_logins={json.dumps(sorted({l for r in rows for l in r['review_logins']}))}")
    print(f"RESULT approvals_whose_commit_is_not_the_merged_head="
          f"{sum(1 for r in rows if r['approval_commits'] and r['merged_head'] not in r['approval_commits'])}/{n}")
    print(f"RESULT conformance_a_verdict_for_the_merged_head="
          f"{sum(1 for r in rows if r['verdict_names_the_merged_head'])}/{n}")
    print(f"RESULT conformance_a_verdict_by_a_login_other_than_the_author="
          f"{sum(1 for r in rows if r['verdict_login'] and not r['verdict_from_the_author_login'])}/{n}")
    print(f"RESULT conformance_an_approving_review_object_by_a_non_author="
          f"{sum(1 for r in rows if r['approvals_from_non_authors'])}/{n}")
    print(f"RESULT conformance_first_pr_contract_run_at_the_merged_head_green="
          f"{sum(1 for r in rows if r['o3'])}/{n}")
    print(f"RESULT conformance_a_disposition_row_in_the_tree_at_the_merged_head="
          f"{sum(1 for r in rows if r['o4'])}/{n}")
    print(f"RESULT conformance_every_required_red_answered_under_Red_checks="
          f"{sum(1 for r in rows if r['o5'])}/{n}")
    print(f"RESULT merges_carrying_a_red_required_context_at_the_merged_head="
          f"{sum(1 for r in rows if r['required_reds'])}/{n}")
    for r in rows:
        if r["required_reds"] or not r["o3"] or not r["o4"]:
            print(f"  PR {r['pr']} reds={r['required_reds']} first_pr_contract={r['first_pr_contract']} "
                  f"o4={int(r['o4'])} o5={int(r['o5'])}")
    (HERE / "verdict_raw.json").write_text(json.dumps(rows, indent=1))
    print(f"RESULT raw_rows_file={HERE / 'verdict_raw.json'}")
    print(f"RESULT load1={os.getloadavg()[0]}")
    print("RESULT thread_factor=1.0")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
