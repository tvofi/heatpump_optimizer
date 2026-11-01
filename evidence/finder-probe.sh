#!/bin/bash
# usage: probe.sh <shim path> <outfile>
SHIM=$1; OUT=$2
T=$(mktemp -d); mkdir -p $T/shim $T/real $T/st $T/w
cp "$SHIM" $T/shim/gh; chmod +x $T/shim/gh
printf '#!/bin/sh\nexit 0\n' > $T/real/gh; chmod +x $T/real/gh
export PATH=$T/shim:$T/real:/usr/bin:/bin HPO_STATE_DIR=$T/st
PY=/usr/bin/python3
cat > $T/w/caller.py <<'P'
import subprocess,sys; subprocess.run(['gh','api','repos/o/r','-f','body=x'])
P
cp $T/w/caller.py $T/w/caller_mod.py
printf 'gh api repos/o/r\n' > $T/w/s.sh
mkdir -p "$T/w/GH_TOKEN=abcLEAKVAL"; cp $T/w/s.sh "$T/w/GH_TOKEN=abcLEAKVAL/script"
: > $OUT
run() { local label=$1; shift; : > $T/st/gh-calls.log; ( cd $T/w && "$@" ) >/dev/null 2>&1 </dev/null; local l; l=$(cat $T/st/gh-calls.log); local tag=clean; case $l in *LEAKVAL*|*ghp_*|*abc*) tag=LEAK;; esac; [ -z "$l" ] && tag=NOLINE; printf '%-6s | %s\n       -> %s\n' "$tag" "$label" "$l" >> $OUT; }
echo "## census, 25 flags via sh -c 'gh api repos/o/r FLAG LEAKVAL'" >> $OUT
for f in -f -F -H -b -n -t -T -q -d --body --body-file --notes --notes-file --title --subject --desc --description --field --raw-field --header --input --jq --template --env-file --squash-merge-commit-message; do
  run "sh -c gh api repos/o/r $f LEAKVAL; :" sh -c "gh api repos/o/r $f LEAKVAL; :"; done
echo "## round-2 out-of-census flags" >> $OUT
for f in -A --author-email -S --search -m --milestone -l --label -a --assignee -r --reviewer -B --base --match-head-commit -p --preview -e --env; do
  run "sh -c gh pr merge 1 $f LEAKVAL; :" sh -c "gh pr merge 1 $f LEAKVAL; :"; done
echo "## round-2 non-flag shapes" >> $OUT
run "sh -c GH_TOKEN=ghp_LEAKVAL gh api user; :" sh -c 'GH_TOKEN=ghp_LEAKVAL gh api user; :'
run "sh -c echo ghp_LEAKVAL | gh secret set NAME; :" sh -c 'echo ghp_LEAKVAL | gh secret set NAME; :'
run "sh -c printf %s LEAKVAL | gh secret set NAME; :" sh -c 'printf %s LEAKVAL | gh secret set NAME; :'
run "python3 -c argv-list -f body=LEAKVAL" $PY -c "import subprocess; subprocess.run(['gh','api','repos/o/r','-f','body=LEAKVAL'])"
run "python3 -c argv-list --body LEAKVAL" $PY -c "import subprocess; subprocess.run(['gh','pr','comment','1','--body','LEAKVAL'])"
run "python3 -c shell=True" $PY -c "import subprocess; subprocess.run('gh api repos/o/r -f body=LEAKVAL', shell=True)"
run "python3 -c (no spaces) -fx=LEAKVAL" $PY -c "import subprocess as s;s.run(['gh','api','-fx=LEAKVAL'])"
run "timeout 10 gh api -f body=LEAKVAL" timeout 10 gh api repos/o/r -f body=LEAKVAL
run "bash -c x=1; gh issue comment --body LEAKVAL" bash -c 'x=1; gh issue comment 1 --body LEAKVAL; :'
run "xargs -a /dev/null sh -c ... --body LEAKVAL" xargs -a /dev/null sh -c 'gh api repos/o/r --body LEAKVAL; :'
echo "## null controls" >> $OUT
run "PY -I W/caller.py --body LEAKVAL (expect: python3 caller.py path)" $PY -I $T/w/caller.py --body LEAKVAL
run "cd W && PY -m caller_mod --body LEAKVAL (expect python3 -m caller_mod)" $PY -m caller_mod --body LEAKVAL
echo "## reviewer-3 shapes" >> $OUT
run "python3 -cCODE glued (no spaces)" $PY "-cimport subprocess as s;s.run(['gh','api','-fx=LEAKVAL'])"
run "python3 -Bc CODE" $PY -Bc "import subprocess as s;s.run(['gh','api','-fx=LEAKVAL'])"
run "python3 -uc CODE" $PY -uc "import subprocess as s;s.run(['gh','api','-fx=LEAKVAL'])"
run "python3 -Ec CODE" $PY -Ec "import subprocess as s;s.run(['gh','api','-fx=LEAKVAL'])"
run "perl -eCODE glued" perl "-esystem('gh','api','-fx=LEAKVAL')"
run "perl -e CODE" perl -e "system('gh','api','-fx=LEAKVAL')"
run "perl -Mstrict -e CODE" perl -Mstrict -e "system('gh','api','-fx=LEAKVAL')"
command -v ruby >/dev/null && run "ruby -rjson -e CODE" ruby -rjson -e "system('gh','api','-fx=LEAKVAL')"
command -v ruby >/dev/null && run "ruby -eCODE glued" ruby "-esystem('gh','api','-fx=LEAKVAL')"
command -v node >/dev/null && run "node -e CODE" node -e "require('child_process').execFileSync('gh',['api','-fx=LEAKVAL'])"
command -v node >/dev/null && run "node --eval=CODE" node "--eval=require('child_process').execFileSync('gh',['api','-fx=LEAKVAL'])"
command -v node >/dev/null && run "node --print=CODE" node "--print=require('child_process').execFileSync('gh',['api','-fx=LEAKVAL']).toString()"
printf "require('child_process').execFileSync('gh',['api','x'])\n" > $T/w/n.js; : > $T/w/r.js
command -v node >/dev/null && run "node --require r.js n.js LEAKVAL" node --require ./r.js n.js LEAKVAL
run "bash --command=? (bash rejects; shape only)" bash "--command=gh api x LEAKVAL"
run "sh ./GH_TOKEN=abcLEAKVAL/script" sh "./GH_TOKEN=abcLEAKVAL/script"
run "bash -x s.sh LEAKVAL" bash -x s.sh LEAKVAL
run "python3 -W error -m caller_mod LEAKVAL" $PY -W error -m caller_mod LEAKVAL
run "python3 -W LEAKVAL caller.py (option value)" $PY -W ignore::LEAKVAL caller.py
run "python3 -X LEAKVAL caller.py (option value)" $PY -X LEAKVAL caller.py
run "sh -s LEAKVAL < s.sh (stdin script)" sh -c 'sh -s LEAKVAL < s.sh'
run "sh -s -- LEAKVAL < s.sh" sh -c 'sh -s -- LEAKVAL < s.sh'
run "bash -s LEAKVAL < s.sh" sh -c 'bash -s LEAKVAL < s.sh'
run "echo gh api x | bash -s LEAKVAL" sh -c 'echo "gh api x" | bash -s LEAKVAL'
run "bash -o LEAKVAL s.sh (option value; bash rejects)" bash -o pipefail s.sh LEAKVAL
run "bash -O LEAKVAL s.sh (option value)" bash -O extglob s.sh LEAKVAL
run "xargs gh api x LEAKVAL" sh -c 'echo LEAKVAL | xargs gh api x'
run "env GH_TOKEN=ghp_LEAKVAL gh api user" env GH_TOKEN=ghp_LEAKVAL gh api user
run "sh -c 'env GH_TOKEN=ghp_LEAKVAL gh'" sh -c 'env GH_TOKEN=ghp_LEAKVAL gh api user; :'
cp $T/real/gh "$T/w/my prog"; printf '#!/bin/sh\ngh api x\n' > "$T/w/my prog"; chmod +x "$T/w/my prog"
run "argv0 with a space: './my prog' LEAKVAL" "./my prog" LEAKVAL
ln -sf /bin/bash "$T/w/bashLEAKVAL"
run "argv0 basename itself secret-like (bashLEAKVAL symlink)" "$T/w/bashLEAKVAL" -c 'gh api x; :'
rm -rf $T
