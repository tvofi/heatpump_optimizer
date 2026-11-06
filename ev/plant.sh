# Real-replay plants: one --one synthetic replay per (probe, plant) in the planted copy
# ~/wtm (tests/replay.py with a PLANT_* override: ref_ms moved to PLANT_REF_MS, cpu/loop
# set to a CI class's measured clean reading, then PLANT_SCALE applied to PLANT_KEYS).
# Exit code per row = 1 iff the run's own cycle_cost offenders are non-empty, which is
# what makes tests/replay.py exit 1 (R.check "<fixture>: cycle_cost" -> R.close -> 1).
cd $HOME/wtm
probe() {  # label ref_ms cpu loop
  for plant in "clean 1 cpu_ratio" "cpu2 2 cpu_ratio" "cpu1.5 1.5 cpu_ratio" "loop2 2 loop_cpu_ratio" "loop1.5 1.5 loop_cpu_ratio" "mem2 2 peak_kib" "mem1.5 1.5 peak_kib"; do
    set -- $1 $2 $3 $4 $plant
    out=$(PYTHONPATH=tests/hastub HASTUB_TZ=UTC OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
      PLANT_REF_MS=$2 PLANT_CPU_RATIO=$3 PLANT_LOOP=$4 PLANT_SCALE=$6 PLANT_KEYS=$7 \
      python3 tests/replay.py --one tests/replay/synthetic-dhw-only.json 2>/dev/null | python3 -c '
import sys, json
for ln in sys.stdin:
    i = ln.find("{")
    if i >= 0 and "cycle_cost" in ln:
        d = json.loads(ln[i:]); cc = d["results"]["cycle_cost"]; c = d["cost"]
        print(1 if cc else 0, "ref_ms %.2f cpu %.4g loop %.4g kib %.0f" % (c["ref_ms"], c["cpu_ratio"], c["loop_cpu_ratio"], c["peak_kib"]), "|", "; ".join(cc)[:150]); break
else: print("ERR no result line")')
    echo "PLANT $1 $5: rc=$out"
  done
}
export -f probe
cat > /tmp/probes.$$ <<'EOF'
ref24-lo 19.6 2.414 0.1109
ref24-mid 22.0 2.414 0.1109
ref24-hi 25.4 2.414 0.1109
ref30-lo 28.8 2.728 0.0889
ref30-mid 30.7 2.728 0.0889
ref30-hi 32.6 2.728 0.0889
ref46-lo 43.1 2.275 0.0822
ref46-mid 46.0 2.275 0.0822
ref46-hi 49.4 2.275 0.0822
ref53-lo 49.7 1.444 0.093
ref53-mid 53.0 1.444 0.093
ref53-hi 56.7 1.444 0.093
fb-27 27.0 2.417 0.0848
fb-35 35.0 2.417 0.0848
fb-40.1 40.1 2.417 0.0848
fb-15 15.0 2.417 0.0848
fb-80 80.0 2.417 0.0848
fb-floor 35.0 2.09 0.0848
EOF
cat /tmp/probes.$$ | xargs -P 4 -L 1 bash -c 'probe "$@"' _
echo PLANTS-DONE
