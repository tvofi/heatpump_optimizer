# usage: run_one.sh <srcwt> <name> <old> <new>   (old empty = null)
W=/root/w; src=$1; name=$2; old=$3; new=$4
d=$W/m-$name; rm -rf $d; mkdir -p $d
for x in tests custom_components tools; do cp -r $src/$x $d/; done
cd $d
if [ -n "$old" ]; then python3 - "$old" "$new" <<'PY'
import sys; p='tests/replay.py'; s=open(p).read(); o,n=sys.argv[1],sys.argv[2]
assert s.count(o)==1, s.count(o); open(p,'w').write(s.replace(o,n))
PY
fi
( time HASTUB_TZ=Europe/Stockholm OPENBLAS_NUM_THREADS=1 PYTHONPATH=tests/hastub python3 tests/replay.py --one tests/replay/owner-2026-10-30-away.json --step-minutes 60 > $W/ev/one60_$name.json 2> $W/ev/one60_$name.err ) 2> $W/ev/one60_$name.time
python3 $W/summ_finder.py $W/ev/one60_$name.json > $W/ev/one60_$name.summary 2>&1
echo "done $name"
