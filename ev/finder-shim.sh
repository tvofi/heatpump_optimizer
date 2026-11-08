#!/bin/bash
# usage: shim.sh <dir> -> creates <dir>/bin/git that advances clock 70s per call, unconditionally overriding
d=$1; mkdir -p $d/bin; gt=$(command -v git); rm -f $d/clk
cat > $d/bin/git <<E2
#!/bin/bash
f="$d/clk"; n=\$(( \$(cat "\$f" 2>/dev/null || echo 0) + 70 )); echo "\$n" > "\$f"
export GIT_TEST_DATE_NOW="\${GIT_TEST_DATE_NOW:-\$(( \$(date +%s) + n ))}"
exec "$gt" "\$@"
E2
chmod +x $d/bin/git
