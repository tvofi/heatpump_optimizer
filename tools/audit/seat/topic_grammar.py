#!/usr/bin/env python3
"""The topic grammar: one owner for how a topic joins dispatch, return, PR and roster records.

    python3 tools/audit/seat/topic_grammar.py pr-topic <head>
    python3 tools/audit/seat/topic_grammar.py family-refs <topic> <kind>[,<kind>...] < ls-remote-text
    python3 tools/audit/seat/topic_grammar.py --self-test

The topic is the join key between the dispatch ref (`dispatch/fixer-<topic>`), the return refs
(`handoff/`, `handoff-wip/`, `handoff-body/<topic>`), the PR head (`fix/<topic>[-pr]`) and the roster
group. A split adds `-p<N>` partway through the work, so a join keyed on the exact string misses
(dev/audit/rca/topic-family.md). The rules:

  pr_topic    a PR head less `fix/` and one trailing `-pr`.
  family      the topic less one trailing `-p<N>` is the base; the family is the base plus every
              `<base>-p<N>`. A bare `-<N>` is never a member: R10-ROSTER-OPS-2, R10-STALE-PATHS-2
              and R10-TICK-DRIVERS-2 are distinct groups.
  family_refs the listed `refs/heads/<kind>/<member>` refs whose member FULL-matches the family,
              never by prefix (`r10-deeplink-census` is not `r10-deeplink`'s).
  group_of    the roster group of a topic: exact, then one `-p<N>`, then one `-<N>` off, behind a
              body check (moved unchanged from open_driver.resolve).
  owner_topic the group(s) a head answers for: the longest matching topic's alone (moved
              unchanged from roster_sync.matches).

`family-refs` prints `<sha> <ref>` per match, for the bash callers.
"""
from __future__ import annotations

import re
import sys

PART = re.compile(r"(.+)-p\d+")


def pr_topic(head: str) -> str:
    t = head[len("fix/"):] if head.startswith("fix/") else head
    return t[:-len("-pr")] if t.endswith("-pr") else t


def base(topic: str) -> str:
    m = PART.fullmatch(topic)
    return m.group(1) if m else topic


def family(topic: str) -> "re.Pattern[str]":
    """The pattern a family member's name fully matches: the base, or `<base>-p<N>`."""
    return re.compile(re.escape(base(topic)) + r"(?:-p\d+)?")


def family_refs(topic: str, ls_remote_text: str, kinds) -> "list[tuple[str, str]]":
    """[(sha, ref)] of the `refs/heads/<kind>/<member>` lines whose member is in the family."""
    fam, out = family(topic), []
    for line in ls_remote_text.splitlines():
        f = line.split()
        if len(f) != 2:
            continue
        for k in kinds:
            pre = f"refs/heads/{k}/"
            if f[1].startswith(pre) and fam.fullmatch(f[1][len(pre):]):  # mut:tgprefix
                out.append((f[0], f[1]))
    return out


def names_group(body_head: str, group: str) -> bool:
    """`group` appears as a whole name in the text: not inside a longer one."""
    return re.search(r"(?<![A-Za-z0-9_-])%s(?![A-Za-z0-9_-])" % re.escape(group), body_head, re.I) is not None


def group_of(topic: str, groups, body_head: str, titles: "dict | None" = None) -> tuple:
    """(group, title) or (None, why). `groups` are the roster's group ids."""
    words = topic.replace("-", " ")
    t = (titles or {}).get(topic)
    if isinstance(t, dict) and t.get("group") and t.get("title"):
        return t["group"], t["title"]
    m = re.fullmatch(r"triage-s(\d+)-batch(\d+)", topic)
    if m:
        for g in (f"R10-TRIAGE-S{m.group(1)}", f"R10-TRIAGE-B{m.group(2)}"):
            if g in groups:
                return g, f"{g}: {words}"
        return None, "NEEDS-TITLE"
    up = topic.upper()
    if up in groups:  # exact match always wins
        return up, f"{up}: {words}"
    for rx in (r"-p(\d+)", r"-(\d+)"):  # (ii) one trailing -p<N>, then (iii) one trailing -<N>
        m = re.fullmatch(r"(.+)" + rx, topic)
        if m and m.group(1).upper() in groups and names_group(body_head, m.group(1).upper()):
            g = m.group(1).upper()
            return g, f"{g} (part {m.group(2)}): {words}"
    return None, "NEEDS-TITLE"


def owner_topic(name: str, topics: dict) -> list:
    """The group ids (`topics`: id -> topic) a normalized head answers for: the longest
    matching topic's alone, so `r10-stale-paths-2` is never also R10-STALE-PATHS's."""
    hits = [(len(t), gid) for gid, t in topics.items() if t and (name == t or name.startswith(t + "-"))]
    if not hits:
        return []
    longest = max(n for n, _ in hits)
    return [gid for n, gid in hits if n == longest]


def self_test() -> int:
    bad = 0

    def ck(name, cond):
        nonlocal bad
        print(("  ok   " if cond else "  FAIL ") + name)
        bad += not cond

    ck("pr_topic strips fix/ and one -pr", [pr_topic(h) for h in ("fix/a-p1-pr", "fix/a", "a-pr-pr", "handoff/x")]
       == ["a-p1", "a", "a-pr", "handoff/x"])
    ck("the base drops one trailing -p<N> only", [base(t) for t in ("a-p2", "a", "a-p1-p2", "r10-roster-ops-2")]
       == ["a", "a", "a-p1", "r10-roster-ops-2"])
    ls = "\n".join(f"{c * 40}\trefs/heads/{r}" for c, r in (
        ("1", "handoff/r10-agreement-bootstrap-p1"), ("2", "handoff-wip/r10-roster-ops-2"),
        ("3", "handoff/r10-deeplink-census"), ("4", "handoff-body/r10-agreement-bootstrap"),
        ("5", "handoff/r10-agreement-bootstrap-p2x"), ("6", "fix/r10-agreement-bootstrap-p3")))
    refs = lambda t, k=("handoff", "handoff-wip", "handoff-body"): [r.removeprefix("refs/heads/") for _, r in family_refs(t, ls, k)]
    ck("a part ref belongs to its base's family", refs("r10-agreement-bootstrap")
       == ["handoff/r10-agreement-bootstrap-p1", "handoff-body/r10-agreement-bootstrap"])
    ck("a part topic reaches the base and its siblings", refs("r10-agreement-bootstrap-p2")
       == ["handoff/r10-agreement-bootstrap-p1", "handoff-body/r10-agreement-bootstrap"])
    ck("a bare -<N> is not a family member", refs("r10-roster-ops") == [])  # mut:tgbare
    ck("a sibling topic is not matched by prefix", refs("r10-deeplink") == [])
    ck("only the asked kinds are listed", refs("r10-agreement-bootstrap", ("handoff-body",))
       == ["handoff-body/r10-agreement-bootstrap"])
    ck("a malformed line is skipped", family_refs("a", "junk\n", ("handoff",)) == [])
    groups = {"R10-A", "R10-A-2", "R10-TRIAGE-S6"}
    ck("group_of: exact, part, bare number behind a body check, triage, none",
       group_of("r10-a", groups, "")[0] == "R10-A" and group_of("r10-a-p3", groups, "R10-A x")[0] == "R10-A"
       and group_of("r10-a-p3", groups, "")[0] is None and group_of("triage-s6-batch1", groups, "")[0] == "R10-TRIAGE-S6"
       and group_of("r10-a-2", groups, "R10-A-2")[0] == "R10-A-2" and group_of("zzz", groups, "")[0] is None)
    ck("owner_topic: the longest topic wins, shared topics share, none is empty",
       owner_topic("r10-stale-paths-2", {"A": "r10-stale-paths", "B": "r10-stale-paths-2"}) == ["B"]
       and owner_topic("x", {"A": "x", "B": "x"}) == ["A", "B"] and owner_topic("y", {"A": "x"}) == [])
    print(f"topic_grammar self-test: {bad and 'FAILED' or 'ok'}")
    return 1 if bad else 0


def main(argv) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if len(argv) == 2 and argv[0] == "pr-topic":
        print(pr_topic(argv[1]))
        return 0
    if len(argv) == 3 and argv[0] == "family-refs":
        for sha, ref in family_refs(argv[1], sys.stdin.read(), argv[2].split(",")):
            print(sha, ref)
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
