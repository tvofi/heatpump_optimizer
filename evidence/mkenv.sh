# usage: mkenv.sh <tree> <outdir> : builds an offline arm: own/gh (shim with gcpy baked), stub/gh, tools/ (symlinks), home/
T=$1; O=$2; rm -rf $O; mkdir -p $O/own $O/stub $O/tools $O/home
sed "s|^gcpy=@HPO_GH_COMMENT@\$|gcpy=$T/tools/pr/gh_comment.py|" $T/tools/audit/seat/shims/seat-gh > $O/own/gh; chmod 755 $O/own/gh
cat > $O/stub/gh <<STUB
#!/bin/bash
printf '%q ' "\$@" >> $O/stub.log; printf '\n' >> $O/stub.log
echo '{"id": 1, "body": "x"}'
exit 0
STUB
chmod 755 $O/stub/gh
for c in bash sh ps tr cat printf mkdir date chmod mv stat env sed head tail wc rm ls id basename dirname readlink cp sleep touch true false grep tee uname; do p=$(command -v $c) && ln -s $p $O/tools/$c; done
ln -s /opt/hpo/venv-ci/bin/python3 $O/tools/python3
