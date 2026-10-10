import sys, tempfile
from pathlib import Path
WT=Path("/Users/timmalmstrom/hpo-seats/r9rev-2111/wt")
sys.path.insert(0,str(WT/"tools/audit/seat")); sys.path.insert(0,str(WT/"tests"))
import importlib.util
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m; spec.loader.exec_module(m); return m
base=load(str(WT/"tools/audit/seat/_baseline_rr.py"),"_baseline_rr")
head=load(str(WT/"tools/audit/seat/record_row.py"),"record_row_head")
API="abcdef1234567890abcdef1234567890abcdef12"
for tag,mod in (("BASELINE(7cd5a588c, pre-fix)",base),("HEAD(3f82aba33, fixed)",head)):
    root=Path(tempfile.mkdtemp(prefix="be-"))
    (root/"dev/programme/delivery").mkdir(parents=True)
    (root/"dev/programme/delivery/2001.md").write_text(
      "- [#2001](https://github.com/tvofi/heatpump_optimizer/pull/2001) — **open**, fix: stale\n")
    m={"number":2001,"title":"fix: stale","state":"closed","head_ref":"x","merge_sha":API}
    plan=mod.plan_merges([m],root,roster=None)
    wrote=mod.write_rows(plan,root)
    after=(root/"dev/programme/delivery/2001.md").read_text()
    print(f"RESULT {tag}: plan={[p['number'] for p in plan]} wrote={wrote} "
          f"row_still_open={'**open**' in after} row_merged={'**merged `' in after}")
