# Adapted from the finder's ev/a5.py (probe/rev-3047-30905b88) to the head's reader _a5_refusals.
import sys, os, asyncio
p = os.path.join(os.getcwd(), "tests/config_flow_steps.py")
src = open(p).read()
src = src[:src.rindex("sys.exit(asyncio.run(main()))")]
mut = os.environ.get("A5_MUT")
def rep(s, old, new):
    assert s.count(old) == 1, (old, s.count(old)); return s.replace(old, new)
if mut == "no-append":
    src = rep(src, '            refused.append(f"{step}: {err}")', '            pass')
if mut == "skip-all":
    src = rep(src, '        if shown.get("type") != "form":\n            continue', '        if True:\n            continue')
g = {"__name__": "cfs", "__file__": p}
exec(compile(src, p, "exec"), g)
if os.environ.get("A5_DEFECT"):
    nm = g["_nightly"]
    ns = open("tests/nightly_ha.py").read()
    ns = rep(ns, 'if step in ("setup_overview", "factory_reset"):', 'if step == "setup_overview":')
    exec(compile(ns, nm.__file__, "exec"), nm.__dict__)
if os.environ.get("A5_PLANT") == "required":
    import voluptuous as vol
    cf = g["config_flow"]
    cf._FACTORY_RESET_SCHEMA = vol.Schema({**cf._FACTORY_RESET_SCHEMA.schema, vol.Required("planted"): str})
asyncio.run(g["nightly_a5_resubmits_fit_every_page"]())
sys.exit(g["R"].close("A5 checks"))
