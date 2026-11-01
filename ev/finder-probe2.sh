SHIM=$1; OUT=$2
T=$(mktemp -d); mkdir -p $T/shim $T/real $T/st $T/w
cp "$SHIM" $T/shim/gh; chmod +x $T/shim/gh
printf '#!/bin/sh\nexit 0\n' > $T/real/gh; chmod +x $T/real/gh
export PATH=$T/shim:$T/real:/opt/node22/bin:/usr/local/bin:/usr/bin:/bin HPO_STATE_DIR=$T/st
: > $OUT
run() { local label=$1; shift; : > $T/st/gh-calls.log; ( cd $T/w && "$@" ) >/dev/null 2>&1 </dev/null; local l; l=$(cat $T/st/gh-calls.log); local tag=clean; case $l in *LEAKVAL*) tag=LEAK;; esac; [ -z "$l" ] && tag=NOLINE; printf '%-6s | %s\n       -> %s\n' "$tag" "$label" "$l" >> $OUT; }
run "python3 -cCODE glued, no spaces" /usr/bin/python3 "-c__import__('subprocess').run(['gh','api','-fx=LEAKVAL'])"
run "python3 -BcCODE glued, no spaces" /usr/bin/python3 "-Bc__import__('subprocess').run(['gh','api','-fx=LEAKVAL'])"
run "ruby -rjson -e CODE" ruby -rjson -e "system('gh','api','-fx=LEAKVAL')"
run "ruby -eCODE glued" ruby "-esystem('gh','api','-fx=LEAKVAL')"
run "node -e CODE" node -e "require('child_process').execFileSync('gh',['api','-fx=LEAKVAL'])"
run "node --eval=CODE" node "--eval=require('child_process').execFileSync('gh',['api','-fx=LEAKVAL'])"
run "node --print=CODE" node "--print=require('child_process').execFileSync('gh',['api','-fx=LEAKVAL']).toString()"
printf "require('child_process').execFileSync('gh',['api','x'])\n" > $T/w/n.js; : > $T/w/r.js
run "node --require ./r.js n.js LEAKVAL" node --require ./r.js n.js LEAKVAL
run "node -r ./r.js n.js LEAKVAL" node -r ./r.js n.js LEAKVAL
run "node --input-type=module -e CODE" node --input-type=commonjs -e "require('child_process').execFileSync('gh',['api','-fx=LEAKVAL'])"
run "curl|bash -s -- --token LEAKVAL shape" sh -c 'echo "gh api x" | bash -s -- --token LEAKVAL'
rm -rf $T
