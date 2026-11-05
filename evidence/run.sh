# usage: run.sh <armdir> <cmd...> : runs offline; prints rc and stub-log line count
O=$1; shift; : > $O/stub.log
env -i HOME=$O/home PATH=$O/own:$O/stub:$O/tools HPO_STATE_DIR=$O/home/state "$@" >$O/out 2>$O/err; rc=$?
echo "rc=$rc stub_lines=$(wc -l < $O/stub.log)"
