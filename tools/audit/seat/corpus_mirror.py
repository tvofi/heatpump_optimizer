#!/usr/bin/env python3
"""The corpus mirror of an owner-only audit dimension: every published source, read once, into the private root.

    python3 -I corpus_mirror.py run --private-root DIR --token-fd N [--own-identity] [--only S2,S3,S4,S5]
                                    [--repo OWNER/NAME] [--checkout DIR]
    python3 -I corpus_mirror.py cost --private-root DIR
    python3 -I corpus_mirror.py --self-test [--no-mutants]

tools/audit/seat/owner_only.py starts it before the session, with the read
credential on a descriptor. It is the ONLY process of an owner-only run that
calls GitHub, so "one stream per bucket" is a property of the design: the
seats read `<private root>/corpus/` and call nothing. Everything it stores is
UNTRUSTED DATA: nothing from the corpus is executed or imported, here or by a
seat.

THE SOURCES (the axis of the dimension's scopes; S1, the tree at the baseline,
is the driver's export and costs nothing):
  S2 history and refs   `git ls-remote origin`, then one fetch of heads, tags
      and pull refs into a bare mirror (`corpus/git`). A listed ref outside
      those three namespaces is a `not_reached: unmapped namespace` line and a
      non-zero exit: never skipped. The before-SHA of every force-push (the
      activity list) is fetched by SHA once: fetched, it is listed `served by
      SHA only`; refused, `not_reached: gone`.
  S3 GitHub text        the issue list (titles and bodies of issues and pull
      requests), issue, review and commit comments, issue events, labels and
      milestones as paged lists; then one GraphQL query per GRAPHQL_BATCH
      items for review bodies, edit histories GitHub still serves, forced-push
      items and the head commit's status contexts.
  S4 published          releases and each asset under the size cap; the Pages
      site crawled over plain HTTPS from tools/audit/seat/plan_public.py's
      root; the code-scanning, secret-scanning and Dependabot alert lists; the
      wiki's repository when the repository row reports one.
  S5 CI                 workflow runs, newest first, windowed by `created`;
      per run its logs archive and its check runs (annotations only where a
      row counts one); artifacts under the size cap.
MANIFEST.json holds each source's denominator -- enumerator, universe,
examined, not_reached with a reason per unit -- and the scan's state. A unit
GitHub no longer serves (404, 410) is `gone`, read once. A per-item read that
answers an error is a not_reached line of its pass, and the next pass reads
the unit again; only an answer (`answered`) is kept, and a kept answer that
is not `ok` is a not_reached line of every later pass. What no endpoint
serves is stated there too (a job's step summary; status contexts of commits
heading no pull request).

THE READ BUDGET (tvofi 2026-11-15; the rule and its argument are
tools/audit/seat/gh_read.py's, the constants BATCH, MIN_GAP_S, FLOOR_SHARED and
FLOOR_OWN). One serial stream, at least MIN_GAP_S between calls. Before every
BATCH calls it reads `rate_limit` (free) and goes on only while core and
graphql each keep the floor: FLOOR_SHARED on the shared token, FLOOR_OWN with
`--own-identity` (a read-only identity with its own bucket). Below it, or on a
rate-limit answer (a secondary limit, a spent bucket), it writes its cursor and
exits 0 printing `paused`; the next run resumes from the cursor, losing and
repeating no page. Every page is cached with its ETag and re-read with
If-None-Match: a 304 costs nothing against the primary limit, so a later round
pays for what changed. It never calls a search endpoint and never writes: every
call it issues passes gh_read.is_read or gh_read.is_query, or it stops.
`cost` prints the calls per bucket this scan made (its own count; `gh_calls.py
--top --since <scan start>` prints the shim's, from the log).

ARCHIVES. A logs or artifact archive is extracted only under the corpus. An
archive with a member whose path leaves its directory, a link, or a size or
ratio past the cap is refused whole and recorded in refused.json by the rule
it broke; nothing of it is extracted. WHOSE FAILURE: an archive is read from
memory, so whatever reading it raises is the archive's and is a refusal, an
answer; whatever a call on this host's file system raises is this host's and
is no answer (`each`): the unit is read again by the next pass.

NOT EXERCISED HERE: the self-test drives every path over a stub of `gh`, `git`
and HTTPS. A first real scan confirms each endpoint's shape; one that does not
serve what this file expects becomes a `not_reached` line with the reason,
never a dropped row.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gh_read  # noqa: E402 -- the read rule, the budget and its constants have one owner

REPO = "tvofi/heatpump_optimizer"
NAMESPACES = ("refs/heads/", "refs/tags/", "refs/pull/")
GRAPHQL_BATCH = 50
RUN_WINDOW = 1000          # the run list serves at most this many rows per filter
MAX_MEMBER = 64 * 2**20    # one extracted member
MAX_ARCHIVE = 512 * 2**20  # one archive, extracted
MAX_RATIO = 200            # extracted over compressed, per member
MAX_NAME = 255             # bytes of one component of a member's path: past it no common file system stores the name
MAX_DOWNLOAD = 256 * 2**20  # an asset or artifact above this is not_reached: size
MAX_SITE_PAGES = 2000
NOT_REACHED_CAP = 200
SAVE_EVERY = 20
UNSERVED = {"S5": ["a job's step summary: no endpoint (removal route: deleting the run)"],
            "S3": ["status contexts of commits that head no pull request: cost (enumerator: git rev-list --count --all)"]}

ITEM_QUERY = """query($o:String!,$n:String!){repository(owner:$o,name:$n){%s}}"""
ITEM_FIELDS = """i%d: issueOrPullRequest(number:%d){__typename
 ... on Issue{userContentEdits(first:50){nodes{editedAt diff}} comments(first:100){pageInfo{hasNextPage} nodes{databaseId userContentEdits(first:20){nodes{editedAt diff}}}}}
 ... on PullRequest{userContentEdits(first:50){nodes{editedAt diff}} comments(first:100){pageInfo{hasNextPage} nodes{databaseId userContentEdits(first:20){nodes{editedAt diff}}}}
  reviews(first:100){pageInfo{hasNextPage} nodes{databaseId body userContentEdits(first:20){nodes{editedAt diff}}}}
  timelineItems(itemTypes:[HEAD_REF_FORCE_PUSHED_EVENT],first:50){nodes{... on HeadRefForcePushedEvent{beforeCommit{oid}}}}
  commits(last:1){nodes{commit{statusCheckRollup{contexts(first:100){nodes{__typename ... on StatusContext{context description}}}}}}}}}"""


#: What the remote answers for good. Any other state is no answer -- an HTTP error, a transport failure, a
#: failure of this host (HOST_FAILED), or one computed from a row with no call (`size`, `not a sha`, `no check
#: suite`) -- and is a not_reached line of its pass; the next pass reads the unit again.
ANSWERED = ("ok", "gone")
HOST_FAILED = "error: this host failed"


def answered(state: str) -> bool:
    return state in ANSWERED or state.startswith("refused: ")


class Paused(Exception):
    """The scan stops at its cursor: the budget floor, or a rate-limit answer."""


def unmapped(ls_remote: str) -> list[str]:
    """The namespaces `git ls-remote` lists outside the three the fetch maps, each once."""
    out = set()
    for line in ls_remote.splitlines():
        ref = line.split("\t", 1)[-1].strip()
        if ref.startswith("refs/") and not ref.startswith(NAMESPACES):
            out.add("/".join(ref.split("/")[:2]) + "/")
    return sorted(out)


def archive_refusal(zf: zipfile.ZipFile, dest: Path) -> str:
    """The rule an archive breaks, or "": judged whole, before any member is written."""
    base, total, files, parents = os.path.realpath(dest), 0, set(), set()
    for info in zf.infolist():
        name = info.filename
        if stat.S_ISLNK(info.external_attr >> 16):
            return "a member is a link"
        target = os.path.realpath(os.path.join(base, name))
        if name.startswith(("/", "\\")) or re.match(r"[A-Za-z]:", name) or not (target == base or target.startswith(base + os.sep)):
            return "a member's path leaves the archive's directory"
        if target == base and not info.is_dir():
            return "a member's path is the archive's directory"
        if any(len(part.encode("utf-8", "replace")) > MAX_NAME for part in name.split("/")):
            return "a member's name is past the length cap"
        (parents if info.is_dir() else files).add(target)
        parent = os.path.dirname(target)
        while len(parent) > len(base):  # every directory between the member and the archive's own
            parents.add(parent)
            parent = os.path.dirname(parent)
        if info.file_size > MAX_MEMBER:
            return "a member is past the size cap"
        if info.file_size > MAX_RATIO * max(info.compress_size, 1):
            return "a member is past the ratio cap"
        total += info.file_size
        if total > MAX_ARCHIVE:
            return "the archive is past the size cap"
    if files & parents:
        return "a member's path is both a file and a directory"
    return ""


def read_archive(read):
    """One read of an archive's bytes -> (its value, "") or (None, the class of what it raised).

    The boundary of the archive's own failures. `read` touches only bytes held in memory, so an Exception out
    of it is a function of those bytes, whatever its class (zipfile raises RuntimeError for an encrypted member,
    NotImplementedError for a method it lacks, zlib.error for a corrupt stream, and names no complete set).
    MemoryError alone is this host's, and is raised.
    """
    try:
        return read(), ""
    except MemoryError:
        raise
    except Exception as e:  # noqa: BLE001 -- the boundary is the rule: see the docstring
        return None, type(e).__name__


def safe_extract(data: bytes, dest: Path) -> str:
    """Extract a zip under `dest` -> "" when whole, else the rule the archive broke (and nothing is left under `dest`).

    Whose failure, by what a call reads: opening the archive and decoding a member go through `read_archive`
    and return a rule. Every call on the file system is this host's: its failure is raised as OSError, never
    returned, so no caller can record it as the archive's rule (`Mirror.each` reads it as no answer).
    """
    def member(info):
        with zf.open(info) as src:
            return src.read(MAX_MEMBER + 1)[:MAX_MEMBER]

    zf, bad = read_archive(lambda: zipfile.ZipFile(io.BytesIO(data)))
    if bad:
        return "not a zip archive"
    whole = False
    with zf:
        why = archive_refusal(zf, dest)
        if why:
            return why
        try:
            os.makedirs(dest, mode=0o700, exist_ok=True)  # an archive of no file is whole too, and has its directory
            for info in zf.infolist():
                if info.is_dir():
                    continue
                body, bad = read_archive(lambda: member(info))
                if bad:
                    return f"a member cannot be read ({bad})"
                try:
                    target = Path(os.path.join(dest, info.filename))
                    os.makedirs(target.parent, mode=0o700, exist_ok=True)
                    target.write_bytes(body)
                    os.chmod(target, 0o600)
                except OSError:
                    raise
                except Exception as e:  # noqa: BLE001 -- the names passed archive_refusal: what is left is this host's
                    raise OSError(f"a member could not be written ({type(e).__name__})") from e
            whole = True
        finally:
            if not whole:
                shutil.rmtree(dest, ignore_errors=True)
    return ""


def host_failure(e: BaseException) -> str:
    """The state of a unit this host failed on, naming the errno or the class and nothing of the path."""
    import errno
    return f"{HOST_FAILED} ({errno.errorcode.get(getattr(e, 'errno', None)) or type(e).__name__})"


def links(base: str, html: str) -> list[str]:
    """Same-site links of a page, absolute, fragment and query cut, in order."""
    from urllib.parse import urljoin, urlsplit
    out, root = [], urlsplit(base)
    for m in re.finditer(r"""(?:href|src)\s*=\s*["']([^"'#?]+)""", html, re.I):
        u = urlsplit(urljoin(base, m.group(1)))
        if u.scheme == "https" and u.netloc == root.netloc:
            out.append(f"https://{u.netloc}{u.path}")
    return list(dict.fromkeys(out))


class Mirror:
    def __init__(self, root, *, run, run_bytes, git, http, new_bare, sleep=time.sleep, now=time.time, floor=gh_read.FLOOR_SHARED,
                 repo=REPO, site="", say=print):
        self.root, self.dir = Path(root), Path(root) / "corpus"
        self.run, self.run_bytes, self.git, self.http, self.new_bare = run, run_bytes, git, http, new_bare
        self.sleep, self.now, self.floor, self.repo, self.site, self.say = sleep, now, floor, repo, site, say
        self.cur = self._load("cursor.json", {"lists": {}, "items": {}, "calls": {}, "pass": 0, "state": "new"})
        self.man = self._load("MANIFEST.json", {"sources": {}})
        self.since_budget = gh_read.BATCH  # the first call is preceded by a budget read
        self.dirty = 0

    # ---- state -------------------------------------------------------------------
    def _load(self, name, default):
        try:
            return json.loads((self.dir / name).read_text())
        except (OSError, ValueError):
            return default

    def _write(self, rel: str, data) -> Path:
        p = self.dir / rel
        os.makedirs(p.parent, mode=0o700, exist_ok=True)
        tmp = p.with_name(p.name + ".tmp")
        tmp.write_bytes(data if isinstance(data, bytes) else data.encode())
        os.chmod(tmp, 0o600)
        os.replace(tmp, p)
        return p

    def save(self):
        self._write("cursor.json", json.dumps(self.cur, indent=1, sort_keys=True) + "\n")
        self._write("MANIFEST.json", json.dumps(self.man, indent=1, sort_keys=True) + "\n")
        self.dirty = 0

    def source(self, s: str) -> dict:
        return self.man["sources"].setdefault(s, {"units": {}, "not_reached": [], "unserved": UNSERVED.get(s, [])})

    def unit(self, s: str, name: str, enumerator: str) -> dict:
        return self.source(s)["units"].setdefault(name, {"enumerator": enumerator, "universe": 0, "examined": 0})

    def missed(self, s: str, what: str):
        nr = self.source(s)["not_reached"]
        if what not in nr:
            nr.append(what) if len(nr) < NOT_REACHED_CAP else None
            self.source(s)["not_reached_over_cap"] = self.source(s).get("not_reached_over_cap", 0) + (len(nr) >= NOT_REACHED_CAP)

    # ---- the one stream ----------------------------------------------------------
    def _gate(self, argv, bucket: str):
        """Before every call: it is a read, it is no search, the budget holds, the gap has passed."""
        path = argv[3] if argv[2:3] == ["-i"] else (argv[2] if len(argv) > 2 else "")
        if not (gh_read.is_read(argv) or gh_read.is_query(argv)) or path.lstrip("/").split("?")[0].split("/")[0] == "search":
            raise AssertionError("corpus_mirror issues only reads, and no search: " + " ".join(argv[:3]))
        if self.since_budget >= gh_read.BATCH:
            low = gh_read.below_floor(gh_read.budget(self.run), self.floor)
            if low:
                raise Paused(f"budget: {', '.join(low)} below {self.floor:.0%} of its limit")
            self.since_budget = 0
        if sum(self.cur["calls"].values()):
            self.sleep(gh_read.MIN_GAP_S)
        self.since_budget += 1
        self.cur["calls"][bucket] = self.cur["calls"].get(bucket, 0) + 1

    def get(self, path: str, etag: str = ""):
        """A conditional REST read -> (state, body, etag): fresh, unchanged, gone or error:<what>."""
        self._gate(["gh", "api", "-i", path], "core")
        state, body, tag, raw = gh_read.read_conditional(self.run, path, etag, self.sleep, now=self.now)
        if state != "failed":
            return state, body, tag
        wait = gh_read.rate_wait(raw, self.now)
        if wait is not None:
            raise Paused(f"rate limit: the answer names a {wait:.0f} s wait")
        status = gh_read.parse_included(raw)[0]
        return ("gone" if status in (404, 410) else f"error: HTTP {status or 'unread'}"), "", etag

    def query(self, doc: str, **fields):
        """A GraphQL query -> (data or None, why)."""
        argv = ["gh", "api", "graphql", "-f", "query=" + doc]
        for k, v in fields.items():
            argv += ["-f", f"{k}={v}"]
        self._gate(argv, "graphql")

        def attempt():
            code, out = self.run(argv)
            return (out, None) if code == 0 else (None, out)
        value, failure, _, _ = gh_read.retry(attempt, gh_read.gh_wait, self.sleep)
        if failure is not None:
            if gh_read.RATE_LIMIT in failure.lower():
                raise Paused("rate limit: a GraphQL answer names one")
            return None, gh_read.one_line(failure)[-80:]
        try:
            return json.loads(value).get("data"), ""
        except (ValueError, AttributeError):
            return None, "not JSON"

    def download(self, path: str, accept: str = ""):
        """A binary read -> (bytes or None, why)."""
        argv = ["gh", "api", path] + (["-H", f"Accept: {accept}"] if accept else [])
        self._gate(argv, "core")
        code, data, err = self.run_bytes(argv)
        if code == 0:
            return data, ""
        if gh_read.RATE_LIMIT in err.lower():
            raise Paused("rate limit: a download's answer names one")
        gone = re.search(r"HTTP (404|410)", err)
        return None, "gone" if gone else "error: " + gh_read.one_line(err)[-60:]

    # ---- paged lists and per-item reads ---------------------------------------------
    def pages(self, s: str, name: str, path: str, key: str = ""):
        """Walk a paged list from the cursor, one stored page per call; -> its items, from the stored pages."""
        st = self.cur["lists"].setdefault(name, {"next": 1, "etags": {}, "done": False, "pages": 0})
        sep = "&" if "?" in path else "?"
        while not st["done"]:
            n = st["next"]
            state, body, etag = self.get(f"repos/{self.repo}/{path}{sep}per_page={gh_read.PER_PAGE}&page={n}", st["etags"].get(str(n), ""))
            if state == "fresh":
                self._write(f"pages/{name}/{n}.json", body)
                st["etags"][str(n)] = etag
            elif state != "unchanged":
                self.missed(s, f"{name} page {n}: {state}")
                st["done"] = True
                break
            count = len(self._page(name, n, key))
            st["next"], st["pages"] = n + 1, max(st["pages"], n)
            if count < gh_read.PER_PAGE:
                st["done"] = True
            self.save()  # the cursor write: a resume starts at the page after the last one stored
        items = [x for n in range(1, st["pages"] + 1) for x in self._page(name, n, key)]
        u = self.unit(s, name, f"gh api 'repos/{self.repo}/{path}{sep}per_page=100&page=N' (every page)")
        u["universe"] = u["examined"] = len(items)
        return items

    def _page(self, name: str, n: int, key: str):
        try:
            page = json.loads((self.dir / f"pages/{name}/{n}.json").read_text())
        except (OSError, ValueError):
            return []
        page = page.get(key, []) if key and isinstance(page, dict) else page
        return page if isinstance(page, list) else []

    def each(self, s: str, name: str, ids, fetch, enumerator: str):
        """Run `fetch(id) -> state` once per id and pass; a unit that answered (`answered`) is never read again.

        The boundary of this host's own failures: an OSError (a full or failing file system, a program that is
        not there) or MemoryError out of a fetch says nothing of the unit, so it is no answer."""
        done = self.cur["items"].setdefault(name, {})
        u = self.unit(s, name, enumerator)
        ids = [str(i) for i in ids]
        u["universe"] = len(set(ids) | set(done))
        try:
            for i in ids:
                if i in done:
                    if done[i] != "ok":  # an answer kept from an earlier pass is still not reached in this one
                        self.missed(s, f"{name} {i}: {done[i]}")
                    continue
                try:
                    state = fetch(i)
                except (OSError, MemoryError) as e:
                    state = host_failure(e)
                done[i] = state
                if state != "ok":
                    self.missed(s, f"{name} {i}: {state}")
                self.dirty += 1
                if self.dirty >= SAVE_EVERY:
                    self.save()
        finally:
            u["examined"] = sum(1 for v in done.values() if v == "ok")

    # ---- the sources -----------------------------------------------------------------
    def s2(self, origin: str, auth_env: dict):
        rc, ls = self.git(["git", "ls-remote", origin], auth_env)
        if rc != 0:
            self.missed("S2", "git ls-remote origin failed: no ref was read")
            return 1
        refs = [ln.split("\t", 1)[1] for ln in ls.splitlines() if "\t" in ln]
        u = self.unit("S2", "refs", "git ls-remote origin")
        u["universe"] = len(refs)
        bad = unmapped(ls)
        for ns in bad:
            self.missed("S2", f"unmapped namespace {ns}")
        mirror = str(self.dir / "git")
        if not os.path.isdir(mirror):
            self.new_bare(mirror)
        rc, _ = self.git(["git", "-C", mirror, "fetch", "-q", "--no-tags", origin] + [f"+{ns}*:refs/d18/{ns[5:]}*" for ns in NAMESPACES], auth_env)
        if rc != 0:
            self.missed("S2", "the fetch of heads, tags and pull refs failed")
            return 1
        u["examined"] = sum(1 for r in refs if r.startswith(NAMESPACES))
        shas = [str(a.get("before", "")) for a in self.pages("S2", "force-pushes", "activity?activity_type=force_push") if isinstance(a, dict)]

        def by_sha(sha):
            if not re.fullmatch(r"[0-9a-f]{40}", sha):
                return "not a sha"
            if self.git(["git", "-C", mirror, "cat-file", "-e", sha + "^{commit}"], {})[0] == 0:
                return "ok"
            if self.git(["git", "-C", mirror, "fetch", "-q", origin, f"{sha}:refs/d18/by-sha/{sha}"], auth_env)[0] == 0:
                self.source("S2").setdefault("served_by_sha_only", []).append(sha)
                return "ok"
            return "gone"
        self.each("S2", "force-pushed commits", [x for x in shas if x], by_sha, "the `before` of each row of the activity list")
        return 1 if bad else 0

    def s3(self):
        issues = self.pages("S3", "issues", "issues?state=all&sort=created&direction=asc")
        for name, path in (("issue-comments", "issues/comments?sort=created&direction=asc"),
                           ("review-comments", "pulls/comments?sort=created&direction=asc"), ("commit-comments", "comments"),
                           ("issue-events", "issues/events"), ("labels", "labels"), ("milestones", "milestones?state=all")):
            self.pages("S3", name, path)
        numbers = sorted(i["number"] for i in issues if isinstance(i, dict) and isinstance(i.get("number"), int))
        owner, repo = self.repo.split("/", 1)
        batches = {f"{b[0]}-{b[-1]}": b for b in (numbers[k:k + GRAPHQL_BATCH] for k in range(0, len(numbers), GRAPHQL_BATCH))}

        def batch(key):
            data, why = self.query(ITEM_QUERY % "\n".join(ITEM_FIELDS % (n, n) for n in batches[key]), o=owner, n=repo)
            if data is None:
                return "error: " + why
            self._write(f"graphql/items/{key}.json", json.dumps(data))
            if '"hasNextPage": true' in json.dumps(data):
                self.missed("S3", f"items {key}: a comment or review list runs past its first page")
            return "ok"
        self.each("S3", "item batches", list(batches), batch, f"the issue list's numbers, {GRAPHQL_BATCH} per GraphQL query")

    def s4(self, origin: str, auth_env: dict):
        state, body, _ = self.get(f"repos/{self.repo}")
        row = json.loads(body) if state == "fresh" else {}
        releases = self.pages("S4", "releases", "releases")
        assets = {str(a["id"]): a for r in releases if isinstance(r, dict) for a in r.get("assets", []) if isinstance(a, dict) and "id" in a}

        def asset(i):
            if int(assets[i].get("size") or 0) > MAX_DOWNLOAD:
                return "size"
            data, why = self.download(f"repos/{self.repo}/releases/assets/{i}", "application/octet-stream")
            if data is None:
                return why
            self._write(f"assets/{i}", data)
            return "ok"
        self.each("S4", "release assets", list(assets), asset, "each release row's asset list")
        for name, path in (("code-scanning alerts", "code-scanning/alerts"), ("secret-scanning alerts", "secret-scanning/alerts"),
                           ("dependabot alerts", "dependabot/alerts")):
            self.pages("S4", name, path)
        if row.get("has_wiki"):
            wiki = str(self.dir / "wiki.git")
            base = re.sub(r"(\.git)?/*$", "", origin)
            if not os.path.isdir(wiki):
                self.new_bare(wiki)
            if self.git(["git", "-C", wiki, "fetch", "-q", "--prune", base + ".wiki.git", "+refs/*:refs/*"], auth_env)[0] != 0:
                self.missed("S4", "the wiki: the repository row reports one and it has no git repository")
        if row.get("has_discussions"):
            self.missed("S4", "discussions: enabled, and this scan reads none (no list is read yet)")
        if self.site:
            self.crawl()

    def crawl(self):
        """The published site, over plain HTTPS with no credential: no API call, so no bucket."""
        seen = self.cur["items"].setdefault("site", {})
        queue = [self.site] + [u for u, v in seen.items() if v == "queued"]
        u = self.unit("S4", "site pages", f"a crawl of same-site links from {self.site}")
        while queue and len(seen) < MAX_SITE_PAGES:
            url = queue.pop(0)
            if seen.get(url) in ("ok", "gone"):
                continue
            status, ctype, data = self.http(url)
            if status != 200:
                seen[url] = "gone"
                self.missed("S4", f"site {hashlib.sha256(url.encode()).hexdigest()[:12]}: HTTP {status}")
                continue
            self._write(f"site/{hashlib.sha256(url.encode()).hexdigest()}", data)
            seen[url] = "ok"
            if "html" in ctype:
                for nxt in links(url, data.decode("utf-8", "replace")):
                    if nxt.startswith(self.site) and nxt not in seen:
                        seen[nxt] = "queued"
                        queue.append(nxt)
        if queue:
            self.missed("S4", f"site: more than {MAX_SITE_PAGES} pages; the rest is not crawled")
        self._write("site/index.json", json.dumps({k: hashlib.sha256(k.encode()).hexdigest() for k, v in seen.items() if v == "ok"}, indent=1))
        u["universe"], u["examined"] = len(seen), sum(1 for v in seen.values() if v == "ok")

    def s5(self):
        runs, before = {}, ""
        for window in range(1000):  # newest first: each window's filter ends where the last one's oldest row began
            rows = self.pages("S5", f"runs-{window}", "actions/runs" + (f"?created=<{before}" if before else ""), "workflow_runs")
            for r in rows:
                if isinstance(r, dict) and "id" in r:
                    runs[str(r["id"])] = r
            stamps = sorted(str(r.get("created_at", "")) for r in rows if isinstance(r, dict))
            if len(rows) < RUN_WINDOW or not stamps or stamps[0] == before:
                break
            before = stamps[0]
        order = sorted(runs, key=lambda i: str(runs[i].get("created_at", "")), reverse=True)

        def logs(i):
            data, why = self.download(f"repos/{self.repo}/actions/runs/{i}/logs")
            if data is None:
                return why
            return self.extract(f"logs/{i}", data)

        def checks(i):
            suite = runs[i].get("check_suite_id")
            if not suite:
                return "no check suite"
            state, body, _ = self.get(f"repos/{self.repo}/check-suites/{suite}/check-runs?per_page=100")
            if state != "fresh":
                return state
            self._write(f"checks/{i}.json", body)
            try:
                rows = json.loads(body).get("check_runs", [])
            except (ValueError, AttributeError):
                return "error: not JSON"
            for c in rows:
                if isinstance(c, dict) and (c.get("output") or {}).get("annotations_count"):
                    st, b, _ = self.get(f"repos/{self.repo}/check-runs/{c['id']}/annotations?per_page=100")
                    if st == "fresh":
                        self._write(f"annotations/{c['id']}.json", b)
                    else:
                        self.missed("S5", f"annotations of check run {c['id']}: {st}")
            return "ok"
        self.each("S5", "run logs", order, logs, "the run list, newest first; one logs archive per run")
        self.each("S5", "run check runs", order, checks, "the run list; one check-run page per run's check suite")
        arts = {str(a["id"]): a for a in self.pages("S5", "artifacts", "actions/artifacts", "artifacts") if isinstance(a, dict) and "id" in a}

        def artifact(i):
            if arts[i].get("expired"):
                return "gone"
            if int(arts[i].get("size_in_bytes") or 0) > MAX_DOWNLOAD:
                return "size"
            data, why = self.download(f"repos/{self.repo}/actions/artifacts/{i}/zip")
            if data is None:
                return why
            return self.extract(f"artifacts/{i}", data)
        self.each("S5", "artifacts", list(arts), artifact, "the artifact list; one download per unexpired artifact under the size cap")

    def extract(self, where: str, data: bytes) -> str:
        """An archive's state: `ok`, or refused by the rule it broke, recorded in refused.json."""
        why = safe_extract(data, self.dir / where)
        if not why:
            return "ok"
        rows = self._load("refused.json", [])
        rows.append({"archive": where, "rule": why})
        self._write("refused.json", json.dumps(rows, indent=1) + "\n")
        return "refused: " + why

    # ---- one scan --------------------------------------------------------------------
    def scan(self, only, origin: str, auth_env: dict) -> int:
        """-> 0 complete or paused, 1 a source that could not be read whole in a way a later run cannot repair."""
        if self.cur["state"] in ("new", "complete"):  # a new pass: every list is walked again, against its cached ETags
            for st in self.cur["lists"].values():
                st["next"], st["done"] = 1, False
            for done in self.cur["items"].values():  # with the not_reached lines cleared below, what gave no answer is asked again
                for i in [i for i, state in done.items() if not answered(state)]:
                    del done[i]
            self.cur["pass"] += 1
            self.cur["calls"] = {}
            for s in self.man["sources"].values():
                s["not_reached"] = []
        self.cur["state"] = "running"
        rc = 0
        try:
            if "S2" in only:
                rc |= self.s2(origin, auth_env)
            if "S3" in only:
                self.s3()
            if "S4" in only:
                self.s4(origin, auth_env)
            if "S5" in only:
                self.s5()
        except Paused as e:
            self.cur["state"] = "paused"
            self.man["state"], self.man["pass"] = "paused", self.cur["pass"]
            self.save()
            self.say(f"corpus_mirror: paused ({e}); the next run resumes from the cursor")
            return 0
        self.cur["state"] = "complete"
        self.man["state"], self.man["pass"] = ("incomplete" if rc else "complete"), self.cur["pass"]
        self.save()
        self.say(f"corpus_mirror: {self.man['state']}; calls this pass {json.dumps(self.cur['calls'], sort_keys=True)}")
        return rc


def _host(token: str):
    """The real runners: gh with the credential in its child's environment only, git with it in a config variable."""
    import base64
    import urllib.request
    env = {**os.environ, "GH_TOKEN": token, "GH_PROMPT_DISABLED": "1"}
    env.pop("HPO_OWNER_ONLY", None)  # the mirror reads conditionally and over GraphQL; its own gate holds it to reads
    basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    auth = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
            "GIT_CONFIG_VALUE_0": f"AUTHORIZATION: basic {basic}", "GIT_TERMINAL_PROMPT": "0"} if token else {"GIT_TERMINAL_PROMPT": "0"}

    def run(argv):
        p = subprocess.run(argv, capture_output=True, text=True, env=env)
        return p.returncode, p.stdout + p.stderr

    def run_bytes(argv):
        p = subprocess.run(argv, capture_output=True, env=env)
        return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace")

    def git(argv, extra):
        p = subprocess.run(argv, capture_output=True, text=True, env={**{k: v for k, v in os.environ.items() if k != "GH_TOKEN"}, **extra})
        return p.returncode, p.stdout

    def http(url):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "corpus-mirror"}), timeout=30) as r:
                return r.status, r.headers.get("Content-Type", ""), r.read(MAX_MEMBER)
        except Exception as e:  # noqa: BLE001 -- any failure is one unreached page
            return getattr(e, "code", 0) or 0, "", b""
    def new_bare(path):
        """A bare repository built the one way a tracked script builds one (tests/throwaway_git.py): no global
        config, no auto-maintenance. Not a throwaway: it is the mirror, and it stays."""
        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
        from throwaway_git import throwaway_git_init
        os.makedirs(path, mode=0o700, exist_ok=True)
        throwaway_git_init(path, "-q", "--bare")
    return run, run_bytes, git, http, new_bare, auth


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test(Path(__file__), mutants="--no-mutants" not in argv)
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("cmd", choices=["run", "cost"])
    ap.add_argument("--private-root", required=True)
    ap.add_argument("--token-fd", type=int)
    ap.add_argument("--own-identity", action="store_true")
    ap.add_argument("--only", default="S2,S3,S4,S5")
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--site", default="https://tvofi.github.io/heatpump_optimizer/")
    a = ap.parse_args(argv)
    root = Path(a.private_root)
    if not root.is_absolute() or stat.S_IMODE(os.stat(root).st_mode) != 0o700:
        print("corpus_mirror: REFUSED the private root is an absolute path of mode 700")
        return 2
    if a.cmd == "cost":
        cur = json.loads((root / "corpus" / "cursor.json").read_text())
        print(f"corpus_mirror: pass {cur['pass']} ({cur['state']}), calls per bucket {json.dumps(cur['calls'], sort_keys=True)}")
        return 0
    if a.token_fd is None:
        print("corpus_mirror: REFUSED --token-fd names the descriptor the read credential is on (never a variable or an argument)")
        return 2
    with os.fdopen(a.token_fd) as f:
        token = f.read().strip()
    only = [s for s in a.only.split(",") if s]
    if not only or any(s not in ("S2", "S3", "S4", "S5") for s in only):
        print("corpus_mirror: REFUSED --only takes S2, S3, S4 and S5")
        return 2
    os.umask(0o077)
    run, run_bytes, git, http, new_bare, auth = _host(token)
    m = Mirror(root, run=run, run_bytes=run_bytes, git=git, http=http, new_bare=new_bare, repo=a.repo, site=a.site,
               floor=gh_read.FLOOR_OWN if a.own_identity else gh_read.FLOOR_SHARED)
    return m.scan(only, f"https://github.com/{a.repo}", auth)


SELF_TEST_MARK = "# ---" + "--- self-test: mutants edit only the code above this line"
# ------ self-test: mutants edit only the code above this line


class Stub:
    """GitHub, git and the site, as far as the mirror asks; it records every call and can answer a limit once."""

    def __init__(self, n_issues=250, runs=3, ls=None, hostile=None):
        self.calls, self.sleeps, self.clock = [], [], 1000.0
        self.issues = [{"number": i + 1, "title": f"t{i + 1}"} for i in range(n_issues)]
        self.runs = [{"id": 900 + i, "created_at": f"2026-11-0{i + 1}T00:00:00Z", "check_suite_id": 70 + i} for i in range(runs)]
        self.remaining = {"core": 5000, "graphql": 5000}
        self.limit_at = {}       # call index -> the output a limit answer carries
        self.ls = ls if ls is not None else "a\trefs/heads/main\nb\trefs/tags/v1\nc\trefs/pull/7/head\nd\tHEAD\n"
        self.hostile = hostile or {}
        self.fresh: list[str] = []   # every path answered 200, in order
        self.limit_download = 0  # the nth download answers a rate limit, once
        self.down: set[str] = set()  # a read whose path holds one of these answers 502, every time
        self.downloads: list[str] = []

    @staticmethod
    def inc(status, headers=(), body="", tail=""):
        return f"HTTP/2.0 {status}\r\n" + "".join(f"{k}: {v}\r\n" for k, v in headers) + "\r\n" + body + tail

    def rows(self, path):
        base = path.split("?")[0]
        if base.endswith("/issues"):
            return self.issues
        if base.endswith("/actions/runs"):
            return {"workflow_runs": self.runs}
        if base.endswith("/actions/artifacts"):
            return {"artifacts": [{"id": 5, "size_in_bytes": 10}, {"id": 6, "expired": True}]}
        if base.endswith("/releases"):
            return [{"assets": [{"id": 3, "size": 4}]}]
        if base.endswith("/activity"):
            return [{"before": "1" * 40}, {"before": "2" * 40}]
        return []

    def run(self, argv):
        self.calls.append(list(argv))
        if argv == ["gh", "api", "rate_limit"]:
            return 0, json.dumps({"resources": {k: {"limit": 5000, "remaining": v, "reset": 9999} for k, v in self.remaining.items()}})
        k = sum(1 for c in self.calls if c != ["gh", "api", "rate_limit"])
        if k in self.limit_at:
            return 1, self.limit_at.pop(k)
        if argv[:3] == ["gh", "api", "graphql"]:
            return 0, json.dumps({"data": {"repository": {"i1": {"__typename": "Issue"}}}})
        path = argv[3]
        if any(d in path for d in self.down):
            return 1, self.inc(502, [], "", "gh: Bad Gateway (HTTP 502)\n")
        etag = argv[argv.index("-H") + 1].split(": ", 1)[1] if "-H" in argv else ""
        tag = 'W/"' + hashlib.sha256(path.encode()).hexdigest()[:8] + '"'
        if etag == tag:
            return 1, self.inc(304, [("Etag", tag)], "", "gh: HTTP 304\n")
        from urllib.parse import parse_qs, urlsplit
        page = parse_qs(urlsplit(path).query).get("page")
        if "/check-suites/" in path:
            body = {"check_runs": [{"id": 1, "output": {"annotations_count": 0}}]}
        elif path.count("/") == 2 and "?" not in path:
            body = {"has_wiki": False}
        else:
            rows = self.rows(path)
            n = int(page[0]) if page else 1
            cut = lambda xs: xs[(n - 1) * 100:n * 100]  # noqa: E731
            body = {k: cut(v) for k, v in rows.items()} if isinstance(rows, dict) else cut(rows)
        self.fresh.append(path)
        return 0, self.inc(200, [("Etag", tag)], json.dumps(body))

    def run_bytes(self, argv):
        self.calls.append(list(argv))
        path = argv[2]
        if self.limit_download and len(self.downloads) + 1 == self.limit_download:
            self.limit_download = 0
            return 1, b"", "gh: API rate limit exceeded (HTTP 403)"
        self.downloads.append(path)
        if path in self.hostile:
            return 0, self.hostile[path], ""
        if path.endswith("/logs") or path.endswith("/zip"):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as z:
                z.writestr("job/1_step.txt", "log line\n")
            return 0, buf.getvalue(), ""
        return 0, b"asset", ""

    def git(self, argv, env):
        self.calls.append(list(argv))
        if "ls-remote" in argv:
            return 0, self.ls
        if "cat-file" in argv:
            return 1, ""
        if "fetch" in argv and any(a.startswith("2" * 40) for a in argv):
            return 128, ""
        return 0, ""

    def new_bare(self, path):
        self.calls.append(["new-bare", path])

    def http(self, url):
        self.calls.append(["https", url])
        if url.endswith("/site/"):
            return 200, "text/html", b'<a href="a.html">a</a><a href="https://elsewhere.example/x">x</a><a href="/other/y">y</a>'
        if url.endswith("/site/a.html"):
            return 200, "text/html", b'<a href="./">home</a><a href="gone.html">g</a>'
        return 404, "", b""


def zip_of(members, link=None):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in members:
            z.writestr(name, data)
        if link:
            info = zipfile.ZipInfo(link)
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            z.writestr(info, "/etc/passwd")
    return buf.getvalue()


def unreadable_zips() -> dict[str, bytes]:
    """Archives that pass every rule on their names and sizes and whose one member cannot be decoded, by shape."""
    import struct
    plain = zip_of([("m.txt", "hello " * 40)])
    local, central = plain.find(b"PK\x03\x04"), plain.find(b"PK\x01\x02")
    name_len, extra_len = struct.unpack_from("<HH", plain, local + 26)
    start, size = local + 30 + name_len + extra_len, struct.unpack_from("<I", plain, local + 18)[0]

    def patched(fmt, local_off, central_off, value):
        b = bytearray(plain)
        struct.pack_into(fmt, b, local + local_off, value)
        struct.pack_into(fmt, b, central + central_off, value)
        return bytes(b)
    corrupt, short = bytearray(plain), bytearray(plain)
    corrupt[start:start + size] = b"\xff" * size
    short[start + 2:start + size] = b"\x00" * (size - 2)
    two = bytearray(zip_of([("first.txt", "x"), ("m.txt", "hello " * 40)]))
    second = two.find(b"PK\x03\x04", 4)
    name_len, extra_len = struct.unpack_from("<HH", two, second + 26)
    at, n = second + 30 + name_len + extra_len, struct.unpack_from("<I", two, second + 18)[0]
    two[at:at + n] = b"\xff" * n
    return {"its encrypted flag is set": patched("<H", 6, 8, 1), "its compression method is not implemented": patched("<H", 8, 10, 99),
            "its deflate stream is corrupt": bytes(corrupt), "its stream does not hold what its header says": bytes(short),
            "a later member's stream is corrupt, after one that was written": bytes(two)}


def byte_changes(data: bytes):
    """Every archive one byte away from `data`: each offset set to 0x00 and 0xff and with its low and high bit flipped."""
    for k in range(len(data)):
        for v in {0, 0xff, data[k] ^ 1, data[k] ^ 0x80} - {data[k]}:
            yield data[:k] + bytes([v]) + data[k + 1:]


class LocalFailure:
    """While held, the first `count` writes of a file whose path holds `part` fail as this host's file system would."""

    def __init__(self, part: str, error: BaseException, count: int = 1):
        self.part, self.error, self.left, self.real = part, error, count, Path.write_bytes

    def __enter__(self):
        outer = self

        def write_bytes(path, data):
            if outer.left and outer.part in str(path):
                outer.left -= 1
                raise outer.error
            return outer.real(path, data)
        Path.write_bytes = write_bytes
        return self

    def __exit__(self, *exc):
        Path.write_bytes = self.real


def cases(m) -> dict[str, bool]:
    import errno
    import tempfile
    r: dict[str, bool] = {}
    site = "https://example.invalid/site/"
    sec = Stub.inc(403, [("Retry-After", "600")], '{"message": "You have exceeded a secondary rate limit."}', "gh: (HTTP 403)\n")
    spent = Stub.inc(403, [("X-Ratelimit-Remaining", "0"), ("X-Ratelimit-Reset", "4600")], '{"message": "API rate limit exceeded"}', "gh: (HTTP 403)\n")

    def mirror(root, stub, only=("S3",), floor=None, said=None):
        mm = m.Mirror(root, run=stub.run, run_bytes=stub.run_bytes, git=stub.git, http=stub.http, new_bare=stub.new_bare, sleep=stub.sleeps.append,
                      now=lambda: stub.clock, repo="o/r", site=site, say=(said if said is not None else []).append,
                      **({} if floor is None else {"floor": floor}))
        return mm, mm.scan(list(only), "https://example.invalid/o/r", {})

    def issue_pages(stub):
        return [p for p in stub.fresh if "/issues?" in p]

    with tempfile.TemporaryDirectory() as td:
        # The null control first: no limit answer, one pass, every page once.
        a = Stub()
        ma, rc = mirror(Path(td) / "a", a)
        whole = sorted(x["number"] for x in ma.pages("S3", "issues", "issues?state=all&sort=created&direction=asc"))
        r["scan null: with no limit answer one pass reads every page once and completes"] = \
            rc == 0 and ma.cur["state"] == "complete" and whole == list(range(1, 251)) and len(issue_pages(a)) == 3 \
            and len(set(issue_pages(a))) == 3
        r["budget: rate_limit is read before the first call, and the gap is kept between calls"] = \
            a.calls[0] == ["gh", "api", "rate_limit"] and len(a.sleeps) >= len(a.fresh) - 1 and set(a.sleeps) == {m.gh_read.MIN_GAP_S}
        r["reads only: every gh call is a read or a query, and none names a search endpoint"] = \
            all(m.gh_read.is_read(c) or m.gh_read.is_query(c) for c in a.calls if c[:1] == ["gh"]) \
            and not any("search" in " ".join(c) for c in a.calls)
        for label, answer in (("a secondary limit naming a long Retry-After", sec), ("a spent core bucket", spent)):
            b, said = Stub(), []
            b.limit_at = {2: answer}  # the second page's read
            mb, rc1 = mirror(Path(td) / label[:9], b, said=said)
            first = list(issue_pages(b))
            state1, slept = mb.cur["state"], [s for s in b.sleeps if s > 60]
            mb2, rc2 = mirror(Path(td) / label[:9], b)
            got = sorted(x["number"] for x in mb2.pages("S3", "issues", "issues?state=all&sort=created&direction=asc"))
            r[f"pause: {label} pauses the scan at its cursor, exit 0, without sleeping the wait out"] = \
                rc1 == 0 and state1 == "paused" and len(first) == 1 and slept == [] and any("paused" in s for s in said)
            r[f"resume: after {label} the union of pages read is the whole list, and no page is read twice"] = \
                rc2 == 0 and mb2.cur["state"] == "complete" and got == whole and sorted(issue_pages(b)) == sorted(issue_pages(a)) \
                and len(issue_pages(b)) == len(set(issue_pages(b)))
        k = Stub()
        boom = k.run

        def dying(argv):
            if "page=2" in " ".join(argv):
                raise KeyboardInterrupt  # the process is killed mid-list: no handler runs
            return boom(argv)
        try:
            m.Mirror(Path(td) / "crash", run=dying, run_bytes=k.run_bytes, git=k.git, http=k.http, new_bare=k.new_bare, sleep=k.sleeps.append,
                     repo="o/r", say=lambda s_: None).scan(["S3"], "x", {})
        except KeyboardInterrupt:
            pass
        mk, rc = mirror(Path(td) / "crash", k)
        r["crash: a scan killed mid-list resumes at the page after the last one stored, re-reading none"] = \
            rc == 0 and sorted(issue_pages(k)) == sorted(issue_pages(a)) and len(issue_pages(k)) == 3
        c = Stub()
        c.remaining = {"core": 2999, "graphql": 5000}
        mc, rc = mirror(Path(td) / "floor", c)
        r["floor: a core bucket under 60 % pauses before any read, and the same bucket passes the own-identity floor"] = \
            rc == 0 and mc.cur["state"] == "paused" and c.fresh == [] \
            and mirror(Path(td) / "floor-own", Stub(), floor=m.gh_read.FLOOR_OWN)[0].cur["state"] == "complete" \
            and (lambda s: (setattr(s, "remaining", {"core": 2999, "graphql": 5000}), mirror(Path(td) / "floor-own2", s, floor=m.gh_read.FLOOR_OWN)[0].cur["state"])[1])(Stub()) == "complete"
        d = Stub()
        md, _ = mirror(Path(td) / "a", d)   # a second pass over the first scan's cache
        r["incremental: a second pass re-reads every list with If-None-Match and stores nothing new on a 304"] = \
            md.cur["pass"] == 2 and issue_pages(d) == [] and sum(1 for c_ in d.calls if "-H" in c_) >= 3 \
            and sorted(x["number"] for x in md.pages("S3", "issues", "issues?state=all&sort=created&direction=asc")) == whole
        e = Stub()
        me, rc = mirror(Path(td) / "s2", e, only=("S2",))
        r["refs null: three mapped namespaces and HEAD exit 0 with no unmapped line"] = \
            rc == 0 and not any("unmapped" in x for x in me.man["sources"]["S2"]["not_reached"])
        r["refs: a force-pushed commit no ref reaches is fetched by SHA once; refused, it is not_reached: gone"] = \
            me.man["sources"]["S2"].get("served_by_sha_only") == ["1" * 40] \
            and any(x.endswith("2" * 40 + ": gone") for x in me.man["sources"]["S2"]["not_reached"])
        n_gone = lambda: sum(1 for c_ in e.calls if "fetch" in c_ and any(a_.startswith("2" * 40) for a_ in c_))  # noqa: E731
        first_gone = n_gone()
        mirror(Path(td) / "s2", e, only=("S2",))
        r["refs: a commit found gone is an answer, and a later pass does not fetch it again"] = (first_gone, n_gone()) == (1, 1)
        f = Stub(ls="a\trefs/heads/main\nb\trefs/notes/commits\nc\trefs/pull/7/head\nd\trefs/notes/x\ne\trefs/gh-readonly-queue/main/q\n")
        mf, rc = mirror(Path(td) / "s2b", f, only=("S2",))
        r["refs: a fourth namespace is a not_reached line per namespace and a non-zero exit, and the mapped ones are still fetched"] = \
            rc == 1 and mf.man["state"] == "incomplete" and any(a_[:4] == ["git", "-C", str(Path(td) / "s2b" / "corpus" / "git"), "fetch"] for a_ in f.calls) \
            and [x for x in mf.man["sources"]["S2"]["not_reached"] if "unmapped" in x] == ["unmapped namespace refs/gh-readonly-queue/", "unmapped namespace refs/notes/"]
        g = Stub(hostile={"repos/o/r/actions/runs/900/logs": zip_of([("ok.txt", "x"), ("../../escape.txt", "x")]),
                          "repos/o/r/actions/runs/901/logs": zip_of([("ok.txt", "x")], link="l"),
                          "repos/o/r/actions/runs/902/logs": zip_of([("bomb.txt", "0" * (m.MAX_RATIO * 2000))])})
        mg, rc = mirror(Path(td) / "s5", g, only=("S5",))
        corpus = Path(td) / "s5" / "corpus"
        refused = json.loads((corpus / "refused.json").read_text()) if (corpus / "refused.json").exists() else []
        r["archives: a traversing member, a link and a ratio bomb are each refused whole, by rule, and nothing of them is extracted"] = \
            {x["archive"]: x["rule"] for x in refused} == {"logs/900": "a member's path leaves the archive's directory",
                                                            "logs/901": "a member is a link", "logs/902": "a member is past the ratio cap"} \
            and not (corpus / "logs").exists() and not (Path(td) / "escape.txt").exists() and not (Path(td) / "s5" / "escape.txt").exists() \
            and len([x for x in mg.man["sources"]["S5"]["not_reached"] if x.startswith("run logs")]) == 3
        r["archives null: a well-formed archive extracts whole, owner-only, and an expired artifact is gone without a download"] = \
            (corpus / "artifacts" / "5" / "job" / "1_step.txt").read_text() == "log line\n" \
            and stat.S_IMODE(os.stat(corpus / "artifacts" / "5" / "job" / "1_step.txt").st_mode) == 0o600 \
            and mg.cur["items"]["artifacts"] == {"5": "ok", "6": "gone"} and not any(c_[2:3] == ["repos/o/r/actions/artifacts/6/zip"] for c_ in g.calls)
        mirror(Path(td) / "s5", g, only=("S5",))
        r["archives: a refused archive is an answer, and a later pass does not download it again"] = \
            sorted(d_ for d_ in g.downloads if d_.endswith("/logs")) == sorted(f"repos/o/r/actions/runs/{n}/logs" for n in (900, 901, 902))
        shapes = {"a member named for the directory itself": [(".", "x")], "the same through a parent": [("ok.txt", "x"), ("a/..", "x")],
                  "a file that is also a directory": [("a", "x"), ("a/b", "y")], "a directory that is also a file": [("a/b", "y"), ("a", "x")],
                  "a directory entry and a file of one name": [("a/", ""), ("a", "x")]}
        got = {}
        for n_, (label, members) in enumerate(shapes.items()):
            try:
                got[label] = m.safe_extract(zip_of(members), Path(td) / "shape" / str(n_)), (Path(td) / "shape" / str(n_)).exists()
            except Exception as e_:  # the defect: the archive's shape reaches the caller as a traceback
                got[label] = type(e_).__name__, None
        r["archives: a member that is the directory itself, or a path that is both a file and a directory, is refused whole by rule and never raises"] = \
            got == {**{label: ("a member's path is both a file and a directory", False) for label in shapes},
                    "a member named for the directory itself": ("a member's path is the archive's directory", False),
                    "the same through a parent": ("a member's path is the archive's directory", False)}
        try:
            long_name = m.safe_extract(zip_of([("ok.txt", "x"), ("n" * 300, "x")]), Path(td) / "shape" / "long"), (Path(td) / "shape" / "long").exists()
        except Exception as e_:
            long_name = type(e_).__name__, None
        r["archives: a member whose name is past the length cap is refused whole by rule, and one at the cap extracts"] = \
            long_name == ("a member's name is past the length cap", False) \
            and m.safe_extract(zip_of([("d/" + "n" * m.MAX_NAME, "x")]), Path(td) / "shape" / "cap") == ""
        with LocalFailure("/second.txt", OSError(errno.EIO, "Input/output error")):
            try:
                partial = m.safe_extract(zip_of([("first.txt", "x"), ("second.txt", "y")]), Path(td) / "shape" / "partial")
            except OSError as e_:
                partial = e_
        r["archives: a write this host fails is raised, never returned as the archive's rule, and what was written before it is removed"] = \
            isinstance(partial, OSError) and partial.errno == errno.EIO and not (Path(td) / "shape" / "partial").exists()
        r["archives null: nested files, a directory entry and a repeated ancestor extract whole"] = \
            m.safe_extract(zip_of([("./", ""), ("a", "x"), ("b/", ""), ("b/c", "y"), ("b/d/e", "z")]), Path(td) / "shape" / "ok") == "" \
            and sorted(str(f.relative_to(Path(td) / "shape" / "ok")) for f in (Path(td) / "shape" / "ok").rglob("*") if f.is_file()) == ["a", "b/c", "b/d/e"] \
            and m.safe_extract(zip_of([("only/", "")]), Path(td) / "shape" / "nofile") == "" and (Path(td) / "shape" / "nofile").is_dir()
        s_ = Stub(hostile={"repos/o/r/actions/runs/901/logs": zip_of([("a", "x"), ("a/b", "y")])})
        try:
            ms, rc = mirror(Path(td) / "s5shape", s_, only=("S5",))
        except OSError:  # the defect: the scan dies with its cursor unsaved
            ms, rc = m.Mirror(Path(td) / "none", run=s_.run, run_bytes=s_.run_bytes, git=s_.git, http=s_.http, new_bare=s_.new_bare, repo="o/r"), None
        r["archives: an archive of such a shape is recorded as refused, the scan completes, and the other runs are read"] = \
            rc == 0 and ms.cur["state"] == "complete" and ms.cur["items"].get("run logs") == {"900": "ok", "901": "refused: a member's path is both a file and a directory", "902": "ok"} \
            and ms._load("refused.json", []) == [{"archive": "logs/901", "rule": "a member's path is both a file and a directory"}]
        logs_of = lambda stub, n_: sum(1 for d_ in stub.downloads if d_.endswith(f"runs/{n_}/logs"))  # noqa: E731
        unreadable = unreadable_zips()
        got = {}
        for n_, (label, data) in enumerate(unreadable.items()):
            try:
                got[label] = m.safe_extract(data, Path(td) / "unread" / str(n_)), (Path(td) / "unread" / str(n_)).exists()
            except Exception as e_:  # the defect: what the reader raises reaches the caller
                got[label] = "RAISED " + type(e_).__name__, None
        r["archives: a member that cannot be read (encrypted, an unimplemented method, a corrupt or short stream) is refused whole and never raises"
          + ("" if all(v[1] is False for v in got.values()) else f"; got {got}")] = \
            all(why.startswith("a member cannot be read (") and there is False for why, there in got.values()) and len(got) == 5
        try:
            no_zip = m.safe_extract(b"no archive at all", Path(td) / "unread" / "none"), m.safe_extract(b"", Path(td) / "unread" / "none")
        except Exception as e_:
            no_zip = type(e_).__name__
        r["archives: bytes that open as no archive are refused by that rule"] = no_zip == ("not a zip archive", "not a zip archive")
        for label, data in unreadable.items():
            u_ = Stub(hostile={"repos/o/r/actions/runs/901/logs": data})
            try:
                mu, rc = mirror(Path(td) / ("s5u" + str(len(label))), u_, only=("S5",))
                state, items, rows = mu.cur["state"], mu.cur["items"].get("run logs", {}), mu._load("refused.json", [])
            except Exception as e_:  # the defect: the scan dies with its cursor unsaved
                rc, state, items, rows = None, "RAISED " + type(e_).__name__, {}, []
            r[f"archives: through a scan, a logs archive where {label} is recorded as refused, the scan completes and the other runs are read"] = \
                rc == 0 and state == "complete" and {k_: v_ for k_, v_ in items.items() if k_ != "901"} == {"900": "ok", "902": "ok"} \
                and items.get("901", "").startswith("refused: a member cannot be read (") and [x["archive"] for x in rows] == ["logs/901"]
        raised, n_changed = [], 0
        for seed in (zip_of([("m.txt", "hello " * 8)]), zip_of([("a", "x"), ("b/c", "y")]), (lambda b_: (zipfile.ZipFile(b_, "w").writestr("s", "stored"), b_.getvalue())[1])(io.BytesIO())):
            for n_changed, data in enumerate(byte_changes(seed), n_changed + 1):
                try:
                    if not isinstance(m.safe_extract(data, Path(td) / "fuzz"), str):
                        raised.append("no rule")
                except Exception as e_:
                    raised.append(type(e_).__name__)
                shutil.rmtree(Path(td) / "fuzz", ignore_errors=True)
        r[f"archives: each of {n_changed} archives one byte away from a well-formed one extracts or is refused by a rule, and none raises"
          + (f"; raised {sorted(set(raised))}" if raised else "")] = not raised and n_changed > 1000
        for label, error in (("its file system is full (ENOSPC)", OSError(errno.ENOSPC, "No space left on device")),
                             ("a write fails with no OSError", ValueError("synthetic"))):
            w = Stub()
            with LocalFailure("/logs/901/", error):
                try:
                    mw, rc1 = mirror(Path(td) / ("s5w" + label[:5].strip()), w, only=("S5",))
                    st1, nr1 = mw.cur["items"]["run logs"].get("901", ""), [x for x in mw.man["sources"]["S5"]["not_reached"] if x.startswith("run logs 901")]
                except Exception as e_:
                    rc1, st1, nr1 = None, "RAISED " + type(e_).__name__, []
            first = logs_of(w, 901)
            mw2, rc2 = mirror(Path(td) / ("s5w" + label[:5].strip()), w, only=("S5",))
            r[f"local failure: a healthy archive this host could not write because {label} is no answer: not_reached in its pass, nothing refused, nothing left, downloaded again by the next pass and examined"] = \
                rc1 == 0 and st1.startswith("error: this host") and len(nr1) == 1 and (first, logs_of(w, 901)) == (1, 2) and rc2 == 0 \
                and mw2.cur["items"]["run logs"] == {"900": "ok", "901": "ok", "902": "ok"} and mw2._load("refused.json", []) == [] \
                and mw2.man["sources"]["S5"]["units"]["run logs"]["examined"] == 3 \
                and not [x for x in mw2.man["sources"]["S5"]["not_reached"] if x.startswith("run logs")]
        y = Stub()
        real_read = m.zipfile.ZipExtFile.read
        m.zipfile.ZipExtFile.read = lambda *a_, **k_: (_ for _ in ()).throw(MemoryError())
        try:
            my, rc1 = mirror(Path(td) / "s5mem", y, only=("S5",))
            states = set(my.cur["items"]["run logs"].values())
        except BaseException as e_:  # noqa: BLE001 -- MemoryError is no Exception's child
            rc1, states = None, {"RAISED " + type(e_).__name__}
        finally:
            m.zipfile.ZipExtFile.read = real_read
        r["local failure: memory running out while a member is read is this host's failure, never the archive's rule"] = \
            rc1 == 0 and len(states) == 1 and all(st.startswith("error: this host") for st in states) and my._load("refused.json", []) == []
        o_ = Stub()
        with LocalFailure("/assets/3", OSError(errno.EIO, "Input/output error")):
            try:
                mo, rc1 = mirror(Path(td) / "s4w", o_, only=("S4",))
                st1 = mo.cur["items"]["release assets"].get("3", "")
            except Exception as e_:
                rc1, st1 = None, "RAISED " + type(e_).__name__
        mo2, rc2 = mirror(Path(td) / "s4w", o_, only=("S4",))
        r["local failure: every per-item read holds the rule: an asset this host could not store is no answer and is read again"] = \
            rc1 == 0 and st1.startswith("error: this host") and rc2 == 0 and mo2.cur["items"]["release assets"] == {"3": "ok"} \
            and sum(1 for d_ in o_.downloads if d_.endswith("/assets/3")) == 2
        bad = Stub(hostile={"repos/o/r/actions/runs/901/logs": unreadable["its deflate stream is corrupt"]})
        try:
            mirror(Path(td) / "s5bad", bad, only=("S5",))
            mb2, rc2 = mirror(Path(td) / "s5bad", bad, only=("S5",))
        except Exception:
            mb2, rc2 = mirror(Path(td) / "s5none", Stub(), only=("S5",))[0], None
        r["local failure null: an archive that is itself bad stays refused: the next pass downloads it no second time and still lists it not_reached"] = \
            rc2 == 0 and logs_of(bad, 901) == 1 and mb2.cur["items"]["run logs"]["901"].startswith("refused: ") \
            and len([x for x in mb2.man["sources"]["S5"]["not_reached"] if x.startswith("run logs 901: refused: ")]) == 1 \
            and (mb2.man["sources"]["S5"]["units"]["run logs"]["universe"], mb2.man["sources"]["S5"]["units"]["run logs"]["examined"]) == (3, 2)
        t = Stub()
        t.down = {"/check-suites/71/"}
        mt, rc1 = mirror(Path(td) / "s5t", t, only=("S5",))
        unit1, nr1 = dict(mt.man["sources"]["S5"]["units"]["run check runs"]), list(mt.man["sources"]["S5"]["not_reached"])
        asked1 = sum(1 for c_ in t.calls if "/check-suites/71/" in " ".join(c_))
        t.down, n_before = set(), len(t.calls)
        mt2, rc2 = mirror(Path(td) / "s5t", t, only=("S5",))
        later = [" ".join(c_) for c_ in t.calls[n_before:]]
        r["transient: a read that answers an error is not_reached in its pass and is read again by the next, where it is examined"] = \
            rc1 == 0 and (unit1["universe"], unit1["examined"]) == (3, 2) and [x for x in nr1 if x.startswith("run check runs 901: error")] != [] and asked1 >= 1 \
            and mt2.man["sources"]["S5"]["units"]["run check runs"]["examined"] == 3 \
            and mt2.man["sources"]["S5"]["not_reached"] == ["artifacts 6: gone"] \
            and mt2.cur["items"]["run check runs"] == {"900": "ok", "901": "ok", "902": "ok"}
        r["transient null: the pass that re-reads it reads no answered unit again"] = \
            sum(1 for c_ in later if "/check-suites/71/" in c_) == 1 and not any("/check-suites/70/" in c_ or "/check-suites/72/" in c_ or c_.endswith("/logs") for c_ in later)
        h = Stub()
        mh, rc = mirror(Path(td) / "s5ok", h, only=("S5",))
        n_logs = sum(1 for c_ in h.calls if c_[2:3] and str(c_[2]).endswith("/logs"))
        mirror(Path(td) / "s5ok", h, only=("S5",))
        r["runs: each run's logs and check runs are read once, and a later pass reads none of them again"] = \
            n_logs == 3 and sum(1 for c_ in h.calls if c_[2:3] and str(c_[2]).endswith("/logs")) == 3 \
            and mh.man["sources"]["S5"]["units"]["run logs"] == {"enumerator": mh.man["sources"]["S5"]["units"]["run logs"]["enumerator"], "universe": 3, "examined": 3} \
            and (Path(td) / "s5ok" / "corpus" / "logs" / "900" / "job" / "1_step.txt").exists()
        q, said = Stub(), []
        q.limit_download = 2
        mq, rc1 = mirror(Path(td) / "s5p", q, only=("S5",), said=said)
        state1 = mq.cur["state"]
        mq2, rc2 = mirror(Path(td) / "s5p", q, only=("S5",))
        logs_read = [d_ for d_ in q.downloads if d_.endswith("/logs")]
        r["pause in a per-item read: a download's rate-limit answer pauses, and the resume downloads every run's logs once"] = \
            rc1 == 0 and state1 == "paused" and rc2 == 0 and mq2.cur["state"] == "complete" \
            and sorted(logs_read) == sorted(f"repos/o/r/actions/runs/{n}/logs" for n in (900, 901, 902))
        i = Stub()
        mi, rc = mirror(Path(td) / "s4", i, only=("S4",))
        idx = json.loads((Path(td) / "s4" / "corpus" / "site" / "index.json").read_text())
        r["site: the crawl stays on the site's own prefix, records a dead link, and stores each page once"] = \
            sorted(idx) == [site, site + "a.html"] and [c_[1] for c_ in i.calls if c_[0] == "https"] == [site, site + "a.html", site + "gone.html"] \
            and any(x.startswith("site ") and x.endswith("HTTP 404") for x in mi.man["sources"]["S4"]["not_reached"])
        r["manifest: every source states its denominators and what no endpoint serves, and the files are owner-only"] = \
            all(set(u) == {"enumerator", "universe", "examined"} for s in (ma, mg, mi) for src in s.man["sources"].values() for u in src["units"].values()) \
            and mg.man["sources"]["S5"]["unserved"] == m.UNSERVED["S5"] and ma.man["sources"]["S3"]["unserved"] == m.UNSERVED["S3"] \
            and stat.S_IMODE(os.stat(Path(td) / "a" / "corpus" / "MANIFEST.json").st_mode) == 0o600 \
            and stat.S_IMODE(os.stat(Path(td) / "a" / "corpus" / "pages" / "issues" / "1.json").st_mode) == 0o600
        j = Stub()
        mj = m.Mirror(Path(td) / "gate", run=j.run, run_bytes=j.run_bytes, git=j.git, http=j.http, new_bare=j.new_bare, sleep=j.sleeps.append, repo="o/r")
        blocked = []
        for argv in (["gh", "api", "-i", "search/issues?q=x"], ["gh", "api", "repos/o/r/issues", "-f", "title=x"],
                     ["gh", "api", "graphql", "-f", "query=mutation{x}"], ["gh", "issue", "create"]):
            try:
                mj._gate(argv, "core")
                blocked.append(False)
            except AssertionError:
                blocked.append(True)
        r["gate: a search path, a field write, a mutation or any other gh command stops the mirror before the call"] = \
            blocked == [True] * 4 and j.calls == []
    r["unmapped: only refs/ names outside heads, tags and pull count, each namespace once"] = \
        m.unmapped("a\tHEAD\nb\trefs/heads/x\nc\trefs/notes/a\nd\trefs/notes/b\ne\trefs/pull/1/merge\n") == ["refs/notes/"]
    r["links: relative and absolute same-site links are kept, another host and a fragment are cut"] = \
        m.links(site, '<a href="b.html#x">b</a><img src="/site/i.png"><a href="http://example.invalid/site/c">c</a><a href="https://o.example/">o</a>') \
        == [site + "b.html", site + "i.png"]
    return r


#: (needle, replacement, the case that must fail). One per predicate.
MUTANTS = {
    "cursor write at a pause": ('            self.save()\n            self.say(f"corpus_mirror: paused', '            self.say(f"corpus_mirror: paused', "downloads every run's logs once"),
    "cursor write per page": ("            self.save()  # the cursor write: a resume starts at the page after the last one stored\n", "", "killed mid-list resumes"),
    "pause on a limit": ('        if wait is not None:\n            raise Paused(f"rate limit: the answer names a {wait:.0f} s wait")\n', "", "pauses the scan at its cursor"),
    "floor": ("            if low:\n                raise Paused(", "            if False:\n                raise Paused(", "under 60 % pauses"),
    "budget first": ("        self.since_budget = gh_read.BATCH  # the first call is preceded by a budget read", "        self.since_budget = 0", "rate_limit is read before the first call"),
    "gap": ('        if sum(self.cur["calls"].values()):\n            self.sleep(gh_read.MIN_GAP_S)\n', "", "gap is kept between calls"),
    "reads only": ('        if not (gh_read.is_read(argv) or gh_read.is_query(argv)) or', "        if", "a field write, a mutation"),
    "no search": (' or path.lstrip("/").split("?")[0].split("/")[0] == "search":', ":", "a search path"),
    "etag sent": ('st["etags"].get(str(n), ""))', '"")', "If-None-Match"),
    "namespace exit": ("        return 1 if bad else 0\n", "        return 0\n", "a fourth namespace"),
    "namespace line": ('        for ns in bad:\n            self.missed("S2", f"unmapped namespace {ns}")\n', "", "a fourth namespace"),
    "by sha": ('                self.source("S2").setdefault("served_by_sha_only", []).append(sha)\n', "", "fetched by SHA once"),
    "traversal": ("not (target == base or target.startswith(base + os.sep)):", "False:", "a traversing member"),
    "link": ("        if stat.S_ISLNK(info.external_attr >> 16):\n", "        if False:\n", "a link and a ratio bomb"),
    "ratio": ("        if info.file_size > MAX_RATIO * max(info.compress_size, 1):\n", "        if False:\n", "a ratio bomb"),
    "directory itself": ("        if target == base and not info.is_dir():\n", "        if False:\n", "a member that is the directory itself"),
    "file and directory": ("    if files & parents:\n", "    if False:\n", "a member that is the directory itself"),
    "ancestors": ("        while len(parent) > len(base):  #", "        while False:  #", "a member that is the directory itself"),
    "archive boundary": ("    except Exception as e:  # noqa: BLE001 -- the boundary is the rule", "    except (OSError, ValueError, zipfile.BadZipFile) as e:  #", "a member that cannot be read"),
    "archive boundary, zipfile's own": ("    except Exception as e:  # noqa: BLE001 -- the boundary is the rule", "    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError, NotImplementedError) as e:  #", "its deflate stream is corrupt is recorded as refused"),
    "memory is the host's": ("    except MemoryError:\n        raise\n    except Exception as e:  # noqa: BLE001 -- the boundary is the rule", "    except Exception as e:  # noqa: BLE001 -- the boundary is the rule", "memory running out"),
    "unreadable member": ('                if bad:\n                    return f"a member cannot be read ({bad})"\n', "", "a member that cannot be read"),
    "unreadable archive": ('    if bad:\n        return "not a zip archive"\n', '    if bad:\n        raise zipfile.BadZipFile(bad)\n', "open as no archive"),
    "host write raised": ('                    raise OSError(f"a member could not be written ({type(e).__name__})") from e\n', "                    raise\n", "a write fails with no OSError"),
    "host write not a rule": ("                except OSError:\n                    raise\n", '                except OSError as e:\n                    return f"a member cannot be written ({type(e).__name__})"\n', "its file system is full"),
    "partial removed": ("            if not whole:\n                shutil.rmtree(dest, ignore_errors=True)\n", "            pass\n", "what was written before it is removed"),
    "partial of a refused removed": ("            if not whole:\n", "            if False:\n", "a member that cannot be read"),
    "read once": ('                        self.missed(s, f"{name} {i}: {done[i]}")\n                    continue\n', '                        self.missed(s, f"{name} {i}: {done[i]}")\n', "a later pass reads none of them again"),
    "host failure caught": ("                except (OSError, MemoryError) as e:\n", "                except MemoryError as e:\n", "its file system is full"),
    "memory failure caught": ("                except (OSError, MemoryError) as e:\n", "                except OSError as e:\n", "memory running out"),
    "host failure is no answer": ('HOST_FAILED = "error: this host failed"', 'HOST_FAILED = "refused: this host failed"', "its file system is full"),
    "kept answer listed": ('                    if done[i] != "ok":  # an answer kept from an earlier pass is still not reached in this one\n                        self.missed(s, f"{name} {i}: {done[i]}")\n', "", "still lists it not_reached"),
    "an archive of no file": ("            os.makedirs(dest, mode=0o700, exist_ok=True)  # an archive of no file", "            pass  # an archive of no file", "archives null: nested files"),
    "name cap": ("        if any(len(part.encode(", "        if False and any(len(part.encode(", "past the length cap"),
    "name at the cap": ("> MAX_NAME for part in", ">= MAX_NAME for part in", "one at the cap extracts"),
    "refusal recorded": ('        rows.append({"archive": where, "rule": why})\n', "", "is recorded as refused"),
    "no answer is asked again": ("if not answered(state)]:", "if False]:", "is read again by the next"),
    "an answer is kept": ("if not answered(state)]:", "if True]:", "reads no answered unit again"),
    "refused is an answer": (' or state.startswith("refused: ")', "", "a refused archive is an answer"),
    "gone is an answer": ('ANSWERED = ("ok", "gone")', 'ANSWERED = ("ok",)', "a commit found gone is an answer"),
    "an error is no answer": ("    return state in ANSWERED or", "    return True or", "is read again by the next"),
    "judged whole": ("        why = archive_refusal(zf, dest)\n        if why:\n            return why\n", "", "nothing of them is extracted"),
    "expired": ('            if arts[i].get("expired"):\n                return "gone"\n', "", "an expired artifact is gone"),
    "site prefix": ("                    if nxt.startswith(self.site) and nxt not in seen:\n", "                    if nxt not in seen:\n", "stays on the site's own prefix"),
    "owner-only files": ("        os.chmod(tmp, 0o600)\n", "        os.chmod(tmp, 0o644)\n", "the files are owner-only"),
    "new pass": ('                st["next"], st["done"] = 1, False\n', "                pass\n", "re-reads every list"),
}


def self_test(path: Path, mutants: bool = True) -> int:
    import importlib.util
    import shutil
    import tempfile
    bad = []

    def load(p: Path):
        spec = importlib.util.spec_from_file_location("corpus_mirror_under_test", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    for name, ok in cases(load(path)).items():
        print(("ok   " if ok else "FAIL ") + name)
        if not ok:
            bad.append(name)
    if mutants:
        code, sep, tail = path.read_text().partition(SELF_TEST_MARK)
        for name, (old, new, case) in MUTANTS.items():
            if code.count(old) != 1:
                print(f"FAIL mutant {name}: needle found {code.count(old)} times in the code")
                bad.append("mutant " + name)
                continue
            with tempfile.TemporaryDirectory() as td:
                shutil.copy(path.with_name("gh_read.py"), Path(td) / "gh_read.py")
                mp = Path(td) / path.name
                mp.write_text(code.replace(old, new) + sep + tail)
                p = subprocess.run([sys.executable, "-I", str(mp), "--self-test", "--no-mutants"],
                                   capture_output=True, text=True, timeout=300)
            killed = p.returncode != 0 and any(ln.startswith("FAIL") and case in ln for ln in p.stdout.splitlines())
            print(("ok   " if killed else "FAIL ") + f"mutant killed: {name} (by '{case}')")
            if not killed:
                bad.append("mutant " + name)
    print("corpus_mirror self-test: " + ("FAIL " + "; ".join(bad) if bad else f"ok ({'with' if mutants else 'without'} mutants)"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
