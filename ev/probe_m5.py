import sys, copy; sys.path.insert(0, sys.argv[1]); import merge_train as m
H0="a"*40; G=m.GATE
def page(nodes, more, cur):
    return {"data":{"repository":{"pullRequest":{"commits":{"nodes":[{"commit":{"oid":H0,"statusCheckRollup":{"contexts":{"pageInfo":{"hasNextPage":more,"endCursor":cur},"nodes":nodes}}}}]}}}}}
cr=lambda n,c,req=True:{"__typename":"CheckRun","name":n,"status":"COMPLETED","conclusion":c,"isRequired":req}
cases={"page1 red required gate, page2 green gate rerun":[[cr(G,"FAILURE")],[cr(G,"SUCCESS")]],
       "page1 non-gate required ctx, page2 green gate":[[cr("other-req","SUCCESS")],[cr(G,"SUCCESS")]],
       "control: both on one walk, gate red on page2":[[cr(G,"SUCCESS")],[cr(G,"FAILURE")]]}
for k,pages in cases.items():
    f=lambda c,p=pages: copy.deepcopy(page(p[0 if c is None else int(c)], c is None, "1"))
    print(f"{k}: {m.platform_gate(m.rollup_walk(f,H0),H0)}")
