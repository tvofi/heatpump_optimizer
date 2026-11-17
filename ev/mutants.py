"""Reviewer's own targeted mutants for #3662: each is (name, file, old, new), applied alone."""
A = "custom_components/heatpump_optimizer/accuracy.py"
C = "custom_components/heatpump_optimizer/coordinator.py"
M = [
 ("bound_z_zero", A, "FOLLOW_BOUND_Z = 3.0", "FOLLOW_BOUND_Z = 0.0"),
 ("bound_z_one", A, "FOLLOW_BOUND_Z = 3.0", "FOLLOW_BOUND_Z = 1.0"),
 ("ddof_zero", A, "np.std(self.contrasts, ddof=1)", "np.std(self.contrasts, ddof=0)"),
 ("second_row_new_coin", A, "        if self.ahead is not None and not self.ahead[1]:\n            self.ahead = (self.ahead[0], True)\n        else:\n            self.ahead = (self.coin.choice((-1, 1)), False)",
                            "        if self.ahead is not None and not self.ahead[1]:\n            self.ahead = (self.coin.choice((-1, 1)), True)\n        else:\n            self.ahead = (self.coin.choice((-1, 1)), False)"),
 ("levels_flat", A, "        return base / half, base * half", "        return base, base"),
 ("unsettled_never", A, "        return self.moved or self.owed is not None", "        return False"),
 ("unsettled_moved_only", A, "        return self.moved or self.owed is not None", "        return self.moved"),
 ("read_always", A, "self.refusal not in (COP_REFUSED_FROZEN, COP_REFUSED_NO_POWER))", "True)"),
 ("admits_no_draw_check", A, "return state == ASK_UNOBTAINABLE and draw is not None and not measured_heat", "return state == ASK_UNOBTAINABLE and not measured_heat"),
 ("admits_ignores_measured_heat", A, "return state == ASK_UNOBTAINABLE and draw is not None and not measured_heat", "return state == ASK_UNOBTAINABLE and draw is not None"),
 ("release_waits_no_owed", A, "if waits := self.probe.owed is not None or (probed and state == ASK_PENDING):", "if waits := (probed and state == ASK_PENDING):"),
 ("reset_keeps_verdict", A, "        self.response, self.reseeded = ASK_PENDING, False\n", "        self.reseeded = False\n"),
 ("from_dict_ignored_no_restore", A, "probe.response, probe.restore_due = response, response == ASK_IGNORED", "probe.response, probe.restore_due = response, False"),
 ("park_never_rearms_horizon_x2", A, "<= COP_HOLD_HORIZON_S:\n                return self.base", "<= 2 * COP_HOLD_HORIZON_S:\n                return self.base"),
 ("contrast_unsigned_heat_gate", A, "if coin * math.log(first.heat_ask_kw / row.heat_ask_kw) >= FOLLOW_SLOPE_MIN * step:", "if abs(math.log(first.heat_ask_kw / row.heat_ask_kw)) >= FOLLOW_SLOPE_MIN * step:"),
 ("contrast_drawn_over_heat", A, "self.contrasts.append(coin * math.log(first.drawn_kw / row.drawn_kw) / step)", "self.contrasts.append(coin * math.log(first.drawn_kw / row.drawn_kw) / math.log(first.heat_ask_kw / row.heat_ask_kw) * coin)"),
 ("priced_after_moves", C, "row = CopInterval(commanded, cast(float, self._measured_power), self._cop_reference_curve(), priced, dt_util.now())", "row = CopInterval(commanded, cast(float, self._measured_power), self._cop_reference_curve(), self._cop_scale, dt_util.now())"),
 ("coord_measured_heat_false", C, "probe_install(ctx._config).measured_heat, self._cop_scale", "False, self._cop_scale"),
 ("owed_before_release", C, "        for row in self._measured_cop.release(draw, params, dt_util.now(), measured_heat):\n            self._fold_cop_evidence(row.asked_kw, row.drawn_kw, None, row.reference, row.cop_scale)\n        if (owed := self._measured_cop.owed_scale(lambda: ctx._config.cop_scale, dt_util.now())) is not None:\n            self._apply_cop_scale(owed)\n",
   "        if (owed := self._measured_cop.owed_scale(lambda: ctx._config.cop_scale, dt_util.now())) is not None:\n            self._apply_cop_scale(owed)\n        for row in self._measured_cop.release(draw, params, dt_util.now(), measured_heat):\n            self._fold_cop_evidence(row.asked_kw, row.drawn_kw, None, row.reference, row.cop_scale)\n"),
 ("store_base_domain_dropped", "custom_components/heatpump_optimizer/store.py", '        "measured_cop/scale_base": Domain("real", c.COP_SCALE_MIN, c.COP_SCALE_MAX, null=True),\n', ""),
]
