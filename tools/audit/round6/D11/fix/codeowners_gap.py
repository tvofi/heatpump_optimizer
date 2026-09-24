#!/usr/bin/env python3
"""codeowners_gap.py -- the required-check enforcement surface vs CODEOWNERS.

R6-D11-01 (#1402). The live ruleset `main-protect-checks` (23698884) arms
`pull_request.require_code_owner_review`, so a change to an owner-carrying
`.github/CODEOWNERS` pattern cannot merge without @tvofi's approving review.
This harness measures how much of the surface that PRODUCES and IMPLEMENTS the
required checks is inside that boundary.

THE SURFACE (derived, never carried -- the run prints each group's size):

  A  every tracked `.github/workflows/*.yml`, the files that hold the jobs
     whose status contexts the `main-protect-checks` ruleset requires
  B  the scripts those workflows' non-comment lines execute: a script
     invoked with an interpreter -- `node`, `python`/`python3`, `bash` or
     `sh` -- or by its own `./` path, on a line that is not a comment, kept
     only where the path is a tracked file and is not in A. A path with
     neither prefix is not an invocation: `tools/audit/w5-partition/
     coverage_tree.sh fast || true`, a non-required job's instrument, is
     invoked bare and is not counted. The `./` form is round 8's addition
     (#1515): `./tests/run.sh` and `./tests/derive_closures.sh` are how two
     required jobs run their scripts, and the interpreter-only rule missed
     both.
  E  what B's scripts load, transitively (#1515): a relative `import`,
     `import()` or `require()` in a `.mjs`/`.js`, and a Python `import` or
     `from ... import` naming a tracked module beside the importer or under
     `tests/`. A script's imports execute with it, so an unowned import is an
     unowned check -- round 8 turned `pr-contract`'s refusal green with one
     line appended to `counts.mjs`, which `policy_lint.mjs` imports. The walk
     does not enter a shell script's body: `tests/run.sh` runs the whole
     suite, and owning the suite is not what this surface is.
  F  what B's and E's governance scripts can EXECUTE by path (#1515 review,
     round 1): a script outside `tests/` that holds an evaluating construct
     -- `new Function(`, `eval(`, `vm.`, `import(`, `exec(`, `runpy` -- joins
     the tracked code files it names in a quoted string, repo-relative or
     relative to itself. `policy_lint.mjs` builds `web-fix-wave.js`'s
     VERDICT_RE through `new Function`, and one line there turned a red
     corpus's `policy-docs` green; E, which follows only imports, never
     reached it. A name is not proof of evaluation, so F over-approximates:
     every file it returns is owned rather than argued. Strings, docstrings
     and block comments are blanked before the construct is looked for, and
     a RegExp's `.exec(` is not one. `tests/` is out of F for E's reason: the
     suite runs the pull request's code by design.
  C  the hooks population, `.claude/hooks/*` (three are wired by
     `.claude/settings.json`; `always-fails.sh` is a deliberate unwired
     control -- the whole directory is the surface)
  D  `.claude/settings.json`, the wiring that gives a session its hooks

THE METRIC. Count of surface files COVERED: matched by a CODEOWNERS pattern
that carries an owner, last-match-wins (GitHub's rule; a later ownerless line
un-owns a path -- this file's own header relies on that for COMMON.md), or
PINNED (decision 0013): a file in B, E or F that no job reachable from a pull
request executes from the pull request's own copy. A job is reachable unless
its `if:` names `github.event_name` only against other events; a job whose
`env:` sets `HPO_JOB_GRADES: nothing` runs self-tests whose verdict is about
the pull request's instruments and grades nothing, and is skipped -- `--check`
refuses one that a required context names. In every other reachable job, each
execution of the file must come after a step of the form
`git checkout "$PINNED" -- '<pathspec>' ...` whose pathspecs match it (git's
glob, where `*` crosses `/`), and a pinned `.py` must run under `python3 -I`,
so a module the pull request adds beside it cannot shadow an import. The
workflows, hooks and settings (A, C, D) are never pinned: GitHub runs the pull
request's own workflow file, and a hook is graded by no job. So a pull request
editing a pinned file changes nothing its own required checks run -- the
restore puts the base's copy back first -- and the edit reaches `main` only
through review; an owned file needs the owner's review besides.

ARMS.
  none           -- the tree's `.github/CODEOWNERS` unchanged (the null control)
  add-dir        -- perturbed: append `/.claude/workflows/  @tvofi`
  add-dir-unown  -- perturbed: that line, then an ownerless one naming
                    `.claude/workflows/web-fix-wave.js`, which a grader
                    evaluates from the pull request's copy (last-match-wins:
                    one surface file back out of coverage)
  unpin          -- perturbed: the pinnable files (B, E, F outside tests/ and
                    the evaluated wave scripts) lose their owners, AND the
                    restore steps are dropped: every one goes uncovered
  --check        -- the standing gate (#1515): arm `none`, exit 1 when any
                    surface file is uncovered or the surface is empty. The
                    `policy-docs` job runs it with the base commit's copy of
                    this file over the pull request's CODEOWNERS and tree.

The matcher mirrors GitHub's CODEOWNERS semantics for the pattern forms this
repository uses: a trailing-slash directory pattern, and an exact path.

    python3 -I tools/audit/round6/D11/fix/codeowners_gap.py [--check]

`-I` in the gate, always: without it Python puts this file's directory first on
sys.path, and a pull request that adds `subprocess.py` beside it runs its own
module before the check (#1515 review, round 1).
"""

import os
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
    r"(?<![\w./-])(?:(?:node|python3|python|bash|sh|npx|pnpm)\s+(?:-[A-Za-z]+\s+)*|\./)"
    r"((?:tests|tools|\.claude|\.github)/[A-Za-z0-9_./-]+\.(?:py|mjs|js|sh|yml))\b"
)

# What an executed script loads (group E). JS: a RELATIVE specifier in a static
# or dynamic import or a require -- a bare specifier is a package, not the tree.
JS_LOAD = re.compile(
    r"""(?:\bfrom\s+|\bimport\s*\(\s*|\bimport\s+|\brequire\(\s*)['"](\.{1,2}/[^'"]+)['"]"""
)
# Python: the first dotted component of every `import X` / `from X import`,
# resolved beside the importer and under `tests/`, where the suite puts its
# shared modules on `sys.path`.
PY_LOAD = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+(?:\s*,\s*[\w.]+)*))", re.M)


# Group F. A quoted path to a code file, and the constructs that can run one.
NAMED = re.compile(r"""['"]((?:\.{1,2}/)?[A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:js|mjs|cjs|py|sh))['"]""")
# `.exec(` is a RegExp method, not an evaluation, so `eval(`/`exec(` must not follow a dot.
EVALS = re.compile(r"new Function\(|(?<![.\w])(?:eval|exec)\(|\bvm\.|\bimport\(|\brunpy\b")
CODE_EXT = (".js", ".mjs", ".cjs", ".py", ".sh")
# Docstrings and block comments are prose, not code.
BLOCKS = re.compile(r'"""[\s\S]*?"""' + r"|'''[\s\S]*?'''" + r"|/\*[\s\S]*?\*/")
QUOTED = re.compile(r"'(?:[^'\\]|\\.)*'" + r'|"(?:[^"\\]|\\.)*"')


def named(path: str, have: set[str]) -> set[str]:
    """The tracked code files an evaluating script outside tests/ names (group F)."""
    if path.startswith("tests/") or not path.endswith(CODE_EXT):
        return set()
    text = BLOCKS.sub("", (ROOT / path).read_text(errors="replace"))
    live = [ln for ln in text.splitlines()
            if not ln.lstrip().startswith(("#", "//", "*", "/*"))]
    # The construct must be code, not text: quoted strings are blanked first, so
    # a pattern that names `exec(` (this file's own EVALS) is not an evaluation.
    if not any(EVALS.search(QUOTED.sub("''", ln)) for ln in live):
        return set()
    out: set[str] = set()
    for ln in live:
        for m in NAMED.finditer(ln):
            v = m.group(1)
            for p in (os.path.normpath(v), os.path.normpath(os.path.join(os.path.dirname(path), v))):
                if p in have and p != path and p.endswith(CODE_EXT):
                    out.add(p)
    return out


def loads(path: str, have: set[str]) -> set[str]:
    """The tracked files `path` imports, one level."""
    src = (ROOT / path).read_text(errors="replace")
    out: set[str] = set()
    if path.endswith((".mjs", ".js")):
        for m in JS_LOAD.finditer(src):
            p = os.path.normpath(os.path.join(os.path.dirname(path), m.group(1)))
            if p in have:
                out.add(p)
    elif path.endswith(".py"):
        for m in PY_LOAD.finditer(src):
            names = [m.group(1)] if m.group(1) else [n.strip() for n in m.group(2).split(",")]
            for name in names:
                for d in (os.path.dirname(path), "tests"):
                    p = os.path.normpath(os.path.join(d, name.split(".")[0] + ".py"))
                    if p in have:
                        out.add(p)
    return out


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

    seen: set[str] = set()
    todo = sorted(execs)
    while todo:
        f = todo.pop()
        if f not in seen:
            seen.add(f)
            todo += sorted(loads(f, have))
    imported = seen - execs - set(workflows)
    evaluated: set[str] = set()
    todo = sorted(seen)
    while todo:
        f = todo.pop()
        for p in sorted(named(f, have) | loads(f, have)):
            if p not in seen:
                seen.add(p)
                evaluated.add(p)
                todo.append(p)

    hooks = sorted(f for f in have if f.startswith(HOOKS_DIR + "/"))
    settings = [f for f in sorted(have) if f == SETTINGS]
    return {"workflows": workflows, "execs": sorted(execs), "imports": sorted(imported),
            "evaluated": sorted(evaluated), "hooks": hooks, "settings": settings}


RESTORE = re.compile(r"""git checkout\s+"?\$\{?PINNED\}?"?\s+--\s+((?:\\?\s*'[^']+'\s*)+)""")
SELF_TEST_ONLY = re.compile(r"^      HPO_JOB_GRADES:\s*[\"']?nothing[\"']?\s*$", re.M)
EVENT_IF = re.compile(r"github\.event_name\s*(==|!=)\s*'([a-z_]+)'")


def spec_hit(spec: str, path: str) -> bool:
    """git pathspec semantics for the forms the restore steps use."""
    import fnmatch

    if any(ch in spec for ch in "*?["):
        return fnmatch.fnmatch(path, spec)
    return path == spec or path.startswith(spec.rstrip("/") + "/")


def jobs_of(wf_text: str) -> list[tuple[str, str]]:
    """(job id, job text) for every job under the top-level `jobs:` key."""
    i = wf_text.find("\njobs:\n")
    if i < 0:
        return []
    body = wf_text[i + len("\njobs:\n"):]
    parts = re.split(r"^  ([A-Za-z][\w-]*):\n", body, flags=re.M)
    return [(parts[k], parts[k + 1]) for k in range(1, len(parts) - 1, 2)]


def pr_reachable(wf_text: str, job_text: str) -> bool:
    """False only when the workflow has no `pull_request` trigger, or the job's
    `if:` compares `github.event_name` solely against other events."""
    head = wf_text[: wf_text.find("\njobs:\n")]
    if not re.search(r"^  pull_request:", head, re.M) and "pull_request]" not in head:
        return False
    m = re.search(r"^    if:(.*?)(?=^    [a-z-]+:)", job_text, re.M | re.S)
    if not m:
        return True
    tests = EVENT_IF.findall(m.group(1))
    if not tests:
        return True
    if any(op == "!=" and ev == "pull_request" for op, ev in tests):
        return False
    return any(ev == "pull_request" for op, ev in tests if op == "==") or any(op == "!=" for op, _ in tests)


def executions(have: set[str]) -> list[tuple[str, str, str, bool, bool]]:
    """Every (workflow, job, file, pinned, isolated) a PR-reachable grading job
    executes or loads, in step order."""
    out = []
    workflows = sorted(f for f in have if f.startswith(WF_DIR + "/") and f.endswith(".yml"))
    for wf in workflows:
        text = (ROOT / wf).read_text()
        for job, jt in jobs_of(text):
            if not pr_reachable(text, jt) or SELF_TEST_ONLY.search(jt):
                continue
            specs: list[str] = []
            for step in jt.split("\n      - ")[1:]:
                live = "\n".join(ln for ln in step.splitlines() if not ln.lstrip().startswith("#"))
                r = RESTORE.search(live)
                if r:
                    specs += re.findall(r"'([^']+)'", r.group(1))
                for line in live.splitlines():
                    for m in EXEC.finditer(line):
                        entry = m.group(1)
                        if entry not in have:
                            continue
                        iso = bool(re.search(r"python3?\s+(?:-[A-Za-z]+\s+)*-I\b", line))
                        seen, todo = set(), [entry]
                        while todo:
                            f = todo.pop()
                            if f in seen:
                                continue
                            seen.add(f)
                            todo += sorted(loads(f, have) | named(f, have))
                        for f in sorted(seen):
                            out.append((wf, job, f, any(spec_hit(sp, f) for sp in specs), iso))
    return out


def self_test_only_required(have: set[str]) -> list[str]:
    """Self-test-only jobs a required context names -- refused by --check."""
    try:
        import json

        ctx = set(json.loads((ROOT / ".claude/workflows/fixtures/required-contexts.json").read_text())["contexts"])
    except (OSError, ValueError, KeyError):
        return []
    bad = []
    for wf in sorted(f for f in have if f.startswith(WF_DIR + "/") and f.endswith(".yml")):
        for job, jt in jobs_of((ROOT / wf).read_text()):
            if SELF_TEST_ONLY.search(jt) and job in ctx:
                bad.append(f"{wf}:{job}")
    return bad


def pinned(files: list[str], ex: list[tuple[str, str, str, bool, bool]], s: dict) -> list[str]:
    """Pinnable surface files (B, E, F) that every PR-reachable grading job runs
    from the base's copy -- `.py` under `-I`."""
    pinnable = set(s["execs"] + s["imports"] + s["evaluated"])
    out = []
    for f in files:
        if f not in pinnable:
            continue
        runs = [e for e in ex if e[2] == f]
        # `-I` is the interpreter's, so it is read off the line that started
        # the process and holds for every module that process imports.
        if all(p and (iso or not f.endswith(".py")) for (_, _, _, p, iso) in runs):
            out.append(f)
    return out


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


def run(arm: str) -> int:
    s = surface()
    files = sorted(set(s["workflows"] + s["execs"] + s["imports"] + s["evaluated"]
                       + s["hooks"] + s["settings"]))
    rules = patterns()
    ex = executions(tracked())

    if arm in ("add-dir", "add-dir-unown"):
        rules = list(rules) + [("/.claude/workflows/", ["@tvofi"])]
        if arm == "add-dir-unown":
            rules = rules + [("/.claude/workflows/web-fix-wave.js", [])]
    if arm == "unpin":
        pin_now = set(pinned(files, ex, s))
        rules = list(rules) + [("/" + f, []) for f in sorted(pin_now)]
        ex = [(w, j, f, False, iso) for (w, j, f, _, iso) in ex]

    owned = covered(files, rules)
    pins = [f for f in pinned(files, ex, s) if f not in owned]
    cov = sorted(set(owned) | set(pins))

    print(f"# arm {arm}: {len(rules)} pattern(s), {len(cov)} covered ({len(pins)} of them pinned, not owned)")
    print(f"# surface: {len(s['workflows'])} workflow(s), {len(s['execs'])} exec'd script(s), "
          f"{len(s['imports'])} imported by them, {len(s['evaluated'])} run by path, "
          f"{len(s['hooks'])} hook(s), {len(s['settings'])} settings file = {len(files)}")
    for path in files:
        tag = "COVERED" if path in owned else "PINNED" if path in pins else "UNCOVERED"
        print(f"#   {tag} {path}")
    print(f"RESULT enforcement_surface_files={len(files)} count")
    print(f"RESULT covered_by_an_owner={len(owned)} count")
    print(f"RESULT pinned_by_base_restore={len(pins)} count")
    print(f"RESULT uncovered_files={len(files) - len(cov)} count")
    return len(files) - len(cov) if files else -1


def main() -> int:
    if sys.argv[1:] == ["--check"]:
        gap = run("none")
        bad = self_test_only_required(tracked())
        if bad:
            print("REFUSED: a job marked `HPO_JOB_GRADES: nothing` is a required context "
                  f"({', '.join(bad)}); it runs the pull request's own copies, so it cannot grade")
            return 1
        if gap:
            print("REFUSED: " + ("the surface is empty -- nothing was derived" if gap < 0 else
                  f"{gap} file(s) a workflow executes or loads carry no CODEOWNERS owner; "
                  "own each above, or restore it from the base before every PR-reachable job runs it, "
                  "or the pull request can change the check it is graded by (#1515)"))
            return 1
        return 0
    arms = sys.argv[1:] or ["none", "add-dir", "add-dir-unown", "unpin"]
    for arm in arms:
        run(arm)
    return 0


if __name__ == "__main__":
    sys.exit(main())
