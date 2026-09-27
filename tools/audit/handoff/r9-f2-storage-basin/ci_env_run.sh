export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
P=/tmp/claude-0/vci/bin/python
for core in default Haswell Zen; do
 for t in wt-main r9-f2-fix2; do
  ( if [ $core != default ]; then export OPENBLAS_CORETYPE=$core; fi
    cd /tmp/claude-0/$t && PYTHONPATH=tests/hastub timeout 1800 $P /tmp/claude-0/bt_gain.py /tmp/claude-0/$t > /tmp/claude-0/ci/gain-$t-$core.log 2>&1 ) &
 done
 wait
done
(cd /tmp/claude-0/r9-f2-fix2 && /tmp/claude-0/vtyping/bin/python tests/typing_ruler.py --mypy > /tmp/claude-0/ci/mypy.log 2>&1; echo $? > /tmp/claude-0/ci/mypy.rc)
touch /tmp/claude-0/ci/done
