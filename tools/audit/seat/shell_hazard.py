#!/usr/bin/env python3
"""Refuse three shell hazards on the lines a branch adds to a tools/**/*.sh script.

    python3 -I tools/audit/seat/shell_hazard.py --check [--base <ref>] [--head <ref>]
    python3 -I tools/audit/seat/shell_hazard.py --self-test

WHY. Linux CI cannot see a host-dependent or input-size-dependent shell hazard,
and each reached a later, dearer gate: BSD `wc` pads its count (macOS), so a raw
`wc -l` compared as a string fails only on the operator's seat -- three
`prepr.sh --self-test` failures in round 10 (R10-RCA-PREPR-DARWIN-SELFTEST); a
pipe into an early-exit reader under `pipefail` kills its writer with SIGPIPE
only once the writer outgrows the pipe buffer (R10-RCA-FAMILY-PIPEFAIL-SIGPIPE,
`app_approve.sh`'s carry-tip read). Only ADDED lines are judged: the existing
sites cost nothing, and a hazard already on main is not this branch's.

THE RULES, one per added non-comment line:
  wc-compare  a `wc -l|-c|-w` command substitution that nothing normalises
              (`| tr -d ' '`, awk, sed, xargs) and that is compared as a STRING:
              the first argument of `st` or `case`, or either side of `=`,
              `==` or `!=` inside the `[`/`[[` test that holds it. A numeric
              test (`-eq`, `(( ))`, `$(( ))`) is read as a number and passes;
              only the compare holding the substitution is judged, never the
              rest of its line. Repair: `... | wc -l | tr -d ' '`; a compare that
              asserts the raw count on purpose (a stub's own padding) carries
              `# wc-raw: <reason>` on its line.
  wc-stub     a stub script text (a `#!` line) that calls the host's `wc` by
              absolute path without stripping its padding first: its output is
              then the host's formatting plus the stub's, which doubles the
              padding on BSD and none on GNU. Repair: `| tr -d ' '` before the
              stub shapes the count (a stub is host-independent).
  early-pipe  in a file that sets `pipefail`, a pipe into an early-exit reader
              (`grep -q`, `grep -m`, `head`): the reader leaves at its match, the
              writer takes SIGPIPE, the pipeline reads 141. Repair: a
              here-string, `grep -q PAT <<<"$x"`. A line ending `|| true`, or
              carrying `# pipe-small: <reason>` (the writer cannot outgrow a
              pipe buffer), passes.
"""
from __future__ import annotations

import re
import subprocess
import sys

WC_SUB = re.compile(r"\$\((?P<in>[^()]*\bwc\s+-[lcw]\b[^()]*)\)")
NORMALISE = re.compile(r"\|\s*(?:tr\s+-d|awk|sed|xargs|cut)\b")
STR_SUBJECT = re.compile(r"""\b(?:st|case)\s+['"]?$""")
TEST_OPEN = re.compile(r"(?:^|\s)\[\[?\s")
STR_OP_AFTER = re.compile(r"""^['"]?\s+(?:==?|!=)\s""")
STR_OP_BEFORE = re.compile(r"""\s(?:==?|!=)\s+['"]?$""")
STUB_WC = re.compile(r"#!/bin/(?:ba)?sh[^\n]*?/usr/bin/wc\b")
EARLY = re.compile(r"\|\s*(?:grep\s+(?:-[A-Za-z]*[qm]\w*|--quiet\b|--max-count\b)|head\b)")
PIPEFAIL = re.compile(r"^\s*[^#\n]*\bset\b[^#\n]*(?:-[A-Za-z]*o\s+pipefail|pipefail)", re.M)
RAW = re.compile(r"#\s*wc-raw:\s*\S")
SMALL = re.compile(r"#\s*pipe-small:\s*\S")
DRAINED = re.compile(r"\|\|\s*true\b")


def string_compared(line: str, m: re.Match) -> bool:
    """Whether the substitution `m` is itself an operand of a string compare: `st`'s or `case`'s
    subject, or a side of `=`/`==`/`!=` inside the `[`/`[[` test that holds it. A numeric
    operator, an arithmetic context or a compare elsewhere on the line does not count."""
    pre, post = line[:m.start()], line[m.end():]
    if STR_SUBJECT.search(pre):
        return True
    opener = None
    for opener in TEST_OPEN.finditer(pre):
        pass
    if opener is None or "]" in pre[opener.end():]:
        return False
    return bool(STR_OP_AFTER.search(post) or STR_OP_BEFORE.search(pre))


def hazards(text: str, lines: set[int] | None = None) -> list[tuple[int, str, str]]:
    """(line number, rule, line) per refused line of one script; `lines` restricts to those numbers."""
    pipefail = bool(PIPEFAIL.search(text))
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if (lines is not None and n not in lines) or line.lstrip().startswith("#"):
            continue
        for m in WC_SUB.finditer(line):
            if NORMALISE.search(m.group("in")) or RAW.search(line):
                continue
            if string_compared(line, m):
                out.append((n, "wc-compare", line.strip()))
                break
        if STUB_WC.search(line) and not re.search(r"\|\s*tr\s+-d", line):
            out.append((n, "wc-stub", line.strip()))
        if pipefail and EARLY.search(line) and not DRAINED.search(line) and not SMALL.search(line):
            out.append((n, "early-pipe", line.strip()))
    return out


REPAIR = {
    "wc-compare": "strip the count: `| wc -l | tr -d ' '` (BSD wc pads, so a raw string compare fails on macOS)",
    "wc-stub": "strip the host wc's padding (`| tr -d ' '`) before the stub shapes its count",
    "early-pipe": "feed the reader a here-string (`grep -q PAT <<<\"$x\"`), or mark `# pipe-small: <why>`",
}


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL)


def added_lines(diff: str) -> dict[str, set[int]]:
    """path -> new-side line numbers a `git diff -U0` adds."""
    out: dict[str, set[int]] = {}
    path = None
    for ln in diff.splitlines():
        if ln.startswith("+++ "):
            path = ln[6:] if ln.startswith("+++ b/") else None
        elif ln.startswith("@@") and path:
            m = re.match(r"@@ -\S+ \+(\d+)(?:,(\d+))? @@", ln)
            if m:
                a, c = int(m.group(1)), int(m.group(2) if m.group(2) is not None else 1)
                out.setdefault(path, set()).update(range(a, a + c))
    return out


def scan(base: str, head: str = "HEAD") -> list[str]:
    """`path:line: rule: text -- repair` per refused added line in tools/**/*.sh, base...head."""
    diff = _git("diff", "-U0", "--no-renames", "--diff-filter=AM", f"{base}...{head}",
                "--", ":(glob)tools/**/*.sh")
    res = []
    for path, nums in sorted(added_lines(diff).items()):
        for n, rule, text in hazards(_git("show", f"{head}:{path}"), nums):
            res.append(f"{path}:{n}: {rule}: {text} -- {REPAIR[rule]}")
    return res


def self_test() -> int:
    fails = []

    def st(got, want, name):
        if got != want:
            fails.append(f"{name}: got {got!r}, want {want!r}")

    def rules(text):
        return [r for _, r, _ in hazards(text)]

    pf = "#!/bin/bash\nset -uo pipefail\n"
    # wc-compare: the line #3455 (003f89cf9c) added, which reached the macOS seat red.
    raw = 'st "$(mg status --porcelain | wc -l)" 0 "and the in-place run leaves the work tree clean"\n'
    st(rules(raw), ["wc-compare"], "the raw wc string compare #3455 added is refused")
    st(rules(raw.replace("wc -l)", "wc -l | tr -d ' ')")), [], "the stripped compare passes (null)")
    st(rules('[ "$(wc -l <"$f")" = 3 ] || x\n'), ["wc-compare"], "a bracket string compare of a raw wc is refused")
    st(rules('[ "$(wc -l <"$f" | tr -d " ")" = 3 ] || x\n'), [], "a stripped bracket compare passes (null)")
    st(rules('[ "$(wc -l <"$f")" -eq 3 ] || x\n'), [], "a numeric test reads a number, not a string (null)")
    # The exemption is the compare that holds the substitution, never the line (verdict/3639).
    st(rules('[ "$(wc -l <f)" -eq 3 ] || [ "$a" = b ]\n'), [],
       "a numeric compare of wc beside an unrelated string compare passes (null)")
    st(rules('st "$(a | wc -l)" 0 m && [ $n -eq 0 ]\n'), ["wc-compare"],
       "a numeric test elsewhere on the line does not excuse an st compare")
    st(rules('[ "$(wc -l <f)" = 3 ] || exit $((1))\n'), ["wc-compare"],
       "an arithmetic expansion elsewhere on the line does not excuse a bracket compare")
    st(rules('[ 3 = "$(wc -l <f)" ]\n'), ["wc-compare"], "a raw wc on the right of = is refused")
    st(rules('[ "$(wc -l <f)" != 3 ]\n'), ["wc-compare"], "!= is a string compare")
    st(rules('[[ $(wc -l <f) == 3 ]]\n'), ["wc-compare"], "[[ == ]] is a string compare")
    st(rules('[ "$a" = b ] && [ "$(wc -l <f)" = 3 ]\n'), ["wc-compare"],
       "a closed test before the compare does not hide it: the test holding the substitution is the last opener")
    st(rules('case "$(wc -l <f)" in 3) x;; esac\n'), ["wc-compare"], "a case subject is a string compare")
    st(rules('(( $(wc -l <f) == 3 ))\n'), [], "an arithmetic == reads a number (null)")
    st(rules('n=$(( $(wc -l <f) + 1 ))\n'), [], "an arithmetic expansion reads a number (null)")
    st(rules('[ -n "$x" ] && echo "$(wc -l <f)" = 3\n'), [], "an = outside any test bracket is no compare (null)")
    # A generated spelling corpus: bracket x quoting x side x operator x unrelated tail.
    corpus = bad = 0
    for o, c in (("[", "]"), ("[[", "]]")):
        for q in ('"', ""):
            sub = f"{q}$(wc -l <f){q}"
            for op in ("=", "==", "!=", "-eq", "-ne", "-lt", "-gt", "-le", "-ge"):
                for tail in ("", " && [ $n -eq 0 ]", " || exit $((1))", " || [ \"$a\" = b ]"):
                    for text in (f"{o} {sub} {op} 3 {c}{tail}\n", f"{o} 3 {op} {sub} {c}{tail}\n"):
                        corpus += 1
                        want = ["wc-compare"] if op in ("=", "==", "!=") else []
                        if rules(text) != want:
                            bad += 1
                            st(rules(text), want, f"corpus: {text.strip()}")
    st((corpus, bad), (288, 0), "the spelling corpus is judged by the compare holding the substitution")
    st(rules('n=$(wc -l <"$f")\n'), [], "a bare assignment is not a compare (null)")
    st(rules(raw.rstrip() + "  # wc-raw: asserts the stub's padding\n"), [], "a wc-raw reason passes (null)")
    st(rules(raw.rstrip() + "  # wc-raw:\n"), ["wc-compare"], "a wc-raw marker with no reason does not excuse")
    st(rules('# st "$(a | wc -l)" 0 x\n'), [], "a comment line is skipped (null)")
    st(rules('st "$(printf x | wc -c | awk \'{print $1}\')" 1 x\n'), [], "an awk-normalised count passes (null)")
    # wc-stub: 1386441425's padding stub, which doubled BSD wc's own padding.
    stub = """PW=$(mktemp -d); printf '#!/bin/sh\\n/usr/bin/wc "$@" | sed "s/^/       /"\\n' > "$PW/wc"\n"""
    st(rules(stub), ["wc-stub"], "the stub that pads a host wc's already padded count is refused")
    st(rules("""printf '#!/bin/sh\\nn=$(/usr/bin/wc "$@" | tr -d " ")\\nprintf "%%8s\\\\n" "$n"\\n' > "$PW/wc"\n"""), [],
       "c8780ea33d's stub, which strips before it pads, passes (null)")
    st(rules('/usr/bin/wc -l <x\n'), [], "an absolute wc outside a stub text is not a stub (null)")
    # early-pipe: the carry-tip read cb803e9eed^ had in app_approve.sh.
    pipe = '  printf \'%s\\n\' "$heads" | grep -q "^$h[[:space:]]refs/heads/" || ours=0\n'
    st(rules(pf + pipe), ["early-pipe"], "printf | grep -q under pipefail is refused")
    st(rules(pf + '  grep -q "^$h[[:space:]]refs/heads/" <<<"$heads" || ours=0\n'), [],
       "the here-string that fixed it passes (null)")
    st(rules("#!/bin/bash\nset -u\n" + pipe), [], "a file without pipefail has no SIGPIPE status (null)")
    st(rules(pf + 'x | grep -q y || true\n'), [], "a drained pipe passes (null)")
    st(rules(pf + 'x | grep -q y  # pipe-small: one line\n'), [], "a pipe-small reason passes (null)")
    st(rules(pf + 'x | grep -q y  # pipe-small:\n'), ["early-pipe"], "a marker with no reason does not excuse")
    st(rules(pf + 'x | head -1\n'), ["early-pipe"], "head is an early-exit reader")
    st(rules(pf + 'x | grep -m1 y\n'), ["early-pipe"], "grep -m is an early-exit reader")
    st(rules(pf + 'x | grep -c y\n'), [], "a reader that reads to the end passes (null)")
    st(rules("#!/bin/bash\nset -o errexit -o pipefail\nx | grep -q y\n"), ["early-pipe"], "long-form pipefail counts")
    st(rules(pf + '# x | grep -q y\n'), [], "a comment passes (null)")
    # The diff scope, over a scratch repository: only added lines of tools/**/*.sh.
    import tempfile
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
    from throwaway_git import throwaway_git_init
    with tempfile.TemporaryDirectory() as d:
        env = throwaway_git_init(d, "-q")
        root = Path(d)
        (root / "tools/sub").mkdir(parents=True)
        old = pf + 'old | grep -q y\n'
        (root / "tools/a.sh").write_text(old)

        def run(*a):
            return subprocess.run(a, cwd=d, env=env, capture_output=True, text=True, check=True).stdout

        run("git", "add", "-A")
        run("git", "commit", "-qm", "base")
        run("git", "branch", "-M", "main")
        run("git", "checkout", "-qb", "b")
        (root / "tools/a.sh").write_text(old + 'new | grep -q y\n')
        (root / "tools/sub/b.sh").write_text(pf + raw)
        (root / "tools/c.py").write_text("x | grep -q y\n")
        (root / "d.sh").write_text(pf + "x | grep -q y\n")
        run("git", "add", "-A")
        run("git", "commit", "-qm", "branch")
        res = subprocess.run([sys.executable, "-I", __file__, "--check", "--base", "main"], cwd=d, env=env,
                             capture_output=True, text=True)
        got = [x.split(" -- ")[0] for x in res.stdout.splitlines()]
        st((res.returncode, got), (1, ["tools/a.sh:4: early-pipe: new | grep -q y",
                                       "tools/sub/b.sh:3: wc-compare: " + raw.strip()]),
           "--check names the added hazards in nested tools/**/*.sh only: not the old line, a .py or a root .sh")
        run("git", "checkout", "-q", "main")
        run("git", "checkout", "-qb", "ok")
        (root / "tools/a.sh").write_text(old + "new <<<x grep -q y\n")
        run("git", "commit", "-qam", "ok")
        res = subprocess.run([sys.executable, "-I", __file__, "--check", "--base", "main"], cwd=d, env=env,
                             capture_output=True, text=True)
        st((res.returncode, res.stdout), (0, ""), "--check on a branch adding no hazard passes (null)")
        st(subprocess.run([sys.executable, "-I", __file__], cwd=d, env=env, capture_output=True).returncode, 2,
           "no arm prints the usage, rc 2")
    for f in fails:
        print("FAIL", f)
    print("shell_hazard self-test:", "FAILED" if fails else "ok")
    return 1 if fails else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    if "--check" in sys.argv:
        base = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else "origin/main"
        head = sys.argv[sys.argv.index("--head") + 1] if "--head" in sys.argv else "HEAD"
        hits = scan(base, head)
        if hits:
            print("\n".join(hits))
        sys.exit(1 if hits else 0)
    print(__doc__)
    sys.exit(2)
