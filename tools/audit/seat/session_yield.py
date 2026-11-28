#!/usr/bin/env python3
"""session_yield.py -- what the seats' transcripts say about rules, instruments and workflows.

    python3 -I tools/audit/seat/session_yield.py --projects DIR [--projects DIR ...]
                                                  [--cloud-projects DIR ...] [--since ISO] [--until ISO]
                                                  [--repo DIR]
    python3 -I tools/audit/seat/session_yield.py --self-test

WHY (R11-NO-READ-BUILDERS-C: part C of the approved R11-PRE-NO-READ-BUILDERS
design, note 9edf64948f section C; decision 0018 section 3): three objects
were NO-READ because nothing counted them. Card E11-N-RULE-YIELD: a rule's
loads. Card E11-N-INSTRUMENT-YIELD: an instrument's refusals with what
followed. Card E11-N-GATE-CAUSE: a run line per `.claude/workflows/` script.
All three are in the transcripts the token ledger already walks, so this reads
them through `token_ledger.sessions()` (each session's own transcript and its
subagent transcripts) and writes nothing.

THE SHAPES, measured in a seat transcript (the measurement is the self-test's
fixture lines):
  a rule load      an `attachment` line of type `nested_memory` whose path is
                   `.claude/rules/<rule>.md` (a Read of a file the rule's
                   globs match writes one; a Bash `sed` of it writes none);
  a Bash exit      the `tool_result` of a Bash `tool_use`: `is_error` with the
                   text `Exit code N` first, else exit 0;
  a hook denial    a `tool_result` with `is_error` whose text begins
                   `PreToolUse:` and names `hook error`, then `<name>:`.

LOADS. `load <rule> <n>` for every tracked `.claude/rules/*.md`, 0 included,
so a rule nothing loaded prints 0 rather than vanishing.

REFUSALS, by exit status, never by wording (note [P1]: the wording is not
uniform enough to be the predicate). An instrument is a tracked file under
`tools/` or `.claude/hooks/` named as a word of a Bash call's simple command.
A call is attributed only when its LAST simple command names the instrument;
any other call naming one prints `masked` (`| tail`, `; echo`, `|| true`),
never a refusal or a zero. A refusal is an attributed non-zero exit, or a hook
denial, less these structural rows, each counted and never dropped:
  not-run   126, 127;
  killed    124, above 128;
  deferred  75 (EX_TEMPFAIL), and each wait code its instrument declares
            (WAIT_CODES, note [c-deferred]);
  crash     the output holds `Traceback (most recent call last):`;
  usage     exit 2 whose first output line begins `usage:` (argparse's form),
            so exit 2 is a refusal unless it is that form.
A call whose exit cannot be read (a background run, an error with no exit
line) is the scope row `unread`. Exit 0 with a marker line (first token,
after an optional prefix up to its first colon, `REFUSE[DS]?`) is no refusal,
the instrument let the run pass: it is the scope row `marked at exit 0`, so a
report-only instrument shows rather than reads 0. No instrument is
classified by its text, and none is edited by this reader.

OUTCOME, from the next attributed run of the same instrument in the same
transcript file (a subagent's refusal is read within its own file):
  override  that run, or a `git push` after the refusal and before it, carries
            an OVERRIDES token;
  fix       that run exits 0 and an Edit, Write or `git commit` came between;
  nothing   otherwise, the instrument never run again included.

WORKFLOWS. `workflow <script> <UTC> <status>` per Workflow tool call: the
script is the call's `name`, its `scriptPath`'s file name, or its inline
script's `meta` name; the status is the `<status>` of a `<task-notification>`
whose `<tool-use-id>` is the call's (measured: it lands as a `queued_command`
attachment), `error` for a refused call, or `unnotified`.

THE CLASSES. `--projects` dirs are the host's (local), `--cloud-projects` a
cloud seat's own; a class given no dir prints NO-READ beside its counts, never
0 (a cloud transcript lives only in its container; token_ledger.py, THE
CLASS).
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import re
import shlex
import subprocess
import sys
import tempfile
from itertools import dropwhile
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("token_ledger", HERE / "token_ledger.py")
token_ledger = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(token_ledger)

CLASSES = ("local", "cloud")
INSTRUMENT_DIRS = ("tools/", ".claude/hooks/")
RULES_DIR = ".claude/rules/"
# Each instrument's own declared wait code, enumerated by
# `git grep -n -E "WAIT|return 75|exit 75" -- tools .claude/hooks` at a59a1b0d9a and
# read against each instrument's page: merge_pr.sh's WAIT-EXHAUSTED (exit 3), merge_train
# classify's WAIT (rc 3), record_row --automerge-check's "required check not yet" (exit 3),
# toolchain promote's PROMOTE-HELD (exit 3). 75 is every instrument's (DEFERRED_ALL).
DEFERRED_ALL = frozenset({75})
WAIT_CODES = {
    "tools/audit/seat/merge_pr.sh": frozenset({3}),
    "tools/audit/seat/merge_train.py": frozenset({3}),
    "tools/audit/seat/record_row.py": frozenset({3}),
    "tools/audit/seat/toolchain.py": frozenset({3}),
}
# Seeded by `git grep -n -E "ALLOW_|--force|--no-verify" -- .claude/hooks tools/pr` (it prints
# only worktree-cleanup `--force`s at a59a1b0d9a), so the list is the seed's three forms:
# an `ALLOW_` word (HPO_ALLOW_STALE_TOOLS, FRUGAL_ALLOW_INLINE), `--force*`, `--no-verify`.
OVERRIDES = re.compile(r"(?:^|[^\w-])(?:\w*ALLOW_\w+|--force[\w-]*|--no-verify)(?![\w-])")
ASSIGN = re.compile(r"\A[A-Za-z_]\w*=")
WRAPPERS = {"env", "timeout", "nice", "exec", "time", "command", "nohup", "stdbuf"}
INTERPRETERS = r"(?:python[\d.]*|bash|sh|zsh|node)"
EXIT = re.compile(r"\AExit code (-?\d+)\s*\n?")
HOOK = re.compile(r"\APreToolUse:(\S+) hook error: (?:\[[^\]]*\]: )?([\w.-]+):")
MARKER = re.compile(r"^\s*(?:[^:\n]*:\s*)?REFUSE[DS]?\b", re.M)
REFUS = re.compile(r"(?i)refus")
TRACEBACK = "Traceback (most recent call last):"
SEPARATORS = {";", "&&", "||", "|", "&", "\n", "|&", ";;"}
EDITS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
STRUCTURAL = ("usage", "crash", "not-run", "killed", "deferred", "unread", "masked", "marked at exit 0")
NOTIFIED = re.compile(r"<task-notification>(?:(?!</task-notification>).)*?<tool-use-id>([\w-]+)</tool-use-id>"
                      r"(?:(?!</task-notification>).)*?<status>([\w-]+)</status>", re.S)


class Refusal(Exception):
    pass


def tracked(repo: Path) -> set[str]:
    p = subprocess.run(["git", "-C", str(repo), "ls-files", "-z", "--", "tools", ".claude/hooks", ".claude/rules"],
                       capture_output=True, text=True, check=False)
    if p.returncode != 0:
        raise Refusal(f"{repo} is no git checkout: {p.stderr.strip()[:200]}")
    return set(filter(None, p.stdout.split("\0")))


def simple_commands(cmd: str) -> list[list[str]]:
    """The words of each simple command of a Bash call, in order; `2>&1`'s `&` is no separator."""
    try:
        lex = shlex.shlex(cmd, posix=True, punctuation_chars=";&|\n")
        lex.whitespace, lex.whitespace_split = " \t\r", True
        toks = list(lex)
    except ValueError:  # an unbalanced quote or a heredoc body: split on the separators alone
        toks = [t for t in re.split(r"(;|&&|\|\||\||\n)|\s+", cmd) if t]
    out, cur, prev = [], [], ""
    for t in toks:
        if t in SEPARATORS and not (t == "&" and prev.endswith((">", "<"))):
            if cur:
                out.append(cur)
            cur = []
        elif not t.startswith("&") or not prev.endswith((">", "<")):
            cur.append(t)
        prev = t
    if cur:
        out.append(cur)
    return out


def instrument_of(words: list[str], files: set[str]) -> str | None:
    """The tracked file a simple command EXECUTES: its command word, or an interpreter's script
    argument, past leading assignments and wrappers; a path read as an argument (`sed`, `cat`,
    `grep`) is no run of it."""
    w = list(dropwhile(ASSIGN.match, words))
    while w and Path(w[0]).name in WRAPPERS:
        w = w[1:]
        while w and (w[0].startswith("-") or w[0].replace(".", "").isdigit()):
            w = w[1:]
    if w and re.fullmatch(INTERPRETERS, Path(w[0]).name):
        args = list(dropwhile(lambda x: x.startswith("-") and x not in ("-", "-c", "-m"), w[1:]))
        w = [] if not args or args[0] in ("-", "-c", "-m") else args[:1]
    if not w:
        return None
    x = "/" + w[0].removeprefix("./")
    for d in INSTRUMENT_DIRS:
        i = x.rfind("/" + d)
        if i >= 0 and x[i + 1:] in files:
            return x[i + 1:]


def _text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
    return ""


def classify(rc: int, out: str, instrument: str) -> str:
    """The structural row of a non-zero attributed exit, or `refusal`."""
    if rc in (126, 127):
        return "not-run"
    if rc == 124 or rc > 128 or rc < 0:
        return "killed"
    if rc in DEFERRED_ALL or rc in WAIT_CODES.get(instrument, ()):
        return "deferred"
    if TRACEBACK in out:
        return "crash"
    if rc == 2 and out.lstrip("\n").startswith("usage:"):
        return "usage"
    return "refusal"


def read_file(path: Path, files: set[str], since: str = "", until: str = "") -> dict:
    """One transcript file's loads, calls (in order), and workflow runs."""
    loads: collections.Counter = collections.Counter()
    uses: dict = {}
    events: list[dict] = []  # each: kind run|edit|push, with its fields, in file order
    workflows: list[dict] = []
    notified: dict = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            try:
                o = json.loads(ln)
            except ValueError:
                continue
            if not isinstance(o, dict):
                continue
            notified.update(NOTIFIED.findall(ln))
            stamp = str(o.get("timestamp") or "")
            a = o.get("attachment")
            if o.get("type") == "attachment" and isinstance(a, dict) and a.get("type") == "nested_memory":
                p = str(a.get("displayPath") or a.get("path") or "")
                i = p.rfind(RULES_DIR)
                if i >= 0 and (since <= stamp or not stamp) and (not until or stamp < until):
                    loads[p[i:]] += 1
                continue
            m = o.get("message")
            if not isinstance(m, dict) or not isinstance(m.get("content"), list):
                continue
            for b in m["content"]:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use":
                    uses[b.get("id")] = (b, stamp)
                    continue
                if b.get("type") != "tool_result" or b.get("tool_use_id") not in uses:
                    continue
                use, t = uses.pop(b["tool_use_id"])
                if not (since <= t and (not until or t < until)):
                    continue
                name, inp, text = use.get("name"), use.get("input") or {}, _text(b.get("content"))
                err = bool(b.get("is_error"))
                if name == "Workflow":
                    script = (inp.get("name") or Path(str(inp.get("scriptPath") or "")).name
                              or (re.search(r"""\bname:\s*['"]([^'"]+)""", str(inp.get("script") or "")) or [None, "-"])[1])
                    workflows.append({"script": script or "-", "t": t, "id": b["tool_use_id"],
                                      "status": "error" if err else "unnotified"})
                    continue
                hook = HOOK.match(text) if err else None
                if hook:
                    h = f".claude/hooks/{hook.group(2)}.sh"
                    events.append({"kind": "run", "instrument": h if h in files else f"hook:{hook.group(2)}",
                                   "row": "refusal", "rc": "hook", "t": t, "cmd": "", "out": text})
                    continue
                if name in EDITS:
                    events.append({"kind": "edit"})
                    continue
                if name != "Bash":
                    continue
                cmd = str(inp.get("command") or "")
                cmds = simple_commands(cmd)
                bare = [list(dropwhile(ASSIGN.match, w)) for w in cmds]
                if any(w[:2] == ["git", "commit"] or (w[:1] == ["git"] and "commit" in w[1:3]) for w in bare):
                    events.append({"kind": "edit"})
                if any(w[:1] == ["git"] and "push" in w[1:4] for w in bare):
                    events.append({"kind": "push", "cmd": cmd})
                named = [instrument_of(w, files) for w in cmds]
                if not any(named):
                    continue
                last = named[-1]
                ev = {"kind": "run", "instrument": last or next(n for n in named if n), "t": t, "cmd": cmd}
                if not last:
                    ev["row"] = "masked"
                elif inp.get("run_in_background"):
                    ev["row"] = "unread"
                else:
                    em = EXIT.match(text) if err else None
                    if err and not em:
                        ev["row"] = "unread"
                    else:
                        rc, out = (int(em.group(1)), text[em.end():]) if em else (0, text)
                        ev |= {"rc": rc, "out": out}
                        ev["row"] = (classify(rc, out, last) if rc else
                                     ("marked at exit 0" if MARKER.search(out) else "pass"))
                events.append(ev)
    for w in workflows:
        if w["status"] != "error":
            w["status"] = notified.get(w["id"], w["status"])
    return {"loads": loads, "events": events, "workflows": workflows}


def outcomes(events: list[dict]) -> list[dict]:
    """Each refusal row with its outcome, read from the next attributed run of its instrument."""
    rows = []
    for i, ev in enumerate(events):
        if ev["kind"] != "run" or ev["row"] != "refusal":
            continue
        edited, pushes, nxt = False, [], None
        for later in events[i + 1:]:
            if later["kind"] == "edit":
                edited = True
            elif later["kind"] == "push":
                pushes.append(later["cmd"])
            elif later["instrument"] == ev["instrument"] and later["row"] != "masked":
                nxt = later
                break
        if (nxt and OVERRIDES.search(nxt["cmd"])) or any(OVERRIDES.search(c) for c in pushes):
            outcome = "override"
        elif nxt and nxt.get("rc") == 0 and edited:
            outcome = "fix"
        else:
            outcome = "nothing"
        first = next((x for x in ev["out"].splitlines() if REFUS.search(x)), "-")
        rows.append(ev | {"outcome": outcome, "line": first.strip()[:160]})
    return rows


def report(projects: dict[str, list[Path]], repo: Path, since: str = "", until: str = "") -> list[str]:
    files = tracked(repo)
    rules = sorted(f for f in files if f.startswith(RULES_DIR) and f.endswith(".md"))
    loads: collections.Counter = collections.Counter(dict.fromkeys(rules, 0))
    counts = {c: {"sessions": 0, "subagents": 0} for c in CLASSES}
    scope: collections.Counter = collections.Counter()
    refusals, workflows = [], []
    for cls in CLASSES:
        for proj in projects.get(cls) or ():
            for sid, main, subs in token_ledger.sessions(proj):
                counts[cls]["sessions"] += 1
                counts[cls]["subagents"] += len(subs)
                for path in [main, *subs]:
                    got = read_file(path, files, since, until)
                    loads.update(got["loads"])
                    where = sid if path == main else f"{sid}/{path.stem}"
                    for ev in got["events"]:
                        if ev["kind"] == "run" and ev["row"] in STRUCTURAL:
                            scope[ev["row"]] += 1
                    refusals += [r | {"cls": cls, "file": where} for r in outcomes(got["events"])]
                    workflows += [w | {"cls": cls} for w in got["workflows"]]
    read = {c: bool(projects.get(c)) for c in CLASSES}

    def per(k: str) -> str:
        return ", ".join(f"{c} {counts[c][k] if read[c] else 'NO-READ'}" for c in CLASSES)
    lines = [f"sessions read {per('sessions')}", f"subagent files read {per('subagents')}"]
    lines += [f"load {r} {n}" for r, n in sorted(loads.items())]
    oc = collections.Counter(r["outcome"] for r in refusals)
    lines.append(f"refusals {len(refusals)} (fix {oc['fix']}, override {oc['override']}, nothing {oc['nothing']})")
    lines += [f"refusal {r['instrument']} rc={r['rc']} outcome={r['outcome']} {r['cls']} {r['file']} {r['t']} {r['line']}"
              for r in refusals]
    lines += [f"scope {k} {scope[k]}" for k in STRUCTURAL]
    lines.append(f"workflows {len(workflows)}")
    lines += [f"workflow {w['script']} {w['t']} {w['status']} {w['cls']}" for w in workflows]
    return lines


# ---------------------------------------------------------------- self-test

def _use(uid: str, tool: str, t: str, **inp) -> str:
    return json.dumps({"type": "assistant", "timestamp": t, "message": {"role": "assistant", "content": [
        {"type": "tool_use", "id": uid, "name": tool, "input": inp}]}}) + "\n"


def _res(uid: str, t: str, text, err: bool = False) -> str:
    return json.dumps({"type": "user", "timestamp": t, "message": {"role": "user", "content": [
        {"type": "tool_result", "content": text, "is_error": err, "tool_use_id": uid}]}}) + "\n"


def _bash(uid: str, t: str, cmd: str, rc: int, out: str, **kw) -> str:
    text = f"Exit code {rc}\n{out}" if rc else out
    return _use(uid, "Bash", t, command=cmd, **kw) + _res(uid, t, text, err=bool(rc))


def _load(t: str, rule: str) -> str:
    return json.dumps({"type": "attachment", "timestamp": t, "attachment": {
        "type": "nested_memory", "path": f"/home/x/repo/.claude/rules/{rule}",
        "displayPath": f".claude/rules/{rule}", "content": "..."}}) + "\n"


def self_test() -> int:
    passed = failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + bool(cond), failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    T = "2026-11-28T10:00:{:02d}Z".format
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        for f in ("tools/pr/prepr.sh", "tools/pr/app_push.sh", "tools/pr/push.sh", "tools/audit/seat/bus.sh",
                  "tools/audit/seat/merge_pr.sh", "tools/audit/seat/x.py", ".claude/hooks/pre-bash.sh",
                  ".claude/rules/gate-scoping.md", ".claude/rules/claim-files.md"):
            (repo / f).parent.mkdir(parents=True, exist_ok=True)
            (repo / f).write_text("x\n")
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        files = tracked(repo)

        check("simple commands: `2>&1` is no separator, `|`, `&&`, `;` and a newline are",
              [w[0] for w in simple_commands("cd /x && bash tools/pr/prepr.sh 2>&1 | tail -3\necho ok; ls")]
              == ["cd", "bash", "tail", "echo", "ls"])
        check("an instrument is a tracked file, by relative, ./ or absolute path; an untracked one is none",
              instrument_of(["python3", "-I", "/root/wt/tools/audit/seat/x.py"], files) == "tools/audit/seat/x.py"
              and instrument_of(["./tools/pr/push.sh"], files) == "tools/pr/push.sh"
              and instrument_of(["python3", "tools/audit/seat/nope.py"], files) is None)
        check("a run is the command word or an interpreter's script, past assignments and wrappers; a file "
              "read as an argument is no run of it",
              instrument_of(["A=1", "timeout", "5", "bash", "-e", "tools/pr/push.sh"], files) == "tools/pr/push.sh"
              and instrument_of(["sed", "-n", "1,5p", "tools/pr/push.sh"], files) is None
              and instrument_of(["python3", "-", "tools/pr/push.sh"], files) is None
              and instrument_of(["nohup", "tools/pr/push.sh"], files) == "tools/pr/push.sh")
        check("a quoted instrument path is the path; an unbalanced quote falls back to the separators",
              [instrument_of(w, files) for w in simple_commands('bash "tools/pr/push.sh" && echo')]
              == ["tools/pr/push.sh", None]
              and [w[:2] for w in simple_commands("bash tools/pr/push.sh 'x; ls")] == [["bash", "tools/pr/push.sh"], ["ls"]])
        check("every instrument's declared wait code is deferred, and only there",
              all(classify(3, "", f) == "deferred" for f in ("tools/audit/seat/merge_pr.sh",
                  "tools/audit/seat/merge_train.py", "tools/audit/seat/record_row.py", "tools/audit/seat/toolchain.py")))

        proj = Path(tmp) / "proj"
        (proj / "s1" / "subagents").mkdir(parents=True)
        (proj / "s1.jsonl").write_text(
            _load(T(0), "gate-scoping.md") + _load(T(0), "gate-scoping.md")
            # prepr --body-check exit 2 with `REFUSE pr-body`, an edit, then exit 0: fix
            + _bash("b1", T(1), "bash tools/pr/prepr.sh --body-check b.md", 2, "  REFUSE pr-body: no ## Figures\n")
            + _use("e1", "Edit", T(2), file_path="b.md") + _res("e1", T(2), "ok")
            + _bash("b2", T(3), "bash tools/pr/prepr.sh --body-check b.md", 0, "  ok pr-body\n")
            # [P1] app_push's die (exit 1), then a git push carrying an override token: override
            + _bash("b3", T(4), "bash tools/pr/app_push.sh", 1, "app_push: REFUSE: no pr_args.sh beside this script\n")
            + _bash("b4", T(5), "HPO_ALLOW_STALE_TOOLS=1 git push origin x", 0, "")
            # push.sh exit 2 with its column line (not argparse's form): a refusal, never re-run: nothing
            + _bash("b5", T(6), "tools/pr/push.sh", 2, "  REFUSE   no body at b.md\n")
            # bus.sh exit 1 whose wording has `refused` mid-line
            + _bash("b6", T(7), "bash tools/audit/seat/bus.sh post x", 1, "BUS refused post x: already posted\n")
            # ... re-run with nothing changed between and passing: a retry, not a fix
            + _bash("b6b", T(7), "bash tools/audit/seat/bus.sh post x", 0, "BUS posted x\n")
            # structural rows
            + _bash("b7", T(8), "python3 -I tools/audit/seat/x.py --bad", 2, "usage: x.py [-h]\nx.py: error: bad\n")
            + _bash("b8", T(9), "python3 -I tools/audit/seat/x.py", 1, "Traceback (most recent call last):\n  ...\n")
            + _bash("b9", T(10), "tools/audit/seat/x.py", 127, "not found\n")
            + _bash("b10", T(11), "timeout 5 python3 tools/audit/seat/x.py", 124, "")
            + _bash("b11", T(12), "python3 tools/audit/seat/x.py", 75, "x: BUSY\n")
            + _bash("b12", T(13), "bash tools/audit/seat/merge_pr.sh 5", 3, "WAIT-EXHAUSTED: classify still reads WAIT\n")
            + _bash("b13", T(14), "bash tools/pr/push.sh | tail -3", 1, "REFUSE x\n")
            + _use("b14", "Bash", T(15), command="python3 tools/audit/seat/x.py")
            + _res("b14", T(15), [{"type": "text", "text": "x: REFUSED 2 rows (report only)\n"}])
            + _bash("b15", T(16), "python3 tools/audit/seat/x.py", 0, "x: NOT REFUSED\n")
            + _bash("b16", T(17), "python3 tools/audit/seat/x.py", 0, "", run_in_background=True)
            # a hook denial is a refusal of the hook
            + _use("h1", "Bash", T(18), command="pkill -f x")
            + _res("h1", T(18), "PreToolUse:Bash hook error: [command hook 2]: pre-bash: `pkill` kills ...\n", True)
            # a Workflow call, its run id and its notification
            + _use("w1", "Workflow", T(19), script="export const meta = { name: 'review-changes', phases: [] }")
            + _res("w1", T(19), "Workflow started; a task-notification arrives when done")
            + json.dumps({"type": "attachment", "timestamp": T(30), "attachment": {
                "type": "queued_command", "prompt": "<task-notification>\n<task-id>t1</task-id>\n"
                "<tool-use-id>w1</tool-use-id>\n<status>completed</status>\n</task-notification>"}}) + "\n"
            + _use("w2", "Workflow", T(31), name="saved-flow") + _res("w2", T(31), "started")
            + "not json\n")
        (proj / "s1" / "subagents" / "agent-a1.jsonl").write_text(
            _load(T(20), "claim-files.md")
            + _bash("c1", T(21), "python3 -I tools/audit/seat/x.py --check", 1, "x: REFUSE: stale\n")
            + _bash("c2", T(22), "git commit -qam fix", 0, "")
            + _bash("c3", T(23), "python3 -I tools/audit/seat/x.py --check", 0, "x: ok\n"))
        lines = report({"local": [proj]}, repo)
        row = {ln.split(" rc=")[0].removeprefix("refusal "): ln for ln in lines if ln.startswith("refusal ")}
        check("sessions and subagent files read per class; the class given no dir prints NO-READ, never 0",
              lines[:2] == ["sessions read local 1, cloud NO-READ", "subagent files read local 1, cloud NO-READ"])
        check("loads per rule from nested_memory lines, subagent files included, a rule never loaded at 0",
              "load .claude/rules/gate-scoping.md 2" in lines and "load .claude/rules/claim-files.md 1" in lines)
        check("refusals by exit status: prepr exit 2, app_push 1, push.sh 2, bus.sh 1, the hook, the subagent's x.py",
              "refusals 6 (fix 2, override 1, nothing 3)" in lines)
        check("prepr's REFUSE pr-body, an Edit, then exit 0 reads fix",
              "outcome=fix" in row.get("tools/pr/prepr.sh", "") and "REFUSE pr-body" in row["tools/pr/prepr.sh"])
        check("app_push's REFUSE then a git push carrying an ALLOW_ token reads override",
              "outcome=override" in row.get("tools/pr/app_push.sh", ""))
        check("push.sh exit 2 in its column form is a refusal (not argparse's usage), never re-run: nothing",
              "rc=2 outcome=nothing" in row.get("tools/pr/push.sh", ""))
        check("bus.sh's `BUS refused` (no leading REFUSE) is a refusal by its exit, its line carried; re-run "
              "passing with no edit between, it reads nothing, not fix",
              "BUS refused post x" in row.get("tools/audit/seat/bus.sh", "")
              and "outcome=nothing" in row["tools/audit/seat/bus.sh"])
        check("a hook denial is the hook's refusal", "rc=hook" in row.get(".claude/hooks/pre-bash.sh", ""))
        check("a subagent's refusal is its own row, its outcome read in its own file (a git commit between: fix)",
              "outcome=fix local s1/agent-a1" in row.get("tools/audit/seat/x.py", ""))
        check("structural rows: usage, crash, not-run, killed, deferred (75 and merge_pr's declared 3), masked, "
              "marked at exit 0, unread (a background run)",
              all(f"scope {k} {n}" in lines for k, n in (("usage", 1), ("crash", 1), ("not-run", 1), ("killed", 1),
                                                          ("deferred", 2), ("masked", 1), ("marked at exit 0", 1),
                                                          ("unread", 1))))
        check("a Workflow call prints its script, time and notified status",
              f"workflow review-changes {T(19)} completed local" in lines and "workflows 2" in lines
              and f"workflow saved-flow {T(31)} unnotified local" in lines)
        check("--since past every event reads 0 refusals and 0 loads (the window's null control)",
              "refusals 0 (fix 0, override 0, nothing 0)" in report({"local": [proj]}, repo, since=T(59))
              and "load .claude/rules/gate-scoping.md 0" in report({"local": [proj]}, repo, since=T(59)))
        check("exit 3 is deferred only where the instrument declares it: from x.py it is a refusal",
              classify(3, "", "tools/audit/seat/x.py") == "refusal"
              and classify(3, "", "tools/audit/seat/merge_pr.sh") == "deferred")
        check("exit 2 is usage only in argparse's form", classify(2, "usage: x\n", "t") == "usage"
              and classify(2, "  REFUSE pr-body\n", "t") == "refusal")

        # the null control: a session whose instruments refused nothing logs nothing
        quiet = Path(tmp) / "quiet"
        quiet.mkdir()
        (quiet / "q.jsonl").write_text(
            _bash("q1", T(1), "python3 -I tools/audit/seat/x.py --self-test", 0, "x self-test: 3 passed, 0 failed\n")
            + _bash("q2", T(2), "echo REFUSE: not an instrument", 1, "REFUSE: not an instrument\n")
            + _bash("q3", T(3), "grep -n REFUSE tools/pr/push.sh", 0, "634: push.sh: REFUSE   no body\n")
            + _bash("q4", T(4), "sed -n 1p tools/pr/push.sh | false", 1, ""))
        ql = report({"local": [quiet], "cloud": [quiet]}, repo)
        check("null control: an instrument that passed and an untracked command's non-zero exit log 0 refusals",
              "refusals 0 (fix 0, override 0, nothing 0)" in ql and "scope masked 0" in ql and "scope marked at exit 0 0" in ql
              and ql[0] == "sessions read local 1, cloud 1")
        check("no stray refusal row in the quiet report", not any(x.startswith("refusal ") for x in ql))
        try:
            tracked(Path(tmp) / "nowhere")
            check("a --repo that is no checkout refuses", False)
        except Refusal:
            check("a --repo that is no checkout refuses", True)
    print(f"session_yield self-test: {passed} passed, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    ap = argparse.ArgumentParser(prog="session_yield.py")
    ap.add_argument("--projects", action="append", default=[], type=Path)
    ap.add_argument("--cloud-projects", action="append", default=[], type=Path)
    ap.add_argument("--since", default="")
    ap.add_argument("--until", default="")
    ap.add_argument("--repo", type=Path, default=HERE.parents[2])
    a = ap.parse_args(argv)
    try:
        dirs = a.projects + a.cloud_projects
        if not dirs:
            raise Refusal("no --projects or --cloud-projects directory given")
        missing = [str(p) for p in dirs if not p.is_dir()]
        if missing:
            raise Refusal(f"no project directory: {', '.join(missing)}")
        print("\n".join(report({"local": a.projects, "cloud": a.cloud_projects}, a.repo, a.since, a.until)))
    except Refusal as e:
        print(f"session_yield: REFUSED {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
