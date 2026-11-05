import sys
p=sys.argv[1]; s=open(p).read()
a="  const unreached = Object.entries(reach).filter(([, v]) => !v).map(([k]) => k);\n"
assert s.count(a)==1
s=s.replace(a,a+'  if (process.env.HPO_DUMP) (await import("node:fs")).writeFileSync(process.env.HPO_DUMP, JSON.stringify(bad.overflow, null, 1));\n')
open(p,"w").write(s)
