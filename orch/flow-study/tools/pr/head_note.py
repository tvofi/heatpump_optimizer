#!/usr/bin/env python3
"""Prefix a note under a pull-request body's `## Head` heading.

    python3 tools/pr/head_note.py <body-file> <note>      # rewrites the file in place
    python3 tools/pr/head_note.py --self-test

`## Head` is the HEADING LINE `checkPrBody` reads (`sections()` in
tools/policy/policy_lint.mjs: a line `##`, whitespace, the title, outside a
code fence) -- never the first substring `## Head`. A body whose prose quotes
`` `## Head` `` above the heading took both of #2400's recarry notes into its
preamble (`app_push.sh --recarry`, `s.index('## Head')`): the section named
neither new head, and pr-contract refused edc4484 and fd0f5d9 alike. The note
goes after the heading and any blank lines under it, then a blank line, so
each later note lands above the earlier ones. No `## Head` heading exits 1
with the file untouched.
"""
import sys


def head_offset(body: str) -> int:
    """Offset of the first line of the `## Head` section's content (past its
    blank lines), or -1 when the body has no `## Head` heading."""
    pos, fence = 0, False
    lines = body.split("\n")
    for n, line in enumerate(lines):
        nxt = pos + len(line) + 1
        if line.lstrip().startswith(("```", "~~~")):
            fence = not fence
        elif not fence and line[:2] == "##" and line[2:3].isspace() and line[2:].strip() == "Head":
            i = n + 1
            while i < len(lines) and not lines[i].strip():
                nxt += len(lines[i]) + 1
                i += 1
            return min(nxt, len(body))
        pos = nxt
    return -1


def prefix(body: str, note: str) -> str:
    i = head_offset(body)
    if i < 0:
        raise ValueError("no `## Head` heading")
    if i == len(body) and not body.endswith("\n"):
        body, i = body + "\n\n", i + 2
    return body[:i] + note.strip("\n") + "\n\n" + body[i:]


def self_test() -> int:
    fails = n = 0

    def st(got, want, what):
        nonlocal fails, n
        ok = got == want
        n += 1
        fails += not ok
        print(("ok   " if ok else "FAIL ") + what + ("" if ok else " (got %r, want %r)" % (got, want)))

    quoted = "Intro: update_pr words the `## Head` note.\n\n## Head\n\n`a0`\n\n## Figures\n\nf\n"
    st(prefix(quoted, "N1"), "Intro: update_pr words the `## Head` note.\n\n## Head\n\nN1\n\n`a0`\n\n## Figures\n\nf\n",
       "prose quoting `## Head` above the heading: the note lands under the heading, not in the prose")
    st(prefix(prefix(quoted, "N1"), "N2").split("## Head\n\n")[1].split("\n\n")[:3], ["N2", "N1", "`a0`"],
       "two notes: the later one above the earlier, both under the heading")
    st(prefix("x\n```\n## Head\n```\n## Head\n\nh\n", "N"), "x\n```\n## Head\n```\n## Head\n\nN\n\nh\n",
       "a `## Head` line inside a code fence is not the heading")
    st(prefix("### Head\n\n## Heading\n\n##  Head  \r\n\r\nh\n", "N"), "### Head\n\n## Heading\n\n##  Head  \r\n\r\nN\n\nh\n",
       "`### Head` and `## Heading` are not it; `##  Head  ` with CRLF is (sections()'s \\s)")
    st(prefix("## Head", "N"), "## Head\n\nN\n\n", "a heading at the end of the body with no newline")
    try:
        prefix("`## Head` only in prose\n", "N")
        st("no raise", "ValueError", "no heading refuses")
    except ValueError:
        st("ValueError", "ValueError", "no heading refuses")
    print("head_note self-test: %d checks, %d failed" % (n, fails))
    return 1 if fails else 0


def main(argv: list) -> int:
    if argv[1:] == ["--self-test"]:
        return self_test()
    if len(argv) != 3:
        print("usage: head_note.py <body-file> <note> | --self-test", file=sys.stderr)
        return 2
    with open(argv[1], newline="") as f:
        body = f.read()
    try:
        out = prefix(body, argv[2])
    except ValueError as e:
        print("head_note: REFUSE: %s: %s" % (argv[1], e), file=sys.stderr)
        return 1
    with open(argv[1], "w", newline="") as f:
        f.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
