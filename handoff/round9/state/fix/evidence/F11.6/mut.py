import subprocess, sys, os, shutil
src = open('tools/audit/app_approve.sh').read()
M = {
 'M1 byte comparison always passes': ('  cmp -s <(norm "$mv" "$v") <(norm "$mh" "$h") \\\n', '  true \\\n'),
 'M2 no commit-shape check': ('    elif [[ $subj != ci:* ]]; then\n', '    elif false; then\n'),
 'M3 no ancestor check': ('  git merge-base --is-ancestor "$v" "$h" 2>/dev/null ||', '  true ||'),
 'M4 merge parents need not be on main': ('      git merge-base --is-ancestor "$2" "$main" ||', '      true ||'),
 'M11 hand-resolved merges pass': ('      git diff --quiet "$t" "$c" -- . "${x[@]}" \\' + '\n', '      true \\' + '\n'),
 'M12 octopus merges pass': ('      [ $# -eq 2 ] ||', '      true ||'),
 'M13 ci: commits may touch any file': ('      git diff --quiet "$c^" "$c" -- . "${x[@]}" \\' + '\n', '      true \\' + '\n'),
 'M5 evidence read at the head, not the verdict': ('    if grep -rqF -- "$evsha" "$resolved"', '    if grep -rqF -- "$sha" "$resolved"'),
 'M6 approve never carries': ('    carried=$(carry "$vsha" "$sha" refs/hpo-carry/main) ||', '    carried=$(false) ||'),
 'M7 driver files read at the head, not main': ('x=$(git show "$main:.gitattributes"', 'x=$(git show "$h:.gitattributes"'),
 'M8 hunk headers compared raw': ("-e 's/^@@ .*/@@/'", "-e 's/^@@@//'"),
 'M9 no driver-file exclusion': ('"${d[@]}" "$1" "$2" -- . "${x[@]}"', '"${d[@]}" "$1" "$2"'),
 'M10 index lines compared raw': ("-e '/^index /d' ", ""),
}
os.makedirs('/tmp/claude-0/-home-claude/07a1ebb3-77dc-514b-aed6-75fef96d253b/scratchpad/mut/w', exist_ok=True)
for name,(a,b) in M.items():
    assert src.count(a)==1, name
    p='/tmp/claude-0/-home-claude/07a1ebb3-77dc-514b-aed6-75fef96d253b/scratchpad/mut/w/app_approve.sh'
    open(p,'w').write(src.replace(a,b))
    r=subprocess.run(['bash',p,'--self-test'],capture_output=True,text=True)
    fails=[l for l in r.stdout.splitlines() if l.startswith('FAIL')]
    print(f"{name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'}")
    for f in fails: print('   ',f)
