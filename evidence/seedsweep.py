
from itertools import combinations
C=("boost","comfort","eco","hot_water","idle","normal","off","pre_heat","system_identification","unknown")
p=next((a,b) for a,b in combinations([c for c in C if c!="idle"]+[f"reason_{n}" for n in range(1000)],2) if list({a,b})==list({b,a}))
x,y=p
s=[max(set(c),key=c.count) for c in ([x,x,y,y],[y,y,x,x])]
print(p, s, "killed" if s!=[x,y] else "LIVES")
