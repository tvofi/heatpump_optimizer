import re,sys,pathlib
src=pathlib.Path("tools/audit/seat/merge_train.py").read_text()
m=re.search(r'^FAILED_SCRIPT = re\.compile\((r".*?")\)$',src,re.M); rx=re.compile(eval(m.group(1)))
print("FAILED_SCRIPT =",rx.pattern)
for l in [">>> FAILED: tests/entities.py",">>> ENDED BEFORE ITS SUMMARY: tests/entities.py (exit 1; last line reached: OSError)",">>> ENDED BEFORE ITS SUMMARY: python3 tests/entities.py (exit 1; last line reached: OSError)"]:
    print(repr(l),"->",rx.findall(l))
