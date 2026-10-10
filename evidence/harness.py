import sys, tempfile, re, json
from pathlib import Path
WT = Path("/Users/timmalmstrom/hpo-seats/r9rev-2111/wt")
sys.path.insert(0, str(WT/"tools/audit/seat")); sys.path.insert(0, str(WT/"tests"))
import record_row as R, delivery_status as DS

def R_(label, cond, extra=""):
    print(f"RESULT {'PASS' if cond else 'FAIL'}  {label}  {extra}")
    return cond

fails=0
def chk(label, cond, extra=""):
    global fails
    if not R_(label, cond, extra): fails+=1

API_SHA = "abcdef1234567890abcdef1234567890abcdef12"   # 40-hex, API's merge_sha
OTHER   = "99"*20
root = Path(tempfile.mkdtemp(prefix="rowstale-"))
(root/"dev/programme/delivery").mkdir(parents=True)
def put(n, text): (root/f"dev/programme/delivery/{n}.md").write_text(text)
def get(n): return (root/f"dev/programme/delivery/{n}.md").read_text()

# ---------- (1) status-aware, and REWRITES rather than skips ----------
put(2001, "- [#2001](https://github.com/tvofi/heatpump_optimizer/pull/2001) — **open**, fix: stale title\n")
m = {"number":2001,"title":"fix: real api title","state":"closed","head_ref":"fix/x","merge_sha":API_SHA}
plan = R.plan_merges([m], root, roster=None)
chk("Q1 stale open row for a MERGED PR IS planned", [p["number"] for p in plan]==[2001], f"plan={[p['number'] for p in plan]}")
wrote = R.write_rows(plan, root)
chk("Q1 apply REWRITES (does not skip) the existing file", wrote==["dev/programme/delivery/2001.md"], f"wrote={wrote}")
chk("Q1 rewritten line == row_line() byte for byte", get(2001)==R.row_line(2001,m["title"],API_SHA,None)+"\n")
chk("Q1 rewritten row records the API sha", ("**merged `%s`**"%API_SHA[:7]) in get(2001))

# ---------- (2) idempotency ----------
plan2 = R.plan_merges([m], root, roster=None)
chk("Q2 re-plan after rewrite is empty (idempotent)", plan2==[], f"plan2={plan2}")
chk("Q2 write_rows on the merged row is a no-op", R.write_rows([{"number":2001,"path":R.row_path(2001),"line":R.row_line(2001,m["title"],API_SHA,None)}], root)==[])
before = get(2001)
# a row whose sha DIFFERS from the API's is corrected
put(2002, R.row_line(2002,"fix: misrowed",OTHER,None)+"\n")
m2={"number":2002,"title":"fix: misrowed","state":"closed","head_ref":"","merge_sha":API_SHA}
plan3=R.plan_merges([m2], root, roster=None)
chk("Q2 wrong-sha row is planned", [p["number"] for p in plan3]==[2002])
w3=R.write_rows(plan3, root)
chk("Q2 wrong-sha row corrected to the API's sha", w3==["dev/programme/delivery/2002.md"] and API_SHA[:7] in get(2002))
chk("Q2 corrected row is still one line", len(get(2002).splitlines())==1)
chk("Q2 row at the API sha is left byte-identical by a re-plan", R.plan_merges([m], root, roster=None)==[] and get(2001)==before)

# ---------- (3) grammar ----------
GRP_ROSTER={"groups":[{"group":"R9-X","resume":{"branch":"fix/x"}}]}
put(2003, "- [#2003](https://github.com/tvofi/heatpump_optimizer/pull/2003) — **open**, old\n")
m3={"number":2003,"title":"fix: title with | pipe  and\nnewline refs #999","state":"closed","head_ref":"fix/x","merge_sha":API_SHA}
p3=R.plan_merges([m3], root, roster=GRP_ROSTER); R.write_rows(p3, root)
line=get(2003).splitlines()[0]
chk("Q3 anchor preserved", line.startswith("- [#2003](https://github.com/tvofi/heatpump_optimizer/pull/2003) — "))
chk("Q3 '|' sanitised to '/'", "|" not in line)
chk("Q3 no newline in row (one line)", len(get(2003).splitlines())==1)
chk("Q3 group suffix kept", p3[0]["line"].endswith("(R9-X)."))
chk("Q3 no closing keyword", not R.CLOSING_KEYWORD.search(p3[0]["line"]))
chk("Q3 delivery_status.mentions() reads it", DS.mentions(2003,[get(2003)]))
chk("Q3 delivery_status.anchored() reads it", DS.anchored(2003,line))
chk("Q3 rowed_line reads it", R.rowed_line(2003,line))
chk("Q3 line is exactly row_line's output", p3[0]["line"]==R.row_line(2003,m3["title"],API_SHA,"R9-X"))

# ---------- (4) planted controls ----------
put(2004, "- [#2004](https://github.com/tvofi/heatpump_optimizer/pull/2004) — **open**, fix: still in review\n")
b4=get(2004)
mo={"number":2004,"title":"fix: still in review","state":"open","head_ref":"fix/y","merge_sha":API_SHA}
chk("Q4 CONTROL A open PR with open row: not planned", R.plan_merges([mo],root,roster=None)==[])
chk("Q4 CONTROL A file untouched", get(2004)==b4)
chk("Q4 CONTROL A row alone DOES read stale (so the state clause is load-bearing)", R.row_matches_merge(2004,API_SHA,root) is False)
# no row at all -> merged entry still gets a row
m5={"number":2005,"title":"fix: unrowed","state":"closed","head_ref":"","merge_sha":API_SHA}
p5=R.plan_merges([m5],root,roster=None)
chk("Q4 CONTROL B no-row merged entry planned", [p["number"] for p in p5]==[2005])
chk("Q4 CONTROL B no-row merge CREATED with merged row", R.write_rows(p5,root)==["dev/programme/delivery/2005.md"] and "**merged `" in get(2005))
# the pre-merge beat still writes open_row_line
sr=R.self_row(2006)
chk("Q4 CONTROL B self_row writes open_row_line", R.write_rows([sr],root)==["dev/programme/delivery/2006.md"] and "**open**" in get(2006) and "**merged `" not in get(2006))

# ---------- BOUNDARY: write set ----------
import traceback
def refused(rows):
    try: R.write_rows(rows, root); return None
    except R.Refuse as e: return str(e)
r1=refused([{"number":2007,"path":"dev/programme/plan-2026-09-open-issues.md","line":R.row_line(2007,"t",API_SHA,None)}])
chk("BOUNDARY plan of record REFUSED", r1 is not None and "plan-2026-09" in r1)
r2=refused([{"number":2008,"path":"dev/programme/HANDOVER.md","line":R.row_line(2008,"t",API_SHA,None)}])
chk("BOUNDARY HANDOVER.md REFUSED", r2 is not None)
r3=refused([{"number":2009,"path":"dev/programme/delivery/../../X.md","line":R.row_line(2009,"t",API_SHA,None)}])
chk("BOUNDARY path escape REFUSED", r3 is not None)
r4=refused([{"number":2009,"path":"dev/programme/delivery/2009.txt","line":R.row_line(2009,"t",API_SHA,None)}])
chk("BOUNDARY non-.md REFUSED", r4 is not None)
# a rewrite aimed at another file's number
try:
    R.write_rows([{"number":2001,"path":R.row_path(2002),"line":R.row_line(2001,"t",API_SHA,None)}],root)
    chk("BOUNDARY cross-number rewrite REFUSED", False)
except R.Refuse: chk("BOUNDARY cross-number rewrite REFUSED", True)

print("HARNESS FAILS:", fails)
sys.exit(1 if fails else 0)
