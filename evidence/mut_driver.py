import sys,re
f,name=sys.argv[1],sys.argv[2]
s=open(f).read()
def nth(s,old,new,n):
    i=-1
    for _ in range(n): i=s.index(old,i+1)
    return s[:i]+new+s[i+len(old):]
M={
 "drop-quiet-find-first": lambda s: nth(s,"(draft.quietWindows || []).find(","(draft.dhwWindows || []).find(",1),
 "drop-quiet-find-second": lambda s: nth(s,"(draft.quietWindows || []).find(","(draft.dhwWindows || []).find(",2),
 "band-literal-10": lambda s: s.replace('band: finiteNum(refit.band_percent) ? String(Number(refit.band_percent)) : "—"','band: "10"'),
 "band-dropped": lambda s: s.replace('pairs: refit.pairs,\n        band:','pairs: refit.pairs,\n        bandX:'),
 "note-none": lambda s: s.replace('${ADVISOR_OPT_IN.includes(id) ? esc','${false ? esc'),
 "note-all": lambda s: s.replace('${ADVISOR_OPT_IN.includes(id) ? esc','${true ? esc'),
 "sv-band-literal": lambda s: s.replace("osäkerhet ungefär ±{band} %","osäkerhet ungefär ±7-10 %"),
 "de-note-missing": lambda s: s.replace('"advisor.optin_sensor_off": "dann seinen Sensor in den Entitätseinstellungen aktivieren: er ist standardmäßig deaktiviert",\n',''),
}
t=M[name](s)
assert t!=s, name
open(f,"w").write(t)
