#!/usr/bin/env python3
"""Build results/<key>.json for every gated key lacking one. Runs the key's probe (baseline vs in-memory mutant)."""
import json, os, re, subprocess, sys
W = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(W, *[".."]*8))
M4 = {}
for l in open(f"{W}/keys.tsv").read().splitlines()[1:]:
    f = l.split("\t"); M4[f[0]] = dict(src=f[1], file=f[2], line=int(f[3]), fn=f[4], cluster=f[5], kind=f[8], m4=f[10])
NOTE = {  # (line, kind-class) -> why the number matters / why it cannot move
 2583: ("equivalent", "drawn==delivered gives scale 1.0 (identity); delivered==0 gives scale 0.0 and the emitters are zeroed exactly as the elif branch does"),
 2587: ("candidate", "delivered==0 with drawn>0 (both tanks empty) leaves the emitter delivery unscaled: heat is delivered that no tank holds"),
 2593: ("candidate", "the dt_hours<=0 floor on the single-tank available-energy term: dt_hours==0 raises ZeroDivisionError and dt_hours<1e-6 inflates the stored-heat term"),
 2594: ("mixed", "available==0 ties scale to 0 (same as elif) and drawn==available scales by 1.0 (identity); `if False` drops the proportional starvation altogether"),
 2598: ("candidate", "available<=0 no longer zeroes the emitters: a tank with no stored heat and less pump output than its loss still feeds the emitters"),
 2939: ("equivalent", "hp_temp==flow_set: region 2 gives f_w=0 so v2=0, which equals region 3's value at the tie"),
 2946: ("candidate", "flow_set==floor_temp makes the span 0: 0/0 -> NaN wood share for an element that baseline resolves to 0.0"),
 2952: ("candidate", "margin==0 makes m 0: NaN wood share; only reachable with an explicit margin argument (call site uses the default constant)"),
 2827: ("candidate", "non-positive vapour pressure: baseline clamps to 1e-9 (finite dew point), mutant raises ValueError; the one caller guards e<=1e-9 first"),
 2998: ("candidate", "draw_kw<=0: baseline returns (draw, 0.0) untouched; mutant scales a negative draw and moves heat to the coil term"),
}
def probe(key):
    p = f"{W}/probes/probe_{key}.py"
    out = subprocess.run([os.path.join(os.environ["HOME"], "venv-ci/bin/python3"), p], cwd=ROOT, env={**os.environ, "PYTHONPATH": "tests/hastub"}, capture_output=True, text=True).stdout
    v = {m.group(1): int(m.group(2)) for m in re.finditer(r"RESULT (\w+)=(\d+)", out)}
    fd = re.search(r"first_difference (.*)", out)
    return v, (fd.group(1) if fd else None)
for key, meta in M4.items():
    out = f"{W}/results/{key}.json"; gj = f"{W}/gates/{key}.json"
    if os.path.exists(out) or not os.path.exists(gj): continue
    g = json.load(open(gj)); mut = g["mutant"]
    rec = dict(key=key, site=f"{meta['file']}:{meta['line']} {meta['kind']}", patch=f"{mut['old'].strip()} -> {mut['new'].strip()}", function=meta["fn"], cluster=meta["cluster"],
        gate={k: g.get(k) for k in ("verdict","killed_by","gate_rc","wall_s","load1_start","load1_end")}, m4_carried=meta["m4"], provisional=True)
    if g["verdict"] == "KILLED":
        rec["class"] = "killed"; rec["should_fail"] = None
    elif g["verdict"] == "TIMEOUT":
        rec["class"] = "timeout"
    else:
        v, fd = probe(key)
        nd = v.get("n_differing", 0)
        rec["probe"] = dict(path=f"dev/audit/rounds/round11/D3/s1/wave/D3-g46/probes/probe_{key}.py",
            command=f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g46/probes/probe_{key}.py",
            baseline_n_differing=0, mutant_n_differing=nd, n_inputs=v.get("n_inputs"), null_n_differing=v.get("n_differing_null"), first_difference=fd,
            inputs_tried="grid in probes/_mut.py (see generator for the function), ties and zero/non-finite-adjacent values included")
        kind, why = NOTE[meta["line"]]
        if nd > 0:
            rec["class"] = "candidate"; rec["why"] = why
            rec["should_fail"] = f"a closure script whose traced baseline executes thermal_model.py:{meta['line']} lacks an assertion on {why}"
            rec.update(title=f"{meta['fn']} line {meta['line']}: `{mut['new'].strip()}` survives the full gate", claim=f"The full gate (GATE_SCOPE=full GOLDEN_MODE=drift) stays at the null's red set under `{mut['old'].strip()} -> {mut['new'].strip()}` although the output of {meta['fn']} changes on {nd} of {v.get('n_inputs')} probed inputs: {why}.",
                step="D3.M3", scope="D3-s1", class_guess="new", severity_claimed="low: boundary/degenerate input of a pure helper; gate-visible behaviour change", harness_paths=["dev/audit/rounds/round11/D3/s1/fullgate.py", rec["probe"]["path"]],
                evidence_command=rec["probe"]["command"], perturbation=f"line {meta['line']} `{mut['old'].strip()}` -> `{mut['new'].strip()}`, in memory; n_differing 0 -> {nd}", null_control="probe compares the unmutated module with itself: n_differing_null=0; gate null control gates/null.json")
        else:
            rec["class"] = "equivalent-candidate"; rec["why"] = why
    json.dump(rec, open(out, "w"), indent=1); print(key, rec["class"])
