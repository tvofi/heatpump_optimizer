set -e
S=/tmp/claude-0/-home-user/15da69dc-fe9d-55c1-9c21-29654add546e/scratchpad
cd /home/user/heatpump_optimizer
grep -c "GATE_SCOPE" tests/entities.py || true
rm -rf $S/wt; git worktree add -q --detach $S/wt e4eda221
cd $S/wt
# attack: shrink features.py entry by dropping a production file it reads, nothing else changed
python3 - <<'EOF'
import json
p='tests/closures.json'; d=json.load(open(p))
f=d['closures']['tests/features.py']
victim=[x for x in f if x.startswith('custom_components/')][0]
f.remove(victim); print('dropped', victim)
json.dump(d, open(p,'w'), indent=1); open(p,'a').write('\n')
EOF
git -c user.email=r@x -c user.name=r commit -qam "probe shrink"
echo "== real wiring"
python3 tests/closure.py select --diff e4eda221 | sed -n 1,12p
python3 tests/closure.py select --diff e4eda221 --json | python3 -c "import json,sys;p=json.load(sys.stdin);print(p['mode'],p['run'],p.get('entry_changed'))"
echo "== mutant: base read from HEAD instead of merge base"
sed -i 's|f"{base.stdout.strip()}:{CLOSURES_REL}"|f"HEAD:{CLOSURES_REL}"|' tests/closure.py
git diff --stat tests/closure.py
python3 tests/closure.py select --diff e4eda221 --json | python3 -c "import json,sys;p=json.load(sys.stdin);print(p['mode'],p['run'],p.get('entry_changed'))"
git checkout -q tests/closure.py
echo "== no base (unrelated ref)"
python3 -c "
import sys; sys.path.insert(0,'tests'); import closure
print(closure.base_closures('no-such-ref'))
print(closure.select(['tests/closures.json'], None)['mode'])"
