import ast, sys, importlib.util, pathlib
spec = importlib.util.spec_from_file_location("st", "tests/structure.py")
st = importlib.util.module_from_spec(spec); sys.modules["st"]=st; spec.loader.exec_module(st)
src = pathlib.Path("custom_components/heatpump_optimizer/coordinator.py").read_text()
def cut(source):
    local = st.Package([(st.PACKAGE_DIR / "coordinator.py", ast.parse(source))])
    helpers = st.CoordinatorRoles(local).coordinator_helpers()
    cls = local.classes[(st.COORDINATOR_MODULE, "HeatPumpOptimizerCoordinator")]
    return st.seam_metrics(cls, None, helpers)["seam_cut_total"]
print("base", cut(src))
old = "            ctx._current_state.peak_guard_active = self._peak_guard.suppressing\n"
assert src.count(old)==1
v1 = src.replace(old, "            self._ctx = ctx.published(peak_guard_active=self._peak_guard.suppressing)\n")
print("grid rebinds self._ctx", cut(v1))
v2 = src.replace(old, "            ctx.publish(self, peak_guard_active=self._peak_guard.suppressing)\n")
print("grid calls ctx method", cut(v2))
old2 = "            ctx._current_state.ecl110_effective_displace = effective\n"
assert src.count(old2)==1
v3 = src.replace(old2, "            self._ctx = ctx.published(ecl110_effective_displace=effective)\n")
print("core ecl110 rebinds self._ctx", cut(v3))
