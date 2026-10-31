import sys, copy, io, contextlib
WT="/home/user/wt"; sys.path[:0]=[WT+"/tools/audit/seat", WT+"/tools/audit"]
import roster_lib as L, roster_edit as E, carry_audit as CA
base={"groups":[
 {"group":"A","resume":{"stage":"in-progress"},"carry":["c0","c1"],"issues":[5],"fixes":[]},
 {"group":"OPEN","resume":{"stage":"not-started"},"carry":[],"issues":[6],"fixes":[]},
 {"group":"DONE","resume":{"stage":"done"},"carry":[],"issues":[7],"fixes":[]},
 {"group":"RCA","resume":{"stage":"rca-done"},"carry":[],"issues":[],"fixes":[]},
 {"group":"ABS","resume":{"stage":"absorbed","absorbed_into":"OPEN"},"carry":[],"issues":[8],"fixes":[]},
 {"group":"CO","resume":{"stage":"carries-open"},"carry":[],"issues":[],"fixes":[]},
]}
def op(o, g, v, rest=(), field=None, legacy=None, r=None):
    r = r or copy.deepcopy(base); buf=io.StringIO()
    try:
        with contextlib.redirect_stdout(buf): E.apply_op(r,o,g,v,field,None,None,"x",(),legacy or {},rest)
        return "ok", r, buf.getvalue()
    except E.Refuse as e: return f"REFUSE {e}", r, buf.getvalue()
def res(name, got): print(f"RESULT {name}: {got}")
# mark-carry refusals each with a null
cases=[("moved to a closed (done) group", ("0",("moved","DONE")), ("0",("moved","OPEN"))),
       ("moved to an absorbed group", ("0",("moved","ABS")), ("0",("moved","OPEN"))),
       ("moved to rca-done", ("0",("moved","RCA")), ("0",("moved","OPEN"))),
       ("moved to missing", ("0",("moved","NOPE")), ("0",("moved","OPEN"))),
       ("moved to itself", ("0",("moved","A")), ("0",("moved","OPEN"))),
       ("value with ]", ("0",("dismissed","a]b")), ("0",("dismissed","ab"))),
       ("implemented without sha", ("0",("implemented",)), ("0",("implemented","0123abcd"))),
       ("implemented non-sha", ("0",("implemented","main")), ("0",("implemented","0123abcd"))),
       ("dismissed no reason", ("0",("dismissed",)), ("0",("dismissed","dup"))),
       ("dismissed whitespace reason", ("0",("dismissed","   ")), ("0",("dismissed","dup"))),
       ("unknown mark", ("0",("shipped","x")), ("0",("dismissed","x"))),
       ("no kind", ("0",()), ("0",("dismissed","x"))),
]
for name,(i,rest),(ni,nrest) in cases:
    a=op("mark-carry","A",i,rest)[0]; b=op("mark-carry","A",ni,nrest)
    res(f"mark-carry {name}", f"{a[:70]} | null: {b[0]} -> {b[1]['groups'][0]['carry'][0]!r}")
# already marked
_,r,_=op("mark-carry","A","0",("dismissed","dup"))
res("mark-carry already marked", op("mark-carry","A","0",("implemented","0123abcd"),r=r)[0][:70] + " | null idx1: " + op("mark-carry","A","1",("implemented","0123abcd"),r=r)[0])
# moved to carries-open (open-like, should be allowed?)
res("mark-carry moved to carries-open group", op("mark-carry","A","0",("moved","CO"))[0])
# set-stage behaviours
for st in ("done","rca-done","absorbed","in-progress","review","refused"):
    s,r,out=op("set-stage","A",st)
    res(f"set-stage A {st} over 2 pending", f"{s} wrote={r['groups'][0]['resume']['stage']} out={out.strip()!r}")
# set-resume --field note: does it need legacy? (in-memory, n/a) 
# carry text spelled with a mark by append-carry
s,r,_=op("append-carry","A","new owed thing [dismissed: looks marked]")
res("append-carry text ending in a mark-shaped suffix", f"{s}; pending={L.pending_carries(r['groups'][0],{})} (indices of 3 carries)")
# carry_audit roster arm
ro=copy.deepcopy(base); ro["groups"][2]["carry"]=["owed"]; ro["groups"][4]["carry"]=["owed2"]; ro["groups"][3]["carry"]=["owed3"]
print("\n".join(CA.roster_report(ro, {}, {5,6,7,8,9,201})))
print("-- without issues:"); print("\n".join(CA.roster_report(ro, {}, None)))
print("-- legacy null:"); print(CA.roster_report(ro, {"DONE":frozenset({"owed"}),"ABS":frozenset({"owed2"}),"RCA":frozenset({"owed3"})}, set()))
