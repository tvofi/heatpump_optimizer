#!/usr/bin/env python3
"""Generated figure blocks for a pull-request body (owner's card 7, option B).

A body's `## Figures` may carry a block whose text is *rendered*, not typed:

    <!-- figure-block: scope-line mb=<40 hex> head=<40 hex> -->
    ~~~text
    <what the registered instrument printed>
    ~~~
    <!-- /figure-block -->

``figure_registry.json`` names the instruments a block may come from. It is read
from the BASE tree (``--base``), as ``.claude/workflows/*`` already is, so a pull
request can neither add an instrument nor choose a command and use it in the
same pull request: **the author chooses no command**, only a registered name.
Each registered instrument runs in a throwaway worktree of the head, with the
registry's ``files`` overlaid from the base, so the program is the base's and the
tree it measures is the head's.

    figure_block.py render NAME   [--base REF] [--head REF]   print one block
    figure_block.py refresh BODY  [--base REF] [--head REF]   re-render every block in place
    figure_block.py verify  BODY  [--base REF] [--head REF]   refuse a block that is not what the
                                                               registry renders (read-only)
    figure_block.py --self-test

``refresh`` is the seat-side writer (``body_push.sh``, ``prepr.sh``): a body
carries an empty marker and the writer fills it at the head with no agent turn.
``verify`` (``pr-contract``) renders and compares; it writes nothing. Only a
*registered* figure is structurally non-stale: a free-form figure under
``## Figures`` stays as it was, well-formed and resolvable, never executed.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

REGISTRY = "tools/pr/figure_registry.json"
OPEN_RE = re.compile(r"^<!-- figure-block: (?P<name>[a-z][a-z0-9-]*)(?P<attrs>(?: [a-z]+=[0-9a-f]{40})*) -->$")
CLOSE = "<!-- /figure-block -->"
FENCE = "~~~text"
FENCE_END = "~~~"
PLACEHOLDERS = ("mb", "head", "base", "workdir")


class Refused(Exception):
    pass


def _git(root: str, *args: str) -> str:
    p = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, check=False)
    if p.returncode:
        raise Refused(f"git {' '.join(args)}: {p.stderr.strip() or 'failed'}")
    return p.stdout.strip()


def load_registry(root: str, base: str) -> dict:
    """The registry as the BASE tree holds it; a base without one registers nothing."""
    p = subprocess.run(["git", "-C", root, "show", f"{base}:{REGISTRY}"], capture_output=True, text=True, check=False)
    if p.returncode:
        return {}
    data = json.loads(p.stdout)
    return data.get("instruments", {})


def parse(text: str):
    """Yield (start, end, name, attrs, body) per block; line indexes are [start, end]."""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        m = OPEN_RE.match(lines[i])
        if not m:
            if lines[i].startswith("<!-- figure-block"):
                raise Refused(f"line {i + 1}: a figure-block marker that does not parse: {lines[i][:80]!r}")
            i += 1
            continue
        j = i + 1
        while j < len(lines) and lines[j] != CLOSE:
            if lines[j].startswith("<!-- figure-block"):
                raise Refused(f"line {j + 1}: a figure-block opens inside another")
            j += 1
        if j >= len(lines):
            raise Refused(f"line {i + 1}: figure-block {m['name']} is never closed")
        attrs = dict(a.split("=") for a in m["attrs"].split())
        out.append((i, j, m["name"], attrs, lines[i + 1:j]))
        i = j + 1
    return lines, out


def render_text(name: str, attrs: dict, output: str) -> list[str]:
    a = "".join(f" {k}={attrs[k]}" for k in ("mb", "head") if k in attrs)
    return [f"<!-- figure-block: {name}{a} -->", FENCE, *output.rstrip("\n").split("\n"), FENCE_END, CLOSE]


def run_instrument(root: str, base: str, head: str, mb: str, name: str, reg: dict) -> str:
    """Run one registered instrument over the head's tree with the base's program."""
    if name not in reg:
        raise Refused(f"`{name}` is not in the registry at {base[:12]}:{REGISTRY} "
                      f"({', '.join(sorted(reg)) or 'it registers nothing'}); a pull request cannot add an instrument and use it")
    ent = reg[name]
    tmp = tempfile.mkdtemp(prefix="figblock-")
    wt = os.path.join(tmp, "wt")
    workdir = os.path.join(tmp, "work")
    os.mkdir(workdir)
    try:
        _git(root, "worktree", "add", "--detach", "-q", wt, head)
        for f in ent.get("files", []):
            _git(wt, "checkout", base, "--", f)  # the base's program, not the head's
        sub = dict(mb=mb, head=head, base=base, workdir=workdir)
        argv = [a.format(**sub) for a in ent["argv"]]
        env = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "LANG", "TMPDIR", "VIRTUAL_ENV")}
        env["PYTHONPATH"] = "tests/hastub"
        p = subprocess.run(argv, cwd=wt, env=env, capture_output=True, text=True, timeout=ent.get("timeout_s", 300), check=False)
        if p.returncode not in ent.get("ok_rc", [0]):
            raise Refused(f"`{name}` exited {p.returncode}: {(p.stderr or p.stdout).strip()[-300:]}")
        lines = p.stdout.rstrip("\n").split("\n")
        if "grep" in ent:
            lines = [ln for ln in lines if re.search(ent["grep"], ln)]
        if "tail" in ent:
            lines = lines[-int(ent["tail"]):]
        if not lines or lines == [""]:
            raise Refused(f"`{name}` printed nothing after its filter")
        return "\n".join(lines)
    finally:
        subprocess.run(["git", "-C", root, "worktree", "remove", "--force", wt], capture_output=True, check=False)
        shutil.rmtree(tmp, ignore_errors=True)


def context(root: str, base: str, head: str) -> tuple[str, str]:
    head_sha = _git(root, "rev-parse", "--verify", head + "^{commit}")
    return head_sha, _git(root, "merge-base", base, head_sha)


def cmd_render(root, base, head, name):
    head_sha, mb = context(root, base, head)
    out = run_instrument(root, base, head_sha, mb, name, load_registry(root, base))
    print("\n".join(render_text(name, {"mb": mb, "head": head_sha}, out)))


def cmd_refresh(root, base, head, body_path):
    text = open(body_path, encoding="utf-8").read()
    lines, blocks = parse(text)
    if not blocks:
        return 0
    head_sha, mb = context(root, base, head)
    reg = load_registry(root, base)
    for i, j, name, _attrs, _b in reversed(blocks):
        out = run_instrument(root, base, head_sha, mb, name, reg)
        lines[i:j + 1] = render_text(name, {"mb": mb, "head": head_sha}, out)
    open(body_path, "w", encoding="utf-8").write("\n".join(lines))
    print(f"figure_block: refreshed {len(blocks)} block(s) at {head_sha[:12]}")
    return 0


def verify_text(text: str, root: str, base: str, head: str) -> list[str]:
    """Problems with the blocks in ``text``; none when every block is what the registry renders."""
    _lines, blocks = parse(text)
    if not blocks:
        return []
    head_sha, mb = context(root, base, head)
    reg = load_registry(root, base)
    problems = []
    for i, _j, name, attrs, body in blocks:
        if attrs.get("head") != head_sha or attrs.get("mb") != mb:
            problems.append(f"line {i + 1}: block `{name}` names head={attrs.get('head', '-')[:12]} mb={attrs.get('mb', '-')[:12]}, "
                            f"this run is head={head_sha[:12]} mb={mb[:12]}; re-render with `figure_block.py refresh <body>`")
            continue
        try:
            want = render_text(name, attrs, run_instrument(root, base, head_sha, mb, name, reg))[1:-1]
        except Refused as e:
            problems.append(f"line {i + 1}: block `{name}`: {e}")
            continue
        if body != want:
            problems.append(f"line {i + 1}: block `{name}` is not what the registered instrument printed at {head_sha[:12]}; "
                            "a figure block is rendered, never typed -- run `figure_block.py refresh <body>`")
    return problems


def cmd_verify(root, base, head, body_path):
    problems = verify_text(open(body_path, encoding="utf-8").read(), root, base, head)
    for p in problems:
        print(f"  ERROR   [figure-block] {p}")
    n = len(parse(open(body_path, encoding="utf-8").read())[1])
    print(f"figure_block verify: {n} block(s), {len(problems)} refused")
    return 1 if problems else 0


def _scope(root: str, mb: str, workdir: str) -> int:
    """The registered `scope-line` instrument: the gate's MODE line for the diff since ``mb``."""
    p = subprocess.run([sys.executable, "tests/closure.py", "select", "--diff", mb, "--workdir", workdir],
                       cwd=root, capture_output=True, text=True, check=False)
    scope = os.path.join(workdir, "scope.txt")
    if p.returncode or not os.path.exists(scope):
        print(p.stderr[-300:], file=sys.stderr)
        return 1
    mode = [ln for ln in open(scope, encoding="utf-8").read().split("\n") if ln.strip().startswith("MODE:")]
    print(mode[0].strip() if mode else "no MODE line")
    return 0 if mode else 1


def _self_test() -> int:
    results = []

    def check(name, ok):
        results.append(bool(ok))
        print(("  ok  " if ok else "  FAIL") + " " + name)

    def refused(fn):
        try:
            fn()
        except Refused:
            return True
        return False

    tmp = tempfile.mkdtemp(prefix="figblock-st-")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests"))
        from throwaway_git import throwaway_git_init
        env = throwaway_git_init(tmp, "-q", "-b", "main")

        def g(*a, cwd=tmp):
            subprocess.run(["git", *a], cwd=cwd, env=env, check=True, capture_output=True)
        os.makedirs(os.path.join(tmp, "tools/pr"))
        reg = {"instruments": {"mb": {"argv": ["git", "merge-base", "{base}", "{head}"], "files": []},
                               "bad": {"argv": ["false"], "files": []}}}
        open(os.path.join(tmp, REGISTRY), "w").write(json.dumps(reg))
        open(os.path.join(tmp, "f"), "w").write("1")
        g("add", "-A"); g("commit", "-qm", "base")
        g("checkout", "-qb", "topic")
        open(os.path.join(tmp, "f"), "w").write("2")
        # a head that adds an instrument the base lacks
        reg["instruments"]["evil"] = {"argv": ["echo", "pwned"], "files": []}
        open(os.path.join(tmp, REGISTRY), "w").write(json.dumps(reg))
        g("commit", "-qam", "head")
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp, capture_output=True, text=True).stdout.strip()
        mbsha = subprocess.run(["git", "rev-parse", "main"], cwd=tmp, capture_output=True, text=True).stdout.strip()
        body = os.path.join(tmp, "body.md")
        empty = f"## Figures\n<!-- figure-block: mb -->\n<!-- /figure-block -->\nfree-form: `git log`\n"
        open(body, "w").write(empty)
        check("refresh fills an empty marker at the head with no agent turn", cmd_refresh(tmp, "main", "HEAD", body) == 0
              and mbsha in open(body).read() and head in open(body).read())
        check("verify accepts the refreshed body and the free-form line beside it", verify_text(open(body).read(), tmp, "main", "HEAD") == []
              and "free-form: `git log`" in open(body).read())
        typed = open(body).read().replace(mbsha + "\n~~~", "0" * 40 + "\n~~~", 1)
        check("a hand-typed value in a block is refused", len(verify_text(typed, tmp, "main", "HEAD")) == 1)
        moved = open(body).read().replace(head, "1" * 40)
        check("a block naming another head is refused as stale", len(verify_text(moved, tmp, "main", "HEAD")) == 1)
        g("commit", "-q", "--allow-empty", "-m", "head2")
        check("a moved head is stale until the writer re-renders it", len(verify_text(open(body).read(), tmp, "main", "HEAD")) == 1
              and cmd_refresh(tmp, "main", "HEAD", body) == 0 and verify_text(open(body).read(), tmp, "main", "HEAD") == [])
        evil = "<!-- figure-block: evil -->\n<!-- /figure-block -->\n"
        check("an instrument registered only by the head is refused (null: the base's own mb passes above)",
              refused(lambda: cmd_refresh(tmp, "main", "HEAD", _w(body, evil))))
        check("an unknown name is refused", refused(lambda: cmd_refresh(tmp, "main", "HEAD", _w(body, "<!-- figure-block: nope -->\n<!-- /figure-block -->\n"))))
        check("an instrument that exits non-zero is refused", refused(lambda: cmd_refresh(tmp, "main", "HEAD", _w(body, "<!-- figure-block: bad -->\n<!-- /figure-block -->\n"))))
        check("an unclosed block is refused", refused(lambda: parse("<!-- figure-block: mb -->\nx\n")))
        check("a malformed marker is refused", refused(lambda: parse("<!-- figure-block: Mb -->\n")))
        check("a body with no block is untouched (null control)", verify_text("## Figures\nnone\n", tmp, "main", "HEAD") == [])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    failed = results.count(False)
    print(f"figure_block self-test: {len(results)} checks, {failed} failed")
    return 1 if failed else 0


def _w(path: str, text: str) -> str:
    open(path, "w").write(text)
    return path


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return _self_test()
    if argv[:1] == ["_scope"]:
        return _scope(os.getcwd(), argv[1], argv[2])
    opts = {"--base": "origin/main", "--head": "HEAD"}
    pos = []
    it = iter(argv)
    for a in it:
        if a in opts:
            opts[a] = next(it, "")
        else:
            pos.append(a)
    if len(pos) != 2 or pos[0] not in ("render", "refresh", "verify"):
        print(__doc__)
        return 2
    root = _git(os.getcwd(), "rev-parse", "--show-toplevel")
    try:
        if pos[0] == "render":
            cmd_render(root, opts["--base"], opts["--head"], pos[1])
            return 0
        fn = cmd_refresh if pos[0] == "refresh" else cmd_verify
        return fn(root, opts["--base"], opts["--head"], pos[1])
    except Refused as e:
        print(f"  ERROR   [figure-block] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
