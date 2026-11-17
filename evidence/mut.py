import subprocess,sys
F="custom_components/heatpump_optimizer/accuracy.py"
M={
"dither_noop":("        return self.levels(base)[(coin > 0) != second]","        return base"),
"coin_always_plus":("            self.ahead = (self.coin.choice((-1, 1)), False)","            self.ahead = (1, False)"),
"no_pair_differencing_levels":("self.contrasts.append(coin * math.log(first.drawn_kw / row.drawn_kw) / step)","self.contrasts.append(math.log(row.drawn_kw / self.base_ref) / step) if False else self.contrasts.append(coin * math.log(first.drawn_kw / 1.0) / step)"),
"follows_inverted":("        if mean - bound >= FOLLOW_SLOPE_MIN:\n            return ASK_FOLLOWS","        if mean - bound <= FOLLOW_SLOPE_MIN:\n            return ASK_FOLLOWS"),
"no_bound":("bound = FOLLOW_BOUND_Z * float","bound = 0.0 * float"),
"drop_clamp_reseed":("if not self.reseeded and not COP_SCALE_MIN < row.cop_scale < COP_SCALE_MAX:","if False:"),
"follows_no_owed":("            self.owed, self.base = self.base, None","            self.base = None"),
}
for k,(a,b) in M.items():
    s=open(F).read(); assert s.count(a)==1,k
    open(F,"w").write(s.replace(a,b))
    r=subprocess.run(["bash","/root/rev-ev/drive.sh","/root/wt-mut"],capture_output=True,text=True)
    out=r.stdout+r.stderr
    open(f"/root/rev-ev/C_{k}.txt","w").write(out)
    fails=[l for l in out.splitlines() if "FAIL" in l]
    print(k,"KILLED" if r.returncode!=0 else "SURVIVED",len(fails),(fails[0][:140] if fails else out.strip().splitlines()[-1]),flush=True)
    subprocess.run(["git","checkout","--","."])
