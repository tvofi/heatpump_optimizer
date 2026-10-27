import os, sys
WT=os.environ["WT"]; sys.path.insert(0,WT+"/tools/audit/seat"); sys.path.insert(0,WT+"/tools/audit")
import roster_sync as R
def show(n,g,w): print(f"RESULT {n}: got={g!r} want={w!r} -> {'PASS' if g==w else 'FAIL'}")
# same trailing Carry marker in both, so only the markup spelling differs
h1=["budget 2*3 per pass. `Carry: R9-DEST`"]
show("collide_asterisk", R.already_carried(h1,"budget 23 per pass. Carry: R9-DEST"), h1[0])
h2=["call set_state now. `Carry: R9-DEST`"]
show("collide_underscore", R.already_carried(h2,"call setstate now. Carry: R9-DEST"), h2[0])
h3=["**Ship it** now. `Carry: R9-DEST`"]
show("collide_emphasis", R.already_carried(h3,"Ship it now. Carry: R9-DEST"), h3[0])
