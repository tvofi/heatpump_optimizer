# usage: mk.sh NAME FILE PYEXPR-old PYEXPR-new
set -e
N=$1; F=$2
D=/tmp/claude-0/mut/$N; rm -rf $D; mkdir -p $D
cd /tmp/claude-0/wt && git ls-files -z | xargs -0 cp --parents -t $D 2>/dev/null || true
python3 - "$D/$F" "$3" "$4" <<'PY'
import sys
p,old,new=sys.argv[1:]
s=open(p).read(); c=s.count(old)
assert c==1, (old,c)
open(p,'w').write(s.replace(old,new))
PY
echo made $N
