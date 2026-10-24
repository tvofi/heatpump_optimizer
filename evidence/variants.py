"""Reviewer's own instrument: more spellings of the O19 getter plant, priced by the tree's seam_metrics."""
import sys, importlib.util
from pathlib import Path
root = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("h", sys.argv[2])
h = importlib.util.module_from_spec(spec); sys.argv = [sys.argv[2]]; spec.loader.exec_module(h)
src = h.COORD.read_text()
D = "self._cop_baseline, self._cop_health_cusum"
def plant(body, call="baseline, cusum = self._cop_state()", sig="(self)"):
    return (("    def _raise_cop_issue(self, baseline: float) -> None:\n",
             f"    def _cop_state{sig}:\n{body}\n\n    def _raise_cop_issue(self, baseline: float) -> None:\n"),
            ("        operation = self._operation_score\n        return compose_scores(",
             f"        operation = self._operation_score\n        {call}\n        return compose_scores("),
            ("machine_score(self._cop_baseline, self._cop_health_cusum.stat),",
             "machine_score(baseline, cusum.stat),"))
V = {
 "ref_plain": plant(f"        return {D}"),
 "call_type_self": plant(f"        return {D}", "baseline, cusum = type(self)._cop_state(self)"),
 "call_getattr": plant(f"        return {D}", "baseline, cusum = getattr(self, '_cop_state')()"),
 "call_bound_alias": plant(f"        return {D}", "g = self._cop_state; baseline, cusum = g()"),
 "body_const_getattr": plant("        return getattr(self, '_cop_baseline'), getattr(self, '_cop_health_cusum')"),
 "body_nested_def": plant(f"        def g():\n            return {D}\n        return g()"),
 "body_lambda_call": plant(f"        return (lambda: ({D}))()"),
 "body_dict_unpack": plant("        return {**{'b': self._cop_baseline}, 'c': self._cop_health_cusum}",
                           "st = self._cop_state(); baseline, cusum = st['b'], st['c']"),
 "body_iadd": plant("        x = [self._cop_baseline]\n        x += [self._cop_health_cusum]\n        return x"),
 "body_try": plant(f"        try:\n            return {D}\n        finally:\n            pass"),
 "body_if_else": plant(f"        if True:\n            r = ({D})\n        else:\n            r = None\n        return r"),
 "outparam_dict": plant("        out['b'] = self._cop_baseline\n        out['c'] = self._cop_health_cusum",
                        "st = {}; self._cop_state(st); baseline, cusum = st['b'], st['c']", "(self, out)"),
 "outparam_append": plant("        out.append(self._cop_baseline)\n        out.append(self._cop_health_cusum)",
                          "st = []; self._cop_state(st); baseline, cusum = st", "(self, out)"),
 "outparam_attr": plant("        out.b = self._cop_baseline\n        out.c = self._cop_health_cusum",
                        "st = types.SimpleNamespace(); self._cop_state(st); baseline, cusum = st.b, st.c", "(self, out)"),
 "outparam_extend": plant(f"        out.extend(({D}))",
                          "st = []; self._cop_state(st); baseline, cusum = st", "(self, out)"),
 "callback": plant(f"        cb({D})",
                   "box = []; self._cop_state(lambda a, b: box.extend((a, b))); baseline, cusum = box", "(self, cb)"),
}
print(f"RESULT clean={h.seam_cut(src, {})}")
for n, e in V.items():
    t = h.planted(src, e)
    print(f"RESULT {n}={'anchor-gone' if t is None else h.seam_cut(t, {'_cop_state': 'learning'})}")
