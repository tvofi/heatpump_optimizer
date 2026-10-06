#!/usr/bin/env python3
"""Replay every Delivery-status row conflict under one file per pull request.

The harness behind the root cause on #201 (comment 5704098870) and the pull
request that built its countermeasure. Read-only: it writes nothing to the tree.

For every pull request merged on `main` since merge commits began (2026-09-14),
and for any extra branch heads named on the command line, it finds each merge of
`main` into the branch and asks `git merge-tree --write-tree` whether that merge
conflicted in the plan of record. Each such conflict is then replayed twice with
`git merge-file` on the plan's three versions (merge base, branch, main):

  as-is   the file as it was -- the null control; it must conflict every time.
  files   a row whose identity is absent at the merge base leaves the plan for
          `docs/delivery/<N>.md`, keyed by the pull request that added it; a row
          re-truthed in place stays in the table. Conflicting means the plan
          still conflicts, or both sides wrote the same row file differently.

    python3 tools/audit/record-predicate/row_files_replay.py [branch-ref ...]
"""
import re
import subprocess
import sys
import tempfile

PLAN = "docs/plan-2026-09-open-issues.md"
SINCE = "2026-09-14"


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True)


def out(*args):
    return git(*args).stdout.strip()


FIRST_PARENT = set(out("rev-list", "--first-parent", "origin/main").split())


def row_lines(lines):
    """Indices of the two seams: the section's first-table rows, and every
    `- [#N]` item in `## Delivery status`."""
    idx, sec, sub = [], None, None
    for i, line in enumerate(lines):
        if line.startswith("## "):
            sec, sub = line[3:].strip(), None
        elif line.startswith("### "):
            sub = line[4:].strip()
        if sec != "Delivery status":
            continue
        if sub is None and line.startswith("|") and not re.match(r"^\|[\s|:-]+\|\s*$", line) \
                and not line.startswith("| Wave"):
            idx.append(i)
        elif line.startswith("- [#"):
            idx.append(i)
    return idx


def identity(row):
    m = re.match(r"- \[#(\d+)\]", row)
    if m:
        return "L" + m.group(1)
    return "T" + "|".join(c.strip() for c in row.strip("|").split("|")[:2])[:120]


def merge_file(ours, base, theirs):
    with tempfile.TemporaryDirectory() as d:
        for name, text in (("a", ours), ("o", base), ("b", theirs)):
            with open(f"{d}/{name}", "w") as fh:
                fh.write("\n".join(text))
        return subprocess.run(["git", "merge-file", "-p", f"{d}/a", f"{d}/o", f"{d}/b"],
                              capture_output=True, text=True).returncode


def sync_merges(label, number, tip, base):
    for s in out("rev-list", "--merges", f"{base}..{tip}").split():
        p1, p2 = out("rev-parse", f"{s}^1", f"{s}^2").split()
        if p2 in FIRST_PARENT:
            branch, main = p1, p2
        elif p1 in FIRST_PARENT:
            branch, main = p2, p1
        else:
            continue
        r = git("merge-tree", "--write-tree", "--name-only", branch, main)
        conflicted = r.stdout.split("\n\n")[0].split("\n")[1:]
        if r.returncode == 1 and PLAN in conflicted:
            yield label, number, s, branch, main


def replay(number, branch, main):
    base = out("merge-base", branch, main)
    O, A, B = (out("show", f"{c}:{PLAN}").split("\n") for c in (base, branch, main))
    known = {identity(O[i]) for i in row_lines(O)}
    introduced = {}
    for mc in reversed(out("rev-list", "--first-parent", f"{base}..{main}").split()):
        m = re.search(r"#(\d+)", out("log", "-1", "--format=%s", mc))
        for d in out("diff", f"{mc}^1", mc, "--", PLAN).split("\n"):
            if d.startswith("+") and not d.startswith("+++"):
                introduced.setdefault(d[1:], int(m.group(1)) if m else -1)

    def strip(lines, owner):
        rows, keep, files = set(row_lines(lines)), [], {}
        for i, line in enumerate(lines):
            if i in rows and identity(line) not in known:
                files.setdefault(owner(line), []).append(line)
            else:
                keep.append(line)
        return keep, files

    A2, fa = strip(A, lambda line: number)
    B2, fb = strip(B, lambda line: introduced.get(line, -1))
    collisions = [k for k in fa if k in fb and fa[k] != fb[k]]
    return merge_file(A, O, B), merge_file(A2, O, B2), sorted(fa), sorted(fb), collisions


def main():
    targets = []
    for m in out("rev-list", "--first-parent", "--merges", f"--since={SINCE}", "origin/main").split():
        n = re.search(r"#(\d+)", out("log", "-1", "--format=%s", m))
        if n:
            targets.append((f"#{n.group(1)} merged", int(n.group(1)), f"{m}^2", f"{m}^1"))
    for ref in sys.argv[1:]:
        n = re.search(r"(\d+)", ref)
        targets.append((f"{ref} open", int(n.group(1)) if n else -1, ref, "origin/main"))
    pairs = as_is = files = 0
    for label, number, tip, base in targets:
        for label, number, s, branch, main_parent in sync_merges(label, number, tip, base):
            rc_as_is, rc_files, fa, fb, coll = replay(number, branch, main_parent)
            pairs += 1
            as_is += rc_as_is != 0
            files += bool(rc_files or coll)
            print(f"{label:<14} {s[:7]} as-is rc={rc_as_is} files rc={rc_files} "
                  f"ours={fa} theirs={fb} collisions={coll}")
    print(f"PAIRS: {pairs} plan-file conflicts; as-is {as_is} conflicting (null control); "
          f"one file per pull request {files} conflicting")
    return 0 if pairs and as_is == pairs and files == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
