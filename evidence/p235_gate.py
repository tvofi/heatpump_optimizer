import sys, pathlib
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import roster_edit as r
p = "dev/programme/triage/s6-batch47.md"
src = pathlib.Path(sys.argv[1], p).read_text()
txt = [f"carry text for V149 triage: {p}#P235"]
print("RESULT committed verdict=", r.ruling_verdict(src, "P235"), "refusal=", r.triage_refusal(txt, lambda q: src if q == p else None))
mut = src.replace("Verdict: DEFER", "Verdict: ACCEPT", 1)
print("RESULT mutant(ACCEPT) verdict=", r.ruling_verdict(mut, "P235"), "refusal=", r.triage_refusal(txt, lambda q: mut if q == p else None))
mut2 = src.replace("Verdict: DEFER", "Verdict: REJECT", 1)
print("RESULT mutant(REJECT) refusal=", r.triage_refusal(txt, lambda q: mut2 if q == p else None))
print("RESULT null(base, no file) refusal=", r.triage_refusal(txt, lambda q: None))
print("RESULT wrong-pid refusal=", r.triage_refusal([f"x triage: {p}#P236"], lambda q: src))
