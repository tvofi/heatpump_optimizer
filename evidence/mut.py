import sys, re
sys.path.insert(0, "tools/audit/seat")
import roster_edit as r
src = open(sys.argv[1]).read()
P = "dev/programme/triage/s6-batch51.md"
for p in ["P249","P250","P251","P252","P253","P254"]:
    print("verdict", p, r.ruling_verdict(src, p))
def run(label, s):
    rd = lambda path: s if path == P else None
    for p in ["P249","P250","P251","P252","P253"]:
        t = f"carry text. triage: {P}#{p}"
        print(label, p, r.triage_refusal([t], rd))
run("committed", src)
run("absent", None)
run("mut249", re.sub(r"(## P249:.*?\n\nVerdict: )REJECT", r"\1ACCEPT", src, flags=re.S))
run("mut253", re.sub(r"(## P253:.*?\n\nVerdict: )ACCEPT", r"\1REJECT", src, flags=re.S))
run("mut253-noverdict", re.sub(r"(## P253:.*?\n\n)Verdict: ACCEPT", r"\1Ruling: ACCEPT", src, flags=re.S))
