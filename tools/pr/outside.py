#!/usr/bin/env python3
"""The outside-contributor contract (decision 0017): one owner for "is this an
admitted outside pull request, which class is each path it changes, and is its
class-O read the owner's".

    python3 -I tools/pr/outside.py check --repo O/R --pr N [--ref origin/main] [--early] [--no-fetch]
    python3 -I tools/pr/outside.py check --repo O/R --pr N --ref SHA --early --no-fetch --pull-json FILE
    python3 -I tools/pr/outside.py classify --pr N [--ref origin/main] PATH...
    python3 -I tools/pr/outside.py cross --repo O/R --pr N
    python3 -I tools/pr/outside.py approve --repo O/R --pr N --head SHA40 --mandate ID [--role TEXT]
    python3 -I tools/pr/outside.py --self-test

`check` is the whole contract at the live head: the allowlist (login, numeric
id, type User), a cross-repository head on `main` of ours, the head ref name,
no other pull request at the head, the path classes over the three-dot diff,
the manifest version, and class O. rc 0 admitted, 1 refused (each reason on a
`REFUSE:` line), 3 not an outside pull request (its author is on no allowlist
entry, so the ordinary contract judges it). `--early` is pr-contract's signal:
a class-O read still owed prints `PENDING:` and does not refuse. With
`--pull-json` it makes no API call at all (the job's API step read the pull
request into a file; this program is handed no token), so it reads neither
the reviews nor the other pull requests at the head: adoption does.

WHERE THE RULES ARE READ. The programs are this file's own tree: `bus.sh adopt`
runs main's copy from a throwaway directory, pr-contract the base's restored
copy. The DATA (the allowlist, CODEOWNERS) is read with `git show <ref>:<path>`,
never from a checkout a head could have written. Nothing here executes, checks
out or imports anything of the head: git objects and the API only.

`cross` answers one fact for a shell caller: rc 0 and `CROSS-REPOSITORY` when
the pull request's head lives in another repository, rc 3 and
`SAME-REPOSITORY` when it is ours, rc 1 and `REFUSE:` when it could not be read.
A Python caller imports `cross_repository(pull_facts(repo, pr), repo)`.

THE CLASSES, first match wins, default deny:
  R  refused: .github/, tools/, .claude/, .cursor/, the policy set
     (policy_lint.mjs's POLICY_GLOBS and POLICY_DIRS, read from that file),
     any *_budgets.json, tests/closures.json, tests/golden/,
     tests/mutation_ledger/, every tests/closure.py GATE_FILES entry, every
     root file but README.md, and any path in no class.
  F  free: custom_components/, blueprints/, README.md, a *.md, *.png or *.svg
     under docs/ outside docs/site/ and outside every CODEOWNERS line, and the
     pull request's own dev/programme/delivery/<N>.md.
  O  owner-read: every other path under tests/ or docs/, and any other
     CODEOWNERS-matched path.
R is tested first: no R rule lies under an F prefix (the self-test holds that
over the tracked tree), so the order changes no answer and a later R rule
cannot be shadowed by F.

CLASS O is the owner's LATEST decisive review on the pull request, admitted
only when it is APPROVED, carries the outside-read line naming a commit L that
is the head or carries to it (`app_approve.sh --carry`), sits at L, at the head
or at a commit between them that carries both ways, and is one of two forms:
the owner's own (it declares no agent and cites no mandate), or the
machinery's (it declares an agent and cites exactly one mandate that is in
force NOW with the gate's MANDATE_COVERS_POLICY scope, and the owner's own
latest decisive review is not CHANGES_REQUESTED). The mandate, the owner's
identity and both patterns are budget_raise_gate.py's, imported, never
re-typed. `approve` is the one writer of the machinery's form.
"""
import argparse
import ast
import datetime
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST = "dev/governance/config/outside_contributors.json"
CODEOWNERS = ".github/CODEOWNERS"
MANIFEST = "custom_components/heatpump_optimizer/manifest.json"
# Matched whole with fullmatch: `$` under match admits a trailing newline.
HEAD_REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,99}")
READ_WORDS = "Outside read:"
READ_LINE = re.compile(r"^" + READ_WORDS + r" ([0-9a-f]{40})$", re.M)
DECISIVE = ("APPROVED", "CHANGES_REQUESTED", "DISMISSED")
SHA40 = re.compile(r"[0-9a-f]{40}")


class Refuse(Exception):
    """A read that failed: nothing unread is ever read as a pass."""


def load_gate(root: Path = ROOT):
    """budget_raise_gate.py of THIS tree, by path (main's at adoption)."""
    p = root / "tools/policy/budget_raise_gate.py"
    spec = importlib.util.spec_from_file_location("budget_raise_gate", str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- plumbing: every command is a list, nothing is interpolated into a shell --

def _run(argv: "list[str]", stdin: "str | None" = None) -> "tuple[int, str, str]":
    r = subprocess.run(argv, capture_output=True, text=True, input=stdin)
    return r.returncode, r.stdout, r.stderr


def api(path: str, pages: bool = False):
    argv = ["gh", "api"] + (["--paginate", "--slurp"] if pages else []) + [path]
    rc, out, err = _run(argv)
    if rc:
        raise Refuse(f"gh api {path.split('?')[0]} exited {rc}: {err.strip()[:160]}")
    try:
        data = json.loads(out)
    except ValueError:
        raise Refuse(f"gh api {path.split('?')[0]} answered no JSON") from None
    if not pages:
        return data
    if not isinstance(data, list) or not all(isinstance(p, list) for p in data):
        raise Refuse(f"gh api {path.split('?')[0]} answered no list of pages")
    return [x for page in data for x in page]


def git(*args: str) -> str:
    rc, out, err = _run(["git", *args])
    if rc:
        raise Refuse(f"git {args[0]} exited {rc}: {err.strip()[:160]}")
    return out


def show(ref: str, path: str) -> "str | None":
    rc, out, _ = _run(["git", "show", f"{ref}:{path}"])
    return out if rc == 0 else None


def carries(lsha: str, head: str, ref: str) -> bool:
    """`app_approve.sh --carry` of this tree: on a head that is no branch of
    ours it carries the automatic merge of main and nothing else."""
    rc, _, _ = _run(["bash", str(ROOT / "tools/pr/app_approve.sh"), "--carry", lsha, head, ref])
    return rc == 0


def now_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


# --- the rules' sources -------------------------------------------------------

def policy_patterns(root: Path = ROOT) -> "list[re.Pattern]":
    """POLICY_GLOBS and POLICY_DIRS as policy_lint.mjs writes them: the regex
    literals of the two arrays, read from the file. Either array missing or
    empty refuses: a policy set that reads as empty would class policy free."""
    text = (root / "tools/policy/policy_lint.mjs").read_text(encoding="utf-8")
    out = []
    for name in ("POLICY_GLOBS", "POLICY_DIRS"):
        m = re.search(r"^const " + name + r" = \[(.*?)^\]", text, re.M | re.S) \
            or re.search(r"^const " + name + r" = \[(.*?)\]$", text, re.M | re.S)
        lits = re.findall(r"(?m)(?:^|[\[,])\s*/((?:\\.|[^/\\\n])+)/,?", m.group(1)) if m else []
        if not lits:
            raise Refuse(f"policy_lint.mjs holds no readable {name}")
        out += [re.compile(lit.replace("\\/", "/")) for lit in lits]
    return out


def gate_files(root: Path = ROOT) -> "tuple[str, ...]":
    """tests/closure.py's GATE_FILES, read as a literal and never imported."""
    tree = ast.parse((root / "tests/closure.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "GATE_FILES" for t in node.targets):
            val = ast.literal_eval(node.value)
            if val and all(isinstance(v, str) for v in val):
                return tuple(val)
    raise Refuse("tests/closure.py holds no literal GATE_FILES")


def owner_patterns(text: "str | None") -> "list[re.Pattern]":
    """Every CODEOWNERS pattern that names an owner. Matching errs toward
    owning (any such line, never last-match): owned is the stricter class."""
    if text is None:
        raise Refuse(f"{CODEOWNERS} could not be read")
    out = []
    for line in text.splitlines():
        parts = line.partition("#")[0].split()
        if len(parts) < 2:
            continue
        pat = parts[0]
        isdir = pat.endswith("/")
        core = pat.strip("/")
        anchored = pat.startswith("/") or "/" in core
        body = "".join(".*" if tok == "**" else "[^/]*" if tok == "*" else "[^/]" if tok == "?" else re.escape(tok)
                       for tok in re.findall(r"\*\*|\*|\?|[^*?]+", core))
        out.append(re.compile(("" if anchored else "(?:.*/)?") + body + ("/.*" if isdir else "(?:/.*)?")))
    if not out:
        raise Refuse(f"{CODEOWNERS} holds no rules")
    return out


class Rules:
    def __init__(self, ref: str, root: Path = ROOT, codeowners: "str | None" = None):
        self.policy = policy_patterns(root)
        self.gate = gate_files(root)
        self.owned = owner_patterns(show(ref, CODEOWNERS) if codeowners is None else codeowners)

    def is_owned(self, path: str) -> bool:
        return any(p.fullmatch(path) for p in self.owned)

    def refused(self, path: str) -> bool:
        return (path.startswith((".github/", "tools/", ".claude/", ".cursor/", "tests/golden/", "tests/mutation_ledger/"))
                or any(p.search(path) for p in self.policy)
                or path.endswith("_budgets.json")
                or path == "tests/closures.json"
                or path in self.gate
                or ("/" not in path and path != "README.md"))

    def free(self, path: str, pr: int) -> bool:
        if path.startswith(("custom_components/", "blueprints/")) or path == "README.md":
            return True
        if path == f"dev/programme/delivery/{pr}.md":
            return True
        return (path.startswith("docs/") and not path.startswith("docs/site/")
                and path.endswith((".md", ".png", ".svg")) and not self.is_owned(path))

    def classify(self, path: str, pr: int) -> str:
        if self.refused(path):
            return "R"
        if self.free(path, pr):
            return "F"
        if path.startswith(("tests/", "docs/")) or self.is_owned(path):
            return "O"
        return "R"  # default deny: a path in no class


def allowlisted(user, allow) -> "dict | None":
    """The allowlist entry `user` (an API user object) matches by login,
    numeric id and type User, or None."""
    user = user or {}
    if user.get("type") != "User":
        return None
    for e in (allow or {}).get("contributors") or []:
        if isinstance(e, dict) and isinstance(e.get("id"), int) and e.get("login") == user.get("login") and e["id"] == user.get("id"):
            return e
    return None


def read_allowlist(ref: str) -> dict:
    text = show(ref, ALLOWLIST)
    if text is None:
        raise Refuse(f"{ALLOWLIST} is not at {ref}")
    try:
        data = json.loads(text)
    except ValueError:
        raise Refuse(f"{ALLOWLIST} at {ref} is not JSON") from None
    if not isinstance(data, dict) or not isinstance(data.get("contributors"), list):
        raise Refuse(f"{ALLOWLIST} at {ref} holds no contributors list")
    return data


# --- class O ------------------------------------------------------------------

def mandate_now(gate, repo: str, cid: int) -> "tuple[bool, str]":
    """The mandate `cid`, read live through the gate's own two functions and
    judged at this instant for the policy scope; an unread one grants nothing."""
    try:
        comment, thread = gate._mandate(repo, cid)
    except Exception as e:  # fail closed
        return False, f"mandate {cid} could not be read ({str(e).splitlines()[0][:160] if str(e) else type(e).__name__})"
    now = now_utc()
    return gate.mandate_state(cid, comment, thread, now, now.strftime("%Y-%m-%dT%H:%M:%SZ"), "class-O read",
                              gate.MANDATE_COVERS_POLICY, "an outside pull request's class-O paths")


def owner_read(reviews: "list[dict]", head: str, gate, repo: str, carry) -> "tuple[bool, str]":
    """(admitted, why): the class-O approval at `head`. `carry(L, head)` says
    whether the commit L reaches `head` by automatic merges of main only."""
    own = [r for r in reviews if gate._is_owner(r.get("user")) and r.get("state") in DECISIVE]
    if not own:
        return False, f"no decisive review by {gate.OWNER_LOGIN} (id {gate.OWNER_ID}) on this pull request"
    last = own[-1]
    rid, body = last.get("id"), last.get("body") or ""
    if last.get("state") != "APPROVED":
        return False, f"{gate.OWNER_LOGIN}'s latest review {rid} is {last.get('state')}, which voids any earlier approval"
    lines = READ_LINE.findall(body)
    if len(lines) != 1:
        return False, (f"review {rid} carries {len(lines)} lines of the form `{READ_WORDS} <sha40>` on a line of "
                       "their own, and exactly one says which commit was read")
    lsha = lines[0]
    if lsha != head and not carry(lsha, head):
        return False, f"review {rid} read {lsha[:12]}, which does not carry to this head {head[:12]}"
    cid = last.get("commit_id")
    if cid not in (lsha, head) and not (isinstance(cid, str) and SHA40.fullmatch(cid) and carry(lsha, cid) and carry(cid, head)):
        return False, (f"review {rid} sits on {str(cid)[:12]}, which is neither the commit it read "
                       f"({lsha[:12]}), this head, nor a commit that carries between them")
    declared = bool(gate.AGENT_DECLARED.search(body))
    cited = {int(a or b) for a, b in gate.MANDATE_CITE.findall(body)}
    if not declared and not cited:
        return True, f"{gate.OWNER_LOGIN} approved the class-O paths at {lsha[:12]} (review {rid})"
    if not declared:
        return False, f"review {rid} cites a mandate and declares no agent: neither the owner's own form nor the machinery's"
    if len(cited) != 1:
        return False, f"review {rid} declares an agent and cites {len(cited)} mandates, and exactly one decides"
    mid = cited.pop()
    ok, why = mandate_now(gate, repo, mid)
    if not ok:
        return False, f"review {rid} is an agent's, and {why}"
    theirs = [r for r in own if not gate.AGENT_DECLARED.search(r.get("body") or "")]
    if theirs and theirs[-1].get("state") == "CHANGES_REQUESTED":
        return False, (f"{gate.OWNER_LOGIN}'s own latest decisive review is CHANGES_REQUESTED, and a mandated "
                       "approval does not override it")
    return True, f"an agent approved the class-O paths at {lsha[:12]} under {gate.OWNER_LOGIN}'s account (review {rid}), under {why}"


# --- the contract -------------------------------------------------------------

def pull_facts(repo: str, pr: int, pull: "dict | None" = None) -> dict:
    p = api(f"repos/{repo}/pulls/{pr}") if pull is None else pull
    if not isinstance(p, dict) or p.get("number") != pr:
        raise Refuse(f"the pull request read is not #{pr}")
    head, base = p.get("head") or {}, p.get("base") or {}
    return {"author": p.get("user") or {}, "state": p.get("state"),
            "head_repo": (head.get("repo") or {}).get("full_name"), "head_ref": head.get("ref"),
            "head_owner": ((head.get("repo") or {}).get("owner") or {}).get("login"),
            "head": head.get("sha"), "base_repo": (base.get("repo") or {}).get("full_name"),
            "base_ref": base.get("ref")}


def cross_repository(f: dict, repo: str) -> bool:
    """THE definition of a cross-repository head, for every reader (the merge
    train and merge_pr.sh import or call it, never re-type it): the head lives
    in another repository than `repo`. A head repository that is gone is not
    ours either. `f` is pull_facts' answer."""
    return f["head_repo"] != repo


def shape(f: dict, repo: str) -> "list[str]":
    """Steps 2 and 5: a cross-repository head on main of ours, under a head
    ref name no shell expands."""
    out = []
    if not f["head_repo"] or not cross_repository(f, repo):
        out.append(f"the head repository is {f['head_repo'] or 'gone'}: an outside pull request comes from a fork, "
                   "and a branch of ours is authored by the hpo-author App (decision 0011)")
    if f["base_repo"] != repo or f["base_ref"] != "main":
        out.append(f"the base is {f['base_repo']}:{f['base_ref']}, not {repo}:main")
    ref = f["head_ref"]
    if not isinstance(ref, str) or not HEAD_REF.fullmatch(ref) or ref == "main":
        out.append(f"the head branch name {ref!r} is outside [A-Za-z0-9][A-Za-z0-9._/-]{{0,99}} or is `main`: "
                   "rename the branch (letters, digits, dot, underscore, dash, slash; at most 100 characters)")
    if not isinstance(f["head"], str) or not SHA40.fullmatch(f["head"]):
        out.append("the pulls API names no 40-hex head")
    return out


def other_pulls(repo: str, pr: int, f: dict) -> "list[int]":
    """Step 7: every other pull request, of any state, whose head is this head.
    Its runs leave check runs of the same names on the commit."""
    seen = set()
    for p in api(f"repos/{repo}/commits/{f['head']}/pulls?per_page=100", pages=True):
        if (p.get("head") or {}).get("sha") == f["head"]:
            seen.add(p.get("number"))
    for p in api(f"repos/{repo}/pulls?state=all&head={f['head_owner']}:{f['head_ref']}&per_page=100", pages=True):
        if (p.get("head") or {}).get("sha") == f["head"]:
            seen.add(p.get("number"))
    return sorted(n for n in seen if n != pr)


def manifest_version(ref: str) -> "tuple[bool, object]":
    text = show(ref, MANIFEST)
    if text is None:
        return True, None
    try:
        return True, json.loads(text).get("version")
    except (ValueError, AttributeError):
        return False, None


def changed(ref: str, head: str) -> "tuple[str, list[str]]":
    base = git("merge-base", ref, head).strip()
    return base, [p for p in git("-c", "core.quotepath=off", "diff", "--no-renames", "--name-only", f"{base}...{head}").splitlines() if p]


def check(repo: str, pr: int, ref: str, gate=None, fetch: bool = True, early: bool = False,
          comment: "int | None" = None, pull: "dict | None" = None) -> "tuple[int, list[str]]":
    """The whole contract. (rc, lines): 0 admitted, 1 refused, 3 not outside.
    `pull` is pr-contract's form: the pulls API's answer as a caller already
    read it, judged with no API call here. That form reads neither the other
    pull requests at the head nor the reviews, so it is `early` only: it can
    say PENDING, never that class O is met."""
    gate = gate or load_gate()
    try:
        if pull is not None and not early:
            return 1, ["REFUSE: a pull request handed in as a file is the early signal's form; the gate reads the API itself"]
        f = pull_facts(repo, pr, pull)
        allow = read_allowlist(ref)
        entry = allowlisted(f["author"], allow)
        if entry is None:
            return 3, [f"NOT OUTSIDE: #{pr}'s author {f['author'].get('login')!r} (id {f['author'].get('id')}, "
                       f"type {f['author'].get('type')}) matches no entry of {ALLOWLIST} at {ref}"]
        out = shape(f, repo)
        if f["state"] != "open":
            out.append(f"the pull request is {f['state']}, not open")
        if comment is not None:
            c = api(f"repos/{repo}/issues/comments/{comment}")
            if not str(c.get("issue_url") or "").endswith(f"/repos/{repo}/issues/{pr}"):
                out.append(f"comment {comment} is not an issue comment of #{pr}")
            if allowlisted(c.get("user"), allow) is not entry:
                out.append(f"comment {comment}'s author {(c.get('user') or {}).get('login')!r} is not the pull "
                           "request author's allowlist entry by login, id and type")
        if out:
            return 1, ["REFUSE: " + o for o in out]
        head = f["head"]
        if fetch:
            git("fetch", "-q", "--no-tags", "origin", f"+refs/pull/{pr}/head:refs/hpo-outside/{pr}")
            if git("rev-parse", f"refs/hpo-outside/{pr}").strip() != head:
                return 1, [f"REFUSE: refs/pull/{pr}/head is not the head {head} the API names (it moved; run again)"]
        others = other_pulls(repo, pr, f) if pull is None else []
        if others:
            out.append(f"the head {head[:12]} is also the head of #{', #'.join(map(str, others))}: its runs leave "
                       "check runs of the same names on this commit, so close it and push a new head")
        base, paths = changed(ref, head)
        if not paths:
            out.append(f"the diff {base[:12]}...{head[:12]} names no path")
        rules = Rules(ref)
        classes = {p: rules.classify(p, pr) for p in paths}
        for p in sorted(p for p, c in classes.items() if c == "R"):
            out.append(f"class R: {p} is a path an outside pull request does not change (decision 0017)")
        if MANIFEST in classes:
            (ok_b, vb), (ok_h, vh) = manifest_version(base), manifest_version(head)
            if not (ok_b and ok_h) or vb != vh:
                out.append(f"{MANIFEST}'s version changes ({vb!r} -> {vh!r}): versions are assigned after the merge, by stamp.py")
        opaths = sorted(p for p, c in classes.items() if c == "O")
        lines = []
        if opaths and not out and pull is not None:
            lines.append(f"PENDING: class O ({', '.join(opaths[:6])}{' ...' if len(opaths) > 6 else ''}) needs the owner's "
                         f"approving review at {head[:12]}, or his machinery's under his mandate; adoption reads it")
        elif opaths and not out:
            ok, why = owner_read(api(f"repos/{repo}/pulls/{pr}/reviews?per_page=100", pages=True), head, gate, repo,
                                 lambda a, b: carries(a, b, ref))
            if ok:
                lines.append(f"CLASS O: {why}")
            elif early:
                lines.append(f"PENDING: class O ({', '.join(opaths[:6])}{' ...' if len(opaths) > 6 else ''}) is not yet read at {head[:12]}: {why}")
            else:
                out.append(f"class O: {', '.join(opaths[:6])}{' ...' if len(opaths) > 6 else ''} need the owner's "
                           f"approving review at {head[:12]}, or his machinery's under his mandate: {why}")
        if out:
            return 1, ["REFUSE: " + o for o in out]
        n = {c: sum(1 for v in classes.values() if v == c) for c in "FO"}
        return 0, lines + [f"OUTSIDE: #{pr} by {entry['login']} (id {entry['id']}) at {head}: {n['F']} class-F and {n['O']} class-O path(s), none refused"]
    except Refuse as e:
        return 1, [f"REFUSE: {e} (an unread fact refuses)"]


def cross(repo: str, pr: int) -> "tuple[int, str]":
    """The `cross` subcommand: (rc, line)."""
    try:
        f = pull_facts(repo, pr)
    except Refuse as e:
        return 1, f"REFUSE: {e} (whether #{pr}'s head is cross-repository is unread)"
    if cross_repository(f, repo):
        return 0, f"CROSS-REPOSITORY #{pr}: head repository {f['head_repo'] or 'gone'}, not {repo}"
    return 3, f"SAME-REPOSITORY #{pr}: head repository {repo}"


# --- the one writer of the machinery's class-O approval -------------------------

def approval_body(pr: int, head: str, mandate: int, paths: "list[str]", role: str) -> str:
    return (f"Agent approval of the class-O paths of outside pull request #{pr}, given by {role}, a seat and not "
            f"tvofi in person, under mandate comment {mandate}.\n\n"
            "Class-O paths read: " + ", ".join(f"`{p}`" for p in paths) + "\n\n"
            f"{READ_WORDS} {head}\n")


def approve(repo: str, pr: int, head: str, mandate: "int | None", ref: str, role: str, gate=None,
            fetch: bool = True) -> "tuple[int, list[str]]":
    gate = gate or load_gate()
    try:
        if mandate is None:
            return 1, ["REFUSE: --mandate <comment id> is required and never defaulted: a stale default is a forged grant"]
        f = pull_facts(repo, pr)
        entry = allowlisted(f["author"], read_allowlist(ref))
        out = [] if entry else [f"#{pr}'s author is on no allowlist entry: not an outside pull request"]
        out += shape(f, repo)
        if f["head"] != head:
            out.append(f"the live head is {f['head']}, not the head read, {head}")
        if out:
            return 1, ["REFUSE: " + o for o in out]
        if fetch:
            git("fetch", "-q", "--no-tags", "origin", f"+refs/pull/{pr}/head:refs/hpo-outside/{pr}")
        if other_pulls(repo, pr, f):
            return 1, ["REFUSE: another pull request has this head"]
        _, paths = changed(ref, head)
        rules = Rules(ref)
        classes = {p: rules.classify(p, pr) for p in paths}
        if "R" in classes.values():
            return 1, ["REFUSE: the diff holds a class-R path; nothing is approved on a head adoption refuses"]
        opaths = sorted(p for p, c in classes.items() if c == "O")
        if not opaths:
            return 1, ["REFUSE: the diff holds no class-O path, so there is nothing for this approval to read"]
        ok, why = mandate_now(gate, repo, mandate)
        if not ok:
            return 1, [f"REFUSE: {why}"]
        if not gate._is_owner(api("user")):
            return 1, [f"REFUSE: gh is not authenticated as {gate.OWNER_LOGIN} (id {gate.OWNER_ID}); only that account's review can be class O"]
        reviews = api(f"repos/{repo}/pulls/{pr}/reviews?per_page=100", pages=True)
        theirs = [r for r in reviews if gate._is_owner(r.get("user")) and r.get("state") in DECISIVE
                  and not gate.AGENT_DECLARED.search(r.get("body") or "")]
        if theirs and theirs[-1].get("state") == "CHANGES_REQUESTED":
            return 1, [f"REFUSE: {gate.OWNER_LOGIN}'s own latest decisive review is CHANGES_REQUESTED; a mandate never overrules him"]
        body = approval_body(pr, head, mandate, opaths, role)
        cited = {int(a or b) for a, b in gate.MANDATE_CITE.findall(body)}
        if cited != {mandate} or not gate.AGENT_DECLARED.search(body) or READ_LINE.findall(body) != [head]:
            return 1, ["REFUSE: the body built does not read back as declared, citing this mandate alone and naming this head"]
        # The reviews API with commit_id, never `gh pr review`, which anchors at
        # whatever the head is at the post.
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as t:
            json.dump({"commit_id": head, "event": "APPROVE", "body": body}, t)
        try:
            rc, o, err = _run(["gh", "api", "-X", "POST", f"repos/{repo}/pulls/{pr}/reviews", "--input", t.name])
        finally:
            os.unlink(t.name)
        if rc:
            return 1, [f"REFUSE: the review was refused: {err.strip()[:200]}"]
        back = api(f"repos/{repo}/pulls/{pr}/reviews?per_page=100", pages=True)
        if not any(r.get("commit_id") == head and (r.get("body") or "") == body and r.get("state") == "APPROVED" for r in back):
            return 1, ["REFUSE: the approval did not read back byte-identical at the head; a failed read-back approves nothing"]
        ok, why = owner_read(back, head, gate, repo, lambda a, b: carries(a, b, ref))
        if not ok:
            return 1, [f"REFUSE: the approval landed and the class-O check does not admit it: {why}"]
        return 0, [f"APPROVED: {why}"]
    except Refuse as e:
        return 1, [f"REFUSE: {e} (an unread fact refuses)"]


# --- self-test ------------------------------------------------------------------

def self_test() -> int:
    global carries, show, changed, now_utc
    g = load_gate()
    fails = n = 0

    def st(got, want, what):
        nonlocal fails, n
        n += 1
        if got != want:
            fails += 1
        print(("ok   " if got == want else "FAIL ") + what + ("" if got == want else f" (got {got!r}, want {want!r})"))

    R, PR = g.DEFAULT_REPO, 7
    H, L, X, Z = "a" * 40, "b" * 40, "c" * 40, "d" * 40
    OWN = {"login": g.OWNER_LOGIN, "id": g.OWNER_ID, "type": g.OWNER_TYPE}
    BK = {"login": "bankaifan", "id": 555001, "type": "User"}
    MID, RID = 4100000001, 4100000002
    NOW = datetime.datetime(2026, 11, 12, 12, 0, tzinfo=datetime.timezone.utc)
    iso = lambda m: (NOW + datetime.timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: E731
    real_now = now_utc
    now_utc = lambda: NOW  # noqa: E731

    def mandate(scope="all", start=-60, until=60, user=OWN, issue=None, repo=R, edited=False, body=None):
        c = iso(start)
        return {"id": MID, "user": user, "created_at": c, "updated_at": iso(start + 1) if edited else c,
                "issue_url": f"https://api.github.com/repos/{repo}/issues/{issue or g.RECORD_ISSUE}",
                "body": body or f"MANDATE: agents may approve as {g.OWNER_LOGIN}, scope {scope}, from {c} until {iso(until)}"}

    def rv(body, state="APPROVED", sha=H, user=OWN, rid=None):
        rv.n += 1
        return {"id": rid or 9000 + rv.n, "user": user, "state": state, "commit_id": sha, "body": body,
                "submitted_at": iso(-30)}
    rv.n = 0

    def pull(author=BK, head_repo="bankaifan/heatpump_optimizer", ref="fix/issue-12_a.b", sha=H, base_repo=R,
             base_ref="main", state="open", number=PR):
        return {"number": number, "user": author, "state": state,
                "head": {"sha": sha, "ref": ref, "repo": {"full_name": head_repo, "owner": {"login": "bankaifan"}} if head_repo else None},
                "base": {"ref": base_ref, "repo": {"full_name": base_repo}}}

    # A fake `gh`: every `gh` call of this module AND of the gate's `_mandate`
    # is answered from `routes`; a missing route is a 404, "ERR" a server error.
    world = {"routes": {}, "me": OWN, "log": [], "mangle": False, "paths": [], "files": {}, "carry": set()}
    real_run = subprocess.run

    class Done:
        def __init__(self, rc, out="", err=""):
            self.returncode, self.stdout, self.stderr = rc, out, err

    def fake_run(argv, **kw):
        if not argv or argv[0] != "gh":
            return real_run(argv, **kw)
        world["log"].append(" ".join(argv))
        args, post, inp, slurp, ep = argv[2:], False, None, False, None
        i = 0
        while i < len(args):
            a = args[i]
            if a == "-X":
                post = args[i + 1] == "POST"; i += 2
            elif a == "--input":
                inp = args[i + 1]; i += 2
            elif a in ("--paginate", "--slurp"):
                slurp = slurp or a == "--slurp"; i += 1
            else:
                ep = a; i += 1
        key = ep.split("?")[0]
        if post:
            d = json.load(open(inp))
            r = {"id": 9900 + len(world["log"]), "user": world["me"], "state": "APPROVED", "commit_id": d["commit_id"],
                 "body": d["body"] + ("mangled" if world["mangle"] else ""), "submitted_at": iso(0)}
            world["routes"].setdefault(key, []).append(r)
            return Done(0, json.dumps(r))
        if key == "user":
            return Done(0, json.dumps(world["me"]))
        val = world["routes"].get(key, [] if re.search(r"/issues/\d+/comments$|/commits/[0-9a-f]+/pulls$|/pulls$", key) else None)
        if val is None:
            return Done(1, "", "gh: Not Found (HTTP 404)")
        if val == "ERR":
            return Done(1, "", "gh: Server Error (HTTP 500)")
        if val == "RAW":
            return Done(0, "<html>not json</html>")
        return Done(0, json.dumps([val] if slurp else val))

    ALLOW = {"contributors": [{"login": "bankaifan", "id": 555001, "since": "2026-11-12", "decision": "0017"}]}
    OWNERS = "/.github/workflows/ @tvofi\n/dev/governance/ @tvofi\n/docs/ownedir/ @tvofi\n/docs/owned.md @tvofi\n/dev/x/unowned.md\n"

    def fake_show(ref, path):
        return world["files"].get((ref, path), world["files"].get(path))

    def reset(reviews=(), mand="live", paths=("custom_components/heatpump_optimizer/x.py",), **pullkw):
        world.update(routes={}, me=OWN, log=[], mangle=False, paths=list(paths), carry=set(),
                     files={ALLOWLIST: json.dumps(ALLOW), CODEOWNERS: OWNERS})
        ro = world["routes"]
        ro[f"repos/{R}/pulls/{PR}"] = pull(**pullkw)
        ro[f"repos/{R}/pulls/{PR}/reviews"] = list(reviews)
        if mand is not None:
            ro[f"repos/{R}/issues/comments/{MID}"] = mandate() if mand == "live" else mand
        return ro

    subprocess.run = fake_run
    real = carries, show, changed
    carries = lambda a, b, ref: (a, b) in world["carry"]  # noqa: E731
    show = fake_show
    changed = lambda ref, head: ("e" * 40, list(world["paths"]))  # noqa: E731
    try:
        def chk(**kw):
            rc, lines = check(R, PR, "origin/main", gate=g, fetch=False, **kw)
            return rc, " | ".join(lines)

        # --- the API read itself ---------------------------------------------
        def refuses(fn, word):
            try:
                fn()
            except Refuse as e:
                return word in str(e)
            return False

        ro = reset(); ro["k"] = {"a": 1}; ro["raw"] = "RAW"; ro["err"] = "ERR"
        st(api("k"), {"a": 1}, "api(): one document comes back parsed")
        st(refuses(lambda: api("k", pages=True), "no list of pages"), True, "api(): a paginated answer whose page is no list refuses")
        st(refuses(lambda: api("absent"), "exited 1"), True, "api(): a 404 refuses, naming gh's exit")
        st(refuses(lambda: api("err"), "exited 1"), True, "api(): a server error refuses, naming gh's exit")
        st(refuses(lambda: api("raw"), "no JSON"), True, "api(): an answer that is not JSON refuses")
        st(_run(["git", "--version"])[1].startswith("git version"), True, "_run(): a command's stdout is captured")

        # --- admission -------------------------------------------------------
        reset(); rc, out = chk()
        st(rc, 0, "admitted: an allowlisted login+id on a cross-repository head touching class F")
        reset(); world["files"][ALLOWLIST] = json.dumps({"contributors": []}); rc, out = chk()
        st(rc, 3, "(null control) the allowlist entry removed: the same pull request is not an outside one")
        reset(author={**BK, "id": 555002}); st(chk()[0], 3, "not outside: the login under another numeric id")
        reset(author={**BK, "type": "Bot"}); st(chk()[0], 3, "not outside: the login and id on a Bot record")
        reset(author={**BK, "login": "bankaifan2"}); st(chk()[0], 3, "not outside: the id under another login")
        reset(); world["files"][ALLOWLIST] = json.dumps({"contributors": [{"login": "bankaifan", "id": "555001"}]})
        st(chk()[0], 3, "not outside: an allowlist id recorded as a string matches nothing")
        reset(); del world["files"][ALLOWLIST]; rc, out = chk()
        st((rc, "is not at origin/main" in out), (1, True), "REFUSE: the allowlist unreadable at the ref")
        reset(head_repo=R); rc, out = chk()
        st((rc, "comes from a fork" in out), (1, True), "REFUSE: a same-repository head")
        reset(head_repo=None); st(chk()[0], 1, "REFUSE: a head repository that is gone")
        reset(); st(cross(R, PR)[0], 0, "cross: a fork's head is cross-repository (rc 0)")
        reset(head_repo=R); st(cross(R, PR)[0], 3, "cross: a head of ours is not (rc 3)")
        reset(head_repo=None); st(cross(R, PR)[0], 0, "cross: a head repository that is gone is not ours")
        ro = reset(); ro[f"repos/{R}/pulls/{PR}"] = "ERR"; st(cross(R, PR)[0], 1, "cross: an unreadable pull request refuses, never read as ours")
        reset(base_ref="release"); rc, out = chk()
        st((rc, "not tvofi/heatpump_optimizer:main" in out), (1, True), "REFUSE: a base other than main")
        reset(base_repo="bankaifan/heatpump_optimizer"); st(chk()[0], 1, "REFUSE: main of another repository as the base")
        reset(state="closed"); st(chk()[0], 1, "REFUSE: a closed pull request")
        ro = reset(); ro[f"repos/{R}/commits/{H}/pulls"] = [pull(), pull(number=8)]; rc, out = chk()
        st((rc, "also the head of #8" in out), (1, True), "REFUSE: a second open pull request at the head")
        ro = reset(); ro[f"repos/{R}/pulls"] = [pull(number=9, state="closed")]; rc, out = chk()
        st((rc, "also the head of #9" in out), (1, True), "REFUSE: a CLOSED pull request at the head (its runs left check runs on the commit)")
        ro = reset(); ro[f"repos/{R}/pulls"] = [pull(number=9, sha=Z)]
        st(chk()[0], 0, "(null control) another pull request of the same branch at another commit refuses nothing")
        ro = reset(); ro[f"repos/{R}/commits/{H}/pulls"] = "ERR"; st(chk()[0], 1, "REFUSE: the other-pull-requests read failed")
        ro = reset(); ro[f"repos/{R}/pulls/{PR}"] = "ERR"; st(chk()[0], 1, "REFUSE: the pull request unreadable")
        reset(paths=()); st(chk()[0], 1, "REFUSE: an empty diff is not a thing a pull request has")
        # The comment adoption names (item 7).
        ro = reset(); ro[f"repos/{R}/issues/comments/31"] = {"user": BK, "issue_url": f"https://api.github.com/repos/{R}/issues/{PR}"}
        st(chk(comment=31)[0], 0, "admitted: the verdict comment is the author's allowlist entry's, on this pull request")
        ro[f"repos/{R}/issues/comments/31"]["issue_url"] = f"https://api.github.com/repos/{R}/issues/8"
        st(chk(comment=31)[0], 1, "REFUSE: the comment is on another pull request")
        ro[f"repos/{R}/issues/comments/31"] = {"user": {**BK, "id": 4}, "issue_url": f"https://api.github.com/repos/{R}/issues/{PR}"}
        st(chk(comment=31)[0], 1, "REFUSE: the comment's author is not the allowlist entry")
        st(chk(comment=32)[0], 1, "REFUSE: the comment does not exist")

        # --- the head ref name ------------------------------------------------
        for bad in ('a";$(id)', "a b", "a$b", "a`b", "-a", "x" * 101, "main", "a\n", "fix/ok\n", "", "a;b", "a(b)", "a~1", "a*"):
            reset(ref=bad); rc, out = chk()
            st((rc, "head branch name" in out), (1, True), f"REFUSE: the head branch name {bad[:20]!r}{'...' if len(bad) > 20 else ''}")
        for good in ("fix/issue-12_a.b", "x" * 100, "A", "0/9"):
            reset(ref=good); st(chk()[0], 0, f"admitted: the head branch name {good[:20]!r}")
        reset(ref=None); st(chk()[0], 1, "REFUSE: no head ref in the API's answer")

        # --- the classes -------------------------------------------------------
        rules = Rules("origin/main")
        cl = lambda p: rules.classify(p, PR)  # noqa: E731
        for p in (".github/workflows/tests.yml", ".github/CODEOWNERS", "tools/pr/outside.py", ".claude/settings.json",
                  ".cursor/rules/x.mdc", "CLAUDE.md", "AGENTS.md", "dev/governance/roles/fixer.md", ALLOWLIST,
                  "dev/governance/decisions/0017-x.md", "dev/audit/README.md", "tests/README.md",
                  "tests/structure_budgets.json", "dev/governance/config/policy_budgets.json", "x/new_budgets.json",
                  "tests/closures.json", "tests/golden/claimed_drift.txt", "tests/golden/a/b.json",
                  "tests/mutation_ledger/killed_by/a.json", "tests/run.sh", "tests/closure.py", "VERSION",
                  "RELEASE_NOTES.md", ".gitattributes", "LICENSE", "newroot.txt", "dev/programme/delivery/8.md",
                  "dev/programme/HANDOVER.md", "scripts/new.sh", "dev/x/unowned.md", "custom_componentsx/a.py"):
            st(cl(p), "R", f"class R: {p}")
        for p in ("custom_components/heatpump_optimizer/coordinator.py", "blueprints/a.yaml", "README.md",
                  "docs/setup.md", "docs/img/card/plan-dark.png", "docs/img/brand/coffee.svg", "dev/programme/delivery/7.md"):
            st(cl(p), "F", f"class F: {p}")
        for p in ("docs/index.html", "docs/site/docs.css", "docs/site/readme.md", "docs/img/readme/render.mjs",
                  "docs/img/model/make_model_figures.py", "docs/img/card/pages.json", "docs/owned.md",
                  "docs/ownedir/0001.md", "tests/entities.py", "tests/structure.py", "tests/new_test.py",
                  "tests/hastub/homeassistant/core.py"):
            st(cl(p), "O", f"class O: {p}")
        st(len(rules.policy) >= 10 and len(rules.gate) >= 5, True, "the policy patterns and GATE_FILES were read, not empty")
        # The tracked tree; in an export with no .git, every file of the export.
        tracked = real_run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True).stdout.splitlines() \
            or [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.relative_to(ROOT).parts]
        st(len(tracked) > 100, True, "the tracked tree was listed (the next four checks read it)")
        st([p for p in rules.gate if cl(p) != "R"], [], "every closure.GATE_FILES entry classifies R")
        st([p for p in tracked if p.endswith("_budgets.json") and cl(p) != "R"], [], "every tracked *_budgets.json classifies R")
        st([p for p in tracked if rules.refused(p) and rules.free(p, PR)], [], "no tracked R path lies under an F rule, so the order changes no answer")
        st(sorted({cl(p) for p in tracked if p.startswith("docs/") and p.endswith((".mjs", ".py", ".json", ".html", ".css"))}), ["O"],
           "every tracked script, data file and page under docs/ classifies O")
        try:
            owner_patterns("# comments only\n"); st("passed", "refused", "REFUSE: a CODEOWNERS holding no rules")
        except Refuse:
            st("refused", "refused", "REFUSE: a CODEOWNERS holding no rules")
        reset(paths=("custom_components/a.py", "tools/pr/x.py", "newroot.txt")); rc, out = chk()
        st((rc, out.count("class R:")), (1, 2), "REFUSE: a diff with class-R paths names each")
        reset(); del world["files"][CODEOWNERS]; st(chk()[0], 1, "REFUSE: CODEOWNERS unreadable at the ref")

        # --- the manifest version ----------------------------------------------
        mf = lambda v: json.dumps({"domain": "x", "version": v})  # noqa: E731
        reset(paths=(MANIFEST,)); world["files"].update({("e" * 40, MANIFEST): mf("7.1.9"), (H, MANIFEST): mf("7.2.0")})
        rc, out = chk(); st((rc, "version changes" in out), (1, True), "REFUSE: a manifest version edit")
        world["files"][(H, MANIFEST)] = json.dumps({"domain": "y", "version": "7.1.9"})
        st(chk()[0], 0, "(null control) a manifest edit that leaves the version key alone is class F")
        world["files"][(H, MANIFEST)] = "{not json"; st(chk()[0], 1, "REFUSE: a manifest that no longer parses")

        # --- class O, the owner's own form ---------------------------------------
        OP = ("tests/entities.py",)
        line = lambda s=H: f"Read the test diff.\n\n{READ_WORDS} {s}\n"  # noqa: E731

        def o(reviews, mand="live", carry=(), **kw):
            reset(reviews=reviews, mand=mand, paths=OP, **kw); world["carry"] = set(carry)
            rc, out = chk(); return rc

        st(o([]), 1, "class O REFUSE: no review at all")
        reset(reviews=[], paths=OP); rc, out = chk(early=True)
        st((rc, out.startswith("PENDING:")), (0, True), "pr-contract's early signal: a class-O read still owed is PENDING, not a refusal")
        # pr-contract's offline form: the pull request from a file, no API call at all.
        reset(reviews=[], paths=OP); world["log"].clear()
        rc, lines = check(R, PR, "origin/main", gate=g, fetch=False, early=True, pull=pull())
        st((rc, lines[0].startswith("PENDING:"), world["log"]), (0, True, []), "the offline early form: PENDING for class O, and not one gh call")
        rc, lines = check(R, PR, "origin/main", gate=g, fetch=False, early=True, pull=pull(ref="a$(id)"))
        st((rc, world["log"]), (1, []), "the offline early form refuses a head branch name a shell expands, with no gh call")
        world["paths"] = ["tools/x.py"]
        st(check(R, PR, "origin/main", gate=g, fetch=False, early=True, pull=pull())[0], 1, "the offline early form refuses a class-R path")
        st(check(R, PR, "origin/main", gate=g, fetch=False, early=True, pull=pull(author={**BK, "id": 1}))[0], 3, "the offline early form: an author on no entry is not outside")
        st(check(R, PR, "origin/main", gate=g, fetch=False, early=True, pull=pull(number=8))[0], 1, "the offline early form refuses a file that is another pull request's")
        world["paths"] = list(OP)
        st(check(R, PR, "origin/main", gate=g, fetch=False, pull=pull())[0], 1, "REFUSE: the offline form without --early: it is never the gate")
        st(o([rv(line())]), 0, "class O admitted: the owner's APPROVED review at H carrying the line")
        st(o([rv(line(), user={**OWN, "id": 5})]), 1, "class O REFUSE: the same review under another numeric id")
        st(o([rv(line(), user=BK)]), 1, "class O REFUSE: the same review under the contributor's account")
        st(o([rv(line(L), sha=L)], carry={(L, H)}), 0, "class O admitted: read at L, and L carries to H")
        st(o([rv(line(L), sha=L)]), 1, "class O REFUSE: read at L, and L does not carry to H")
        st(o([rv(line(L), sha=H)], carry={(L, H)}), 0, "class O admitted: commit_id re-anchored to H, the line names a carried L")
        st(o([rv(line(L), sha=X)], carry={(L, H)}), 1, "class O REFUSE: a commit_id that is neither L nor H")
        st(o([rv(line(L), sha=X)], carry={(L, H), (L, X), (X, H)}), 0, "class O admitted: commit_id on an intermediate X with L->X and X->H carried (item 25)")
        st(o([rv(line(L), sha=X)], carry={(L, H), (L, X)}), 1, "class O REFUSE: an intermediate X that does not carry to H")
        st(o([rv(line(L), sha=X)], carry={(L, H), (X, H)}), 1, "class O REFUSE: an intermediate X that L does not carry to")
        st(o([rv(line(L), sha=None)], carry={(L, H)}), 1, "class O REFUSE: a review with no commit_id")
        st(o([rv("")]), 1, "class O REFUSE: an empty body (ci_probe.py's approval)")
        st(o([rv("Looks good to me.")]), 1, "class O REFUSE: an approval with no outside-read line")
        st(o([rv(f"I did the {READ_WORDS} {H} today")]), 1, "class O REFUSE: the words inside a sentence, not on a line of their own")
        st(o([rv(f"{READ_WORDS} {H[:39]}")]), 1, "class O REFUSE: a 39-hex commit on the line")
        st(o([rv(f"{READ_WORDS} {H}\n{READ_WORDS} {L}\n")], carry={(L, H)}), 1, "class O REFUSE: two outside-read lines")
        st(o([rv(line(), state="COMMENTED")]), 1, "class O REFUSE: the line in a COMMENTED review")
        st(o([rv(line()), rv("no", state="CHANGES_REQUESTED")]), 1, "class O REFUSE: a later CHANGES_REQUESTED by the owner voids the approval")
        st(o([rv(line()), rv("", state="DISMISSED")]), 1, "class O REFUSE: a later DISMISSED review under the owner's account voids it")
        st(o([rv("no", state="CHANGES_REQUESTED"), rv(line())]), 0, "(null control) the approval AFTER his change request stands: latest, not any")
        st(o([rv(line()), rv("a note", state="COMMENTED")]), 0, "(null control) a later COMMENTED review is not decisive and voids nothing")
        st(o([rv(line()), rv("no", state="CHANGES_REQUESTED", user=BK)]), 0, "(null control) the contributor's own change request voids nothing")
        st(o([rv(line() + "\nGiven from my seat at the desk.")]), 1,
           "class O REFUSE (fail closed, item 28): the owner's own words trip AGENT_DECLARED, so the form is neither")
        ro = reset(reviews=[rv(line())], paths=OP); ro[f"repos/{R}/pulls/{PR}/reviews"] = "ERR"
        st(chk()[0], 1, "class O REFUSE: the review list unreadable")
        ro[f"repos/{R}/pulls/{PR}/reviews"] = {"not": "a list"}; st(chk()[0], 1, "class O REFUSE: a review list that is no list of pages")
        # The four existing writers under the owner's account, each body produced
        # by the writer itself, never copied here.
        sh = real_run(["bash", "-c", 'eval "$(sed -n \'/^owner_body() {/,/^}/p\' "$1")"; owner_body "$2" "$3" "in force (scope all)"',
                       "x", str(ROOT / "tools/audit/seat/merge_pr.sh"), H, str(MID)], capture_output=True, text=True).stdout
        st(bool(sh) and str(MID) in sh, True, "merge_pr.sh's owner_body was called and produced a body")
        st(o([rv(sh)]), 1, "class O REFUSE: merge_pr.sh owner mode's body (declared, mandated, no line)")
        spec = importlib.util.spec_from_file_location("merge_train_for_outside", str(ROOT / "tools/audit/seat/merge_train.py"))
        mt = importlib.util.module_from_spec(spec); sys.modules[spec.name] = mt; spec.loader.exec_module(mt)
        tr = type("T", (), {"role": "the orchestrator seat", "ignore": []})()
        item = {"verdict": H, "verdict_comment": 1}
        bare = mt.Train._agent_approval_body(tr, H, item, "code-owned paths", ["tests/entities.py"], str(MID))
        cite = mt.Train._agent_approval_body(tr, H, item, "code-owned paths", ["tests/entities.py"], f"mandate comment {MID}")
        st(o([rv(bare)]), 1, "class O REFUSE: _agent_approval_body under a bare mandate id")
        st(o([rv(cite)]), 1, "class O REFUSE: _agent_approval_body under 'mandate comment <id>'")
        st(o([rv(sh.rstrip() + f"\n\nCarried by the train's clean recarry from {L} (delta: main's commits only); prior owner review 1; mandate re-read in force at merge: {MID}.\n")]),
           1, "class O REFUSE: _post_carry's body over owner_body's")
        tracked_now = real_run(["git", "-C", str(ROOT), "ls-files", "tools", ".github"], capture_output=True, text=True).stdout.splitlines() \
            or [str(p.relative_to(ROOT)) for d in ("tools", ".github") for p in (ROOT / d).rglob("*") if p.is_file()]
        st([p for p in tracked_now if p != "tools/pr/outside.py" and not p.startswith("tools/audit/seat/instruments/")
            and (ROOT / p).is_file() and READ_WORDS.encode() in (ROOT / p).read_bytes()], [],
           "no program under tools/ or .github/ but this one writes the outside-read line")

        # --- class O, the machinery's form -----------------------------------------
        AB = approval_body(PR, H, MID, list(OP), "the class-O read seat")
        st({int(a or b) for a, b in g.MANDATE_CITE.findall(AB)}, {MID}, "the approve body: MANDATE_CITE reads exactly the id given")
        st(bool(g.AGENT_DECLARED.search(AB)), True, "the approve body declares an agent")
        st(READ_LINE.findall(AB), [H], "the approve body names the head on the outside-read line")
        st(o([rv(AB)]), 0, "class O admitted: the approve body at H under a mandate of scope all in force now")
        st(o([rv(AB)], mand=None), 1, "(null control) the same body with the mandate comment gone (404)")
        st(o([rv(AB)], mand=mandate(scope="code-owned")), 1, "class O REFUSE: a mandate of scope code-owned")
        st(o([rv(AB)], mand=mandate(scope="budget-raise")), 1, "class O REFUSE: a mandate of scope budget-raise")
        st(o([rv(AB)], mand=mandate(start=-120, until=-10)), 1, "class O REFUSE: a mandate expired now, though in force when the review was submitted")
        r_old = rv(AB); r_old["submitted_at"] = iso(-90)
        st(o([r_old], mand=mandate(start=-120, until=-10)), 1, "... judged now, never at the review's submission (in force then)")
        st(o([rv(AB)], mand=mandate(start=10, until=60)), 1, "class O REFUSE: a mandate not yet in force")
        st(o([rv(AB)], mand=mandate(edited=True)), 1, "class O REFUSE: an edited mandate comment")
        st(o([rv(AB)], mand=mandate(user=BK)), 1, "class O REFUSE: the mandate comment written by another account")
        st(o([rv(AB)], mand=mandate(user={**OWN, "id": 9})), 1, "class O REFUSE: by an account named as the owner's under another id")
        st(o([rv(AB)], mand=mandate(issue=4242)), 1, "class O REFUSE: the mandate comment on another issue")
        st(o([rv(AB)], mand=mandate(issue=201, repo="evil/other")), 1, "class O REFUSE: on record issue 201 of another repository")
        st(o([rv(AB)], mand=mandate(body="please MANDATE: agents may approve")), 1, "class O REFUSE: a comment whose first line is not the grammar")
        st(o([rv(AB)], mand="ERR"), 1, "class O REFUSE: a mandate read that fails")
        rev = lambda user=OWN: [{"id": RID, "user": user, "body": f"MANDATE REVOKED {MID}", "created_at": iso(-5), "updated_at": iso(-5)}]  # noqa: E731
        for issue in g.RECORD_ISSUES:
            ro = reset(reviews=[rv(AB)], paths=OP); ro[f"repos/{R}/issues/{issue}/comments"] = rev()
            st(chk()[0], 1, f"class O REFUSE: the mandate revoked by the owner on #{issue}")
        ro = reset(reviews=[rv(AB)], paths=OP); ro[f"repos/{R}/issues/{g.RECORD_ISSUE}/comments"] = rev(BK)
        st(chk()[0], 0, "(null control) a revocation by another account revokes nothing")
        ro = reset(reviews=[rv(AB)], paths=OP); ro[f"repos/{R}/issues/{g.RECORD_ISSUE}/comments"] = "ERR"
        st(chk()[0], 1, "class O REFUSE: the record thread unreadable, so a revocation could not be ruled out")
        st(o([rv(AB + f"\nAlso mandate comment {MID + 5}.")]), 1, "class O REFUSE: two mandates cited")
        st(o([rv(f"Agent approval by a seat.\n\n{READ_WORDS} {H}\n")]), 1, "class O REFUSE: a declared body citing no mandate")
        st(o([rv(f"As discussed, mandate comment {MID}.\n\n{READ_WORDS} {H}\n".replace("mandate comment", "see issuecomment-" + str(MID) + " and"))]), 1,
           "class O REFUSE: a mandate cited by URL in a body that declares no agent")
        st(o([rv(AB, user=BK)]), 1, "class O REFUSE: the same body, line and citation under the contributor's id")
        st(o([rv("no", state="CHANGES_REQUESTED"), rv(AB)]), 1, "class O REFUSE: a mandated approval after the owner's own CHANGES_REQUESTED")
        st(o([rv("no", state="CHANGES_REQUESTED"), rv(line()), rv(AB)]), 0, "(null control) his own later approval lifts his change request")
        GR = f"MANDATE: agents may approve as {g.OWNER_LOGIN}, scope all, from {iso(-60)} until {iso(60)}"
        ro = reset(reviews=[rv(AB)], mand=None, paths=OP)
        ro[f"repos/{R}/pulls/{PR}"]["body"] = GR
        ro[f"repos/{R}/issues/{PR}/comments"] = [{"id": MID, "user": BK, "body": GR}]
        world["files"][(H, "MANDATE.md")] = GR
        st(chk()[0], 1, "class O REFUSE: the grammar in the pull-request body, a pull-request comment and a file of the head, with no record comment")
        st(o([rv(AB)], mand={**mandate(), "issue_url": f"https://api.github.com/repos/{R}/issues/{PR}"}), 1,
           "class O REFUSE: the owner's grammar in a comment on the pull request itself, not a record issue")

        # --- the approve subcommand ----------------------------------------------
        def ap(mand_id=MID, head=H, **kw):
            rc, lines = approve(R, PR, head, mand_id, "origin/main", "the class-O read seat", gate=g, fetch=False)
            return rc, sum(1 for c in world["log"] if "-X POST" in c), " | ".join(lines)

        reset(paths=OP); rc, posts, out = ap()
        st((rc, posts), (0, 1), "approve: one review posted on an outside head with a class-O path, under a mandate in force")
        posted = world["routes"][f"repos/{R}/pulls/{PR}/reviews"][-1]
        st((posted["commit_id"], posted["body"]), (H, AB), "... through the reviews API with commit_id the head read, the body read back")
        st(chk()[0], 0, "... and the contract then admits the head")
        st(any("pr review" in c for c in world["log"]), False, "... never through `gh pr review`")
        reset(paths=OP); world["mangle"] = True
        st(ap()[0], 1, "approve REFUSE: a read-back that differs from what was posted")
        for name, kw, mid in (("a same-repository head", {"head_repo": R}, MID), ("a head that moved", {"sha": Z}, MID),
                              ("an author on no allowlist entry", {"author": {**BK, "id": 1}}, MID),
                              ("a head branch name a shell expands", {"ref": "a$(id)"}, MID), ("no --mandate", {}, None)):
            reset(paths=OP, **kw); rc, posts, out = ap(mand_id=mid)
            st((rc, posts), (1, 0), f"approve REFUSE, nothing posted: {name}")
        for name, paths in (("a diff with a class-R path", OP + ("tools/x.py",)), ("a diff with no class-O path", ("README.md",))):
            reset(paths=paths); st(ap()[:2], (1, 0), f"approve REFUSE, nothing posted: {name}")
        reset(paths=OP, mand=mandate(scope="code-owned")); st(ap()[:2], (1, 0), "approve REFUSE, nothing posted: a mandate not in force for this scope")
        reset(paths=OP, mand=None); st(ap()[:2], (1, 0), "approve REFUSE, nothing posted: a mandate that does not exist")
        reset(paths=OP); world["me"] = BK; st(ap()[:2], (1, 0), "approve REFUSE, nothing posted: a gh account that is not the owner's")
        reset(paths=OP, reviews=[rv("no", state="CHANGES_REQUESTED")]); st(ap()[:2], (1, 0), "approve REFUSE, nothing posted: the owner's own CHANGES_REQUESTED stands")
        ro = reset(paths=OP); ro[f"repos/{R}/commits/{H}/pulls"] = [pull(number=8)]
        st(ap()[:2], (1, 0), "approve REFUSE, nothing posted: another pull request at the head")
    finally:
        subprocess.run = real_run
        carries, show, changed = real
        now_utc = real_now

    # --- the live plumbing, over a throwaway repository (every case above fakes it) --
    import shutil
    tmp = tempfile.mkdtemp(prefix="outside-selftest-")
    cwd = os.getcwd()
    try:
        sys.path.insert(0, str(ROOT / "tests"))
        from throwaway_git import throwaway_git_init  # the one hermetic way to build a repository
        env = throwaway_git_init(tmp, "-q", "-b", "main")

        def tg(*a):
            return subprocess.run(["git", "-C", tmp, "-c", "user.name=t", "-c", "user.email=t@t", *a], capture_output=True, text=True, env=env)

        Path(tmp, "f.txt").write_text("one\n")
        tg("add", "-A"); tg("commit", "-q", "-m", "c")
        os.chdir(tmp)
        c = git("rev-parse", "HEAD").strip()
        st(bool(SHA40.fullmatch(c)), True, "git(): a command's stdout comes back")
        try:
            git("rev-parse", "--verify", "-q", "refs/heads/absent"); st("returned", "raised", "git(): a failing command raises")
        except Refuse:
            st("raised", "raised", "git(): a failing command raises, never an empty answer")
        st(show(c, "f.txt"), "one\n", "show(): a path at a ref comes back")
        st(show(c, "absent.txt"), None, "show(): a path the ref does not hold is None, never empty text")
        st(changed(c, c), (c, []), "changed(): the merge base and the three-dot path list")
        st(carries(c, c, c), True, "carries(): app_approve.sh --carry says yes for a head onto itself")
        st(carries("a" * 40, c, c), False, "carries(): and no for a commit that is no ancestor of the head")
        st(now_utc().tzinfo is not None and abs((now_utc() - datetime.datetime.now(datetime.timezone.utc)).total_seconds()) < 60, True,
           "now_utc(): the instant a mandate is judged at is the clock's, with a zone")
        Path(tmp, "tools/policy").mkdir(parents=True); Path(tmp, "tests").mkdir()
        Path(tmp, "tools/policy/policy_lint.mjs").write_text("const POLICY_GLOBS = [\n]\nconst POLICY_DIRS = []\n")
        Path(tmp, "tests/closure.py").write_text("GATE_FILES = tuple(x for x in ())\n")
        for fn, what in ((policy_patterns, "policy_lint.mjs with empty policy arrays"), (gate_files, "a closure.py whose GATE_FILES is no literal")):
            try:
                fn(Path(tmp)); st("read", "refused", f"REFUSE: {what}")
            except (Refuse, ValueError):
                st("refused", "refused", f"REFUSE: {what}")
    finally:
        os.chdir(cwd)
        shutil.rmtree(tmp, ignore_errors=True)

    # --- the workflows: no contributor-named value in a shell, a fork never skips --
    wf = sorted((ROOT / ".github/workflows").glob("*.yml"))
    named = re.compile(r"\$\{\{[^}]*(github\.head_ref|head\.ref|head\.label|github\.ref_name|pull_request\.title|pull_request\.body)")

    def run_hits(text):
        hits, block = [], None
        for i, ln in enumerate(text.splitlines(), 1):
            ind = len(ln) - len(ln.lstrip())
            if block is not None and ln.strip() and ind <= block:
                block = None
            if block is None:
                m = re.match(r"\s*(?:- )?run:\s*(.*)$", ln)
                if m:
                    if m.group(1).strip() in ("|", ">", "|-", ">-", "|+", ">+"):
                        block = ind
                    elif named.search(m.group(1)):
                        hits.append(i)
            elif named.search(ln) and not ln.lstrip().startswith("#"):
                hits.append(i)
        return hits

    st(run_hits("jobs:\n  a:\n    steps:\n      - run: |\n          B=\"${{ github.head_ref || github.ref_name }}\"\n      - env:\n          B: ${{ github.head_ref }}\n        run: echo \"$B\"\n      - run: echo ${{ github.event.pull_request.title }}\n"),
       [5, 9], "the workflow scan finds a contributor-named value inside a run: block and on a run: line, and not under env:")
    st(len(wf) > 5, True, "the workflows were listed")
    st({p.name: h for p in wf if (h := run_hits(p.read_text(encoding="utf-8")))}, {},
       "no workflow expands a contributor-named value (head ref, title, body) inside a run: block")
    tests_yml = (ROOT / ".github/workflows/tests.yml").read_text(encoding="utf-8")
    m = re.search(r"\n      - name: [^\n]*\n        id: laneskip\n(?:        #[^\n]*\n)*        if: >-\n(.*?)\n        (?:env|run):", tests_yml, re.S)
    st(bool(m) and "github.event.pull_request.head.repo.full_name == github.repository" in m.group(1), True,
       "tests.yml's laneskip step carries the same-repository conjunct: a fork head restores no lane proof and always runs")
    print(f"outside self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


def main(argv: "list[str]") -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    ap = argparse.ArgumentParser(prog="outside.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("--repo", required=True); c.add_argument("--pr", type=int, required=True)
    c.add_argument("--ref", default="origin/main"); c.add_argument("--early", action="store_true")
    c.add_argument("--no-fetch", action="store_true"); c.add_argument("--comment", type=int)
    c.add_argument("--pull-json", help="the pulls API's answer as a file (pr-contract, with --early): no API call is made")
    k = sub.add_parser("classify"); k.add_argument("--pr", type=int, required=True); k.add_argument("--ref", default="origin/main")
    k.add_argument("paths", nargs="+")
    x = sub.add_parser("cross"); x.add_argument("--repo", required=True); x.add_argument("--pr", type=int, required=True)
    a = sub.add_parser("approve"); a.add_argument("--repo", required=True); a.add_argument("--pr", type=int, required=True)
    a.add_argument("--head", required=True); a.add_argument("--mandate", type=int); a.add_argument("--ref", default="origin/main")
    a.add_argument("--role", default="the class-O read seat"); a.add_argument("--no-fetch", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "cross":
        rc, line = cross(args.repo, args.pr)
        print(line)
        return rc
    if args.cmd == "classify":
        try:
            rules = Rules(args.ref)
        except Refuse as e:
            print(f"REFUSE: {e}"); return 1
        for p in args.paths:
            print(rules.classify(p, args.pr), p)
        return 0
    if args.cmd == "check":
        pull = None
        if args.pull_json:
            try:
                pull = json.load(open(args.pull_json, encoding="utf-8"))
            except (OSError, ValueError):
                print(f"REFUSE: {args.pull_json} is not a readable JSON file"); return 1
        rc, lines = check(args.repo, args.pr, args.ref, fetch=not args.no_fetch, early=args.early, comment=args.comment, pull=pull)
    else:
        if not SHA40.fullmatch(args.head):
            print("REFUSE: --head takes a 40-hex commit"); return 1
        rc, lines = approve(args.repo, args.pr, args.head, args.mandate, args.ref, args.role, fetch=not args.no_fetch)
    print("\n".join(lines))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
