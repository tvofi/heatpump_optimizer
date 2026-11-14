# usage: mut.sh NAME OLD NEW [env...]
cd $HOME/wt; S=/tmp/claude-0/-home-user-heatpump-optimizer/e429680b-ed91-5819-8d43-9af532a0cb77/scratchpad
name="$1"; old="$2"; new="$3"; shift 3
python3 -I -c 'import sys; s=open(sys.argv[1]).read(); a,b=sys.argv[2],sys.argv[3]; assert s.count(a)==1,a; open(sys.argv[4],"w").write(s.replace(a,b))' tools/ci/selftest_scope.py "$old" "$new" $S/mutsrc.py || { echo "== $name NOT APPLIED"; exit; }
out=$(env "$@" python3 -I -c 'import sys; f, real = sys.argv[1], sys.argv[2]; sys.argv = [real, "--self-test"]; exec(compile(open(f).read(), real, "exec"), {"__name__": "__main__", "__file__": real})' $S/mutsrc.py "$PWD/tools/ci/selftest_scope.py" 2>&1); rc=$?
echo "== $name: rc $rc; $(echo "$out" | grep 'self-test:' | tail -1)"; echo "$out" | grep FAIL | head -3
