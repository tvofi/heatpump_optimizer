"""Reconcile tests/comment_ratchet.py's production long units with the D5-s3 and D5-s4 finders' harnesses.

Usage: PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r11_comments_production_reconcile.py EXPORT
           [--ref REF] [--show] [FILE ...]
EXPORT is a directory holding `git archive origin/plan/r11 dev/audit/rounds/round11/D5/s3
dev/audit/rounds/round11/D5/s4`. The finders' harnesses stay out of the tree, so their rules are
imported from the export. Run it from the repository root. FILE is a path under the package (or
`www/heatpump-optimizer-card.js`); none means every production file in the ratchet's scope. REF reads
the files at a commit instead of the worktree.

The harness side is each finder's own rule on its own cell: s3 is c5_long.py's `long_sentences` over
`[_a-i]*.py`, and s4 is comments.py's `clean` plus `text_ledger.sentences` over `[j-z]*.py` and the card.
A unit counts when one of its sentences has more than 40 words. The script side is
`comment_ratchet.long_units`. Each part of R11-SEAM-comments-production reads its files here at its
base and its head.
It prints:
  FILE <file> harness=<n> ratchet=<n>, then with --show one LONG line per sentence a harness flags.
  RESULT harness_long=<n> and RESULT ratchet_long=<n>: the totals over the files read.
  RESULT ratchet_above_harness_files=<n>: files where the script flags more units than the harness.
    The script splits a unit into paragraphs at list items, indented blocks, banners and trailing
    comments, where both harnesses read one sentence across them, so this reads 0.
Null control: --perturb appends a 41-word comment to every file read, in memory; both totals then
rise by the number of files read.
"""
import importlib.util, subprocess, sys

sys.path[:0] = ["tools/audit", "tests"]
import comment_ratchet as CR  # noqa: E402
import text_ledger as TL  # noqa: E402

X = sys.argv[1].rstrip("/") + "/dev/audit/rounds/round11/D5/"
ARGS = sys.argv[2:]
REF = ARGS[ARGS.index("--ref") + 1] if "--ref" in ARGS else None
FILES = [a for i, a in enumerate(ARGS) if not a.startswith("--") and (i == 0 or ARGS[i - 1] != "--ref")]
PLANT = "\n# " + " ".join(["word"] * 40) + " end.\n"


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, X + rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


s3, s4 = load("s3", "s3/c5_long.py"), load("s4", "s4/comments.py")


def harness_long(path, text):
    """[(line, sentence)] for each unit the cell's own finder flags, its first long sentence."""
    out = []
    for _uid, line, kind, body in TL.units_of(path, text, "D5"):
        if s3.CELL.match(path):
            longs = s3.long_sentences(body)
        else:
            longs = [s for s in TL.sentences(s4.clean(body, kind)) if len(s.split()) > 40]
        if longs:
            out.append((line, longs[0]))
    return out


def main():
    files = [f if f.startswith("custom") else CR.PKG + f for f in FILES] or [
        f for f in CR.tracked(REF) if not f.startswith("tests/")]
    texts = CR.blobs(REF, files) if REF else CR.head_texts(files)
    h_tot = r_tot = above = 0
    for f in files:
        text = texts[f] + (PLANT if "--perturb" in ARGS and f.endswith(".py") else "")
        if "--perturb" in ARGS and f.endswith(".js"):
            text += PLANT.replace("#", "//")
        h, r = harness_long(f, text), CR.long_units(f, text)
        h_tot, r_tot, above = h_tot + len(h), r_tot + len(r), above + (len(r) > len(h))
        print(f"FILE {f[len(CR.PKG):]} harness={len(h)} ratchet={len(r)}")
        if "--show" in ARGS:
            for line, s in h:
                print(f"LONG {f[len(CR.PKG):]}:{line} {len(s.split())}w: {' '.join(s.split()[:14])} ...")
    print(f"RESULT files={len(files)} ref={REF or 'worktree'}")
    print(f"RESULT harness_long={h_tot}")
    print(f"RESULT ratchet_long={r_tot}")
    print(f"RESULT ratchet_above_harness_files={above}")


if __name__ == "__main__":
    main()
