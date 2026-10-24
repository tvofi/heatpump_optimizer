"""Reviewer's own probe (not the finder's): spellings of the O19 getter plant."""
import sys, importlib.util
root = sys.argv[1]
spec = importlib.util.spec_from_file_location("h", f"{root}/dev/audit/harnesses/r10_structure_alias.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
src = h.COORD.read_text()
caller = (("        operation = self._operation_score\n        return compose_scores(",
           "        operation = self._operation_score\n        baseline, cusum = self._cop_state()%s\n"
           "        return compose_scores("),
          ("machine_score(self._cop_baseline, self._cop_health_cusum.stat),",
           "machine_score(baseline, cusum.stat),"))
anchor = "    def _raise_cop_issue(self, baseline: float) -> None:\n"
V = {
 "tuple_plant": ("        return self._cop_baseline, self._cop_health_cusum", ""),
 "trailing_none": ("        return self._cop_baseline, self._cop_health_cusum, None", ""),
 "tuple_call": ("        return tuple((self._cop_baseline, self._cop_health_cusum))", ""),
 "slice_copy": ("        return (self._cop_baseline, self._cop_health_cusum)[:]", ""),
 "dict_call": ("        return dict(b=self._cop_baseline, c=self._cop_health_cusum)", "DICT"),
 "pass_stmt": ("        pass\n        return self._cop_baseline, self._cop_health_cusum", ""),
}
print(f"RESULT clean={h.seam_cut(src, {})} count")
for name, (body, mode) in V.items():
    edits = [(anchor, f"    def _cop_state(self):\n{body}\n\n" + anchor)]
    if name == "trailing_none":
        edits += [(caller[0][0], caller[0][1].replace("baseline, cusum =", "baseline, cusum, _x =") % ""), caller[1]]
    elif mode == "DICT":
        edits += [(caller[0][0], caller[0][1].replace("baseline, cusum = self._cop_state()", "st = self._cop_state(); baseline, cusum = st['b'], st['c']") % ""), caller[1]]
    else:
        edits += [(caller[0][0], caller[0][1] % ""), caller[1]]
    text = h.planted(src, edits)
    print(f"RESULT {name}={'anchor-gone' if text is None else h.seam_cut(text, {'_cop_state': 'learning'})} count")
