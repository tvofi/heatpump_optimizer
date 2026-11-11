#!/usr/bin/env python3
"""Say whether a session owes a policy re-read: OK, or OWED.

    python3 -I tools/audit/seat/policy_reread_check.py --transcript <session.jsonl> --stamp <file>
    python3 -I tools/audit/seat/policy_reread_check.py --stamp <file> --write-stamp
    python3 -I tools/audit/seat/policy_reread_check.py --self-test

WHY THIS EXISTS. A compaction replaces the session's copy of CLAUDE.md, the
rules and the role contracts with a summary of them. The sweep's first step
(`tools/audit/seat/sweep_template.md`) re-reads the corpus from fresh
origin/main after each one, and this is the predicate that says whether that is
owed. Round 10 kept it as a session-local shell script under the orchestration
scratch; decision 0013 puts an instrument the programme runs in the tree.

THE RULE. OK when the stamp is strictly later than the newest compaction in
the transcript; otherwise OWED. A compaction is a JSON line of the transcript
whose `subtype` is `compact_boundary`, timed by its `timestamp`. The stamp file
holds one ISO-8601 UTC instant, the moment the re-read finished, written by
`--write-stamp` so its format is this file's own.

FAIL CLOSED. Each shape below prints OWED, never OK, because OK is the answer
that skips the re-read:
  - no stamp file, an empty one, or one that does not parse;
  - a stamp later than this host's clock (an age computed from a stamp ahead of
    the reading clock is unknowable, fixer.md step 16);
  - a transcript that cannot be read;
  - a line naming `compact_boundary` that is not JSON (a compaction whose time
    cannot be read is not evidence there was none) or whose timestamp does not
    parse.
A transcript with no compaction and a valid stamp is OK: nothing has replaced
the corpus the session loaded.

Matching is on the parsed `subtype` field, never on the text: a tool result
that quotes the string `compact_boundary` is JSON-escaped inside its line and
is not a compaction. Exit 0 on OK, 1 on OWED, 2 on a usage error.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

MARKER = "compact_boundary"


def parse_instant(text: str) -> datetime | None:
    """One ISO-8601 instant with a zone, as an aware UTC datetime; None if it does not parse."""
    t = text.strip()
    if t.endswith("Z"):
        t = t[:-1] + "+00:00"
    try:
        d = datetime.fromisoformat(t)
    except ValueError:
        return None
    if d.tzinfo is None:
        return None
    return d.astimezone(timezone.utc)


def last_compaction(transcript: Path) -> tuple[datetime | None, str | None]:
    """(newest compaction instant or None, refusal reason or None)."""
    try:
        lines = transcript.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as e:
        return None, f"transcript unreadable: {e.__class__.__name__}"
    newest = None
    for n, line in enumerate(lines, 1):
        if MARKER not in line:
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            return None, f"transcript line {n} names {MARKER} and is not JSON"
        if not isinstance(obj, dict) or obj.get("subtype") != MARKER:
            continue
        at = parse_instant(str(obj.get("timestamp", "")))
        if at is None:
            return None, f"transcript line {n} is a compaction with no readable timestamp"
        if newest is None or at > newest:
            newest = at
    return newest, None


def verdict(transcript: Path, stamp: Path, now: datetime | None = None) -> tuple[bool, str]:
    """(ok, line). The line starts with OK or OWED."""
    now = now or datetime.now(timezone.utc)
    last, why = last_compaction(transcript)
    if why:
        return False, f"OWED ({why})"
    shown = last.isoformat(timespec="milliseconds").replace("+00:00", "Z") if last else "none"
    try:
        raw = stamp.read_text(encoding="utf-8")
    except OSError:
        return False, f"OWED (no stamp; last compaction {shown})"
    read_at = parse_instant(raw)
    if read_at is None:
        return False, f"OWED (stamp does not parse; last compaction {shown})"
    if read_at > now:
        return False, f"OWED (stamp {raw.strip()} is ahead of this clock; its age is unknowable)"
    if last is None:
        return True, f"OK (read {raw.strip()}; no compaction in the transcript)"
    if read_at > last:
        return True, f"OK (read {raw.strip()} > compaction {shown})"
    return False, f"OWED (read {raw.strip()} <= compaction {shown})"


def write_stamp(stamp: Path, now: datetime | None = None) -> str:
    at = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    stamp.parent.mkdir(parents=True, exist_ok=True)
    stamp.write_text(at + "\n", encoding="utf-8")
    return at


def self_test() -> int:
    passed = failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + cond, failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    def boundary(ts: str) -> str:
        return json.dumps({"type": "system", "subtype": MARKER, "content": "Conversation compacted", "timestamp": ts})

    now = parse_instant("2026-10-18T16:00:00Z")
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        tr, st = root / "t.jsonl", root / "s.stamp"

        def run(lines, stamp_text):
            tr.write_text("\n".join(lines) + "\n", encoding="utf-8")
            if stamp_text is None:
                st.unlink(missing_ok=True)
            else:
                st.write_text(stamp_text, encoding="utf-8")
            return verdict(tr, st, now)

        msg = json.dumps({"type": "user", "message": {"content": "hello"}, "timestamp": "2026-10-18T15:00:00Z"})
        two = [msg, boundary("2026-10-18T14:00:00.100Z"), msg, boundary("2026-10-18T15:23:48.517Z")]
        ok, line = run(two, "2026-10-18T15:46:25Z\n")
        check("a stamp after the newest compaction is OK", ok and line.startswith("OK "))
        ok, line = run(two, "2026-10-18T15:00:00Z\n")
        check("a stamp between two compactions is OWED: the newest one binds (null control for OK)",
              not ok and line.startswith("OWED "))
        ok, _ = run(two, "2026-10-18T15:23:48Z\n")
        check("a stamp in the same second but before the compaction's fraction is OWED", not ok)
        ok, _ = run(two, None)
        check("no stamp is OWED", not ok)
        ok, _ = run(two, "")
        check("an empty stamp is OWED", not ok)
        ok, _ = run(two, "yesterday\n")
        check("an unparseable stamp is OWED", not ok)
        ok, _ = run(two, "2026-10-18T15:46:25\n")
        check("a stamp with no zone is OWED", not ok)
        ok, _ = run(two, "2026-10-18T17:00:00Z\n")
        check("a stamp ahead of the clock is OWED", not ok)
        ok, line = run([msg], "2026-10-18T15:46:25Z\n")
        check("no compaction and a valid stamp is OK", ok and line.startswith("OK "))
        ok, _ = run([msg], None)
        check("no compaction and no stamp is OWED", not ok)
        quoted = json.dumps({"type": "user", "message": {"content": '{"subtype":"compact_boundary","timestamp":"2026-10-18T15:59:00Z"}'}})
        ok, _ = run(two + [quoted], "2026-10-18T15:46:25Z\n")
        check("a quoted compact_boundary inside a message is not a compaction", ok)
        ok, line = run(two + ['{"subtype":"compact_boundary", truncated'], "2026-10-18T15:46:25Z\n")
        check("a non-JSON line naming compact_boundary is OWED", not ok and "not JSON" in line)
        ok, _ = run([boundary("not a time")], "2026-10-18T15:46:25Z\n")
        check("a compaction with an unreadable timestamp is OWED", not ok)
        ok, line = verdict(root / "absent.jsonl", st, now)
        check("an unreadable transcript is OWED", not ok and "unreadable" in line)
        tr.write_text("\n".join(two) + "\n", encoding="utf-8")
        at = write_stamp(root / "sub" / "w.stamp", now - timedelta(minutes=1))
        ok, _ = verdict(tr, root / "sub" / "w.stamp", now)
        check("--write-stamp writes a stamp this check reads as OK", ok and at == "2026-10-18T15:59:00Z")
    print(f"policy_reread_check self-test: {passed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--transcript", type=Path, help="the session transcript (.jsonl)")
    ap.add_argument("--stamp", type=Path, help="the policy re-read stamp file")
    ap.add_argument("--write-stamp", action="store_true", help="record that the re-read finished now")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.stamp is None:
        ap.error("--stamp is required")
    if a.write_stamp:
        print(f"STAMPED {write_stamp(a.stamp)}")
        return 0
    if a.transcript is None:
        ap.error("--transcript is required")
    ok, line = verdict(a.transcript, a.stamp)
    print(line)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
