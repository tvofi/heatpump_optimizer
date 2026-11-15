import json
A="custom_components/heatpump_optimizer/accuracy.py"; D="custom_components/heatpump_optimizer/draw_range.py"; C="custom_components/heatpump_optimizer/coordinator.py"
M=[
# the five the repair answers
("R1 judge_ratio follows operand deleted",A,"if abs(ratio - 1.0) <= COP_ASK_TOLERANCE or state == ASK_FOLLOWS:","if abs(ratio - 1.0) <= COP_ASK_TOLERANCE:"),
("R2 replay row.reference -> live curve",C,"None, row.reference, row.cop_scale)","None, self._cop_reference_curve(), row.cop_scale)"),
("R3 span close window arg dropped",C,"ctx._thermal_params, coord._accuracy.draw))","ctx._thermal_params))"),
("R4 release 0.0 <= -> 0.0 <",A,"0.0 <= utc_elapsed_seconds(now, row.at)","0.0 < utc_elapsed_seconds(now, row.at)"),
("R5 flow lift < -> <=",C,"if commanded < draw_range.power_floor_kw(","if commanded <= draw_range.power_floor_kw("),
# reviewer's own
("A3 release i >= over -> >",A,"if i >= over and","if i > over and"),
("A4 release horizon <= -> <",A,"<= COP_HOLD_HORIZON_S:","< COP_HOLD_HORIZON_S:"),
("A5 release follows by base rule",A,"            return rows\n","            return [r for r in rows if self._base_folds(r, params)]\n"),
("A6 release ignored returns rows",A,"if state == ASK_IGNORED:\n            return []","if state == ASK_IGNORED:\n            return rows"),
("A7 pending refused but not held",A,"            self.held.append(row)\n            return COP_REFUSED_NO_EVIDENCE","            return COP_REFUSED_NO_EVIDENCE"),
("A8 base_folds >= -> >",A,">= params.nameplate_power_floor_kw)","> params.nameplate_power_floor_kw)"),
("A9 base_folds ignores the draw",A,"min(row.asked_kw, row.ratio * row.asked_kw) >=","row.asked_kw >="),
("A15 release aged rows dropped",A,"            rows = due\n","            rows = []\n"),
("A12 diagnostics floor configured",A,'round(power_floor_kw(draw, params), 3)','round(power_floor_kw(None, params), 3)'),
("D1 full window boundary >= -> >",D,"if len(draw.samples) >= WINDOW else ASK_PENDING","if len(draw.samples) > WINDOW else ASK_PENDING"),
("D3 run ask exclusive of the minimum",D,"if a >= floor and a > 0.0]","if a > floor and a > 0.0]"),
("D5 cap key ignores the configured max",D,"or draw.config != (cfg_min, cfg_max):","or draw.config is None or draw.config[0] != cfg_min:"),
("D6 floor needs MIN_SAMPLES+1",D,"    if len(drawn) < MIN_SAMPLES:\n        return floor","    if len(drawn) <= MIN_SAMPLES:\n        return floor"),
("D7 cap reads the high percentile",D,"low_kw = float(np.percentile(drawn, LOW_PERCENTILE))","low_kw = float(np.percentile(drawn, HIGH_PERCENTILE))"),
("D10 follows_ask ignored reads None",D,"{ASK_FOLLOWS: True, ASK_IGNORED: False}","{ASK_FOLLOWS: True, ASK_IGNORED: None}"),
("C4 replay swaps ask and draw",C,"self._fold_cop_evidence(row.asked_kw, row.drawn_kw, None,","self._fold_cop_evidence(row.drawn_kw, row.asked_kw, None,"),
("C8 held row stamped a month old",C,"self._cop_reference_curve(), self._cop_scale, dt_util.now())","self._cop_reference_curve(), self._cop_scale, dt_util.now() - timedelta(days=30))"),
("C12 judge_ratio reads no window",C,"self._measured_cop.judge_ratio(ewma, row, params, draw)","self._measured_cop.judge_ratio(ewma, row, params, None)"),
("C13 release reads no window",C,"self._measured_cop.release(draw, params, dt_util.now())","self._measured_cop.release(None, params, dt_util.now())"),
("C14 live fold reads live reference twice",C,"return self._fold_cop_evidence(commanded, row.drawn_kw, heat_kw, row.reference)","return self._fold_cop_evidence(commanded, row.drawn_kw, None, row.reference)"),
]
for k in range(3):
    json.dump([dict(name=n,file=f,old=o,new=w) for n,f,o,w in M[k::3]], open(f"/root/rev/spec{k}.json","w"), indent=1)
for n,f,o,w in M:
    c=open(f).read().count(o)
    if c!=1: print("COUNT",c,n)
print(len(M))
