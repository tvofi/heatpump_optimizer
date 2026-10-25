import sys,subprocess,pathlib
f=pathlib.Path(sys.argv[1]); src=f.read_text()
M=[("R1-unread-not-held",'|| { echo UNREAD; return 0; }','|| { return 1; }'),
   ("R2-no-level_set-held",'  level_set handoff-held "$state/cloud-level-held.$$"\n',''),
   ("R3-no-worktree-read",'\\\n     || git worktree list --porcelain | awk -v h="$2" \'$1 == "HEAD" { at = ($2 == h) } $1 == "detached" && at { f = 1 } END { exit !f }\'',''),
   ("R4-vrefs-listing-fail-ignored",'git ls-remote origin \'refs/heads/verdict/*\' > "$state/cloud-vrefs.$$" \\\n    ||','true ||'),
   ("R5-verdict-before-hold",None,None),
]
for name,old,new in M:
  if old is None: continue
  n=src.count(old)
  if n!=1: print(name,"ANCHOR",n); continue
  f.write_text(src.replace(old,new,1))
  r=subprocess.run(["bash",str(f),"--self-test"],capture_output=True,text=True)
  last=[l for l in r.stdout.splitlines()+r.stderr.splitlines() if 'self-test:' in l]
  fails=[l for l in (r.stdout+r.stderr).splitlines() if l.startswith('FAIL')][:3]
  print(name,"KILLED" if r.returncode else "SURVIVED",last[-1] if last else r.returncode,fails)
  f.write_text(src)
