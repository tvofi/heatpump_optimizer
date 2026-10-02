import re,subprocess,sys
H=re.compile(r"\[.*?\]\([^#](?!.*?://).*?\)")
for sha in sys.argv[1:]:
    t=subprocess.run(['git','show',f'{sha}:README.md'],capture_output=True,text=True).stdout
    bad=[]
    for m in H.finditer(t):
        s=m.group(0); i=s.index('(')
        tgt=s[i+1:]
        if re.match(r'[a-z][a-z0-9+.-]*://',tgt,re.I): bad.append(s[:90])
    print(f'RESULT {sha} spans_whose_first_paren_is_absolute={len(bad)}'); [print('  ',b) for b in bad]
