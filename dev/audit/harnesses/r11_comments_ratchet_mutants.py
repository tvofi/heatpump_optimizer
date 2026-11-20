"""Mutation proof for tests/comment_ratchet.py: each predicate the design names, broken in place.

Usage: python3 dev/audit/harnesses/r11_comments_ratchet_mutants.py   (from the repository root, clean tree)
For each mutant the script rewrites tests/comment_ratchet.py, runs `--self-test`, prints one line
and restores the file, also on an error. A mutant is KILLED when the self-test exits non-zero; the
line names the self-test arms that failed. An empty arm list means a crash, which also kills.
  RESULT killed=<n> survived=<n>
Null control: the unmutated script's self-test exits 0, printed as RESULT baseline_rc=0.
"""
import subprocess, sys

P = "tests/comment_ratchet.py"
MUTANTS = [
    ("> 40 compare", "if len(s.split()) > MAX_WORDS), None)", "if len(s.split()) >= MAX_WORDS), None)"),
    ("per-file compare", "if old is not None and len(head[f]) > len(old):",
     "if old is not None and len(head[f]) > len(old) + 1:"),
    ("total compare", "    if th > tb:", "    if th > tb + 1:"),
    ("new-file branch", "if old is not None and len(head[f]) > len(old):",
     "old = old or []\n        if len(head[f]) > len(old):"),
    ("base resolution", "    if not ref:\n        return None\n", '    ref = ref or "HEAD"\n'),
    (".sh marker strip", 'for m in ("#:", "#", "//", "/*", "*/", "*"):', 'for m in ("#:", "//", "/*", "*/", "*"):'),
    ("text-only code arm", '                body[0].value.value = ""', "                pass"),
    ("text-only hunk arm", 'if op != "equal" and i2 - i1 != j2 - j1)', 'if op != "equal" and False)'),
    ("comment code strip", 'text = text.replace(piece.strip(), " ", 1)', "pass"),
]


def self_test():
    r = subprocess.run([sys.executable, P, "--self-test"], capture_output=True, text=True)
    return r.returncode, [l[5:] for l in r.stdout.splitlines() if l.startswith("FAIL ")]


src = open(P, encoding="utf-8").read()
print(f"RESULT baseline_rc={self_test()[0]}")
killed = survived = 0
try:
    for name, old, new in MUTANTS:
        if src.count(old) != 1:
            sys.exit(f"mutant {name!r}: its site is not exactly once in {P}")
        open(P, "w", encoding="utf-8").write(src.replace(old, new))
        rc, fails = self_test()
        killed += rc != 0
        survived += rc == 0
        print(("KILLED  " if rc else "SURVIVED"), name, "|", "; ".join(fails))
finally:
    open(P, "w", encoding="utf-8").write(src)
print(f"RESULT killed={killed} survived={survived}")
