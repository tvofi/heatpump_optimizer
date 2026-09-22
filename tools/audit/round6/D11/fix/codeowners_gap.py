#!/usr/bin/env python3
"""codeowners_gap.py -- the required-check enforcement surface vs CODEOWNERS.

R6-D11-01 (#1402). The live ruleset `main-protect-checks` (23698884) arms
`pull_request.require_code_owner_review`, so a change to an owner-carrying
`.github/CODEOWNERS` pattern cannot merge without @tvofi's approving review.
This harness measures how much of the surface that PRODUCES and IMPLEMENTS the
required checks is inside that boundary.

THE SURFACE (derived, never carried):

  A  every tracked `.github/workflows/*.yml`                        -- 6
     the six files that hold the jobs whose status contexts the
     `main-protect-checks` ruleset requires
  B  the scripts those workflows' non-comment lines execute         -- 26
     a script invoked with an interpreter -- `node`, `python`/`python3`,
     `bash` or `sh` -- on a line that is not a comment, kept only where
     the path is a tracked file and is not one of the six in A. The
     interpreter prefix is the rule, not decoration: a script invoked
     bare (`tools/audit/w5-partition/coverage_tree.sh fast || true`, a
     non-required job's instrument) is not counted, and the rule
     reproduces the finding's 26 exactly at the merge base.
  C  the hooks population, `.claude/hooks/*`                        -- 4
     (three are wired by `.claude/settings.json`; `always-fails.sh` is a
     deliberate unwired control -- the whole directory is the surface)
  D  `.claude/settings.json`                                        -- 1
     the wiring that gives a session its hooks

  A + B + C + D = 37 tracked files.

THE METRIC. Count of surface files matched by a CODEOWNERS pattern that
carries an owner, last-match-wins (GitHub's rule; a later ownerless line
un-owns a path -- this file's own header relies on that for COMMON.md).

ARMS.
  none           -- the tree's `.github/CODEOWNERS` unchanged (the null control)
  add-dir        -- perturbed: append `/.claude/workflows/  @tvofi`
  add-dir-unown  -- perturbed: that line, then an ownerless one naming
                    `.claude/workflows/policy_lint.mjs` (last-match-wins:
                    it takes the 11 covered back to 10)

The matcher mirrors GitHub's CODEOWNERS semantics for the pattern forms this
repository uses: a trailing-slash directory pattern, and an exact path.

    PYTHONPATH=tests/hastub python3 tools/audit/round6/D11/fix/codeowners_gap.py
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
CODEOWNERS = ".github/CODEOWNERS"
WF_DIR = ".github/workflows"
HOOKS_DIR = ".claude/hooks"
SETTINGS = ".claude/settings.json"

# A script the workflows execute: invoked with an interpreter on a line that
# is not a comment.
EXEC = re.compile(
    r"(?<![\w./-])(?:node|python3|python|bash|sh|npx|pnpm)\s+"
    r"((?:tests|tools|\.claude|\.github)/[A-Za-z0-9_./-]+\.(?:py|mjs|js|sh|yml))\b"
)


def tracked() -> set[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    return set(out)


def surface() -> dict[str, list[str]]:
    """The enforcement surface, grouped by how it is derived."""
    have = tracked()
    workflows = sorted(f for f in have if f.startswith(WF_DIR + "/") and f.endswith(".yml"))

    execs: set[str] = set()
    for wf in workflows:
        text = (ROOT / wf).read_text()
        for line in text.splitlines():
            if line.lstrip().startswith("#"):
                continue
            for m in EXEC.finditer(line):
                p = m.group(1)
                if p in have and p not in workflows:
                    execs.add(p)

    hooks = sorted(f for f in have if f.startswith(HOOKS_DIR + "/"))
    settings = [f for f in sorted(have) if f == SETTINGS]
    return {"workflows": workflows, "execs": sorted(execs), "hooks": hooks, "settings": settings}


def patterns() -> list[tuple[str, list[str]]]:
    """CODEOWNERS read as (pattern, owners) in file order. Blank/comment out."""
    rules = []
    for line in (ROOT / CODEOWNERS).read_text().splitlines():
        line = line.split("#", 1)[0].split()
        if line:
            rules.append((line[0], line[1:]))
    return rules


def hit(pat: str, path: str) -> bool:
    """GitHub CODEOWNERS pattern semantics for the forms used here."""
    anchored = pat.startswith("/")
    p = pat.strip("/")
    if p in ("", "*", "**"):
        return True
    if pat.endswith("/") or not any(ch in p for ch in "*?["):
        if anchored or "/" in p:
            return path == p or path.startswith(p + "/")
        return p in path.split("/")
    if anchored or "/" in p:
        import fnmatch

        return fnmatch.fnmatch(path, p) or fnmatch.fnmatch(path, p + "/*")
    import fnmatch

    return any(fnmatch.fnmatch(seg, p) for seg in path.split("/")) or fnmatch.fnmatch(path, p)


def covered(files: list[str], rules: list[tuple[str, list[str]]]) -> list[str]:
    out = []
    for path in files:
        last = None
        for pat, who in rules:
            if hit(pat, path):
                last = who
        if last:
            out.append(path)
    return out


def run(arm: str) -> None:
    s = surface()
    files = sorted(s["workflows"] + s["execs"] + s["hooks"] + s["settings"])
    rules = patterns()

    if arm in ("add-dir", "add-dir-unown"):
        rules = list(rules) + [("/.claude/workflows/", ["@tvofi"])]
        if arm == "add-dir-unown":
            rules = rules + [("/.claude/workflows/policy_lint.mjs", [])]

    cov = covered(files, rules)

    print(f"# arm {arm}: {len(rules)} pattern(s), {len(cov)} covered")
    print(f"# surface: {len(s['workflows'])} workflow(s), {len(s['execs'])} exec'd script(s), "
          f"{len(s['hooks'])} hook(s), {len(s['settings'])} settings file = {len(files)}")
    for path in files:
        print(f"#   {'COVERED' if path in cov else 'UNCOVERED'} {path}")
    print(f"RESULT enforcement_surface_files={len(files)} count")
    print(f"RESULT covered_by_an_owner={len(cov)} count")
    print(f"RESULT uncovered_files={len(files) - len(cov)} count")


def main() -> int:
    arms = sys.argv[1:] or ["none", "add-dir", "add-dir-unown"]
    for arm in arms:
        run(arm)
    return 0


if __name__ == "__main__":
    sys.exit(main())
