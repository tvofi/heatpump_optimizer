# usage: run.sh <tree> <out>
cd $1; PYTHONPATH=$1/tests/hastub:$1/tests timeout 900 python3 /tmp/tmp.FTRFP8LkC0/ev/mutants/cut_features.py > $2 2>&1; echo "exit=$?" >> $2
