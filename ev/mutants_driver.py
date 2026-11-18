import subprocess, sys, shutil
P='/root/wt/custom_components/heatpump_optimizer/accuracy.py'
orig=open(P).read()
M={
 'M2_hold_only': ("self.ahead = want if self.holding else self._next(want)", "self.ahead = self._next(want)"),
 'M3_b1_park': ("            if self.voided >= PROBE_VOID_CAP:\n                self.parked_at = row.at\n", ""),
 'M4_horizon_off': ("if not read or (started is not None and not 0.0 <= utc_elapsed_seconds(now, started) <= COP_HOLD_HORIZON_S):", "if not read:"),
 'M4b_horizon_lower': ("not 0.0 <= utc_elapsed_seconds(now, started) <= COP_HOLD_HORIZON_S", "not utc_elapsed_seconds(now, started) <= COP_HOLD_HORIZON_S"),
 'M5_reset_count_off': ("            self.voided = 0 if self.dither.contrasts else self.voided + 1\n", "            pass\n"),
 'M5b_reset_never_clear': ("self.voided = 0 if self.dither.contrasts else self.voided + 1", "self.voided = self.voided + 1"),
 'M5c_reset_when_parked': ("if self.base is not None and self.parked_at is None:\n            self.voided", "if self.base is not None:\n            self.voided"),
 'M6_rearm_clear': ("self.parked_at, self.voided = None, 0", "self.parked_at = None"),
 'M7_take_want_guard': ("if self.reading is None or self.reading != self._want():", "if self.reading is None:"),
 'M8_since_at_complete': ("None, row.at\n", "None, self.since\n"),
 'M9_cap_off': ("PROBE_VOID_CAP = 3", "PROBE_VOID_CAP = 1000"),
 'M9b_cap_2': ("PROBE_VOID_CAP = 3", "PROBE_VOID_CAP = 2"),
 'M10_admitted_start': ("            if not admitted:\n                return base\n", ""),
 'M11_holding_false': ("self.holding = running is not None and running == self._next(want)", "self.holding = False"),
 'M12_owed_admitted_reset': ("        self.dither.admitted = False  # read by the step alone, and only this cycle\n", ""),
}
which=sys.argv[1:] or list(M)
for k in which:
    a,b=M[k]
    assert orig.count(a)==1,(k,orig.count(a))
    open(P,'w').write(orig.replace(a,b))
    try:
        subprocess.run(['/root/blk.sh',k])
    finally:
        open(P,'w').write(orig)
    log=open(f'/root/mut/{k}.log').read()
    fails=[l for l in log.splitlines() if l.lstrip().startswith('FAIL')]
    print(k, log.strip().splitlines()[-1], 'fails=',len(fails), 'KILLED' if 'rc=0' not in log.splitlines()[-1] else 'SURVIVED')
    for f in fails[:4]: print('   ',f[:200])
