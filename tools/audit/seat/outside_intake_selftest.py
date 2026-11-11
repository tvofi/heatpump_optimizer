"""The fixtures, cases and mutants of outside_intake.py's self-test, kept beside it.

Run through `outside_intake.py`'s own flag, which CI's governance workflow
names. Offline: `gh` is a fake answering each endpoint from raw API-shaped
fixtures, projected through the real `jq` with the instrument's own `--jq`
expressions, so a projection that misreads the API fails here. The fixtures
are the round's three outside submissions (tvofi 2026-11-06): #3224 (adopted
via #3231, on the roster and answered), #3225 (design R10-COMBI-TANK, on the
roster and unanswered) and #3226 (adopted via #3232, here on no roster group),
plus the shapes around them: our own thread, a bot's pull request, an outside
comment on our issue, a review comment, a forged marker, a third-party bot's marker
and its later comment on an answered thread,
our App's marker in a discussion, a refusal with and
without a later outside reply, and a discussion. MUTANTS plants one edit per
predicate in a temp copy and expects its named case to fail.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SINCE = "2026-11-05T00:00:00Z"
NOW = "2026-11-07T00:00:00Z"
OUT = {"login": "Bankaifan", "type": "User"}
ME = {"login": "tvofi", "type": "User"}


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def issue(n, user, at, pr=False):
    d = {"number": n, "user": user, "created_at": at, "title": f"t{n}"}
    if pr:
        d["pull_request"] = {"url": f"x/pulls/{n}"}
    return d


def comment(n, user, at, body="", review=False):
    key = "pull_request_url" if review else "issue_url"
    return {key: f"https://api.github.com/repos/o/r/{'pulls' if review else 'issues'}/{n}",
            "user": user, "created_at": at, "body": body}


def world(m):
    """The fixture repository, as raw API objects; m is the module under test (its markers)."""
    issues = [
        issue(3224, OUT, "2026-11-05T09:45:08Z", pr=True),
        issue(3225, OUT, "2026-11-05T10:29:13Z"),
        issue(3226, OUT, "2026-11-05T11:36:11Z", pr=True),
        issue(3250, ME, "2026-11-05T12:00:00Z"),
        issue(3251, {"login": "dependabot[bot]", "type": "Bot"}, "2026-11-05T12:30:00Z", pr=True),
        issue(3252, {"login": "someone", "type": "User"}, "2026-11-05T13:00:00Z"),
        issue(3253, {"login": "other", "type": "User"}, "2026-11-05T14:00:00Z"),
        issue(3100, {"login": "old", "type": "User"}, "2026-10-01T00:00:00Z"),
        issue(3240, {"login": "hpo-author[bot]", "type": "Bot"}, "2026-11-05T15:00:00Z", pr=True),
    ]
    comments = [
        comment(3224, ME, "2026-11-06T05:07:57Z", m.ANSWER_MARK + "\nlanded through #3231"),
        comment(3225, ME, "2026-11-06T21:11:33Z", "being investigated"),
        comment(3226, OUT, "2026-11-06T06:00:00Z", m.ANSWER_MARK + " forged by the submitter"),
        comment(3250, {"login": "visitor", "type": "User"}, "2026-11-06T07:00:00Z", "a question on our issue"),
        comment(3252, ME, "2026-11-06T01:00:00Z", m.REFUSED_MARK + "\nout of scope"),
        comment(3252, {"login": "someone", "type": "User"}, "2026-11-06T02:00:00Z", "but why?"),
        comment(3253, ME, "2026-11-06T01:00:00Z", m.REFUSED_MARK + "\nout of scope"),
        comment(3253, {"login": "other", "type": "User"}, "2026-11-06T02:00:00Z", "ok"),
        comment(3253, ME, "2026-11-06T03:00:00Z", "noted"),
        comment(3100, ME, "2026-11-06T04:00:00Z", "an old thread we touched"),
    ]
    reviews = [comment(3240, {"login": "reviewer-x", "type": "User"}, "2026-11-06T08:00:00Z", "nit", review=True)]
    return {"issues": issues, "comments": comments, "reviews": reviews, "discussions": []}


def roster():
    return {"groups": [
        {"group": "R10-ADOPTED-3231", "issues": [3224], "fixes": []},
        {"group": "R10-COMBI-TANK", "issues": [3225]},
        {"group": "R10-OTHER", "issues": ["3226"], "fixes": None},  # a string is not a wiring
    ]}


def jq(expr: str, data) -> str:
    p = subprocess.run(["jq", "-c", expr], input=json.dumps(data), capture_output=True, text=True, check=True)
    return p.stdout


class Fake:
    """`gh`, answering from a world; records every argv; `fail` names an endpoint fragment that errors."""

    def __init__(self, w, fail: str | None = None):
        self.w, self.fail, self.calls = w, fail, []

    def __call__(self, argv):
        self.calls.append(list(argv))
        path = argv[1] if argv[1] != "--paginate" else argv[2]
        if self.fail and self.fail in " ".join(argv):
            return 1, ""
        expr = argv[argv.index("--jq") + 1] if "--jq" in argv else None
        w = self.w
        if path == "graphql":
            nodes = [{"number": d["n"], "createdAt": d["at"], "author": {"login": d["login"], "__typename": d["type"]},
                      "comments": {"nodes": [{"createdAt": c["at"], "body": c["body"],
                                              "author": {"login": c["login"], "__typename": c["type"]}}
                                             for c in d["comments"]]}} for d in w["discussions"]]
            return 0, json.dumps({"data": {"repository": {"discussions": {"nodes": nodes}}}})
        if path == "repos/o/r":
            return 0, jq(expr, {"has_discussions": bool(w["discussions"])})
        tail = path.split("?")[0][len("repos/o/r/"):]
        if tail == "issues":
            return 0, jq(expr, w["issues"])
        if tail == "issues/comments":
            return 0, jq(expr, w["comments"])
        if tail == "pulls/comments":
            return 0, jq(expr, w["reviews"])
        parts = tail.split("/")
        n = int(parts[1])
        if parts[0] == "issues" and len(parts) == 2:
            hit = [i for i in w["issues"] if i["number"] == n]
            return (0, jq(expr, hit[0])) if hit else (1, "")
        if parts[0] == "issues" and parts[2] == "comments":
            return 0, jq(expr, [c for c in w["comments"] if c.get("issue_url", "").endswith(f"/{n}")])
        if parts[0] == "pulls" and parts[2] == "comments":
            return 0, jq(expr, [c for c in w["reviews"] if c["pull_request_url"].endswith(f"/{n}")])
        raise AssertionError(f"unexpected gh call {argv}")


class Poster:
    def __init__(self):
        self.posts = []

    def __call__(self, repo, n, body, dry):
        self.posts.append((n, body))
        return 0


LIVE, DOWN = (lambda: (True, "HTTP 200")), (lambda: (False, "URLError"))


class Ran:
    """subprocess.run for post(): records each argv and the body file's text, answers rc."""

    def __init__(self, rc: int):
        self.rc, self.argv, self.body = rc, [], None

    def __call__(self, argv):
        self.argv = list(argv)
        self.body = Path(argv[argv.index("--body-file") + 1]).read_text()
        return subprocess.CompletedProcess(argv, self.rc)


def main_list(m, w, d: Path, since: str) -> tuple[int, list[str]]:
    """m.main(["list", ...]) over world w with the cursor in d: (rc, printed lines). `gh` and the
    plan probe are swapped on the module for the fake, the only seam main() reads them through."""
    (d / "roster.json").write_text(json.dumps(roster()))
    m.gh, m.plan_live = Fake(w), LIVE
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = m.main(["list", "--repo", "o/r", "--since", since, "--cursor", str(d / "c" / "cursor.json"),
                     "--roster", str(d / "roster.json")])
    return rc, out.getvalue().splitlines()


def cases(m) -> dict[str, bool]:
    res: dict[str, bool] = {}
    w = world(m)
    lines, keep = m.listing(Fake(w), "o/r", SINCE, roster(), LIVE(), NOW)
    want = [
        "OUTSIDE #3225 owed=answer group=R10-COMBI-TANK issue by=Bankaifan since=2026-11-05T10:29:13Z",
        "OUTSIDE #3226 owed=triage pr by=Bankaifan since=2026-11-05T11:36:11Z",
        "OUTSIDE #3240 owed=triage comment by=reviewer-x since=2026-11-06T08:00:00Z",
        "OUTSIDE #3250 owed=triage comment by=visitor since=2026-11-06T07:00:00Z",
        "OUTSIDE #3252 owed=reply issue by=someone since=2026-11-05T13:00:00Z",
    ]
    res["list: the fixture world gives exactly its owed lines (answered, bot, ours, old and replied-to threads silent)"] = (
        lines == want)
    res["list: a marker in the submitter's own comment disposes of nothing (#3226 owes triage)"] = any(
        ln.startswith("OUTSIDE #3226 owed=triage") for ln in lines)
    res["list: the cursor stays at the earliest owed submission's first outside activity"] = (
        keep == "2026-11-05T10:29:13Z")
    lines, keep = m.listing(Fake(w), "o/r", SINCE, roster(), DOWN(), NOW)
    res["list: with the plan page down, an answer waits behind one UNAVAILABLE line and still holds the cursor"] = (
        not any("#3225" in ln for ln in lines) and lines[-1] == "OUTSIDE plan-page UNAVAILABLE URLError; 1 answer(s) wait"
        and keep == "2026-11-05T10:29:13Z")
    empty = {"issues": [], "comments": [], "reviews": [], "discussions": []}
    lines, keep = m.listing(Fake(empty), "o/r", SINCE, roster(), LIVE(), NOW)
    res["list null: no outside activity prints nothing and moves the cursor to now"] = lines == [] and keep == NOW
    lines, _ = m.listing(Fake(w), "o/r", "2026-11-06T09:00:00Z", roster(), LIVE(), NOW)
    res["list: activity before the cursor is not re-read"] = lines == []
    with tempfile.TemporaryDirectory() as d:
        rc1, l1 = main_list(m, w, Path(d), SINCE)
        cur = json.loads((Path(d) / "c" / "cursor.json").read_text())
        rc2, l2 = main_list(m, w, Path(d), "2026-11-06T09:00:00Z")  # a later --since: the cursor must win
        rc3, l3 = main_list(m, empty, Path(d), SINCE)
    res["main list: rc 1 with owed lines, the cursor persisted at the earliest owed activity and read back next pass"] = (
        rc1 == 1 and l1 == want and cur == {"since": "2026-11-05T10:29:13Z"} and rc2 == 1 and l2 == want)
    res["main list null: no owed submission is rc 0 and prints nothing"] = rc3 == 0 and l3 == []
    w4 = world(m)
    w4["comments"].append(comment(3225, {"login": "renovate[bot]", "type": "Bot"}, "2026-11-06T22:00:00Z",
                                  m.ANSWER_MARK + " quoted by a third-party App"))
    lines, _ = m.listing(Fake(w4), "o/r", SINCE, roster(), LIVE(), NOW)
    res["identity: a third-party bot's marker disposes of nothing (#3225 still owes the answer)"] = (
        lines == want)
    try:
        m.listing(Fake(w, fail="issues/comments"), "o/r", SINCE, roster(), LIVE(), NOW)
        res["list: a failed read is UNREADABLE, never a clean board"] = False
    except m.Unreadable:
        res["list: a failed read is UNREADABLE, never a clean board"] = True

    p = Poster()
    rc, msg = m.dispose(Fake(w), "o/r", 3225, roster(), LIVE, None, False, p)
    body = p.posts[0][1] if p.posts else ""
    res["answer: an unanswered submission on the roster gets the plan page link once, marked"] = (
        rc == 0 and len(p.posts) == 1 and p.posts[0][0] == 3225 and body.startswith(m.ANSWER_MARK)
        and m.plan_public.PLAN_URL in body and "`R10-COMBI-TANK`" in body)
    w2 = world(m)
    w2["comments"].append(comment(3225, {"login": "hpo-approver[bot]", "type": "Bot"}, "2026-11-06T22:00:00Z", body))
    p = Poster()
    rc, msg = m.dispose(Fake(w2), "o/r", 3225, roster(), LIVE, None, False, p)
    lines, _ = m.listing(Fake(w2), "o/r", SINCE, roster(), LIVE(), NOW)
    after = {}
    for who in ({"login": "renovate[bot]", "type": "Bot"}, {"login": "Bankaifan", "type": "User"}):
        w5 = world(m)
        w5["comments"] += [w2["comments"][-1], comment(3225, who, "2026-11-06T23:00:00Z", "a later comment")]
        after[who["type"]] = ([ln for ln in m.listing(Fake(w5), "o/r", SINCE, roster(), LIVE(), NOW)[0] if "#3225" in ln],
                              m.owed(m.one_thread(Fake(w5), "o/r", 3225), m.wired(roster()), True))
    res["identity: a third-party bot's comment after our answer owes nothing; an outsider's owes a reply"] = (
        after["Bot"] == ([], None) and len(after["User"][0]) == 1 and " owed=reply " in after["User"][0][0]
        and after["User"][1] == "reply")
    for dry in (True, False):
        r = Ran(0)
        got = m.post("o/r", 3225, "the body\n", dry, r)
        res[f"post: gh_comment.py post is run with the body file, --dry-run {'passed' if dry else 'absent'}, rc 0 kept"] = (
            got == 0 and Path(r.argv[2]).relative_to(m.REPO_ROOT).as_posix() == "tools/pr/gh_comment.py"
            and r.argv[3:9] == ["post", "--repo", "o/r", "--issue", "3225", "--body-file"]
            and r.body == "the body\n" and (r.argv[10:] == ["--dry-run"] if dry else len(r.argv) == 10))
    res["post: a failed gh_comment read-back (rc 1) is a non-zero answer"] = m.post("o/r", 3225, "b", False, Ran(1)) == 1
    res["answer: an answered submission is refused and no longer listed (never answered twice)"] = (
        rc == 1 and "already answered" in msg and not p.posts and not any("#3225" in ln for ln in lines))
    for n, why, live in ((3226, "on no roster group", LIVE), (3225, "does not answer", DOWN),
                         (3252, "already refused", LIVE), (3251, "no outside activity", LIVE),
                         (9999, "no outside activity", LIVE)):
        p = Poster()
        rc, msg = m.dispose(Fake(w), "o/r", n, roster(), live, None, False, p)
        res[f"answer: #{n} is refused ({why}) and nothing is posted"] = rc == 1 and why in msg and not p.posts
    p = Poster()
    rc, msg = m.dispose(Fake(w), "o/r", 3226, roster(), LIVE, "Not in scope: reason.\n", False, p)
    res["refuse: the reason is posted under the refusal marker, and the thread is then silent"] = (
        rc == 0 and p.posts and p.posts[0][1].startswith(m.REFUSED_MARK) and "reason" in p.posts[0][1])
    pr = Poster()
    rc, msg = m.dispose(Fake(w), "o/r", 3240, roster(), LIVE, "Not in scope: reason.\n", False, pr)
    res["refuse: a pull request whose only outside activity is a review comment is refused, marked (#3240)"] = (
        rc == 0 and len(pr.posts) == 1 and pr.posts[0][0] == 3240 and pr.posts[0][1].startswith(m.REFUSED_MARK))
    w3 = world(m)
    w3["comments"].append(comment(3226, ME, "2026-11-06T23:00:00Z", p.posts[0][1] if p.posts else ""))
    lines, _ = m.listing(Fake(w3), "o/r", SINCE, roster(), LIVE(), NOW)
    res["refuse: a refused submission owes nothing until the submitter writes again"] = not any(
        "#3226" in ln for ln in lines)
    wd = dict(empty, discussions=[{"n": 3260, "at": "2026-11-06T10:00:00Z", "login": "asker", "type": "User",
                                   "comments": []}])
    lines, _ = m.listing(Fake(wd), "o/r", SINCE, roster(), LIVE(), NOW)
    p = Poster()
    rc, msg = m.dispose(Fake(wd), "o/r", 3260, {"groups": [{"group": "G", "issues": [3260]}]}, LIVE, None, False, p)
    res["discussions: an outside discussion is listed, and answering one is refused (by hand)"] = (
        lines == ["OUTSIDE #3260 owed=triage discussion by=asker since=2026-11-06T10:00:00Z"]
        and rc == 1 and "discussion" in msg and not p.posts)
    wd = dict(empty, discussions=[{"n": 3261, "at": "2026-11-06T10:00:00Z", "login": "asker", "type": "User",
                                   "comments": [{"login": "hpo-approver", "type": "Bot", "at": "2026-11-06T11:00:00Z",
                                                 "body": m.REFUSED_MARK + " by our App"}]}])
    lines, _ = m.listing(Fake(wd), "o/r", SINCE, roster(), LIVE(), NOW)
    res["discussions: our App's marker is read (GraphQL names a bot without its [bot] suffix)"] = lines == []
    wd = dict(empty, discussions=[{"n": 3262, "at": "2026-11-01T10:00:00Z", "login": "asker", "type": "User",
                                   "comments": [{"login": "asker", "type": "User", "at": "2026-11-06T10:00:00Z",
                                                 "body": "still open?"}]}])
    lines, _ = m.listing(Fake(wd), "o/r", SINCE, roster(), LIVE(), NOW)
    res["discussions: a discussion opened before the cursor, its new outside comment listed as a discussion"] = (
        lines == ["OUTSIDE #3262 owed=triage discussion by=asker since=2026-11-06T10:00:00Z"])
    # A design choice: GitHub stamps to the second, so a same-second outside comment cannot be
    # ordered against our answer; only outside activity strictly after our latest comment owes a reply.
    t = m.Thread(3225, "issue")
    t.saw("Bankaifan", "2026-11-06T22:00:00Z")
    t.answered = t.last_ours = "2026-11-06T22:00:00Z"
    later = m.Thread(3225, "issue")
    later.saw("Bankaifan", "2026-11-06T22:00:01Z")
    later.answered = later.last_ours = "2026-11-06T22:00:00Z"
    res["reply: outside activity in our answer's own second owes nothing; one second later owes a reply"] = (
        m.owed(t, m.wired(roster()), True) is None and m.owed(later, m.wired(roster()), True) == "reply")
    res["identity: every account of ours and every bot is not outside; a stranger is"] = (
        not any(m.outside(a, "User") for a in m.OURS) and not m.outside("renovate[bot]", "Bot")
        and m.outside("Bankaifan", "User"))
    return res


#: (old, new, the case that must fail). Each old string appears once in outside_intake.py.
MUTANTS = {
    "bots_outside": ('return login not in OURS and typ != "Bot"', "return login not in OURS",
                     "identity: every account of ours and every bot is not outside; a stranger is"),
    "forged_marker_read": ('        if c["login"] not in OURS:\n            return\n', '        if c["login"] not in OURS:\n            pass\n',
                           "list: a marker in the submitter's own comment disposes of nothing (#3226 owes triage)"),
    "since_ignored": ("        if at >= since and outside(login, typ):", "        if outside(login, typ):",
                      "list: activity before the cursor is not re-read"),
    "answer_twice": ("    if t.refused or t.answered:", "    if t.refused:",
                     "answer: an answered submission is refused and no longer listed (never answered twice)"),
    "unwired_answered": ("        if group is None:\n", "        if False:\n", "answer: #3226 is refused (on no roster group) and nothing is posted"),
    "plan_down_answers": ('        return "answer" if live else "wait"', '        return "answer"',
                          "list: with the plan page down, an answer waits behind one UNAVAILABLE line and still holds the cursor"),
    "reply_never": ('        return "reply" if t.last_out > max(disposed, t.last_ours) else None', "        return None",
                    "list: the fixture world gives exactly its owed lines (answered, bot, ours, old and replied-to threads silent)"),
    "cursor_jumps": ("        keep = min(keep, t.first)\n", "",
                     "list: the cursor stays at the earliest owed submission's first outside activity"),
    "review_comments_unread": ('(("issues/comments", "issue_url"), ("pulls/comments", "pull_request_url"))',
                               '(("issues/comments", "issue_url"),)',
                               "list: the fixture world gives exactly its owed lines (answered, bot, ours, old and replied-to threads silent)"),
    "one_thread_pr_reviews_drop": ('        if r["kind"] == "pr":\n', "        if False:\n",
                                   "refuse: a pull request whose only outside activity is a review comment is refused, marked (#3240)"),
    "unreadable_swallowed": ('        raise Unreadable(f"gh {\' \'.join(argv[:2])} rc={rc}")', "        return []",
                             "list: a failed read is UNREADABLE, never a clean board"),
    "marker_any_bot": ('        if c["login"] not in OURS:\n', '        if outside(c["login"], c["type"]):\n',
                       "identity: a third-party bot's marker disposes of nothing (#3225 still owes the answer)"),
    "thirdbot_moves_out": ('        if c["login"] not in OURS:\n            return\n',
                           '        if c["login"] not in OURS:\n            self.last_out = max(self.last_out, c["at"])\n            return\n',
                           "identity: a third-party bot's comment after our answer owes nothing; an outsider's owes a reply"),
    "graphql_bot_suffix": ('        login = f"{login}[bot]"\n', "        pass\n",
                           "discussions: our App's marker is read (GraphQL names a bot without its [bot] suffix)"),
    "main_cursor_unread": ('                since = json.loads(a.cursor.read_text()).get("since") or since\n',
                           "                pass\n",
                           "main list: rc 1 with owed lines, the cursor persisted at the earliest owed activity and read back next pass"),
    "main_cursor_now": ('json.dumps({"since": keep})', 'json.dumps({"since": utc()})',
                        "main list: rc 1 with owed lines, the cursor persisted at the earliest owed activity and read back next pass"),
    "main_list_rc0": ("    return 1 if lines else 0\n", "    return 0\n",
                      "main list: rc 1 with owed lines, the cursor persisted at the earliest owed activity and read back next pass"),
    "post_rc_dropped": ("    return runner(argv).returncode\n", "    runner(argv)\n    return 0\n",
                        "post: a failed gh_comment read-back (rc 1) is a non-zero answer"),
    "post_dry_dropped": (' + (["--dry-run"] if dry else [])', "",
                         "post: gh_comment.py post is run with the body file, --dry-run passed, rc 0 kept"),
    "post_wrong_script": ('"tools/pr/gh_comment.py"', '"tools/pr/gh_comment_missing.py"',
                          "post: gh_comment.py post is run with the body file, --dry-run absent, rc 0 kept"),
    "scan_disc_kind": ('        if t.n in disc:\n            t.kind = "discussion"', '        if False:\n            t.kind = "discussion"',
                       "discussions: a discussion opened before the cursor, its new outside comment listed as a discussion"),
    "owed_reply_ge": ('"reply" if t.last_out > max(disposed, t.last_ours) else None',
                      '"reply" if t.last_out >= max(disposed, t.last_ours) else None',
                      "reply: outside activity in our answer's own second owes nothing; one second later owes a reply"),
    "discussion_answered": ('        return 1, f"outside_intake: REFUSED: #{n} is a discussion; answer it by hand"', "        pass",
                            "discussions: an outside discussion is listed, and answering one is refused (by hand)"),
}


def run(mutants: bool = True) -> int:
    if not shutil.which("jq"):
        print("outside_intake self-test: REFUSED: no jq on PATH; the projections cannot be driven")
        return 1
    import outside_intake as m
    res = cases(m)
    for name, ok in res.items():
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
    fails = [n for n, ok in res.items() if not ok]
    if mutants:
        src = (HERE / "outside_intake.py").read_text()
        for mid, (old, new, case) in MUTANTS.items():
            if src.count(old) != 1 or case not in res:
                fails.append(f"mutant {mid} is stale (old string x{src.count(old)}, case known={case in res})")
                print(f"FAIL mutant {mid}: stale")
                continue
            with tempfile.TemporaryDirectory() as d:
                p = Path(d) / "tools" / "audit" / "seat" / "outside_intake.py"  # the module's own depth
                p.parent.mkdir(parents=True)
                p.write_text(src.replace(old, new))
                try:
                    killed = not cases(load(p, f"oi_mutant_{mid}"))[case]
                except Exception as e:  # a crash is reported, never counted as a kill
                    print(f"FAIL mutant {mid}: crashed the cases ({type(e).__name__})")
                    fails.append(f"mutant {mid} crashed")
                    continue
            print(f"{'ok  ' if killed else 'FAIL'} mutant {mid} killed by: {case}")
            if not killed:
                fails.append(f"mutant {mid} survived")
    if fails:
        print(f"{len(fails)} self-test check(s) failed: " + "; ".join(fails))
        return 1
    print("outside_intake self-test: all checks passed")
    return 0
