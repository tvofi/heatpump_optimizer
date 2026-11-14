B = "custom_components/heatpump_optimizer/boost.py"
C = "custom_components/heatpump_optimizer/coordinator.py"
M = {
 "X1 clear_spent ignores a live overlay": (B, "                and CHANNEL_SPACE not in self.until and self.mode_since is None):", "                and self.mode_since is None):"),
 "X2 clear_spent ignores a live mode": (B, "                and CHANNEL_SPACE not in self.until and self.mode_since is None):", "                and CHANNEL_SPACE not in self.until):"),
 "X3 re-press resets the start": (B, "            if channel == CHANNEL_SPACE and not self.active(channel, now):\n", "            if channel == CHANNEL_SPACE:\n"),
 "X4 mode exit not persisted": (B, "        if old == MODE_BOOST:\n            _schedule_persist(coord)\n", "        if False:\n            _schedule_persist(coord)\n"),
 "X5 apply persists only on release": (B, "    if released or held.space_settle_until != tail:\n", "    if released:\n"),
 "X6 ended-while-down owes nothing": (B, "        held.settle(end, since)\n        held._clear_spent(now)\n", "        pass\n"),
 "X7 settle may shorten a running tail": (B, "        if held is None or utc_elapsed_seconds(until, held) > 0:\n", "        if True:\n"),
 "X8 payload drops since": (B, "    if held.space_since is not None and CHANNEL_SPACE in held.until:\n        payload", "    if False:\n        payload"),
 "X9 restore drops since": (B, "    if since is not None and CHANNEL_SPACE in held.until:\n        held.space_since = since\n", "    if False:\n        held.space_since = since\n"),
 "X10 coordinator mode hook removed": (C, "        boost.note_mode_change(self, self._mode, mode)  # #1935: the mode's settling tail\n", "        pass\n"),
 "X11 negative boosted_h accepted": (B, "and not isinstance(hours, bool) and 0.0 <= hours < math.inf else None)", "and not isinstance(hours, bool) and hours < math.inf else None)"),
 "X12 spent tail restored": (B, "    if until is not None and dt_util.as_utc(until) > dt_util.as_utc(now):\n", "    if until is not None:\n"),
 "X13 mode entry does not clear spent": (B, "        if live:\n            self._clear_spent(now)\n", "        if live:\n            pass\n"),
}
