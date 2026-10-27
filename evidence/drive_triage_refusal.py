import sys, importlib.util
WT = sys.argv[1]
spec = importlib.util.spec_from_file_location("roster_edit", WT + "/tools/audit/seat/roster_edit.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

REL = "dev/programme/triage/s6-batch40.md"
HEAD_SRC = open(WT + "/" + REL, encoding="utf-8").read()

# mutation 2: the P211 verdict line changed to DEFER
def_v = HEAD_SRC.replace("Verdict: ACCEPT narrowed, in two carries.",
                         "Verdict: DEFER narrowed, in two carries.", 1)
assert def_v != HEAD_SRC, "verdict substitution matched nothing"
# mutation 3: the heading renamed
head_v = HEAD_SRC.replace("## P211: the push-stuck guard", "## P211 (relay P1): the push-stuck guard", 1)
assert head_v != HEAD_SRC, "heading substitution matched nothing"

TEXT_CITE = ("triage P211 (V124): accept the lease half -> "
             "triage: dev/programme/triage/s6-batch40.md#P211")
TEXT_NULL = "R10-PREPR-CAP: add a self-test arm to the flock-wrap path."

arms = [
    ("1 corrected file (ACCEPT)",      HEAD_SRC, [TEXT_CITE]),
    ("2 verdict -> DEFER",              def_v,    [TEXT_CITE]),
    ("3 heading renamed",               head_v,   [TEXT_CITE]),
    ("4 null control (no proposal)",    HEAD_SRC, [TEXT_NULL]),
    ("5 unmodified main (pre-fix)",     None,     [TEXT_CITE]),
]
for name, src, texts in arms:
    if src is None:
        import subprocess
        r = subprocess.run(["git","-C",WT,"show","origin/main:"+REL],
                           capture_output=True, text=True)
        src = r.stdout
    print(f"RESULT arm {name}: {m.triage_refusal(texts, lambda p, s=src: s)!r}")
