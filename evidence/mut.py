import sys
f=".github/workflows/codeql.yml"; s=open(f).read()
G="(github.event_name == 'pull_request' && matrix.language == 'python')"
PR="""'[".claude/workflows/*.js", "tests/**", "dev/**"]'"""
BA="""'[".claude/workflows/*.js"]'"""
m={
"M1":lambda s:s.replace(" && matrix.language == 'python')",")",1),
"M2":lambda s:s.replace("${{ "+G,"${{ !"+G,1),
"M3":lambda s:s.replace("matrix.language == 'python')","matrix.language == 'python' || true)",1),
"M4":lambda s:s.replace("github.event_name == 'pull_request' &&","github.event_name == 'push' &&",1),
"M5":lambda s:s.replace(G+" && "+PR+" || "+BA,G+" && "+BA+" || "+PR,1),
"M6":lambda s:s.replace(PR+" || "+BA,PR+" && "+BA,1),
"M7":lambda s:s.replace(', "dev/**"]\'',']\'',1),
"M8":lambda s:s.replace(" || "+BA," || "+PR,1),
"M9":lambda s:s.replace("github.event_name == 'pull_request' &&","github.event_name != 'pull_request' &&",1),
"M10":lambda s:s.replace("matrix.language == 'python'","matrix.language != 'python'",1),
"M11":lambda s:s.replace(" && '[\".claude/workflows/*.js\", \"tests/**\"", " && '[\".claude/workflows/*.js\", \"tests/**\", \"x/**\"",1),
"M12":lambda s:s.replace("github.event_name == 'pull_request' &&","github.event_name == 'pull_request' || github.event_name == 'merge_group' &&",1),
}
n=sys.argv[1]; t=m[n](s) if n!="M0" else s
assert n=="M0" or t!=s, "no-op "+n
open(f,"w").write(t)
