import sys, importlib.util
from pathlib import Path
root = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(root/"tests"/"hastub"), str(root/"tests")]
spec = importlib.util.spec_from_file_location("h", root/"dev/audit/harnesses/r10_structure_alias.py")
h = importlib.util.module_from_spec(spec); sys.argv=[str(spec.origin)]; spec.loader.exec_module(h)
src = h.COORD.read_text()
old = '        for name in ("_unsub_ecl110_state", "_unsub_peak_guard", "_unsub_defrost"):\n            unsub = getattr(self, name, None)\n'
assert src.count(old) == 1
new = '        _ = (self._unsub_ecl110_state, self._unsub_peak_guard, self._unsub_defrost)\n' + old.replace('getattr(self, name, None)', 'None')
print("RESULT clean=", h.seam_cut(src, {}))
print("RESULT loop_without_getattr_but_direct_reads=", h.seam_cut(src.replace(old, new), {}))
print("RESULT loop_dropped_reads=", h.seam_cut(src.replace(old, old.replace('getattr(self, name, None)', 'None')), {}))
