import subprocess, sys, os, pathlib
S=os.environ["S"]; W=pathlib.Path(S+"/wtm"); P="custom_components/heatpump_optimizer/"
M={
"M1_fuse_admit":(P+"coordinator.py",'        if not admitted("ledger", {"fuse_advisor": stored["fuse_advisor"]}):\n','        if False:\n'),
"M2_snap_admit":(P+"snapshots.py",'and not admitted("snapshots", summary):','and False:'),
"M3_comfort_clip":(P+"comfort_learning.py","float(data.get(\"learned_weight\", configured_weight)), COMFORT_WEIGHT_MIN, COMFORT_WEIGHT_MAX))","float(data.get(\"learned_weight\", configured_weight)), -1e9, 1e9))"),
"M4_cusum_cap":(P+"drift.py","self.stat = min(max(0.0, float(data.get(\"stat\", 0.0))), self.threshold * STAT_CAP_FACTOR)","self.stat = max(0.0, float(data.get(\"stat\", 0.0)))"),
"M5_pair_pos":(P+"coordinator.py","np.isfinite(value) and value > 0 and count >= 1","np.isfinite(value) and count >= 1"),
"M6_draw_nonneg":(P+"dhw_draws.py","np.isfinite(np.float64(e)) and e >= 0","np.isfinite(np.float64(e))"),
"M7_log_off":(P+"store.py","            _log_off_domain(self, data)\n",""),
"M8_meta_count":(P+"ledger.py",' if int(_leaf(e["count"])) >= 1  # the first fold writes 1',''),
"M9_freq_overflow":(P+"freq_control.py","    except (TypeError, ValueError, OverflowError):\n        return None\n    return result if np.isfinite","    except (TypeError, ValueError):\n        return None\n    return result if np.isfinite"),
"M10_lead_counts":(P+"accuracy.py","if (count := int(value)) >= 1:","if (count := int(value)) >= 0:"),
"M11_monthrep_admit":(P+"coordinator.py",' and admitted("ledger", {"month_reports": {key: value}})',''),
"M12_scoreday":(P+"coordinator.py",'if admitted("ledger", {"score_day": cleaned}):','if cleaned["day"]:'),
"M13_gains":(P+"coordinator.py","[max(0.0, float(g)) for g in raw_gains]","[float(g) for g in raw_gains]"),
"M14_aperture":(P+"coordinator.py",'(("n", 0.0), ("mx", 0.0), ("my", -np.inf), ("cov", -np.inf), ("var", 0.0)','(("n", -np.inf), ("mx", 0.0), ("my", -np.inf), ("cov", -np.inf), ("var", 0.0)'),
"M15_wear":(P+"wear.py","if (starts := int(value)) >= 1:","if (starts := int(value)) >= 0:"),
"M16_inrange":(P+"store.py","and math.isfinite(value) and domain.lo <= value <= domain.hi","and math.isfinite(value) and domain.lo <= value"),
}
env=dict(os.environ, PYTHONPATH="tests/hastub", OPENBLAS_CORETYPE="Haswell", OPENBLAS_NUM_THREADS="1")
only=sys.argv[1:]
for name,(f,a,b) in M.items():
    if only and name not in only: continue
    p=W/f; src=p.read_text(); n=src.count(a)
    if n!=1: print(name,"SITE-COUNT",n); continue
    p.write_text(src.replace(a,b))
    try:
        r=subprocess.run([S+"/vci/bin/python","tests/finite_boundary.py"],cwd=W,env=env,capture_output=True,text=True)
        out=r.stdout+r.stderr
        fails=[l for l in out.splitlines() if l.startswith("FAIL")][:2]
        print(name,"rc=%d"%r.returncode,"KILLED" if r.returncode else "SURVIVED",fails)
    finally:
        p.write_text(src)
