C="custom_components/heatpump_optimizer/coordinator.py"
HE="custom_components/heatpump_optimizer/heat_energy.py"
RH="custom_components/heatpump_optimizer/room_history.py"
M={
 "T1_tank_none": (C,"tank.value if tank.ok else None,","None,"),
 "T2_tank_okgate": (C,"tank.value if tank.ok else None,","tank.value,"),
 "Ra_room_nextplan": (C,'served_space_alone((self._pending_prediction or {}).get("split"))','served_space_alone((float(self._current_action.get("power", 0.0)), float(self._current_action.get("dhw_power", 0.0))))'),
 "Rb_alone_no_unplanned": (HE,"return a.dhw <= 0.0 < a.space and not self.unplanned_charge(plan_split)","return a.dhw <= 0.0 < a.space"),
 "Rc_accumulate_true": (RH,"period.space += house.space_alone","period.space += True"),
 "Rd_nosplit_true": (HE,"        if plan_split is None:\n            return False\n        a = self.attribution","        if plan_split is None:\n            return True\n        a = self.attribution"),
 "O_lower_noevidence": (C,"sample=learning_freeze.Sample.SPACE_HEAT, evidence=_space_evidence(self, self._commanded_split()),","sample=learning_freeze.Sample.SPACE_HEAT,"),
 "P_house_noevidence": (C,"sample=learning_freeze.Sample.SPACE_HEAT, evidence=_space_evidence(self, self._commanded_split()))","sample=learning_freeze.Sample.SPACE_HEAT)"),
 "X1_tankpair_noshift": (HE,"self.tank_c = (self.tank_c[1], tank_c)","self.tank_c = (tank_c, tank_c)"),
 "X2_span_open_read": (HE,"        if self._opened:\n            self._span_tank_c = self.tank_c[1]\n","        if False:\n            self._span_tank_c = self.tank_c[1]\n"),
 "X3_close_unplanned_false": (HE,"bool(ev.clean.get(\"cop\")) or e is None, unplanned_charge(ev.attribution, ev.tank_rise_k),","bool(ev.clean.get(\"cop\")) or e is None, False,"),
 "X4_booked_share": (HE,"            return 1.0\n        return dhw_share(self.attribution(plan_split))","            return dhw_share(self.attribution(plan_split))\n        return dhw_share(self.attribution(plan_split))"),
 "X5_observed_dropped": (HE,"not a.observed and a.dhw <= 0.0 < a.space","a.dhw <= 0.0 < a.space"),
 "X6_drawgate_noevidence": (C,'evidence=_space_evidence(self, pending["split"]))','evidence=learning_freeze.NO_EVIDENCE)'),
}
