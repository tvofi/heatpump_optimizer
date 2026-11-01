#!/bin/bash
# reviewer's own shapes (round 6); usage: probe4.sh <shim> <out>
SHIM=$1; OUT=$2
T=$(mktemp -d); mkdir -p $T/shim $T/real $T/st $T/w
cp "$SHIM" $T/shim/gh; chmod +x $T/shim/gh
printf '#!/bin/sh\nexit 0\n' > $T/real/gh; chmod +x $T/real/gh
export PATH=$T/shim:$T/real:/opt/node22/bin:/usr/local/bin:/usr/bin:/bin HPO_STATE_DIR=$T/st
PY=/usr/bin/python3
printf 'import subprocess;subprocess.run(["gh","api","x"])\n' > $T/w/c.py
printf 'gh api x\n' > $T/w/s.sh
mkdir -p "$T/w/d LEAKVAL"; cp $T/w/c.py "$T/w/d LEAKVAL/c.py"; cp $T/w/s.sh "$T/w/d LEAKVAL/s.sh"
printf '#!/usr/bin/python3 -X importtime=LEAKVAL\nimport subprocess;subprocess.run(["gh","api","x"])\n' > $T/w/sb1; chmod +x $T/w/sb1
printf '#!/usr/bin/python3 -W ignore LEAKVAL\nimport subprocess;subprocess.run(["gh","api","x"])\n' > $T/w/sb2; chmod +x $T/w/sb2
printf '#!/bin/bash -o pipefail LEAKVAL\ngh api x\n' > $T/w/sb3; chmod +x $T/w/sb3
printf '#!/usr/bin/env -S python3 -W ignore::LEAKVAL\nimport subprocess;subprocess.run(["gh","api","x"])\n' > $T/w/sb4; chmod +x $T/w/sb4
printf 'package M;1;\n' > $T/w/M.pm; printf "system('gh','api','x')\n" > $T/w/p.pl
: > $OUT
run() { local label=$1; shift; : > $T/st/gh-calls.log; ( cd $T/w && "$@" ) >/dev/null 2>&1 </dev/null; local l; l=$(cat $T/st/gh-calls.log); local tag=clean; case $l in *LEAKVAL*) tag=LEAK;; esac; [ -z "$l" ] && tag=NOLINE; printf '%-6s | %s\n       -> %s\n' "$tag" "$label" "$l" >> $OUT; }
run "shebang python3 -X val c" ./sb1
run "shebang python3 -W 'ignore LEAKVAL'" ./sb2
run "shebang bash -o 'pipefail LEAKVAL'" ./sb3
run "env -S python3 -W val" ./sb4
run "python3 'd LEAKVAL/c.py' (spaced script path)" $PY "d LEAKVAL/c.py"
run "bash 'd LEAKVAL/s.sh' (spaced script path)" bash "d LEAKVAL/s.sh"
run "python3 -u 'd LEAKVAL/c.py'" $PY -u "d LEAKVAL/c.py"
run "perl -I. -m M p.pl LEAKVAL" perl -I. -mM p.pl LEAKVAL
run "perl -m LEAKVAL-ish module (spaced)" perl -I. -m M p.pl
run "bash -m s.sh LEAKVAL" bash -m s.sh LEAKVAL
run "python3 -E -s -c CODE" $PY -E -s -c "import subprocess as s;s.run(['gh','api','x'])#LEAKVAL"
run "python3 -c with value word first" $PY -c "import subprocess as s;s.run(['gh','api','x'])" LEAKVAL
run "python3 -X'a LEAKVAL' glued spaced" $PY "-Ximporttime LEAKVAL" c.py
run "python3 -bb -X LEAKVAL c.py" $PY -bb -X LEAKVAL c.py
run "python3.11-like name via symlink -W" sh -c "ln -sf $PY ./python3.99; ./python3.99 -W 'ignore LEAKVAL' c.py"
run "pythonw-like name (unlisted) -W" sh -c "ln -sf $PY ./pythonw; ./pythonw -W 'ignore LEAKVAL' c.py"
run "bash -c CODE argv0 LEAKVAL" bash -c 'gh api x' sh LEAKVAL
run "bash -Hc CODE" bash -Hc 'gh api x #LEAKVAL'
run "sh -n? -s LEAKVAL" sh -c 'echo "gh api x" | sh -vs LEAKVAL'
run "gh api -H 'Authorization: LEAKVAL' x" gh api -H "Authorization: LEAKVAL" x
run "gh api --header=LEAKVAL x" gh api --header=LEAKVAL x
run "gh api x -f q=LEAKVAL" gh api x -f q=LEAKVAL
run "gh secret set N --body LEAKVAL" gh secret set N --body LEAKVAL
run "gh api 'x?tok=LEAKVAL'" gh api "x?tok=LEAKVAL"
rm -rf $T
