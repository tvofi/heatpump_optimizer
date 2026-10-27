import sys, pathlib
sys.path.insert(0, "/Users/timmalmstrom/hpo-seats/r10s6/rev-2879/tools/audit/seat")
import roster_edit as R
src = pathlib.Path("/Users/timmalmstrom/hpo-seats/r10s6/rev-2879/dev/programme/triage/s6-batch37.md").read_text()
print("P205 verdict:", R.ruling_verdict(src, "P205"))
# the gate's own refusal path, with the ruling read from the committed file
def reader(path):
    return src if path.endswith("s6-batch37.md") else None
txt = ["proposal P205: a STOP result body reads as an orphan handoff. triage: dev/programme/triage/s6-batch37.md#P205"]
print("refusal on committed file:", R.triage_refusal(txt, reader))
# mutant: flip the verdict line to DEFER
mut = src.replace("Verdict: ACCEPT narrowed", "Verdict: DEFER narrowed", 1)
print("mutant verdict:", R.ruling_verdict(mut, "P205"))
print("mutant refusal:", R.triage_refusal(txt, lambda p: mut))
print("missing-file refusal:", R.triage_refusal(txt, lambda p: None))
print("P999 refusal:", R.triage_refusal(
    ["proposal P999: x. triage: dev/programme/triage/s6-batch37.md#P999"], reader))
