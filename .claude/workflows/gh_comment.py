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
"""
from __future__ import annotations

import argparse
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


def read_body(path: str) -> str:
    """Read the body file, or refuse. Never returns a body it cannot vouch for."""
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


def fetch_comment(repo: str, cid: int) -> dict:
    out = gh(["api", f"/repos/{repo}/issues/comments/{cid}"])
    try:
        obj = json.loads(out)
    except ValueError as exc:
        die(f"read-back returned output that is not JSON: {exc}")
    if not isinstance(obj, dict):
        die("read-back returned a non-object; read-back could not be performed")
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
    "Closes #541.",
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


def run(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="gh_comment.py")
    p.add_argument("action", choices=["post", "patch", "verify", "self-test"])
    p.add_argument("--repo", help="OWNER/REPO")
    p.add_argument("--issue", help="issue or pull-request number (post)")
    p.add_argument("--comment", help="comment id (patch, verify)")
    p.add_argument("--body-file", help="path to the file holding the body")
    p.add_argument("--dry-run", action="store_true",
                   help="post/patch: stop after the refusals, write nothing")
    a = p.parse_args(argv)

    if a.action == "self-test":
        return self_test()

    if not a.repo:
        die(f"{a.action} needs --repo OWNER/REPO")
    if not a.body_file:
        die(f"{a.action} needs --body-file")

    body = read_body(a.body_file)
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
