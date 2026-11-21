"""Reviewer's mutant table for PR 3812 round 2: (id, file, old, new). Each old must match once."""
P = "custom_components/heatpump_optimizer/"
MUTANTS = [
 ("R2-M1", P+"coordinator.py", "restored=restored, write_unread=True)", "restored=restored, write_unread=False)"),
 ("R2-M2", P+"off_restore.py", "if current is not None or restorer.neutral is not None or restorer.write_unread:", "if current is not None or restorer.neutral is not None:"),
 ("R2-M3", P+"off_restore.py", "if baseline is None and restorer.neutral is None and not restorer.write_unread:", "if baseline is None and restorer.neutral is None:"),
 ("R2-M4", P+"pump_arbiter.py", "        held.supply, held.supply_held = None, False\n", "        pass\n"),
 ("R2-M5", P+"off_restore.py", "return done and release is not None", "return done"),
 ("REV-A unread-unarmed", P+"off_restore.py", "if baseline is None and restorer.neutral is None and not restorer.write_unread:\n        return False", "if baseline is None and restorer.neutral is None:\n        return restorer.write_unread"),
 ("REV-B unread-captures-later", P+"off_restore.py", "if current is not None or restorer.neutral is not None or restorer.write_unread:\n                return True", "if current is not None or restorer.neutral is not None or (restorer.write_unread and restorer.baseline_of(hass, restorer.entity_id) is None):\n                return True"),
 ("REV-C freq-319", P+"freq_control.py", "abs(hz - self.commanded) < FREQ_WRITE_EPSILON_HZ", "abs(hz - self.commanded) <= FREQ_WRITE_EPSILON_HZ"),
 ("REV-D row-2204", P+"pump_arbiter.py", "        for slot in [s for s in record if s != \"space_setpoint\"]:\n            del record[slot]", "        for slot in [s for s in record if False]:\n            del record[slot]"),
 ("REV-E empty-drop-tells", P+"off_restore.py", "    if done:\n        held.armed.pop(key)", "    if done:\n        if restorer is not None and restorer.restored is not None: restorer.restored(entry, restorer.entity_id, 0.0)\n        held.armed.pop(key)"),
]
