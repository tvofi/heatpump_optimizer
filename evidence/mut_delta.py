"""Reviewer mutants of the da2eef8a..c5ea2af8 repair (heat_energy.py)."""
import sys
MUT = {
 "NULL": None,
 "D1 guard drops dhw_seen": ("(e.dhw_seen or ran_hot_water(ev.attribution))", "(ran_hot_water(ev.attribution))"),
 "D2 fold never sets seen": ("self._dhw_seen |= shares[1] > 0.0", "pass"),
 "D3 seen not reset at close": ("self._opened, self._dhw_kwh, self._dhw_seen = True, 0.0, False", "self._opened, self._dhw_kwh = True, 0.0"),
 "D4 old early return restored": ("or not open_span:\n", "or not open_span or self._dhw_kwh is None:\n"),
 "D5 seen not passed to SpanEnergy": ("self._dhw_kwh, self._dhw_seen)", "self._dhw_kwh)"),
}
p, name = sys.argv[1], sys.argv[2]
src = open(p).read()
if MUT[name]:
    a, b = MUT[name]
    assert src.count(a) == 1, (name, src.count(a))
    src = src.replace(a, b)
open(p, "w").write(src)
