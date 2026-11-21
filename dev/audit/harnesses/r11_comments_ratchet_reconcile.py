"""Reconcile tests/comment_ratchet.py's long units with the three D5 round-11 finders' harnesses.

Usage: PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r11_comments_ratchet_reconcile.py EXPORT
EXPORT is a directory holding `git archive origin/plan/r11 dev/audit/rounds/round11/D5/s7
dev/audit/rounds/round11/D5/s8 dev/audit/rounds/round11/D5/s9`. The finders' harnesses stay out of
the tree, so they are imported from the export. Run it from the repository root.

The comparison is unit by unit, over each harness's own cells inside the ratchet's scope. s9 is
comments.py's `long_sentences`, s7 is m4_comments.py's `paragraphs` and `long_sentences`, and s8 is
m4_ledger.py's `max_sentence_words` over 40. A unit counts when one of its sentences is long.
It prints:
  RESULT <h>_harness=<n> and RESULT <h>_script=<n>: long units on harness h's cells, by each side.
  RESULT harness_only=<n> and RESULT script_only=<n>: the units one side flags and the other does not.
  RESULT class_<rules>=<n>: each harness-only unit, classed by the smallest set of the script's rules
  that, reverted in memory, makes the script flag it too.
    colon     the harness counts the `:` of a `#:` marker as a word
    banner    the harness joins a `--- title ---` banner line to the sentence after it
    trailing  the harness joins a trailing comment on a code line to the block below it
    rule      the harness counts a rule line as a word
  UNCLASSED <h> <file:line>: a harness-only unit no reverted rule set explains.
Null control: with every rule reverted, the classes sum to harness_only less the UNCLASSED lines.
"""
import importlib.util, itertools, subprocess, sys
from collections import Counter

sys.path[:0] = ["tools/audit", "tests"]
import comment_ratchet as CR  # noqa: E402
import text_ledger as TL  # noqa: E402

X = sys.argv[1].rstrip("/") + "/dev/audit/rounds/round11/D5/"


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, X + rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


s9, s7, s8 = load("s9", "s9/comments.py"), load("s7", "s7/m4_comments.py"), load("s8", "s8/m4_ledger.py")


def cells(seat):
    out = subprocess.check_output([sys.executable, "tools/audit/check_scopes.py", "--repo", ".", "--ref", "HEAD",
                                   "--seat", seat], text=True)
    return sorted({l.split("\t")[2] for l in out.splitlines() if l.count("\t") >= 2})


HARNESSES = {
    "s9": (cells("D5-s9"), lambda f, t, u: bool(s9.long_sentences(u[3]))),
    "s7": (s7.SEAT_FILES, lambda f, t, u: bool(s7.long_sentences(s7.paragraphs(u[2], u[3], t.splitlines(), u[1])))),
    "s8": (cells("D5-s8"), lambda f, t, u: s8.max_sentence_words(u[3]) > 40),
}
TEXT = {f: open(f, encoding="utf-8").read() for files, _ in HARNESSES.values() for f in files if CR.in_scope(f)}
THEIRS = {}
for h, (files, fn) in HARNESSES.items():
    for f in files:
        if f in TEXT:
            t = TEXT[f]
            THEIRS[h, f] = {u[1] for u in TL.units_of(f, t, "D5") if u[2] != "file" and fn(f, t, u)}


def script_side():
    return {key: {line for line, _q in CR.long_units(key[1], TEXT[key[1]])} for key in THEIRS}


ORIG = {n: getattr(CR, n) for n in ("_strip_marker", "_is_heading", "_split_trailing", "_is_rule")}
REVERT = {
    "colon": ("_strip_marker", lambda l: (": " if l.lstrip().startswith("#:") else "") + ORIG["_strip_marker"](l)),
    "banner": ("_is_heading", lambda t: False),
    "trailing": ("_split_trailing", lambda path, src, line, kind, body: [body]),
    "rule": ("_is_rule", lambda t: False),
}


def harness_only(mine):
    return {(h, f, l) for (h, f), lines in THEIRS.items() for l in lines - mine[h, f]}


mine = script_side()
for h in HARNESSES:
    print(f"RESULT {h}_harness={sum(len(v) for (k, _f), v in THEIRS.items() if k == h)}")
    print(f"RESULT {h}_script={sum(len(v) for (k, _f), v in mine.items() if k == h)}")
left = harness_only(mine)
print(f"RESULT harness_only={len(left)}")
print(f"RESULT script_only={sum(len(mine[k] - THEIRS[k]) for k in THEIRS)}")
classes = Counter()
for k in range(1, len(REVERT) + 1):
    for combo in itertools.combinations(REVERT, k):
        if not left:
            break
        for name in combo:
            setattr(CR, *REVERT[name])
        try:
            hit = left - harness_only(script_side())
        finally:
            for n, fn in ORIG.items():
                setattr(CR, n, fn)
        if hit:
            classes["+".join(combo)] += len(hit)
            left -= hit
for name, n in sorted(classes.items()):
    print(f"RESULT class_{name.replace('+', '_')}={n}")
for h, f, l in sorted(left):
    print(f"UNCLASSED {h} {f}:{l}")
