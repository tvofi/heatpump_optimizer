#!/usr/bin/env python3
"""token_ledger.py -- decision 0018's token ledger: usage per seat, every field apart.

    python3 -I tools/audit/seat/token_ledger.py header --role R [--group G] [--model M] [--dimension D] [--seat S]
    python3 -I tools/audit/seat/token_ledger.py collect --projects DIR [--projects DIR ...] --out FILE
                                                        [--seat-class cloud]
    python3 -I tools/audit/seat/token_ledger.py summary --ledger FILE [--since ISO] [--until ISO]
    python3 -I tools/audit/seat/token_ledger.py --self-test

WHY (owner ruling 2026-11-13, card P4; the round-10 process convergence audit
d5d7ff81, section 1 T and section 6 row a4; decision 0018 section 2,
`tokens_per_change`): no record of token use existed, so T could not be a
controlled variable.

THE KEY. Every dispatch writes one line `Seat key: group=G role=R dimension=D
model=M seat=S` (`header`; `-` for a field that does not apply) into the seat's
first message, at a line's start or after a space: `cloud_dispatch.py` ends the
first line of every prompt with it. `collect` reads it from the first user
message of each transcript.

THE SOURCE. A Claude project directory holds `<session>.jsonl` (the session's
own transcript) and `<session>/subagents/agent-<id>.jsonl` (each spawned seat's);
`sessions()` yields both per session, importable by any reader. Every assistant
line carries `message.usage`; one API response is written once per content
block, so usage is counted once per (message id, request id) over the whole
session. The four fields are kept apart (FIELDS); `tokens` is their sum.

THE CLASS (round_metrics.SEAT_CLASSES): a session's own transcript with no seat
key is the orchestrator's; with one, a local seat run as its own session; every
subagent transcript is a local seat. `--seat-class cloud` labels every row cloud:
a cloud seat's transcript lives only in its own container (measured: the seat
reads it at `~/.claude/projects/<cwd slug>/$CLAUDE_CODE_SESSION_ID.jsonl`), and
no tracked path brings it to the host this job runs on, so the cloud class has
no row and round_metrics' `tokens` line prints unread, never a partial.

THE LEDGER `--out` (the beat's `<state>/scorecard/tokens.tsv`, round_metrics'
input): one row per (session, agent, UTC day), columns COLUMNS, `t` the day's
last usage stamp. A pass replaces the rows of every transcript it read and keeps
the rest, so a transcript the client has since pruned keeps its rows.
"""
from __future__ import annotations

import argparse
import collections
import csv
import importlib.util
import io
import json
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIELDS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
KEYS = ("group", "role", "dimension", "model", "seat")
COLUMNS = ("t", "seat_class", "tokens", *FIELDS, "session", "agent", *KEYS)
HEADER = re.compile(r"(?:^|(?<= ))Seat key: (.*)$", re.M)
VALUE = re.compile(r"[A-Za-z0-9._/@+-]+")


class Refusal(Exception):
    pass


def header(**kw: str) -> str:
    """The seat-key line; a value outside VALUE (a space, an `=`) would split the key, so it refuses."""
    if set(kw) - set(KEYS):
        raise Refusal(f"unknown key {sorted(set(kw) - set(KEYS))}")
    vals = {k: (kw.get(k) or "-") for k in KEYS}
    bad = [k for k, v in vals.items() if not VALUE.fullmatch(v)]
    if bad or vals["role"] == "-":
        raise Refusal(f"seat key {', '.join(bad) or 'role'} is empty or not one token: {vals}")
    return "Seat key: " + " ".join(f"{k}={vals[k]}" for k in KEYS)


def parse_header(text: str) -> dict | None:
    m = HEADER.search(text or "")
    if not m:
        return None
    got = dict(p.split("=", 1) for p in m.group(1).split() if "=" in p)
    return {k: got.get(k, "-") for k in KEYS}


def sessions(project: Path):
    """(session id, its own transcript, [its subagent transcripts]) per session of one project dir."""
    for main in sorted(Path(project).glob("*.jsonl")):
        yield main.stem, main, sorted((main.parent / main.stem / "subagents").glob("*.jsonl"))


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content or [] if isinstance(b, dict))


def read_transcript(path: Path, seen: set) -> tuple[dict | None, dict]:
    """(the seat key of its first user message, {day: {field: n, "t": last stamp, "model": m}})."""
    key, first, days = None, True, {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            try:
                o = json.loads(ln)
            except ValueError:
                continue
            m = o.get("message") if isinstance(o, dict) else None
            if not isinstance(m, dict):
                continue
            if first and o.get("type") == "user":
                first, key = False, parse_header(_text(m.get("content")))
            u = m.get("usage")
            stamp = str(o.get("timestamp") or "")
            if not isinstance(u, dict) or len(stamp) < 10:
                continue
            ident = (m.get("id"), o.get("requestId"))
            if ident in seen and ident != (None, None):
                continue
            seen.add(ident)
            d = days.setdefault(stamp[:10], dict.fromkeys(FIELDS, 0) | {"t": "", "model": "-"})
            for k in FIELDS:
                d[k] += int(u.get(k) or 0)
            d["t"] = max(d["t"], stamp)
            d["model"] = m.get("model") or d["model"]
    return key, days


def rows_of(project: Path, seat_class: str | None = None) -> list[dict]:
    rows = []
    for sid, main, subs in sessions(project):
        seen: set = set()
        for path in [main, *subs]:
            key, days = read_transcript(path, seen)
            own = path == main
            cls = seat_class or ("local" if not own or key else "orchestrator")
            if key is None:
                key = dict.fromkeys(KEYS, "-") | ({"role": "orchestrator"} if cls == "orchestrator" else {})
            for day in sorted(days):
                d = days[day]
                rows.append({"t": d["t"], "seat_class": cls, "tokens": sum(d[k] for k in FIELDS),
                             **{k: d[k] for k in FIELDS}, "session": sid,
                             "agent": "-" if own else path.stem.removeprefix("agent-"),
                             **key, "model": key["model"] if key["model"] != "-" else d["model"]})
    return rows


def read_ledger(path: Path) -> list[dict]:
    try:
        return list(csv.DictReader(io.StringIO(Path(path).read_text()), delimiter="\t"))
    except OSError:
        return []


def collect(projects: list[Path], out: Path, seat_class: str | None = None) -> tuple[int, int]:
    """Rewrite `out`: the rows of every transcript read now, plus kept rows of transcripts not read.
    Returns (rows written, transcripts read)."""
    fresh = [r for p in projects for r in rows_of(p, seat_class)]
    read = {(sid, "-" if path == main else path.stem.removeprefix("agent-"))
            for p in projects for sid, main, subs in sessions(p) for path in [main, *subs]}
    kept = [r for r in read_ledger(out) if (r.get("session"), r.get("agent")) not in read]
    rows = sorted(kept + fresh, key=lambda r: (r["t"], r["session"], r["agent"]))
    buf = io.StringIO()
    w = csv.DictWriter(buf, COLUMNS, delimiter="\t", extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=out.parent, prefix=".tokens.")
    with os.fdopen(fd, "w") as f:
        f.write(buf.getvalue())
    os.replace(tmp, out)
    return len(rows), len(read)


def summary(rows: list[dict], since: str = "", until: str = "") -> list[str]:
    """Per seat class and role, each field apart and the total, over rows with since <= t < until."""
    acc: dict = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        if since <= r["t"] and (not until or r["t"] < until):
            acc[(r["seat_class"], r["role"])].update({k: int(r[k]) for k in (*FIELDS, "tokens")})
    return [f"{c}\t{role}\t" + "\t".join(f"{k}={n[k]}" for k in (*FIELDS, "tokens"))
            for (c, role), n in sorted(acc.items())]


# ---------------------------------------------------------------- self-test

def _line(kind: str, mid: str, req: str, t: str, usage: dict | None = None, text: str = "") -> str:
    msg = {"role": kind, "content": text} if kind == "user" else {"id": mid, "model": "m-x", "usage": usage}
    return json.dumps({"type": kind, "requestId": req, "timestamp": t, "message": msg}) + "\n"


def self_test() -> int:
    passed = failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + bool(cond), failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    u = {"input_tokens": 1, "output_tokens": 10, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 1000}
    key = header(group="G-1", role="fixer", model="opus", seat="fixer-g-1")
    check("header renders every key, `-` where unset",
          key == "Seat key: group=G-1 role=fixer dimension=- model=opus seat=fixer-g-1")
    check("parse_header reads it back from inside a longer message",
          parse_header("CLOUD FIXER seat.\n" + key + "\nmore") == parse_header("CLOUD FIXER seat. " + key) ==
          {"group": "G-1", "role": "fixer", "dimension": "-", "model": "opus", "seat": "fixer-g-1"})
    check("no seat key, or one glued to a word, parses as None (null control)",
          parse_header("CLOUD FIXER seat.") is None and parse_header("xSeat key: role=r") is None)

    def refuses(**kw) -> bool:
        try:
            header(**kw)
        except Refusal:
            return True
        return False
    check("a value with a space, an `=`, an empty role or an unknown key refuses; a plain one does not",
          refuses(role="fix er") and refuses(role="fixer", group="a=b") and refuses(group="G")
          and refuses(role="x", colour="red") and not refuses(role="x"))

    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp) / "proj"
        (proj / "s1" / "subagents").mkdir(parents=True)
        (proj / "s1.jsonl").write_text(
            _line("user", "", "", "2026-11-01T00:00:00Z", text="hello")
            + _line("assistant", "m1", "r1", "2026-11-01T01:00:00Z", u)
            + _line("assistant", "m1", "r1", "2026-11-01T01:00:01Z", u)  # a second content block of m1
            + _line("assistant", "m2", "r2", "2026-11-02T01:00:00Z", u) + "not json\n")
        (proj / "s1" / "subagents" / "agent-a1.jsonl").write_text(
            _line("user", "", "", "2026-11-01T02:00:00Z", text=key + "\nbrief")
            + _line("assistant", "m3", "r3", "2026-11-01T02:00:00Z", u))
        (proj / "s1" / "subagents" / "agent-a2.jsonl").write_text(
            _line("user", "", "", "2026-11-01T03:00:00Z", text="no key")
            + _line("assistant", "m4", "r4", "2026-11-01T03:00:00Z", u))
        got = list(sessions(proj))
        check("sessions() yields the session's own transcript and each subagent transcript",
              [(s, m.name, [p.name for p in subs]) for s, m, subs in got]
              == [("s1", "s1.jsonl", ["agent-a1.jsonl", "agent-a2.jsonl"])])
        out = Path(tmp) / "state" / "scorecard" / "tokens.tsv"
        n, read = collect([proj], out)
        rows = read_ledger(out)
        by = {(r["agent"], r["t"][:10]): r for r in rows}
        check("one row per transcript and day: 2 orchestrator days, 2 subagents", n == 4 and read == 3)
        o1 = by[("-", "2026-11-01")]
        check("a response written once per content block counts once (m1 twice is 1111, not 2222)",
              o1["tokens"] == "1111")
        check("every usage field is kept apart and `tokens` is their sum",
              [o1[k] for k in FIELDS] == ["1", "10", "100", "1000"])
        check("a session's own transcript with no key is the orchestrator's",
              o1["seat_class"] == "orchestrator" and o1["role"] == "orchestrator")
        a1, a2 = by[("a1", "2026-11-01")], by[("a2", "2026-11-01")]
        check("a keyed subagent is a local seat keyed by group, role, dimension, model and seat",
              (a1["seat_class"], a1["group"], a1["role"], a1["dimension"], a1["model"], a1["seat"])
              == ("local", "G-1", "fixer", "-", "opus", "fixer-g-1"))
        check("an unkeyed subagent is still a local seat, its model read from the response",
              (a2["seat_class"], a2["group"], a2["role"], a2["model"]) == ("local", "-", "-", "m-x"))
        (proj / "s1" / "subagents" / "agent-a2.jsonl").unlink()
        collect([proj], out)
        check("a transcript pruned since keeps its rows; the rest are replaced, not appended",
              len(read_ledger(out)) == 4)
        n2, _ = collect([proj], Path(tmp) / "cloud.tsv", seat_class="cloud")
        check("--seat-class cloud labels every row cloud",
              {r["seat_class"] for r in read_ledger(Path(tmp) / "cloud.tsv")} == {"cloud"} and n2 == 3)
        check("summary keeps each field apart per seat class and role",
              "local\tfixer\tinput_tokens=1\toutput_tokens=10\tcache_creation_input_tokens=100"
              "\tcache_read_input_tokens=1000\ttokens=1111" in summary(rows))
        # the reader this ledger feeds: round_metrics.token_line, unchanged
        spec = importlib.util.spec_from_file_location("round_metrics", HERE / "round_metrics.py")
        rm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rm)
        merges = [{"class": "production", "ct": rm.epoch("2026-11-01T12:00:00Z")}]
        a, b = rm.epoch("2026-11-01T00:00:00Z"), rm.epoch("2026-11-03T00:00:00Z")
        line = rm.token_line(out.parent, merges, a, b)
        check("round_metrics reads the ledger and prints unread while the cloud class has no row",
              "seat classes with no ledger row: cloud;" in line)
        with open(out, "a") as f:
            f.write("2026-11-01T05:00:00Z\tcloud\t5\n")
        check("one cloud row makes it read, summing `tokens` (null control for the unread arm)",
              rm.token_line(out.parent, merges, a, b).startswith("tokens 4449 per production merge"))
    print(f"token_ledger self-test: {passed} passed, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    ap = argparse.ArgumentParser(prog="token_ledger.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("header")
    for k in KEYS:
        h.add_argument(f"--{k}", default="")
    c = sub.add_parser("collect")
    c.add_argument("--projects", action="append", required=True, type=Path)
    c.add_argument("--out", required=True, type=Path)
    c.add_argument("--seat-class", choices=("cloud",))
    s = sub.add_parser("summary")
    s.add_argument("--ledger", required=True, type=Path)
    s.add_argument("--since", default="")
    s.add_argument("--until", default="")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "header":
            print(header(**{k: getattr(a, k) for k in KEYS}))
        elif a.cmd == "collect":
            missing = [str(p) for p in a.projects if not p.is_dir()]
            if missing:
                raise Refusal(f"no project directory: {', '.join(missing)}")
            n, read = collect(a.projects, a.out, a.seat_class)
            print(f"token_ledger: {n} rows from {read} transcripts into {a.out}")
        else:
            print("\n".join(summary(read_ledger(a.ledger), a.since, a.until)))
    except Refusal as e:
        print(f"token_ledger: refused: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
