#!/usr/bin/env python3
"""Refuse two bash-3.2-only failures in a tracked tools/ shell script.

    python3 -I tools/audit/seat/bare_array.py --check [--ref <commit>]
    python3 -I tools/audit/seat/bare_array.py --self-test

WHY. macOS /bin/bash 3.2 rejects the expansion of an EMPTY array under `set -u`
(`name[@]: unbound variable`); bash 4.4+ and so CI's bash 5 expand it cleanly.
A run-time test on CI therefore passes on the defect, and the rule that
`bus.sh`, `body_push.sh` and `seat_venv.sh` each state in prose did not stop
`bus.sh orphans` (`"${arms[@]}"`, R10-FLY-ORPHANS-REWRITTEN) from dying on the
operator's machine (triage P303). This is the static half.

THE RULE: every tracked tools/**/*.sh is judged, with or without a `set -u` of
its own, because a sourced library (`pr_args.sh`, `delivery_row.sh`,
`app_mint.sh`) runs under its caller's `-u`, and nounset has spellings a
textual test misses (`set -o errexit -o nounset`, a `#!/bin/bash -u` shebang).
Each non-comment line is refused for every `"${name[@]}"` that is not the
guarded form `${name[@]+"${name[@]}"}`, unless `# never-empty: <reason>` with
a reason, stating why the array cannot be empty there, sits on the line itself
or on a comment-only line directly above it. A line that ends in a
`# mut:<name>` marker takes the reason on the line above: its self-test finds
the mutant line by that marker at the line's end (`pr_args.sh`'s header), so a
reason appended after the marker unanchors the mutant, and any line carrying
one is refused. `"${name[*]}"`, `${#name[@]}` and `"${name[@]:...}"` are not
matched.

THE SECOND RULE: a `case` pattern without its leading `(` inside a `$( ... )`
command substitution, or a `<( ... )`/`>( ... )` process substitution, quoted
or not. Bash 3.2 finds the end of a substitution by counting parentheses, so
the pattern's `)` closes it early: unquoted, `bash -n` fails (`tick_loop.sh`,
PR 3520, the tick loop's own freshness check refusing on every pass); inside
double quotes `bash -n` passes and the substitution dies at run time. Bash 4+
parses both. The way out is the pattern's own `(`: `(func) ...;;`. A case in a
plain `( ... )` subshell, in backquotes, or at top level is not refused, since
3.2 parses those; there is no opt-out marker, because a refused site never
parses on 3.2. Comments, quotes and here-document bodies are skipped (an
unbalanced `)` in a here-document inside a substitution is a 3.2 hazard of its
own, which this rule does not judge).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

BARE = re.compile(r'"\$\{([A-Za-z_]\w*)\[@\]\}"')
MARK = re.compile(r"#\s*never-empty:\s*\S")
MUT = re.compile(r"#\s*mut:\S")


def marked(line: str) -> bool:
    """The line's own never-empty reason, unless it follows a `# mut:` marker."""
    mark, mut = MARK.search(line), MUT.search(line)
    return bool(mark) and not (mut and mut.start() < mark.start())


def sites(text: str) -> list[tuple[int, str]]:
    """(line number, line) of each refused expansion in one script's text."""
    lines = text.splitlines()
    # A reason after a mut marker is refused on any line, bare expansion or not.
    out = {n for n, ln in enumerate(lines, 1) if MARK.search(ln) and not marked(ln)}
    above = False  # the previous line is a comment-only never-empty reason
    for n, line in enumerate(lines, 1):
        comment = line.lstrip().startswith("#")
        excused, above = above, comment and bool(MARK.search(line))
        if comment or excused or marked(line):
            continue
        for m in BARE.finditer(line):
            if not line[: m.start()].endswith("${%s[@]+" % m.group(1)):
                out.add(n)
                break
    return [(n, lines[n - 1].strip()) for n in sorted(out)]


WORD = re.compile(r"\w+")  # a word; only case, in and esac are read
HEREDOC = re.compile(r"""<<(-?)[ \t]*(['"]?)\\?([A-Za-z_][A-Za-z0-9_]*)\2""")
COMMAND = re.compile(r"(?:\A|[\n;&|(){!`]|(?:\A|\W)(?:then|do|else|time))[ \t]*\Z")  # `case` is a keyword here
BEFORE, AFTER = " \t\n;&|(){`", " \t\n;&|()`"
EOL = re.compile(r".*")  # to the end of the line, the newline left
SQUOTE = re.compile(r"'[^']*'?")
PATTERN = re.compile(r"""(?:\\.|'[^']*'?|"(?:\\.|[^"\\])*"?|[^)'"\\])*\)?""", re.S)  # through its `)`


def case_sites(text: str) -> list[tuple[int, str]]:
    """(line number, line) of each case pattern lacking `(` inside a substitution."""
    stack: list = []  # "sub", "paren", "dq", "bt", "param", or a case: [case, head|pat|body]
    hits, docs, i, n = set(), [], 0, len(text)
    lines = text.splitlines()
    while i < n:
        c, t = text[i], stack[-1] if stack else None
        if isinstance(t, list) and t[1] == "pat":
            m = WORD.match(text, i)
            if c in " \t\n":
                i += 1
            elif c == "#":
                i = EOL.match(text, i).end()
            elif m and m.group() == "esac" and text[m.end():m.end() + 1] in AFTER:
                stack.pop()  # the keyword is then read again, in the enclosing context
            else:
                outer = [e for e in stack if e in ("sub", "bt")]
                if c != "(" and outer[-1:] == ["sub"]:
                    hits.add(text.count("\n", 0, i) + 1)
                t[1], i = "body", PATTERN.match(text, i + (c == "(")).end()
            continue
        if t == "dq" and c not in "\\$`":
            stack.pop() if c == '"' else None
            i += 1
            continue
        word = text[i - 1:i] in BEFORE  # at i == 0 the slice is "", which is in any string
        m = WORD.match(text, i) if word else None
        kw = m.group() if m and text[m.end():m.end() + 1] in AFTER else None
        if c == "\\":
            i += 1
        elif c == "}" and t == "param":
            stack.pop()
        elif c == "#" and word and t != "param":
            i = EOL.match(text, i).end() - 1
        elif c == "'" and t != "dq":
            i = SQUOTE.match(text, i).end() - 1
        elif c == '"':
            stack.append("dq")
        elif c == "`":
            stack.pop() if t == "bt" else stack.append("bt")
        elif text.startswith(("$(", "<(", ">("), i):
            stack.append("sub")  # `$((` too: its `((` and `))` then pair as a paren
            i += 1
        elif text.startswith("${", i):
            stack.append("param")
        elif c == "(":
            stack.append("paren")
        elif c == ")" and t in ("sub", "paren"):
            stack.pop()
        elif HEREDOC.match(text, i) and not text.startswith("<<<", i):
            h = HEREDOC.match(text, i)
            docs.append(re.compile("^" + "\t*" * len(h.group(1)) + h.group(3) + "$", re.M))
        elif c == "\n" and docs:
            for d in docs:  # each body in turn, to its delimiter line or the end
                e = d.search(text, i + 1)
                i = e.end() if e else n
            docs = []
            continue
        elif isinstance(t, list) and t[1] == "body" and text.startswith((";;", ";&"), i):
            t[1] = "pat"
            i += 2 if text.startswith(";;&", i) else 1
        elif m:
            if kw == "case" and COMMAND.search(text, max(0, i - 9), i):
                stack.append(["case", "head"])
            elif kw == "in" and t == ["case", "head"]:
                t[1] = "pat"
            elif kw == "esac" and t == ["case", "body"]:
                stack.pop()
            i = m.end() - 1
        i += 1
    return [(k, lines[k - 1].strip()) for k in sorted(hits)]


def scan(ref: str | None = None) -> list[str]:
    """`path:line: text` per refused site across tracked tools/**/*.sh."""
    root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    if ref:
        names = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", ref, "--", "tools"], text=True, cwd=root).split()
    else:
        names = subprocess.check_output(
            ["git", "ls-files", "--", "tools"], text=True, cwd=root).split()
    out = []
    for p in sorted(n for n in names if n.endswith(".sh")):
        if ref:
            text = subprocess.check_output(["git", "show", f"{ref}:{p}"], text=True, cwd=root)
        else:
            text = (Path(root) / p).read_text()
        out += [f"{p}:{n}: {t}" for n, t in sorted(set(sites(text) + case_sites(text)))]
    return out


def self_test() -> int:
    fails = []

    def st(got, want, name):
        if got != want:
            fails.append(f"{name}: got {got!r}, want {want!r}")

    head = "#!/bin/bash\nset -uo pipefail\n"
    bare = head + 'f "${arms[@]}" x\n'
    st(len(sites(bare)), 1, "a bare expansion under set -u is refused")
    st(sites(head + 'f ${arms[@]+"${arms[@]}"} x\n'), [], "the guarded form passes")
    st(sites(head + 'f "${a[@]}" # never-empty: argv of this script, checked above\n'), [],
       "an allow-marked never-empty site passes (null)")
    st(len(sites(head + 'f "${a[@]}" # never-empty:\n')), 1, "a marker with no reason does not excuse")
    st(len(sites('#!/bin/bash\nset -e\nf "${a[@]}"\n')), 1,
       "a file without set -u is judged too: a sourced library runs under its caller's -u")
    st(sites('#!/bin/bash\nset -e\nf ${a[@]+"${a[@]}"}\n'), [],
       "the guarded form passes in a file without set -u (null)")
    st(len(sites('set -o errexit -o nounset\nf "${a[@]}"\n')), 1, "a long-form nounset file is judged")
    st(len(sites('#!/bin/bash -u\nf "${a[@]}"\n')), 1, "a -u shebang file is judged")
    st(sites(head + '# f "${a[@]}"\n'), [], "a comment line is skipped")
    st(len(sites(head + 'f ${b[@]+"${b[@]}"} "${a[@]}"\n')), 1,
       "a guard on one array does not excuse another on the line")
    st(len(sites(head + 'f ${b[@]+"${a[@]}"}\n')), 1, "a guard names its own array")
    st(sites(head + 'n=${#a[@]}; f "${a[*]}"\n'), [], "length and star forms are not matched")
    st(sites(head + '# never-empty: argv, checked above\nf "${a[@]}"  # mut:x\n'), [],
       "a reason on the comment line above excuses the next line (null)")
    st(len(sites(head + '# never-empty: argv\n\nf "${a[@]}"\n')), 1,
       "a reason above excuses only the line directly below it")
    st(len(sites(head + 'f "${a[@]}"  # mut:x  # never-empty: argv\n')), 1,
       "a reason after a mut marker does not excuse: it unanchors the mutant")
    st(sites(head + 'f "${a[@]}"  # never-empty: argv  # mut:x\n'), [],
       "a reason before the mut marker excuses (null)")
    st(len(sites('#!/bin/bash\nf x  # mut:x  # never-empty: argv\n')), 1,
       "a reason after a mut marker is refused in an unjudged file too")
    st(len(sites(head + 'f x  # mut:x  # never-empty: argv\n')), 1,
       "a reason after a mut marker is refused in a judged file on a line with no bare expansion")
    st(len(sites(head + 'f ${a[@]+"${a[@]}"}  # mut:x  # never-empty: argv\n')), 1,
       "a reason after a mut marker is refused in a judged file on a guarded line")
    st(sites(head + 'f x  # never-empty: argv  # mut:x\n'), [],
       "a judged file's non-bare line with the reason before the marker passes (null)")
    # The second rule: the line numbers each text refuses. Run against bash 3.2.57, every refused
    # shape fails, at `bash -n` or (quoted, or in backquotes) at run time.
    def cs(text, want, name):
        st([k for k, _ in case_sites(text)], want, name)

    tick = ('out=$(export A=1\n  case $1 in\n    func) . "$t/e"; export -f exec; "$B" --n ;;\n'
            '    bashenv) BASH_ENV=$t/e "$B" --n ;;\n    none) "$B" --n ;;\n  esac 2>&1); src=$?\n')
    cs(tick, [3, 4, 5], "planted: tick_loop.sh's shape at PR 3520, three bare patterns in $( )")
    cs(tick.replace("func)", "(func)").replace("bashenv)", "(bashenv)").replace("none)", "(none)"), [],
       "the same with each pattern's own ( passes (null)")
    cs("case a in a) x=$(echo 1);; esac\n", [], "a case at top level passes, its body's $( ) too")
    cs("( case a in a) :;; esac )\nx=`case a in a) :;; esac`\n", [], "a subshell or backquotes pass")
    cs("x=$(y=`case a in a) :;; esac`)\n", [], "backquotes inside $( ) reset it")
    cs("x=$(y=`echo $(case a in a) :;; esac)`)\n", [1], "a $( ) inside those backquotes counts")
    cs("cat <(case a in a) :;; esac)\ncat >(case a in\n b) :;; esac)\n", [1, 3],
       "a process substitution counts, either direction")
    cs('x="$(case a in a) :;; esac)"\n', [1], "a quoted $( ) counts: bash -n passes, the run dies")
    cs("x=$(case a in (a|b) :;& c) :;; esac)\nx=$(case a in (a) :;;& (b) :;; d) :;; esac)\n", [1, 2],
       "a bare pattern after ;& or ;;& is refused, a led one after ;; passes")
    cs("x=$(case a in (a) :;; esac; echo b)\nx=$(echo)\ncase a in a) :;; esac\n", [],
       "esac and the closing ) end the substitution's reach")
    cs("x=$(case a in\n  # c) a comment\n  (a) :;;\nesac; echo '# case a in a)' \"case a in a)\")\n", [],
       "comments and quoted text are not patterns")
    cs("x=$(echo a#b $# \"\\\"\" \"$(echo \\\")\"; case a in a) :;; esac)\n", [1],
       "a mid-word # is no comment; escapes in and out of quotes")
    cs("x=$(echo \\)\ncase a in a) :;; esac)\n", [2], "an escaped ) does not close the substitution")
    cs("x=$(cat <<E\ncase a in a) x;; esac\nE\ncat <<-'F'\n\tb) )\n\tF\ncase a in a) :;; esac)\n", [7],
       "here-document bodies are skipped, and scanning resumes after the delimiter")
    cs("x=$(cat <<<case; case a in a) :;; esac)\n", [1], "a here-string is not a here-document")
    cs("x=$(echo $(( (1)+2 )) ${y:-z}; case a in a) :;; esac)\nx=$(( (1) ))${y}\ncase a in a) :;; esac\n",
       [1], "arithmetic and ${ } nest and close")
    cs("x=$(f() { case a in a) :;; esac; }; ( case b in b) :;; esac ))\n", [1],
       "a function or subshell inside $( ) is still inside it")
    cs("x=$(if t; then case a in a) :;; esac; fi; while t; do case b in\n b) :;; esac; done)\n", [1, 2],
       "case after then and do is a keyword")
    cs("x=$(t && case a in a) :;; esac)\nx=$(case a in (a) case b in b) :;; esac;; esac)\n", [1, 2],
       "case after && and a nested case after a pattern are keywords")
    cs("local rt case\ncase=$(echo case a in b)\nx=$(mycase a in b)\n", [],
       "case as an argument, a variable or inside a word is not the keyword")
    cs('x=$(case "$y" in ("a)") :;; \'b)\'|c) :;; esac)\n', [1], "a pattern's quoted ) is not its end")
    cs("$(case a in a) :;; esac)\n\nx=$(case a in (a\\'\"\") :;;\n c) :;; esac)\n", [1, 4],
       "a $( ) at the text's start; an escaped quote and an empty quote inside a led pattern")
    cs("\n# $(\ncase a in a) :;; esac\nx=$(case a in (a);;\n b) :;; esac)\n", [5],
       "a leading newline counts; a comment opens no $( ); ;; right after a pattern")
    cs("x=$(echo ')' '' \")\" ${#a} $((1)) $(((1)+(2))); case a in a) :;; esac)\n", [1],
       "quoted ), an empty quote, ${#...}, arithmetic: none closes the substitution")
    cs("x=$(echo $((1)))\ncase a in a) :;; esac\nx=${y}$(case a in a) :;; esac)\n", [3],
       "arithmetic and ${ } close where they end")
    cs("x=$(echo # )\ncase a in a) :;; esac)\nx=$(case a in (a) :;;&(b) :;;\n c) :;; esac)\n", [2, 4],
       "a comment's ) closes nothing; ;;& is consumed whole")
    cs("x=$(cat <<E\nE\ncase a in a) :;; esac)\nx=$(case a in (a) :\nesac)\ncase b in b) :;; esac\n", [3],
       "a here-document's delimiter can be its first line; esac after a body without ;; ends the case")
    cs("x=$(cat <<-E\n\t\tE\ncase a in a) :;; esac)\nx=$(cat <<E\n\tE\ncase a in a) :;; esac\nE\n)\n", [3],
       "<<- strips tabs before its delimiter, << does not")
    cs("x=`echo $(case a in a) :;; esac)`; y=$(z=`case a in a) :;; esac`)\n", [1],
       "case right after a backquote is a keyword; a $( ) inside backquotes counts")
    # The CLI over a scratch repository: both rules, `--check` on the tree and at a ref.
    import tempfile
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
    from throwaway_git import throwaway_git_init
    with tempfile.TemporaryDirectory() as d:
        env = throwaway_git_init(d, "-q")
        (Path(d) / "tools").mkdir()
        (Path(d) / "tools/a.sh").write_text('f "${a[@]}"\nx=$(case a in a) :;; esac)\n')
        (Path(d) / "tools/b.txt").write_text('f "${a[@]}"\n')

        def cli(*args):
            r = subprocess.run([sys.executable, "-I", __file__, *args], cwd=d, env=env,
                               capture_output=True, text=True)
            return r.returncode, r.stdout.split("\n")[:-1]

        subprocess.run(["git", "add", "-A"], cwd=d, env=env, check=True)
        subprocess.run(["git", "commit", "-qm", "x"], cwd=d, env=env, check=True)
        want = (1, ['tools/a.sh:1: f "${a[@]}"', "tools/a.sh:2: x=$(case a in a) :;; esac)"])
        st(cli("--check"), want, "--check prints each site of both rules in .sh files, rc 1")
        (Path(d) / "tools/a.sh").write_text("x=$(case a in (a) :;; esac)\n")
        st(cli("--check"), (0, []), "--check on the repaired tree passes (null)")
        st(cli("--check", "--ref", "HEAD"), want, "--check --ref reads the commit, not the tree")
        st(cli()[0], 2, "no arm prints the usage, rc 2")
    for f in fails:
        print("FAIL", f)
    print("bare_array self-test:", "FAILED" if fails else "ok")
    return 1 if fails else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    if "--check" in sys.argv:
        ref = sys.argv[sys.argv.index("--ref") + 1] if "--ref" in sys.argv else None
        hits = scan(ref)
        if hits:
            print("\n".join(hits))
        sys.exit(1 if hits else 0)
    print(__doc__)
    sys.exit(2)
