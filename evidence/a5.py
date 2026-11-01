import sys, os, asyncio
p = os.path.join(os.getcwd(), "tests/config_flow_steps.py")
src = open(p).read()
src = src[:src.rindex("sys.exit(asyncio.run(main()))")]
mut = os.environ.get("A5_MUT")
if mut == "no-append":
    src = src.replace('            refused.append(f"{page.step}: {err}")', '            pass')
if mut == "skip-all":
    src = src.replace('        if shown.get("type") != "form":\n            continue', '        if True:\n            continue')
g = {"__name__": "cfs", "__file__": p}
exec(compile(src, p, "exec"), g)
if os.environ.get("A5_PLANT") == "required":
    import voluptuous as vol
    cf = g["config_flow"]
    cf._FACTORY_RESET_SCHEMA = vol.Schema({**cf._FACTORY_RESET_SCHEMA.schema, vol.Required("planted"): str})
asyncio.run(g["nightly_a5_resubmits_fit_every_page"]())
sys.exit(g["R"].close("A5 checks"))
