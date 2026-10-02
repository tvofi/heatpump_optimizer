import re,sys
p="custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
s=open(p).read()
a="        list-style: none; margin: 0; padding: 0;\n"
assert s.count(a)==1; s=s.replace(a,"")
i=s.index("      /* R9-UX-1: why an idle step is idle. Prose")
j=s.index("      .tooltip .dot {",i)
s=s[:i]+s[j:]
open(p,"w").write(s)
