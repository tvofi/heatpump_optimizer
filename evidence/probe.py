import sys, json
sys.path.insert(0, "tools/audit/seat")
import merge_train as m
GATE = m.GATE; H = "a" * 40
def page(nodes, more, cursor, oid=H):
    return {"data": {"repository": {"pullRequest": {"commits": {"nodes": [{"commit": {"oid": oid,
        "statusCheckRollup": {"contexts": {"pageInfo": {"hasNextPage": more, "endCursor": cursor}, "nodes": nodes}}}}]}}}}}
def run(r, n="gate"):
    return {"__typename": "CheckRun", "name": n, "status": r[0], "conclusion": r[1], "isRequired": r[2]}
fill = [run(("COMPLETED", "FAILURE", False), f"x{i}") for i in range(100)]
def walker(pages, fail_at=None, exc=OSError):
    reads = []
    def fetch(c):
        reads.append(c); k = 0 if c is None else int(c)
        if k == fail_at: raise exc("boom")
        p = pages[k]
        return p(k) if callable(p) else p
    return fetch, reads
def two(p2nodes, oid2=H, more2=False, cur2="2"):
    return [page(fill, True, "1"), page(p2nodes, more2, cur2, oid2)]
def gate(st):  # wrap like Train.platform_check
    f, r = st
    try:
        return m.platform_gate(m.rollup_walk(f, H), H)[0], r
    except OSError: return "unread(OSError)", r
    except ValueError: return "unread(ValueError)", r
cases = {
 "p2 required red": two([run(("COMPLETED","FAILURE",True), GATE)]),
 "p2 required pending": two([run(("IN_PROGRESS",None,True), GATE)]),
 "p2 required green": two([run(("COMPLETED","SUCCESS",True), GATE)]),
 "required absent on both pages": two([run(("COMPLETED","SUCCESS",False), "y")]),
 "p2 other required ctx (StatusContext)": two([run(("COMPLETED","SUCCESS",True), GATE),
      {"__typename":"StatusContext","context":"ci/x","state":"SUCCESS","isRequired":True}]),
 "last page exactly full (100), green": two([run(("COMPLETED","SUCCESS",True), GATE)] + fill[:99]),
 "p2 at another head": two([run(("COMPLETED","SUCCESS",True), GATE)], oid2="f"*40),
 "p2 hasNext true, no cursor": two([run(("COMPLETED","SUCCESS",True), GATE)], more2=True, cur2=None),
 "p2 graphql errors (data null)": [page(fill, True, "1"), {"data": None, "errors": [{"message": "x"}]}],
}
for k, v in cases.items():
    print(f"{k:45s} ->", gate(walker(v)))
pages3 = two([run(("COMPLETED","SUCCESS",True), GATE)], more2=True, cur2="2") + [page([], False, "3")]
print(f"{'3 pages, gate on p2, p3 empty':45s} ->", gate(walker(pages3)))
print(f"{'p2 read fails (OSError)':45s} ->", gate(walker(two([run(('COMPLETED','SUCCESS',True), GATE)]), fail_at=1)))
print(f"{'p2 read not JSON (ValueError)':45s} ->", gate(walker(two([run(('COMPLETED','SUCCESS',True), GATE)]), fail_at=1, exc=ValueError)))
# gate green on p1, red on p2 (two runs of gate)
c = [page([run(("COMPLETED","SUCCESS",True), GATE)] + fill[:99], True, "1"), page([run(("COMPLETED","FAILURE",True), GATE)], False, "2")]
print(f"{'gate green p1, gate red p2':45s} ->", gate(walker(c)))
# cap
inf = [page([run(("COMPLETED","SUCCESS",True), GATE)], True, str(i+1)) for i in range(m.gh_read.MAX_PAGES + 3)]
print(f"{'never-ending listing':45s} ->", gate(walker(inf))[0], len(walker(inf)[1]))
