# build.sh <key8> <fullkey>: header + prelude + body -> probe file in both trees
k=$1; out=dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_$2.py
{ cat $HOME/pt/h_$k.txt; cat $HOME/pt/prelude.py; cat $HOME/pt/b_$k.py; } > $HOME/probe-tree/$out
cd $HOME/probe-tree && PYTHONPATH=tests/hastub timeout 200 /opt/hpo/venv-ci/bin/python3 $out 2>&1 | tail -25
