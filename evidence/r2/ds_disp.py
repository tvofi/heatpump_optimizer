"""Reviewer harness (review-2061 r2): direct-push disposition cases + attacks."""
import importlib.util, sys
R="/Users/timmalmstrom/hpo-seats/review-2061"
sys.path[:0]=[R+"/wt/tests"]
p=sys.argv[1]; s=importlib.util.spec_from_file_location("dsx",p); ds=importlib.util.module_from_spec(s); s.loader.exec_module(ds)
row=ds.ROW_DIR+"/1998.md"
def c(sha,files,subj="merge"): return {"sha":sha+"0"*(40-len(sha)),"parents":2,"subject":subj,"body":"","files":files}
allow=ds.direct_pushes("- 618d014: merged by hand; rows in #1999\n")
cases={
 "rows-only":([c("0a60e06",[row])],{}),
 "code+allow":([c("618d014",["tools/policy/counts.mjs"])],allow),
 "code-no-allow":([c("618d014",["tools/policy/counts.mjs"])],{}),
 "rows+script":([c("0a60e06",[row,"tests/run.sh"])],{}),
 "files-unknown":([c("0a60e06",None)],{}),
 "files-empty":([c("0a60e06",[])],{}),
 "direct-pushes.md-itself":([c("0a60e06",["dev/programme/delivery/direct-pushes.md"])],{}),
 "pre-move-row":([c("0a60e06",["docs/delivery/1998.md"])],{}),
 "row-lookalike":([c("0a60e06",["dev/programme/delivery/1998.md.bak"])],{}),
 "nested-row":([c("0a60e06",["dev/programme/delivery/x/1998.md"])],{}),
 "allow-other-sha":([c("618d015",["x.py"])],allow),
 "allow-6hex":([c("618d01",["x.py"])],ds.direct_pushes("- 618d01: short\n")),
}
for k,(cs,al) in cases.items():
    m,b=ds.collect(cs,allow=al) if "allow" in ds.collect.__code__.co_varnames else ds.collect(cs)
    v=ds.classify(m,[],unattributed=b)["verdict"]
    print(f"RESULT {k}: disp={[x.get('disposition','-') for x in b]} verdict={v}")
