OLD, NEW = "            return peak <= bound and final <= bound", "            return peak < bound and final <= bound"
mut = mutate(SID, "_size_step_power", OLD, NEW)
gen_args = [(p, c, b, o) for p in (1.5, 3.0, 4.5, 6.0, 9.0) for c in (2.0, 3.0, 3.7) for b in (20.0, 21.0) for o in (-5.0, 2.0, 8.0)]
moved, n = scan(mut, args=gen_args)
print(f"RESULT real_inputs_moved={moved}/{n} count")
# the tie, which no rollout of a real house was found to produce: the predictor stubbed to return (bound, bound - 0.1)
def run_tie(fn, peak_off, final_off):
    bound = 0.8  # the full bound, tried after the noise-headroom bound 0.65 fails
    stub = lambda *a, **k: (bound + peak_off, bound + final_off)
    with mock.patch.dict(fn.__globals__, {"_predict_step_excursion_plant": stub}):
        return call(fn, 6.0, 3.0, 21.0, 2.0, HOUSES["features_heavy"])
print(f"RESULT stub_peak_tie_baseline={run_tie(SID._size_step_power, 0.0, -0.1)} mutant={run_tie(mut, 0.0, -0.1)}")
print(f"RESULT stub_null_below_baseline={run_tie(SID._size_step_power, -0.01, -0.1)} mutant={run_tie(mut, -0.01, -0.1)}")
tail()
