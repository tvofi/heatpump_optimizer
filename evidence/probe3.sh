#!/bin/bash
# reviewer's own shapes (round 4); usage: probe3.sh <shim> <out>
SHIM=$1; OUT=$2
T=$(mktemp -d); mkdir -p $T/shim $T/real $T/st $T/w
cp "$SHIM" $T/shim/gh; chmod +x $T/shim/gh
printf '#!/bin/sh\nexit 0\n' > $T/real/gh; chmod +x $T/real/gh
export PATH=$T/shim:$T/real:/opt/node22/bin:/usr/local/bin:/usr/bin:/bin HPO_STATE_DIR=$T/st
PY=/usr/bin/python3
printf 'import subprocess;subprocess.run(["gh","api","x"])\n' > $T/w/c.py
printf 'gh api x\n' > $T/w/s.sh
printf "require('child_process').execFileSync('gh',['api','x'])\n" > $T/w/n.js
printf "system('gh','api','x')\n" > $T/w/p.pl; cp $T/w/p.pl $T/w/r.rb
ln -sf $PY $T/w/pypy3; ln -sf /bin/bash $T/w/zsh; ln -sf /bin/bash $T/w/ksh
: > $OUT
run() { local label=$1; shift; : > $T/st/gh-calls.log; ( cd $T/w && "$@" ) >/dev/null 2>&1 </dev/null; local l; l=$(cat $T/st/gh-calls.log); local tag=clean; case $l in *LEAKVAL*) tag=LEAK;; esac; [ -z "$l" ] && tag=NOLINE; printf '%-6s | %s\n       -> %s\n' "$tag" "$label" "$l" >> $OUT; }
G="import subprocess as s;s.run(['gh','api','x'])#LEAKVAL"
run "python3 -IcCODE" $PY "-Ic$G"
run "python3 -Wd -c CODE" $PY -Wd -c "$G"
run "python3 -WLEAKVAL -c" $PY -Wignore::LEAKVAL -c "$G"
run "python3 -X dev=LEAKVAL c.py" $PY -X dev=LEAKVAL c.py
run "python3 -Xdev=LEAKVAL c.py" $PY -Xdev=LEAKVAL c.py
run "python3 -BWLEAKVAL c.py" $PY -BWignore::LEAKVAL c.py
run "python3 -bX LEAKVAL c.py" $PY -bX LEAKVAL c.py
run "python3 -- c.py LEAKVAL" $PY -- c.py LEAKVAL
run "python3 - LEAKVAL <c.py" sh -c "$PY - LEAKVAL < c.py"
run "python3 -m mod LEAKVAL" sh -c "cp c.py cm.py; $PY -m cm LEAKVAL"
run "python3 -I -S -m cm LEAKVAL" $PY -I -S -m cm LEAKVAL
run "python3 -X 'a LEAKVAL' c.py (value with space)" $PY -X "importtime LEAKVAL" c.py
run "python3 -W 'x LEAKVAL' c.py (value with space)" $PY -W "ignore LEAKVAL" c.py
run "pypy3 -c CODE" ./pypy3 -c "$G"
run "zsh(link) -ce CODE" ./zsh -ce "gh api x; : LEAKVAL"
run "ksh(link) -c CODE" ./ksh -c "gh api x; : LEAKVAL"
run "bash -O extglob -c CODE" bash -O extglob -c "gh api x; : LEAKVAL"
run "bash -Oextglob -c" bash -Oextglob -c "gh api x #LEAKVAL"
run "bash -o pipefail -e s.sh LEAKVAL" bash -o pipefail -e s.sh LEAKVAL
run "bash -xo pipefail s.sh LEAKVAL" bash -xo pipefail s.sh LEAKVAL
run "bash +o pipefail s.sh LEAKVAL" bash +o pipefail s.sh LEAKVAL
run "bash --norc s.sh LEAKVAL" bash --norc s.sh LEAKVAL
run "bash --rcfile LEAKVAL -i? (long w/ value)" bash --rcfile /dev/null s.sh LEAKVAL
run "bash -- s.sh LEAKVAL" bash -- s.sh LEAKVAL
run "bash -ex s.sh LEAKVAL" bash -ex s.sh LEAKVAL
run "sh -s -- LEAKVAL from pipe" sh -c 'echo "gh api x" | sh -s -- LEAKVAL'
run "dash -c CODE" dash -c "gh api x #LEAKVAL"
run "dash -ecCODE" dash "-ecgh api x #LEAKVAL"
run "bash -o 'x LEAKVAL' s.sh (value with space)" bash -o "pipefail LEAKVAL" s.sh
run "perl -w p.pl LEAKVAL" perl -w p.pl LEAKVAL
run "perl -we CODE" perl -we "system('gh','api','x') #LEAKVAL"
run "perl -I LEAKVAL p.pl" perl -I LEAKVAL p.pl
run "perl p.pl LEAKVAL" perl p.pl LEAKVAL
run "ruby -w r.rb LEAKVAL" ruby -w r.rb LEAKVAL
run "ruby -I LEAKVAL r.rb" ruby -I LEAKVAL r.rb
run "node --eval CODE (separate)" node --eval "require('child_process').execFileSync('gh',['api','x'])//LEAKVAL"
run "node --inspect=LEAKVAL n.js" node --inspect-port=0 n.js LEAKVAL
run "node -- n.js LEAKVAL" node -- n.js LEAKVAL
run "node n.js LEAKVAL" node n.js LEAKVAL
run "node -pe CODE" node -pe "require('child_process').execFileSync('gh',['api','x']).toString()//LEAKVAL"
run "env FOO=LEAKVAL python3 c.py" env FOO=LEAKVAL $PY c.py
run "env python3 c.py LEAKVAL" env $PY c.py LEAKVAL
run "xargs python3 c.py" sh -c "echo LEAKVAL | xargs $PY c.py"
run "nice python3 c.py LEAKVAL" nice $PY c.py LEAKVAL
run "timeout 5 bash -c CODE" timeout 5 bash -c "gh api x; : LEAKVAL"
x=$(printf 'A%.0s' $(seq 1 120)); mkdir -p $T/w/$x; cp $T/w/s.sh $T/w/$x/s.sh
run "long path (120 A) LEAKVAL past 80" bash ./$x/s.sh LEAKVAL
rm -rf $T
