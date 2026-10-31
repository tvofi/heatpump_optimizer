"""B2 (BAD): five new private reaches from a collaborator into the coordinator.
pump_arbiter.diagnostics_view starts publishing coordinator internals it has
no business knowing: _measured_power, _freq_fallback, _learner_freeze_reason,
_solve_failures and _outage_recovery_until.
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import PKG, read, write, replace_once

rel = f"{PKG}/pump_arbiter.py"
s = read(rel)
s = replace_once(s, '''        "duty_mode": duty_mode(coord._config),
''', '''        "duty_mode": duty_mode(coord._config),
        "measured_power": coord._measured_power,
        "freq_fallback": coord._freq_fallback,
        "learner_freeze": coord._learner_freeze_reason,
        "solve_failures": coord._solve_failures,
        "outage_until": str(coord._outage_recovery_until),
''')
write(rel, s)
