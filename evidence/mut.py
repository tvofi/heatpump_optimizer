import sys, pathlib
sys.path.insert(0, "tools/audit/seat")
import roster_edit as r
p = "dev/programme/triage/s6-batch50.md"
src = pathlib.Path(p).read_text()
t = [f"carry item. triage: {p}#P248"]
print("committed:", r.ruling_verdict(src, "P248"), "|", r.triage_refusal(t, lambda x: src))
mut = src.replace("Verdict: DEFER.", "Verdict: ACCEPT.", 1)
print("mutant ACCEPT:", r.ruling_verdict(mut, "P248"), "|", r.triage_refusal(t, lambda x: mut))
mut2 = src.replace("Verdict: DEFER.", "Verdict DEFER.", 1)
print("mutant no-verdict-line:", r.ruling_verdict(mut2, "P248"), "|", r.triage_refusal(t, lambda x: mut2))
print("null (absent):", r.triage_refusal(t, lambda x: None))
