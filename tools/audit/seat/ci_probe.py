#!/usr/bin/env python3
"""ci_probe.py -- the writes a CI probe needs, one guarded subcommand each (R10-CI-LAYOUT P2a).

    python3 -I tools/audit/seat/ci_probe.py --repo tvofi/heatpump_optimizer --log FILE [--dry-run] <subcommand>
        push <ref> <sha>                    only refs/heads/ci-probe/*
        dispatch <workflow> --ref ci-probe/... [-f k=v]...
        rerun-job <job-id>
        cancel <run-id>
        label <pr> (--add|--remove) <name>
        retarget <pr> <base>
        close <pr>                          PATCH state=closed (the seat token is hpo-author's)
        review <pr> --approve --sha <sha>               owner account only
        dismiss-review <pr> <review-id> --message TEXT  owner account only
        sarif-upload <pr> --commit SHA --category CAT   an empty CodeQL SARIF to refs/pull/<pr>/merge
        dismiss-alert <n> --reason R [--comment TEXT]   a code-scanning alert, state=dismissed
        workflow-disable <workflow>                     PUT actions/workflows/<file or id>/disable
    python3 -I tools/audit/seat/ci_probe.py --self-test

WHY THIS EXISTS. The CI-layout probes (plans/ci-layout, P2) fan a unit out as a
pull request against a probe ref, then re-run, cancel and retarget it. Done by
hand the writes share no guard: one typo pushes a probe to a live namespace, and
a loop drains the API budget the gate needs. This is the one place they live.
sarif-upload, dismiss-alert and workflow-disable (P2b, U6) are the orchestrator's:
the first two are security-tool writes whose record is permanent (a SARIF on a
closed PR's merge ref, a dismissed alert), and the third is rollback write 21.
`sarif-upload` takes a token with `security-events: write` and writes no file the
caller names: the SARIF it sends is empty (no results), tool CodeQL, with
`automationDetails.id` = `<category>/`, so it supersedes nothing but the
analysis it is meant to outrank at that ref and category.

EVERY SUBCOMMAND, before it writes:
  - needs `--repo tvofi/heatpump_optimizer` spelled out, never a default;
  - reads /rate_limit and refuses below 20 % of the core limit remaining;
  - logs one line, `<utc> <subcommand> <target> <result>`, to --log (a dry run
    logs `dry-run`; the line never names a path on this host);
  - honours --dry-run, which prints the call and writes nothing.
Nothing here polls, so the 60 s floor on a GitHub poll (tvofi, 2026-10-19) holds
vacuously; a subcommand that gains a wait owes `MIN_POLL_S`.

THE NAMESPACE. `push` and `dispatch --ref` accept `ci-probe/<name>` (or the full
`refs/heads/` spelling) and refuse every other ref, `..` segments included: a
probe never moves `main`, `handoff/*` or `probe/*` (cloud_relay.sh owes the
latter). The ref and the log line go through ref_privacy.refusal. A `ci-probe/*`
ref is invisible to cloud_relay.sh's probe arm (it lists `probe/*`) and to
bus.sh orphans (it fetches main, handoff, handoff-body, fix); --self-test plants
one and compares both outputs, with a `probe/foo` null that cloud_relay reports.

A COMMIT is what git says it is: `push` and `review` take a SHA only when
`git rev-parse --verify <sha>^{commit}` prints exactly that SHA, so a short,
upper-case or unknown name refuses before any API write. `review` first fetches
`refs/pull/<pr>/head` when the commit is not local, and refuses if it still is not.

`review` and `dismiss-review` act as the OWNER (decision 6): the orchestrator
runs them, never an App, and the tool refuses when `gh api user` is not tvofi.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import datetime
import gzip
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ref_privacy  # noqa: E402  a ref or log line never names this host (#2310)

REPO = "tvofi/heatpump_optimizer"
OWNER = "tvofi"
PROBE_NS = "ci-probe/"
MIN_REMAINING = 0.20
MIN_POLL_S = 60
REF_RE = re.compile(r"^ci-probe/[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
CATEGORY_RE = re.compile(r"^/language:[a-z-]+$")
DISMISS_REASONS = ("false positive", "won't fix", "used in tests")


class Refuse(Exception):
    pass


def probe_ref(ref: str) -> str:
    """`ci-probe/x` for either spelling of a probe ref, or Refuse."""
    short = ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref
    if not REF_RE.match(short) or ".." in short or short.endswith((".lock", ".", "/")):
        raise Refuse(f"'{short}' is not a ci-probe/<name> ref; only {PROBE_NS}* may be written")
    return short


def gh_api(method: str, path: str, fields: dict | None = None) -> tuple[int, str]:
    """`gh api`, the seat token: (rc, stdout or stderr). JSON fields go as -F / --input."""
    cmd = ["gh", "api", "-X", method, path]
    body = json.dumps(fields) if fields is not None else None
    if body is not None:
        cmd += ["--input", "-"]
    r = subprocess.run(cmd, input=body, capture_output=True, text=True)
    return r.returncode, (r.stdout if r.returncode == 0 else r.stderr).strip()


def git_commit(sha: str) -> bool:
    """True when `sha` is the full name git gives a local commit -- git owns the SHA shape."""
    r = subprocess.run(["git", "rev-parse", "--verify", "--quiet", "--end-of-options", f"{sha}^{{commit}}"],
                       capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip() == sha


def git_fetch_pr(remote: str, pr: int) -> None:
    subprocess.run(["git", "fetch", "-q", remote, f"refs/pull/{pr}/head"], capture_output=True, text=True)


def git_push(remote: str, sha: str, ref: str) -> tuple[int, str]:
    r = subprocess.run(["git", "push", "-q", remote, f"{sha}:refs/heads/{ref}"],
                       capture_output=True, text=True)
    return r.returncode, r.stderr.strip()


class Probe:
    def __init__(self, repo: str, log: str, dry_run: bool, api=gh_api, push=git_push,
                 remote: str = "origin", now=None, commit=git_commit, fetch=git_fetch_pr):
        if repo != REPO:
            raise Refuse(f"--repo {REPO} is required, spelled out; got '{repo}'")
        if not log:
            raise Refuse("--log is required: one line per write")
        self.repo, self.log, self.dry, self.api, self.push = repo, log, dry_run, api, push
        self.remote, self.commit, self.fetch = remote, commit, fetch
        self.now = now or (lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%FT%TZ"))
        self.rate_ok = False

    def rate_check(self) -> None:
        """/rate_limit first; below 20 % remaining is a refusal, and so is a read that fails."""
        rc, out = self.api("GET", "/rate_limit")
        try:
            core = json.loads(out)["resources"]["core"]
            frac = core["remaining"] / core["limit"]
        except (ValueError, KeyError, TypeError, ZeroDivisionError):
            raise Refuse(f"could not read /rate_limit (rc {rc}); an unknown budget is not a full one")
        if frac < MIN_REMAINING:
            raise Refuse(f"rate limit {core['remaining']}/{core['limit']} is below "
                         f"{int(MIN_REMAINING * 100)} % remaining; resets at epoch {core.get('reset')}")

    def owner_check(self) -> None:
        rc, out = self.api("GET", "/user")
        try:
            login = json.loads(out)["login"]
        except (ValueError, KeyError, TypeError):
            raise Refuse("could not read the acting account; review runs as the owner only")
        if login != OWNER:
            raise Refuse(f"review acts as the owner ({OWNER}); this token is not")

    def record(self, sub: str, target: str, result: str) -> None:
        line = f"{self.now()} {sub} {target} {result}"
        why = ref_privacy.refusal("ci-probe/log", [("the log line", line)])
        if why:
            raise Refuse(f"the log line would publish this host: {why}")
        with open(self.log, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def write(self, sub: str, target: str, method: str, path: str, fields=None, owner=False) -> str:
        if not self.rate_ok:
            self.rate_check()
            self.rate_ok = True
        if owner:
            self.owner_check()
        if self.dry:
            print(f"dry-run: {method} {path} {json.dumps(fields) if fields else ''}".rstrip())
            self.record(sub, target, "dry-run")
            return "dry-run"
        rc, out = self.api(method, path, fields)
        result = "ok" if rc == 0 else f"FAILED rc={rc}"
        self.record(sub, target, result)
        if rc:
            raise Refuse(f"{sub} {target}: {out[:200]}")
        return result

    def r(self, tail: str) -> str:
        return f"/repos/{self.repo}/{tail}"

    # -- subcommands -------------------------------------------------------

    def do_push(self, ref: str, sha: str) -> str:
        short = probe_ref(ref)
        if not self.commit(sha):
            raise Refuse(f"'{sha}' is not the full SHA of a local commit (git rev-parse --verify)")
        why = ref_privacy.refusal(short)
        if why:
            raise Refuse(f"the push would publish this host: {why}")
        if not self.rate_ok:
            self.rate_check()
            self.rate_ok = True
        if self.dry:
            print(f"dry-run: git push {self.remote} {sha}:refs/heads/{short}")
            self.record("push", short, "dry-run")
            return "dry-run"
        rc, err = self.push(self.remote, sha, short)
        self.record("push", short, "ok" if rc == 0 else f"FAILED rc={rc}")
        if rc:
            raise Refuse(f"push {short}: {err[:200]}")
        return "ok"

    def do_dispatch(self, workflow: str, ref: str, inputs: dict) -> str:
        short = probe_ref(ref)
        if not re.match(r"^[A-Za-z0-9._-]+\.ya?ml$|^[0-9]+$", workflow):
            raise Refuse("workflow must be a file name or numeric id")
        return self.write("dispatch", f"{workflow}@{short}", "POST",
                          self.r(f"actions/workflows/{workflow}/dispatches"),
                          {"ref": short, "inputs": inputs})

    def do_rerun_job(self, job: str) -> str:
        return self.write("rerun-job", job, "POST", self.r(f"actions/jobs/{self.num(job)}/rerun"))

    def do_cancel(self, run: str) -> str:
        return self.write("cancel", run, "POST", self.r(f"actions/runs/{self.num(run)}/cancel"))

    def do_label(self, pr: str, add: str | None, remove: str | None) -> str:
        n = self.num(pr)
        if add:
            return self.write("label", f"#{n}+{add}", "POST", self.r(f"issues/{n}/labels"), {"labels": [add]})
        return self.write("label", f"#{n}-{remove}", "DELETE", self.r(f"issues/{n}/labels/{quote(remove, safe='')}"))

    def do_retarget(self, pr: str, base: str) -> str:
        return self.write("retarget", f"#{self.num(pr)}->{base}", "PATCH",
                          self.r(f"pulls/{self.num(pr)}"), {"base": base})

    def do_close(self, pr: str) -> str:
        return self.write("close", f"#{self.num(pr)}", "PATCH", self.r(f"pulls/{self.num(pr)}"),
                          {"state": "closed"})

    def do_review(self, pr: str, sha: str) -> str:
        if not self.commit(sha):
            self.fetch(self.remote, self.num(pr))
        if not self.commit(sha):
            raise Refuse(f"--sha '{sha}' is not the full SHA of a commit at refs/pull/{self.num(pr)}/head or "
                         "local: an approval names one tree")
        return self.write("review", f"#{self.num(pr)}@{sha[:12]}", "POST", self.r(f"pulls/{self.num(pr)}/reviews"),
                          {"event": "APPROVE", "commit_id": sha}, owner=True)

    def do_dismiss(self, pr: str, review: str, message: str) -> str:
        why = ref_privacy.body_refusal(message)
        if why:
            raise Refuse(f"the message would publish this host: {why}")
        return self.write("dismiss-review", f"#{self.num(pr)}/{self.num(review)}", "PUT",
                          self.r(f"pulls/{self.num(pr)}/reviews/{self.num(review)}/dismissals"),
                          {"message": message}, owner=True)

    def do_sarif_upload(self, pr: str, commit: str, category: str) -> str:
        if not SHA_RE.match(commit):
            raise Refuse(f"--commit '{commit}' is not a full lower-case SHA")
        if not CATEGORY_RE.match(category):
            raise Refuse(f"--category '{category}' is not /language:<name>")
        sarif = {"version": "2.1.0", "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
                 "runs": [{"tool": {"driver": {"name": "CodeQL"}}, "results": [],
                           "automationDetails": {"id": category + "/"}}]}
        packed = base64.b64encode(gzip.compress(json.dumps(sarif).encode())).decode()
        return self.write("sarif-upload", f"#{self.num(pr)}@{commit[:12]}{category}", "POST",
                          self.r("code-scanning/sarifs"),
                          {"commit_sha": commit, "ref": f"refs/pull/{self.num(pr)}/merge", "sarif": packed})

    def do_dismiss_alert(self, n: str, reason: str, comment: str) -> str:
        if reason not in DISMISS_REASONS:
            raise Refuse(f"--reason must be one of {', '.join(DISMISS_REASONS)}")
        why = ref_privacy.body_refusal(comment)
        if why:
            raise Refuse(f"the comment would publish this host: {why}")
        return self.write("dismiss-alert", f"alert {self.num(n)}", "PATCH",
                          self.r(f"code-scanning/alerts/{self.num(n)}"),
                          {"state": "dismissed", "dismissed_reason": reason, "dismissed_comment": comment})

    def do_workflow_disable(self, workflow: str) -> str:
        if not re.match(r"^[A-Za-z0-9._-]+\.ya?ml$|^[0-9]+$", workflow):
            raise Refuse("workflow must be a file name or numeric id")
        return self.write("workflow-disable", workflow, "PUT", self.r(f"actions/workflows/{workflow}/disable"))

    @staticmethod
    def num(v: str) -> int:
        if not re.fullmatch(r"[0-9]+", str(v)):
            raise Refuse(f"'{v}' is not a number")
        return int(v)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default="")
    ap.add_argument("--log", default="")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    sp = ap.add_subparsers(dest="sub")
    p = sp.add_parser("push"); p.add_argument("ref"); p.add_argument("sha")
    p = sp.add_parser("dispatch"); p.add_argument("workflow"); p.add_argument("--ref", required=True)
    p.add_argument("-f", action="append", default=[], metavar="k=v")
    sp.add_parser("rerun-job").add_argument("job")
    sp.add_parser("cancel").add_argument("run")
    p = sp.add_parser("label"); p.add_argument("pr")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--add"); g.add_argument("--remove")
    p = sp.add_parser("retarget"); p.add_argument("pr"); p.add_argument("base")
    sp.add_parser("close").add_argument("pr")
    p = sp.add_parser("review"); p.add_argument("pr"); p.add_argument("--approve", action="store_true", required=True)
    p.add_argument("--sha", required=True)
    p = sp.add_parser("dismiss-review"); p.add_argument("pr"); p.add_argument("review_id")
    p.add_argument("--message", required=True)
    p = sp.add_parser("sarif-upload"); p.add_argument("pr")
    p.add_argument("--commit", required=True); p.add_argument("--category", required=True)
    p = sp.add_parser("dismiss-alert"); p.add_argument("alert")
    p.add_argument("--reason", required=True); p.add_argument("--comment", default="")
    sp.add_parser("workflow-disable").add_argument("workflow")
    return ap


def run(a: argparse.Namespace, probe: Probe) -> str:
    s = a.sub
    if s == "push":
        return probe.do_push(a.ref, a.sha)
    if s == "dispatch":
        inputs = dict(kv.split("=", 1) for kv in a.f if "=" in kv)
        if len(inputs) != len(a.f):
            raise Refuse("-f takes k=v")
        return probe.do_dispatch(a.workflow, a.ref, inputs)
    if s == "rerun-job":
        return probe.do_rerun_job(a.job)
    if s == "cancel":
        return probe.do_cancel(a.run)
    if s == "label":
        return probe.do_label(a.pr, a.add, a.remove)
    if s == "retarget":
        return probe.do_retarget(a.pr, a.base)
    if s == "close":
        return probe.do_close(a.pr)
    if s == "review":
        return probe.do_review(a.pr, a.sha)
    if s == "sarif-upload":
        return probe.do_sarif_upload(a.pr, a.commit, a.category)
    if s == "dismiss-alert":
        return probe.do_dismiss_alert(a.alert, a.reason, a.comment)
    if s == "workflow-disable":
        return probe.do_workflow_disable(a.workflow)
    return probe.do_dismiss(a.pr, a.review_id, a.message)


def main(argv: list[str]) -> int:
    ap = build_parser()
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.sub:
        ap.print_usage(sys.stderr)
        return 2
    try:
        res = run(a, Probe(a.repo, a.log, a.dry_run, remote=a.remote))
    except Refuse as e:
        print(f"ci_probe: REFUSE: {e}", file=sys.stderr)
        return 2
    print(f"ci_probe: {a.sub} {res}")
    return 0


# ---------------------------------------------------------------------------
# self-test: fakes for the API, a throwaway bare remote for the push and for
# the cloud_relay.sh / bus.sh namespace control.

SELF_DIR = Path(__file__).resolve().parent
ROOT = SELF_DIR.parents[2]


class Fake:
    """An injected `gh api`: records every call, answers /rate_limit and /user."""

    def __init__(self, remaining=5000, limit=5000, login=OWNER, rc=0):
        self.calls, self.remaining, self.limit, self.login, self.rc = [], remaining, limit, login, rc

    def __call__(self, method, path, fields=None):
        if path == "/rate_limit":
            return 0, json.dumps({"resources": {"core": {"remaining": self.remaining, "limit": self.limit, "reset": 1}}})
        if path == "/user":
            return 0, json.dumps({"login": self.login})
        self.calls.append((method, path, fields))
        return self.rc, "" if self.rc == 0 else "boom"


def _git(cwd, *args, env=None):
    return subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=True).stdout


def self_test() -> int:
    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_init
    res: list[tuple[str, bool]] = []

    def ck(tag, cond):
        res.append((tag, bool(cond)))

    def refused(fn, *a, **k):
        try:
            fn(*a, **k)
        except Refuse as e:
            return str(e)
        return None

    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        log = str(t / "probe.log")
        sha = "a" * 40

        def mk(fake=None, dry=False):
            f = fake or Fake()
            return Probe(REPO, log, dry, api=f, push=lambda *x: (0, ""), commit=lambda s: s == sha), f

        # the explicit --repo
        ck("refuses a missing --repo", refused(Probe, "", log, False))
        ck("refuses another repo", refused(Probe, "tvofi/other", log, False))
        ck("refuses a missing --log", refused(Probe, REPO, "", False))

        # the rate-limit refusal, with its boundary and its null
        p, f = mk(Fake(remaining=999, limit=5000))
        ck("rate limit below 20 % refuses, and writes nothing", refused(p.do_close, "7") and not f.calls)
        p, f = mk(Fake(remaining=1000, limit=5000))
        ck("rate limit at 20 % proceeds (null control)", refused(p.do_close, "7") is None and len(f.calls) == 1)
        p, f = mk(Fake(limit=0))
        ck("an unreadable budget refuses", refused(p.do_close, "7") and not f.calls)

        # each subcommand's call
        p, f = mk()
        p.do_dispatch("tests.yml", "ci-probe/a", {"k": "v"})
        p.do_rerun_job("11"); p.do_cancel("12"); p.do_label("3", "x y", None); p.do_label("3", None, "x y")
        p.do_retarget("3", "ci-probe/base"); p.do_close("3")
        want = [("POST", f"/repos/{REPO}/actions/workflows/tests.yml/dispatches", {"ref": "ci-probe/a", "inputs": {"k": "v"}}),
                ("POST", f"/repos/{REPO}/actions/jobs/11/rerun", None),
                ("POST", f"/repos/{REPO}/actions/runs/12/cancel", None),
                ("POST", f"/repos/{REPO}/issues/3/labels", {"labels": ["x y"]}),
                ("DELETE", f"/repos/{REPO}/issues/3/labels/x%20y", None),
                ("PATCH", f"/repos/{REPO}/pulls/3", {"base": "ci-probe/base"}),
                ("PATCH", f"/repos/{REPO}/pulls/3", {"state": "closed"})]
        ck("each subcommand makes its one call", f.calls == want)
        ck("a non-numeric id is refused", refused(p.do_cancel, "1;rm") and refused(p.do_close, "x"))
        ck("dispatch refuses a non-probe ref", refused(p.do_dispatch, "tests.yml", "main", {}) and len(f.calls) == 7)

        # review runs as the owner only
        p, f = mk(Fake(login="hpo-author"))
        ck("review refuses a non-owner", refused(p.do_review, "3", sha) and not f.calls)
        ck("dismiss-review refuses a non-owner", refused(p.do_dismiss, "3", "9", "stale") and not f.calls)
        p, f = mk()
        p.do_review("3", sha); p.do_dismiss("3", "9", "stale head")
        ck("review and dismiss-review as the owner",
           f.calls == [("POST", f"/repos/{REPO}/pulls/3/reviews", {"event": "APPROVE", "commit_id": sha}),
                       ("PUT", f"/repos/{REPO}/pulls/3/reviews/9/dismissals", {"message": "stale head"})])
        ck("review refuses a short sha", refused(p.do_review, "3", "abc"))
        fetched, known = [], {sha}
        f = Fake()
        p = Probe(REPO, log, False, api=f, push=lambda *x: (0, ""), commit=known.__contains__,
                  fetch=lambda remote, pr: fetched.append((remote, pr)))
        ck("review of an unknown full sha fetches the PR head, then refuses before any API write",
           refused(p.do_review, "3", "b" * 40) and fetched == [("origin", 3)] and not f.calls)
        p.fetch = lambda remote, pr: (fetched.append((remote, pr)), known.add("c" * 40))
        ck("null: a head the fetch brings in is reviewed",
           refused(p.do_review, "3", "c" * 40) is None and f.calls[-1][2] == {"event": "APPROVE", "commit_id": "c" * 40})

        # sarif-upload, dismiss-alert, workflow-disable (P2b U6)
        p, f = mk()
        m = "b" * 40
        p.do_sarif_upload("9", m, "/language:python")
        sent = f.calls[-1]
        doc = json.loads(gzip.decompress(base64.b64decode(sent[2]["sarif"])))
        ck("sarif-upload posts an empty CodeQL SARIF for the category to the PR's merge ref",
           sent[:2] == ("POST", f"/repos/{REPO}/code-scanning/sarifs")
           and sent[2]["ref"] == "refs/pull/9/merge" and sent[2]["commit_sha"] == m
           and doc["runs"][0]["results"] == [] and doc["runs"][0]["tool"]["driver"]["name"] == "CodeQL"
           and doc["runs"][0]["automationDetails"]["id"] == "/language:python/")
        n0 = len(f.calls)
        ck("sarif-upload refuses a short commit, an upper-case commit, a non-language category and a non-number PR",
           all(refused(p.do_sarif_upload, *a) for a in (("9", "abc", "/language:python"), ("9", m.upper(), "/language:python"),
                                                       ("9", m, "python"), ("9", m, "/language:python/../x"), ("x", m, "/language:python")))
           and len(f.calls) == n0)
        p.do_dismiss_alert("7", "used in tests", "probe plant")
        ck("dismiss-alert PATCHes the alert dismissed with its reason",
           f.calls[-1] == ("PATCH", f"/repos/{REPO}/code-scanning/alerts/7",
                           {"state": "dismissed", "dismissed_reason": "used in tests", "dismissed_comment": "probe plant"}))
        n0 = len(f.calls)
        ck("dismiss-alert refuses an unlisted reason, a non-number and a host path in the comment",
           refused(p.do_dismiss_alert, "7", "because", "") and refused(p.do_dismiss_alert, "7;x", "used in tests", "")
           and refused(p.do_dismiss_alert, "7", "used in tests", "see /tmp/" + "claude-1000/x") and len(f.calls) == n0)
        p.do_workflow_disable("pr-contract-rerun.yml")
        ck("workflow-disable PUTs the workflow's disable endpoint",
           f.calls[-1] == ("PUT", f"/repos/{REPO}/actions/workflows/pr-contract-rerun.yml/disable", None))
        ck("workflow-disable refuses a path-shaped name",
           refused(p.do_workflow_disable, "../x.yml") and refused(p.do_workflow_disable, "a/b.yml"))
        for tag, call in (("sarif-upload", lambda q: q.do_sarif_upload("9", m, "/language:python")),
                          ("dismiss-alert", lambda q: q.do_dismiss_alert("7", "used in tests", "")),
                          ("workflow-disable", lambda q: q.do_workflow_disable("x.yml"))):
            q, g = mk(Fake(remaining=999, limit=5000))
            ck(f"{tag} refuses below 20 % rate limit and writes nothing", refused(call, q) and not g.calls)
            q, g = mk(dry=True)
            with contextlib.redirect_stdout(io.StringIO()):
                call(q)
            ck(f"{tag} --dry-run makes no write", not g.calls)
        logged = Path(log).read_text().splitlines()
        ck("each of the three logs one `ok` line for its write, and one `dry-run` line for its dry run",
           all(sum(bool(re.fullmatch(rf"\S+ {t} .+ {r}", ln)) for ln in logged) == 1
               for t in ("sarif-upload", "dismiss-alert", "workflow-disable") for r in ("ok", "dry-run")))

        # dry run and the log
        p, f = mk(dry=True)
        with contextlib.redirect_stdout(io.StringIO()):
            p.do_close("5"); p.do_cancel("6")
        ck("--dry-run makes no write", not f.calls)
        lines = Path(log).read_text().splitlines()
        p, f = mk()
        n0 = len(lines)
        p.do_close("5"); p.do_cancel("6")
        lines = Path(log).read_text().splitlines()
        ck("one log line per write: utc, subcommand, target, result",
           len(lines) - n0 == 2 and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ close #5 ok", lines[n0]))
        p, f = mk(Fake(rc=1))
        ck("a failed write is logged and refused", refused(p.do_close, "8") and "FAILED" in Path(log).read_text())
        ck("the log names no home directory", ref_privacy.refusal("ci-probe/log", [("log", Path(log).read_text())]) is None)
        ck("a session scratch path in a dismissal message is refused",
           refused(p.do_dismiss, "3", "9", "see /tmp/" + "claude-1000/x"))

        # the namespace guard, against a throwaway bare remote
        bare, work = t / "origin.git", t / "work"
        env = throwaway_git_init(bare, "-q", "--bare")
        env = throwaway_git_init(work, "-q", "-b", "main")
        _git(work, "commit", "-q", "--allow-empty", "-m", "base", env=env)
        _git(work, "remote", "add", "origin", str(bare), env=env)
        head = _git(work, "rev-parse", "HEAD", env=env).strip()
        _git(work, "push", "-q", "origin", "main", env=env)
        p = Probe(REPO, log, False, api=Fake(), remote="origin")
        cwd = os.getcwd()
        os.chdir(work)
        try:
            ck("push refuses a short sha", refused(p.do_push, "ci-probe/z", head[:12]))
            ck("push refuses an upper-case sha", refused(p.do_push, "ci-probe/z", head.upper()))
            f0 = len(p.api.calls)
            ck("push refuses an unknown full sha before any API write",
               refused(p.do_push, "ci-probe/z", "f" * 40) and len(p.api.calls) == f0 and not p.rate_ok)
            ck("null: an existing local commit passes git's check", git_commit(head))
            ck("push to ci-probe/x lands", refused(p.do_push, "ci-probe/x", head) is None)
            ck("push accepts the refs/heads/ spelling", refused(p.do_push, "refs/heads/ci-probe/y", head) is None)
            for bad in ("main", "probe/foo", "handoff/x", "ci-probe/", "ci-probe/../main", "refs/heads/main", "ci-probe", "xci-probe/a"):
                ck(f"push refuses {bad}", refused(p.do_push, bad, head))
        finally:
            os.chdir(cwd)
        heads = _git(bare, "for-each-ref", "--format=%(refname)", "refs/heads", env=env).split()
        ck("the remote holds main and the two probe refs only",
           sorted(heads) == ["refs/heads/ci-probe/x", "refs/heads/ci-probe/y", "refs/heads/main"])

        # the namespace control: cloud_relay.sh's probe arm and bus.sh orphans
        def relay():
            e = dict(env, HPO_STATE_DIR=str(t / "st"), HPO_BUS_STATE=str(t / "bus"), TMPDIR=str(t))
            r = subprocess.run(["bash", str(SELF_DIR / "cloud_relay.sh"), "--watch", "--once", "--log", str(t / "relay.log")],
                               cwd=work, env=e, capture_output=True, text=True)
            return r.returncode, r.stdout + r.stderr

        def orphans():
            e = dict(env, HPO_BUS_REMOTE="origin")
            r = subprocess.run(["bash", str(SELF_DIR / "bus.sh"), "orphans", "--min-age-h", "0"],
                               cwd=work, env=e, capture_output=True, text=True)
            return r.returncode, r.stdout + r.stderr

        _git(work, "push", "-q", "origin", "--delete", "ci-probe/x", env=env)
        base_relay, base_orph = relay(), orphans()
        ck("the baseline relay and orphans runs complete", base_relay[0] == 0 and "orphans: 0 stranded" in base_orph[1])
        _git(work, "push", "-q", "origin", f"{head}:refs/heads/ci-probe/x", env=env)
        ck("a planted ci-probe/x leaves the probe arm's output unchanged", relay() == base_relay)
        ck("a planted ci-probe/x leaves bus.sh orphans unchanged", orphans() == base_orph)
        _git(work, "push", "-q", "origin", f"{head}:refs/heads/probe/foo", env=env)
        rc, out = relay()
        ck("null: a planted probe/foo IS reported OWED by the probe arm", "OWED probe-ref refs/heads/probe/foo" in out)
        _git(work, "checkout", "-q", "-b", "t", env=env)
        (work / "stranded.txt").write_text("x\n")
        _git(work, "add", "stranded.txt", env=env)
        _git(work, "commit", "-q", "-m", "stranded", env=env)
        tip = _git(work, "rev-parse", "HEAD", env=env).strip()
        _git(work, "push", "-q", "origin", f"{tip}:refs/heads/handoff/zz", f"{tip}:refs/heads/handoff-body/zz", env=env)
        ck("null: a planted handoff/zz IS reported by bus.sh orphans", "ORPHAN zz" in orphans()[1])

    passed = sum(1 for _t, ok in res if ok)
    for tag, ok in res:
        if not ok:
            print(f"  FAIL  {tag}")
    print(f"ci_probe self-test: {len(res)} checks, {len(res) - passed} failed")
    return 0 if passed == len(res) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
