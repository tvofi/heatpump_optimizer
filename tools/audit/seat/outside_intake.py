#!/usr/bin/env python3
"""outside_intake.py -- the submissions outside users make, and what each is owed.

    python3 -I tools/audit/seat/outside_intake.py list   [--repo O/R] --since ISO [--cursor FILE] [--roster FILE]
    python3 -I tools/audit/seat/outside_intake.py answer [--repo O/R] --issue N [--roster FILE] [--dry-run]
    python3 -I tools/audit/seat/outside_intake.py refuse [--repo O/R] --issue N --reason-file F [--dry-run]
    python3 -I tools/audit/seat/outside_intake.py --self-test

WHY THIS EXISTS (R10-OUTSIDE-INTAKE). The owner's ruling, tvofi 2026-11-06:
"During future audit rounds, issues, PRs or other posts from outside users
should be regularly checked, triaged/designed and planned. [...] When the plan
html is done, and any outside submission is on the roster, the plan HTML should
be linked in an answer to the outside submission." Three outside submissions
(#3224, #3225, #3226) reached the round in one day and were found by hand.

OUTSIDE is any author not in OURS and not a bot account (`user.type` Bot):
a bot is not an outside user, ours or a third party's. THIS ENCODES A DESIGN
CHOICE. A submission is one thread -- issue, pull request or discussion, one
number space -- with outside activity at or after the cursor: the thread
itself, an issue comment, a review comment, or a discussion comment.

DISPOSITION, read from the roster and the thread, never from memory:
  refused   a comment by OURS carrying REFUSED_MARK (posted by `refuse`);
  on roster the number is in a roster group's `issues` or `fixes` (wired by
            the roster seat's `roster_edit.py wire-issue`, the existing
            mechanism -- a carry onto a group is wired the same way);
  answered  on roster, and a comment by OURS carrying ANSWER_MARK.
A marker in a comment by anyone else is not read: an outsider cannot dispose
of their own submission, nor a third-party bot (one quoting a submitter's text)
of anyone's; such a bot's comment is neither ours nor outside activity.

LIST prints one line per submission owed this turn, rc 1 when any is, rc 0
when none, rc 2 when a read failed (nothing printed but the UNREADABLE line):
  OUTSIDE #N owed=triage <kind> by=<login> since=<utc>   on no roster group and
      not refused: triage or design it (`designer.md`),
      then the roster seat wires it into a group, or `refuse`;
  OUTSIDE #N owed=answer group=<G> ...  on the roster, unanswered, and the
      plan page answers 200: the dispatch seat runs `answer`;
  OUTSIDE #N owed=reply ...   answered or refused, and an outside comment is
      newer than every comment of ours: read it and reply;
  OUTSIDE plan-page UNAVAILABLE <why>; <k> answer(s) wait   once, while the
      plan page does not answer and a submission on the roster waits for it.
With `--cursor`, the scan starts at the cursor's `since` (else `--since`), and
a readable pass moves it to the earliest activity of any submission still
owed, else to the pass's start: a submission never drops out while owed.

ANSWER posts, through `tools/pr/gh_comment.py post` (its read-back is the
proof), the plan page link to a submission on the roster. Refusals, rc 1 and
nothing posted: the thread has no outside activity, it is already answered or
refused (so none is answered twice), it is on no roster group, the plan page
does not answer, or it is a discussion (answered by hand: gh_comment posts
issue comments only). REFUSE posts the reason file under REFUSED_MARK, with
the same already-disposed refusal.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import plan_public  # noqa: E402
import roster_lib  # noqa: E402

#: Our accounts (CLAUDE.md, Identity): the owner, the retired seat account, and
#: the Apps, though every bot is already not outside by its type.
OURS = frozenset({"tvofi", "tvofi-seat-author", "hpo-author[bot]", "hpo-approver[bot]",
                  "hpo-runs[bot]", "github-actions[bot]"})
ANSWER_MARK = "<!-- outside-intake:answered -->"
REFUSED_MARK = "<!-- outside-intake:refused -->"
REPO_ROOT = HERE.parents[2]
DEFAULT_REPO = "tvofi/heatpump_optimizer"

_ISSUE = ('.[] | {n: .number, login: (.user.login // "ghost"), type: (.user.type // "User"), '
          'at: .created_at, kind: (if .pull_request then "pr" else "issue" end)}')
_COMMENT = ('.[] | {n: (.{url} | split("/") | last | tonumber), login: (.user.login // "ghost"), '
            'type: (.user.type // "User"), at: .created_at}')
_THREAD = ('.[] | {login: (.user.login // "ghost"), type: (.user.type // "User"), at: .created_at, '
           f'answered: (.body | contains("{ANSWER_MARK}")), refused: (.body | contains("{REFUSED_MARK}"))}}')
_DISCUSSIONS = """query($owner: String!, $name: String!) { repository(owner: $owner, name: $name) {
  discussions(first: 100, orderBy: {field: UPDATED_AT, direction: DESC}) { nodes {
    number createdAt author { login __typename }
    comments(first: 100) { nodes { createdAt body author { login __typename } } } } } } }"""


class Unreadable(Exception):
    pass


def gh(argv: list[str]) -> tuple[int, str]:
    p = subprocess.run(["gh", *argv], capture_output=True, text=True)
    return p.returncode, p.stdout


def plan_live(url: str = plan_public.PLAN_URL) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=20) as r:
            return r.status == 200, f"HTTP {r.status}"
    except Exception as e:  # any failure to read is "not live", said with its reason
        return False, type(e).__name__


def outside(login: str, typ: str) -> bool:
    return login not in OURS and typ != "Bot"


def rows(run, argv: list[str]) -> list[dict]:
    rc, out = run(argv)
    if rc != 0:
        raise Unreadable(f"gh {' '.join(argv[:2])} rc={rc}")
    return [json.loads(ln) for ln in out.splitlines() if ln.strip()]


class Thread:
    def __init__(self, n: int, kind: str = "comment"):
        self.n, self.kind, self.by, self.first, self.last_out = n, kind, set(), "", ""
        self.answered = self.refused = self.last_ours = ""

    def saw(self, login: str, at: str) -> None:
        self.by.add(login)
        self.first = min(self.first or at, at)
        self.last_out = max(self.last_out, at)

    def mark(self, c: dict) -> None:
        """A comment of the thread: ours marks it, and no other moves anything here.

        Outside activity reaches `last_out` through `saw` alone: `one_thread` passes it
        every outside comment, and one `scan` skips predates the activity that opened
        the thread, so cannot raise its maximum. A third-party bot's is neither."""
        if c["login"] not in OURS:
            return
        self.last_ours = max(self.last_ours, c["at"])
        if c.get("answered"):
            self.answered = max(self.answered, c["at"])
        if c.get("refused"):
            self.refused = max(self.refused, c["at"])


def discussions(run, repo: str) -> list[dict]:
    """Each discussion as {n, at, login, type, comments: [...]}, [] when the repository has none."""
    rc, out = run(["api", f"repos/{repo}", "--jq", ".has_discussions"])
    if rc != 0:
        raise Unreadable(f"gh api repos/{repo} rc={rc}")
    if out.strip() != "true":
        return []
    owner, name = repo.split("/", 1)
    rc, out = run(["api", "graphql", "-f", f"query={_DISCUSSIONS}", "-F", f"owner={owner}", "-F", f"name={name}"])
    if rc != 0:
        raise Unreadable(f"gh api graphql rc={rc}")
    def who(a: dict | None) -> tuple[str, str]:
        """(login, type) as the REST API spells them: GraphQL names a bot without its `[bot]` suffix."""
        login, typ = (a or {}).get("login") or "ghost", "Bot" if (a or {}).get("__typename") == "Bot" else "User"
        if typ == "Bot":
            login = f"{login}[bot]"
        return login, typ

    res = []
    for d in json.loads(out)["data"]["repository"]["discussions"]["nodes"]:
        login, typ = who(d.get("author"))
        cs = [{"login": who(c.get("author"))[0], "type": who(c.get("author"))[1], "at": c["createdAt"],
               "answered": ANSWER_MARK in c["body"], "refused": REFUSED_MARK in c["body"]}
              for c in d["comments"]["nodes"]]
        res.append({"n": d["number"], "at": d["createdAt"], "login": login, "type": typ, "comments": cs})
    return res


def scan(run, repo: str, since: str) -> dict[int, Thread]:
    """Every thread with outside activity at or after `since`, its comments read for our marks."""
    threads: dict[int, Thread] = {}

    def saw(n: int, kind: str | None, login: str, typ: str, at: str) -> None:
        if at >= since and outside(login, typ):
            t = threads.setdefault(n, Thread(n))
            if kind:
                t.kind = kind
            t.saw(login, at)

    q = f"since={since}&per_page=100"
    for r in rows(run, ["api", "--paginate", f"repos/{repo}/issues?state=all&{q}", "--jq", _ISSUE]):
        saw(r["n"], r["kind"], r["login"], r["type"], r["at"])
    for path, url in (("issues/comments", "issue_url"), ("pulls/comments", "pull_request_url")):
        for r in rows(run, ["api", "--paginate", f"repos/{repo}/{path}?{q}", "--jq",
                            _COMMENT.replace("{url}", url)]):
            saw(r["n"], None, r["login"], r["type"], r["at"])
    disc = {d["n"]: d for d in discussions(run, repo)}
    for d in disc.values():
        saw(d["n"], "discussion", d["login"], d["type"], d["at"])
        for c in d["comments"]:
            saw(d["n"], None, c["login"], c["type"], c["at"])
    for t in threads.values():
        cs = disc[t.n]["comments"] if t.n in disc else rows(
            run, ["api", "--paginate", f"repos/{repo}/issues/{t.n}/comments?per_page=100", "--jq", _THREAD])
        if t.n in disc:
            t.kind = "discussion"
        for c in cs:
            t.mark(c)
    return threads


def one_thread(run, repo: str, n: int) -> Thread | None:
    """Thread n read whole (its opening post and every comment), or None without outside activity.

    A number the issues API does not know is a discussion (or nothing): it is
    returned as a discussion when it has outside activity, so `dispose` refuses it."""
    rc, out = run(["api", f"repos/{repo}/issues/{n}", "--jq", _ISSUE.replace(".[] | ", "")])
    if rc != 0:
        d = next((d for d in discussions(run, repo) if d["n"] == n), None)
        if d is None:
            return None
        t = Thread(n, "discussion")
        if outside(d["login"], d["type"]):
            t.saw(d["login"], d["at"])
        cs = d["comments"]
    else:
        r = json.loads(out)
        t = Thread(n, r["kind"])
        if outside(r["login"], r["type"]):
            t.saw(r["login"], r["at"])
        cs = rows(run, ["api", "--paginate", f"repos/{repo}/issues/{n}/comments?per_page=100", "--jq", _THREAD])
        if r["kind"] == "pr":
            cs += rows(run, ["api", "--paginate", f"repos/{repo}/pulls/{n}/comments?per_page=100", "--jq", _THREAD])
    for c in cs:
        if outside(c["login"], c["type"]):
            t.saw(c["login"], c["at"])
        t.mark(c)
    return t if t.by else None


def wired(roster: dict) -> dict[int, str]:
    """Issue or pull-request number -> the first roster group whose `issues` or `fixes` holds it."""
    out: dict[int, str] = {}
    for g in roster.get("groups", []):
        for n in [*(g.get("issues") or []), *(g.get("fixes") or [])]:
            out.setdefault(n, g["group"])
    return out


def owed(t: Thread, groups: dict[int, str], live: bool) -> str | None:
    """The thread's owed word this turn ('wait' while only the plan page holds it), or None."""
    disposed = max(t.answered, t.refused)
    if disposed:
        return "reply" if t.last_out > max(disposed, t.last_ours) else None
    if t.n in groups:
        return "answer" if live else "wait"
    return "triage"


def load_roster(path: str | None) -> dict:
    if path:
        return roster_lib.load_roster_file(path)
    repo = str(REPO_ROOT)
    ref, _ = roster_lib.default_roster_ref(roster_lib.git_in(repo))
    return roster_lib.show_roster(repo, ref)


def listing(run, repo: str, since: str, roster: dict, live: tuple[bool, str], now: str) -> tuple[list[str], str]:
    """(lines, next cursor)."""
    threads, groups = scan(run, repo, since), wired(roster)
    lines, waiting, keep = [], 0, now
    for n in sorted(threads):
        t = threads[n]
        word = owed(t, groups, live[0])
        if word is None:
            continue
        keep = min(keep, t.first)
        if word == "wait":
            waiting += 1
            continue
        group = f" group={groups[n]}" if n in groups else ""
        lines.append(f"OUTSIDE #{n} owed={word}{group} {t.kind} by={','.join(sorted(t.by))} since={t.first}")
    if waiting:
        lines.append(f"OUTSIDE plan-page UNAVAILABLE {live[1]}; {waiting} answer(s) wait")
    return lines, keep


def post(repo: str, n: int, body: str, dry: bool, runner=subprocess.run) -> int:
    d = tempfile.mkdtemp(prefix="outside-intake-")
    f = Path(d) / "body.md"
    f.write_text(body)
    argv = [sys.executable, "-I", str(REPO_ROOT / "tools/pr/gh_comment.py"), "post", "--repo", repo,
            "--issue", str(n), "--body-file", str(f)] + (["--dry-run"] if dry else [])
    return runner(argv).returncode


def answer_body(group: str) -> str:
    return (f"{ANSWER_MARK}\nThank you for this submission. It is on the current round's plan as "
            f"`{group}`. The plan page shows where that group stands and when it is expected to land, "
            f"and is refreshed as the round runs: {plan_public.PLAN_URL}\n")


def dispose(run, repo: str, n: int, roster: dict | None, live, body: str | None, dry: bool, poster=post) -> tuple[int, str]:
    """Answer (body None) or refuse (body given) thread n; (rc, message)."""
    t = one_thread(run, repo, n)
    if t is None:
        return 1, f"outside_intake: REFUSED: #{n} has no outside activity"
    group = wired(roster or {}).get(n)
    if t.refused or t.answered:
        return 1, f"outside_intake: REFUSED: #{n} is already {'refused' if t.refused else 'answered'}"
    if t.kind == "discussion":
        return 1, f"outside_intake: REFUSED: #{n} is a discussion; answer it by hand"
    if body is None:
        if group is None:
            return 1, f"outside_intake: REFUSED: #{n} is on no roster group; triage it first"
        ok, why = live()
        if not ok:
            return 1, f"outside_intake: REFUSED: the plan page does not answer ({why})"
        body = answer_body(group)
    else:
        body = f"{REFUSED_MARK}\n{body}"
    rc = poster(repo, n, body, dry)
    return rc, f"outside_intake: #{n} {'answered' if REFUSED_MARK not in body else 'refused'} rc={rc}"


def utc(t: float | None = None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        import outside_intake_selftest  # the fixtures and cases live beside this file
        return outside_intake_selftest.run()
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("list", "answer", "refuse"):
        s = sub.add_parser(name)
        s.add_argument("--repo", default=DEFAULT_REPO)
        s.add_argument("--roster", help="a roster file; default: the round's roster ref (roster_lib)")
        if name == "list":
            s.add_argument("--since", required=True)
            s.add_argument("--cursor", type=Path)
        else:
            s.add_argument("--issue", required=True, type=int)
            s.add_argument("--dry-run", action="store_true")
        if name == "refuse":
            s.add_argument("--reason-file", required=True, type=Path)
    a = ap.parse_args(argv)
    try:
        roster = load_roster(a.roster)
        if a.cmd == "list":
            since = a.since
            if a.cursor and a.cursor.exists():
                since = json.loads(a.cursor.read_text()).get("since") or since
            lines, keep = listing(gh, a.repo, since, roster, plan_live(), utc())
        else:
            reason = a.reason_file.read_text() if a.cmd == "refuse" else None
            if reason is not None and not reason.strip():
                print("outside_intake: REFUSED: the reason file is empty", file=sys.stderr)
                return 1
            rc, msg = dispose(gh, a.repo, a.issue, roster, plan_live, reason, a.dry_run)
            print(msg, file=sys.stderr if rc else sys.stdout)
            return rc
    except (Unreadable, roster_lib.RosterNotFound, OSError, ValueError, KeyError) as e:
        print(f"outside-intake: UNREADABLE {type(e).__name__}: {e}")
        return 2
    if a.cursor:
        a.cursor.parent.mkdir(parents=True, exist_ok=True)
        a.cursor.write_text(json.dumps({"since": keep}) + "\n")
    print("".join(ln + "\n" for ln in lines), end="")
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
