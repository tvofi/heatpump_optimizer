import importlib.util,sys
cases={
 "r1: if [ $? -ne 0 ]":("cmd --gate\nif [ $? -ne 0 ]; then exit 1; fi\n",1),
 "r1: if [ \"$?\" = 4 ]":("cmd --gate\nif [ \"$?\" = 4 ]; then :; fi\n",1),
 "r1: if test $? -eq 4":("cmd --gate\nif test $? -eq 4; then :; fi\n",1),
 "r1: while [ $? = 4 ]":("cmd --gate\nwhile [ $? = 4 ]; do :; done\n",1),
 "until [ $? ]":("cmd --gate\nuntil [ $? -eq 0 ]; do :; done\n",1),
 "if ! [ $? ]":("cmd --gate\nif ! [ $? -eq 0 ]; then :; fi\n",1),
 "if [[ $? ]] multiline":("cmd --gate\nif [[ $? -ne 0 ]]\nthen exit 1\nfi\n",1),
 "if (( $? ))":("cmd --gate\nif (( $? != 0 )); then :; fi\n",1),
 "if [ $? ] continuation":("cmd \\\n --gate\nif [ $? -ne 0 ]; then :; fi\n",1),
 "safe: if cond; then if [ $? ]":("if cmd; then\n if [ $? = 0 ]; then :; fi\nfi\n",0),
 "safe: or-capture then if":("rc=0; cmd || rc=$?\nif [ $rc -ne 0 ]; then :; fi\n",0),
 "safe: set +e":("set +e\ncmd\nif [ $? -ne 0 ]; then :; fi\nset -e\n",0),
 "safe: elif":("if cmd; then :\nelif [ $? = 4 ]; then :\nfi\n",0),
 "safe: if cmd || x":("cmd || true\nwhile [ $? = 4 ]; do :; done\n",0),
 "bare plain read":("cmd\nrc=$?\n",1),
}
for p in sys.argv[1:]:
    s=importlib.util.spec_from_file_location("h",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
    print("==",p.rsplit('/',1)[-1])
    for k,(t,w) in cases.items():
        n,h=m.hazards(t); print(f"  {'ok ' if len(h)==w else 'BAD'} want={w} got={len(h)} reads={n} {k}")
