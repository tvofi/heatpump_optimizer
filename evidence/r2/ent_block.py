"""Run the PR's own entities.py direct-push check block, verbatim, against a delivery_status copy."""
import importlib.util, sys, re
R="/Users/timmalmstrom/hpo-seats/review-2061"; sys.path[:0]=[R+"/wt/tests"]
src=open(R+"/wt/tests/entities.py").read()
a=src.index("# R9-RO-9a: a two-parent direct push"); b=src.index('R.check(\n    "a release stamp alone is EMPTY', a)
block=src[a:b]
s=importlib.util.spec_from_file_location("dsx",sys.argv[1]); ds=importlib.util.module_from_spec(s); s.loader.exec_module(ds)
class _R:
    def check(self,name,ok,detail=""): print(("ok  " if ok else "FAIL"), name[:70], "" if ok else detail)
exec(block,{"_ds":ds,"R":_R(),"_DS_ROWED":["a row for [#101](https://github.com/o/r/pull/101) and #102"]})
