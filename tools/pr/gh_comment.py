#!/usr/bin/env python3
"""Post or patch a GitHub comment from a file, and prove it landed.

The countermeasure for the `gh api -f body=@FILE` class, analysed by the
root-cause seat on #541 comment 5625671141 (2026-09-10). Read that comment for
the cause, the process state and the cost test; this file is its product.

Why it exists: `gh api -f body=@FILE` sends the literal string "@FILE" as the
comment body, exits 0, and returns a well-formed comment object with an id and
an html_url. `-f` is `--raw-field` and never reads files; `-F` is `--field` and
does. The two spellings differ by the case of one letter, the wrong one is the
natural specialisation of `gh api --help`'s own comment-posting example, and it
fails open -- nothing between typing the command and believing it worked
carries a signal. Four instances in one day; three of them in seats that had
been warned about this exact flag in writing. Compliance with the warning: 0/3.

So the countermeasure is not a fifth warning. It removes the composition step:
the caller passes a file path and never writes a field flag at all. The payload
is built with json.dumps and handed to `gh api --input`, and the run exits
non-zero unless the comment read back off the API is byte-identical to the file.

Fail-closed is the whole point. Every path that cannot establish byte-identity
-- an absent file, an empty file, an over-cap body, a path-shaped body, a gh
that exited non-zero, a response with no body field, a body that differs by one
byte -- exits non-zero. A check that goes green when it cannot look converts an
open defect into a closed one, which is the failure this repository is worst at.

Usage:
  gh_comment.py post   --repo O/R --issue N   --body-file F
  gh_comment.py patch  --repo O/R --comment I --body-file F
  gh_comment.py verify --repo O/R --comment I --body-file F
  gh_comment.py self-test          (offline; drives every refusal by name)

  --dry-run on post/patch stops after the refusals, before the write.
  --withdraw-mandate CID on post/patch lets the body revoke mandate CID.

THE MANDATE GUARD (triage P336, two instances). budget_raise_gate.py voids a
mandate on any owner-account comment on #201 whose CURRENT body pairs a form
of "revoke" with the mandate comment's id, so a seat's state comment naming a
group whose name holds the word froze every mandated raise. A post or a patch
to #201 is refused when budget_raise_gate.revokes() holds for the body and the
id of a #201 comment budget_raise_gate.revocable() reads as a grant, unless
--withdraw-mandate names that id. Both predicates are imported, never copied.
THIS ENCODES A DESIGN CHOICE: it refuses whatever account posts, since the
guard does not know which one gh holds and an agent's text is reworded at no
cost. Stated gap: a raw `gh api` or `gh issue comment` bypasses it;
comment-readback.md makes this file the posting instrument.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

# A body that is nothing but a filesystem path -- the exact product of the
# defect. The `@` is optional because `-f body=@F` posts "@F" while a seat that
# pipes the wrong variable into a file gets the path without it.
#
# THIS ENCODES A DESIGN CHOICE, stated rather than left for the next reader to
# discover: a one-line, space-free body that is exactly a path fires even
# without the `@` -- a body of exactly `docs/HANDOVER.md` is refused. That is
# deliberate. Such a body is not a comment anyone means to post, and the cost of
# the refusal is one `--` prefix or one more word. It is measured against the
# real corpus rather than asserted; see the sweep in the pull request that
# landed this file. A bare URL does not fire (`https:` cannot start a path
# segment here), and neither does anything containing whitespace.
PATH_SHAPED = re.compile(
    r"^@?(?:/|\./|\.\./|~/|[A-Za-z0-9_.\-]+/)[^\s]*$"   # anything with a separator
    r"|^@[A-Za-z0-9_.\-]+\.[A-Za-z0-9]{1,6}$"           # a bare @filename.ext
)

# Bodies longer than this are not paths, whatever else they are; the shape check
# does not need to scan a 20 000-character verdict.
PATH_MAX = 200

MAX_BODY = 65536  # GitHub's comment-body limit; refuse before the API does.


class Refused(Exception):
    """A fail-closed refusal. Carries the message the caller sees."""


def is_path_shaped(body: str) -> bool:
    t = body.strip()
    if not t or "\n" in t or len(t) > PATH_MAX:
        return False
    return bool(PATH_SHAPED.match(t))


def die(msg: str) -> None:
    raise Refused(msg)


def short_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


SHARED_ROOTS = ("/tmp", "/private/tmp", "/var/tmp", "/private/var/tmp")


def in_shared_root(path: str) -> bool:
    """True when the file, links resolved, sits directly in a shared root.

    Seats of one session share a scratchpad and a machine shares /tmp, so a
    body.md there is overwritten by the next seat choosing the obvious name --
    the #201 root-cause comment for the pull request that added this counts the
    instances. `tools/audit/prepr.sh`'s `shared_root` is the same predicate, and
    its comment states the scope, including why a mkstemp file is refused.
    """
    d = os.path.dirname(os.path.realpath(path))
    roots = SHARED_ROOTS + (os.environ.get("TMPDIR", ""), os.environ.get("HOME", ""))
    base = os.path.basename(d)
    return (d in {os.path.realpath(r) for r in roots if r}
            or base == "scratchpad" or re.fullmatch(r"claude-[0-9]+", base) is not None)


def read_body(path: str) -> str:
    """Read the body file, or refuse. Never returns a body it cannot vouch for."""
    if in_shared_root(path):                     # fail closed on a shared root
        die(f"body file {path} sits directly in a root other seats write to; "
            "move it to your own subdirectory, e.g. <abs-scratch>/<seat>/")
    try:
        with open(path, encoding="utf-8") as fh:
            body = fh.read()
    except OSError as exc:                       # fail closed on absence
        die(f"body file unreadable: {exc}")
    except UnicodeDecodeError as exc:            # fail closed on non-UTF-8
        die(f"body file is not UTF-8: {exc}")
    if not body.strip():                         # fail closed on emptiness
        die(f"body file is empty: {path}")
    if is_path_shaped(body):                     # fail closed on the defect shape
        die(
            f"body is a bare filesystem path ({body.strip()!r}). "
            "This is what `gh api -f body=@FILE` posts. Pass the file, not its name."
        )
    if len(body) > MAX_BODY:                     # fail closed on over-cap
        die(f"body is {len(body)} chars, over GitHub's {MAX_BODY}-character limit")
    return body


def privacy_check(body: str, ident=None) -> None:
    """Refuse a body that names this host: its home, account name, uid or a
    session temp root (#2310's class; a verdict's evidence line carried the
    home path), or one carrying a tool's attribution (R10-FLY-NO-FOOTERS: a
    session link, the generated-by footer). ref_privacy.py owns the classes;
    the text is not echoed."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "audit", "seat"))
    import ref_privacy
    why = ref_privacy.body_refusal(body, ident)
    if why:
        die(f"{why} would publish this host (#2310) or a tool's attribution; post it home-relative (~/...) "
            "or without the path, and with no footer")


def positive_int(value: str, what: str) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        die(f"{what} must be an integer, got {value!r}")
    if n <= 0:
        die(f"{what} must be positive, got {n}")
    return n


def gh(args: list[str]) -> str:
    """Run gh. A non-zero exit is a refusal, never a swallowed failure."""
    try:
        proc = subprocess.run(["gh", *args], capture_output=True, text=True)
    except OSError as exc:
        die(f"could not run gh: {exc}")
    if proc.returncode != 0:
        die(f"gh exited {proc.returncode}: {proc.stderr.strip()[:400]}")
    return proc.stdout


def fetch_comment(repo: str, cid: int) -> dict:
    out = gh(["api", f"/repos/{repo}/issues/comments/{cid}"])
    try:
        obj = json.loads(out)
    except ValueError as exc:
        die(f"read-back returned output that is not JSON: {exc}")
    if not isinstance(obj, dict):
        die("read-back returned a non-object; read-back could not be performed")
    return obj


def _gate():
    """budget_raise_gate, imported from its tree path: one definition of the
    revocation test, the grant reading and the tracking issue."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "policy"))
    import budget_raise_gate
    return budget_raise_gate


def fetch_thread(repo: str, issue: int) -> list[dict]:
    out = gh(["api", "--paginate", "--slurp", f"/repos/{repo}/issues/{issue}/comments?per_page=100"])
    try:
        pages = json.loads(out)
    except ValueError as exc:
        die(f"the #{issue} thread read returned output that is not JSON: {exc}")
    return [c for page in pages for c in page]


def mandate_guard(repo: str, body: str, withdraw, issue=None, comment=None,
                  fetch=fetch_comment, thread=fetch_thread, now=None) -> None:
    """Refuse a post to `issue`, or a patch of `comment`, on the tracking issue
    whose body the gate would read as revoking a mandate that can still bind,
    unless `withdraw` is that mandate's id. A read that fails refuses (gh)."""
    g = _gate()
    if repo.lower() != g.DEFAULT_REPO.lower() or not g.MANDATE_REVOKED.search(body):
        return
    if issue is not None:
        on = issue == g.MANDATE_ISSUE
    else:
        on = str(fetch(repo, comment).get("issue_url") or "").endswith(g.MANDATE_ISSUE_URL)
    if not on:
        return
    now = now or datetime.datetime.now(datetime.timezone.utc)
    hit = sorted({c.get("id") for c in thread(repo, g.MANDATE_ISSUE)
                  if g.revocable(c, now) and g.revokes(body, c.get("id"))} - {withdraw})
    if hit:
        die(f"on #{g.MANDATE_ISSUE} this body would void mandate comment(s) {', '.join(map(str, hit))}: "
            "budget_raise_gate.py reads an owner-account comment pairing the revocation word with a "
            "mandate's id as revoking it (triage P336). Reword it, or pass --withdraw-mandate <id> "
            "to withdraw that mandate on purpose")


def write(repo: str, endpoint: str, method: str, body: str) -> dict:
    """POST or PATCH a JSON payload. No field flag is composed anywhere here."""
    fd, payload = tempfile.mkstemp(suffix=".json", prefix="gh_comment_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump({"body": body}, fh)      # JSON, not a field flag
        out = gh(["api", f"/repos/{repo}/{endpoint}",
                  "--method", method, "--input", payload])
    finally:
        try:
            os.unlink(payload)
        except OSError:
            pass
    try:
        obj = json.loads(out)
    except ValueError as exc:
        die(f"gh returned output that is not JSON: {exc}")
    if not isinstance(obj, dict) or "id" not in obj:
        die(f"gh returned no comment id; cannot verify what landed: {out[:200]!r}")
    return obj



def readback(repo: str, cid: int, body: str, fetch=fetch_comment) -> int:
    """Refuse unless the live comment is byte-identical to `body`.

    `fetch` is a seam so every branch below is drivable offline by self_test();
    a refusal path that only production can reach is a refusal path nobody has
    ever seen work.
    """
    obj = fetch(repo, cid)
    live = obj.get("body")
    if live is None:                             # cannot verify -> not green
        die(f"comment {cid} returned no body field; read-back could not be performed")
    if not isinstance(live, str):
        die(f"comment {cid} returned a non-string body; read-back could not be performed")
    ok = live == body
    print(f"READBACK id={cid} live_len={len(live)} want_len={len(body)} "
          f"live_sha={short_sha(live)} want_sha={short_sha(body)} identical={ok}")
    if not ok:
        first = live.splitlines()[0][:120] if live.splitlines() else ""
        print(f"  live first line: {first!r}", file=sys.stderr)
        die("the comment on the record is not the body that was sent")
    return 0


# ---------------------------------------------------------------------------
# The offline acceptance. Every assertion is named; a failure prints its name.
# ---------------------------------------------------------------------------

# The 72-character body that `-f body=@FILE` actually posted as comment
# 5621913580 on #201 (2026-09-10, since deleted; reconstructed from the record).
DEFECT_BODY = "@/private/tmp/claude-501/heatpump-optimizer-orchestrator/out/sync-201.md"

# Shapes this repository really posts. Hand-checked negatives; none may fire.
REAL_NEGATIVES = (
    "frozen at b86a4bd",
    "claimed-by: zcode · branch zcode/audit-r2-216",
    "docs/HANDOVER.md is stale.",
    "Fix review: merge",
    "v6.3.18",
    "#201",
    "https://github.com/tvofi/heatpump_optimizer/pull/738",
    "leaves #201 open.",
    "See tools/audit/briefs/fixer.md step 3 for the null control.",
    "LGTM",
)

MORE_POSITIVES = (
    "@/abs/path.md",
    "@rel/path.md",
    "@bare-name.md",
    "@./x",
    "@~/x",
    "/private/tmp/x/out/body.md",
    "@../up/one.md",
)


def self_test() -> int:
    """Drive every refusal by name. Offline; no network, no writes."""
    failures: list[str] = []

    def check(name: str, cond: bool) -> None:
        print(f"{'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            failures.append(name)

    def refuses(fn) -> tuple[bool, str]:
        try:
            fn()
        except Refused as exc:
            return True, str(exc)
        return False, ""

    tmp = tempfile.mkdtemp(prefix="gh_comment_selftest_")

    def wrote(name: str, text: str) -> str:
        p = os.path.join(tmp, name)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        return p

    # -- Arm 1: the real defect body is refused ------------------------------
    hit, msg = refuses(lambda: read_body(wrote("defect.md", DEFECT_BODY)))
    check("arm1_defect_body_refused", hit)
    check("arm1_defect_message_names_the_flag", "gh api -f body=@FILE" in msg)
    check("arm1_defect_predicate_true", is_path_shaped(DEFECT_BODY))

    # -- Arm 2: a real repaired body passes ----------------------------------
    healthy = (
        "## Sync to #201\n\n"
        "Merged #738 at ae36eff. The Delivery-status table is updated and\n"
        "`docs/HANDOVER.md` names the same head.\n"
    )
    ok_body = None
    try:
        ok_body = read_body(wrote("repaired.md", healthy))
    except Refused as exc:
        check(f"arm2_healthy_body_accepted ({exc})", False)
    check("arm2_healthy_body_accepted", ok_body == healthy)

    # -- Arm 3: the predicate's own two-sided control -------------------------
    for s in MORE_POSITIVES:
        check(f"arm3_positive[{s}]", is_path_shaped(s))
    for s in REAL_NEGATIVES:
        check(f"arm3_negative[{s}]", not is_path_shaped(s))

    # -- Arm 4: it does not go green by skipping ------------------------------
    body = "the body that was sent\n"

    def fetch_identical(_repo, cid):
        return {"id": cid, "body": body}

    def fetch_one_byte_off(_repo, cid):
        return {"id": cid, "body": body.rstrip("\n")}

    def fetch_other_comment(_repo, cid):
        return {"id": cid, "body": "a completely different comment body\n"}

    def fetch_no_body(_repo, cid):
        return {"id": cid}

    def fetch_null_body(_repo, cid):
        return {"id": cid, "body": None}

    def fetch_nonstring_body(_repo, cid):
        return {"id": cid, "body": 42}

    def fetch_empty_body(_repo, cid):
        return {"id": cid, "body": ""}

    identical_rc = None
    try:
        identical_rc = readback("o/r", 1, body, fetch=fetch_identical)
    except Refused as exc:
        check(f"arm4_identical_passes ({exc})", False)
    check("arm4_identical_passes", identical_rc == 0)

    for name, fetch in (
        ("one_byte_difference", fetch_one_byte_off),
        ("wrong_comment_id", fetch_other_comment),
        ("no_body_field", fetch_no_body),
        ("null_body_field", fetch_null_body),
        ("nonstring_body_field", fetch_nonstring_body),
        ("empty_body_field", fetch_empty_body),
    ):
        hit, _ = refuses(lambda f=fetch: readback("o/r", 1, body, fetch=f))
        check(f"arm4_refuses_{name}", hit)

    hit, _ = refuses(lambda: read_body(os.path.join(tmp, "does-not-exist.md")))
    check("arm4_refuses_absent_file", hit)

    hit, _ = refuses(lambda: read_body(wrote("empty.md", "")))
    check("arm4_refuses_empty_file", hit)

    hit, _ = refuses(lambda: read_body(wrote("blank.md", "   \n\n\t\n")))
    check("arm4_refuses_whitespace_only_file", hit)

    hit, _ = refuses(lambda: read_body(wrote("big.md", "x" * (MAX_BODY + 1))))
    check("arm4_refuses_over_cap_body", hit)

    at_cap = None
    try:
        at_cap = read_body(wrote("cap.md", "x" * MAX_BODY))
    except Refused as exc:
        check(f"arm4_accepts_body_at_cap ({exc})", False)
    check("arm4_accepts_body_at_cap", at_cap is not None and len(at_cap) == MAX_BODY)

    # -- Arm 5: a body in a shared root is refused, a seat's own is not -------
    os.makedirs(os.path.join(tmp, "scratchpad", "seat"))
    hit, _ = refuses(lambda: read_body(wrote("scratchpad/body.md", healthy)))
    check("arm5_refuses_body_directly_in_scratchpad", hit)
    check("arm5_refuses_body_directly_in_tmp", in_shared_root("/tmp/body.md"))
    hit, _ = refuses(lambda: read_body(wrote("scratchpad/seat/body.md", healthy)))
    check("arm5_accepts_body_in_seat_subdirectory", not hit)
    check("arm5_accepts_body_in_mkdtemp", not in_shared_root(os.path.join(tmp, "b.md")))
    for var in ("TMPDIR", "HOME"):
        saved = os.environ.get(var)
        os.environ[var] = tmp
        check(f"arm5_refuses_body_directly_in_{var}", in_shared_root(os.path.join(tmp, "b.md")))
        if saved is None:
            del os.environ[var]
        else:
            os.environ[var] = saved
    check("arm5_refuses_body_directly_in_claude_uid", in_shared_root("/x/claude-501/body.md"))
    fd, mk = tempfile.mkstemp()
    os.close(fd)
    check("arm5_refuses_plain_mkstemp_file", in_shared_root(mk))
    os.unlink(mk)
    link = os.path.join(tmp, "scratchpad", "seat", "link.md")
    os.symlink(wrote("scratchpad/root.md", healthy), link)
    check("arm5_refuses_link_to_root_file", in_shared_root(link))
    os.symlink(wrote("scratchpad/seat/own.md", healthy), os.path.join(tmp, "link2.md"))
    check("arm5_accepts_link_to_seat_file", not in_shared_root(os.path.join(tmp, "link2.md")))

    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "audit", "seat"))
    import ref_privacy
    fid = ref_privacy.Identity.made({"/" + "/".join(("Users", "exampleuser"))}, {"exampleuser"}, 4242)
    hit, why = refuses(lambda: privacy_check("evidence: /" + "/".join(("Users", "exampleuser", ".zcode", "bus")), fid))
    check("arm_privacy_refuses_a_body_naming_the_home (#2310)", hit and "exampleuser" not in why)
    hit, _ = refuses(lambda: privacy_check("evidence: ~/.zcode/bus/verdicts/7", fid))
    check("arm_privacy_passes_the_home_relative_body (null control)", not hit)
    body_f = os.path.join(tmp, "seat", "leak.md")
    os.makedirs(os.path.dirname(body_f), exist_ok=True)
    with open(body_f, "w", encoding="utf-8") as fh:
        fh.write("evidence: " + os.path.realpath(os.environ.get("HOME", "/")) + "/x\n")
    hit, _ = refuses(lambda: run(["post", "--repo", "o/r", "--issue", "7", "--body-file", body_f, "--dry-run"]))
    check("arm_privacy_post_dry_run_refuses_this_hosts_home (the wiring)", hit)

    # -- Arm 6: the mandate guard (triage P336), through run() --------------
    # The fake #201 thread holds the grants the rows name; the field text is
    # an excerpt of #201 comment 6546832523 as first posted (2026-10-31), which
    # #3006's budget-raise-gate read as voiding the session mandate.
    g = _gate()
    owner = {"login": g.OWNER_LOGIN, "id": g.OWNER_ID, "type": g.OWNER_TYPE}
    on201 = f"https://api.github.com/repos/{g.DEFAULT_REPO}/issues/{g.MANDATE_ISSUE}"

    def grant(cid, until="programme-end", user=owner):
        return {"id": cid, "user": user, "issue_url": on201, "created_at": "2026-10-01T00:00:00Z",
                "updated_at": "2026-10-01T00:00:00Z",
                "body": f"MANDATE: agents may approve as {g.OWNER_LOGIN}, scope all, "
                        f"from 2026-10-01T00:00Z until {until}\nreason"}
    BRIEF_ID, LIVE_ID, OLD_ID, ALIEN_ID = 6175172275, 6329234399, 6000000001, 6000000002
    THREAD = [grant(BRIEF_ID), grant(LIVE_ID), grant(OLD_ID, until="2026-10-02T00:00Z"),
              grant(ALIEN_ID, user={"login": "someone", "id": 1, "type": "User"}),
              {"id": 6545892934, "user": owner, "issue_url": on201, "body": "state comment"}]
    targets = {111: {"id": 111, "issue_url": on201}, 222: {"id": 222, "issue_url": on201[:-3] + "7"}}
    reads: list = []

    def fake_fetch(_repo, cid):
        return targets[cid]

    def fake_thread(_repo, issue):
        reads.append(issue)
        if isinstance(THREAD_OVERRIDE[0], Exception):
            raise THREAD_OVERRIDE[0]
        return THREAD
    THREAD_OVERRIDE: list = [None]
    FIELD = ("**Orchestrator s9: state since 6545892934 (2026-10-31, ~17:40Z)**\n\n"
             "- #3016 (R10-WOOD-NOTIFY): verdict merge at `9d304c2d`, with code-owner approval under mandate "
             "6329234399.\n- #3045 (R10-HOTFIX-CI-CRITPATH-2, red-main hotfix, critical path): blocked, "
             "metric-gamed. The body claimed dS +0.0012 IMPROVES, while the measured dS is +0.0000 NULL. The "
             "mandate raise approval at `b02ffd17` rested on that figure, so it is re-given only at the round-2 "
             "head, on the true figure. Round 2 also kills surviving mutant M6. The gate's value-blind dS check "
             "is carried to R10-FLY-MANDATE-REVOKE-GUARD.\n")

    def guarded(name, text, *extra, target=("post", "--issue", "201"), repo=None):
        """(refused, thread reads) for a dry-run post or patch of `text`."""
        reads.clear()
        f = wrote(f"seat/guard-{name}.md", text)
        hit, msg = refuses(lambda: run([target[0], "--repo", repo or g.DEFAULT_REPO, *target[1:],
                                        "--body-file", f, "--dry-run", *extra],
                                       fetch=fake_fetch, thread=fake_thread))
        return hit, len(reads), msg
    patch201, patch7 = ("patch", "--comment", "111"), ("patch", "--comment", "222")
    BRIEF = f"decision 0012 is revoked; mandate {BRIEF_ID} still binds"
    hit, _, msg = guarded("brief", BRIEF)
    check("arm6_brief_row_refused_on_post", hit and str(BRIEF_ID) in msg and "--withdraw-mandate" in msg)
    check("arm6_brief_row_refused_on_patch", guarded("brief-p", BRIEF, target=patch201)[0])
    check("arm6_withdraw_naming_the_id_posts", not guarded("wd", BRIEF, "--withdraw-mandate", str(BRIEF_ID))[0])
    check("arm6_withdraw_naming_another_id_is_refused",
          guarded("wd-other", BRIEF, "--withdraw-mandate", str(LIVE_ID))[0])
    check("arm6_word_without_a_mandate_id_posts", not guarded("noid", "decision 0012 is revoked.")[0])
    check("arm6_mandate_id_without_the_word_posts_and_reads_no_thread",
          guarded("noword", f"mandate {BRIEF_ID} still binds")[:2] == (False, 0))
    check("arm6_non_201_post_posts_and_reads_no_thread",
          guarded("i7", BRIEF, target=("post", "--issue", "7"))[:2] == (False, 0))
    check("arm6_patch_of_a_non_201_comment_posts", not guarded("p7", BRIEF, target=patch7)[0])
    check("arm6_another_repository_posts", not guarded("repo", BRIEF, repo="o/r")[0])
    check("arm6_field_text_refused_on_post", guarded("field", FIELD)[0])
    check("arm6_field_text_refused_on_patch", guarded("field-p", FIELD, target=patch201)[0])
    plain = FIELD.replace("R10-FLY-MANDATE-REVOKE-GUARD", "the mandate guard's group")
    check("arm6_field_text_without_the_word_posts (null control)", guarded("plain", plain)[:2] == (False, 0))
    check("arm6_field_text_without_the_word_patches (null control)", not guarded("plain-p", plain, target=patch201)[0])
    check("arm6_id_inside_a_longer_number_posts (the gate's whole-number test)",
          not guarded("longer", f"decision 0012 is revoked; comment 9{BRIEF_ID} is another")[0])
    check("arm6_an_expired_grant_is_not_guarded", not guarded("old", f"revoked {OLD_ID}")[0])
    check("arm6_a_grant_by_another_account_is_not_guarded", not guarded("alien", f"revoked {ALIEN_ID}")[0])
    check("arm6_a_comment_that_is_no_grant_is_not_guarded", not guarded("state", "revoked 6545892934")[0])
    THREAD_OVERRIDE[0] = Refused("gh exited 1: HTTP 502")
    check("arm6_a_thread_read_that_fails_refuses", guarded("fail", BRIEF)[0])
    THREAD_OVERRIDE[0] = None

    hit, _ = refuses(lambda: positive_int("not-a-number", "--comment"))
    check("arm4_refuses_non_integer_id", hit)

    hit, _ = refuses(lambda: positive_int("0", "--comment"))
    check("arm4_refuses_zero_id", hit)

    print(f"TOTAL: {len(failures)} failed")
    if failures:
        print("FAILED: " + ", ".join(failures), file=sys.stderr)
        return 1
    print("SELF-TEST PASSED")
    return 0


def run(argv: list[str] | None = None, fetch=fetch_comment, thread=fetch_thread) -> int:
    p = argparse.ArgumentParser(prog="gh_comment.py")
    p.add_argument("action", choices=["post", "patch", "verify", "self-test"])
    p.add_argument("--repo", help="OWNER/REPO")
    p.add_argument("--issue", help="issue or pull-request number (post)")
    p.add_argument("--comment", help="comment id (patch, verify)")
    p.add_argument("--body-file", help="path to the file holding the body")
    p.add_argument("--dry-run", action="store_true",
                   help="post/patch: stop after the refusals, write nothing")
    p.add_argument("--withdraw-mandate", metavar="CID",
                   help="post/patch to #201: the body may revoke the mandate comment CID")
    a = p.parse_args(argv)

    if a.action == "self-test":
        return self_test()

    if not a.repo:
        die(f"{a.action} needs --repo OWNER/REPO")
    if not a.body_file:
        die(f"{a.action} needs --body-file")

    body = read_body(a.body_file)
    if a.action in ("post", "patch"):
        privacy_check(body)
        if a.action == "post" and not a.issue:
            die("post needs --issue")
        if a.action == "patch" and not a.comment:
            die("patch needs --comment")
        mandate_guard(a.repo, body,
                      positive_int(a.withdraw_mandate, "--withdraw-mandate") if a.withdraw_mandate else None,
                      issue=positive_int(a.issue, "--issue") if a.action == "post" else None,
                      comment=positive_int(a.comment, "--comment") if a.action == "patch" else None,
                      fetch=fetch, thread=thread)
    print(f"OK body_file={a.body_file} chars={len(body)} sha={short_sha(body)}")

    if a.action == "verify":
        if not a.comment:
            die("verify needs --comment")
        return readback(a.repo, positive_int(a.comment, "--comment"), body)

    if a.dry_run:
        print("DRY RUN: refusals passed, nothing written")
        return 0

    if a.action == "post":
        if not a.issue:
            die("post needs --issue")
        obj = write(a.repo, f"issues/{positive_int(a.issue, '--issue')}/comments",
                    "POST", body)
    else:
        if not a.comment:
            die("patch needs --comment")
        obj = write(a.repo, f"issues/comments/{positive_int(a.comment, '--comment')}",
                    "PATCH", body)

    print(f"WROTE id={obj['id']} url={obj.get('html_url', '?')}")
    return readback(a.repo, int(obj["id"]), body)


def main() -> int:
    try:
        return run()
    except Refused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
