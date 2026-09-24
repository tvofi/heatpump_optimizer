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
     both. An interpreter named by its path counts too (2026-09-24): the
     required `typing` job runs `.venv-typing/bin/python tests/typing_ruler.py`,
     which the bare-name rule never saw, so the ruler was owned by a line no
     derivation asked for.
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
through review; an owned file needs the owner's review besides. A file no
pull-request job grades with -- `nightly_ha.py` and `replay.py` run on the
schedule, and an instrument driven only by a `HPO_JOB_GRADES: nothing` job
grades nothing -- is covered with nothing to restore; the run tags it
`NO-PR-JOB` rather than `PINNED`, so the two are not read as one claim.

A restore holds only in a job that runs none of the pull request's code before
the grader (#1589 review, round 1: `coverage` ran the suite between the
restore and the ratchet). That is a property of the workflow files, which stay
@tvofi's, so the owner's review of a workflow edit is what keeps it; this
harness is a LINT that reads those owned files and refuses the forms that
would break it (the allowlist at ALLOWED_USES below). It is not the trust
boundary and not a shell parser: round 2's denylist missed 18 of 23 probes and
round 3's allowlist 8 more, all of them edits to an owned workflow.
`--self-test` drives the probe table (PROBES, every one must unpin) and its
null controls (NULLS, every one must stay pinned).

What a pin does not reach. The test-side pinned graders' jobs
(`coverage-ratchet`, `nightly-status`, `delivery-status`) are not required
contexts, so a red from the base's copy there blocks nothing by itself:
`pr-contract` makes the body answer it, and the fix review blocks an
unanswered one. A pinned grader still reads the pull request's tree and what
its code produced (the coverage JSON), so a suite that
misreports is left to review. And the base is `pull_request.base.sha`, the
base branch's tip when the event fired: a stricter grader that lands on
`main` later reaches an open pull request only when it is re-run against the
newer base, so until then the pin can be laxer than `main`.

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

    python3 -I tools/audit/round6/D11/fix/codeowners_gap.py [--check | --self-test]

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
    r"(?<![\w./-])(?:(?:[\w.-]+/)*(?:node|python3|python|bash|sh|npx|pnpm)\s+(?:-[A-Za-z]+\s+)*|\./)"
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


# WHAT MAY RUN BEFORE A PINNED GRADER IN ITS JOB -- an ALLOWLIST LINT (#1589
# review, rounds 1 to 4). It is a lint over `.github/workflows/`, which is
# @tvofi's: every construct it refuses is an edit to an owned file, so the
# owner's review is the barrier, and this keeps the owned workflows honest as
# they change. It is not a shell parser and does not prove a job safe; it
# reads the forms below and counts a grader as pinned only when every step
# before it, and the grader's own line, uses nothing else:
#   * `uses:` of ALLOWED_USES, at these exact revisions;
#   * in `run:`, simple commands whose word is `set` (flags only), `git` with a
#     GIT_OK subcommand (`checkout` only from "$PINNED", `-c` only for the
#     identity), `test`/`[`, `echo`/`printf`, a PLAIN_OK tool, `gh api`, shell
#     keywords, or a pinned grader: a file this job restored earlier, run by a
#     BARE interpreter name or by its path, `.py` under `-I`;
#   * `$(...)` only around an admitted command, and output redirection only
#     into the runner's scratch (`$RUNNER_TEMP`, `/tmp`, `$GITHUB_OUTPUT`,
#     `$GITHUB_STEP_SUMMARY`, `/dev/null`).
# It refuses, from that line on: any other command; a line it cannot parse (a
# heredoc, a backtick, a subshell, an unknown operator); a word that makes an
# admitted tool write a file (`-o`, `--output`, `-O`); an assignment to
# `PINNED` or a CODE_VARS name as a bare assignment, a command prefix,
# `read` or `printf -v`, and every `export`/`declare`; a write to `$GITHUB_ENV`
# or `$GITHUB_PATH`; a step or job `shell:`, `working-directory:` or
# `defaults:`; an `env:` value naming a tracked path, a CODE_VARS name in
# `env:`, or a `PINNED` other than the two PINNED_OK forms. Other assignments
# (`BODY=$(...)`, arrays) are admitted: `pr-contract` uses them.
ALLOWED_USES = {
    "actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09",
    "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1",
    "actions/setup-node@a0853c24544627f65ddf259abe73b1d18a591444",
    "actions/download-artifact@37930b1c2abaa49bbe596cd826c3c89aef350131",
}
# `diff` and `commit` because pinned jobs on `main` use them; `show` and `log`
# were dropped in round 4 (`git show --output=` writes a file).
GIT_OK = {"cat-file", "fetch", "checkout", "rev-parse", "hash-object", "diff", "merge-base", "commit"}
PLAIN_OK = {"test", "[", "cmp", "mkdir", "true", "rm", "wc", "sort", "paste", "cat", "jq", "read"}
# Shell grammar words: the commands between them are each checked.
KEYWORDS = {"if", "then", "else", "elif", "fi", "while", "until", "do", "done", "for", "in", "!"}
# A variable that makes a later program load code it names.
# A variable that makes a later program load code it names, and `PINNED`,
# which names the ref every restore and byte check reads.
CODE_VAR_NAME = re.compile(r"^(?:PINNED|PATH|BASH_ENV|ENV|LD_\w+|NODE_\w+|PYTHON\w*|GIT_\w+|PERL5\w*|RUBY\w*)$")
CODE_VARS = re.compile(r"^(?:PINNED|PATH|BASH_ENV|ENV|LD_\w+|NODE_\w+|PYTHON\w*|GIT_\w+|PERL5\w*|RUBY\w*)\+?=")
# A word that tells a program to write a file: `sort -o`, `git diff --output=`,
# `curl -O`. Any such word outside `set` taints (round 4).
WRITES_FILE = re.compile(r"^(?:-[A-Za-z]*[oO][A-Za-z]*|--output\b.*|--o=.*)$")
# The two admitted values of `PINNED` in a step or job `env:`.
PINNED_OK = {"${{ github.event.pull_request.base.sha || github.sha }}",
             "${{ github.event.pull_request.base.sha }}"}
# A bare interpreter name, resolved on the job's PATH, which nothing admitted
# can change; never a path (round 4: `tools/shim/python3`).
INTERP = re.compile(r"^(?:python3?|node|bash|sh)$")
SCRATCH = ("$RUNNER_TEMP", "${RUNNER_TEMP}", "/tmp/", "$GITHUB_OUTPUT", "${GITHUB_OUTPUT}",
           "$GITHUB_STEP_SUMMARY", "${GITHUB_STEP_SUMMARY}", "/dev/null")
OPS = {";", "&&", "||", "|", "&", "|&"}
REDIR = re.compile(r"^\d*(?:>>?|<|>&|&>)$")


def _substitutions(text: str) -> "tuple[str, list[str]] | None":
    """`text` with each top-level `$(...)` replaced by `SUBST`, and the inner
    commands; None when it cannot be read (a backtick, an unbalanced one)."""
    if "`" in text:
        return None
    out, inner, i = [], [], 0
    while i < len(text):
        if text.startswith("$(", i) and not text.startswith("$((", i):
            depth, j = 1, i + 2
            while j < len(text) and depth:
                depth += {"(": 1, ")": -1}.get(text[j], 0)
                j += 1
            if depth:
                return None
            inner.append(text[i + 2:j - 1])
            out.append("SUBST")
            i = j
        else:
            out.append(text[i])
            i += 1
    return "".join(out), inner


def admitted(line: str, have: set[str], specs: list[str], _depth: int = 0) -> bool:
    """True when every command on this logical `run:` line is on the allowlist."""
    import shlex

    if _depth > 3 or "<<" in line:
        return False
    sub = _substitutions(line)
    if sub is None:
        return False
    flat, inner = sub
    flat = re.sub(r"\b([A-Za-z_]\w*)(\+?=)\(([^()]*)\)", r"\1\2ARRAY", flat)
    if not all(admitted(c, have, specs, _depth + 1) for c in inner):
        return False
    try:
        lex = shlex.shlex(flat, posix=True, punctuation_chars=";&|<>()")
        lex.whitespace_split = True
        toks = list(lex)
    except ValueError:
        return False
    cmds, cur = [], []
    for t in toks:
        if t in OPS:
            cmds.append(cur)
            cur = []
        elif t in ("(", ")") or (set(t) <= set(";&|<>()") and not REDIR.match(t)):
            return False
        else:
            cur.append(t)
    cmds.append(cur)
    for cmd in cmds:
        if not cmd:
            continue
        words, k = [], 0
        while k < len(cmd):
            t = cmd[k]
            if REDIR.match(t):
                if k + 1 >= len(cmd):
                    return False
                tgt = cmd[k + 1]
                if "GITHUB_ENV" in tgt or "GITHUB_PATH" in tgt:
                    return False
                if t.lstrip("0123456789") != "<" and not tgt.startswith(SCRATCH):
                    if not (t.endswith("&") and tgt.isdigit()):
                        return False
                k += 2
                continue
            words.append(t)
            k += 1
        while words and words[0] in KEYWORDS:
            words = words[1:]
        while words and re.match(r"^[A-Za-z_]\w*\+?=", words[0]):
            if CODE_VARS.match(words[0]):
                return False  # PATH, BASH_ENV, LD_PRELOAD, NODE_OPTIONS, ...
            words = words[1:]
        if not words:
            continue
        w = words[0]
        if w in ("export", "declare", "local", "readonly", "typeset"):
            return False
        if w in PLAIN_OK | {"git", "echo", "printf", "gh"}:
            if any(WRITES_FILE.match(a) for a in words[1:]):
                return False  # `sort -o`, `git diff --output=`: a write into the tree
            if w == "printf" and "-v" in words[1:]:
                return False  # `printf -v PATH ...` assigns
            if w == "read" and any(CODE_VAR_NAME.match(a) for a in words[1:]):
                return False  # `read -r PATH < file` assigns
        if w == "set":
            if not all(a.startswith(("-", "+")) or a == "pipefail" for a in words[1:]):
                return False
        elif w == "git":
            while len(words) > 2 and words[1] == "-c" and re.match(r"^user\.(?:name|email)=", words[2]):
                words = [w] + words[3:]  # an identity, which runs nothing
            if len(words) < 2 or words[1] not in GIT_OK:
                return False
            if words[1] == "checkout" and (len(words) < 4 or words[2] != "$PINNED" or words[3] != "--"):
                return False
        elif w in ("echo", "printf"):
            pass  # a substitution in it was admitted above, command by command
        elif w == "gh":
            if len(words) < 2 or words[1] != "api":
                return False
        elif w in PLAIN_OK:
            pass
        else:
            # A pinned grader, by interpreter or by its own path.
            target, flags = None, []
            if INTERP.match(w):
                rest = words[1:]
                while rest and rest[0].startswith("-"):
                    flags.append(rest.pop(0))
                target = rest[0] if rest else None
            else:
                target = w
            if not target:
                return False
            target = os.path.normpath(target)
            if target not in have or not any(spec_hit(sp, target) for sp in specs):
                return False
            if target.endswith(".py") and "-I" not in flags:
                return False
    return True


def run_lines(step: str) -> "list[str] | None":
    """The logical lines of a step's `run:` block, continuations joined."""
    m = re.search(r"^        run:[ \t]*(.*)$", step, re.M)
    if not m:
        return []
    head = m.group(1).strip()
    if head and head[0] not in "|>":
        body = [head]
    else:
        body = []
        for ln in step[m.end():].splitlines()[1:]:
            if ln.strip() and not ln.startswith("          "):
                break
            body.append(ln[10:])
    import shlex

    out, buf = [], ""
    for ln in body:
        if not buf and ln.lstrip().startswith("#"):
            continue
        if ln.rstrip().endswith("\\"):
            buf += ln.rstrip()[:-1] + " "
            continue
        buf += ln
        try:
            shlex.split(buf)
        except ValueError:
            buf += "\n"  # a quoted string runs on
            continue
        out.append(buf)
        buf = ""
    if buf:
        out.append(buf)
    return [ln for ln in out if ln.strip()]


def step_uses(step: str) -> str:
    m = re.search(r"^ {6}(?:- | {2})uses:\s*(\S+)", step, re.M)
    return m.group(1) if m else ""


def _bad_pinned(env_block: str) -> bool:
    """True when an `env:` block sets PINNED, or a code-loading variable, to
    anything but the two admitted forms (round 4: `PINNED: ${{ github.sha }}`
    makes the restore and the byte check read the pull request's own commit)."""
    for name, val in re.findall(r"^\s*([A-Za-z_]\w*):\s*(.*?)\s*$", env_block, re.M):
        if name == "PINNED" and val.strip("'\"") not in PINNED_OK:
            return True
        if name != "PINNED" and CODE_VAR_NAME.match(name):
            return True
    return False


def _names_tracked(env_block: str, have: set[str]) -> bool:
    """True when an `env:` value names a tracked file or directory."""
    for val in re.findall(r":\s*(.*)$", env_block, re.M):
        for tok in re.findall(r"[A-Za-z0-9_.][A-Za-z0-9_./-]*", val):
            t = os.path.normpath(tok)
            if "/" in t and (t in have or any(f.startswith(t + "/") for f in have)):
                return True
    return False


def job_executions(wf: str, job: str, jt: str, have: set[str]) -> list[tuple[str, str, str, bool, bool]]:
    """(workflow, job, file, pinned, isolated) for every file the job runs or
    loads; `pinned` needs a restore earlier in the job whose pathspec matches,
    and nothing before it outside the allowlist."""
    out = []
    specs: list[str] = []
    # A job-level `defaults:` can turn every `run:` into another program, and a
    # job-level `env:` value naming a tracked path can load it into one.
    tainted = bool(re.search(r"^    defaults:", jt, re.M))
    jenv = re.search(r"^    env:\n((?:      .*\n?)*)", jt, re.M)
    if jenv and (_names_tracked(jenv.group(1), have) or _bad_pinned(jenv.group(1))):
        tainted = True
    for step in jt.split("\n      - ")[1:]:
        step = "      - " + step
        live = "\n".join(ln for ln in step.splitlines() if not ln.lstrip().startswith("#"))
        uses = step_uses(live)
        if uses and uses not in ALLOWED_USES:
            tainted = True
        if re.search(r"^        (?:shell|working-directory):", live, re.M):
            tainted = True
        envm = re.search(r"^        env:\n((?:          .*\n?)*)", live, re.M)
        if envm and (_names_tracked(envm.group(1), have) or _bad_pinned(envm.group(1))):
            tainted = True
        lines = run_lines(live)
        for line in lines:
            r = RESTORE.search(line)
            # The grader's own line must be admitted too: a grader run by
            # `tools/shim/python3` is the shim's, not the base's.
            line_ok = admitted(line, have, specs)
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
                    out.append((wf, job, f,
                                not tainted and line_ok and any(spec_hit(sp, f) for sp in specs), iso))
            if r:
                specs += re.findall(r"'([^']+)'", r.group(1))
            if not admitted(line, have, specs):
                tainted = True
    return out


def executions(have: set[str]) -> list[tuple[str, str, str, bool, bool]]:
    """Every (workflow, job, file, pinned, isolated) a PR-reachable grading job
    executes or loads, in step order."""
    out = []
    workflows = sorted(f for f in have if f.startswith(WF_DIR + "/") and f.endswith(".yml"))
    for wf in workflows:
        text = (ROOT / wf).read_text()
        head = text[: text.find("\njobs:\n")]
        wenv = re.search(r"^env:\n((?:  .*\n?)*)", head, re.M)
        whole_file = bool(re.search(r"^defaults:", head, re.M)) or bool(
            wenv and _names_tracked(wenv.group(1), have))
        for job, jt in jobs_of(text):
            if not pr_reachable(text, jt) or SELF_TEST_ONLY.search(jt):
                continue
            out += [(w, j, f, p and not whole_file, i)
                    for (w, j, f, p, i) in job_executions(wf, job, jt, have)]
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
    unrun = {f for f in pins if not any(e[2] == f for e in ex)}

    print(f"# arm {arm}: {len(rules)} pattern(s), {len(cov)} covered ({len(pins)} of them pinned, not owned)")
    print(f"# surface: {len(s['workflows'])} workflow(s), {len(s['execs'])} exec'd script(s), "
          f"{len(s['imports'])} imported by them, {len(s['evaluated'])} run by path, "
          f"{len(s['hooks'])} hook(s), {len(s['settings'])} settings file = {len(files)}")
    for path in files:
        tag = ("COVERED" if path in owned else "NO-PR-JOB" if path in unrun
               else "PINNED" if path in pins else "UNCOVERED")
        print(f"#   {tag} {path}")
    print(f"RESULT enforcement_surface_files={len(files)} count")
    print(f"RESULT covered_by_an_owner={len(owned)} count")
    print(f"RESULT pinned_by_base_restore={len(pins)} count")
    print(f"RESULT of_which_no_pr_job_runs={len(unrun)} count")
    print(f"RESULT uncovered_files={len(files) - len(cov)} count")
    return len(files) - len(cov) if files else -1


# THE ALLOWLIST'S MUTATION TABLE (#1589 review, round 3). Each PROBE is one
# step inserted above the grading step of a job shaped like `coverage-ratchet`;
# every one must leave the grader NOT pinned. Round 2's denylist left 18 of
# the reviewer's 23 insertions (and a github-script `require`) pinned. Each
# NULL is a step the allowlist admits, and must leave the grader pinned, so a
# rule that refuses everything fails here too.
SELF_TEST_JOB = """  probe-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5

      - uses: actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1 # v6
        with:
          python-version: "3.13"
%s
      - name: grade
        env:
          PINNED: ${{ github.event.pull_request.base.sha }}
        run: |
          set -euo pipefail
          git checkout "$PINNED" -- \\
            'tests/coverage_ratchet.py'
          test "$(git hash-object tests/coverage_ratchet.py)" = "$(git rev-parse "$PINNED:tests/coverage_ratchet.py")"
          python3 -I -S tests/coverage_ratchet.py --coverage "$RUNNER_TEMP/c.json"
"""
T = "tools/audit/w5-partition/coverage_tree.sh"


def _GRADE(cmd: str):
    """A line inserted into the grading step, before its restore."""
    return lambda jt: jt.replace("          set -euo pipefail\n", "          set -euo pipefail\n          " + cmd + "\n", 1)


def _run(cmd: str) -> str:
    body = "\n".join("          " + ln for ln in cmd.splitlines())
    return "\n      - name: probe\n        run: |\n" + body + "\n"


PROBES = [
    ("pip install", _run("pip install -r tests/requirements-ci.txt")),
    ("npm ci", _run("npm ci")),
    ("bare tracked path", _run(T + " fast || true")),
    ("./ tracked path", _run("./tests/run.sh")),
    ("echo && script", _run("echo ok && " + T)),
    ("; script", _run("echo ok; " + T)),
    ("timeout 60", _run("timeout 60 " + T)),
    ("env A=1", _run("env A=1 " + T)),
    ("sudo", _run("sudo " + T)),
    ("cd x && ./y", _run("cd tools/audit/w5-partition && ./coverage_tree.sh fast")),
    ("bash -c", _run("bash -c '" + T + " fast'")),
    ("source", _run("source " + T)),
    (". file", _run(". " + T)),
    ("python3 -m tests.x", _run("python3 -m tests.harness")),
    ("python3 -c import", _run("python3 -c 'import sys; sys.path.insert(0, \"tests\"); import harness'")),
    ("exec", _run("exec " + T)),
    ("pytest", _run("pytest tests")),
    ("npm test", _run("npm test")),
    ("node --test", _run("node --test tests/")),
    ("npx", _run("npx some-tool")),
    ("find -exec", _run("find tools -name '*.sh' -exec {} \;")),
    ("cat x | bash", _run("cat " + T + " | bash")),
    ("python3 - heredoc", _run("python3 - <<'PY'\nimport runpy\nPY")),
    ("$GITHUB_PATH shim", _run('mkdir -p "$RUNNER_TEMP/shim"\necho "$RUNNER_TEMP/shim" >> "$GITHUB_PATH"')),
    ("$GITHUB_ENV BASH_ENV", _run('echo "BASH_ENV=$PWD/' + T + '" >> "$GITHUB_ENV"')),
    ("PATH= assignment", _run('PATH="$PWD/tools:$PATH" git rev-parse HEAD')),
    ("echo $(script)", _run('echo "$(' + T + ')"')),
    ("backtick", _run("echo `" + T + "`")),
    ("github-script require", "\n      - uses: actions/github-script@v7\n        with:\n"
     "          script: require('./tests/harness.js')\n"),
    ("local action", "\n      - uses: ./.github/actions/setup\n"),
    ("unpinned setup-python", "\n      - uses: actions/setup-python@v6\n"),
    ("step shell:", "\n      - name: probe\n        shell: python {0}\n        run: echo ok\n"),
    ("step env names a tracked file", "\n      - name: probe\n        env:\n"
     "          NODE_OPTIONS: --require ./tests/harness.py\n        run: echo ok\n"),
    ("git checkout HEAD -- grader", _run("git checkout HEAD -- tests/coverage_ratchet.py")),
    ("redirect into the tree", _run("echo 'import sys' > tests/coverage_ratchet.py")),
    # Round 4: eight insertions inside the grading step itself that round 3 admitted.
    ("sort -o into the grader", _GRADE("sort -o tests/coverage_ratchet.py tests/harness.py")),
    ("git show --output=", _GRADE("git show --output=tests/coverage_ratchet.py HEAD:tests/harness.py")),
    ("git diff --output=", _GRADE("git diff --output=tests/coverage_ratchet.py HEAD")),
    ("printf -v PATH", _GRADE("printf -v PATH '%s' \"tools:$PATH\"")),
    ("read -r PATH", _GRADE("read -r PATH < tests/README.md")),
    ("bare PINNED=HEAD before the restore", _GRADE("PINNED=HEAD")),
    ("step env PINNED: github.sha", lambda jt: jt.replace(
        "PINNED: ${{ github.event.pull_request.base.sha }}", "PINNED: ${{ github.sha }}")),
    ("grader run by an interpreter path", lambda jt: jt.replace(
        "python3 -I -S tests/coverage_ratchet.py", "tools/shim/python3 -I -S tests/coverage_ratchet.py")),
]
NULLS = [
    ("no inserted step", ""),
    ("echo and printf", _run("echo ok\nprintf '%s\\n' done")),
    ("git fetch, rev-parse, hash-object", _run('git fetch -q --no-tags --depth=1 origin main\n'
                                                 'git rev-parse HEAD\ngit hash-object README.md > /dev/null')),
    ("set, test, mkdir, cmp", _run('set -eo pipefail\ntest -f README.md\nmkdir -p "$RUNNER_TEMP/x"\n'
                                   'cmp README.md README.md')),
    ("download-artifact at its pin", "\n      - uses: actions/download-artifact@"
     "37930b1c2abaa49bbe596cd826c3c89aef350131 # v7\n        with:\n          name: x\n"),
    ("a scratch write", _run('echo x > "$RUNNER_TEMP/x.txt"')),
]


def self_test() -> int:
    have = tracked()
    grader = "tests/coverage_ratchet.py"
    bad = 0
    for kind, rows, want in (("PROBE", PROBES, False), ("NULL", NULLS, True)):
        for name, step in rows:
            jt = step(SELF_TEST_JOB % "") if callable(step) else SELF_TEST_JOB % step
            ex = [e for e in job_executions("probe.yml", "probe-job", jt.split(":\n", 1)[1], have)
                  if e[2] == grader]
            got = bool(ex) and all(p for (_, _, _, p, _) in ex)
            ok = got == want
            bad += not ok
            print(f"  {'ok  ' if ok else 'FAIL'} {kind:5} {name}: grader {'PINNED' if got else 'not pinned'}")
    print(f"SELF-TEST: {len(PROBES)} probe(s), {len(NULLS)} null(s), {bad} wrong")
    return 1 if bad else 0


def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        return self_test()
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
