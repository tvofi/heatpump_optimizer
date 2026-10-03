#!/usr/bin/env python3
"""Refuse a tracked script, workflow or decision record that depends on a temp or machine path.

    python3 -I tools/audit/seat/tmp_paths.py --check [--ref <commit>]
    python3 -I tools/audit/seat/tmp_paths.py --self-test

WHY THIS EXISTS. On 2026-10-03 a temp cleanup deleted /private/tmp/audit-7. Three
tracked seat scripts kept their state there (ci-watch.sh, handoff_push.sh,
merge_pr.sh), decision 0012 cited a design note there, and the seat interpreter
the ~/hpo-seats shims ran lived there with no recipe anywhere. The owner's
ruling the same day: a tool the programme reruns is a tracked file, and a
session-local copy is a defect. This is the mechanical half of that ruling.

WHAT IT SCANS, at <ref> (default HEAD) through `git grep`, so a ref can be
graded without a checkout: `.github/workflows/*.yml`, `docs/decisions/*.md`,
`.claude/settings.json` (its hooks run commands), and every `.sh .py .mjs .js
.cjs` under `tools/`, `tests/` and `.claude/` plus the seat shims, except the
write-once round evidence under `tools/audit/round*/`, `tools/audit/handoff/`
and `tools/audit/w5-*/`, which records where things were. Policy prose (briefs,
rules, skills) is not scanned: it names paths to explain them.

WHAT IT REFUSES, one line per hit (`path:line: [class] text`); every match is
judged on its own, never excused by something else on its line:
  private-tmp      `/private/tmp` -- macOS-only and wiped by a cleanup;
  tmp              `/tmp` with a fixed name: a path under it (an f-string's
                   `{name}` included), or the bare root joined, concatenated,
                   pathlib-`/`-ed or `${X ?? '/tmp'}/`-suffixed with a literal,
                   or assigned to a variable;
  tmpdir-fixed     `$TMPDIR`, `${TMPDIR:-...}`, `os.environ["TMPDIR"]`,
                   `os.environ.get("TMPDIR"...)` or `tempfile.gettempdir()`
                   followed by a fixed name: a path component, `+ "..."`,
                   `, "..."` (a join) or `) / "..."` (pathlib);
  home-abs         `/Users/<name>/` or `/home/<name>/` -- one machine's home;
  home-instrument  `~/`, `$HOME/` or `${HOME}/` reaching a script or a bin/ dir:
                   an instrument run from outside the tree.

WHAT IT ALLOWS, each by a stated rule, never silently:
  bare root        `/tmp` or `/private/tmp` named alone (prose, a list of temp
                   roots, a fallback default) with no fixed name attached;
  ephemeral        a per-process name (`$$`, `XXXXXX`, `$BASHPID`, `$RANDOM`)
                   inside the same path word as the match;
  runner           a temp path in `.github/workflows/`: a runner is a fresh VM
                   per job, so its /tmp dies with the job by construction;
  lease            exactly `/tmp/hpo-gate.lock`, the shared gate lease
                   `.claude/rules/gate-scoping.md` defines, with nothing appended;
  state            `$HOME/.local/state/hpo`, the documented state root the seat
                   tools default to (seat_venv.sh), outside every temp dir;
  cloud            `/home/user/heatpump_optimizer` and `/home/user/wt/`, the
                   fixed roots of the cloud seat image (cloud-setup.sh);
  ALLOW below      an exact (file, text) pair with its reason. An entry that
                   matches no hit is itself refused, so the list cannot rot into
                   a blanket exemption.

WHAT IT DOES NOT CATCH, so a green run is not read as more than it is: a path
assembled across lines (a root in one variable, its name added later); one
built from pieces that never spell a root (`"/" + "tmp"`, `chr()`, a `printf`
format); a temp root reached through a variable not named TMPDIR; one read from
a config file or the environment at run time; and any path in a file outside
the scope above. It detects the literal shapes that broke on 2026-10-03 and the
gaming shapes #1879's two review rounds measured. It is not a proof, and review
owns the rest (`fix-review.md` step 9).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SELF = "tools/audit/seat/tmp_paths.py"

CLASSES = (
    ("private-tmp", re.compile(r"/private/tmp(?![\w-])")),
    ("tmp", re.compile(r"(?<![\w}\-:./])/tmp(?![\w-])")),
    # The temp dir by its variable or its API, followed by a FIXED name: a path
    # component, a concatenation or an os.path.join argument.
    ("tmpdir-fixed", re.compile(
        r"(?:\$\{TMPDIR(?::-[^}]*)?\}|\$TMPDIR\b|tempfile\.gettempdir\(\)|os\.environ(?:\.get)?\(\s*[\"']TMPDIR[\"'][^)]*\)"
        r"|os\.environ\[\s*[\"']TMPDIR[\"']\s*\])"
        r"(?=\s*(?:/|\+\s*[\"']|,\s*[\"']|\)\s*/\s*[\"']))")),
    ("home-abs", re.compile(r"/(?:Users|home)/[\w.-]+/")),
    ("home-instrument", re.compile(r"(?:~|\$HOME|\$\{HOME\})/[^\s'\"`)]*(?:\.(?:sh|py|mjs|js)\b|/bin\b)")),
)
TEMP_CLASSES = ("private-tmp", "tmp", "tmpdir-fixed")
EPHEMERAL = ("$$", "XXXXXX", "$BASHPID", "$RANDOM")
TOKEN_END = re.compile(r"[\s\"'`;,()\[\]]")

# (file, text the line must contain, reason). Exact and per file.
ALLOW = (
    (".claude/workflows/gh_comment.py", "/private/tmp/claude-501/heatpump-optimizer-orchestrator/out/sync-201.md",
     "the literal body path of the #541 defect, kept as the fixture the poster must refuse"),
    (".claude/workflows/gh_comment.py", '"/private/tmp/x/out/body.md"', "a fixture path the poster's self-test feeds it"),
    (".claude/workflows/gh_comment.py", 'in_shared_root("/tmp/body.md")', "the self-test arm refusing a body directly in /tmp"),
    ("tools/audit/app_comment.sh", "evidence: /private/tmp/x/review-", "a self-test fixture verdict's evidence line"),
    ("tools/audit/app_approve.sh", "evidence: /tmp/", "self-test fixtures of the evidence gate's path refusals"),
    ("tools/audit/app_approve.sh", "`/tmp/../`", "a comment on the dot-segment refusal"),
    ("tools/audit/app_approve.sh", "REFUSE: /tmp/../", "a self-test arm's name"),
    ("tools/audit/prepr.sh", "shared_root /tmp/body.md", "the self-test arm refusing a body directly in /tmp"),
    ("tools/audit/prepr.sh", "grep -v 'codeowners_gap.py --check >/tmp/prepr-owners'",
     "a self-test deleting the owners step by its text, whose temp name carries $$ on the step's own line"),
    ("tools/audit/worktree_gc.sh", "/tmp/hpo-orch", "the seats' scratch root: worktrees that are meant to die, which this tool collects"),
    ("tests/card.mjs", "/tmp/plandata.json", "the legacy payload path the card accepts only as a loud last resort"),
    ("tests/entities.py", "> /tmp/pr-reds.txt", "pins pr-contract.yml's runner-side derivation by its text"),
    ("tests/entities.py", "/tmp/pr-reds.txt` fail-closed", "the docstring of that pin"),
    ("tests/entities.py", "`gh api ... | jq ... > /tmp/pr-reds.txt`", "the comment over that pin"),
    ("tests/entities.py", '"HPO_PLANDATA": "/tmp/plandata"', "a fixture environment for the plan-data path check"),
    ("tests/stress.py", "> /tmp/memory-half.json", "a comment showing a one-off command's output file"),
    ("tests/doc_claims.py", 'pathlib.Path(tempfile.gettempdir()) / "no-such-build.mjs"',
     "a fixture path that must NOT exist: the check drives a missing site builder"),
    ("tests/ha_floor.py", 'default=Path(tempfile.gettempdir()) / "ha-floor-cache"',
     "a disposable download cache, overridable by --cache; losing it costs a re-download, not state"),
    (".claude/workflows/friction_issues.mjs", "process.env.RUNNER_TEMP ?? '/tmp'}/friction-issue-body.md",
     "a workflow program: RUNNER_TEMP is set on the runner; /tmp is a one-shot body's local fallback"),
    ("tests/plan_view.py", '"/tmp", "plandata-%s.json" % hashlib.sha256',
     "the plan payload named per checkout by a hash, overridable by HPO_PLANDATA (tools/audit/README.md)"),
    (SELF, "", "this file names every class in its own patterns, docstring and fixtures"),
)


def scope(path: str) -> bool:
    if re.match(r"tools/audit/(?:round\d+|handoff|w5-[^/]*)/", path):
        return False
    return bool(re.match(r"\.github/workflows/[^/]+\.ya?ml$", path)
                or re.match(r"docs/decisions/[^/]+\.md$", path)
                or re.match(r"(?:tools|tests|\.claude)/.*\.(?:sh|py|mjs|js|cjs)$", path)
                or re.match(r"tools/audit/seat/shims/", path)
                or path == ".claude/settings.json")


def token(text: str, m: re.Match) -> str:
    """The match through the end of its path word: what a per-process marker must be IN."""
    end = TOKEN_END.search(text, m.end())
    return text[m.start(): end.start() if end else len(text)]


def bare_root_used(text: str, m: re.Match) -> bool:
    """A bare /tmp or /private/tmp that a fixed name is attached to on the same line:
    joined with a literal that is not itself a root, concatenated, closing a
    `${X ?? '/tmp'}/name` fallback, or assigned to a variable for later use."""
    rest = text[m.end():]
    return bool(re.match(r"/?[\"'`]?\s*(?:\+\s*[\"'`]|,\s*[\"'`](?!/))", rest)
                or re.match(r"[\"'`]\s*\}\s*/[\w.-]", rest)
                or re.match(r"[\"'`]\s*\)\s*/\s*[\"'`]", rest)
                or re.search(r"[\w}]=\s*[\"'`]?$", text[:m.start()]))


def allowed_by_rule(path: str, cls: str, text: str, m: re.Match) -> bool:
    """Each match is judged on its own, never by what else its line carries."""
    tok = token(text, m)
    if cls in ("tmp", "private-tmp") and not re.match(r"/[\w.${-]", text[m.end():]) and not bare_root_used(text, m):
        return True  # the root itself, named in prose or a list of roots, gets no fixed name here
    if cls in TEMP_CLASSES and any(e in tok for e in EPHEMERAL):
        return True
    if cls in TEMP_CLASSES and path.startswith(".github/workflows/"):
        return True
    if cls == "tmp" and tok.rstrip(".:") == "/tmp/hpo-gate.lock" and not re.match(r"[\"'`]?\s*\+", text[m.start() + len(tok):]):
        return True
    if cls == "home-instrument" and ".local/state/hpo" in m.group(0):
        return True
    if cls == "home-abs" and re.match(r"/home/user/(?:heatpump_optimizer\b|wt/)", text[m.start():]):
        return True
    return False


def classify(lines: list[tuple[str, int, str]], allow=ALLOW) -> tuple[list[str], list[str]]:
    """(refusals, stale allow entries) for (path, line, text) hits."""
    used = set()
    bad = []
    for path, n, text in lines:
        if not scope(path):
            continue
        for cls, rx in CLASSES:
            if all(allowed_by_rule(path, cls, text, m) for m in rx.finditer(text)):
                continue  # no match, or every match excused by a rule
            hit = [i for i, (f, t, _) in enumerate(allow) if f == path and t in text]
            if hit:
                used.update(hit)
                continue
            bad.append(f"{path}:{n}: [{cls}] {text.strip()[:140]}")
    stale = [f"{f}: {t!r} ({why})" for i, (f, t, why) in enumerate(allow) if i not in used]
    return bad, stale


def grep(ref: str) -> list[tuple[str, int, str]]:
    r = subprocess.run(
        ["git", "grep", "-n", "-I", "-E", r"/tmp|/Users/|/home/|~/|\$HOME/|\$\{HOME\}/|TMPDIR|gettempdir", ref, "--",
         ".github/workflows", "docs/decisions", "tools", "tests", ".claude"],
        cwd=ROOT, capture_output=True, text=True)
    if r.returncode not in (0, 1):
        raise SystemExit(f"tmp_paths: git grep failed: {r.stderr.strip()}")
    out = []
    for line in r.stdout.splitlines():
        _, path, n, text = line.split(":", 3)  # "<ref>:<path>:<n>:<text>"
        out.append((path, int(n), text))
    return out


def self_test() -> int:
    passed = failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + cond, failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    def one(path: str, text: str, allow=()) -> list[str]:
        return classify([(path, 1, text)], allow)[0]

    s = "tools/audit/seat/x.sh"
    check("a state dir under /private/tmp is refused", one(s, "S=/private/tmp/audit-7/ci-watch-state") != [])
    check("a fixed /tmp state name is refused", one(s, "KEEP=/tmp/hpo-ev") != [])
    check("a home path is refused", one(s, "cd /Users/someone/heatpump_optimizer") != [])
    check("an instrument run from ~ is refused", one(s, "bash ~/hpo-seats/bin/mergewhen.sh 1 2") != [])
    check("an instrument run from $HOME is refused", one(s, 'export PATH=$HOME/hpo-seats/bin:$PATH') != [])
    check("a decision record citing /private/tmp is refused",
          one("docs/decisions/0012-x.md", "(`/private/tmp/audit-7/r8prog/design.md`)") != [])
    check("a workflow invoking a ~/ instrument is refused", one(".github/workflows/x.yml", "run: bash ~/tools/x.sh") != [])
    check("a repo-relative path passes (null control)", one(s, "bash tools/audit/seat/remerge_main.sh") == [])
    check("a $TMPDIR default passes", one(s, 'f="${TMPDIR:-/tmp}/body_push.$$"') == [])
    check("a per-process temp name passes", one(s, "x >/tmp/prepr-policy.$$ 2>&1") == [])
    check("a runner's /tmp in a workflow passes", one(".github/workflows/x.yml", "> /tmp/pr-body.md") == [])
    check("the gate lease passes", one("tests/x.py", 'LOCK = "/tmp/hpo-gate.lock"') == [])
    check("the lease does not excuse another /tmp name on its line",
          one("tests/x.py", "/tmp/hpo-gate.lock and /tmp/state") != [])
    check("the state root passes", one(s, 'exec "${HPO_STATE_DIR:-$HOME/.local/state/hpo}/venv-ci/bin/python3"') == [])
    check("the cloud checkout root passes", one(s, "REPO=${HPO_REPO:-/home/user/heatpump_optimizer}") == [])
    check("round evidence is out of scope", one("tools/audit/round9/D1/x.py", "/private/tmp/audit-7/x") == [])
    allow = ((s, "/tmp/fixture", "why"),)
    check("an allow entry excuses only its own file", one(s, "/tmp/fixture", allow) == []
          and one("tools/audit/seat/y.sh", "/tmp/fixture", allow) != [])
    check("an allow entry that matches nothing is reported stale",
          classify([(s, 1, "nothing here")], allow)[1] != [] and classify([(s, 1, "/tmp/fixture")], allow)[1] == [])
    # The gaming shapes of #1879's round-1 review (attack/tpgame.py), each a refusal.
    for name, f, t in (
            ("an env default to /tmp with a fixed name", s, "S=${TMPDIR:-/tmp}/audit-7/ci-watch-state"),
            ("$TMPDIR with a fixed name", s, "S=$TMPDIR/audit-7"),
            ("a variable holding /private/tmp", s, "T=/private/tmp; S=$T/audit-7/state"),
            ("os.path.join over /tmp", "tools/x.py", 'S = os.path.join("/tmp", "audit-7", "state")'),
            ("tempfile.gettempdir() plus a fixed name", "tools/x.py", 'S = tempfile.gettempdir() + "/audit-7"'),
            ("os.path.join over gettempdir()", "tools/x.py", 'S = os.path.join(tempfile.gettempdir(), "audit-7")'),
            ("a concatenation", "tools/x.py", 'S = "/private" + "/tmp/" + "audit-7"'),
            ("$$ elsewhere on the line", s, "S=/private/tmp/audit-7/state; L=/tmp/lock.$$"),
            ("$$ in a comment", s, "S=/private/tmp/audit-7/state  # not $$"),
            ("the lease name with a suffix concatenated", "tests/x.py", 'LOCK = "/tmp/hpo-gate.lock" + "/../audit-7"'),
            ("/home/user outside the cloud checkout", s, "S=/home/user/state-that-dies"),
            ("pathlib's / over Path(\"/tmp\")", "tools/x.py", 'S = Path("/tmp") / "audit-7"'),
            ("an f-string under /tmp", "tools/x.py", 'S = f"/tmp/{name}"'),
            ("os.environ[\"TMPDIR\"] plus a fixed name", "tools/x.py", 'S = os.environ["TMPDIR"] + "/audit-7"'),
            ("pathlib's / over gettempdir()", "tools/x.py", 'S = Path(tempfile.gettempdir()) / "audit-7"'),
            ("a hook command in settings.json", ".claude/settings.json", '"command": "bash /tmp/hook.sh"')):
        check(f"refused: {name}", one(f, t) != [])
    check("an env default with a per-process name passes", one(s, 'mktemp -d "${TMPDIR:-/tmp}/app_approve.XXXXXX"') == [])
    check("a bare $TMPDIR handed to mktemp passes", one(s, 'mktemp -p "${TMPDIR:-/tmp}"') == [])
    check("a list of temp roots passes", one("tools/x.py", 'ROOTS = ("/tmp", "/private/tmp", "/var/tmp")') == [])
    check("prose naming /tmp passes", one("tests/x.py", "# it used to sit in /tmp and vanish on reboot.") == [])
    check("a TMPDIR fallback to the bare root passes", one("tests/x.py", 'tmp = Path(os.environ.get("TMPDIR", "/tmp"))') == [])
    check("refused: a fixed name after a `?? '/tmp'` fallback", one("tools/x.mjs", "f(`${process.env.X ?? '/tmp'}/body.md`)") != [])
    check("the cloud worktree root passes", one(s, "git worktree add /home/user/wt/${branch}") == [])
    print(f"tmp_paths self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    if argv[:1] != ["--check"]:
        print(__doc__)
        return 2
    ref = argv[argv.index("--ref") + 1] if "--ref" in argv else "HEAD"
    bad, stale = classify(grep(ref))
    for b in bad:
        print("REFUSE", b)
    for s in stale:
        print("STALE ALLOW", s)
    print(f"tmp_paths: {len(bad)} refused, {len(stale)} stale allow entr{'y' if len(stale) == 1 else 'ies'} at {ref}")
    return 1 if bad or stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
