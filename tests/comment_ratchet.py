#!/usr/bin/env python3
"""The comment-length ratchet: no comment or docstring gains a sentence over 40 words.

The rule is criterion C5 of dev/governance/dimensions/D5.md, measured the way the D5 finders measure
it. tools/audit/text_ledger.py `units_of(path, text, "D5")` yields each comment block and docstring.
Comment markers are stripped, and the text is split into paragraphs at blank, rule and list lines.
`text_ledger.sentences` then splits each paragraph into sentences. A unit is long when one of its
sentences has more than 40 whitespace-separated words.

The ratchet is derived, never stored: it measures the worktree and the ratchet base
(`tests/mutation_table.py` `ratchet_base`: the merge base on a branch, HEAD^1 on main). It refuses
when a file present at both ends has more long units at HEAD, or when the scope's total rises. A
file new at HEAD is counted only by the total, so a split that moves a docstring passes. A base the
checkout cannot read refuses, so a shallow clone fails closed. Each refusal quotes the unit's first
words, because text_ledger's JavaScript line numbers are unreliable.

SCOPE is the one list the comment groups extend: tracked `tests/` files ending `.py`, `.mjs` or `.sh`.

Usage:
  comment_ratchet.py [--base REF]     the ratchet against the ratchet base
  comment_ratchet.py --show           also print one row per long unit
  comment_ratchet.py --text-only REF  prints `RESULT code_changed_files=<n> line_shifted_hunks=<n>`
  comment_ratchet.py --self-test

tests/doc_claims.py runs `gate` as one arm, so the ratchet adds no selectable script.
"""
import argparse, ast, difflib, inspect, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "audit"))
sys.path.insert(0, str(ROOT / "tests"))
import text_ledger  # noqa: E402

MAX_WORDS = 40
SUFFIXES = (".py", ".mjs", ".sh")
QUOTE_WORDS = 12


def in_scope(path):
    return path.startswith("tests/") and path.endswith(SUFFIXES)


def _strip_marker(line):
    s = line.lstrip()
    for m in ("#:", "#", "//", "/*", "*/", "*"):
        if s.startswith(m):
            s = s.lstrip(m[0]) if m in ("#", "//") else s[len(m):]
            break
    return s.replace("*/", " ")


def _is_rule(t):
    return len(t) >= 3 and set(t) <= set("-=#*~_")


def _is_heading(t):
    """A banner line (`--- Title ----`): a paragraph of its own."""
    return t[:3] in ("---", "===", "###", "~~~") or t.endswith(("----", "===="))


def _is_code(kind, line):
    """An indented line (a usage block, a table, a code sample) is not prose: four spaces past the
    docstring's margin, or past the one space after a comment marker."""
    lead = len(line) - len(line.lstrip(" "))
    return bool(line.strip()) and lead >= (4 if kind == "docstring" else 5)


def _is_break(s):
    """A blank line, a rule line or a list item ends a paragraph."""
    t = s.strip()
    if not t or _is_rule(t):
        return True
    head = t.split(None, 1)[0]
    return head in ("-", "*", "+") or head.rstrip(".)").isdigit() and head[-1:] in ".)"


def paragraphs(kind, text):
    """The unit's prose split where a reader sees a break; a rule line is dropped, a list item starts a paragraph."""
    lines = inspect.cleandoc(text).splitlines() if kind == "docstring" else [_strip_marker(l) for l in text.splitlines()]
    out, cur, prev, code, item = [], [], "", False, None
    for ln in lines:
        # An indented block opens after a blank line or a line ending ':'; a hanging indent, and a
        # list item's own continuation paragraph (indented to its text), are prose.
        lead = len(ln) - len(ln.lstrip(" "))
        if ln.strip() and _is_break(ln) and not _is_rule(ln.strip()):
            item = lead + len(ln.split(None, 1)[0]) + 1
        elif ln.strip() and lead <= 1:
            item = None
        code = (_is_code(kind, ln) and (item is None or lead > item + 3)
                and (code or not prev.strip() or prev.rstrip().endswith(":")))
        prev = ln
        if code:
            if cur:
                out.append(" ".join(cur))
            cur = []
            continue
        if _is_break(ln) or _is_heading(ln.strip()):
            if cur:
                out.append(" ".join(cur))
            cur = [] if _is_rule(ln.strip()) or not ln.strip() else [ln.strip()]
            if _is_heading(ln.strip()):
                out.extend(cur)
                cur = []
            continue
        cur.append(ln.strip())
    if cur:
        out.append(" ".join(cur))
    return out


def _split_trailing(path, src, line, kind, body):
    """A Python comment block's lines, each trailing comment (code before the `#`) a unit of its own."""
    if kind != "comment" or not path.endswith(".py"):
        return [body]
    parts, cur = [], []
    for i, ln in enumerate(body.split("\n")):
        code = src[line - 1 + i].split("#", 1)[0].strip() if line - 1 + i < len(src) else ""
        if code:
            parts.append(ln)
        else:
            cur.append(ln)
            continue
        if cur:
            parts.insert(len(parts) - 1, "\n".join(cur))
            cur = []
    if cur:
        parts.append("\n".join(cur))
    return parts


def long_units(path, text):
    """[(line, first words)] for each unit of `text` holding a sentence over MAX_WORDS words."""
    out, src = [], text.splitlines()
    for _uid, line, kind, body in text_ledger.units_of(path, text, "D5"):
        if kind == "file":
            continue
        for para in (p for piece in _split_trailing(path, src, line, kind, body) for p in paragraphs(kind, piece)):
            hit = next((s for s in text_ledger.sentences(para) if len(s.split()) > MAX_WORDS), None)
            if hit:
                out.append((line, " ".join(hit.split()[:QUOTE_WORDS])))
                break
    return out


def git(*args, check=True):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.strip()}")
    return p.stdout


def blobs(ref, paths):
    """{path: text} at `ref` through one `git cat-file --batch`; a missing path is absent."""
    p = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, capture_output=True,
                       input="".join(f"{ref}:{x}\n" for x in paths).encode())
    data, out, i = p.stdout, {}, 0
    for x in paths:
        nl = data.index(b"\n", i)
        head = data[i:nl].split()
        if head[-1] == b"missing":
            i = nl + 1
            continue
        n = int(head[2])
        out[x] = data[nl + 1:nl + 1 + n].decode("utf-8", "replace")
        i = nl + 2 + n
    return out


def tracked(ref=None):
    files = git("ls-tree", "-r", "--name-only", ref).split() if ref else git("ls-files").split()
    return sorted(f for f in files if in_scope(f))


def head_texts(files):
    return {f: (ROOT / f).read_text(encoding="utf-8", errors="replace") for f in files if (ROOT / f).is_file()}


def counts(texts):
    return {f: long_units(f, t) for f, t in texts.items()}


def decide(base, head):
    """Refusal lines for the head's long units against the base's; empty when the ratchet holds."""
    out = []
    for f in sorted(head):
        old = base.get(f)
        if old is not None and len(head[f]) > len(old):
            was = {q for _l, q in old}
            new = [q for _l, q in head[f] if q not in was] or [head[f][-1][1]]
            out.append(f"REFUSE {f}: long units {len(old)} -> {len(head[f])}; new: "
                       + " | ".join(f'"{q} ..."' for q in new))
    tb, th = sum(map(len, base.values())), sum(map(len, head.values()))
    if th > tb:
        out.append(f"REFUSE scope total: long units {tb} -> {th}")
    return out


def resolve_base(base):
    """The ratchet base as a commit this checkout holds, or None (shallow, detached, unknown)."""
    import mutation_table
    ref = mutation_table.ratchet_base("changed", base)
    if not ref:
        return None
    sha = git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", check=False).strip()
    return sha or None


def measure(base):
    """(base sha or None, refusal lines, summary line): the ratchet over SCOPE against `base`'s merge base."""
    base_ref = resolve_base(base)
    if not base_ref:
        return None, ["REFUSE comment_ratchet: no ratchet base in this checkout (a shallow clone fails"
                      " closed; fetch the merge base)"], "", {}
    old = counts(blobs(base_ref, tracked(base_ref)))
    new = counts(head_texts(tracked()))
    summary = (f"RESULT base={base_ref[:12]} files={len(new)} long_units_base={sum(map(len, old.values()))}"
               f" long_units_head={sum(map(len, new.values()))}")
    return base_ref, decide(old, new), summary, new


def ratchet(base, show=False):
    _base_ref, refusals, summary, *rest = measure(base)
    if show:
        for f in sorted(rest[0]):
            for line, q in rest[0][f]:
                print(f"LONG\t{f}:{line}\t{q} ...")
    if summary:
        print(summary)
    for r in refusals:
        print(r)
    print("comment_ratchet: " + ("FAIL" if refusals else "OK"))
    return 1 if refusals else 0


def code_of(path, text):
    """The text with every D5 unit's prose removed: an AST dump for Python, else the comment-free text."""
    if path.endswith(".py"):
        tree = ast.parse(text)
        for node in ast.walk(tree):
            body = getattr(node, "body", None)
            if (isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and body
                    and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                body[0].value.value = ""
        return ast.dump(tree)
    for _line, _kind, comment in text_ledger.scan_c_like(text, path.endswith(".sh"))[0]:
        for piece in comment.split("\n"):
            text = text.replace(piece.strip(), " ", 1)
    return " ".join(text.split())


def shifted_hunks(a, b):
    """Changed hunks whose old and new line counts differ."""
    ops = difflib.SequenceMatcher(None, a.splitlines(), b.splitlines(), autojunk=False).get_opcodes()
    return sum(1 for op, i1, i2, j1, j2 in ops if op != "equal" and i2 - i1 != j2 - j1)


def text_only(ref):
    sha = git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", check=False).strip()
    if not sha:
        print(f"REFUSE comment_ratchet --text-only: {ref} is not a commit in this checkout")
        return 1
    changed = [f for f in git("diff", "--no-renames", "--name-only", sha, "--").split() if in_scope(f)]
    old, new = blobs(sha, changed), head_texts(changed)
    code = hunks = 0
    for f in changed:
        a, b = old.get(f), new.get(f)
        if a is None or b is None:
            code += 1
            continue
        code += code_of(f, a) != code_of(f, b)
        hunks += shifted_hunks(a, b)
    print(f"RESULT code_changed_files={code} line_shifted_hunks={hunks}")
    return 0


LONG41 = " ".join(["word"] * 40) + " end."
SHORT40 = " ".join(["word"] * 39) + " end."


def self_test(out=print):
    fails = []

    def arm(name, cond):
        out(("ok   " if cond else "FAIL ") + name)
        if not cond:
            fails.append(name)

    edge = (ROOT / "tests" / "edge.py").read_text(encoding="utf-8")
    sh = (ROOT / "tests" / "run.sh").read_text(encoding="utf-8")
    base = {"tests/edge.py": long_units("tests/edge.py", edge), "tests/run.sh": long_units("tests/run.sh", sh)}
    arm("the unchanged tree is accepted", not decide(base, dict(base)))
    py41 = edge + f"\n# {LONG41}\n"
    arm("a 41-word sentence planted in a Python comment is refused",
        any("tests/edge.py" in r for r in decide(base, {**base, "tests/edge.py": long_units("tests/edge.py", py41)})))
    py40 = edge + f"\n# {SHORT40}\n"
    arm("a 40-word sentence (the null control) is accepted",
        not decide(base, {**base, "tests/edge.py": long_units("tests/edge.py", py40)}))
    doc41 = edge + f'\n\ndef _planted():\n    """{LONG41}"""\n'
    arm("a 41-word sentence planted in a docstring is refused",
        bool(decide(base, {**base, "tests/edge.py": long_units("tests/edge.py", doc41)})))
    sh41 = sh + f"\n# {LONG41}\n"
    arm("a 41-word sentence planted in a shell comment is refused",
        any("tests/run.sh" in r for r in decide(base, {**base, "tests/run.sh": long_units("tests/run.sh", sh41)})))
    arm("a shell comment marker is stripped before the count",
        len(long_units("tests/run.sh", sh + f"\n# {SHORT40}\n")) == len(base["tests/run.sh"]))
    arm("a rule line is not a word of the sentence after it",
        not long_units("x.py", "# " + "-" * 20 + "\n# " + SHORT40 + "\n"))
    arm("an indented usage line is not prose",
        not long_units("x.py", 'def f():\n    """Run it.\n\n    Usage:\n\n        ' + " ".join(["cmd"] * 45) + '\n    """\n'))
    arm("a hanging indent continues its sentence",
        bool(long_units("x.py", "# - " + " ".join(["word"] * 30) + "\n#       " + LONG41[:60] + " end.\n")))
    arm("a list item's indented paragraph is prose",
        bool(long_units("x.py", "# 1. Item.\n#\n#    " + LONG41 + "\n")))
    arm("an indented docstring's own margin is prose",
        bool(long_units("x.py", 'def f():\n    """' + " ".join(["word"] * 30) + '\n    ' + LONG41[:60] + ' end."""\n')))
    arm("a banner line is a paragraph of its own",
        not long_units("x.py", "# --- " + " ".join(["word"] * 25) + " ---------\n# " + " ".join(["w"] * 25) + "\n"))
    arm("a trailing comment on a code line is not part of the block below it",
        not long_units("x.py", "x = 1  # " + " ".join(["word"] * 25) + "\n# " + " ".join(["w"] * 25) + "\ny = 2\n"))
    arm("a list item ends the sentence before it",
        not long_units("x.py", "# " + " ".join(["word"] * 30) + "\n# - " + " ".join(["word"] * 30) + "\n"))
    moved_from = {"tests/a.py": [(1, "q")], "tests/b.py": []}
    arm("a long unit moved to a new file is accepted", not decide(moved_from, {"tests/a.py": [], "tests/b.py": [],
                                                                             "tests/new.py": [(1, "q")]}))
    arm("a long unit added in a new file is refused",
        bool(decide(moved_from, {**moved_from, "tests/new.py": [(1, "r")]})))
    arm("a file shrinking while another grows is refused per file",
        bool(decide({"tests/a.py": [(1, "q"), (2, "r")], "tests/b.py": []},
                    {"tests/a.py": [], "tests/b.py": [(1, "s")]})))
    arm("a changed code token reads as code",
        code_of("tests/edge.py", edge) != code_of("tests/edge.py", edge.replace("import ", "import  sys, ", 1)
                                                  .replace("sys, sys", "sys")) or
        code_of("x.py", "a = 1\n") != code_of("x.py", "a = 2\n"))
    arm("a docstring edit does not read as code",
        code_of("x.py", 'def f():\n    """one."""\n    return 1\n') ==
        code_of("x.py", 'def f():\n    """two words."""\n    return 1\n'))
    arm("a shell comment edit does not read as code, a shell token does",
        code_of("x.sh", "# one\necho a\n") == code_of("x.sh", "# two words\necho a\n")
        and code_of("x.sh", "echo a\n") != code_of("x.sh", "echo b\n"))
    arm("a line-neutral rewrite reads 0 shifted hunks, an added line 1",
        shifted_hunks("a\nb\nc\n", "a\nB\nc\n") == 0 and shifted_hunks("a\nb\nc\n", "a\nb\nb2\nc\n") == 1)
    saved = os.environ.pop("GOLDEN_REF", None)   # gate_ref reads it before the base argument
    try:
        gone = measure("refs/heads/no-such-branch-for-the-ratchet")
    finally:
        if saved is not None:
            os.environ["GOLDEN_REF"] = saved
    arm("a base the checkout cannot resolve refuses (a shallow clone fails closed)",
        gone[0] is None and any("REFUSE" in r for r in gone[1]))
    out("comment_ratchet self-test: " + ("FAIL" if fails else "OK"))
    return 1 if fails else 0


def gate(base, out=print):
    """[(check name, passed, detail)] for a gate script to report: the self-test, then the ratchet."""
    lines = []
    rc = self_test(lines.append)
    rows = [("comment ratchet self-test (40-word rule, per-file and total compares, --text-only arms)",
             rc == 0, "; ".join(l for l in lines if l.startswith("FAIL")))]
    base_ref, refusals, summary, _ = measure(base)
    if summary:
        out("  " + summary)
    rows.append(("no tests/ comment or docstring gains a sentence over 40 words (comment ratchet)",
                 not refusals, "; ".join(refusals)))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--text-only", metavar="REF")
    ap.add_argument("--base", default="origin/main", help="the branch the merge base is taken against")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.text_only:
        return text_only(a.text_only)
    return ratchet(a.base, a.show)


if __name__ == "__main__":
    sys.exit(main())
