S=/tmp/claude-0/-home-claude/6de11d25-1693-5070-8c25-2c3ab2180e07/scratchpad
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_CORETYPE=Haswell
for i in 0 1 2 3 4 5; do
  if [ $((i%2)) = 0 ]; then arms="base head"; else arms="head base"; fi
  for a in $arms; do
    cd $S/$a && echo "$a $(PYTHONPATH=tests/hastub:custom_components:tests $S/vci/bin/python $S/cpu_one.py 2>&1 | tail -1)"
  done
done
