#!/usr/bin/env python3
"""D13 / round 5 -- the friction histogram's keys, and the file each id names.

METRIC (one line). For every friction entry the production parser returns over
the window's merged pull-request bodies, the set of `--budgets` paths its
`<rule_id>` names under the four spellings below; reported as the share of
entries (and of distinct histogram keys) that name exactly one path, the share
that name several (the ambiguous row), and the share that name none.

THE SPELLING RULE (D13.md item 6), applied to the id with its backticks and its
`#anchor` dropped -- call the bare id `k`. A `--budgets` path `p` is named by
`k` when

    p == k   or   p ends in "/" + k   or   p ends in "/" + k + ".md"
             or   p ends in "/" + k + "/SKILL.md"

and the universe of `p` is the `files` object of `.claude/workflows/
policy_budgets.json` at the pinned baseline -- the paths `--budgets` compares a
size against, which is the surface a reader of the histogram is being sent to.
So `.claude/rules/ratchet-budgets.md` and `ratchet-budgets` name the same one
file, `README.md` names all three files whose basename is README.md, and an id
whose stem exists nowhere names nothing.

WHY THE KEY IS THE FILE. The histogram is the input to a filer that opens one
issue per key, and a key naming no file is an issue with no rule to dispose. The
production `frictionKey` already normalizes to a path where it can; this harness
measures how much of the window's friction survives that normalization as a key
a reader can act on, and it prints the per-file spelling counts so a key that
aggregates two spellings and a key that fragments one are both visible.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 /tmp/heatpump-orch/audit-r5-D13/h6_friction.py
  ... --perturb respell-md      # one accepted id -> `README.md`  (ambiguous row)
  ... --perturb respell-bare    # the same id without `.md`      (null control)
  ... --perturb unbacktick      # the same id, backticks stripped (null control)
  ... --perturb trailer-out     # one trailer line moved out of the section

PERTURBATION AND DIRECTION. `--perturb respell-md` re-spells ONE accepted entry's
id to `README.md`, which names three files: `entries_naming_one_file` must fall
by 1 and `entries_naming_several_files` must rise by 1. `--perturb respell-bare`
drops the `.md` from the same entry's id and `--perturb unbacktick` strips its
backticks; under the rule above both must leave EVERY per-file count unchanged
(they change spelling, not the file named), and those two are the null controls
that separate "the rule reads the file" from "the rule reads the string".
`--perturb trailer-out` inserts a `## Trailers` heading beside ONE body's
trailer line, which is the smallest fixture change that takes that line out of
the section the parser reads: `trailer_entries` must fall by exactly 1 (13 ->
12). `unlabelled_entries` does NOT move under it and that is the point: the
bucket is POSITIONAL, so taking one tail line out of the section only promotes
the next one, and a count that moved with the trailer would have been reading
the line rather than the position.

MACHINE: any; network-bound counts and a Node subprocess, no timing claim.
`RESULT api_failures=0` is required before any figure here is evidence.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d13lib as L  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
UNLABELLED = "(unlabelled friction bullet)"
# What a PR trailer looks like. A body's `## Friction` section runs to the
# next `## ` heading, and the trailers that close a body sit after the last
# section -- so they land INSIDE the friction section and `frictionEntries`
# keeps a section's first non-bullet line as an entry. That is the mechanism,
# this regex only names the shapes the window used.
TRAILER_RE = re.compile(r"^(?:🤖|Co-Authored-By:|Closes #|Generated with)")


def budgets_paths():
    """The `files` keys of the pinned policy_budgets.json."""
    out = subprocess.run(["git", "-C", str(L.ROOT), "show",
                          f"{L.BASELINE_SHA}:.claude/workflows/policy_budgets.json"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit("cannot read policy_budgets.json at the baseline")
    return sorted(json.loads(out.stdout)["files"].keys())


def friction_section(body):
    """The `## Friction` section of a body, ported from `policy_lint.mjs:sections`.

    The port is checked by cross-checking the histogram this harness builds
    against the production CLI's `--stats` CENSUS lines over the same window: a
    section this port missed is a key the CLI has and this harness does not.
    """
    out, cur, fence = {}, None, False
    for line in (body or "").split("\n"):
        if line.strip().startswith("```"):
            fence = not fence
        if not fence:
            if line.startswith("## "):
                cur = line[3:].strip()
                out[cur] = []
                continue
        if cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}.get("Friction", "")


def strip_tokens(raw):
    """The bare id: backticks dropped, `#anchor` dropped (D13.md's rule)."""
    k = str(raw or "").strip().replace("`", "")
    return k.split("#", 1)[0].strip()


def named_files(k, paths):
    """The `--budgets` paths k names, by the four spellings."""
    if not k:
        return []
    hits = []
    for p in paths:
        if (p == k or p.endswith("/" + k) or p.endswith("/" + k + ".md")
                or p.endswith("/" + k + "/SKILL.md")):
            hits.append(p)
    return hits


def run_entries(sections, perturb=None):
    """Drive the production `frictionEntries` over the sections."""
    src, dst = (os.path.join(tempfile.mkdtemp(prefix="d13-fric-"), n)
                for n in ("in.json", "out.json"))
    json.dump(sections, open(src, "w"))
    p = subprocess.run(["node", os.path.join(HERE, "h6_entries.mjs"), src, dst],
                       capture_output=True, text=True, cwd=str(L.ROOT),
                       env=dict(os.environ, D13_ROOT=str(L.ROOT)))
    if p.returncode != 0:
        raise SystemExit(f"the production parser driver failed: {p.stderr[:400]}")
    print(p.stdout.strip())
    return json.loads(open(dst).read())


def main():
    argv = sys.argv[1:]
    perturb = argv[argv.index("--perturb") + 1] if "--perturb" in argv else "none"
    paths = budgets_paths()
    print(f"`--budgets` paths at the baseline: {len(paths)}")

    commits = L.window_commits()
    merges, blind = L.enumerate_merges(commits)
    bodies = {}
    for m in merges:
        p = L.pr(m["number"]) or {}
        bodies[m["number"]] = p.get("body") or ""
    print(f"window {L.W0} .. {L.W1}  merges={len(merges)}  unattributed={len(blind)}")

    sections = [friction_section(b) for b in bodies.values()]
    nums = list(bodies)
    if perturb == "trailer-out":
        # THE FIXTURE EDIT: one body's trailer line is taken out of the section
        # the parser reads, by putting a heading in front of it. Nothing is
        # written to a pull request; the body text lives in this process only.
        for i, (n, s) in enumerate(zip(nums, sections)):
            lines = s.split("\n")
            j = next((k for k, l in enumerate(lines)
                      if l.strip().startswith(("🤖", "Co-Authored-By:", "Closes #"))),
                     None)
            if j is not None:
                lines.insert(j, "## Trailers")
                sections[i] = "\n".join(lines)
                print(f"perturbation trailer-out: a `## Trailers` heading inserted "
                      f"before line {j + 1} of #{n}'s `## Friction` section")
                break
        else:
            raise SystemExit("no trailer line found inside any Friction section")
    entries = run_entries(sections)

    # One row per entry: the id as typed, the file(s) it names, the key.
    rows = []
    for n, per_pr in zip(bodies, entries):
        for e in per_pr:
            raw = e.get("id")
            k = strip_tokens(raw)
            hits = named_files(k, paths) if raw else []
            line = (e.get("line") or "").strip()
            rows.append({"pr": n, "raw": raw, "k": k, "files": hits,
                         "unlabelled": raw is None,
                         "trailer": bool(TRAILER_RE.match(line)),
                         "line": line})
    n_entries = len(rows)
    one = [r for r in rows if len(r["files"]) == 1]
    several = [r for r in rows if len(r["files"]) > 1]
    none_ = [r for r in rows if not r["files"]]
    trailers = [r for r in rows if r["trailer"]]
    print(f"\nentries (production parser): {n_entries}")
    print(f"  naming exactly one --budgets path: {len(one)}")
    print(f"  naming several (ambiguous row):    {len(several)}")
    print(f"  naming none:                       {len(none_)}")
    print(f"  entries that are PULL-REQUEST TRAILER LINES, not friction: "
          f"{len(trailers)}")
    for r in trailers:
        print(f"    #{r['pr']}: {r['line'][:90]!r} -> key "
              f"{UNLABELLED if r['unlabelled'] else r['k']}")
    if perturb in ("respell-md", "respell-bare", "unbacktick"):
        # THE FIXTURE PERTURBATION: one accepted entry's id re-spelled. The
        # bodies are never written anywhere; the rewrite is in this process.
        target = next((r for r in rows if len(r["files"]) == 1 and r["k"].endswith(".md")), None)
        if target is None:
            raise SystemExit("no accepted entry resolves to exactly one .md file")
        before = target["k"]
        if perturb == "respell-md":
            target["k"] = "README.md"
        elif perturb == "respell-bare":
            target["k"] = before[:-3]
        elif perturb == "unbacktick":
            target["raw"] = (target["raw"] or "").replace("`", "")
        else:
            raise SystemExit(f"unknown perturbation {perturb!r}")
        target["files"] = named_files(strip_tokens(target["k"]), paths)
        print(f"perturbation {perturb}: entry on #{target['pr']} "
              f"{before!r} -> {strip_tokens(target['k'])!r} "
              f"now names {target['files']}")
        one = [r for r in rows if len(r["files"]) == 1]
        several = [r for r in rows if len(r["files"]) > 1]
        none_ = [r for r in rows if not r["files"]]
        print(f"  after: one={len(one)} several={len(several)} none={len(none_)}")

    keys = Counter()
    for r in rows:
        if r["unlabelled"]:
            keys[UNLABELLED] += 1
        elif len(r["files"]) == 1:
            keys[r["files"][0]] += 1
        else:
            keys[strip_tokens(r["k"]) or UNLABELLED] += 1
    print(f"\ndistinct keys this harness derives: {len(keys)}")
    for k, c in keys.most_common():
        print(f"  {c:>4}  {k}")
    key_rows = [r for r in rows]
    keys_one = sum(1 for k in keys if k in set(paths))
    L.result("budget_paths", len(paths))
    L.result("friction_entries", n_entries)
    L.result("entries_naming_one_file", len(one))
    L.result("entries_naming_several_files", len(several))
    L.result("entries_naming_no_file", len(none_))
    L.result("entries_share_naming_one_file",
             round(len(one) / n_entries, 4) if n_entries else 0.0)
    L.result("histogram_keys", len(keys))
    L.result("histogram_keys_naming_one_file", keys_one)
    L.result("histogram_keys_naming_no_file",
             len(keys) - keys_one)
    L.result("unlabelled_entries", sum(c for k, c in keys.items()
                                       if k == UNLABELLED))
    L.result("trailer_entries", len(trailers))
    L.result("trailer_entries_that_are_unlabelled",
             sum(1 for r in trailers if r["unlabelled"]))
    L.result("trailer_entries_share_of_entries",
             round(len(trailers) / n_entries, 4) if n_entries else 0.0)
    L.result("trailer_distinct_prs", len({r["pr"] for r in trailers}))
    # the top key, by entry count and by distinct pull request -- the row the
    # filer acts on first
    by_pr = defaultdict(set)
    for r in rows:
        k = (UNLABELLED if r["unlabelled"] else
             (r["files"][0] if len(r["files"]) == 1 else strip_tokens(r["k"])))
        by_pr[k].add(r["pr"])
    top = max(by_pr.items(), key=lambda kv: kv[1])
    L.result("top_key_distinct_prs", len(top[1]))
    L.result("top_key_is_a_file", int(top[0] in set(paths)))
    print(f"\ntop key: {top[0]!r} at {len(top[1])} distinct pull request(s); "
          f"names a --budgets path: {top[0] in set(paths)}")
    # per-file spelling counts: for each path, how many entries reached it and
    # under which spelling of its own stem
    print("\nper-file spelling counts (entries that name the file):")
    spell = defaultdict(Counter)
    for r in rows:
        for p in r["files"]:
            stem = p.rsplit("/", 1)[-1]
            stem = "SKILL" if stem == "SKILL.md" else stem[:-3] if stem.endswith(".md") else stem
            k = r["k"]
            if k == p:
                s = "repo-relative path"
            elif k == stem:
                s = "bare stem"
            elif k == stem + ".md":
                s = "stem.md"
            elif k.endswith("/SKILL.md") or k == p.rsplit("/", 2)[-2]:
                s = "skill dir"
            else:
                s = "other"
            spell[p][s] += 1
            spell[p]["backticked" if "`" in str(r["raw"] or "") else "unbackticked"] += 1
    for p in sorted(spell, key=lambda x: -sum(spell[x].values())):
        L.result(f"file_entries|{p}", sum(v for k, v in spell[p].items()
                                           if k not in ("backticked", "unbackticked")))
        print(f"  {sum(v for k, v in spell[p].items() if k not in ('backticked','unbackticked')):>3}  {p}: "
              f"{dict(spell[p])}")
    L.result("perturbation", perturb)
    L.footer()


if __name__ == "__main__":
    main()
